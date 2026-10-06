// A BANCADA: um Chrome de verdade, fora da tela, dirigido POR DENTRO.
//
// Por que existe: até aqui eu dirigia a tela do Julio — mouse e teclado do
// sistema — e enquanto a captura rodava ele não podia usar o computador. O
// Playwright manda clique e tecla pelo protocolo do próprio navegador, não
// pelo sistema: a janela pode estar atrás de tudo, em -3200 px, e ainda assim
// receber o gesto. A tela fica livre.
//
// A geometria é a MESMA de antes de propósito — viewport 1470x802 com retina
// 2x dá foto de 2940x1604, igual à janela que eu fotografava. Assim todas as
// coordenadas já medidas (a grade do nível, a paleta, os pinos dos blocos)
// continuam valendo.
import { chromium } from 'playwright';
import http from 'node:http';
import fs from 'node:fs';

const PERFIL = '/Users/shoio/.flowlab-bancada';
// O cookie de login do Flowlab e DE SESSAO (expires = -1): o Chrome nao o
// guarda em disco, e todo navegador novo sobe deslogado. Por isso a bancada
// guarda a sessao num arquivo e a injeta ao subir. Ele mora FORA do
// repositorio de proposito — e credencial, nao fonte.
const SESSAO = PERFIL + '/sessao.json';
const PORTA = 8765;
const VISIVEL = process.env.BANCADA_VISIVEL === '1';

const ctx = await chromium.launchPersistentContext(PERFIL, {
  channel: 'chrome',
  headless: false,
  viewport: { width: 1470, height: 802 },
  deviceScaleFactor: 2,
  // O Cloudflare do Flowlab devolvia o desafio PARA SEMPRE: o Playwright abre
  // o Chrome anunciando que e automacao (--enable-automation, a tarja do
  // --no-sandbox, e o navigator.webdriver). Tirando o anuncio, ele passa.
  ignoreDefaultArgs: ['--enable-automation', '--no-sandbox'],
  args: [
    VISIVEL ? '--window-position=40,40' : '--window-position=-3200,0',
    '--disable-blink-features=AutomationControlled',
    '--disable-backgrounding-occluded-windows',
    '--disable-renderer-backgrounding',
    '--disable-features=CalculateNativeWinOcclusion',
  ],
});
if (fs.existsSync(SESSAO)) {
  try {
    const guardada = JSON.parse(fs.readFileSync(SESSAO, 'utf8'));
    await ctx.addCookies(guardada.cookies || []);
    console.log('sessao devolvida ao perfil:', (guardada.cookies || []).length, 'cookies');
  } catch (e) { console.error('sessao guardada ilegivel:', e.message); }
}

const pag = ctx.pages()[0] || await ctx.newPage();

// O diálogo do Chrome ("Sair do site?") deixa de ser um problema de OCR: aqui
// ele chega como evento e eu respondo em uma linha.
pag.on('dialog', async (d) => {
  console.error('dialogo:', d.type(), JSON.stringify(d.message()).slice(0, 80));
  await d.accept().catch(() => {});
});

// as coordenadas que o Python manda são em PIXEL DE IMAGEM (2x)
const css = (v) => v / 2;

async function arrasta({ x0, y0, x1, y1, passos = 45, segura = 0.45 }) {
  await pag.mouse.move(css(x0), css(y0));
  await pag.waitForTimeout(120);
  await pag.mouse.down();
  await pag.waitForTimeout(segura * 1000);
  await pag.mouse.move(css(x1), css(y1), { steps: passos });
  // o tremor do fim: o canvas do Flowlab só reconhece o alvo quando o ponteiro
  // se mexe em cima dele
  for (const [dx, dy] of [[1, 0], [-1, 1], [0, 0]]) {
    await pag.mouse.move(css(x1) + dx, css(y1) + dy);
    await pag.waitForTimeout(90);
  }
  await pag.waitForTimeout(segura * 1000);
  await pag.mouse.up();
  await pag.waitForTimeout(400);
}

const rotas = {
  async ir({ url, espera = 2000 }) {
    await pag.goto(url, { waitUntil: 'domcontentloaded', timeout: 90000 });
    await pag.waitForTimeout(espera);
    return { url: pag.url() };
  },
  async foto({ arquivo }) {
    await pag.screenshot({ path: arquivo });
    return { arquivo };
  },
  async clique({ x, y, duplo = false, botao = 'left' }) {
    await pag.mouse.click(css(x), css(y), { button: botao, clickCount: duplo ? 2 : 1, delay: 40 });
    await pag.waitForTimeout(150);
    return {};
  },
  async lento({ x, y }) {
    // o "clique lento" que abre os ajustes de um bloco: parar em cima,
    // apertar, segurar um instante, soltar
    await pag.mouse.move(css(x), css(y));
    await pag.waitForTimeout(350);
    await pag.mouse.down();
    await pag.waitForTimeout(220);
    await pag.mouse.up();
    await pag.waitForTimeout(250);
    return {};
  },
  async mover({ x, y }) { await pag.mouse.move(css(x), css(y)); return {}; },
  async arrastar(p) { await arrasta(p); return {}; },
  async tecla({ nome }) { await pag.keyboard.press(nome); await pag.waitForTimeout(120); return {}; },
  async segura({ nome, segundos = 1 }) {
    await pag.keyboard.down(nome);
    await pag.waitForTimeout(segundos * 1000);
    await pag.keyboard.up(nome);
    await pag.waitForTimeout(80);
    return {};
  },
  async duas({ anda, pula, antes = 0.25, segurando = 0.45, depois = 0.25,
               toque = 0.18 }) {
    // correr E pular ao mesmo tempo
    //
    // O pulo é SEGURADO, não `press`. `keyboard.press` aperta e solta no mesmo
    // instante, e o motor do jogo lê o estado das teclas uma vez por quadro:
    // um toque de duração zero não aparece em quadro nenhum. Medido na Aula 3
    // — com `press`, o boneco subia 0 px segurando a seta de lado; com a seta
    // de cima segurada 0,2 s sozinha, subia 422 px. O Julio jogou com a mão e
    // o boneco pulou correndo: a fase estava certa, quem não pulava era eu.
    await pag.keyboard.down(anda);
    await pag.waitForTimeout(antes * 1000);
    await pag.keyboard.down(pula);
    await pag.waitForTimeout(toque * 1000);
    await pag.keyboard.up(pula);
    await pag.waitForTimeout(segurando * 1000);
    await pag.keyboard.up(anda);
    await pag.waitForTimeout(depois * 1000);
    return {};
  },
  async roda({ x, y, dx = 0, dy = 0 }) {
    // A roda do mouse. Precisa existir porque a folha do nível pode ser maior
    // que a janela (até 48x32 casas), e o editor de nível não tem a ferramenta
    // mão — ela é do editor de blocos. Sem rolar, a captura só alcança as 16
    // primeiras colunas.
    await pag.mouse.move(css(x), css(y));
    await pag.mouse.wheel(dx, dy);
    await pag.waitForTimeout(350);
    return {};
  },
  async digita({ texto }) { await pag.keyboard.type(texto, { delay: 55 }); return {}; },
  async endereco() { return { url: pag.url() }; },
  async titulo() { return { titulo: await pag.title() }; },
  async aval({ js }) { return { valor: await pag.evaluate(js) }; },
  async area() { return { x: 0, y: 0, w: 1470, h: 802 }; },
  async salva() {
    // guarda a sessao de agora, para o proximo motor subir logado
    const e = await ctx.storageState();
    fs.writeFileSync(SESSAO, JSON.stringify(e));
    return { cookies: e.cookies.length };
  },
};

http.createServer(async (req, res) => {
  let corpo = '';
  for await (const p of req) corpo += p;
  const nome = req.url.split('?')[0].slice(1);
  const fn = rotas[nome];
  res.setHeader('content-type', 'application/json');
  if (!fn) { res.statusCode = 404; return res.end(JSON.stringify({ erro: 'rota ' + nome })); }
  try {
    res.end(JSON.stringify(await fn(corpo ? JSON.parse(corpo) : {})));
  } catch (e) {
    res.statusCode = 500;
    res.end(JSON.stringify({ erro: String(e && e.message || e) }));
  }
}).listen(PORTA, '127.0.0.1', () => console.log('bancada de pe na porta ' + PORTA));
