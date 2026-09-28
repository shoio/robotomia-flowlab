#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monta o site do curso na RAIZ do repositorio, a partir de fonte/.

   Rode de qualquer lugar: `python3 fonte/build_curso.py`.
"""
import os, json, shutil
from PIL import Image
import gera_curso as G
import conteudo_a2, conteudo_a3, conteudo_a4, conteudo_a5, conteudo_a6, conteudo_a7, conteudo_a8, conteudo_a9
import conteudo_a10, conteudo_a11, conteudo_a12, conteudo_a13, conteudo_a14
import conteudo_a15, conteudo_a16, conteudo_a17, conteudo_a18

AQUI  = os.path.dirname(os.path.abspath(__file__))     # .../fonte
SAIDA = os.path.dirname(AQUI)                          # a raiz do repositorio
os.chdir(AQUI)   # todos os caminhos de conteudo sao relativos a fonte/

PLANO = [
    (1, "Obby em 50 minutos", "Um percurso de obstáculos, sem uma linha de código.", True),
    (2, "A lava que mata", "O primeiro script: uma peça que reage a quem encosta.", True),
    (3, "Plataformas que somem", "Pisou, sumiu. O obby vira um jogo de tempo.", True),
    (4, "Publicar o seu jogo", "Seu jogo no ar, com nome e descrição, num link que você manda.", True),
    (5, "Moedas e placar", "Encostou, sumiu, somou — com o placar na tela.", True),
    (6, "Botão e porta", "Um script mexendo em outra peça.", True),
    (7, "O martelo que gira", "Obstáculo que derruba. Repetição.", True),
    (8, "Loja: gaste as moedas", "Três moedas compram velocidade. Aqui entra o if.", True),
    (9, "Projeto livre e mostra", "Você monta o seu jogo, com o kit de receitas do curso inteiro.", True),
    (10, "Checkpoint: a bandeira que salva", "Morreu? Volta na bandeira, não no começo.", True),
]


def aula1():
    """Converte a Aula 1 (ja escrita) para o formato do gerador."""
    P = json.load(open("aula1/passos.json"))
    passos = []
    for p in P:
        passos.append(dict(n=p["n"], titulo=p["titulo"], foto=p["img"],
                           clipe=p["clipe"], corpo=p["corpo"], ck=p["ck"],
                           sos=[tuple(s) for s in p["sos"]]))
    return {
        "n": 1, "slug": "aula1", "titulo": "Obby em 50 minutos",
        "subtitulo": "Você vai construir um percurso de obstáculos no Roblox Studio e atravessar ele.",
        "tempo": "50 minutos", "etiqueta": "Aula 1 · sem programação",
        "fim": "Acabou a Aula 1. Você construiu e atravessou o seu percurso — sem escrever uma linha de código.",
        "avisos": [
          ("Os clipes", "Doze passos têm uma animação curta que mostra o gesto inteiro — o cursor saindo, clicando, e o que muda na tela. Dá para trocar para a foto com as marcações."),
          ("Atalhos", "Este material usa <span class=ui>Ctrl</span>, do Windows. Num Mac, troque Ctrl por <span class=ui>⌘</span>."),
          ("Travou?", "Todo passo tem um quadro laranja embaixo com o conserto dos erros mais comuns."),
        ],
        "passos": passos,
        "fotos_de": "aula1/final", "clipes_de": "aula1/gifs",
    }


def _de_conteudo(mod):
    a = dict(mod.AULA)
    passos = []
    for p in a["passos"]:
        q = dict(p); q["foto"] = os.path.basename(p["img"])
        passos.append(q)
    a["passos"] = passos
    a["fotos_de"] = None      # as fotos vem de caminhos variados; copio uma a uma
    a["clipes_de"] = f'{a["slug"]}/gifs'
    return a


def aula2(): return _de_conteudo(conteudo_a2)
def aula3(): return _de_conteudo(conteudo_a3)
def aula4(): return _de_conteudo(conteudo_a4)
def aula5(): return _de_conteudo(conteudo_a5)
def aula6(): return _de_conteudo(conteudo_a6)
def aula7(): return _de_conteudo(conteudo_a7)
def aula8(): return _de_conteudo(conteudo_a8)
def aula9(): return _de_conteudo(conteudo_a9)
# 2o bloco. Uma aula so entra no PLANO e na tupla do laco quando as fotos
# dela existem: enquanto nao existem, ela nao e uma aula, e um texto.
def aula10(): return _de_conteudo(conteudo_a10)
def aula11(): return _de_conteudo(conteudo_a11)
def aula12(): return _de_conteudo(conteudo_a12)
def aula13(): return _de_conteudo(conteudo_a13)
def aula14(): return _de_conteudo(conteudo_a14)
def aula15(): return _de_conteudo(conteudo_a15)
def aula16(): return _de_conteudo(conteudo_a16)
def aula17(): return _de_conteudo(conteudo_a17)
def aula18(): return _de_conteudo(conteudo_a18)


def indice(aulas_prontas):
    cartoes = []
    for n, tit, sub, pronta in PLANO:
        if pronta:
            cartoes.append(f'<a class="cartao" href="aula{n}/"><div class="num">Aula {n}</div>'
                           f'<h3>{tit}</h3><p>{sub}</p></a>')
        else:
            cartoes.append(f'<div class="cartao embreve"><div class="num">Aula {n} · em breve</div>'
                           f'<h3>{tit}</h3><p>{sub}</p></div>')
    return (G.CABECA.format(titulo="Roblox na Robotomia", css=G.CSS, corpo_attr="",
                            desc="Curso de Roblox Studio da Robotomia: uma aula por semana, "
                                 "passo a passo, com animação em cada gesto.") + f'''
<header class="barra"><div class="barra-in">
  <div class="marca">Robotomia <span>· Roblox</span></div>
  <div class="conta">{len(aulas_prontas)} de {len(PLANO)} aulas no ar</div>
</div></header>

<div class="capa">
  <span class="etiqueta">Curso · 10 a 14 anos</span>
  <h1>Roblox na Robotomia</h1>
  <p class="linha-fina">Uma aula por semana, de 50 minutos. Cada aula começa num projeto novo
  e termina com alguma coisa que dá para jogar no mesmo dia.
  Cada passo tem uma foto da tela, e os gestos novos têm uma animação curta.</p>
</div>

<div class="grade">
{chr(10).join(cartoes)}
</div>

<p class="fim">Feito para a Robotomia. Se um passo não funcionar na sua tela,
o quadro laranja do próprio passo tem o conserto.</p>
</body></html>''')


def monta():
    # o guarda roda ANTES de gerar: toda regra dele nasceu de um defeito
    # que passou pela leitura e so apareceu seguindo a aula como aluno.
    import confere_aulas, confere_lua
    problemas = confere_aulas.confere() + confere_lua.confere()
    if problemas:
        for m in problemas:
            print("  !!", m)
        raise SystemExit("as aulas nao passaram no guarda")
    # Apago so o que ESTE script cria. Um rmtree da pasta inteira ja levou o
    # .git junto uma vez; agora que a saida e a raiz do repositorio, ele
    # levaria tambem a fonte/ que esta gerando o site.
    os.makedirs(SAIDA, exist_ok=True)
    meus = {f"aula{n}" for n, *_ in PLANO} | {"index.html", ".nojekyll"}
    for nome in sorted(meus):
        alvo = os.path.join(SAIDA, nome)
        if os.path.isdir(alvo):
            shutil.rmtree(alvo)
        elif os.path.exists(alvo):
            os.remove(alvo)
    prontas = []
    for construtor in (aula1, aula2, aula3, aula4, aula5, aula6, aula7, aula8, aula9,
                       aula10):
        a = construtor()
        pasta = os.path.join(SAIDA, a["slug"])
        os.makedirs(os.path.join(pasta, "fotos"), exist_ok=True)
        os.makedirs(os.path.join(pasta, "clipes"), exist_ok=True)
        # fotos
        for p in a["passos"]:
            orig = p["img"] if "img" in p else os.path.join(a["fotos_de"], p["foto"])
            if not os.path.exists(orig):
                orig = os.path.join(a["fotos_de"], p["foto"])
            # sempre JPEG: PNG de captura pesa ~1 MB e a turma abre a pagina
            # toda ao mesmo tempo na rede da escola
            p["foto"] = os.path.splitext(p["foto"])[0] + ".jpg"
            destino = os.path.join(pasta, "fotos", p["foto"])
            if not os.path.exists(destino):
                im = Image.open(orig).convert("RGB")
                if im.height > 1620:            # corta a barra de comando do rodape
                    im = im.crop((0, 0, im.width, 1620))
                L = 1200
                im = im.resize((L, round(im.height * L / im.width)), Image.LANCZOS)
                im.save(destino, quality=84, optimize=True)
        # clipes
        for p in a["passos"]:
            if p.get("clipe"):
                o = os.path.join(a["clipes_de"], p["clipe"])
                d = os.path.join(pasta, "clipes", p["clipe"])
                if os.path.exists(o) and not os.path.exists(d):
                    shutil.copy(o, d)
        open(os.path.join(pasta, "index.html"), "w").write(G.pagina_aula(a, len(PLANO)))
        prontas.append(a)
        print(f"  aula {a['n']}: {len(a['passos'])} passos, "
              f"{len(os.listdir(os.path.join(pasta,'clipes')))} clipes")
    open(os.path.join(SAIDA, "index.html"), "w").write(indice(prontas))
    open(os.path.join(SAIDA, ".nojekyll"), "w").write("")
    # Um PDF por aula, impresso da propria pagina — assim ele nunca envelhece
    # em relacao ao site (o PDF antigo da Aula 1 ainda mandava clicar num botao
    # que o texto ja tinha deixado de citar).
    import faz_pdfs
    faz_pdfs.main()
    return prontas


if __name__ == "__main__":
    monta()
