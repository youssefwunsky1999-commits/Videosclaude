// Uso: node scripts/stills.mjs 30 140 190 ...  -> out/c_<frame>.png (un único bundle)
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import { existsSync } from "node:fs";
import path from "node:path";

const SHELL = "/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell";
const browserExecutable = existsSync(SHELL) ? SHELL : null;
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const composition = await selectComposition({ serveUrl, id: "Mente404Dinero", browserExecutable });
for (const f of process.argv.slice(2).map(Number)) {
  await renderStill({ serveUrl, composition, frame: f, output: `out/c_${f}.png`, scale: 0.5, browserExecutable, overwrite: true });
  console.log("ok", f);
}
