// NIVEL 1: 20 navegadores independentes, a MESMA conta, ao mesmo tempo.
//
// Isto nao simula 20 LOGINS (cada um digitando a senha) — simula 20 alunos JA
// logados usando a conta ao mesmo tempo. Mede o risco que eu apontei como o
// mais provavel: teto de requisicoes por conta ou por IP, que numa escola sai
// tudo do mesmo IP.
//
// Cada contexto e isolado (cookie proprio), entao e carga de verdade, nao 20
// abas do mesmo navegador.
import { chromium } from 'playwright';
import fs from 'node:fs';

const N = Number(process.argv[2] || 20);
const ALVO = process.argv[3] || 'https://flowlab.io/games/mine';

// a sessao da conta. Se ja houver uma copia salva, uso ELA: o motor da
// bancada pode estar com o perfil aberto, e dois Chrome nao dividem o mesmo
// diretorio de perfil — abrir de novo mataria a captura que esta rodando.
let estado;
if (fs.existsSync('/tmp/_sessao.json')) {
  estado = JSON.parse(fs.readFileSync('/tmp/_sessao.json', 'utf8'));
  console.log('sessao da conta (copia salva):', estado.cookies.length, 'cookies');
} else {
  const perfil = await chromium.launchPersistentContext('/Users/shoio/.flowlab-bancada', {
    channel: 'chrome', headless: false,
    ignoreDefaultArgs: ['--enable-automation', '--no-sandbox'],
    args: ['--window-position=-3200,0', '--disable-blink-features=AutomationControlled'],
  });
  estado = await perfil.storageState();
  await perfil.close();
  fs.writeFileSync('/tmp/_sessao.json', JSON.stringify(estado));
  console.log('sessao da conta copiada:', estado.cookies.length, 'cookies');
}

const nav = await chromium.launch({
  channel: 'chrome', headless: false,
  ignoreDefaultArgs: ['--enable-automation', '--no-sandbox'],
  args: ['--window-position=-3200,0', '--disable-blink-features=AutomationControlled'],
});

async function umAluno(i) {
  const t0 = Date.now();
  const ctx = await nav.newContext({ storageState: estado, viewport: { width: 1200, height: 800 } });
  const pag = await ctx.newPage();
  let status = 0;
  pag.on('response', (r) => { if (r.url().includes('/games/mine')) status = r.status(); });
  try {
    await pag.goto(ALVO, { waitUntil: 'domcontentloaded', timeout: 90000 });
    await pag.waitForTimeout(6000);
    const titulo = await pag.title();
    const logado = /your games|my games/i.test(titulo);
    const desafio = /moment|momento/i.test(titulo);
    await ctx.close();
    return { i, ms: Date.now() - t0, status, titulo: titulo.slice(0, 40), logado, desafio };
  } catch (e) {
    await ctx.close().catch(() => {});
    return { i, ms: Date.now() - t0, status, erro: String(e.message).slice(0, 60) };
  }
}

console.log(`== ${N} alunos ao mesmo tempo em ${ALVO} ==`);
const r = await Promise.all([...Array(N)].map((_, i) => umAluno(i + 1)));
const ok = r.filter((x) => x.logado).length;
const des = r.filter((x) => x.desafio).length;
const err = r.filter((x) => x.erro);
const tempos = r.map((x) => x.ms).sort((a, b) => a - b);
console.log(`logados: ${ok}/${N}   com desafio do Cloudflare: ${des}   erro: ${err.length}`);
console.log(`tempo: mediana ${tempos[Math.floor(N / 2)]} ms, pior ${tempos[N - 1]} ms`);
const ruins = r.filter((x) => !x.logado);
for (const x of ruins.slice(0, 6)) console.log('  !!', JSON.stringify(x));
const codigos = [...new Set(r.map((x) => x.status))];
console.log('codigos HTTP vistos:', codigos.join(', '));
await nav.close();
