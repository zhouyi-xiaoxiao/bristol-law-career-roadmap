const { chromium } = require('playwright');
const fs = require('node:fs');
const path = require('node:path');
const url = process.argv[2] || 'http://127.0.0.1:8765/';
const root = path.resolve(__dirname, '..');
const evidence = path.join(root, 'evidence'); fs.mkdirSync(evidence, { recursive: true });
let browser;
(async () => {
  browser = await chromium.launch({ channel: 'chrome', headless: true });
  const context = await browser.newContext({ permissions: ['clipboard-read','clipboard-write'] });
  const errors = [], results = [];
  const page = await context.newPage();
  page.on('pageerror', e => errors.push(e.message));
  for (const width of [320, 390, 768, 1024, 1440]) {
    await page.setViewportSize({ width, height: width < 600 ? 844 : 1000 });
    const response = await page.goto(url, { waitUntil: 'networkidle', timeout: 45000 });
    if (response.status() !== 200) throw new Error('HTTP ' + response.status());
    const metrics = await page.evaluate(() => ({
      width: innerWidth, scrollWidth: document.documentElement.scrollWidth,
      headings: document.querySelectorAll('main > section[id]').length,
      h1: document.querySelector('h1').textContent,
      brokenAssets: [...document.images].filter(i => !i.complete || !i.naturalWidth).length,
      links: document.querySelectorAll('#sources a').length
    }));
    if (metrics.scrollWidth > width) throw new Error(`Horizontal overflow at ${width}: ${metrics.scrollWidth}`);
    if (metrics.headings !== 12 || metrics.links < 25) throw new Error('Content is incomplete');
    if (metrics.brokenAssets) throw new Error('Broken image asset');
    results.push({ viewport: width, status: 'PASS', ...metrics });
    if ([390,1440].includes(width)) await page.screenshot({ path: path.join(evidence, `preview-${width}.png`) });
    if (width === 390) {
      await page.locator('.mobile-nav summary').click();
      if (!await page.locator('.mobile-nav').getAttribute('open').then(v=>v!==null)) throw new Error('Mobile menu did not open');
      await page.locator('.mobile-nav a[href="#recruitment"]').click();
      await page.waitForTimeout(400);
      if (!page.url().endsWith('#recruitment')) throw new Error('Mobile navigation failed');
      if (await page.locator('.mobile-nav').getAttribute('open') !== null) throw new Error('Mobile menu did not close');
      await page.locator('#recruitment').scrollIntoViewIfNeeded();
      await page.screenshot({ path: path.join(evidence, 'mobile-recruitment.png') });
    }
  }
  await page.locator('.sidebar a[href="#templates"]').click();
  const template = page.locator('details.template').first();
  await template.locator('summary').click();
  const copy = template.locator('[data-copy]');
  await copy.click();
  await page.waitForFunction(() => document.querySelector('details.template[open] [data-copy]')?.textContent === '已复制', {timeout:5000});
  const copied = await page.evaluate(() => navigator.clipboard.readText());
  if (copied !== await template.locator('.template-text').textContent()) throw new Error('Clipboard content mismatch');
  await page.setViewportSize({width:390,height:844});
  await page.evaluate(() => {document.documentElement.style.fontSize='24px';});
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth);
  if (overflow) throw new Error('Enlarged text overflow');
  const nojs = await browser.newContext({ javaScriptEnabled: false, viewport: {width:390,height:844} });
  const nojsPage = await nojs.newPage(); await nojsPage.goto(url, { waitUntil:'networkidle' });
  if (await nojsPage.locator('#sources a').count() < 25) throw new Error('No-JS source content missing');
  await nojs.close();
  if (errors.length) throw new Error('Browser errors: '+errors.join('; '));
  const report={url,checkedAt:new Date().toISOString(),status:'PASS',results,mobileNavigation:'PASS',templateCopy:'PASS',enlargedText:'PASS',withoutJavaScript:'PASS',pageErrors:errors};
  const file=url.startsWith('http://127.')?'browser-local.json':'browser-live.json';
  fs.writeFileSync(path.join(evidence,file),JSON.stringify(report,null,2));
  console.log(JSON.stringify(report,null,2));
  await browser.close();
})().catch(async e=>{console.error(e.stack);if(browser)await browser.close();process.exitCode=1;});
