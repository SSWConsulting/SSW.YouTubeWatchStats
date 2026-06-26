---
name: youtube-watch-stats
description: >-
  Scrape and analyze the user's YouTube watch history into a personal stats report
  focused on developer-themed watching behaviour. Use when the user asks to
  analyze their own YouTube **watch history** / viewing stats — e.g. "analyze my
  youtube watch history", "how much developer/technical content do I watch", "am
  I watching too many shorts", "what kind of youtube viewer am I", "break down my
  youtube history by topic / channel / video style", or "my youtube watch-time
  stats". (For the user's *own* history — it uses their signed-in YouTube
  account.) Sets up
  Playwright's agent CLI as needed and reads the last ~30 days by driving a real
  browser with a dedicated profile the user signs into once (it never touches their
  main browser profile), then writes one stats-report.md covering the
  developer/technical breakdown (sub-topics and styles), other topics, top
  channels, and watch-time estimates. Trigger even when the user doesn't say
  "Playwright" or "scrape" — they just want their YouTube stats.
---

# YouTube Watch Stats

Generate a personal viewing-stats report from the user's recent YouTube watch
history. The headline question this skill answers is **"what kind of viewer am
I?"** — with a particular focus on how much developer/technical content they
watch and in what *style* (personality channels, shorts, tutorials, podcasts,
conference talks, …), plus topics, channels, and watch-time estimates.

The skill has two stages that are deliberately separate:

1. **Scrape** — a Playwright script drives a browser into the user's logged-in
   YouTube (a dedicated profile they sign into once) and dumps raw history to a
   JSON file.
2. **Analyze** — you read that JSON and write `stats-report.md`.

Keeping them separate means the user can re-run the analysis on already-scraped
data without opening a browser again, and it keeps the slow/fragile browser work
out of the part that needs judgment.

## Get consent before you scrape

The scrape stage reads the user's **private YouTube watch history** through their
**logged-in Google/YouTube account** — authenticated personal data. Before
opening any browser or running the scraper, tell the user plainly what will
happen and get an explicit go-ahead. Something like:

> "To do this I'll open a browser window, have you sign into YouTube once, and
> read your watch-history page (video titles, channels, dates) for the last ~30
> days. It stays on your machine — nothing is uploaded. OK to go ahead?"

Wait for a clear yes before Stage 1. Never enter credentials or sign in on their
behalf — the user does the login themselves in the window. If they only want
analysis of data they already have (see below), you don't touch their account at
all — skip the browser entirely.

## Before you start: do you even need to scrape?

If the user already has scraped history data — they point you at a JSON file, or
there's a `history.json` (or similar) in the working directory from a previous
run — **skip straight to Analyze** using that file. Scraping is the expensive,
flaky part; don't redo it unless you have to. Only fall through to the Scrape
stage when there's no usable data yet.

## Stage 1 — Scrape

### Why it works this way

YouTube's Data API no longer returns watch history at all, and Google Takeout is
a slow manual export with no video durations. The only reliable source is the
logged-in history page at `youtube.com/feed/history`. So we drive a real browser
there — using **Playwright's agent CLI (`@playwright/cli`)**, which is built to
be run from the terminal one command at a time by an agent like you.

The session uses **real Google Chrome with a dedicated, persistent profile of its
own** (`--browser=chrome --persistent`) — *not* the user's main Chrome profile.
That means: you never touch or lock their everyday browser, and they sign into
YouTube **once** in the automation window; the persistent profile remembers it on
every later run. (This sidesteps the old approach's pain: quitting Chrome to
unlock its profile, and Chrome 136+ blocking debug access to the default
profile.)

**Important honesty caveat to carry into the report:** the history page shows the
*duration of each video*, not how long the user actually watched it. So every
"watch time" number is an **estimate based on video length**, not true
watched-seconds. Always label it as such — never imply it's exact.

### Steps

1. **Set up the CLI** (idempotent — safe to run every time):

   ```bash
   bash <skill-dir>/scripts/setup.sh
   ```

   It prints two things to export: `PWCLI` (the `playwright-cli` invocation —
   `playwright-cli` or `npx -y @playwright/cli@latest`) and `BROWSER_FLAG` (which
   browser to use). **Google Chrome is not required** — setup picks Chrome if
   present, else Edge, else Playwright's bundled Chromium (`BROWSER_FLAG` empty).
   All work fine for YouTube. Export both:
   `export PWCLI="<…>" BROWSER_FLAG="<…>"`.

2. **Open the history page** in a named session with a persistent profile:

   ```bash
   $PWCLI -s=yt open "https://www.youtube.com/feed/history" \
     $BROWSER_FLAG --persistent --headed --profile=<work-dir>/yt-profile
   ```

   `--headed` is essential — without it the browser runs invisibly (headless is
   the CLI's default) and the user can't sign in. A real browser window opens.
   Keep the profile dir stable across runs (e.g. a fixed path under the workspace)
   so the login persists. Verify it's visible with `$PWCLI list` (look for
   `headed: true`).

3. **Check sign-in.** Look at the command's snapshot / page title, or run
   `$PWCLI -s=yt --raw eval "!!document.querySelector('ytd-video-renderer')"`.
   If it's `false` or you see a sign-in page, tell the user plainly: *"A Chrome
   window opened — please sign into YouTube in it, then tell me to continue. You
   only need to do this once; I'll remember the session next time."* Wait for
   them, then proceed. (Optionally `$PWCLI -s=yt state-save <work-dir>/yt-state.json`
   to snapshot auth.)

4. **Scroll and extract** with the bundled helper, which scrolls until the page
   stops loading new videos, then dumps the raw extraction JSON:

   ```bash
   PWCLI="$PWCLI" bash <skill-dir>/scripts/scroll_and_extract.sh yt <work-dir>/raw.json
   ```

   (It uses `<skill-dir>/scripts/extract.js` as the page-eval expression. For
   very heavy viewers, pass a higher max-scroll count as a 3rd arg.)

5. **Clean it up** into the file the analysis stage reads:

   ```bash
   python3 <skill-dir>/scripts/process_history.py --in <work-dir>/raw.json \
     --days 30 --out <work-dir>/history.json
   ```

   `process_history.py` unwraps the CLI's output, parses dates/durations, filters
   to the last `--days`, and de-dupes.

6. **Close the browser** when done: `$PWCLI -s=yt close`.

If you get no videos, a sign-in wall you can't pass, or the counts look wrong,
see `references/troubleshooting.md` (login/profile, selector drift, scroll
stalls, locale dates).

### Alternative: a connected Playwright MCP

`@playwright/cli` is just Playwright's MCP browser tools wrapped as a CLI, so if a
**Playwright MCP server is already connected** in this environment you can drive
the browser through its tools instead — the logic is identical, only the calls
differ:

| This skill's CLI | Playwright MCP tool |
|---|---|
| `open … --persistent --headed` | `browser_navigate` (+ persistent/headed launch config) |
| `--raw eval "$(cat extract.js)"` | `browser_evaluate` with the same `extract.js` body |
| `eval "window.scrollTo(…)"` | `browser_evaluate` |
| `state-save` / `state-load` | MCP storage-state tools |

Use the MCP route when it's already configured (cleaner structured results, no
shell quoting). Use the bundled CLI otherwise — it's self-contained and needs no
MCP server, which is why it's the default here. Either way, feed the harvested
JSON to `process_history.py` and analyze the same way.

`process_history.py` writes a JSON array of items, each roughly:

```json
{
  "title": "Building a Rust web server from scratch",
  "channel": "Let's Get Rusty",
  "url": "https://www.youtube.com/watch?v=...",
  "duration_seconds": 1832,
  "is_short": false,
  "section": "Yesterday",
  "watched_date": "2026-06-24"
}
```

## Stage 2 — Analyze

Read the JSON and produce **one file: `stats-report.md`** in the working
directory. (Per the user's preference there's no separate data deliverable — the
JSON is just working data.)

Before writing, read `references/categorization.md`. It defines the taxonomy and
heuristics for two things that need to be consistent: (a) deciding whether a
video is developer/technical, and (b) classifying its *style*. Apply real
judgment using the title + channel — don't keyword-match blindly. A video titled
"I quit my FAANG job" on a tech-career vlog channel is developer-adjacent
*personality/vlog* content, not a tutorial.

### What to compute

Work from the data, but use your own knowledge of channels and topics to
classify. Cover:

- **Coverage line** — how many videos, over what actual date range, and note if
  some items had unparseable dates or were excluded.
- **Developer/technical viewing — the centerpiece.** This is what the user most
  wants, so go deep, not just a single percentage:
  - the dev share as **count and % of videos** *and* **% of estimated time**;
  - a **three-way split** (per `references/categorization.md` §1b): genuine
    third-party dev viewing vs the user's own/work uploads vs dev-adjacent — lead
    with the genuine number, since work-demo uploads can masquerade as "watching".
    This trap usually inflates the *count*, not the time (work clips are short),
    so show the split by count and note its small time impact;
  - a **dev sub-theme breakdown** (§1a: languages/frameworks, web, backend,
    devops/cloud, data/AI-ML, systems, system design, security, tooling, career)
    so you can say *what kind* of dev content;
  - **dev styles** (tutorial, course, conference talk, live-coding, podcast,
    news, personality) — "what format of dev content do they watch";
  - the **top dev channels** specifically.
- **Video style breakdown** — distribution across the styles in
  `references/categorization.md` (shorts, tutorial/how-to, podcast/long-form
  interview, personality/vlog, conference talk/meetup, news/commentary,
  live-coding/project build, course/lecture, music, entertainment, other). Give
  this both overall and *within the dev/technical slice*, since "what style of
  dev content" is a core question.
- **Top topics** — cluster titles/channels into ~5–10 topical themes (e.g. "Rust
  & systems programming", "AI/LLM tooling", "web frontend", "personal finance",
  "gaming"). Show rough volume per topic.
- **Video-length buckets** — for long-form, bucket durations (`<5min`,
  `5–20min`, `20–60min`, `>1hr`) and show the distribution. Shorts are all
  sub-minute — report them separately, not in these buckets.
- **Top channels** — the most-watched channels by video count, with a one-word
  tag of what each is. **Caveat to state in the report:** Shorts *usually* carry
  no channel name in YouTube history (`channel: ""`), so the channel ranking is
  effectively long-form only — say so when it applies. Also watch for work/own-account
  uploads dominating the ranking (e.g. the user's own demo videos); call those out
  rather than treating them as ordinary viewing.
- **Watch-time estimates** — clearly labelled as *estimates from video length*:
  total estimated hours, daily average (over the **actual covered span**, not the
  nominal `--days`), average video length, and the shorts-vs-long-form split
  (count and estimated time). Shorts dramatically skew
  counts but not time — call that out. A few very long items (multi-hour
  livestreams, "focus" playlists left running) can dominate the total and mislead
  — surface the total *and* the total minus the top 2–4 outliers, and flag likely
  background-audio items.
- **Viewing patterns** — derive these straight from the data (no extra scraping):
  - **Rewatches** — videos that appear more than once in the window. Count
    repeated video URLs in `history.json`; list the top few rewatched titles with
    channel/what-they-are. (This catches cross-day rewatches; same-day repeats are
    de-duped, so note it's a floor, not exact.)
  - **Rhythm** — the **busiest day** (most videos) and roughly how many of the
    covered days were active vs idle. A rough daily-volume sketch is fine.
  - **Channel concentration** — is viewing concentrated in a handful of channels
    or spread thin across many? (e.g. "top 5 channels = 40% of views" vs "90
    channels, no repeats"). It says a lot about whether they follow creators or
    graze the algorithm.
  Classify content **by judgment** (title + channel + what you know), never by a
  fixed keyword table — hardcoded keyword lists overfit to one person's history
  and fail for everyone else.
- **"What kind of viewer are you"** — a short, specific, human paragraph that
  synthesizes the above into a recognizable portrait. This is the part the user
  actually remembers; make it sharp and a little fun, grounded in the numbers.

### Report structure

Use this template (adapt headings to what the data supports — don't invent
sections you have no data for):

```markdown
# Your YouTube Watch Stats

_Last N days · M videos · <date range>_

## The short version
<2–4 sentence portrait — what kind of viewer they are, dev-content share,
dominant style, anything surprising.>

## Developer / technical viewing   ← the centerpiece, go deep
<dev share as count + % of videos AND % of estimated time.
Three-way split: genuine third-party dev viewing vs own/work uploads vs
dev-adjacent — lead with the genuine number.
Dev sub-themes (languages/devops/AI/system-design/career/…) with rough volume.
Dev styles (tutorial/talk/podcast/live-coding/…).
Top dev channels. What it all says about how they learn/stay current.>

## How you watch overall (video styles)
<style breakdown across all viewing; shorts vs long-form; length buckets.>

## Everything else you watch (topics)
<the non-dev topical clusters with rough volume — lighter touch.>

## Top channels
<ranked by video count; note Shorts carry no channel, so this is long-form only;
flag any own/work channels; note channel concentration (few-channels vs spread).>

## Viewing patterns
<busiest day + active-vs-idle days; most-rewatched videos with context.>

## Watch time (estimated)
<total / daily avg / avg length / shorts vs long-form — labelled as estimates;
surface the total minus the top 2–4 outliers; flag likely background-audio items.>

## Notes & caveats
<watch-time is video-length-based not actual; Shorts have no channel; topic %s
are judgment calls; any data gaps; profile/date caveats.>
```

Keep the prose tight and concrete — cite the actual numbers, name the actual
channels. A stat with no interpretation is filler; an interpretation with no
stat is a horoscope. Pair them.

### Clean up

Close the browser session (`$PWCLI -s=yt close`). Then tidy up — but **don't
delete the user's data silently**. Tell them what you're removing and leave the
reusable bits:

- Safe to remove without asking: throwaway scratch like `raw.json` / title dumps.
- **Keep `history.json`** (or ask before deleting it) — it's the user's scraped
  data, and the whole point of the two-stage split is that they can re-run the
  analysis from it without scraping again. Mention it's there.
- **Keep the persistent profile dir** (`yt-profile`) — that's what lets the next
  run skip the login. (It holds their YouTube session cookies, so don't commit or
  share it.)

State briefly what you cleaned up so nothing disappears as a surprise.
