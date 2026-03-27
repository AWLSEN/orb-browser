/**
 * orb-browser demo — browser sessions that sleep for $0
 *
 * Usage:
 *   ORB_API_KEY=orb_... node demo.mjs
 */

import { createRequire } from "module";
const require = createRequire(import.meta.url);
const { OrbBrowser } = require("./sdk");
const fs = require("fs");

const apiKey = process.env.ORB_API_KEY;
if (!apiKey) {
  console.error("Set ORB_API_KEY environment variable");
  console.error("Get one at: https://docs.orbcloud.dev");
  process.exit(1);
}

const browser = new OrbBrowser({ apiKey });

try {
  // 1. Deploy a browser (~1-3 min)
  console.log("Deploying browser on Orb Cloud...");
  const { vmUrl } = await browser.deploy();
  console.log(`Browser running at ${vmUrl}`);

  // 2. Navigate
  const nav = await browser.navigate("https://www.google.com");
  console.log(`Page: ${nav.title} | Cookies: ${nav.cookies}`);

  // 3. Screenshot before sleep
  fs.writeFileSync("before.jpg", await browser.screenshot());
  console.log("Saved before.jpg");

  // 4. Sleep — checkpoint to NVMe, $0/hr
  console.log("Sleeping...");
  await browser.sleep();
  console.log("Browser is frozen on NVMe. Costs $0.");

  // 5. Wait (simulating idle time)
  console.log("Waiting 5 seconds (could be hours/days)...");
  await new Promise((r) => setTimeout(r, 5000));

  // 6. Wake — restore in ~500ms
  console.log("Waking...");
  const start = Date.now();
  await browser.wake();
  console.log(`Awake in ${Date.now() - start}ms`);

  // 7. Verify everything survived
  const status = await browser.status();
  console.log(`Still on: ${status.currentUrl} | Cookies: ${status.cookies}`);

  fs.writeFileSync("after.jpg", await browser.screenshot());
  console.log("Saved after.jpg — compare with before.jpg");

  // 8. Clean up
  await browser.destroy();
  console.log("Done. VM destroyed.");
} catch (err) {
  console.error("Error:", err.message);
  await browser.destroy().catch(() => {});
  process.exit(1);
}
