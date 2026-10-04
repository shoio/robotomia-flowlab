#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Captura da Aula 1 — Pega-moedas.

   O jogo: um boneco que corre num chao, e uma moeda que some quando ele
   encosta. Termina jogavel, com link para mandar para a familia.

   Cada gesto que a aula pede fica registrado em `alvos.json` com o PONTO do
   clique e QUAL BOTAO — e dai sai a animacao com o mouse do botao aceso.

   Medidas da tela (pagina em 100%):
   - a area do nivel comeca em (958, 415) e cada celula tem 64 px;
   - o OK do painel do objeto e branco sobre AZUL (o OCR nao le) e muda de
     altura quando o Physics esta aberto: acha-se pela cor."""
import os, sys, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rs, nav, editor, blocos

D = "aula1"
ALVOS = os.path.join(D, "alvos.json")

import comum
from comum import (celula, clique, pinta, nomeia, abre_sprite, marca_caixa,
                   arrasta_slider, fecha_painel_objeto, confere_fase,
                   LINHA_CHAO, LINHA_ANDAR, COL_JOGADOR, COL_MOEDA, COLS_CHAO,
                   CELULA, GRADE_X, GRADE_Y, A, etapa, ETAPAS)

comum.pasta("aula1")
ETAPAS.clear()      # a lista vive em comum.py: cada aula comeca a sua
D = "aula1"

@etapa
def novo():
    A.url = editor.jogo_novo()
    print("   jogo:", A.url, flush=True)
    A.cap("p01_vazio")
    return True


@etapa
def jogador():
    x, y = celula(COL_JOGADOR, LINHA_ANDAR)
    A.gesto("criar_objeto", "g01", (x, y), lambda: clique(x, y), espera=1.5)
    a, _ = nav.captura("/tmp/_rad.png")
    p = nav.acha_texto("create", arquivo=a)
    A.gesto("escolher_create", "g02", p, lambda: clique(*p), espera=3)
    editor.espera_tela("behaviors", limite=20)
    A.cap("p02_painel")
    nomeia("Jogador")
    A.cap("p03_nome")
    abre_sprite()
    A.cap("p04_sprite")
    pinta("azul")
    A.cap("p05_azul")
    clique(*SPRITE_OK); time.sleep(2); nav.espera_parar(limite=15)
    a, _ = nav.captura("/tmp/_fis.png")
    q = nav.acha_texto("physics", arquivo=a)
    A.gesto("abrir_physics", "g03", q, lambda: clique(*q), espera=2.5)
    A.gesto("marcar_movable", "g04", (1681, 476),
            lambda: marca_caixa("movable", True), espera=1.2)
    A.cap("p06_movable")
    fecha_painel_objeto()
    A.cap("p07_jogador_pronto")
    return True


@etapa
def peso():
    """Deixa o jogador PESADO. Sem isto ele corre 180 px por quadro e atravessa
       a moeda sem a fisica registrar contato: a moeda nao some e nada no
       editor acusa. Medido: com densidade e friccao no maximo o passo cai
       para 52 px e a colisao vale."""
    x, y = celula(COL_JOGADOR, LINHA_ANDAR)
    editor.objeto_ou_abre(x, y)
    a, _ = nav.captura("/tmp/_c1_fis.png")
    q = nav.acha_texto("physics", arquivo=a)
    A.gesto("abrir_physics2", "g07", q, lambda: clique(*q), espera=2.5)
    marca_caixa("movable", True)      # sem isto a Densidade fica desabilitada
    arrasta_slider("density")
    A.cap("p21_densidade")
    arrasta_slider("friction")
    A.cap("p22_friccao")
    fecha_painel_objeto()
    return True


@etapa
def movimento():
    x, y = celula(COL_JOGADOR, LINHA_ANDAR)
    editor.objeto_ou_abre(x, y)
    editor.abre_comportamentos()
    A.cap("p08_comportamentos")
    blocos.abre_categoria("Behavior Bundles")
    A.cap("p09_pacotes")
    b = blocos.solta("Run & Jump", 1400, 700)
    A.cap("p10_run_and_jump")
    print("   pacote:", b, flush=True)
    time.sleep(2.5)                     # o Flowlab precisa de tempo para guardar
    editor.fecha_comportamentos()
    time.sleep(2.5)
    fecha_painel_objeto()
    time.sleep(2.0)
    # PROVA de que ficou salvo: reabre e procura. Sem isto, o pacote some em
    # silencio, o jogador nao anda, e nada no editor acusa — foi o que fez a
    # Aula 1 falhar tres vezes seguidas.
    editor.objeto_ou_abre(x, y)
    editor.abre_comportamentos()
    # o canvas demora a desenhar: tento algumas vezes antes de acusar sumico,
    # senao eu reprovo um pacote que esta la e so nao foi pintado ainda
    lido = ""
    for tentativa in range(4):
        time.sleep(1.5)
        a, _ = nav.captura("/tmp/_c1_persist.png")
        lido = " ".join(t for t, *_ in rs.ocr_forte(a, regiao=(0.2, 0.05, 1, 0.9),
                                                    psm="6")).lower()
        if "run" in lido or "jump" in lido:
            break
    if "run" not in lido and "jump" not in lido:
        raise RuntimeError("o pacote Run & Jump NAO ficou salvo no jogador "
                           f"(li {lido[:80]!r})")
    print("   pacote conferido depois de reabrir", flush=True)
    editor.fecha_comportamentos()
    time.sleep(2.0)
    fecha_painel_objeto()
    return True


@etapa
def chao():
    """Chao CONTIGUO: pecas coladas, de 64 em 64 px. Na primeira montagem elas
       sairam espacadas e o jogador caiu pelo vao."""
    x, y = celula(COLS_CHAO[0], LINHA_CHAO)
    editor.objeto_ou_abre(x, y)
    nomeia("Chao")
    abre_sprite()
    pinta("verde")
    A.cap("p11_chao_verde")
    clique(*SPRITE_OK); time.sleep(2); nav.espera_parar(limite=15)
    fecha_painel_objeto()
    clique(x, y); time.sleep(1.5)
    a, _ = nav.captura("/tmp/_rad2.png")
    p = nav.acha_texto("clone", arquivo=a)
    A.gesto("clonar", "g05", p, lambda: clique(*p), espera=2)
    for c in COLS_CHAO[1:]:
        cx, cy = celula(c, LINHA_CHAO)
        clique(cx, cy); time.sleep(1.1)        # devagar: clique rapido nao coloca
    A.cap("p12_chao")
    q = nav.acha_texto("done cloning")
    clique(*q); time.sleep(2); nav.espera_parar(limite=15)
    A.cap("p13_chao_pronto")
    return True


@etapa
def moeda():
    x, y = celula(COL_MOEDA, LINHA_ANDAR)
    editor.objeto_ou_abre(x, y)
    nomeia("Moeda")
    abre_sprite()
    pinta("amarelo")
    A.cap("p14_moeda_amarela")
    clique(*SPRITE_OK); time.sleep(2); nav.espera_parar(limite=15)
    editor.abre_comportamentos()
    c = blocos.solta("Collision", 1100, 500)
    A.cap("p15_collision")
    d = blocos.solta("Destroyer", 1900, 950)
    A.cap("p16_destroyer")
    blocos.liga_fixo(c, "hit", d, "in")
    A.cap("p17_fio")
    editor.fecha_comportamentos()
    fecha_painel_objeto()
    A.cap("p18_moeda_pronta")
    return True


@etapa
def prova():
    """Joga, anda para a direita e PROVA que a moeda sumiu."""
    from PIL import Image
    import numpy as np

    def amarelo(f):
        im = np.asarray(Image.open(os.path.join(D, f)).convert("RGB"), dtype=int)
        return int(((im[:, :, 0] > 200) & (im[:, :, 1] > 140) &
                    (im[:, :, 1] < 200) & (im[:, :, 2] < 110)).sum())

    confere_fase()
    p = nav.acha_texto("play")
    A.gesto("jogar", "g06", p, lambda: clique(*p), espera=6)
    clique(1470, 640); time.sleep(1.5)
    antes = A.cap("p19_jogo")
    n0 = amarelo(antes)
    # toques CURTOS, conferindo a cada um: segurando, o boneco passa correndo
    # pela moeda e cai no fim do chao antes de a colisao valer
    n1 = n0
    for k in range(14):
        rs.segura_tecla(124, 0.12); time.sleep(0.45)   # 124 = seta direita
        n1 = amarelo(A.cap("p20_pegou"))
        if n1 < n0 * 0.5:
            print(f"   a moeda sumiu no toque {k+1}", flush=True)
            break
    print(f"   moeda: {n0} px antes, {n1} px depois", flush=True)
    if n1 >= n0 * 0.5:
        raise RuntimeError(f"a moeda NAO sumiu ({n0} -> {n1} px amarelos): "
                           "o jogo nao faz o que a aula promete")
    print("   PROVADO: a moeda sumiu quando o jogador encostou", flush=True)
    return True


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
