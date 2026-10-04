// Chromium DE VERDADE (o Chrome instalado), com janela, mas FORA DA TELA.
// O Playwright manda clique e tecla por CDP: nao passa pelo mouse do sistema.
import { chromium } from 'playwright';

const url = process.argv[2] || 'https://flowlab.io/games/mine';
const ctx = await chromium.launchPersistentContext('/Users/shoio/.flowlab-bancada', {
  channel: 'chrome',
  headless: false,
  viewport: { width: 1470, height: 802 },
  deviceScaleFactor: 2,
  args: [
    '--window-position=-3200,0',              // longe da area visivel
    '--disable-backgrounding-occluded-windows',
    '--disable-renderer-backgrounding',
    '--disable-features=CalculateNativeWinOcclusion',
  ],
});
const pag = ctx.pages()[0] || await ctx.newPage();
await pag.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
await pag.waitForTimeout(10000);
await pag.screenshot({ path: '/tmp/_pw2.png' });
console.log('titulo:', await pag.title());
console.log('url  :', pag.url());
await ctx.close();
