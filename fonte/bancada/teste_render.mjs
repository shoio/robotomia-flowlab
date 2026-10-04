// A pergunta decisiva: o editor do Flowlab desenha num Chromium SEM TELA?
// Se desenhar, a captura inteira sai do computador do Julio.
import { chromium } from 'playwright';

const url = process.argv[2] || 'https://flowlab.io/game/play/2044776';
const navegador = await chromium.launch({ headless: true });
const ctx = await navegador.newContext({
  viewport: { width: 1470, height: 802 },   // o MESMO tamanho da janela de hoje
  deviceScaleFactor: 2,                      // ...e o mesmo retina: 2940x1604
});
const pag = await ctx.newPage();
await pag.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
await pag.waitForTimeout(12000);
await pag.screenshot({ path: '/tmp/_pw.png' });
console.log('titulo:', await pag.title());
console.log('tamanho da foto: ver sips');
await navegador.close();
