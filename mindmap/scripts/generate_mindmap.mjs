#!/usr/bin/env node
/**
 * Generate mind map images using mind-elixir + Puppeteer.
 *
 * Usage:
 *   node generate_mindmap.mjs -i input.txt -o output.png
 *   node generate_mindmap.mjs -i input.txt -o output.svg -f svg
 *   cat input.txt | node generate_mindmap.mjs -o output.png
 *
 * Input: mind-elixir plaintext format (indented markdown list)
 *   - Root Node
 *     - Branch 1
 *       - Leaf 1
 *       - Leaf 2
 *     - Branch 2
 *       - Leaf 3
 */

import puppeteer from "puppeteer";
import { readFileSync, writeFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";
import { parseArgs } from "util";

const __dirname = dirname(fileURLToPath(import.meta.url));

// ---------------------------------------------------------------------------
// CLI args
// ---------------------------------------------------------------------------
const { values: args } = parseArgs({
  options: {
    input:     { type: "string",  short: "i" },
    output:    { type: "string",  short: "o" },
    format:    { type: "string",  short: "f", default: "png" },
    theme:     { type: "string",  short: "t", default: "academic" },
    direction: { type: "string",  short: "d", default: "side" },
    width:     { type: "string",  short: "w", default: "2400" },
    height:    { type: "string",  short: "h", default: "1400" },
    typst:     { type: "boolean", default: false },
    "typst-width": { type: "string", default: "90%" },
    caption:   { type: "string" },
    scale:     { type: "string",  short: "s", default: "3" },
  },
  strict: true,
});

const format    = args.format ?? "png";
const theme     = args.theme ?? "latte";
const direction = args.direction ?? "side";
const vpWidth   = parseInt(args.width ?? "2400", 10);
const vpHeight  = parseInt(args.height ?? "1400", 10);

// ---------------------------------------------------------------------------
// Read input plaintext
// ---------------------------------------------------------------------------
let plaintext;
if (args.input) {
  plaintext = readFileSync(args.input, "utf-8");
} else {
  // Read from stdin
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  plaintext = Buffer.concat(chunks).toString("utf-8");
}

if (!plaintext.trim()) {
  console.error("Error: empty input");
  process.exit(1);
}

if (!args.output) {
  console.error("Error: -o / --output is required");
  process.exit(1);
}
const outputPath = resolve(args.output);

// ---------------------------------------------------------------------------
// Load mind-elixir assets
// ---------------------------------------------------------------------------
const meDir  = resolve(__dirname, "node_modules/mind-elixir/dist");
const jsFile = readFileSync(resolve(meDir, "MindElixir.iife.js"), "utf-8");
const cssFile = readFileSync(resolve(meDir, "MindElixir.css"), "utf-8");
const converterFile = readFileSync(resolve(meDir, "PlaintextConverter.js"), "utf-8");

// Patch converter to work in non-module context (IIFE wrapper)
const converterIIFE = `
var PlaintextConverter = (function() {
  ${converterFile.replace(/^export\s*\{[^}]*\};?\s*$/m, "")}
  return { plaintextToMindElixir: L, plaintextExample: M };
})();
`;

// ---------------------------------------------------------------------------
// Direction constant
// ---------------------------------------------------------------------------
const directionMap = { side: 2, right: 1, left: 0 };
const meDirection = directionMap[direction] ?? 2;

// ---------------------------------------------------------------------------
// Themes
// ---------------------------------------------------------------------------
const academicTheme = {
  name: 'academic',
  palette: ['#1565c0', '#0277bd', '#00838f', '#00695c', '#2e7d32', '#ef6c00'],
  cssVar: {
    '--main-color': '#1a237e',
    '--main-bgcolor': '#e3f2fd',
    '--color': '#4e342e',
    '--bgcolor': '#fff3e0',
    '--selected': '#e65100',
    '--root-color': '#ffffff',
    '--root-bgcolor': '#1565c0',
    '--root-radius': '8px',
    '--main-radius': '5px',
    '--topic-padding': '8px 14px',
  },
};

// ---------------------------------------------------------------------------
// Build HTML
// ---------------------------------------------------------------------------
const html = `<!DOCTYPE html>
<html>
<head>
<style>
${cssFile}
body { margin: 0; background: white; overflow: hidden; }
#map { width: ${vpWidth}px; height: ${vpHeight}px; }
.mind-elixir-toolbar { display: none !important; }
</style>
</head>
<body>
<div id="map"></div>
<script>${jsFile}<\/script>
<script>${converterIIFE}<\/script>
<script>
try {
  var ME = MindElixir.default || MindElixir;
  var data = PlaintextConverter.plaintextToMindElixir(${JSON.stringify(plaintext)});
  var me = new ME({
    el: '#map',
    direction: ${meDirection},
    draggable: false,
    contextMenu: false,
    toolBar: false,
    nodeMenu: false,
    keypress: false,
    allowUndo: false,
    ${theme === "dark" ? "theme: ME.DARK_THEME," : theme === "academic" ? `theme: ${JSON.stringify(academicTheme)},` : ""}
  });
  me.init(data);
  me.toCenter();
  window.__mindElixirReady = true;
  window.__mindElixirError = null;
} catch(e) {
  window.__mindElixirReady = false;
  window.__mindElixirError = e.message;
}
<\/script>
</body>
</html>`;

// ---------------------------------------------------------------------------
// Render with Puppeteer
// ---------------------------------------------------------------------------
const browser = await puppeteer.launch({ headless: true });
const page = await browser.newPage();
const scaleFactor = parseInt(args.scale ?? "3", 10);
await page.setViewport({ width: vpWidth, height: vpHeight, deviceScaleFactor: scaleFactor });

const tmpHtml = resolve(__dirname, ".tmp-mindmap.html");
writeFileSync(tmpHtml, html);

await page.goto(`file://${tmpHtml}`, { waitUntil: "networkidle0" });

// Check for errors
const initError = await page.evaluate(() => window.__mindElixirError);
if (initError) {
  console.error(`Error: mind-elixir init failed: ${initError}`);
  await browser.close();
  process.exit(1);
}

const ready = await page.evaluate(() => window.__mindElixirReady);
if (!ready) {
  await page.waitForFunction(() => window.__mindElixirReady === true, { timeout: 15000 });
}

// Let layout settle
await new Promise((r) => setTimeout(r, 800));

// ---------------------------------------------------------------------------
// Compute content bounding box for tight crop
// ---------------------------------------------------------------------------
const bounds = await page.evaluate(() => {
  // Measure all individual topic nodes + SVG lines to get tight bounding box
  const els = document.querySelectorAll("me-tpc, me-root, me-main, svg.bindbindbindmind-elixir-bindlines");
  const tpcs = document.querySelectorAll("me-tpc, me-root me-tpc");
  if (tpcs.length === 0) return null;

  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  for (const el of tpcs) {
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) continue;
    minX = Math.min(minX, r.left);
    minY = Math.min(minY, r.top);
    maxX = Math.max(maxX, r.right);
    maxY = Math.max(maxY, r.bottom);
  }
  // Also include the SVG lines container
  const svgs = document.querySelectorAll("svg");
  for (const svg of svgs) {
    const r = svg.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) continue;
    minX = Math.min(minX, r.left);
    minY = Math.min(minY, r.top);
    maxX = Math.max(maxX, r.right);
    maxY = Math.max(maxY, r.bottom);
  }

  if (minX === Infinity) return null;
  return { x: minX, y: minY, width: maxX - minX, height: maxY - minY };
});

const padding = 60;
const clip = bounds
  ? {
      x: Math.max(0, bounds.x - padding),
      y: Math.max(0, bounds.y - padding),
      width: Math.min(vpWidth - Math.max(0, bounds.x - padding), bounds.width + padding * 2),
      height: Math.min(vpHeight - Math.max(0, bounds.y - padding), bounds.height + padding * 2),
    }
  : undefined;

// ---------------------------------------------------------------------------
// Export
// ---------------------------------------------------------------------------
if (format === "svg") {
  // For SVG: screenshot as PNG then note it, or extract DOM
  // mind-elixir renders as DOM, not SVG, so we use foreignObject SVG wrapper
  const screenshotBuffer = await page.screenshot({ clip, type: "png", encoding: "base64" });
  const w = clip ? clip.width : vpWidth;
  const h = clip ? clip.height : vpHeight;
  const svgContent = `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="${w}" height="${h}">
  <image width="${w}" height="${h}" href="data:image/png;base64,${screenshotBuffer}"/>
</svg>`;
  writeFileSync(outputPath, svgContent);
} else {
  await page.screenshot({ path: outputPath, clip, type: "png" });
}

await browser.close();

// Cleanup temp
import { unlinkSync } from "fs";
try { unlinkSync(tmpHtml); } catch {}

// ---------------------------------------------------------------------------
// Output
// ---------------------------------------------------------------------------
const { statSync } = await import("fs");
const size = statSync(outputPath).size;
const sizeStr = size >= 1024 * 1024
  ? `${(size / (1024 * 1024)).toFixed(1)} MB`
  : `${(size / 1024).toFixed(0)} KB`;

console.log(`Saved: ${outputPath} (${sizeStr})`);

if (args.typst) {
  const cap = args.caption || "Mind Map";
  const tw = args["typst-width"] || "90%";
  console.log(`\nTypst:`);
  console.log(`#figure(
  image("${outputPath}", width: ${tw}),
  caption: [${cap}],
)`);
}
