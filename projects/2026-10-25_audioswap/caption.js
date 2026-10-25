// Renders the OSM caption (locked style: white text on a solid #56A0FB bar, IBM Plex Sans Arabic 700,
// 66 px, line-height 1.7, padding 6/30/10, radius 20, no shadow/glow) as a 1080x1920 transparent PNG.
// node caption.js <caption.txt> <centerY 0-1> <out.png>
const { chromium } = require(process.env.PW || "playwright");
const fs = require("fs");
const path = require("path");
(async () => {
  const [txtFile, cy, out, breakAfter] = process.argv.slice(2);
  const text = fs.readFileSync(txtFile, "utf8").trim();
  const fonts = path.resolve(__dirname, "../../brand/fonts");
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face { font-family: PlexAr; src: url('file://${fonts}/IBMPlexSansArabic-Bold.ttf'); font-weight: 700; }
html,body { margin:0; width:1080px; height:1920px; background:transparent; }
.wrap { position:absolute; left:0; width:1080px; top:${Math.round(1920 * cy)}px; transform:translateY(-50%);
        display:flex; justify-content:center; }
.cap { max-width:864px; box-sizing:border-box; direction:rtl; text-align:center; font-family: PlexAr, 'Noto Color Emoji';
       font-weight:700; font-size:66px; line-height:1.7; color:#FFFFFF; background:#56A0FB; border:1px solid #56A0FB;
       padding:6px 30px 10px; border-radius:20px; box-shadow:none; text-shadow:none; }
</style></head><body><div class="wrap"><div class="cap" id="c"></div></div>
<script>const T=${JSON.stringify(text)}, B=${JSON.stringify(breakAfter || '')}; const c=document.getElementById('c');
// visual line breaks only (after each word in B, separated by '|'): the words themselves are not changed
let rest = T; for (const w of (B ? B.split('|') : [])) { const i = rest.indexOf(w + ' '); if (i < 0) continue;
  c.append(rest.slice(0, i + w.length)); c.append(document.createElement('br')); rest = rest.slice(i + w.length + 1); }
c.append(rest);
document.fonts.ready.then(() => document.body.dataset.ready = 1)</script></body></html>`;
  const tmp = path.join(path.dirname(path.resolve(out)), "caption.html");
  fs.writeFileSync(tmp, html);
  const b = await chromium.launch({ args: ["--allow-file-access-from-files"] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto("file://" + tmp);
  await p.waitForFunction(() => document.body.dataset.ready == 1);
  const box = await p.$eval("#c", (e) => { const r = e.getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom]; });
  const shown = await p.$eval("#c", (e) => Array.from(e.childNodes).map((n) => n.nodeName === "BR" ? " " : n.textContent).join(""));
  await p.screenshot({ path: out, omitBackground: true });
  await b.close();
  console.log(JSON.stringify({ box: box.map(Math.round), boxFrac: [box[1] / 1920, box[3] / 1920], exact: shown === text }));
})();
