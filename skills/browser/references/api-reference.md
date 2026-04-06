# orb-browser API Reference

## CLI Commands

### Lifecycle
```bash
orb-browser deploy              # Deploy browser VM (~1-2 min)
orb-browser sleep               # Checkpoint to disk ($0/hr)
orb-browser wake                # Restore (~500ms, still logged in)
orb-browser destroy             # Delete the browser VM
orb-browser status              # Health check
orb-browser live                # Open interactive live view in your browser
```

### Navigation
```bash
orb-browser go <url>            # Navigate to URL
orb-browser back                # Go back
orb-browser forward             # Go forward
orb-browser url                 # Get current URL + title (JSON)
```

### Interaction
```bash
orb-browser click <x> <y>      # Click at pixel coordinates
orb-browser click <selector>    # Click CSS selector
orb-browser fill <sel> <value>  # Fill input field
orb-browser type <text>         # Type text into focused element
orb-browser press <key>         # Press key: Enter, Tab, Escape, ArrowDown, etc
orb-browser scroll [down|up]    # Scroll page
orb-browser eval <javascript>   # Execute JavaScript, returns result
```

### Content
```bash
orb-browser text                # Page text (first 10K chars)
orb-browser html                # Full page HTML
orb-browser screenshot [path]   # JPEG screenshot (prints base64 if no path)
orb-browser cookies             # All cookies as JSON
```

### AI Agent
```bash
orb-browser task "<prompt>"                    # Vision agent loop
orb-browser task --url <url> "<prompt>"        # Navigate first, then run
orb-browser ask <url> "<question>"             # Read page text + LLM answer
```

### Auth
```bash
orb-browser setup               # Interactive setup wizard
orb-browser auth <api_key>      # Save Orb API key
orb-browser signup <email>      # Create account
orb-browser login               # Log into a site via live view
orb-browser login --cookies <file>  # Import cookies from JSON file
```

### Environment Variables
```bash
ORB_API_KEY                     # Orb Cloud API key
LLM_API_KEY                     # LLM key for /task and /ask
OPENROUTER_API_KEY              # Alternative: OpenRouter key
```

## Python SDK

```python
from orb_browser import OrbBrowser

orb = OrbBrowser(api_key="orb_...")
orb.deploy()                          # Deploy browser

# Browse
orb.navigate("https://example.com")
orb.click(selector="button.submit")   # or: orb.click(x=400, y=300)
orb.fill("input[name=email]", "test@example.com")
orb.type("hello world")
orb.press("Enter")
orb.scroll("down", 500)
orb.back()
orb.forward()

# Read
text = orb.text()                     # Page text
html = orb.html()                     # Full HTML
url_info = orb.url()                  # {"url": "...", "title": "..."}
cookies = orb.cookies()               # Cookie list
orb.screenshot("page.jpg")            # Save screenshot
result = orb.evaluate("document.title")  # Run JavaScript

# AI
result = orb.task("describe this page")  # Vision agent
answer = orb.ask("https://example.com", "What is this about?")

# Lifecycle
orb.sleep()                           # Checkpoint ($0)
orb.wake()                            # Restore (500ms)
orb.destroy()                         # Delete VM

# Properties
orb.vm_url                            # https://abc123.orbcloud.dev
orb.live_url                          # https://abc123.orbcloud.dev/live
orb.computer_id                       # VM ID
orb.state                             # init/deploying/running/sleeping
```
