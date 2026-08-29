import { chromium } from 'playwright';
import { mkdir } from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const outDir = path.join(__dirname, '..', 'docs', 'screenshots');
const baseUrl = process.env.APP_URL || 'http://localhost:3001';

const pages = [
  { name: '01-login', path: '/login', wait: 1500 },
  { name: '02-cloud-setup', path: '/cloud-setup', wait: 1000 },
  { name: '03-llm-setup', path: '/llm-setup', wait: 1000 },
  { name: '04-dashboard', path: '/dashboard', wait: 4000 },
  { name: '05-security', path: '/security', wait: 1000 },
  { name: '06-settings', path: '/settings', wait: 1000 },
];

const browser = await chromium.launch();
const context = await browser.newContext({
  viewport: { width: 1440, height: 900 },
  deviceScaleFactor: 1,
});
const page = await context.newPage();

await mkdir(outDir, { recursive: true });

for (const entry of pages) {
  await page.goto(`${baseUrl}${entry.path}`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(entry.wait);
  await page.screenshot({
    path: path.join(outDir, `${entry.name}.png`),
    fullPage: true,
  });
  console.log(`Captured ${entry.name}.png`);
}

// Dark theme dashboard
await page.goto(`${baseUrl}/dashboard`, { waitUntil: 'networkidle' });
await page.waitForTimeout(2500);
const navToggle = page.locator('.nav-theme-toggle');
if (await navToggle.count()) {
  await navToggle.click();
  await page.waitForTimeout(800);
}
await page.screenshot({
  path: path.join(outDir, '07-dashboard-dark.png'),
  fullPage: true,
});
console.log('Captured 07-dashboard-dark.png');

// API docs (backend)
try {
  await page.goto('http://localhost:8000/docs', { waitUntil: 'networkidle', timeout: 10000 });
  await page.waitForTimeout(1500);
  await page.screenshot({
    path: path.join(outDir, '08-api-docs.png'),
    fullPage: true,
  });
  console.log('Captured 08-api-docs.png');
} catch (error) {
  console.warn('Skipped API docs screenshot (backend may be offline).');
}

await browser.close();
console.log(`Screenshots saved to ${outDir}`);
