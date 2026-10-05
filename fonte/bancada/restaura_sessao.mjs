// Devolve ao perfil da bancada a sessao guardada em /tmp/_sessao.json.
// Serve quando o Chrome e morto a forca e o perfil perde o cookie.
import { chromium } from 'playwright';
import fs from 'node:fs';

const estado = JSON.parse(fs.readFileSync('/tmp/_sessao.json', 'utf8'));
const ctx = await chromium.launchPersistentContext('/Users/shoio/.flowlab-bancada', {
  channel: 'chrome', headless: false,
  viewport: { width: 1470, height: 802 }, deviceScaleFactor: 2,
  ignoreDefaultArgs: ['--enable-automation', '--no-sandbox'],
  args: ['--window-position=-3200,0', '--disable-blink-features=AutomationControlled'],
});
await ctx.addCookies(estado.cookies);
const p = ctx.pages()[0] || await ctx.newPage();
await p.goto('https://flowlab.io/games/mine', { waitUntil: 'domcontentloaded', timeout: 60000 });
await p.waitForTimeout(6000);
console.log('titulo:', await p.title(), '| url:', p.url());
await ctx.close();          // fechar com jeito e o que GRAVA o cookie no perfil
