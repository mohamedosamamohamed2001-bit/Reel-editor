// Screenshot slide pages at exactly 1080x1350:  node shoot.js OUTDIR page1.html page2.html ...
// Prints each page's text boxes (and whether any line overflows) for the layout checks.
const { chromium } = require(process.env.PW || "/opt/node-tools/node_modules/playwright");
const path = require("path");
(async () => {
  const [out, ...pages] = process.argv.slice(2);
  const b = await chromium.launch({ args: ["--allow-file-access-from-files"] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
  for (const [i, f] of pages.entries()) {
    await p.goto("file://" + path.resolve(f));
    await p.waitForFunction(() => window.done === true, null, { timeout: 30000 });
    await p.evaluate(() => Promise.all([...document.images].map((im) => im.decode())));
    console.log(`slide ${i + 1}`, JSON.stringify(await p.evaluate(() => window.boxes)));
    await p.screenshot({ path: path.join(out, `Slide ${String(i + 1).padStart(2, "0")}.png`), clip: { x: 0, y: 0, width: 1080, height: 1350 } });
  }
  await b.close();
})();
