// NIVEL 2: LOGINS DE VERDADE, um por aluno, ao mesmo tempo.
//
// E isto que acontece na sala: 20 maquinas, cada uma digitando o mesmo e-mail
// e a mesma senha. O teste anterior (teste_20_sessoes.mjs) copiava UMA sessao
// ja aberta 20 vezes — mede carga, nao mede login. As duas perguntas que so
// este aqui responde:
//
//   1. o Flowlab INVALIDA as sessoes antigas quando entra uma nova?
//      (se invalidar, o aluno 1 cai quando o aluno 2 entra — e a aula acaba)
//   2. ele trava o endereco depois de muitos logins seguidos? (429)
//
// A SENHA NAO FICA AQUI. Ela e lida do Chaveiro do macOS na hora de rodar.
// Para guardar, uma vez, no terminal (ele pergunta a senha num prompt do
// sistema; nao fica no historico):
//
//     security add-generic-password -a SEU@EMAIL -s flowlab-bancada -w
//
// Subo em ondas — 2, 5, 10, 20 — e paro na primeira que falhar, para nao
// martelar a conta a toa.
import { chromium } from 'playwright';
import { execFileSync } from 'node:child_process';

function doChaveiro() {
  const bruto = execFileSync('security',
    ['find-generic-password', '-s', 'flowlab-bancada'], { encoding: 'utf8' });
  const email = (bruto.match(/"acct"<blob>="([^"]+)"/) || [])[1];
  const senha = execFileSync('security',
    ['find-generic-password', '-s', 'flowlab-bancada', '-w'], { encoding: 'utf8' }).trim();
  if (!email || !senha) throw new Error('nao achei a entrada flowlab-bancada no Chaveiro');
  return { email, senha };
}

const { email, senha } = doChaveiro();
console.log('conta:', email.replace(/(.{3}).*(@.*)/, '$1***$2'));

const ONDAS = (process.argv[2] || '2,5,10,20').split(',').map(Number);
const nav = await chromium.launch({
  channel: 'chrome', headless: false,
  ignoreDefaultArgs: ['--enable-automation', '--no-sandbox'],
  args: ['--window-position=-3200,0', '--disable-blink-features=AutomationControlled'],
});

const vivos = [];          // as sessoes ja abertas, para reconferir depois

async function umLogin(i) {
  const t0 = Date.now();
  const ctx = await nav.newContext({ viewport: { width: 1100, height: 760 } });
  const pag = await ctx.newPage();
  const codigos = [];
  pag.on('response', (r) => {
    if (r.url().includes('flowlab.io') && r.status() >= 400) codigos.push(r.status());
  });
  try {
    await pag.goto('https://flowlab.io/register/sign_in',
                   { waitUntil: 'domcontentloaded', timeout: 90000 });
    await pag.fill('input[type="email"], input[name*="email" i]', email);
    await pag.fill('input[type="password"]', senha);
    await Promise.all([
      pag.waitForLoadState('domcontentloaded', { timeout: 90000 }),
      pag.click('input[type="submit"], button[type="submit"], text=Sign In'),
    ]);
    await pag.waitForTimeout(5000);
    const t = await pag.title();
    const ok = !/sign in|entrar/i.test(t);
    vivos.push({ i, ctx, pag });
    return { i, ms: Date.now() - t0, ok, titulo: t.slice(0, 44), ruins: codigos };
  } catch (e) {
    await ctx.close().catch(() => {});
    return { i, ms: Date.now() - t0, ok: false, erro: String(e.message).slice(0, 70), ruins: codigos };
  }
}

async function aindaVivo(s) {
  try {
    await s.pag.goto('https://flowlab.io/games/mine',
                     { waitUntil: 'domcontentloaded', timeout: 60000 });
    await s.pag.waitForTimeout(2500);
    return /your games|my games/i.test(await s.pag.title());
  } catch { return false; }
}

let n = 0;
for (const onda of ONDAS) {
  const quantos = onda - n;
  if (quantos <= 0) continue;
  console.log(`\n== onda: mais ${quantos} logins, total ${onda} ==`);
  const r = await Promise.all([...Array(quantos)].map((_, k) => umLogin(n + k + 1)));
  const ok = r.filter((x) => x.ok).length;
  const err429 = r.flatMap((x) => x.ruins).filter((c) => c === 429).length;
  console.log(`  entraram: ${ok}/${quantos}   respostas 429: ${err429}`);
  for (const x of r.filter((y) => !y.ok)) console.log('   !!', JSON.stringify(x));

  // A PERGUNTA QUE IMPORTA: os que entraram ANTES continuam de pe?
  const checagem = await Promise.all(vivos.map(aindaVivo));
  const depe = checagem.filter(Boolean).length;
  console.log(`  sessoes anteriores ainda de pe: ${depe}/${vivos.length}`);
  if (ok < quantos || depe < vivos.length) {
    console.log('  >> PAREI AQUI: alguma coisa cedeu nesta onda.');
    break;
  }
  n = onda;
  await new Promise((r2) => setTimeout(r2, 4000));
}

console.log(`\nresumo: ${vivos.length} sessoes abertas por login de verdade, todas conferidas.`);
await nav.close();
