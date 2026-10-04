// Entrar na conta UMA VEZ. Depois disso o perfil fica guardado em
// ~/.flowlab-bancada e todas as capturas rodam fora da tela.
//
// A janela abre VISIVEL de proposito: a senha e digitada por voce, na pagina
// do proprio Flowlab. Eu nao peco nem guardo senha.
import { chromium } from 'playwright';

const ctx = await chromium.launchPersistentContext('/Users/shoio/.flowlab-bancada', {
  channel: 'chrome',
  headless: false,
  viewport: { width: 1470, height: 802 },
  deviceScaleFactor: 2,
  ignoreDefaultArgs: ['--enable-automation', '--no-sandbox'],
  args: ['--window-position=40,40', '--disable-blink-features=AutomationControlled'],
});
const pag = ctx.pages()[0] || await ctx.newPage();
await pag.goto('https://flowlab.io/games/mine', { waitUntil: 'domcontentloaded' });
console.log('>> Entre com a sua conta do Flowlab nesta janela.');
console.log('>> Assim que a lista MY GAMES aparecer, eu fecho sozinho.');

const limite = Date.now() + 10 * 60 * 1000;
while (Date.now() < limite) {
  await pag.waitForTimeout(2000);
  const u = pag.url();
  if (u.includes('/games/mine') && !u.includes('sign_in')) {
    const temLista = await pag.locator('text=New Game').count().catch(() => 0);
    if (temLista > 0) {
      await pag.screenshot({ path: '/tmp/_login_ok.png' });
      console.log('LOGADO — perfil guardado. Pode fechar o que quiser.');
      await ctx.close();
      process.exit(0);
    }
  }
}
console.log('passaram 10 minutos sem login');
await ctx.close();
process.exit(2);
