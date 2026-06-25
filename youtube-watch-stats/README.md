# youtube-watch-stats (Agent Skill)

Reads your last ~30 days of YouTube watch history (live, in your own logged-in
browser) and writes a `stats-report.md` focused on **developer-themed watching
behaviour** — how much dev/technical content you watch and what *kind* — plus
topics, channels, and watch-time estimates.

A "skill" is just this folder: `SKILL.md` + `scripts/` + `references/`. How you
install it depends on your harness.

## Prerequisites
- **Node.js + npm** (for `@playwright/cli`, installed on first run)
- **Python 3** (for the processing script)
- An environment where a **real browser window can open and you can log in**
  (interactive/headed). It will **not** work in a headless/cloud agent with no
  display, because YouTube history requires your signed-in session.
- A browser: Google Chrome, Microsoft Edge, *or* nothing (it installs Chromium).

## Install

**Claude Code**
- Drop the folder into `~/.claude/skills/youtube-watch-stats/` (personal) or
  `<repo>/.claude/skills/youtube-watch-stats/` (project). It's picked up
  automatically.
- Or, if you publish this repo as a plugin marketplace, users run
  `/plugin marketplace add <you>/youtube-watch-stats` then install it.

**Claude.ai / Claude Desktop**
- Settings → Capabilities → **Skills** → upload the packaged
  `youtube-watch-stats.skill` (a zip). (See "Packaging" below.)

**Claude Agent SDK / other harnesses**
- Point your skills directory at this folder, or unzip the `.skill` into it.

## Packaging (to share as one file)
From a checkout that has the skill-creator tooling:
```bash
python -m scripts.package_skill path/to/youtube-watch-stats
```
…produces `youtube-watch-stats.skill` (a zip) you can email/Slack or attach to a
GitHub Release. Plain `zip -r youtube-watch-stats.zip youtube-watch-stats` works
too for harnesses that accept a zip.

## Usage
Just ask: *"analyze my YouTube watch history"* / *"what kind of YouTube viewer am
I?"*. First run opens a browser and asks you to sign into YouTube once; later runs
reuse that login.

## Notes
- Watch-time figures are **estimates from video length**, not actual seconds.
- YouTube's history DOM changes over time; if a run returns nothing, see
  `references/troubleshooting.md` (selectors may need a refresh).
- Credit: the verified DOM selectors and two-phase harvest approach came from a
  sibling `youtube-watch-history` skill; this version wraps them in a portable,
  self-contained CLI flow with a dev-themed report.
