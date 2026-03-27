# orb-browser

Browser sessions that sleep for $0 and wake in 500ms.

Run headless Chrome on [Orb Cloud](https://orbcloud.dev). When idle, checkpoint the entire browser to NVMe — cookies, DOM, localStorage, everything. Wake it up later in ~500ms, exactly where you left off. Still logged in. No re-authentication.

## Get Started (2 minutes)

### 1. Get an Orb Cloud API key

```bash
# Register
curl -X POST https://api.orbcloud.dev/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@example.com"}'
# Returns: {"api_key":"..."}

# Create an org key (use the api_key from above)
curl -X POST https://api.orbcloud.dev/v1/keys \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"name":"my-key"}'
# Returns: {"key":"orb_..."}
```

### 2. Clone and run

```bash
git clone https://github.com/nextbysam/orb-browser.git
cd orb-browser
```

### 3. Try it

```javascript
// demo.mjs
import { OrbBrowser } from "./sdk/index.js";

const browser = new OrbBrowser({ apiKey: "orb_..." });

// Deploy a browser (~1 min)
await browser.deploy();
console.log("Browser running at", browser.vmUrl);

// Navigate
const result = await browser.navigate("https://www.google.com");
console.log("Page:", result.title, "Cookies:", result.cookies);

// Screenshot
const fs = await import("fs");
fs.writeFileSync("before.jpg", await browser.screenshot());
console.log("Screenshot saved to before.jpg");

// Sleep — frozen to NVMe, costs $0/hr
await browser.sleep();
console.log("Sleeping... (frozen, $0)");

// Wake — ~500ms, everything restored
await browser.wake();
console.log("Awake! Browser restored.");

// Verify — same page, same cookies
const after = await browser.navigate("https://www.google.com");
console.log("Still has", after.cookies, "cookies");
fs.writeFileSync("after.jpg", await browser.screenshot());
console.log("Screenshots saved. Compare before.jpg and after.jpg");

// Clean up
await browser.destroy();
```

```bash
node demo.mjs
```

## How It Works

1. **Playwright + Chromium** runs inside an Orb Cloud VM
2. When you call `sleep()`, **CRIU** (Checkpoint/Restore in Userspace) freezes the entire process tree — Node.js, Chromium, renderer processes — to NVMe storage
3. When you call `wake()`, CRIU restores everything in ~500ms. The browser doesn't know it was frozen.

This is different from saving/restoring cookies. The actual browser process — memory, file descriptors, network state — is preserved. It's like hibernating a laptop, but for a headless browser in the cloud.

## SDK API

```javascript
const { OrbBrowser } = require("./sdk");
const browser = new OrbBrowser({ apiKey: "orb_..." });
```

| Method | Description |
|--------|-------------|
| `browser.deploy()` | Create and deploy a browser VM (~1-3 min) |
| `browser.connect({ computerId, agentPort })` | Connect to an existing VM |
| `browser.navigate(url)` | Navigate to URL, returns `{ title, url, cookies }` |
| `browser.screenshot()` | Returns JPEG Buffer |
| `browser.cookies()` | Returns `{ cookies: [...] }` |
| `browser.status()` | Returns `{ browserReady, currentUrl, cookies, error }` |
| `browser.sleep()` | Checkpoint to NVMe ($0 while sleeping) |
| `browser.wake()` | Restore from checkpoint (~500ms) |
| `browser.destroy()` | Delete the VM |

## VM Endpoints

The browser server exposes these HTTP endpoints directly on the VM:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Server and browser status |
| `/navigate?url=X` | GET | Navigate to URL, returns title and cookie count |
| `/screenshot` | GET | JPEG screenshot of current page |
| `/cookies` | GET | All cookies in the browser context |
| `/status` | GET | Full status including current URL |

## Why This Exists

Every browser automation tool has the same problem: sessions are ephemeral. Restart the container, lose your cookies. Timeout, lose your login. Scale to 1,000 browsers, pay for VMs that sit idle 90% of the time.

orb-browser solves this:
- **$0 when idle** — sleeping browsers use no compute
- **No re-login** — sessions survive indefinitely
- **500ms wake** — not minutes, not seconds, milliseconds
- **1,000 sleeping browsers** — costs nearly nothing

## Testing

```bash
ORB_API_KEY=orb_... ./test/e2e.sh
```

## License

MIT
