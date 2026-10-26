/** Optional release-engineering QA, not a runtime dependency or canonical PDF renderer.
 * node scripts/phase10_render_qa.mjs ACCEPTANCE_RESULTS OUTPUT_DIR
 * Environment: PLAYWRIGHT_MODULE (absolute module entry), CHROME_EXECUTABLE.
 * Chromium/PW versions, checked HTML bytes, viewports and PDFs are recorded.
 */
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import crypto from 'node:crypto';

const [resultsPath, destination] = process.argv.slice(2);
if (!resultsPath || !destination || !process.env.PLAYWRIGHT_MODULE || !process.env.CHROME_EXECUTABLE) {
  throw new Error('Supply results/output paths and PLAYWRIGHT_MODULE/CHROME_EXECUTABLE');
}
const { chromium } = await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
const results = JSON.parse(fs.readFileSync(resultsPath, 'utf8'));
const output = path.resolve(destination);
fs.mkdirSync(output, { recursive: false });
const browser = await chromium.launch({ executablePath: process.env.CHROME_EXECUTABLE, headless: true });
const digest = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const manifest = { method: 'Actual Chromium screen and print rendering; PDF is QA evidence only',
  browser_version: browser.version(), cases: [] };
try {
  for (const id of ['positive_full_path', 'negative_full_path', 'material_unknown',
                    'long_hostile_render', 'human_import_history', 'explicit_human_revision']) {
    const result = results.results.find(item => item.id === id);
    if (!result?.passed || !result.actual.bundle) throw new Error(`No accepted bundle for ${id}`);
    const html = path.join(result.actual.bundle, 'report.html');
    let page = await browser.newPage({ viewport: { width: 1280, height: 960 } });
    const errors = [], externalRequests = [];
    page.on('pageerror', error => errors.push(String(error)));
    await page.route(/^https?:/, route => { externalRequests.push(route.request().url()); return route.abort(); });
    await page.goto(pathToFileURL(html).href, { waitUntil: 'load' });
    await page.screenshot({ path: path.join(output, `${id}-top.png`) });
    await page.screenshot({ path: path.join(output, `${id}-desktop.png`), fullPage: true });
    const desktop = await page.evaluate(() => ({
      width: innerWidth, document_width: document.documentElement.scrollWidth,
      section_count: document.querySelectorAll('section').length,
      active_elements: document.querySelectorAll('script,iframe,object,embed,img,[onerror],[onclick]').length,
      headings: Array.from(document.querySelectorAll('h1,h2')).map(el => el.textContent),
      text_length: document.body.innerText.length,
    }));
    for (const [label, pattern] of [['review', /conflicts|review history/i], ['evidence', /evidence and source/i]]) {
      const heading = page.getByRole('heading', { level: 2, name: pattern }).first();
      if (await heading.count()) {
        await heading.scrollIntoViewIfNeeded();
        await page.screenshot({ path: path.join(output, `${id}-${label}-detail.png`) });
      }
    }
    await page.close();
    page = await browser.newPage({ viewport: { width: 390, height: 844 } });
    page.on('pageerror', error => errors.push(String(error)));
    await page.route(/^https?:/, route => { externalRequests.push(route.request().url()); return route.abort(); });
    await page.goto(pathToFileURL(html).href, { waitUntil: 'load' });
    await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
    await page.screenshot({ path: path.join(output, `${id}-narrow-fresh.png`) });
    await page.screenshot({ path: path.join(output, `${id}-narrow.png`), fullPage: true });
    const narrow = await page.evaluate(() => ({ width: innerWidth,
      document_width: document.documentElement.scrollWidth,
      clipped: Array.from(document.querySelectorAll('section,pre,td,p')).filter(el =>
        el.scrollWidth > el.clientWidth + 2 && ['hidden', 'clip'].includes(getComputedStyle(el).overflowX)
      ).map(el => el.tagName),
    }));
    await page.emulateMedia({ media: 'print' });
    const pdf = path.join(output, `${id}-print.pdf`);
    await page.pdf({ path: pdf, format: 'A4', printBackground: true,
      margin: { top: '14mm', bottom: '14mm', left: '14mm', right: '14mm' } });
    manifest.cases.push({ id, html, html_sha256: digest(fs.readFileSync(html)),
      desktop, narrow, errors, externalRequests, pdf: path.basename(pdf),
      pdf_sha256: digest(fs.readFileSync(pdf)),
      passed: errors.length === 0 && externalRequests.length === 0 && desktop.active_elements === 0 &&
        desktop.document_width <= desktop.width && narrow.document_width <= narrow.width && narrow.clipped.length === 0 });
    await page.close();
  }
} finally {
  await browser.close();
  fs.writeFileSync(path.join(output, 'render-manifest.json'), JSON.stringify(manifest, null, 2) + '\n');
}
if (!manifest.cases.every(item => item.passed)) process.exitCode = 1;
