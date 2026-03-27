#!/bin/bash
#
# orb-browser E2E test
#
# Deploys a browser VM, navigates, screenshots, sleeps, wakes,
# verifies everything survives the checkpoint/restore cycle.
#
# Usage: ORB_API_KEY=orb_xxx ./test/e2e.sh
#

set -uo pipefail

ORB_KEY="${ORB_API_KEY:?Set ORB_API_KEY}"
ORB_API="https://api.orbcloud.dev"
PASS=0
FAIL=0

timestamp() { date -u '+%Y-%m-%dT%H:%M:%SZ'; }
log() { echo "[$(timestamp)] $*"; }

check() {
  local name="$1" ok="$2" detail="$3"
  if [ "$ok" = "true" ]; then
    PASS=$((PASS+1)); log "PASS: $name — $detail"
  else
    FAIL=$((FAIL+1)); log "FAIL: $name — $detail"
  fi
}

orb() {
  curl -s -X "$1" "${ORB_API}$2" \
    -H "Authorization: Bearer $ORB_KEY" \
    -H 'Content-Type: application/json' "${@:3}"
}

log "orb-browser E2E test"
log "===================="

# 1. Create
log "Creating VM..."
COMP=$(orb POST /v1/computers -d '{"name":"e2e-orb-browser","runtime_mb":2048,"disk_mb":4096}')
COMP_ID=$(echo "$COMP" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
SHORT="${COMP_ID:0:8}"
VM="https://${SHORT}.orbcloud.dev"
check "create" "$([ -n "$COMP_ID" ] && echo true || echo false)" "$SHORT"

# 2. Config
curl -s -X POST "${ORB_API}/v1/computers/${COMP_ID}/config" \
  -H "Authorization: Bearer $ORB_KEY" -H 'Content-Type: application/toml' \
  --data-binary @orb.toml > /dev/null
check "config" "true" "uploaded"

# 3. Build
log "Building (~3-5 min)..."
BUILD=$(curl -s -m 900 -X POST "${ORB_API}/v1/computers/${COMP_ID}/build" -H "Authorization: Bearer $ORB_KEY")
BUILD_OK=$(echo "$BUILD" | python3 -c "import sys,json; print(json.loads(sys.stdin.read(),strict=False).get('success',False))" 2>/dev/null)
check "build" "$([ "$BUILD_OK" = "True" ] && echo true || echo false)" "$BUILD_OK"
if [ "$BUILD_OK" != "True" ]; then
  log "Build failed — cleaning up"
  orb DELETE "/v1/computers/$COMP_ID" > /dev/null
  exit 1
fi

# 4. Deploy
DEPLOY=$(orb POST "/v1/computers/$COMP_ID/agents" -d '{}')
PORT=$(echo "$DEPLOY" | python3 -c "import sys,json; print(json.load(sys.stdin)['agents'][0]['port'])" 2>/dev/null)
check "deploy" "$([ -n "$PORT" ] && echo true || echo false)" "port $PORT"

sleep 15

# 5. Health
HEALTH=$(curl -s "$VM/health" 2>/dev/null)
READY=$(echo "$HEALTH" | python3 -c "import sys,json; print(json.load(sys.stdin).get('browserReady',False))" 2>/dev/null)
check "health" "$([ "$READY" = "True" ] && echo true || echo false)" "$HEALTH"

# 6. Navigate
NAV=$(curl -s "$VM/navigate?url=https://www.google.com")
TITLE=$(echo "$NAV" | python3 -c "import sys,json; print(json.load(sys.stdin).get('title',''))" 2>/dev/null)
check "navigate" "$([ "$TITLE" = "Google" ] && echo true || echo false)" "$TITLE"

# 7. Screenshot BEFORE
curl -s "$VM/screenshot" --output /tmp/orb-before.jpg
BEFORE=$(wc -c < /tmp/orb-before.jpg | tr -d ' ')
check "screenshot-before" "$([ "$BEFORE" -gt 1000 ] && echo true || echo false)" "${BEFORE}B"

# 8. Cookies
COOKIES_BEFORE=$(curl -s "$VM/cookies" | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('cookies',[])))" 2>/dev/null)
check "cookies-before" "$([ "$COOKIES_BEFORE" -gt 0 ] && echo true || echo false)" "$COOKIES_BEFORE cookies"

# 9. SLEEP
log "Sleeping (checkpoint to NVMe)..."
DEMOTE=$(orb POST "/v1/computers/$COMP_ID/agents/demote" -d "{\"port\": $PORT}")
DEMOTE_OK=$(echo "$DEMOTE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null)
check "sleep" "$([ "$DEMOTE_OK" = "demoted" ] && echo true || echo false)" "$DEMOTE_OK"

sleep 5

# 10. WAKE
log "Waking (restore from NVMe)..."
PROMOTE=$(orb POST "/v1/computers/$COMP_ID/agents/promote" -d "{\"port\": $PORT}")
PROMOTE_OK=$(echo "$PROMOTE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null)
NEW_PORT=$(echo "$PROMOTE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('port',''))" 2>/dev/null)
if [ -n "$NEW_PORT" ] && [ "$NEW_PORT" != "None" ]; then PORT=$NEW_PORT; fi
check "wake" "$([ "$PROMOTE_OK" = "promoted" ] && echo true || echo false)" "$PROMOTE_OK"

sleep 5

# 11. Health after wake
HEALTH2=$(curl -s "$VM/health" 2>/dev/null)
READY2=$(echo "$HEALTH2" | python3 -c "import sys,json; print(json.load(sys.stdin).get('browserReady',False))" 2>/dev/null)
check "health-after-wake" "$([ "$READY2" = "True" ] && echo true || echo false)" "$HEALTH2"

# 12. Screenshot AFTER
curl -s "$VM/screenshot" --output /tmp/orb-after.jpg
AFTER=$(wc -c < /tmp/orb-after.jpg | tr -d ' ')
check "screenshot-after" "$([ "$AFTER" -gt 1000 ] && echo true || echo false)" "${AFTER}B"

# 13. Cookies survived?
COOKIES_AFTER=$(curl -s "$VM/cookies" | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('cookies',[])))" 2>/dev/null)
check "cookies-after" "$([ "$COOKIES_AFTER" -gt 0 ] && echo true || echo false)" "$COOKIES_AFTER cookies"

# 14. Navigate after wake (proves Chrome is functional)
NAV2=$(curl -s "$VM/navigate?url=https://example.com")
TITLE2=$(echo "$NAV2" | python3 -c "import sys,json; print(json.load(sys.stdin).get('title',''))" 2>/dev/null)
check "navigate-after-wake" "$([ "$TITLE2" = "Example Domain" ] && echo true || echo false)" "$TITLE2"

# Cleanup
log "Cleaning up..."
orb DELETE "/v1/computers/$COMP_ID" > /dev/null

log ""
log "===================="
log "PASS: $PASS  FAIL: $FAIL  TOTAL: $((PASS+FAIL))"
log "===================="

[ "$FAIL" -eq 0 ] && exit 0 || exit 1
