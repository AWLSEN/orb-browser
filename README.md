# orb-browser

Browser sessions that sleep for $0 and wake in 500ms.

Run headless Chrome on [Orb Cloud](https://orbcloud.dev). When idle, checkpoint the entire browser to NVMe — cookies, DOM, localStorage, everything. Wake it up later in ~500ms, exactly where you left off. Still logged in. No re-authentication.

## Quick Start

### SDK

```javascript
const { OrbBrowser } = require("./sdk");

const browser = new OrbBrowser({ apiKey: "orb_..." });

// Deploy (~3-5 min first time)
await browser.deploy();

// Browse
await browser.navigate("https://example.com");
const screenshot = await browser.screenshot(); // Buffer (JPEG)

// Sleep — frozen to NVMe, costs $0
await browser.sleep();

// ... hours, days later ...

// Wake — ~500ms, everything restored
await browser.wake();
const screenshot2 = await browser.screenshot(); // Same page, same cookies
```

### Manual (curl)

```bash
# Deploy
ORB_KEY="orb_..."
COMP_ID=$(curl -s -X POST https://api.orbcloud.dev/v1/computers \
  -H "Authorization: Bearer $ORB_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"name":"my-browser","runtime_mb":2048,"disk_mb":4096}' | jq -r .id)

curl -s -X POST "https://api.orbcloud.dev/v1/computers/$COMP_ID/config" \
  -H "Authorization: Bearer $ORB_KEY" \
  -H 'Content-Type: application/toml' \
  --data-binary @orb.toml

curl -s -X POST "https://api.orbcloud.dev/v1/computers/$COMP_ID/build" \
  -H "Authorization: Bearer $ORB_KEY"

curl -s -X POST "https://api.orbcloud.dev/v1/computers/$COMP_ID/agents" \
  -H "Authorization: Bearer $ORB_KEY" \
  -H 'Content-Type: application/json' -d '{}'

# Use
VM="https://${COMP_ID:0:8}.orbcloud.dev"
curl "$VM/navigate?url=https://example.com"
curl "$VM/screenshot" -o screenshot.jpg
curl "$VM/cookies"

# Sleep ($0/hr while frozen)
curl -X POST "https://api.orbcloud.dev/v1/computers/$COMP_ID/agents/demote" \
  -H "Authorization: Bearer $ORB_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"port": PORT}'

# Wake (~500ms)
curl -X POST "https://api.orbcloud.dev/v1/computers/$COMP_ID/agents/promote" \
  -H "Authorization: Bearer $ORB_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"port": PORT}'
```

## API Endpoints

The browser server exposes these endpoints on the VM:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Server and browser status |
| `/navigate?url=X` | GET | Navigate to URL, returns title and cookie count |
| `/screenshot` | GET | JPEG screenshot of current page |
| `/cookies` | GET | All cookies in the browser context |
| `/status` | GET | Full status including current URL |

## How It Works

1. **Playwright + Chromium** runs inside an Orb Cloud VM
2. **CRIU** (Checkpoint/Restore in Userspace) freezes the entire process tree — Node.js, Chromium, renderer processes — to NVMe storage
3. On wake, CRIU restores everything in ~500ms. The browser doesn't know it was frozen.

This is different from saving/restoring cookies. The actual browser process — memory, file descriptors, network state — is preserved. It's like hibernating a laptop, but for a headless browser in the cloud.

## Why This Exists

Every browser automation tool has the same problem: sessions are ephemeral. Restart the container, lose your cookies. Timeout, lose your login. Scale to 1,000 browsers, pay $30,000/month for VMs that sit idle 90% of the time.

orb-browser solves this:
- **$0 when idle** — sleeping browsers use no compute
- **No re-login** — sessions survive indefinitely
- **500ms wake** — not minutes, not seconds, milliseconds

## Testing

```bash
ORB_API_KEY=orb_... ./test/e2e.sh
```

## License

MIT
