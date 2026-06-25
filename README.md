# SSW.YouTubeWatchStats

A Claude **Agent Skill** that reads your last ~30 days of YouTube watch history —
live, in your own logged-in browser — and writes a `stats-report.md` focused on
**developer-themed watching behaviour**: how much dev/technical content you watch
and *what kind* (sub-topics + styles), plus topics, channels, and watch-time
estimates.

The skill itself lives in [`youtube-watch-stats/`](youtube-watch-stats/). See its
[README](youtube-watch-stats/README.md) for full install/usage details.

## What it does

- Drives a real browser to `youtube.com/feed/history` via Playwright's agent CLI
  (`@playwright/cli`) with a **dedicated, persistent profile** — you sign into
  YouTube once, in a window the skill opens; it never touches your main browser
  profile.
- Harvests the history (handling YouTube's current DOM and its virtualized list),
  then analyzes it into a single Markdown report.
- Leads with **developer/technical viewing**: a genuine-vs-own/work-uploads split,
  dev sub-topics (languages / devops / AI / system design / career…), dev styles
  (tutorial / talk / podcast / live-coding…), and top dev channels — with the
  other breakdowns as supporting detail.

## Quick start

In any harness that supports Agent Skills, install the skill (below) and just ask:

> Analyze my YouTube watch history from the past 30 days. Categorize what I watched, summarize my main interests, and include key stats like video count, video length, watch time, viewing patterns, etc.

### Install

- **Claude Code** — copy [`youtube-watch-stats/`](youtube-watch-stats/) into
  `~/.claude/skills/` (personal) or `<repo>/.claude/skills/` (project).
- **Claude.ai / Desktop** — upload the packaged `.skill` (a zip) under
  Settings → Capabilities → Skills. Build it with
  `python -m scripts.package_skill youtube-watch-stats`, or grab one from
  [Releases](../../releases).
- **Agent SDK / other** — point your skills directory at `youtube-watch-stats/`.

### Prerequisites

- **Node.js + npm** (for `@playwright/cli`, installed on first run)
- **Python 3** (for the processing script)
- An environment where a **real browser window can open and you can sign in**
  (interactive/headed). It will **not** work in a headless/cloud agent with no
  display — YouTube watch history requires your signed-in session.
- A browser: Google Chrome, Microsoft Edge, **or none** (it installs Chromium).

## Privacy

Your watch history is private personal data. This skill reads it **locally** in a
browser you control and writes the report to your machine — it never uploads your
history or login anywhere. The persistent profile stores your YouTube session
cookies locally so you don't re-login each run; treat that profile dir like a
credential and don't commit or share it. Watch-time figures are **estimates from
video length**, not actual seconds watched.

## Notes & maintenance

YouTube's history DOM changes over time. If a run returns nothing, the selectors
likely need a refresh — see
[`references/troubleshooting.md`](youtube-watch-stats/references/troubleshooting.md).
The current selectors and two-phase "load fully, then harvest once" approach were
verified against YouTube's 2026 layout.

## Example Output

<img width="681" height="599" alt="Screenshot 2026-06-25 at 6 41 29 pm" src="https://github.com/user-attachments/assets/0889edc5-0ef9-47bd-aa59-70ae9093acbe" />

**Figure: screenshot of example watch history run against the rule**

## License

[MIT](LICENSE) © SSW Consulting Pty Ltd.
