// Record scripted, READ-ONLY flows of the real OSM web app (https://osm.sotech.website) as phone-sized video.
//
//   PW=/opt/node-tools/node_modules/playwright node tools/app_record.js STATE_JSON OUT_DIR FLOW [FLOW ...]
//
// STATE_JSON = a Playwright storage state of a signed-in demo account (never committed; credentials stay out of the repo).
// Each flow writes OUT_DIR/<flow>.mp4 (1170x2532 = iPhone 13 at 3x, constant 30 fps) and OUT_DIR/<flow>.json with the
// taps ({t, x, y} as fractions of the screen) for the studio's screenCard tap ripples.
// Frames come from the Chrome DevTools screencast (every repaint, JPEG q96 at 3x: PNG was too slow to keep up with scrolling).
// Flows only navigate, scroll and open lists: nothing is logged, chosen, uploaded, sent or saved, and the Payments
// screen is never opened.
const { chromium, devices } = require(process.env.PW);
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const BASE = 'https://osm.sotech.website/me/';
const CACHE = '/tmp/osm-app-video-cache';

// The open-source Chromium used here has no H.264 decoder, so the app's exercise demo videos (the coach's own MP4s)
// would stay black. Each one is fetched as the app requests it, re-encoded to VP9 WebM (same picture) and served to the
// page in place of the MP4, so the screen recording shows the real demo videos playing.
async function serveDemoVideo(route) {
  const url = new URL(route.request().url());
  const key = url.pathname.replace(/[^a-zA-Z0-9]+/g, '_');
  fs.mkdirSync(CACHE, { recursive: true });
  const webm = path.join(CACHE, key + '.webm');
  if (!fs.existsSync(webm)) {
    const res = await route.fetch({ headers: { ...route.request().headers(), range: 'bytes=0-' } });
    const mp4 = path.join(CACHE, key + '.mp4');
    fs.writeFileSync(mp4, await res.body());
    execFileSync('ffmpeg', ['-y', '-v', 'error', '-i', mp4, '-an', '-vf', 'scale=-2:min(ih\\,1280)', '-c:v', 'libvpx-vp9',
      '-crf', '28', '-b:v', '0', '-deadline', 'realtime', '-cpu-used', '8', '-row-mt', '1', webm]);
  }
  const body = fs.readFileSync(webm);
  await route.fulfill({ status: 200, contentType: 'video/webm', body, headers: { 'accept-ranges': 'none' } });
}
const [stateFile, outDir, ...flows] = process.argv.slice(2);

const FLOWS = {
  // home dashboard: today's workout, meals and the daily challenge
  async home(r) {
    await r.go('home'); await r.wait(2200);
    await r.scroll(260, 900); await r.wait(1400);
    await r.scroll(-260, 700); await r.wait(800);
  },
  // the workout: the coach's own exercise demo videos, sets/reps/rest; next exercise (navigation only)
  async workout(r) {
    await r.go('workout'); await r.wait(1500);
    await r.playVideo(); await r.wait(4200);
    await r.scroll(330, 900); await r.wait(1600);
    await r.scroll(-330, 700); await r.wait(500);
    await r.tap('button[aria-label="Open exercise 5"]'); await r.wait(900);
    await r.playVideo(); await r.wait(3800);
    await r.tap('button[aria-label="Open exercise 8"]'); await r.wait(900);
    await r.playVideo(); await r.wait(3800);
  },
  // the diet plan: macros, grams, cooked weights; the swap list for chicken (opened, nothing chosen)
  async diet(r) {
    await r.go('diet'); await r.wait(2000);
    await r.scroll(420, 1100); await r.wait(900);
    await r.tap('text=Swap (9) >> nth=0'); await r.wait(1800);
    await r.scroll(380, 1400); await r.wait(1600);
    await r.scroll(-380, 1000); await r.wait(600);
    await r.tap('text=Swap (9) >> nth=0'); await r.wait(1200);
  },
  // the calorie calculator: values typed into the form (a calculator, nothing is saved), the result
  async calculator(r) {
    await r.go('calorie-calculator'); await r.wait(1500);
    const fill = async (sel, v) => { await r.tap(sel); await r.p.fill(sel, ''); await r.p.type(sel, v, { delay: 110 }); await r.wait(250); };
    await fill('input[type=number] >> nth=0', '27');
    await fill('input[type=number] >> nth=1', '178');
    await fill('input[type=number] >> nth=2', '84');
    await r.p.locator('select').nth(1).evaluate((el) => {  // activity level -> "Active" (a native picker can't be filmed)
      el.selectedIndex = 2; el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true }));
    }); await r.wait(900);
    await r.scroll(520, 1300); await r.wait(2600);
    await r.scroll(420, 1100); await r.wait(2200);
  },
  // today's challenge, the points, the leaderboard (read only: no upload)
  async challenges(r) {
    await r.go('challenges'); await r.wait(2400);
    await r.scroll(300, 900); await r.wait(1200);
    await r.tap('a[href="/me/challenges/leaderboard"]'); await r.wait(2800);
  },
  async points(r) {
    await r.go('points/about'); await r.wait(2200);
    await r.scroll(500, 1600); await r.wait(1500);
    await r.scroll(500, 1600); await r.wait(1500);
  },
  async badges(r) {
    await r.go('badges'); await r.wait(2000);
    await r.scroll(700, 2200); await r.wait(1200);
  },
  async streak(r) {
    await r.go('streak'); await r.wait(2200);
    await r.scroll(300, 900); await r.wait(1500);
  },
  // progress: weight + measurements (the photo strip at the bottom is not filmed)
  async progress(r) {
    await r.go('progress'); await r.wait(2600);
    await r.scroll(200, 900); await r.wait(1800);
  },
  // the coach chat: text or a voice note (nothing is typed or sent)
  async messages(r) {
    await r.go('messages'); await r.wait(2600);
  },
};

class Rec {
  constructor(p, cdp) { this.p = p; this.cdp = cdp; this.frames = []; this.taps = []; this.t0 = null; }
  now() { return Date.now() / 1000 - this.t0; }
  wait(ms) { return this.p.waitForTimeout(ms); }
  async go(u) {
    await this.p.goto(BASE + u, { waitUntil: 'load' });
    await this.p.waitForLoadState('networkidle', { timeout: 6000 }).catch(() => {});  // video pages keep streaming
  }
  async playVideo() {
    await this.p.evaluate(() => { const v = document.querySelector('video'); if (v) { v.muted = true; v.currentTime = 0; v.play().catch(() => {}); } });
  }
  async tap(sel) {
    const el = this.p.locator(sel).first();
    await el.scrollIntoViewIfNeeded();
    const b = await el.boundingBox();
    const vp = this.p.viewportSize();
    if (b) this.taps.push({ t: +this.now().toFixed(3), x: +((b.x + b.width / 2) / vp.width).toFixed(4), y: +((b.y + b.height / 2) / vp.height).toFixed(4) });
    await el.click();
  }
  // smooth finger-like scroll (ease in-out) of dy CSS px over ms
  async scroll(dy, ms) {
    const n = Math.max(2, Math.round(ms / 16));
    let done = 0;
    for (let i = 1; i <= n; i++) {
      const k = i / n, e = k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
      const want = Math.round(dy * e);
      await this.p.mouse.wheel(0, want - done); done = want;
      await this.p.waitForTimeout(ms / n);
    }
  }
}

(async () => {
  const b = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  for (const name of flows) {
    const ctx = await b.newContext({ ...devices['iPhone 13'], deviceScaleFactor: 3, storageState: stateFile, hasTouch: false, isMobile: true });
    await ctx.route(/\/r2media\/exercises\/videos\/.*\.mp4/, serveDemoVideo);
    const p = await ctx.newPage();
    const cdp = await ctx.newCDPSession(p);
    const r = new Rec(p, cdp);
    const dir = path.join(outDir, name + '_frames');
    fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
    cdp.on('Page.screencastFrame', async (f) => {
      const ts = f.metadata.timestamp;
      if (r.t0 !== null && ts >= r.t0) {
        const file = path.join(dir, String(r.frames.length).padStart(5, '0') + '.jpg');
        fs.writeFileSync(file, Buffer.from(f.data, 'base64'));
        r.frames.push({ file, t: ts - r.t0 });
      }
      await cdp.send('Page.screencastFrameAck', { sessionId: f.sessionId }).catch(() => {});
    });
    await p.goto(BASE + 'home', { waitUntil: 'load' }); await p.waitForTimeout(1500);  // warm the session before filming
    r.t0 = Date.now() / 1000;
    await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 96, maxWidth: 1170, maxHeight: 2532, everyNthFrame: 1 });
    await FLOWS[name](r);
    await r.wait(300);
    const end = r.now();
    await cdp.send('Page.stopScreencast');
    await ctx.close();
    // constant 30 fps: each output frame shows the latest screencast frame at that time
    const list = path.join(dir, 'list.txt');
    const fr = r.frames.filter((f) => f.t >= 0);
    let lines = [];
    for (let i = 0; i < fr.length; i++) {
      const d = (i + 1 < fr.length ? fr[i + 1].t : end) - fr[i].t;
      lines.push(`file '${path.resolve(fr[i].file)}'`, `duration ${Math.max(0.001, d).toFixed(4)}`);
    }
    lines.push(`file '${path.resolve(fr[fr.length - 1].file)}'`);
    fs.writeFileSync(list, lines.join('\n'));
    const out = path.join(outDir, name + '.mp4');
    const first = fr.length ? fr[0].t : 0;
    execFileSync('ffmpeg', ['-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', list,
      '-vf', `tpad=start_duration=${first.toFixed(3)}:start_mode=clone,fps=30,scale=1170:2532:flags=lanczos,format=yuv420p`,
      '-c:v', 'libx264', '-crf', '12', '-preset', 'medium', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
      '-movflags', '+faststart', out]);
    fs.writeFileSync(path.join(outDir, name + '.json'), JSON.stringify({ duration: +end.toFixed(3), frames: fr.length, taps: r.taps }, null, 1));
    fs.rmSync(dir, { recursive: true, force: true });
    console.log(`${name}: ${end.toFixed(1)} s, ${fr.length} screencast frames, ${r.taps.length} taps`);
  }
  await b.close();
})();
