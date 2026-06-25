#!/usr/bin/env python3
"""Turn the raw `playwright-cli eval` dump into a clean history.json.

Input: the JSON produced by extracting the history page (see extract.js), passed
either as a file (--in) or on stdin. `playwright-cli --raw eval` wraps the
stringified result as a quoted JSON string, so we transparently unwrap one or two
levels of JSON encoding.

Output: a JSON array of de-duplicated videos within the last --days, each with a
parsed `watched_date` and `duration_seconds`. This is the file the analysis stage
of SKILL.md reads.

Honesty note carried downstream: `duration_seconds` is the video's length, not
how long it was watched — any "watch time" derived from it is an estimate.
"""
import argparse
import json
import re
import sys
from datetime import date, timedelta

MONTHS = {m.lower(): i for i, m in enumerate(
    ["", "January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"])}
MONTHS.update({m[:3].lower(): i for m, i in list(MONTHS.items()) if m})
WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday",
            "saturday", "sunday"]


def _decode_one(text: str):
    """Decode one CLI eval result, unwrapping JSON-string nesting -> list."""
    val = json.loads(text)
    while isinstance(val, str):   # --raw hands us a JSON string containing JSON
        val = json.loads(val)
    if not isinstance(val, list):
        raise ValueError(f"Expected a list of videos, got {type(val).__name__}")
    return val


def load_raw(text: str):
    """Decode the raw capture into a flat list of video dicts.

    Because YouTube virtualizes the history list (only the videos near the
    viewport exist in the DOM at any moment), the scrape captures one extract per
    scroll step. The input is therefore JSON-lines: each non-empty line is one
    `--raw eval` result (a JSON-quoted JSON array). A single-array input (one
    line) still works. De-duplication happens later in main().
    """
    items = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        items.extend(_decode_one(line))
    return items


def parse_duration(text: str):
    """'12:34' -> 754, '1:02:03' -> 3723, Shorts/no badge -> None."""
    if not text:
        return None
    text = text.strip()
    if not re.match(r"^(\d+:)?\d{1,2}:\d{2}$", text):
        return None
    seconds = 0
    for p in text.split(":"):
        seconds = seconds * 60 + int(p)
    return seconds


def parse_section_date(header: str, today: date):
    """Map a history section header to a date. None if unparseable.

    Headers: 'Today', 'Yesterday', a weekday name for the last week, or a full
    date like 'Jun 20, 2026' / 'June 20, 2026' (sometimes weekday-prefixed).
    """
    if not header:
        return None
    h = header.strip().lower()
    if h == "today":
        return today
    if h == "yesterday":
        return today - timedelta(days=1)
    if h in WEEKDAYS:
        delta = (today.weekday() - WEEKDAYS.index(h)) % 7
        return today - timedelta(days=delta)
    # Match either order: "Jun 9, 2026" (month-first, US) or "9 Jun 2026"
    # (day-first, en-GB/AU — what YouTube uses in those locales). Year optional.
    mon = day = year = None
    m = re.search(r"([A-Za-z]+)\.?\s+(\d{1,2})(?:,?\s*(\d{4}))?", header)  # month first
    if m and MONTHS.get(m.group(1).lower()):
        mon, day = MONTHS[m.group(1).lower()], int(m.group(2))
        year = int(m.group(3)) if m.group(3) else None
    else:
        m = re.search(r"(\d{1,2})\s+([A-Za-z]+)\.?(?:\s+(\d{4}))?", header)  # day first
        if m and MONTHS.get(m.group(2).lower()):
            day, mon = int(m.group(1)), MONTHS[m.group(2).lower()]
            year = int(m.group(3)) if m.group(3) else None
    if mon is None:
        return None
    try:
        d = date(year or today.year, mon, day)
        if year is None and d > today:   # no explicit year -> assume last year
            d = date(today.year - 1, mon, day)
        return d
    except ValueError:
        return None


def reached_cutoff(headers, days):
    """True if any section header parses to a date older than the N-day window.

    Used by the scroller to know the full window is loaded so it can stop early
    instead of scrolling through the user's entire multi-year history.
    """
    today = date.today()
    cutoff = today - timedelta(days=days)
    for h in headers:
        d = parse_section_date(h, today)
        if d and d < cutoff:
            return True
    return False


def main():
    ap = argparse.ArgumentParser(description="Clean raw history eval output.")
    ap.add_argument("--in", dest="infile", help="Raw JSON file (default: stdin).")
    ap.add_argument("--out", default="history.json", help="Cleaned output path.")
    ap.add_argument("--days", type=int, default=30, help="Keep last N days (default 30).")
    ap.add_argument("--reached-cutoff", action="store_true",
                    help="Read a JSON array of section headers on stdin; print "
                         "REACHED if any is older than --days, else MORE.")
    args = ap.parse_args()

    if args.reached_cutoff:
        headers = _decode_one(sys.stdin.read().strip() or "[]")
        print("REACHED" if reached_cutoff(headers, args.days) else "MORE")
        return

    raw_text = open(args.infile, encoding="utf-8").read() if args.infile else sys.stdin.read()
    try:
        raw = load_raw(raw_text)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"ERROR: couldn't parse eval output: {e}", file=sys.stderr)
        sys.exit(1)

    today = date.today()
    cutoff = today - timedelta(days=args.days)

    seen = set()
    records = []
    skipped_undated = 0
    for it in raw:
        d = parse_section_date(it.get("section", ""), today)
        if d is None:
            skipped_undated += 1
            continue
        if d < cutoff or d > today:
            continue
        url = it.get("url", "")
        key = (url, it.get("section", ""))
        if url and key in seen:
            continue
        seen.add(key)
        records.append({
            "title": it.get("title", ""),
            "channel": it.get("channel", ""),
            "url": url,
            "duration_seconds": parse_duration(it.get("duration_text", "")),
            "is_short": bool(it.get("is_short")),
            "section": it.get("section", ""),
            "watched_date": d.isoformat(),
        })

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    dates = [r["watched_date"] for r in records]
    span = f"{min(dates)} … {max(dates)}" if dates else "n/a"
    print(f"Wrote {len(records)} videos to {args.out}")
    print(f"Date range: {span}  (cutoff {cutoff.isoformat()})")
    if skipped_undated:
        print(f"Note: {skipped_undated} items had unrecognized date headers and were skipped.")
    if not records:
        print("WARNING: 0 videos in range — check login/profile and that watch "
              "history is enabled.", file=sys.stderr)


if __name__ == "__main__":
    main()
