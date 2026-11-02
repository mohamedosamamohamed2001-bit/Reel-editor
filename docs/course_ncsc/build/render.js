// node render.js in.html out.pdf [cover|footerTitle]
const { chromium } = require(process.env.PW || "/opt/node-tools/node_modules/playwright");
const [, , inp, out, mode] = process.argv;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto("file://" + inp, { waitUntil: "load" });
  await p.evaluate(() => document.fonts.ready);
  const cover = mode === "cover";
  if (cover) await p.addStyleTag({ content: "@page{size:A4;margin:0} html,body{margin:0;padding:0}" });
  await p.pdf({
    path: out, format: "A4", printBackground: true, preferCSSPageSize: cover,
    margin: cover ? { top: 0, bottom: 0, left: 0, right: 0 } : undefined,
    displayHeaderFooter: !cover,
    headerTemplate: "<div></div>",
    footerTemplate: cover ? "<div></div>" : `<div style="width:100%;font-family:Helvetica,Arial;font-size:7px;color:#4F5B6B;padding:0 14mm;display:flex;justify-content:space-between">
      <span><b style="color:#0A0F16">OSM</b> · Osama Strength Method · ${mode}</span><span>Page <span class="pageNumber"></span> / <span class="totalPages"></span></span></div>`,
  });
  await b.close();
})();
