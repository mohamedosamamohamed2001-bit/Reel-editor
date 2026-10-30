// Head-zone check: every text block's rendered box vs. the YuNet face box of its photo (work/layout_info.json),
// forbidden zone = face box grown 30 px + the column above it up to the top of the frame. Also checks the frame edges.
const { chromium } = require(process.env.PW);
const path = require('path'); const fs = require('fs');
(async () => {
  const P = __dirname, info = JSON.parse(fs.readFileSync(path.join(P, 'work/layout_info.json')));
  const b = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 } });
  let bad = 0;
  for (const n of Object.keys(info).sort()) {
    await p.goto('file://' + path.join(P, `work/html/slide_${n}.html`)); await p.waitForFunction(() => document.body.dataset.ready == 1);
    const boxes = await p.$$eval('.block', els => els.map(e => { const r = e.getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom]; }));
    const [fx, fy, fw, fh] = info[n].face, g = 30, z = [fx - g, 0, fx + fw + g, fy + fh + g];
    for (const [l, t, r, bt] of boxes) {
      const hit = l < z[2] && r > z[0] && t < z[3] && bt > z[1];
      const edge = l < 30 || r > 1050 || t < 120 || bt > 1320;
      if (hit || edge) bad++;
      console.log(`${n} block ${[l, t, r, bt].map(Math.round)} head-zone ${z} ${hit ? 'OVERLAP' : 'clear'}${edge ? ' EDGE' : ''}`);
    }
  }
  await b.close(); console.log(bad ? `${bad} problem(s)` : 'all blocks clear of head zones and edges'); process.exit(bad ? 1 : 0);
})();
