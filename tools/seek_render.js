// Deterministic motion-piece renderer (docs/motion/MOTION_SYSTEM.md; Spec 1 build 4, Spec 2 build 1-5).
//
//   node tools/seek_render.js PIECE.html OUT.mp4 --dur 8 [--fps 60] [--sub 3] [--size 1080x1920] [--audio] [--crf 14]
//   node tools/seek_render.js PIECE.html OUTDIR --stills 0.5,1,1.5        one PNG per time + contact sheet (review first)
//   node tools/seek_render.js PIECE.html OUTDIR --beats 120 --dur 8         one PNG per beat + contact sheet
//   node tools/seek_render.js PIECE.html - --determinism --dur 8           same t rendered twice, out of order: hashes must match
//   --query k=v[&k2=v2]   extra URL parameters for the piece (e.g. scene=dht)
//   --dump EXPR           with --stills: also write OUTDIR/dump.json = JSON of the page expression after the last still (e.g. window.boxes)
//
// The piece is a single HTML file that sets window.ready (a Promise) and window.seek(t): every pixel computed from t,
// no CSS animations, no timers, no state carried between frames. It is loaded from https://osm.local/piece/<file>
// with ?render, so local assets resolve next to it; /osm/motion-core.js (studio/src/lib/motionCore.ts, transpiled here),
// /osm/audio.js (motion/lib/audio.js), /osm/fonts/* (brand/fonts) and /osm/brand/* (brand/) are served locally.
// CDN requests (e.g. three.js) go to the network unchanged.
// Video: fps x sub subframes, blended with ffmpeg tmix (sub frames) and decimated to fps = real motion blur.
// Audio (--audio): window.renderAudio() -> base64 WAV (OfflineAudioContext), muxed as AAC 320k.
const { chromium } = require(process.env.PW || "/opt/node-tools/node_modules/playwright");
const fs = require("fs"), path = require("path"), crypto = require("crypto"), { spawn, execFileSync } = require("child_process");
const ROOT = path.resolve(__dirname, "..");
const ts = require(path.join(ROOT, "studio/node_modules/typescript"));

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf("--" + k); return i < 0 ? d : (args[i + 1] && !args[i + 1].startsWith("--") ? args[i + 1] : true); };
const [piece, out] = args;
if (!piece || !out) { console.error("usage: seek_render.js PIECE.html OUT.mp4|OUTDIR|- [--dur s] [--fps 60] [--sub 3] [--size WxH] [--audio] [--stills a,b] [--beats bpm] [--determinism]"); process.exit(2); }
const pieceAbs = path.resolve(piece), pieceDir = path.dirname(pieceAbs);
const [W, H] = String(opt("size", "1080x1920")).split("x").map(Number);
const FPS = Number(opt("fps", 60)), SUB = Number(opt("sub", 3)), DUR = Number(opt("dur", 0)), CRF = String(opt("crf", 14));

const coreJs = ts.transpileModule(fs.readFileSync(path.join(ROOT, "studio/src/lib/motionCore.ts"), "utf8"),
  { compilerOptions: { target: ts.ScriptTarget.ES2020, module: ts.ModuleKind.ES2020 } }).outputText;
const MIME = { ".html": "text/html", ".js": "text/javascript", ".mjs": "text/javascript", ".css": "text/css", ".ttf": "font/ttf", ".otf": "font/otf",
  ".woff2": "font/woff2", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".svg": "image/svg+xml", ".json": "application/json", ".mp4": "video/mp4" };
const inside = (base, p) => { const r = path.resolve(base, p); if (!r.startsWith(base + path.sep) && r !== base) throw new Error("path escapes " + base); return r; };

async function open(browser) {
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  page.on("pageerror", (e) => console.error("PAGE ERROR:", e.message));
  page.on("console", (m) => { if (m.type() === "error") console.error("console:", m.text()); });
  await page.route("https://osm.local/**", async (route) => {
    const u = new URL(route.request().url()); let file;
    try {
      if (u.pathname === "/osm/motion-core.js") return route.fulfill({ status: 200, contentType: "text/javascript", body: coreJs });
      if (u.pathname.startsWith("/osm/audio.js")) file = path.join(ROOT, "motion/lib/audio.js");
      else if (u.pathname.startsWith("/osm/fonts/")) file = inside(path.join(ROOT, "brand/fonts"), decodeURIComponent(u.pathname.slice(11)));
      else if (u.pathname.startsWith("/osm/brand/")) file = inside(path.join(ROOT, "brand"), decodeURIComponent(u.pathname.slice(11)));
      else if (u.pathname.startsWith("/piece/")) file = inside(pieceDir, decodeURIComponent(u.pathname.slice(7)));
      else return route.fulfill({ status: 404, body: "" });
      return route.fulfill({ status: 200, contentType: MIME[path.extname(file).toLowerCase()] || "application/octet-stream", body: fs.readFileSync(file) });
    } catch (e) { return route.fulfill({ status: 404, body: String(e) }); }
  });
  const q = opt("query") ? "&" + String(opt("query")) : "";  // e.g. --query scene=dht (one piece file, several scenes)
  await page.goto(`https://osm.local/piece/${encodeURIComponent(path.basename(pieceAbs))}?render${q}`);
  await page.waitForFunction(() => window.ready !== undefined && typeof window.seek === "function", null, { timeout: 60000 });
  await page.evaluate(() => window.ready);
  return page;
}
const shot = async (page, t) => { await page.evaluate((t) => window.seek(t), t); return page.screenshot({ type: "png", clip: { x: 0, y: 0, width: W, height: H } }); };
const sha = (b) => crypto.createHash("sha256").update(b).digest("hex").slice(0, 16);
const sheet = (files, dst, cols) => execFileSync("montage", [...files, "-tile", `${cols}x`, "-geometry", `${Math.round(W / 5)}x${Math.round(H / 5)}+4+4`,
  "-background", "#0A0F16", "-fill", "white", "-pointsize", "18", "-label", "%t", dst]);

(async () => {
  const browser = await chromium.launch({ args: ["--allow-file-access-from-files", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] });
  const page = await open(browser);
  const meta = await page.evaluate(() => window.meta || {});
  const dur = DUR || meta.dur;
  if (opt("determinism")) {
    const ts_ = [0.37, dur * 0.5, dur - 0.21].map((t) => Math.round(t * FPS) / FPS);
    const a = []; for (const t of ts_) a.push(sha(await shot(page, t)));
    const b = []; for (const t of [...ts_].reverse()) b.unshift(sha(await shot(page, t)));
    const ok = a.every((h, i) => h === b[i]);
    console.log(JSON.stringify({ determinism: ok, times: ts_, first: a, second: b }));
    await browser.close(); process.exit(ok ? 0 : 1);
  }
  const stills = opt("stills") ? String(opt("stills")).split(",").map(Number)
    : opt("beats") ? Array.from({ length: Math.floor(dur / (60 / Number(opt("beats"))) + 1e-6) + 1 }, (_, n) => n * 60 / Number(opt("beats"))).filter((t) => t < dur)
    : null;
  if (stills) {
    fs.mkdirSync(out, { recursive: true }); const files = [];
    for (const t of stills) { const f = path.join(out, `t${t.toFixed(3)}.png`); fs.writeFileSync(f, await shot(page, t)); files.push(f); }
    if (opt("dump")) fs.writeFileSync(path.join(out, "dump.json"), JSON.stringify(await page.evaluate(String(opt("dump"))), null, 1));
    sheet(files, path.join(out, "sheet.jpg"), Math.min(8, files.length));
    console.log(`${files.length} stills -> ${out}/sheet.jpg`);
    await browser.close(); return;
  }
  if (!dur) throw new Error("--dur (or window.meta.dur) required");
  const n = Math.round(dur * FPS) * SUB, vid = out.replace(/\.mp4$/, "") + ".video.mp4";
  const ff = spawn("ffmpeg", ["-v", "error", "-y", "-f", "image2pipe", "-c:v", "png", "-framerate", String(FPS * SUB), "-i", "-",
    "-vf", `tmix=frames=${SUB},select='eq(mod(n\\,${SUB})\\,${SUB - 1})',setpts=N/${FPS}/TB,format=yuv420p`,
    "-r", String(FPS), "-c:v", "libx264", "-preset", "slow", "-crf", CRF, "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
    "-movflags", "+faststart", vid], { stdio: ["pipe", "inherit", "inherit"] });
  const t0 = Date.now();
  for (let i = 0; i < n; i++) {
    const png = await shot(page, i / (FPS * SUB));
    if (!ff.stdin.write(png)) await new Promise((r) => ff.stdin.once("drain", r));
    if (i % (FPS * SUB) === 0) console.log(`  ${(i / (FPS * SUB)).toFixed(1)}s / ${dur}s`);
  }
  ff.stdin.end(); await new Promise((r) => ff.on("close", r));
  let final = vid;
  if (opt("audio")) {
    const b64 = await page.evaluate(async () => (window.renderAudio ? await window.renderAudio() : null));
    if (!b64) throw new Error("--audio: the piece has no window.renderAudio()");
    const wav = out.replace(/\.mp4$/, "") + ".wav"; fs.writeFileSync(wav, Buffer.from(b64, "base64"));
    execFileSync("ffmpeg", ["-v", "error", "-y", "-i", vid, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k",
      "-t", String(dur), "-movflags", "+faststart", out]);
    fs.unlinkSync(vid); final = out;
  } else { fs.renameSync(vid, out); final = out; }
  console.log(`done ${final}: ${n / SUB} frames (${SUB} subframes each) in ${((Date.now() - t0) / 1000).toFixed(0)} s`);
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
