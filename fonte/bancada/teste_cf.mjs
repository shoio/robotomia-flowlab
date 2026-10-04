// So uma pergunta: o Cloudflare deixa passar agora?
import { chromium } from 'playwright';
const ctx = await chromium.launchPersistentContext('/Users/shoio/.flowlab-bancada', {
  channel: 'chrome', headless: false,
  viewport: { width: 1470, height: 802 }, deviceScaleFactor: 2,
  ignoreDefaultArgs: ['--enable-automation', '--no-sandbox'],
  args: ['--window-position=-3200,0', '--disable-blink-features=AutomationControlled',
         '--disable-backgrounding-occluded-windows'],
});
const p = ctx.pages()[0] || await ctx.newPage();
await p.goto('https://flowlab.io/games/mine', { waitUntil: 'domcontentloaded', timeout: 60000 });
for (let i = 0; i < 12; i++) {
  await p.waitForTimeout(2500);
  const t = await p.title();
  if (!/moment|momento|just a/i.test(t)) { console.log('PASSOU — titulo:', t, '| url:', p.url()); break; }
  if (i === 11) console.log('AINDA NO DESAFIO — titulo:', t);
}
await p.screenshot({ path: '/tmp/_cf.png' });
console.log('webdriver:', await p.evaluate('navigator.webdriver'));
await ctx.close();
