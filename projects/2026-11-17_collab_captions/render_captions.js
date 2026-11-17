// Render captions.html once per SOURCE frame (its own timestamp) as 2160x3840 RGBA PNGs.
//   node render_captions.js SPEC.json OUTDIR
// spec.times = the source video's frame timestamps. Frames without a caption are hard links to one empty frame.
const { chromium } = require(process.env.PW || "/opt/node-tools/node_modules/playwright");
const fs = require("fs"), path = require("path");
const ROOT = path.resolve(__dirname, "../..");
const [specPath, outDir] = process.argv.slice(2);
(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const spec = JSON.parse(fs.readFileSync(specPath, "utf8"));
  const b = await chromium.launch();
  const page = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 2 });
  page.on("pageerror", (e) => console.error("PAGE ERROR:", e.message));
  await page.route("https://osm.local/**", async (route) => {
    const u = new URL(route.request().url()); let file;
    if (u.pathname.startsWith("/osm/fonts/")) file = path.join(ROOT, "brand/fonts", decodeURIComponent(u.pathname.slice(11)));
    else if (u.pathname === "/captions.html") file = path.join(__dirname, "captions.html");
    else if (u.pathname === "/spec.json") file = path.resolve(specPath);
    else return route.fulfill({ status: 404, body: "" });
    const type = { ".html": "text/html", ".ttf": "font/ttf", ".json": "application/json" }[path.extname(file)] || "application/octet-stream";
    return route.fulfill({ status: 200, contentType: type, body: fs.readFileSync(file) });
  });
  await page.goto("https://osm.local/captions.html?spec=/spec.json");
  await page.waitForFunction(() => window.ready !== undefined, null, { timeout: 60000 });
  await page.evaluate(() => window.ready);
  const clip = { x: 0, y: 0, width: 1080, height: 1920 };
  await page.evaluate(() => window.seek(-1));
  const empty = path.join(outDir, "_empty.png");
  fs.writeFileSync(empty, await page.screenshot({ type: "png", omitBackground: true, clip }));
  let drawn = 0;
  for (let i = 0; i < spec.times.length; i++) {
    const f = path.join(outDir, `f_${String(i).padStart(5, "0")}.png`);
    const vis = await page.evaluate((t) => { window.seek(t); return document.getElementById("cap").style.display !== "none"; }, spec.times[i]);
    if (fs.existsSync(f)) fs.unlinkSync(f);
    if (vis) { fs.writeFileSync(f, await page.screenshot({ type: "png", omitBackground: true, clip })); drawn++; } else fs.linkSync(empty, f);
  }
  console.log(`captions: ${spec.times.length} frames, ${drawn} drawn`);
  await b.close();
})();
