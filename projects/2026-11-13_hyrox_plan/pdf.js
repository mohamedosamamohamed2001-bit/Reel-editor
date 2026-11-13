// node pdf.js : plan.html -> OSM_HYROX_8_Week_Plan.pdf (A4, backgrounds on)
const { chromium } = require(process.env.PW || "/opt/node-tools/node_modules/playwright");
const path = require("path");
(async () => {
  const b = await chromium.launch({ args: ["--allow-file-access-from-files"] });
  const p = await b.newPage();
  await p.goto("file://" + path.join(__dirname, "plan.html"));
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: path.join(__dirname, "out", "OSM_HYROX_8_Week_Plan.pdf"), format: "A4", printBackground: true, preferCSSPageSize: true });
  await b.close();
})();
