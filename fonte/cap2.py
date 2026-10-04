#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Captura da Aula 2 — Pulo e plataformas.

   O jogo: um boneco que corre e PULA entre plataformas para pegar a estrela
   no alto; se cair na lava de baixo, o jogo recomeca.

   O que foi MEDIDO antes de escrever a aula (no rascunho 3150167):
   - o pacote `Run & Jump` so deixa pular quando um `Collision` liga um
     `Switch` — isto e, com o boneco TOCANDO alguma coisa — e a forca do pulo
     e 12, fixa;
   - por isso o PESO decide o pulo: com densidade 100 ele nao sai do chao, com
     densidade ~30 ele sobe 273 px (quatro casas), e leve demais ele some da
     tela;
   - com densidade ~30 o passo horizontal fica em 60 px, menos que uma casa,
     entao ele nao atravessa a estrela;
   - `Collision -> RestartGame` na lava devolve o jogador ao comeco (provado:
     ele voltou de x=1794 para x=1309)."""
import os, sys, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rs, nav, editor, blocos, comum
from comum import (celula, clique, pinta, nomeia, abre_sprite, marca_caixa,
                   arrasta_slider, fecha_painel_objeto, A, etapa, ETAPAS,
                   CELULA, GRADE_X, GRADE_Y)

comum.pasta("aula2")
ETAPAS.clear()      # a lista vive em comum.py: cada aula comeca a sua
D = "aula2"

# o desenho da fase
LINHA_CHAO = 8          # a plataforma onde o boneco comeca
LINHA_MEIO = 6          # a segunda plataforma
LINHA_ALTA = 4          # a terceira, onde fica a estrela
LINHA_LAVA = 11
COL_JOGADOR = 4
COLS_CHAO = [3, 4, 5, 6]
COLS_MEIO = [8, 9, 10]
COLS_ALTA = [12, 13, 14]
COL_ESTRELA = 13
COLS_LAVA = list(range(1, 16))

DENSIDADE = 30          # medido: pula 273 px e anda 60 px por toque


def faz_peca(c, r, nome, cor, cols_clone=None):
    """Cria um objeto na casa (c, r), pinta, e clona para as colunas pedidas."""
    x, y = celula(c, r)
    editor.objeto_ou_abre(x, y)
    nomeia(nome)
    abre_sprite()
    pinta(cor)
    clique(*comum.SPRITE_OK); time.sleep(2); nav.espera_parar(limite=15)
    fecha_painel_objeto()
    if cols_clone:
        clique(x, y); time.sleep(1.5)
        a, _ = nav.captura("/tmp/_c2_clone.png")
        p = nav.acha_texto("clone", arquivo=a)
        if not p:
            raise RuntimeError(f"nao achei Clone para {nome}")
        clique(*p); time.sleep(2)
        for cc in cols_clone:
            cx, cy = celula(cc, r)
            clique(cx, cy); time.sleep(1.0)
        q = nav.acha_texto("done cloning")
        clique(*q); time.sleep(2); nav.espera_parar(limite=15)
    return True


@etapa
def novo():
    A.url = editor.jogo_novo()
    print("   jogo:", A.url, flush=True)
    A.guarda_url()
    A.cap("p01_vazio")
    return True


@etapa
def jogador():
    x, y = celula(COL_JOGADOR, LINHA_CHAO - 1)
    A.gesto("criar_objeto", "g01", (x, y), lambda: clique(x, y), espera=1.5)
    a, _ = nav.captura("/tmp/_c2_rad.png")
    p = nav.acha_texto("create", arquivo=a)
    A.gesto("escolher_create", "g02", p, lambda: clique(*p), espera=3)
    editor.espera_tela("behaviors", limite=20)
    nomeia("Jogador")
    A.cap("p02_nome")
    abre_sprite()
    pinta("azul")
    A.cap("p03_azul")
    clique(*comum.SPRITE_OK); time.sleep(2); nav.espera_parar(limite=15)
    a, _ = nav.captura("/tmp/_c2_fis.png")
    q = nav.acha_texto("physics", arquivo=a)
    A.gesto("abrir_physics", "g03", q, lambda: clique(*q), espera=2.5)
    A.gesto("marcar_movable", "g04", (0, 0),
            lambda: marca_caixa("movable", True), espera=1.2)
    # o peso: medido, e o que decide se ele pula
    pd = nav.acha_texto("density", arquivo=nav.captura("/tmp/_c2_d.png")[0],
                        regiao=(0.45, 0.1, 1.0, 0.85))
    alvo = (int(pd[0] + 155 + 2.75 * DENSIDADE), pd[1])
    A.gesto("peso_do_pulo", "g05", alvo, lambda: clique(*alvo), espera=1.2)
    arrasta_slider("friction")
    A.cap("p04_fisica")
    fecha_painel_objeto()
    return True


@etapa
def movimento():
    x, y = celula(COL_JOGADOR, LINHA_CHAO - 1)
    editor.objeto_ou_abre(x, y)
    editor.abre_comportamentos()
    blocos.abre_categoria("Behavior Bundles")
    b = blocos.solta("Run & Jump", 1400, 700)
    A.cap("p05_run_and_jump")
    print("   pacote:", b, flush=True)
    time.sleep(2.5)
    editor.fecha_comportamentos(); time.sleep(2.5)
    fecha_painel_objeto(); time.sleep(2)
    return True


@etapa
def plataformas():
    faz_peca(COLS_CHAO[0], LINHA_CHAO, "Chao", "verde", COLS_CHAO[1:])
    A.cap("p06_chao")
    faz_peca(COLS_MEIO[0], LINHA_MEIO, "Plataforma", "verde", COLS_MEIO[1:])
    A.cap("p07_plataforma")
    x, y = celula(COLS_ALTA[0], LINHA_ALTA)
    clique(x, y); time.sleep(1.5)
    a, _ = nav.captura("/tmp/_c2_r2.png")
    p = nav.acha_texto("create", arquivo=a)
    if p:                      # casa vazia: faco a terceira a partir da Plataforma
        clique(*p); time.sleep(2.5); nav.espera_parar(limite=20)
        nomeia("Alta"); abre_sprite(); pinta("verde")
        clique(*comum.SPRITE_OK); time.sleep(2); nav.espera_parar(limite=15)
        fecha_painel_objeto()
        clique(x, y); time.sleep(1.5)
        a, _ = nav.captura("/tmp/_c2_r3.png")
        q = nav.acha_texto("clone", arquivo=a)
        clique(*q); time.sleep(2)
        for cc in COLS_ALTA[1:]:
            cx, cy = celula(cc, LINHA_ALTA); clique(cx, cy); time.sleep(1.0)
        d = nav.acha_texto("done cloning"); clique(*d); time.sleep(2)
        nav.espera_parar(limite=15)
    A.cap("p08_tres_plataformas")
    return True


@etapa
def lava():
    faz_peca(COLS_LAVA[0], LINHA_LAVA, "Lava", "vermelho", COLS_LAVA[1:])
    A.cap("p09_lava")
    x, y = celula(COLS_LAVA[0], LINHA_LAVA)
    editor.objeto_ou_abre(x, y)
    editor.abre_comportamentos()
    c = blocos.solta("Collision", 1150, 600)
    A.cap("p10_collision")
    r = blocos.solta("Restart Game", 1900, 950, titulo="RestartGame")
    A.cap("p11_restart")
    blocos.liga_fixo(c, "hit", r, "go")
    A.cap("p12_fio_lava")
    print("   lava ligada ao reinicio", flush=True)
    time.sleep(2)
    editor.fecha_comportamentos(); time.sleep(2.5)
    fecha_painel_objeto(); time.sleep(1.5)
    return True


@etapa
def estrela():
    x, y = celula(COL_ESTRELA, LINHA_ALTA - 1)
    editor.objeto_ou_abre(x, y)
    nomeia("Estrela")
    abre_sprite(); pinta("amarelo")
    clique(*comum.SPRITE_OK); time.sleep(2); nav.espera_parar(limite=15)
    A.cap("p13_estrela")
    editor.abre_comportamentos()
    c = blocos.solta("Collision", 1150, 600)
    d = blocos.solta("Destroyer", 1900, 950)
    blocos.liga_fixo(c, "hit", d, "in")
    A.cap("p14_fio_estrela")
    time.sleep(2)
    editor.fecha_comportamentos(); time.sleep(2.5)
    fecha_painel_objeto(); time.sleep(1.5)
    A.cap("p15_fase_pronta")
    return True


@etapa
def prova():
    """Prova em jogo as DUAS promessas da aula: o pulo sobe, e cair recomeca."""
    from PIL import Image
    import numpy as np

    def pos():
        """A MAIOR mancha azul, nao a media de todo o azul da pagina."""
        a, _ = nav.captura("/tmp/_c2_j.png")
        im = np.asarray(Image.open(a).convert("RGB"), dtype=int)
        g = comum.maior_mancha((im[:, :, 2] > 100) &
                               (im[:, :, 2] - im[:, :, 0] > 40) &
                               (im[:, :, 1] < 120))
        return (g[0], g[1]) if g and g[2] > 600 else None

    p = nav.acha_texto("play")
    A.gesto("jogar", "g06", p, lambda: clique(*p), espera=6)
    editor.exige_jogo()
    clique(1470, 620); time.sleep(2)
    base = pos()
    A.cap("p16_jogo")
    # 1) o pulo sobe
    alturas = []
    rs.segura_tecla(126, 0.2)
    for _ in range(6):
        time.sleep(0.12)
        q = pos()
        alturas.append(q[1] if q else None)
    validos = [a for a in alturas if a]
    sobe = base[1] - min(validos) if validos else 0
    A.cap("p17_pulo")
    print(f"   pulo: subiu {sobe} px", flush=True)
    if sobe < 60:
        raise RuntimeError(f"o pulo subiu so {sobe} px — a aula promete pular "
                           "entre plataformas")
    # 2) cair na lava recomeca
    #
    # SEGURANDO a seta, nao com toquinhos. Com toques de 0,12 s o boneco anda
    # um passo curto e para: eu dava dezoito e ele nem chegava na beirada do
    # chao — a sonda concluia que o jogo nao recomeca, quando ele nem tinha
    # caido. E assim que a crianca joga: segurando.
    # O REINICIO SE PROVA PELO PAR: o boneco SAI de onde estava e VOLTA para
    # la. A queda e rapida demais para aparecer numa foto — ele cai e renasce
    # entre duas capturas minhas — entao o que eu procuro e o sumico (ou uma
    # posicao bem longe) seguido do reaparecimento na origem.
    #
    # A versao anterior desta sonda lia a MEDIA de todo o azul da pagina e
    # andava com toquinhos de 0,12 s: ela deu "recomecou" sem o boneco ter
    # saido do lugar. Prova que passa por acaso e pior que prova que falha.
    caiu = False
    for k in range(14):
        rs.segura_tecla(123, 0.3)          # 123 = seta esquerda
        for _ in range(5):
            q = pos()                       # a captura ja leva ~0,4 s
            if q is None or abs(q[0] - base[0]) > 80:
                caiu = True
            elif caiu and abs(q[0] - base[0]) < 40:
                A.cap("p18_recomecou")
                print(f"   caiu na lava e o jogo RECOMECOU (leitura {k+1})", flush=True)
                return True
    raise RuntimeError("andei para a esquerda ate o fim e nao vi o jogo recomecar")


def main():
    alvo = sys.argv[1] if len(sys.argv) > 1 else None
    nomes = [f.__name__ for f in ETAPAS]
    fns = ETAPAS if not alvo else ETAPAS[nomes.index(alvo):]
    for f in fns:
        print(f"== {f.__name__} ==", flush=True)
        f()
    print("== fim ==", flush=True)


if __name__ == "__main__":
    main()
