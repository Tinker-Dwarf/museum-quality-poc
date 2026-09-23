import { createServer } from "vite";
import { chromium } from "playwright";
import { mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const outPath = join(root, "artifacts/codie-p1/default-camera.png");
mkdirSync(dirname(outPath), { recursive: true });

const server = await createServer({
  root,
  server: { port: 5179, strictPort: true },
  logLevel: "error",
});
await server.listen();
const url = "http://127.0.0.1:5179/";

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({
  viewport: { width: 1440, height: 900 },
  deviceScaleFactor: 1,
});
const errors = [];
page.on("pageerror", (e) => errors.push(String(e)));
page.on("console", (msg) => {
  if (msg.type() === "error") errors.push(msg.text());
});

await page.goto(url, { waitUntil: "networkidle", timeout: 60000 });
await page.waitForSelector("canvas", { timeout: 30000 });
// Settle first paint / fonts / soft shadows
await page.waitForTimeout(2800);
await page.screenshot({ path: outPath, fullPage: false });

await browser.close();
await server.close();

if (errors.length) {
  console.error("Console/page errors:", errors);
  process.exitCode = 1;
}
console.log(JSON.stringify({ ok: errors.length === 0, outPath, errors }, null, 2));
