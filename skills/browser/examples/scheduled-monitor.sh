#!/bin/bash
# Scheduled page monitor — run via /schedule every N hours
# Wakes browser, checks a page, sleeps

orb-browser wake
orb-browser go "$TARGET_URL"
sleep 2

CONTENT=$(orb-browser text)
TITLE=$(orb-browser url | python3 -c "import sys,json; print(json.load(sys.stdin).get('title',''))")

echo "Page: $TITLE"
echo "Content length: ${#CONTENT} chars"

# Take screenshot for visual check
orb-browser screenshot /tmp/monitor.jpg

orb-browser sleep

# The calling Claude Code session can analyze the content and email results
