const { chromium } = require(process.env.PW);
const path = require('path'); const fs = require('fs');
(async () => {
  const dir = process.argv[2], out = process.argv[3];
  const b = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
  for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.html')).sort()) {
    await p.goto('file://' + path.join(dir, f)); await p.waitForFunction(() => document.body.dataset.ready == 1); await p.waitForTimeout(200); 
    await p.screenshot({ path: path.join(out, f.replace('.html', '.png')), clip: { x: 0, y: 0, width: 1080, height: 1350 } });
    console.log(f);
  }
  await b.close();
})();
