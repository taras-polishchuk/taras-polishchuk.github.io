// Five user journeys. Each one fails on what a visitor would actually notice.
const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
const SITE = 'https://taras-polishchuk.github.io';

function sitemapPaths() {
  const xml = fs.readFileSync(path.join(ROOT, 'sitemap.xml'), 'utf8');
  return [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1].trim().replace(SITE, '') || '/');
}

test('home: loads, has the name in the title, no JS errors', async ({ page }) => {
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  const res = await page.goto('/');
  expect(res.status()).toBeLessThan(400);
  await expect(page).toHaveTitle(/Taras Polishchuk/);
  await expect(page.locator('h1').first()).toBeVisible();
  expect(errors, errors.join('\n')).toEqual([]);
});

test('home: no horizontal overflow', async ({ page }) => {
  await page.goto('/');
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  expect(overflow).toBeLessThanOrEqual(2);
});

test('home: every internal link opens', async ({ page, request }) => {
  await page.goto('/');
  const hrefs = await page.$$eval('a[href]', (as) => as.map((a) => a.href));
  const origin = new URL(page.url()).origin;
  const internal = [...new Set(hrefs.filter((h) => h.startsWith(origin)).map((h) => h.split('#')[0]))];
  expect(internal.length).toBeGreaterThan(0);
  const broken = [];
  for (const url of internal) {
    const r = await request.get(url);
    if (r.status() >= 400) broken.push(`${r.status()} ${url}`);
  }
  expect(broken, broken.join('\n')).toEqual([]);
});

test('sitemap: every page loads with a title', async ({ page }) => {
  const bad = [];
  for (const p of sitemapPaths()) {
    const res = await page.goto(p);
    const title = (await page.title()).trim();
    if (!res || res.status() >= 400 || !title) bad.push(`${res && res.status()} ${p} title=${JSON.stringify(title)}`);
  }
  expect(bad, bad.join('\n')).toEqual([]);
});

test('home: images are not broken', async ({ page }) => {
  await page.goto('/');
  await page.waitForLoadState('load');
  const broken = await page.$$eval('img', (imgs) =>
    imgs.filter((i) => i.complete && i.naturalWidth === 0 && i.loading !== 'lazy').map((i) => i.currentSrc || i.src));
  expect(broken, broken.join('\n')).toEqual([]);
});
