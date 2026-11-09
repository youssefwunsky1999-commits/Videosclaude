// Renders ClaudeAnimationBase frames with a fresh page every few frames (software GL slows down after ~5 frames per page).
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const [dir, out, fps = 24, dur = 7, workers = 3, per = 4] = process.argv.slice(2);
(async () => {
  fs.mkdirSync(out, { recursive: true });
  const n = Math.round(dur * fps), todo = [];
  for (let i = 0; i < n; i++) if (!fs.existsSync(path.join(out, `f${String(i).padStart(5, '0')}.png`))) todo.push(i);
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--allow-file-access-from-files', '--ignore-gpu-blocklist'] });
  const t0 = Date.now(); let done = 0;
  await Promise.all(Array.from({ length: +workers }, async () => {
    while (todo.length) {
      const batch = todo.splice(0, +per);
      const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
      await p.goto('file://' + path.resolve(dir, 'studio.html') + '?render', { waitUntil: 'load', timeout: 120000 });
      await p.waitForFunction('window.ready === true', null, { timeout: 120000 });
      for (const i of batch) {
        const url = await p.evaluate(t => window.renderAt(t), i / fps);
        fs.writeFileSync(path.join(out, `f${String(i).padStart(5, '0')}.png`), Buffer.from(url.slice(url.indexOf(',') + 1), 'base64'));
        done++;
      }
      await p.close();
      console.log(`${done}/${n}  ${((Date.now() - t0) / done / 1000).toFixed(2)} s/frame`);
    }
  }));
  await b.close();
})();
