// node render.js in.html out.pdf   (page size, margins and footers come from the page's own @page CSS)
const { chromium } = require(process.env.PW || "/opt/node-tools/node_modules/playwright");
const [, , inp, out] = process.argv;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto("file://" + inp, { waitUntil: "load" });
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: out, preferCSSPageSize: true, printBackground: true });
  await b.close();
})();
