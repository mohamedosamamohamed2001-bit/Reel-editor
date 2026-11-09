// Render the transparent OSM overlay layer to a PNG sequence (RGBA), 1 file per output frame.
//   node render_overlay.js SPEC.json OUTDIR [--fps 30] [--stills 1.2,3.4]
// Frames with nothing on screen are hard links to one empty frame (fast). Same asset routing as tools/seek_render.js.
const { chromium } = require(process.env.PW || "/opt/node-tools/node_modules/playwright");
const fs = require("fs"), path = require("path");
const ROOT = path.resolve(__dirname, "../..");
const ts = require(path.join(ROOT, "studio/node_modules/typescript"));
const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf("--" + k); return i < 0 ? d : args[i + 1]; };
const [specPath, outDir] = args;
const FPS = Number(opt("fps", 30));
const coreJs = ts.transpileModule(fs.readFileSync(path.join(ROOT, "studio/src/lib/motionCore.ts"), "utf8"),
  { compilerOptions: { target: ts.ScriptTarget.ES2020, module: ts.ModuleKind.ES2020 } }).outputText;
const MIME = { ".html": "text/html", ".js": "text/javascript", ".ttf": "font/ttf", ".png": "image/png", ".jpg": "image/jpeg", ".json": "application/json", ".svg": "image/svg+xml" };
(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const b = await chromium.launch();
  const page = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on("pageerror", (e) => console.error("PAGE ERROR:", e.message));
  await page.route("https://osm.local/**", async (route) => {
    const u = new URL(route.request().url()); let file;
    if (u.pathname === "/osm/motion-core.js") return route.fulfill({ status: 200, contentType: "text/javascript", body: coreJs });
    if (u.pathname.startsWith("/osm/fonts/")) file = path.join(ROOT, "brand/fonts", decodeURIComponent(u.pathname.slice(11)));
    else if (u.pathname.startsWith("/osm/brand/")) file = path.join(ROOT, "brand", decodeURIComponent(u.pathname.slice(11)));
    else if (u.pathname === "/overlay.html") file = path.join(__dirname, "overlay.html");
    else if (u.pathname.startsWith("/proj/")) file = path.join(__dirname, decodeURIComponent(u.pathname.slice(6)));
    else if (u.pathname === "/spec.json") file = path.resolve(specPath);
    else return route.fulfill({ status: 404, body: "" });
    return route.fulfill({ status: 200, contentType: MIME[path.extname(file)] || "application/octet-stream", body: fs.readFileSync(file) });
  });
  await page.goto("https://osm.local/overlay.html?spec=/spec.json");
  await page.waitForFunction(() => typeof window.seek === "function" && window.ready !== undefined, null, { timeout: 60000 });
  await page.evaluate(() => window.ready);
  const dur = await page.evaluate(() => window.meta.dur);
  const shot = async (t) => {
    const visible = await page.evaluate((t) => { window.seek(t); return [...document.querySelectorAll("#cap,#hud,#lt,#end,#titles > div,.layer")].some((e) => e.style.display !== "none"); }, t);
    return visible ? page.screenshot({ type: "png", omitBackground: true, clip: { x: 0, y: 0, width: 1080, height: 1920 } }) : null;
  };
  const stills = opt("stills");
  if (stills) {
    for (const t of stills.split(",").map(Number)) { const buf = await shot(t); if (buf) fs.writeFileSync(path.join(outDir, `still_${t.toFixed(2)}.png`), buf); }
    await b.close(); return;
  }
  const empty = path.join(outDir, "_empty.png");
  await page.evaluate(() => { for (const e of document.querySelectorAll("#cap,#hud,#lt,#end,#titles > div,.layer")) e.style.display = "none"; });
  fs.writeFileSync(empty, await page.screenshot({ type: "png", omitBackground: true, clip: { x: 0, y: 0, width: 1080, height: 1920 } }));
  const N = Math.round(dur * FPS);
  let drawn = 0;
  for (let i = 0; i < N; i++) {
    const f = path.join(outDir, `f_${String(i).padStart(5, "0")}.png`);
    const buf = await shot(i / FPS);
    if (fs.existsSync(f)) fs.unlinkSync(f);
    if (buf) { fs.writeFileSync(f, buf); drawn++; } else fs.linkSync(empty, f);
    if (i % 300 === 0) console.log(`overlay ${i}/${N}`);
  }
  console.log(`overlay done: ${N} frames, ${drawn} drawn`);
  await b.close();
})();
