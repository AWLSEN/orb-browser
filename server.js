const http = require("http");
process.env.PLAYWRIGHT_BROWSERS_PATH = process.env.PLAYWRIGHT_BROWSERS_PATH || "/opt/browsers";
const { chromium } = require("playwright");

let browser = null;
let page = null;
let initError = null;

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, "http://localhost");
  res.setHeader("Content-Type", "application/json");

  try {
    if (url.pathname === "/health") {
      res.end(JSON.stringify({ status: "ok", browserReady: !!browser, error: initError }));

    } else if (url.pathname === "/navigate") {
      if (!page) { res.statusCode = 503; res.end(JSON.stringify({ error: "browser not ready" })); return; }
      const target = url.searchParams.get("url") || "https://example.com";
      await page.goto(target, { waitUntil: "domcontentloaded", timeout: 15000 });
      res.end(JSON.stringify({ title: await page.title(), url: target, cookies: (await page.context().cookies()).length }));

    } else if (url.pathname === "/screenshot") {
      if (!page) { res.statusCode = 503; res.end(JSON.stringify({ error: "browser not ready" })); return; }
      const buf = await page.screenshot({ type: "jpeg", quality: 80 });
      res.setHeader("Content-Type", "image/jpeg");
      res.end(buf);

    } else if (url.pathname === "/cookies") {
      if (!page) { res.statusCode = 503; res.end(JSON.stringify({ error: "browser not ready" })); return; }
      res.end(JSON.stringify({ cookies: await page.context().cookies() }));

    } else if (url.pathname === "/status") {
      res.end(JSON.stringify({
        status: "ok",
        browserReady: !!browser,
        currentUrl: page ? page.url() : null,
        cookies: page ? (await page.context().cookies()).length : 0,
        error: initError,
      }));

    } else {
      res.statusCode = 404;
      res.end(JSON.stringify({ error: "not found" }));
    }
  } catch (e) {
    res.statusCode = 500;
    res.end(JSON.stringify({ error: e.message }));
  }
});

// Start server FIRST, then launch Chrome async.
// Critical: Orb checks health immediately after deploy.
// If Chrome crashes during sync init, the agent dies.
server.listen(process.env.PORT || 3000, "0.0.0.0", () => {
  console.log("Listening on :" + (process.env.PORT || 3000));
  chromium.launch({
    headless: true,
    args: ["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"],
  }).then(async (b) => {
    browser = b;
    page = await (await browser.newContext()).newPage();
    console.log("Browser ready");
  }).catch((e) => {
    initError = e.message;
    console.error("Browser launch failed:", e.message);
  });
});
