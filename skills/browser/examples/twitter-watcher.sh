#!/bin/bash
# Twitter watcher: login with cookies, scroll feed, extract content

# First run: import cookies
# orb-browser deploy
# orb-browser login --cookies /tmp/twitter_cookies.json
# orb-browser sleep

# Subsequent runs:
orb-browser wake
orb-browser go https://x.com/home
sleep 3

# Scroll and collect feed content
> /tmp/feed.txt
for i in {1..15}; do
  orb-browser text >> /tmp/feed.txt
  orb-browser scroll down
  sleep 2
done

# Content is now in /tmp/feed.txt — analyze it
echo "Collected $(wc -l < /tmp/feed.txt) lines from Twitter feed"

orb-browser sleep
