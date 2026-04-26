const path = require("path");
const fs = require("fs");
const { execFileSync } = require("child_process");

function findChromiumBinary() {
  const cacheRoot = path.join(process.env.HOME || "", ".cache", "ms-playwright");
  if (!fs.existsSync(cacheRoot)) {
    throw new Error(`Playwright browser cache not found: ${cacheRoot}`);
  }

  const candidates = fs
    .readdirSync(cacheRoot)
    .filter((name) => name.startsWith("chromium-"))
    .sort()
    .reverse()
    .map((name) => path.join(cacheRoot, name, "chrome-linux64", "chrome"))
    .filter((candidate) => fs.existsSync(candidate));

  if (!candidates.length) {
    throw new Error("No cached Chromium binary found under ~/.cache/ms-playwright.");
  }

  return candidates[0];
}

async function main() {
  const htmlPath = path.resolve(__dirname, "UsedCarPricePoster441.html");
  const outPdf = path.resolve(__dirname, "UsedCarPricePoster441.pdf");
  const chrome = findChromiumBinary();
  execFileSync(
    chrome,
    [
      "--headless",
      "--no-sandbox",
      "--disable-gpu",
      `--print-to-pdf=${outPdf}`,
      `file://${htmlPath}`,
    ],
    { stdio: "inherit" }
  );
  console.log(`Wrote: ${outPdf}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
