# Categorization guide

Use this so classifications are consistent across runs. These are heuristics to
anchor your judgment, not a lookup table — read the title *and* channel and use
what you know about the channel. When genuinely unsure, prefer the less specific
bucket over guessing.

## 1. Is it developer / technical?

"Developer/technical" = content whose primary value is about building software,
systems, data, hardware, or the tech industry as a craft. Count it if a working
engineer would plausibly watch it *to get better at or stay current with their
work*.

**Yes:**
- Programming languages, frameworks, libraries (React tutorial, Rust async, Go
  generics).
- Tooling & infra: Docker, Kubernetes, CI/CD, databases, cloud (AWS/GCP/Vercel),
  terminal/editor setups, git.
- CS fundamentals, system design, algorithms, architecture.
- AI/ML engineering, LLMs, data engineering/science with a build-it angle.
- Live coding, project build-alongs, code reviews, debugging sessions.
- Conference talks / meetups on the above.
- Tech-industry/career content aimed at engineers (interview prep, "day in the
  life of a SWE", layoffs/industry analysis from an engineer's lens).
- Hardware/electronics/maker content with a technical build focus.

**No (even though it's tech-adjacent):**
- General consumer tech reviews / unboxings (phone reviews, gadget hauls) — these
  are *consumer tech*, not developer content. Note them as a separate "consumer
  tech" topic if frequent.
- Crypto price/trading hype (unless it's about *building* on-chain).
- Productivity/notion/"tools" content with no engineering substance.
- Business/startup content that's pure founder/marketing, not building.

**Edge calls:** A tech-career *vlog* ("I quit my FAANG job") is dev-*adjacent*:
mark it developer/technical = true but style = personality/vlog. AI news from a
hype channel: developer/technical = true only if there's real technical
substance; otherwise treat as news/commentary and topic = AI.

## 1a. Developer sub-themes (the centerpiece)

The headline of the report is **developer-themed watching behaviour**, so don't
stop at a yes/no — bucket each dev video into a sub-theme so you can say *what
kind* of dev content they watch:

- **Languages & frameworks** — React/Next, Rust, Go, Python, TypeScript, etc.
- **Web / frontend** vs **backend / APIs** (split if volume allows).
- **DevOps / cloud / infra** — Docker, Kubernetes, CI/CD, AWS/GCP/Vercel.
- **Data / AI / ML engineering** — LLM tooling, agents, data pipelines.
- **Systems / low-level** — C/Rust internals, OS, performance.
- **System design / architecture** — design interviews, DDD, scaling.
- **Security**.
- **Tooling & editors** — Neovim/VSCode, git, terminal, dotfiles.
- **Career / industry** — interview prep, layoffs, "day in the life", company
  analysis from an engineer's lens.

## 1b. Separate genuine viewing from own/work uploads

A real trap: a chunk of "dev" entries are often the user's **own uploads or their
employer's channel** (demo recordings, internal `zz…`/test videos, product
marketing they appear in). These are *work artifacts*, not content they chose to
watch to learn. Detect them by channel (matches the user's name/employer) and by
title markers — a recurring demo prefix, internal `zz…`/`test` names, or an
issue-number tag (e.g. `#1234`). When reporting the developer share, **break it
into three**: genuine third-party dev viewing, own/work uploads, and dev-adjacent
— and lead with the genuine number. Saying "≈X% dev, but most of it is your own
work demos" is far more honest and useful than a flat percentage.

## 2. Video style

Assign exactly one primary style per video. Use duration as a strong signal but
let title/channel override it.

| Style | What it is | Signals |
|---|---|---|
| **Shorts** | Vertical < ~60s clips | `is_short` true, or duration ≤ 60s and short-form |
| **Tutorial / how-to** | Teaches a specific skill or build | "how to", "tutorial", "build a", "crash course", step-by-step |
| **Course / lecture** | Long structured teaching | 30min+, "full course", university lectures, MOOC |
| **Podcast / long-form interview** | Conversation, often 2 people | 40min+, "podcast", "ep.", interview, two-name titles |
| **Conference talk / meetup** | Recorded talk to an audience | Conference names (GOTO, QCon, PyCon, re:Invent), "talk", "keynote" |
| **Personality / vlog** | Driven by a host's persona/life | Creator-centric channels, "my", "I", day-in-the-life, reactions, rants |
| **Live coding / project build** | Real-time building/debugging | "live", "building X in Y", streams, "let's build" |
| **News / commentary** | Reporting or opinion on events | "news", weekly roundups, "what happened", reaction to announcements |
| **Music** | Music videos, mixes, lyric videos | Music channels/artists, "official video", "lofi", "mix" |
| **Entertainment** | Comedy, gaming, sketches, general fun | gaming channels, comedy, "funny", playthroughs |
| **Other** | Doesn't fit above | use sparingly |

Report style two ways: overall, and **within the developer/technical slice**
(e.g. "your dev content is mostly tutorials and conference talks, almost no
podcasts"), since the user specifically cares about *what style* of technical
content they consume.

## 3. Topics

Cluster into 5–10 human-readable themes by subject matter (not style). Examples:
"Rust & systems programming", "AI/LLM tooling", "web frontend (React/Next)",
"DevOps & cloud", "personal finance", "gaming", "fitness", "music". Merge tiny
one-off topics into "misc". Give each cluster a rough count or % so volume is
visible.

## 4. Watch-time estimates (be honest about precision)

You only have **video duration**, not actual watch time. So:
- Total estimated time = sum of `duration_seconds` (skip nulls; Shorts often have
  no duration — estimate ~30s each if you include them, and say so).
- Daily average = total ÷ number of days actually covered.
- Average length = mean duration of long-form (non-Short) videos.
- Always present these as "estimated, based on video length — actual watch time
  is likely lower" and never as precise. Shorts inflate video *counts* massively
  while adding little time; separate the two so the picture isn't misleading.
