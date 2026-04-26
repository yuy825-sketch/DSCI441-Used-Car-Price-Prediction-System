const path = require("path");
const { chromium } = require("playwright");

async function main() {
  const htmlPath = path.resolve(__dirname, "UsedCarPricePoster441.html");
  const outPdf = path.resolve(__dirname, "UsedCarPricePoster441.pdf");

  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto(`file://${htmlPath}`, { waitUntil: "networkidle" });
  await page.pdf({
    path: outPdf,
    printBackground: true,
    format: "A4",
    margin: { top: "0", right: "0", bottom: "0", left: "0" },
  });
  await browser.close();
  console.log(`Wrote: ${outPdf}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});

