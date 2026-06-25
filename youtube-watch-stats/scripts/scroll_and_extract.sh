#!/usr/bin/env bash
# Two-phase harvest of the open YouTube history page (the approach verified to
# capture the full ~600-item window):
#   Phase 1 — scroll to load the whole window. With the current layout the page
#             KEEPS loaded items in the DOM (it does not aggressively recycle),
#             so we don't harvest mid-scroll. Stop once a date-section older than
#             the window appears, or the page stops growing.
#   Phase 2 — harvest everything in ONE pass with extract.js.
#
# Usage: PWCLI="<cli>" scroll_and_extract.sh <session> <out.json> [days] [max_scrolls]
set -euo pipefail

PWCLI="${PWCLI:-npx -y @playwright/cli@latest}"
SESSION="${1:-yt}"
OUT="${2:-raw.json}"
DAYS="${3:-30}"
MAX="${4:-100}"
DIR="$(cd "$(dirname "$0")" && pwd)"

raweval() { $PWCLI -s="$SESSION" --raw eval "$1" 2>/dev/null | tr -d '"'; }

# A taller viewport loads more per scroll.
$PWCLI -s="$SESSION" resize 1400 1700 >/dev/null 2>&1 || true

# Phase 1: scroll until the window is fully loaded.
prev_h=-1
stale=0
for i in $(seq 1 "$MAX"); do
  # All current section-header texts -> ask process_history if we've passed the cutoff.
  headers="$($PWCLI -s="$SESSION" --raw eval \
    "JSON.stringify([...document.querySelectorAll('ytd-item-section-renderer #title, ytd-item-section-renderer #header, ytd-item-section-renderer h2, ytd-item-section-renderer h3')].map(e=>e.innerText.trim()))" \
    2>/dev/null)"
  reached="$(printf '%s' "$headers" | python3 "$DIR/process_history.py" --reached-cutoff --days "$DAYS" 2>/dev/null || echo MORE)"
  h="$(raweval 'document.documentElement.scrollHeight')"
  echo "scroll $i: height=${h:-?} cutoff=$reached"
  [ "$reached" = "REACHED" ] && { echo "loaded past the ${DAYS}-day cutoff"; break; }

  if [ "$h" = "$prev_h" ]; then
    stale=$((stale + 1))
    [ "$stale" -ge 3 ] && { echo "page stopped growing — end of history"; break; }
  else
    stale=0
  fi
  prev_h="$h"

  $PWCLI -s="$SESSION" eval "window.scrollTo(0, document.documentElement.scrollHeight)" >/dev/null 2>&1 || true
  $PWCLI -s="$SESSION" run-code "async page => await page.waitForTimeout(900)" >/dev/null 2>&1 || true
done

# Phase 2: one harvest of the fully-loaded DOM.
$PWCLI -s="$SESSION" --raw eval "$(cat "$DIR/extract.js")" > "$OUT"
echo "harvested -> $OUT"
