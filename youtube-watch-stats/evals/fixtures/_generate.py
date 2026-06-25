#!/usr/bin/env python3
"""Generate deterministic fixture watch-history JSON files for evals.

Each video carries the real fields the scraper emits, plus a private "_truth"
block (dev? + style) that we use to compute ground-truth aggregates for
assertions. The skill never sees "_truth" — we strip it into the *_truth.json
summary and write the clean history file separately.
"""
import json
import os
from datetime import date, timedelta

BASE = date(2026, 6, 24)  # most recent watched day; fixtures span back 30 days

def d(n):  # n days before BASE -> iso
    return (BASE - timedelta(days=n)).isoformat()

def vid(title, channel, secs, dev, style, day, short=False):
    return {"title": title, "channel": channel, "url": f"https://www.youtube.com/watch?v={abs(hash((title,day)))%10**11}",
            "duration_seconds": (None if short else secs), "is_short": short,
            "section": "", "watched_date": d(day), "_truth": {"dev": dev, "style": style}}

# ---------------------------------------------------------------------------
# Fixture 1: heavy developer viewer
# ---------------------------------------------------------------------------
heavy_dev = [
    vid("Build a REST API in Rust with Axum — full tutorial", "Let's Get Rusty", 2640, True, "tutorial", 1),
    vid("Async Rust explained from scratch", "Jon Gjengset", 5400, True, "course", 2),
    vid("System Design Interview: Design a URL shortener", "ByteByteGo", 1500, True, "course", 2),
    vid("React Server Components, fully explained", "Theo - t3.gg", 2100, True, "personality", 3),
    vid("I quit my $400k FAANG job — here's why", "ThePrimeagen", 1320, True, "personality", 3),
    vid("Lex Fridman: Programming, AI and the future with John Carmack", "Lex Fridman", 18000, True, "podcast", 4),
    vid("GOTO 2023 • Functional Core, Imperative Shell", "GOTO Conferences", 2700, True, "talk", 5),
    vid("Live coding: building a terminal text editor in C", "Tsoding Daily", 7200, True, "live", 6),
    vid("Kubernetes networking deep dive", "TechWorld with Nana", 1980, True, "tutorial", 7),
    vid("Why I switched from VSCode to Neovim", "Josean Martinez", 1140, True, "personality", 8),
    vid("Postgres performance tuning crash course", "Hussein Nasser", 2280, True, "tutorial", 9),
    vid("The Rust programming language — conference keynote", "RustConf", 3300, True, "talk", 10),
    vid("AI agents are eating software — what engineers should know", "Fireship", 480, True, "news", 11),
    vid("Docker in 100 seconds", "Fireship", 130, True, "tutorial", 11),
    vid("Debugging a memory leak live", "Tsoding Daily", 4200, True, "live", 13),
    vid("My honest review of the M4 MacBook Pro", "MKBHD", 900, False, "personality", 14),  # consumer tech -> not dev
    vid("Lofi hip hop radio — beats to code to", "Lofi Girl", 3600, False, "music", 15),
    vid("How I take notes as a senior engineer", "Continuous Delivery", 1020, True, "personality", 16),
    vid("Quick git rebase tip", "The Coding Train", 45, True, "shorts", 17, short=True),
    vid("POV: your tests pass on the first try", "ThePrimeagen", 30, True, "shorts", 17, short=True),
    vid("Grand strategy: my favorite city builder", "Let's Game It Out", 1500, False, "entertainment", 19),
    vid("Marathon training week 3 vlog", "Nick Bare", 1080, False, "personality", 21),
    vid("TypeScript generics, the parts that confuse everyone", "Matt Pocock", 720, True, "tutorial", 23),
    vid("Designing data-intensive applications — chapter walkthrough", "ByteByteGo", 1620, True, "course", 25),
    vid("Weekly JS news: what shipped this week", "Syntax", 2400, True, "news", 27),
    vid("3 espresso recipes for better mornings", "James Hoffmann", 660, False, "tutorial", 29),
]

# ---------------------------------------------------------------------------
# Fixture 2: casual mixed viewer (mostly non-dev)
# ---------------------------------------------------------------------------
casual_mixed = [
    vid("Official music video — new single", "Taylor Swift", 240, False, "music", 0),
    vid("Trying 10 viral TikTok recipes", "Nick DiGiovanni", 1500, False, "entertainment", 1),
    vid("Day in my life as a nurse", "Miki Rai", 780, False, "personality", 2),
    vid("Premier League weekend roundup", "Sky Sports", 600, False, "news", 2),
    vid("Funny cat compilation 2026", "The Pet Collective", 480, False, "entertainment", 3),
    vid("Beginner Python: your first program", "Programming with Mosh", 1320, True, "tutorial", 4),
    vid("How to start investing in index funds", "The Plain Bagel", 900, False, "tutorial", 5),
    vid("Lofi beats to study/relax to", "Lofi Girl", 7200, False, "music", 6),
    vid("Minecraft hardcore: 100 days", "Forge Labs", 2400, False, "entertainment", 7),
    vid("Get ready with me — autumn edition", "Brooke Miccio", 720, False, "personality", 9),
    vid("Joe Rogan Experience #2100", "PowerfulJRE", 10800, False, "podcast", 10),
    vid("What is an API? explained simply", "Fireship", 360, True, "tutorial", 12),
    vid("30 minute full body HIIT", "Heather Robertson", 1800, False, "entertainment", 14),
    vid("Cute puppy does zoomies", "ViralHog", 25, False, "shorts", 15, short=True),
    vid("Quick pasta hack", "Gordon Ramsay", 40, False, "shorts", 15, short=True),
    vid("This goal was unreal", "ESPN FC", 35, False, "shorts", 16, short=True),
    vid("Budget travel: 5 days in Lisbon", "Kara and Nate", 1080, False, "personality", 18),
    vid("Excel tips every beginner should know", "Leila Gharani", 840, False, "tutorial", 20),
    vid("Reacting to my old videos", "Emma Chamberlain", 960, False, "personality", 23),
    vid("News explained: this week in 10 minutes", "Vox", 600, False, "news", 26),
]

# ---------------------------------------------------------------------------
# Fixture 3: shorts-heavy viewer (counts vs time caveat)
# ---------------------------------------------------------------------------
shorts_heavy = []
short_titles = [
    ("60 second JS tip", "Fireship", True), ("POV: prod is down", "ThePrimeagen", True),
    ("This regex will blow your mind", "Web Dev Simplified", True),
    ("Gym fail compilation", "House of Highlights", False),
    ("Cat knocks over plant", "ViralHog", False), ("1 line python trick", "Indently", True),
    ("He really said that?!", "Daily Dose Of Internet", False),
    ("CSS centering in 2026", "Kevin Powell", True), ("dunk of the night", "NBA", False),
    ("ratatouille speedrun cooking", "Joshua Weissman", False),
]
day = 0
for i in range(40):
    t, ch, dev = short_titles[i % len(short_titles)]
    shorts_heavy.append(vid(f"{t} #{i}", ch, 0, dev, "shorts", i % 30, short=True))
# a handful of long-form to contrast
shorts_heavy += [
    vid("Full Next.js 16 course", "Vercel", 9000, True, "course", 4),
    vid("Joe Rogan #2101", "PowerfulJRE", 11400, False, "podcast", 12),
    vid("Building a SaaS live", "Theo - t3.gg", 6000, True, "live", 20),
]

FIXTURES = {
    "heavy-dev": heavy_dev,
    "casual-mixed": casual_mixed,
    "shorts-heavy": shorts_heavy,
}

def summarize(items):
    n = len(items)
    dev = sum(1 for it in items if it["_truth"]["dev"])
    shorts = sum(1 for it in items if it["is_short"])
    styles = {}
    for it in items:
        styles[it["_truth"]["style"]] = styles.get(it["_truth"]["style"], 0) + 1
    return {"total": n, "dev": dev, "dev_pct": round(100 * dev / n, 1),
            "non_dev": n - dev, "shorts": shorts, "styles": styles}

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    truth = {}
    for name, items in FIXTURES.items():
        clean = [{k: v for k, v in it.items() if k != "_truth"} for it in items]
        with open(os.path.join(here, f"{name}.json"), "w") as f:
            json.dump(clean, f, indent=2)
        truth[name] = summarize(items)
    with open(os.path.join(here, "_truth.json"), "w") as f:
        json.dump(truth, f, indent=2)
    print(json.dumps(truth, indent=2))
