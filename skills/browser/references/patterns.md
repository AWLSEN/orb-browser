# Common orb-browser Patterns

## 1. Read a page and summarize

```bash
orb-browser go https://news.ycombinator.com
TEXT=$(orb-browser text)
# You (Claude) analyze the text directly — no separate LLM call needed
```

## 2. Scroll and collect content

```bash
orb-browser go https://news.ycombinator.com
for i in {1..10}; do
  orb-browser text >> /tmp/content.txt
  orb-browser scroll down
  sleep 1
done
# Analyze /tmp/content.txt
```

## 3. Login with cookies then browse

```bash
# Get cookies from user (see references/cookie-export.md)
orb-browser login --cookies /tmp/cookies.json
orb-browser go https://x.com/home
orb-browser text  # now shows logged-in feed
orb-browser sleep  # checkpoint session for next time
```

## 4. Scheduled monitoring

```bash
# In a script that runs via /schedule:
orb-browser wake
orb-browser go https://news.ycombinator.com
CONTENT=$(orb-browser text)
# Analyze content, email results, etc.
orb-browser sleep
```

Use `/schedule` to run this every N hours. The browser sleeps at $0 between runs.

## 5. Fill and submit a form

```bash
orb-browser go https://example.com/signup
orb-browser fill "input[name=name]" "John Doe"
orb-browser fill "input[name=email]" "john@example.com"
orb-browser fill "textarea[name=bio]" "Software engineer"
orb-browser click "button[type=submit]"
sleep 2
orb-browser screenshot /tmp/result.jpg  # verify submission
```

## 6. Extract structured data with JavaScript

```bash
# Extract all links
orb-browser eval "JSON.stringify(Array.from(document.querySelectorAll('a')).slice(0,20).map(a=>({text:a.textContent.trim(),href:a.href})))"

# Extract table data
orb-browser eval "JSON.stringify(Array.from(document.querySelectorAll('table tr')).map(r=>Array.from(r.cells).map(c=>c.textContent.trim())))"

# Check if logged in (Twitter example)
orb-browser eval "!!document.querySelector('[data-testid=\"primaryColumn\"]')"
```

## 7. Take visual screenshot for analysis

```bash
orb-browser go https://example.com
orb-browser screenshot /tmp/page.jpg
# Read /tmp/page.jpg to analyze the visual layout
```

## 8. Multi-page scraping

```bash
orb-browser go https://example.com/page/1
orb-browser text >> /tmp/all.txt
orb-browser go https://example.com/page/2
orb-browser text >> /tmp/all.txt
orb-browser go https://example.com/page/3
orb-browser text >> /tmp/all.txt
```

## 9. Twitter/X watcher pattern

```bash
# One-time setup:
orb-browser deploy
orb-browser login --cookies /tmp/twitter_cookies.json
orb-browser sleep

# Each run (via /schedule):
orb-browser wake
orb-browser go https://x.com/home
# Scroll and extract posts
for i in {1..15}; do
  orb-browser text >> /tmp/feed.txt
  orb-browser scroll down
  sleep 2
done
# Analyze /tmp/feed.txt for interesting posts
# Email summary to user
orb-browser sleep
```

## 10. Handling errors

- If `orb-browser go` times out → the page might be slow, try again
- If you see "browser not ready" → run `orb-browser wake` first
- If cookies expired → ask user for fresh cookies
- If Cloudflare blocks → need user's cookies (can't bypass from cloud IP)
- If `orb-browser deploy` fails → check ORB_API_KEY is set
