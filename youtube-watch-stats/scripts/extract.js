/*
 * Page-eval expression for `playwright-cli --raw eval "$(cat extract.js)"`.
 * Must be a single JS expression — it runs in page context and returns one
 * object per video, tagged with the raw text of its date-section header.
 * Date/duration parsing happen later in process_history.py.
 *
 * SELECTORS (verified June 2026 — the CURRENT YouTube history layout):
 *   - Date sections:  ytd-item-section-renderer  (header: #title/#header/h2/h3)
 *   - Long-form:      yt-lockup-view-model        (skip ones inside a Shorts shelf)
 *   - Shorts:         ytm-shorts-lockup-view-model-v2 / ...-view-model
 *                     (live inside ytd-reel-shelf-renderer)
 * The OLD `ytd-video-renderer` selector now matches almost nothing — don't use
 * it (kept only as a last-ditch fallback for older layouts).
 *
 * Titles: DON'T trust `.yt-lockup-metadata-view-model__title` (often empty).
 * Parse the lockup's innerText split on newlines instead — it's clean:
 *   [ "12:34" (duration, optional), "Title", "Channel", "•", "68K views" ]
 */
JSON.stringify((() => {
  const isTime = s => /^\d+:\d{2}(:\d{2})?$/.test(s);
  const lines = el => (el.innerText || '').split('\n').map(x => x.trim()).filter(Boolean);
  const out = [];

  document.querySelectorAll('ytd-item-section-renderer').forEach(sec => {
    const header = (sec.querySelector('#title, #header, h2, h3')?.innerText || '').trim();

    // Long-form videos.
    const lockups = sec.querySelectorAll('yt-lockup-view-model');
    lockups.forEach(l => {
      if (l.closest('ytd-reel-shelf-renderer')) return;   // that's a Short
      const ln = lines(l);
      if (!ln.length) return;
      let i = 0, duration = '';
      if (isTime(ln[0])) { duration = ln[0]; i = 1; }
      const title = ln[i] || '';
      const channel = (ln[i + 1] && ln[i + 1] !== '•') ? ln[i + 1] : '';
      const url = (l.querySelector('a')?.href || '').split('&')[0];
      if (title) out.push({ title, url, channel, duration_text: duration, is_short: false, section: header });
    });

    // Shorts (no channel exposed in history).
    sec.querySelectorAll('ytm-shorts-lockup-view-model-v2, ytm-shorts-lockup-view-model').forEach(s => {
      const title = (lines(s)[0]) || '';
      const url = (s.querySelector('a[href*="/shorts/"]')?.href || '').split('?')[0];
      if (title) out.push({ title, url, channel: '', duration_text: '', is_short: true, section: header });
    });

    // Fallback for older layouts only when nothing modern matched in this section.
    if (!lockups.length) {
      sec.querySelectorAll('ytd-video-renderer').forEach(v => {
        const a = v.querySelector('a#video-title, #video-title');
        if (!a) return;
        const title = (a.getAttribute('title') || a.textContent || '').trim();
        const url = (a.href || '').split('&')[0];
        const ch = v.querySelector('ytd-channel-name a, ytd-channel-name #text');
        const dur = v.querySelector('ytd-thumbnail-overlay-time-status-renderer #text, .badge-shape-wiz__text');
        const is_short = url.includes('/shorts/');
        if (title) out.push({
          title, url, channel: ch ? ch.textContent.trim() : '',
          duration_text: dur ? dur.textContent.trim() : '', is_short, section: header,
        });
      });
    }
  });
  return out;
})())
