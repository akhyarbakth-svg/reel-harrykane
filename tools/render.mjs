// Renders reel.html frame-by-frame in headless Chrome and pipes JPEG frames into ffmpeg.
//   node render.mjs video <out.mp4> [audio.wav]
//   node render.mjs stills <outDir> <t1,t2,...>
import puppeteer from 'puppeteer-core';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { spawn, execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const FFMPEG = execFileSync('python', ['-I', '-c', 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())']).toString().trim();
const TYPES = { '.html': 'text/html', '.jpg': 'image/jpeg', '.png': 'image/png', '.js': 'text/javascript', '.css': 'text/css' };

const [mode, out, extra] = process.argv.slice(2);

const server = http.createServer((req, res) => {
  const p = path.join(ROOT, decodeURIComponent(new URL(req.url, 'http://x').pathname));
  if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); res.end(); return; }
  res.writeHead(200, { 'Content-Type': TYPES[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
});
await new Promise(r => server.listen(0, '127.0.0.1', r));
const url = `http://127.0.0.1:${server.address().port}/reel.html?render=1`;

const browser = await puppeteer.launch({ executablePath: CHROME, headless: true, args: ['--force-device-scale-factor=1', '--disable-background-timer-throttling'] });
const page = await browser.newPage();
page.on('console', m => { if (m.type() === 'error') console.error('[page]', m.text()); });
page.on('pageerror', e => console.error('[pageerror]', e.message));
await page.setViewport({ width: 600, height: 1000 });
await page.goto(url, { waitUntil: 'networkidle0', timeout: 120000 });
await page.evaluate(() => window.__ready);
const fontsOk = await page.evaluate(() => ['Unbounded', 'JetBrains Mono', 'Chakra Petch'].map(f => `${f}:${document.fonts.check(`700 20px "${f}"`)}`).join(' '));
console.log('fonts', fontsOk);
const { DUR, FPS } = await page.evaluate(() => ({ DUR: window.__DUR, FPS: window.__FPS }));

if (mode === 'stills') {
  fs.mkdirSync(out, { recursive: true });
  for (const t of extra.split(',').map(Number)) {
    const data = await page.evaluate(t => window.__frame(t, 0.9), t);
    fs.writeFileSync(path.join(out, `t${t.toFixed(2).padStart(5, '0')}.jpg`), Buffer.from(data.split(',')[1], 'base64'));
  }
  console.log('stills written to', out);
} else {
  const N = Math.round(DUR * FPS);
  const args = ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-'];
  if (extra) args.push('-i', extra);
  args.push('-vf', 'scale=out_range=tv:out_color_matrix=bt709,format=yuv420p', '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-profile:v', 'high',
    '-color_range', 'tv', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-r', String(FPS));
  if (extra) args.push('-c:a', 'aac', '-b:a', '192k', '-map', '0:v', '-map', '1:a', '-t', String(DUR));
  args.push('-movflags', '+faststart', out);
  const ff = spawn(FFMPEG, args, { stdio: ['pipe', 'inherit', 'inherit'] });
  const t0 = Date.now();
  for (let f = 0; f < N; f++) {
    const data = await page.evaluate(t => window.__frame(t, 0.95), f / FPS);
    if (!ff.stdin.write(Buffer.from(data.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 150 === 0) console.log(`frame ${f}/${N}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  console.log('video written to', out, `in ${((Date.now() - t0) / 1000).toFixed(0)}s`);
}
await browser.close();
server.close();
