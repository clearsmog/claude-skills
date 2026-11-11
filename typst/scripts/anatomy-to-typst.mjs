#!/usr/bin/env node
// Freeze an Anatomy figure page into a plain SVG that Typst can read.
// Anatomy styles its SVG with CSS custom properties, which Typst's SVG renderer ignores (shapes come out black).
// This opens the built page in headless Chrome (via Anatomy's drive.mjs), bakes every computed paint into
// presentation attributes, drops classes and <style>, and stacks the figure's SVG layers into one file.
// WebGL canvases are not captured: shader layers (plume, water, glow) are lost in the still.
//
// usage: node anatomy-to-typst.mjs <page-light.html> <out.svg> [--actions pose.json] [--layers "<css selector>"]
//   --actions  drive.mjs actions to reach a pose first, e.g. [["key"," "],["wait",2500]]
//   --layers   SVG layers to freeze, back to front (default: the outermost svg.iso-svg elements in the page)
import { spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir, homedir } from "node:os";
import { join, resolve } from "node:path";

const argv = process.argv.slice(2);
const opt = (name) => { const i = argv.indexOf(name); return i < 0 ? null : argv.splice(i, 2)[1]; };
const actionsFile = opt("--actions");
const layers = opt("--layers") || "svg.iso-svg:not(svg.iso-svg svg)";
const [page, out] = argv;
if (!page || !out) { console.error("usage: anatomy-to-typst.mjs <page-light.html> <out.svg> [--actions pose.json] [--layers sel]"); process.exit(2); }

const DRIVE = join(homedir(), ".claude/skills/anatomy/scripts/drive.mjs");
const PROPS = ["fill", "fill-opacity", "fill-rule", "stroke", "stroke-width", "stroke-opacity", "stroke-linecap",
  "stroke-linejoin", "stroke-dasharray", "stroke-dashoffset", "stroke-miterlimit", "opacity", "stop-color", "stop-opacity",
  "font-family", "font-size", "font-weight", "font-style", "text-anchor", "dominant-baseline", "letter-spacing", "filter",
  "mask", "clip-path", "visibility"];

const bake = `(() => {
  const PROPS = ${JSON.stringify(PROPS)};
  const SKIP = { "fill-opacity": "1", "stroke-opacity": "1", "opacity": "1", "fill-rule": "nonzero", "stroke-dasharray": "none",
    "stroke-dashoffset": "0px", "stroke-miterlimit": "4", "visibility": "visible", "dominant-baseline": "auto",
    "text-anchor": "start", "stroke-linecap": "butt", "stroke-linejoin": "miter", "stroke-width": "1px", "stroke": "none" };
  const STOP = new Set(["stop-color", "stop-opacity"]), FONT = /^(font-|text-anchor|dominant-baseline|letter-spacing)/;
  const live = [...document.querySelectorAll(${JSON.stringify(layers)})];
  if (!live.length) return JSON.stringify({ error: "no SVG layers match the --layers selector" });
  const vb = live[0].viewBox.baseVal;
  const blurs = new Map();
  const groups = live.map((svg, n) => {
    const clone = svg.cloneNode(true);
    const a = [svg, ...svg.querySelectorAll("*")], b = [clone, ...clone.querySelectorAll("*")];
    a.forEach((el, i) => {
      const t = b[i], cs = getComputedStyle(el), tag = el.tagName.toLowerCase();
      [...t.attributes].forEach((at) => (at.name === "class" || at.name === "style" || at.name.startsWith("data-") || at.name.startsWith("aria-")) && t.removeAttribute(at.name));
      if (cs.display === "none") { t.setAttribute("display", "none"); return; }
      for (const p of PROPS) {
        if (STOP.has(p) !== (tag === "stop")) continue;
        if (FONT.test(p) && !/^(text|tspan|g|svg)$/.test(tag)) continue;
        let v = cs.getPropertyValue(p).trim();
        if (!v || v === "normal" || SKIP[p] === v || /^(filter|mask|clip-path)$/.test(p) && v === "none") continue;
        if (p === "filter") {
          const m = v.match(/^blur\\(([\\d.]+)px\\)$/);
          if (m) { if (!blurs.has(m[1])) blurs.set(m[1], "blur" + blurs.size); v = "url(#" + blurs.get(m[1]) + ")"; }
        }
        v = v.replace(/url\\("?[^#")]*#([^")]*)"?\\)/g, (_, id) => "url(#" + id + ")");
        t.setAttribute(p, v);
      }
    });
    clone.querySelectorAll("style,title,desc,script,foreignObject").forEach((el) => el.remove());
    clone.querySelectorAll("[id]").forEach((el) => el.id = "L" + n + "-" + el.id);
    const inner = clone.innerHTML.replace(/url\\(#(?!L\\d+-|blur\\d)/g, "url(#L" + n + "-").replace(/href="#(?!L\\d+-)/g, 'href="#L' + n + '-');
    return "<g>" + inner + "</g>";
  });
  const defs = [...blurs].map(([px, id]) => '<filter id="' + id + '" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="' + px + '"/></filter>').join("");
  window.__ats = JSON.stringify({ vb: [vb.x, vb.y, vb.width, vb.height], body: (defs ? "<defs>" + defs + "</defs>" : "") + groups.join("") });
  return window.__ats.length;
})()`;

// drive.mjs prints each eval result on one line, and lines over 64 KB get cut, so read the result back in chunks.
const CHUNK = 30000, MAX_CHUNKS = 400;
const dir = mkdtempSync(join(tmpdir(), "anatomy-typst-"));
const pre = actionsFile ? JSON.parse(readFileSync(actionsFile, "utf8")) : [["wait", 800]];
const reads = Array.from({ length: MAX_CHUNKS }, (_, i) => ["eval", `(window.__ats || "").slice(${i * CHUNK}, ${(i + 1) * CHUNK})`]);
const actionsPath = join(dir, "actions.json");
writeFileSync(actionsPath, JSON.stringify([...pre, ["eval", bake], ...reads]));
const r = spawnSync(process.execPath, [DRIVE, resolve(page), "--actions", actionsPath, "--reduced"], { encoding: "utf8", maxBuffer: 1 << 28 });
const lines = (r.stdout || "").split("\n").filter((l) => l.startsWith("eval: ")).map((l) => JSON.parse(l.slice(6)));
if (!lines.length || typeof lines[0] !== "number") { console.error(r.stdout, r.stderr); process.exit(1); }
const json = lines.slice(1).join("");
if (json.length !== lines[0]) { console.error(`read ${json.length} of ${lines[0]} chars; raise MAX_CHUNKS`); process.exit(1); }
const res = JSON.parse(json);
if (res.error) { console.error(res.error); process.exit(1); }
const [x, y, w, h] = res.vb;
writeFileSync(out, `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="${x} ${y} ${w} ${h}" width="${w}" height="${h}">${res.body}</svg>\n`);
console.log(`wrote ${out} (${w}x${h})`);
