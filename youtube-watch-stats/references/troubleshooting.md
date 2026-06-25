# Scraper troubleshooting

The scrape stage drives real Chrome through Playwright's agent CLI
(`@playwright/cli`, invoked as `playwright-cli` or `npx -y @playwright/cli@latest`)
using a dedicated persistent profile. Most failures are about sign-in state or
YouTube's DOM changing. `$PWCLI` below is the invocation `setup.sh` printed.

## `playwright-cli` not found / npx keeps re-downloading
`setup.sh` resolves the command and prints it. If it chose
`npx -y @playwright/cli@latest`, export it (`export PWCLI=...`) and pass it into
the helper (`PWCLI="$PWCLI" bash scripts/scroll_and_extract.sh ...`) so npx
resolves once instead of per call. For a faster permanent setup:
`npm install -g @playwright/cli@latest`.

## Sign-in wall / no videos on first run
Expected on the very first run — the dedicated profile starts logged out. The
Chrome window is visible: have the user sign into YouTube in it, then continue.
Because the profile is persistent (`--persistent --profile=<dir>`), later runs
reuse the login. Keep the same `--profile` path every run, or the login won't
stick. Optionally snapshot auth with `$PWCLI -s=yt state-save <dir>/yt-state.json`.

## "No history items appeared" even when signed in
- Watch history may be **paused** or cleared (myactivity.google.com → YouTube
  History). Nothing to scrape.
- YouTube changed its markup and `ytd-video-renderer` no longer matches. Inspect
  a video card live — `$PWCLI -s=yt snapshot` or
  `$PWCLI -s=yt --raw eval "document.querySelector('ytd-video-renderer')?.outerHTML?.slice(0,500)"`
  — and update the selectors in `scripts/extract.js` (and the count selector in
  `scripts/scroll_and_extract.sh`). The structure is stable in spirit (a section
  renderer holding video renderers) but tag names drift over time.

## Stops too early / misses older videos
`scroll_and_extract.sh` stops after 3 scrolls with no new videos. If the page
lazy-loads slowly it can stall early:
- Raise the max-scroll count (3rd arg): `... scroll_and_extract.sh yt raw.json 150`.
- Increase the `waitForTimeout(1500)` in the helper for slow connections.
- Over-fetching is harmless — `process_history.py --days N` filters by date
  afterward.

## Real Chrome won't launch
`--browser=chrome` needs Google Chrome installed. If it's missing, `setup.sh`
installs a managed Chromium; you can also force it with
`$PWCLI -s=yt open <url> --persistent --profile=<dir>` (omit `--browser=chrome`)
— the user then signs in via that Chromium window instead.

## Dates look wrong / many "unrecognized date headers"
`process_history.py` parses English headers (`Today`, `Yesterday`, weekday names,
`Mon DD, YYYY`). If the account's YouTube language isn't English, headers won't
parse — switch the YouTube language to English temporarily, or extend
`MONTHS`/`WEEKDAYS` and the regex in `process_history.py`.

## Stale/zombie browser sessions
If a session is wedged: `$PWCLI list`, then `$PWCLI -s=yt close`, or
`$PWCLI kill-all` to force-clear all sessions.

## Bot / automation challenges
Using real Chrome with a persistent profile and a human sign-in usually avoids
challenges. If Google presents one, it appears in the visible window — have the
user solve it, then continue the scroll/extract.
