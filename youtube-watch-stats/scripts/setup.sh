#!/usr/bin/env bash
# Idempotent setup for the youtube-watch-stats skill.
# The skill drives the browser with Playwright's agent CLI (@playwright/cli),
# which is purpose-built to be invoked from the terminal by an agent. We use it
# with real Google Chrome and a *dedicated persistent profile* (NOT the user's
# main Chrome profile), so signing into YouTube once is remembered on later runs.
set -euo pipefail

# Resolve a working `playwright-cli` invocation. Prefer a global install, fall
# back to `npx @playwright/cli@latest` (note: the bare `playwright-cli` npm
# package is deprecated — the live one is `@playwright/cli`).
if command -v playwright-cli >/dev/null 2>&1; then
  PWCLI="playwright-cli"
elif npx --no-install playwright-cli --version >/dev/null 2>&1; then
  PWCLI="npx playwright-cli"
else
  echo "Installing @playwright/cli (one-time)..."
  npm install -g @playwright/cli@latest >/dev/null 2>&1 || true
  if command -v playwright-cli >/dev/null 2>&1; then
    PWCLI="playwright-cli"
  else
    PWCLI="npx -y @playwright/cli@latest"
  fi
fi
echo "playwright-cli: $PWCLI ($($PWCLI --version 2>/dev/null | tail -1))"

# Pick a browser. Real Chrome is nicest (least bot-friction at sign-in) but is NOT
# required — Edge, or Playwright's own bundled Chromium, work just as well for
# YouTube. We emit BROWSER_FLAG for the open command:
#   --browser=chrome | --browser=msedge | (empty => bundled Chromium)
have_chrome=false; have_edge=false
if [ -d "/Applications/Google Chrome.app" ] || command -v google-chrome >/dev/null 2>&1 || command -v google-chrome-stable >/dev/null 2>&1; then
  have_chrome=true
fi
if [ -d "/Applications/Microsoft Edge.app" ] || command -v microsoft-edge >/dev/null 2>&1; then
  have_edge=true
fi

if $have_chrome; then
  BROWSER_FLAG="--browser=chrome"
elif $have_edge; then
  BROWSER_FLAG="--browser=msedge"
else
  echo "No Chrome/Edge found — installing Playwright's bundled Chromium (one-time)."
  $PWCLI install-browser chromium >/dev/null 2>&1 || true
  BROWSER_FLAG=""   # omit --browser => default bundled Chromium
fi

echo "playwright-cli command: $PWCLI"
echo "BROWSER_FLAG: ${BROWSER_FLAG:-(bundled chromium)}"
echo "Setup complete. Export both before opening:"
echo "  export PWCLI=\"$PWCLI\"  BROWSER_FLAG=\"$BROWSER_FLAG\""
