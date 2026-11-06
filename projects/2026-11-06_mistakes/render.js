// node render.js : renders work/html/slide_NN.html -> out/OSM_gym_mistakes_NN.png (1080x1350), prints each slide's fit/boxes
const { chromium } = require(process.env.PW || "/opt/node-tools/node_modules/playwright");
const path = require("path"), fs = require("fs");
(async () => {
  const P = __dirname, dir = path.join(P, "work/html"), out = path.join(P, "out");
  fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch({ args: ["--allow-file-access-from-files"] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
  const report = {};
  for (const f of fs.readdirSync(dir).filter((f) => f.endsWith(".html")).sort()) {
    await p.goto("file://" + path.join(dir, f)); await p.waitForFunction(() => document.body.dataset.ready == 1); await p.waitForTimeout(250);
    const n = f.match(/\d+/)[0];
    await p.screenshot({ path: path.join(out, `OSM_gym_mistakes_${n}.png`), clip: { x: 0, y: 0, width: 1080, height: 1350 } });
    report[n] = await p.evaluate(() => ({ fit: document.body.dataset.fit, gap: document.body.dataset.gap, boxes: window.boxes }));
    console.log(n, report[n].fit || "", "gap", report[n].gap || "");
  }
  fs.writeFileSync(path.join(P, "work/render_report.json"), JSON.stringify(report, null, 1));
  await b.close();
})();
