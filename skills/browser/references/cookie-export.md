# How to Export Cookies from Chrome

When you need the user's login cookies for a site, give them these instructions:

## Option 1: EditThisCookie Extension (Recommended)

Tell the user:

> I need your cookies for [site] so I can browse it as you. Here's how:
>
> 1. Install the "EditThisCookie" Chrome extension: https://chromewebstore.google.com/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg
> 2. Go to [site] in your Chrome (make sure you're logged in)
> 3. Click the EditThisCookie icon in your toolbar
> 4. Click the "Export" button (looks like a box with an arrow)
> 5. Paste the JSON here

## Option 2: Chrome DevTools (No Extension)

Tell the user:

> I need your cookies for [site]. Here's how without an extension:
>
> 1. Go to [site] in Chrome (make sure you're logged in)
> 2. Press F12 or Cmd+Option+I to open DevTools
> 3. Go to the "Application" tab
> 4. In the left sidebar, click "Cookies" → the site URL
> 5. Select all rows (Cmd+A), right-click → Copy
> 6. Paste here

Note: DevTools format is tab-separated, not JSON. You'll need to parse it differently.

## After Receiving Cookies

```bash
# Save to file
cat > /tmp/cookies.json << 'EOF'
[paste the JSON here]
EOF

# Import into orb-browser
orb-browser login --cookies /tmp/cookies.json

# Verify it worked
orb-browser go https://[site]
orb-browser text  # should show logged-in content

# Checkpoint the session
orb-browser sleep
```

## Important Notes

- Cookies expire. If the session stops working, ask the user to re-export.
- Never store or log cookie values — they're credentials.
- Always `orb-browser sleep` after importing to checkpoint the session.
- Twitter/X cookies typically last 1-2 weeks before needing refresh.
