#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera o site do curso: um indice e uma pagina por aula."""
import os, json, shutil, html, re

SAIDA = "curso"

CSS = """
:root{
  --papel:#FBFAF7; --carta:#FFFFFF; --tinta:#14161C; --tinta2:#4E525C;
  --linha:#E3E0D8; --azul:#1B62DC; --azul-fraco:#EAF0FC;
  --verde:#147A38; --verde-fraco:#E7F4EC;
  --laranja:#C2560A; --laranja-fraco:#FDF0E4;
  --roxo:#5B2E9E; --roxo-fraco:#F2ECFB;
  --codigo:#12151C; --codigo-tinta:#E8EBF0;
  --sombra:0 1px 2px rgba(20,22,28,.05), 0 8px 24px rgba(20,22,28,.06);
  --raio:14px;
}
@media (prefers-color-scheme:dark){
  :root:not([data-tema="claro"]){
    --papel:#12141A; --carta:#1A1D25; --tinta:#ECEEF2; --tinta2:#A4AAB6;
    --linha:#2C313C; --azul:#6C9BF0; --azul-fraco:#1B2436;
    --verde:#5CC183; --verde-fraco:#15271C;
    --laranja:#F0964E; --laranja-fraco:#2A1E14;
    --roxo:#B995F0; --roxo-fraco:#221A33;
    --codigo:#0D1016; --codigo-tinta:#E8EBF0;
    --sombra:0 1px 2px rgba(0,0,0,.3), 0 8px 24px rgba(0,0,0,.35);
  }
}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:68px}
body{margin:0;background:var(--papel);color:var(--tinta);
  font-family:"Atkinson Hyperlegible","Helvetica Neue",Arial,sans-serif;
  font-size:17px;line-height:1.6;-webkit-text-size-adjust:100%}
h1,h2,h3{font-family:Archivo,"Helvetica Neue",Arial,sans-serif;
  font-weight:800;letter-spacing:-.015em;text-wrap:balance}
img{max-width:100%;display:block}
[hidden]{display:none!important}
a{color:var(--azul)}

.barra{position:sticky;top:0;z-index:40;background:color-mix(in srgb,var(--papel) 88%,transparent);
  backdrop-filter:blur(10px);border-bottom:1px solid var(--linha)}
.barra-in{max-width:1180px;margin:0 auto;padding:11px 20px;display:flex;align-items:center;gap:14px}
.marca{font-family:Archivo,sans-serif;font-weight:800;font-size:15px;white-space:nowrap}
.marca a{color:inherit;text-decoration:none}
.marca span{color:var(--azul)}
.conta{margin-left:auto;font-size:13px;color:var(--tinta2);font-variant-numeric:tabular-nums;white-space:nowrap}
.trilho{position:absolute;left:0;bottom:-1px;height:3px;width:100%;background:transparent}
.trilho i{display:block;height:100%;width:0;background:var(--azul);transition:width .25s ease}

.capa{max-width:1180px;margin:0 auto;padding:46px 20px 10px}
.etiqueta{display:inline-block;background:var(--azul);color:#fff;font-family:Archivo,sans-serif;
  font-weight:700;font-size:11.5px;letter-spacing:.12em;text-transform:uppercase;
  padding:5px 13px;border-radius:99px}
.capa h1{font-size:clamp(34px,6.2vw,58px);margin:16px 0 10px;line-height:1.02}
.capa .linha-fina{font-size:19px;color:var(--tinta2);max-width:62ch;margin:0}
.avisos{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));margin:26px 0 8px}
.aviso{background:var(--carta);border:1px solid var(--linha);border-radius:var(--raio);
  padding:14px 16px;font-size:15px;box-shadow:var(--sombra)}
.aviso b{font-family:Archivo,sans-serif;display:block;font-size:12px;letter-spacing:.09em;
  text-transform:uppercase;margin-bottom:5px;color:var(--azul)}
.baixar{display:inline-flex;align-items:center;gap:8px;margin-top:6px;font-size:14.5px;
  text-decoration:none;border:1px solid var(--linha);background:var(--carta);
  padding:9px 15px;border-radius:99px;color:var(--tinta);font-weight:700}
.baixar:hover{border-color:var(--azul);color:var(--azul)}

main{max-width:1180px;margin:0 auto;padding:10px 20px 70px}
.passo{background:var(--carta);border:1px solid var(--linha);border-radius:var(--raio);
  padding:20px;margin:22px 0;box-shadow:var(--sombra);scroll-margin-top:70px}
.passo.feito{border-color:var(--verde)}
.cab{display:flex;align-items:flex-start;gap:13px;padding-bottom:13px;border-bottom:2px solid var(--linha)}
.passo.feito .cab{border-bottom-color:var(--verde)}
.bolha{flex:none;width:40px;height:40px;border-radius:11px;background:var(--azul);color:#fff;
  font-family:Archivo,sans-serif;font-weight:800;font-size:19px;
  display:flex;align-items:center;justify-content:center;font-variant-numeric:tabular-nums}
.passo.feito .bolha{background:var(--verde)}
.cab h2{font-size:clamp(20px,2.7vw,26px);margin:3px 0 0;flex:1}
.risca{display:flex;align-items:center;gap:7px;font-size:13.5px;color:var(--tinta2);
  cursor:pointer;user-select:none;flex:none;padding-top:8px;white-space:nowrap}
.risca input{width:19px;height:19px;accent-color:var(--verde);cursor:pointer}

.corpo{display:grid;gap:20px;grid-template-columns:1fr;margin-top:16px}
@media (min-width:920px){ .corpo{grid-template-columns:1.35fr 1fr;align-items:start} }
.midia{margin:0}
.moldura{border:1px solid var(--linha);border-radius:10px;overflow:hidden;background:var(--papel)}
.abas{display:flex;gap:6px;margin-bottom:9px}
.aba{font-family:Archivo,sans-serif;font-size:12.5px;font-weight:700;letter-spacing:.04em;
  border:1px solid var(--linha);background:var(--carta);color:var(--tinta2);
  padding:6px 13px;border-radius:99px;cursor:pointer}
.aba[aria-pressed="true"]{background:var(--roxo-fraco);border-color:var(--roxo);color:var(--roxo)}
.legenda{font-size:13px;color:var(--tinta2);margin:8px 2px 0}

.texto>p{margin:0 0 14px}
.ui{font-family:ui-monospace,"SF Mono",Menlo,monospace;font-size:.86em;
  background:var(--azul-fraco);border:1px solid color-mix(in srgb,var(--azul) 25%,transparent);
  border-radius:5px;padding:1px 6px;white-space:nowrap;color:var(--tinta)}
.certo,.socorro{border-radius:0 10px 10px 0;padding:12px 15px;margin-top:14px;font-size:15.5px}
.certo{background:var(--verde-fraco);border-left:5px solid var(--verde)}
.socorro{background:var(--laranja-fraco);border-left:5px solid var(--laranja)}
.certo>b:first-child,.socorro>b:first-child{font-family:Archivo,sans-serif;display:block;
  font-size:11.5px;letter-spacing:.1em;text-transform:uppercase;margin-bottom:5px}
.certo>b:first-child{color:var(--verde)}
.socorro>b:first-child{color:var(--laranja)}
.socorro dl{margin:0}
.socorro dt{font-weight:700;margin-top:10px}
.socorro dt:first-of-type{margin-top:2px}
.socorro dd{margin:2px 0 0;color:var(--tinta2)}

.codigo{margin:14px 0;border-radius:10px;overflow:hidden;border:1px solid var(--linha)}
.codigo .titulo{display:flex;align-items:center;gap:8px;background:var(--roxo-fraco);
  color:var(--roxo);font-family:Archivo,sans-serif;font-weight:700;font-size:11.5px;
  letter-spacing:.1em;text-transform:uppercase;padding:7px 13px;border-bottom:1px solid var(--linha)}
.codigo pre{margin:0;background:var(--codigo);color:var(--codigo-tinta);padding:14px 16px;
  overflow-x:auto;font-family:ui-monospace,"SF Mono",Menlo,monospace;font-size:14.5px;line-height:1.7}
.codigo ol{margin:0;padding:0 0 0 46px;background:var(--codigo);color:var(--codigo-tinta);
  font-family:ui-monospace,"SF Mono",Menlo,monospace;font-size:14.5px;line-height:1.75;
  overflow-x:auto}
.codigo li{border-left:1px solid color-mix(in srgb,var(--codigo-tinta) 18%,transparent);
  padding:0 16px 0 10px;white-space:pre}
.codigo li::marker{color:color-mix(in srgb,var(--codigo-tinta) 40%,transparent);font-size:12px}
.codigo li.auto{color:color-mix(in srgb,var(--codigo-tinta) 42%,transparent);font-style:italic}
.codigo .rodape{background:var(--codigo);color:color-mix(in srgb,var(--codigo-tinta) 55%,transparent);
  font-family:"Atkinson Hyperlegible",sans-serif;font-size:12.5px;padding:8px 16px 12px;
  border-top:1px solid color-mix(in srgb,var(--codigo-tinta) 15%,transparent)}
.codigo .rodape b{color:color-mix(in srgb,var(--codigo-tinta) 85%,transparent)}
.codigo .rodape code{font-family:ui-monospace,"SF Mono",Menlo,monospace;font-size:13px;
  color:color-mix(in srgb,var(--codigo-tinta) 92%,transparent);
  background:color-mix(in srgb,var(--codigo-tinta) 12%,transparent);
  padding:1px 5px;border-radius:4px}
.codigo .rodape+.rodape{padding-top:10px}
.so-papel{display:none}

.fim{max-width:1180px;margin:0 auto;padding:0 20px 40px;text-align:center;color:var(--tinta2);font-size:15px}
.fim strong{color:var(--tinta)}
.navega{max-width:1180px;margin:0 auto;padding:0 20px 80px;display:flex;gap:12px;justify-content:center;flex-wrap:wrap}
.navega a{text-decoration:none;border:1px solid var(--linha);background:var(--carta);
  padding:11px 18px;border-radius:99px;color:var(--tinta);font-weight:700;font-size:15px}
.navega a:hover{border-color:var(--azul);color:var(--azul)}

/* indice */
.grade{display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));
  max-width:1180px;margin:0 auto;padding:10px 20px 80px}
.cartao{display:block;text-decoration:none;color:inherit;background:var(--carta);
  border:1px solid var(--linha);border-radius:var(--raio);padding:18px 20px;box-shadow:var(--sombra)}
.cartao:hover{border-color:var(--azul)}
.cartao .num{font-family:Archivo,sans-serif;font-weight:800;font-size:12px;letter-spacing:.12em;
  text-transform:uppercase;color:var(--azul)}
.cartao h3{margin:6px 0 6px;font-size:21px}
.cartao p{margin:0;color:var(--tinta2);font-size:15px}
.cartao.embreve{opacity:.55}
.cartao.embreve .num{color:var(--tinta2)}

@media print{
  .barra,.abas,.risca,.baixar,.navega{display:none}
  body{background:#fff}
  .gif{display:none!important}
  .foto{display:block!important}
  /* quebrar DENTRO do passo e nao antes dele: com page-break-inside:avoid num
     passo alto o Chrome pulava a folha inteira e sobravam paginas em branco. */
  .passo{break-inside:auto;box-shadow:none;border-color:#ccc;margin:0 0 16px;padding:16px 18px}
  .cab{break-after:avoid}
  .midia,.certo,.socorro,.codigo{break-inside:avoid}
  .legenda{display:none}
  .legenda.so-papel{display:block}
  .midia img{max-height:11cm;width:auto;margin:0 auto}
  .capa{break-after:page}
}
"""

JS = """
(function(){
  var chave = "robotomia-roblox-" + (document.body.dataset.aula || "x");
  function ler(){ try{ return JSON.parse(localStorage.getItem(chave)||"[]"); }catch(e){ return []; } }
  function gravar(v){ try{ localStorage.setItem(chave, JSON.stringify(v)); }catch(e){} }
  var caixas = [].slice.call(document.querySelectorAll(".risca input"));
  var conta  = document.getElementById("conta");
  var trilho = document.getElementById("trilho");
  if (!caixas.length) return;
  var feitos = ler();
  function pinta(){
    var n = 0;
    caixas.forEach(function(c){
      var p = c.closest(".passo");
      if (c.checked){ n++; p.classList.add("feito"); } else { p.classList.remove("feito"); }
    });
    if (conta)  conta.textContent = n + " de " + caixas.length + " passos prontos";
    if (trilho) trilho.style.width = (100*n/caixas.length) + "%";
  }
  caixas.forEach(function(c){
    c.checked = feitos.indexOf(c.dataset.passo) >= 0;
    c.addEventListener("change", function(){
      var v = ler().filter(function(x){ return x !== c.dataset.passo; });
      if (c.checked) v.push(c.dataset.passo);
      gravar(v); pinta();
    });
  });
  pinta();
  [].slice.call(document.querySelectorAll(".abas")).forEach(function(g){
    g.addEventListener("click", function(e){
      var b = e.target.closest(".aba"); if(!b) return;
      var caixa = g.parentNode;
      [].slice.call(g.children).forEach(function(x){ x.setAttribute("aria-pressed", x===b ? "true":"false"); });
      caixa.querySelector(".gif").hidden  = (b.dataset.ver !== "clipe");
      caixa.querySelector(".foto").hidden = (b.dataset.ver !== "foto");
      caixa.querySelector(".legenda").textContent = b.dataset.legenda;
    });
  });
})();
"""

CABECA = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>{titulo}</title>
<meta name="description" content="{desc}">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><text y='26' font-size='26'>&#129302;</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@700;800&family=Atkinson+Hyperlegible:wght@400;700&display=swap">
<style>{css}</style>
</head>
<body{corpo_attr}>
"""


def midia(p, base=""):
    foto = f'<img class="foto" src="{base}fotos/{p["foto"]}" alt="Tela do Roblox Studio no passo {p["n"]}" loading="lazy">'
    if not p.get("clipe"):
        return (f'<figure class="midia"><div class="moldura">{foto}</div>'
                f'<p class="legenda">Foto da tela.</p></figure>')
    gif = f'<img class="gif" src="{base}clipes/{p["clipe"]}" alt="Animação do passo {p["n"]}" loading="lazy">'
    return ('<figure class="midia"><div class="abas">'
            '<button class="aba" data-ver="clipe" aria-pressed="true" '
            'data-legenda="O clipe repete sozinho. Repare onde o cursor vai antes de clicar.">▶ Clipe</button>'
            '<button class="aba" data-ver="foto" aria-pressed="false" '
            'data-legenda="Foto da tela.">Foto</button></div>'
            f'<div class="moldura">{gif}{foto.replace("<img", "<img hidden", 1)}</div>'
            '<p class="legenda">O clipe repete sozinho. Repare onde o cursor vai antes de clicar.</p>'
            # no papel o clipe nao roda: o @media print troca pela foto, entao
            # a legenda do clipe tambem tem de sair
            '<p class="legenda so-papel">Foto da tela.</p></figure>')


def bloco_codigo(codigo, auto=()):
    """auto = numeros de linha que o EDITOR escreve sozinho. Sao marcadas para
       o aluno nao digitar de novo — foi o erro que apareceu no teste: quem
       digitava tudo terminava com tres 'end)' em vez de um."""
    saida = []
    for i, l in enumerate(codigo.split("\n"), 1):
        classe = ' class="auto"' if i in auto else ""
        saida.append(f"<li{classe}>{html.escape(l) if l else ' '}</li>")
    notas = []
    if auto:
        notas.append("as linhas em cinza o editor escreve sozinho — não digite elas")
    # Teclado brasileiro: a aspa e tecla MORTA. Medido no Studio, tres vezes:
    #   aspa + vogal  -> trema   (Instance.new("IntValue") sai Instance.new(ÏntValue")
    #   aspa no fim da linha + Enter -> a aspa DOBRA ("leaderstats"")
    #   aspa + barra de espaco -> uma aspa limpa, sem espaco, nos dois casos.
    if '"' in codigo:
        notas.append('teclado brasileiro: a aspa é <b>tecla muda</b> — ela não aparece na hora. '
                     'Aperte a tecla da aspa e <b>logo a barra de espaço</b>: sai uma aspa '
                     'sozinha, sem espaço nenhum. Faça isso com <b>todas</b> as aspas. Se você '
                     'digitar a letra direto depois da aspa, ela vira trema '
                     '(<code>&quot;I</code> sai <code>Ï</code>).')
    rodape = ("".join(f'<div class="rodape">{n}</div>' for n in notas))
    return ('<div class="codigo"><div class="titulo">⌨ digite você mesmo — não copie</div>'
            f'<ol>{"".join(saida)}</ol>{rodape}</div>')


def pagina_aula(aula, total_aulas):
    passos = []
    for p in aula["passos"]:
        sos = "".join(f"<dt>{d}</dt><dd>{r}</dd>" for d, r in p["sos"])
        cod = bloco_codigo(p["codigo"], p.get("auto", ())) if p.get("codigo") else ""
        dep = f'<p>{p["depois"]}</p>' if p.get("depois") else ""
        passos.append(f'''<section class="passo" id="passo{p["n"]}">
  <div class="cab"><div class="bolha">{p["n"]}</div><h2>{p["titulo"]}</h2>
  <label class="risca"><input type="checkbox" data-passo="{p["n"]}"> feito</label></div>
  <div class="corpo">{midia(p)}
    <div class="texto"><p>{p["corpo"]}</p>{cod}{dep}
      <div class="certo"><b>Está certo se</b>{p["ck"]}</div>
      <div class="socorro"><b>Não deu certo?</b><dl>{sos}</dl></div>
    </div></div></section>''')
    avisos = "".join(f'<div class="aviso"><b>{t}</b>{c}</div>' for t, c in aula["avisos"])
    prox = aula["n"] + 1
    nav = ['<a href="../">⌂ Todas as aulas</a>']
    if aula["n"] > 1: nav.append(f'<a href="../aula{aula["n"]-1}/">← Aula {aula["n"]-1}</a>')
    if prox <= total_aulas: nav.append(f'<a href="../aula{prox}/">Aula {prox} →</a>')
    return (CABECA.format(titulo=f'{aula["titulo"]} — Robotomia', desc=aula["subtitulo"],
                          css=CSS, corpo_attr=f' data-aula="{aula["slug"]}"') + f'''
<header class="barra"><div class="barra-in">
  <div class="marca"><a href="../">Robotomia</a> <span>· Roblox · Aula {aula["n"]}</span></div>
  <div class="conta" id="conta">0 de {len(aula["passos"])} passos prontos</div>
</div><div class="trilho"><i id="trilho"></i></div></header>

<div class="capa">
  <span class="etiqueta">{aula["etiqueta"]}</span>
  <h1>{aula["titulo"]}</h1>
  <p class="linha-fina">{aula["subtitulo"]} São {len(aula["passos"])} passos, {aula["tempo"]}.
  Faça um de cada vez e só passe adiante depois de conferir o quadro verde.</p>
  <div class="avisos">{avisos}</div>
  <a class="baixar" href="aula{aula["n"]}.pdf">⤓ Baixar esta aula em PDF (para imprimir)</a>
</div>

<main>
{chr(10).join(passos)}
</main>

<p class="fim"><strong>{aula["fim"]}</strong></p>
<div class="navega">{"".join(nav)}</div>
<script>{JS}</script>
</body></html>''')
