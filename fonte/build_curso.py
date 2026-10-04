#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monta o site do curso na RAIZ do repositorio, a partir de fonte/.

   Rode de qualquer lugar: `python3 fonte/build_curso.py`.
"""
import os, json, shutil
from PIL import Image
import gera_curso as G
import conteudo_a1, conteudo_a2, conteudo_a3

AQUI  = os.path.dirname(os.path.abspath(__file__))     # .../fonte
SAIDA = os.path.dirname(AQUI)                          # a raiz do repositorio
os.chdir(AQUI)   # todos os caminhos de conteudo sao relativos a fonte/

PLANO = [
    (1,  "Pega-moedas", "Um boneco que corre e uma moeda que some. O primeiro jogo.", True),
    (2,  "Pulo e plataformas", "Três degraus, uma estrela no alto e lava embaixo. Caiu, recomeça.", True),
    (3,  "A lava que sobe", "A lava não fica parada: ela sobe sozinha. Suba a escada antes.", True),
    (4,  "Nave e tiro", "Inimigos descendo, tiro que destroi, placar na tela.", False),
    (5,  "Um botao so", "O passaro entre os canos: acaso e dificuldade que cresce.", False),
    (6,  "Chave e porta", "Labirinto com chave: o jogo passa a ter memoria.", False),
    (7,  "Empurra-blocos", "Quebra-cabeca: empurrar caixas ate os alvos.", False),
    (8,  "Contra o relogio", "Percurso cronometrado, com recorde da partida.", False),
    (9,  "Inimigo que persegue", "IA simples, vida e barra de vida.", False),
    (10, "Menu, fases e fim de jogo", "Tela de titulo, tres fases e tela de vitoria.", False),
    (11, "Som, animacao e brilho", "O mesmo jogo, mas com vida.", False),
    (12, "Projeto livre e mostra", "O jogo do aluno, publicado, com link para a familia.", False),
]


def aula1(): return _de_conteudo(conteudo_a1)
def aula2(): return _de_conteudo(conteudo_a2)
def aula3(): return _de_conteudo(conteudo_a3)


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


def indice(aulas_prontas):
    cartoes = []
    for n, tit, sub, pronta in PLANO:
        if pronta:
            cartoes.append(f'<a class="cartao" href="aula{n}/"><div class="num">Aula {n}</div>'
                           f'<h3>{tit}</h3><p>{sub}</p></a>')
        else:
            cartoes.append(f'<div class="cartao embreve"><div class="num">Aula {n} · em breve</div>'
                           f'<h3>{tit}</h3><p>{sub}</p></div>')
    return (G.CABECA.format(titulo="Flowlab na Robotomia", css=G.CSS, corpo_attr="",
                            desc="Curso de Flowlab da Robotomia: uma aula por semana, "
                                 "passo a passo, com animação em cada gesto.") + f'''
<header class="barra"><div class="barra-in">
  <div class="marca">Robotomia <span>· Flowlab</span></div>
  <div class="conta">{len(aulas_prontas)} de {len(PLANO)} aulas no ar</div>
</div></header>

<div class="capa">
  <span class="etiqueta">Curso · 10 a 14 anos</span>
  <h1>Flowlab na Robotomia</h1>
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
    import confere_aulas
    problemas = confere_aulas.confere()
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
    for construtor in (aula1, aula2, aula3):
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
