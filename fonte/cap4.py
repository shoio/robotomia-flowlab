#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aula 4 — Nave e tiro. Constroi o jogo no Flowlab e fotografa cada gesto.

   Primeira aula escrita sobre o `aula_comum.py`: tudo o que ela faz igual as
   anteriores vem de la, e ja com leitura de volta. O que sobra aqui e so o
   que e DESTA aula.

   As tres pecas novas foram medidas antes de a aula ser escrita (§2k e §2l do
   PADRAO.md), num jogo de prototipo:
     - `Keyboard` dispara pela bancada, e nasce SEM tecla;
     - `Timer` dispara sozinho (`auto start`), em decimos de segundo;
     - `Emit` nasce no proprio objeto, ja sai andando e EXPIRA sozinho — por
       isso nao ha "limpar o que sai da tela" nesta aula. Angulo: 0 e direita,
       90 e BAIXO, 270 e cima. `Expire After` e em trinta avos de segundo.

       BANCADA=1 python3 fonte/roda_aula.py 4
"""
import os, shutil, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rs, nav, editor, blocos, comum

comum.pasta("aula4")
import aula_comum as AC
from aula_comum import (celula, clique, A, etapa, ETAPAS, cria_objeto, da_fisica,
                        confere_fisica, abre_mesa, fecha_mesa, rastreio, cor)
from comum import fecha_painel_objeto
ETAPAS.clear()

D = "aula4"
CEU = "0B1026"          # azul quase preto: e ele que faz o tiro aparecer
AC.SPRITES = {
    "Nave":    ("Gustavo Sprites", "Ships", 0, 0),        # nave cinza, aponta para cima
    "Tiro":    ("Gustavo Sprites", "Projectiles", 0, 2),  # o raio amarelo
    "Inimigo": ("Gustavo Sprites", "Ships", 3, 0),        # nave vermelha
    "Canhao":  ("Gustavo Sprites", "Ships", 2, 1),        # nave roxa, la em cima
}

# A FASE CABE NA TELA. Aqui o cenario nao e comprido como na Aula 2: o que se
# move e o que o jogo CRIA, nao a vista.
CEL_NAVE = (8, 10)
CEL_TIRO = (1, 1)
CEL_INIMIGO = (14, 1)
CEL_CANHAO = (8, 0)

ANGULO_CIMA = 270       # medido: 0 e direita, 90 e baixo
ANGULO_BAIXO = 90
VIDA_DO_TIRO = 90       # trinta avos de segundo => 3 s
VIDA_DO_INIMIGO = 150   # 5 s, o bastante para atravessar a tela


@etapa
def novo():
    A.url = editor.jogo_novo()
    print("   jogo:", A.url, flush=True)
    A.guarda_url()
    comum.calibra_grade(16, 12)
    A.cap("p01_vazio")
    # OS TRES CLIPES DE ABERTURA sao os mesmos de toda aula: eles acontecem no
    # SITE do Flowlab, antes de existir jogo nenhum, e o gesto e identico.
    # Reaproveitar aqui nao e a armadilha de reusar foto de outro jogo — nao ha
    # jogo nestes passos.
    for nome in ("abrir_my_games.gif", "novo_jogo.gif", "empty_project.gif"):
        os.makedirs(f"{D}/gifs", exist_ok=True)
        if not os.path.exists(f"{D}/gifs/{nome}"):
            shutil.copy(f"aula3/gifs/{nome}", f"{D}/gifs/{nome}")
    A.gesto("abrir_niveis", "g08a", (0, 0),
            lambda: editor.abre_niveis(), espera=1.8)
    A.gesto("pintar_o_ceu", "g08", (0, 0),
            lambda: editor.cor_do_ceu(CEU, abrir=False), espera=2.0)
    editor.volta_ao_nivel()
    A.cap("p02_ceu")
    return True


@etapa
def nave():
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    x, y = celula(*CEL_NAVE)
    A.gesto("criar_objeto", "g01", (x, y), lambda: clique(x, y), espera=1.5)
    a, _ = nav.captura("/tmp/_c4_rad.png")
    p = nav.acha_texto("create", arquivo=a)
    A.gesto("escolher_create", "g02", p, lambda: clique(*p), espera=3)
    editor.espera_tela("behaviors", limite=20)
    comum.nomeia("Nave"); comum.nomeia_tipo("Nave")
    A.cap("p03_nome")
    comum.abre_sprite()
    pacote, sub, lin, col = AC.SPRITES["Nave"]
    comum.abre_grade_sprite(pacote, sub)
    A.gesto("escolher_sprite", "g13", (0, 0),
            lambda: AC.poe_sprite("Nave", so_clique=True), espera=2.0)
    clique(*comum.SPRITE_OK); time.sleep(2); nav.espera_parar(limite=15)
    A.cap("p04_nave")
    # NO ESPACO NAO HA CHAO: com gravidade a nave cai para fora da tela assim
    # que o jogo comeca, e nada no editor acusa.
    A.gesto("abrir_physics", "g03", (0, 0), lambda: comum.abre_fisica(), espera=2.5)
    A.gesto("marcar_movable", "g04", (0, 0),
            lambda: comum.marca_caixa("movable", True), espera=1.2)
    A.gesto("sem_gravidade", "g05", (0, 0),
            lambda: comum.marca_caixa("affected by gravity", False), espera=1.2)
    A.cap("p05_fisica")
    fecha_painel_objeto(); time.sleep(1.5)
    editor.objeto_ou_abre(x, y)
    confere_fisica(movable=True, gravidade=False)
    fecha_painel_objeto(); time.sleep(1.5)
    return True


@etapa
def movimento():
    abre_mesa(*CEL_NAVE)
    blocos.abre_categoria("Behavior Bundles")
    b = blocos.bloco_ou_solta("Top Down Movement", 1500, 760)
    print("   pacote:", b, flush=True)
    A.cap("p06_movimento")
    time.sleep(2.5)
    fecha_mesa()
    return True


@etapa
def tiro():
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    cria_objeto(*CEL_TIRO, "Tiro", tipo="Tiro")
    A.cap("p07_tiro")
    # A CAIXINHA QUE JA MORDEU TRES VEZES: sem `movable` nenhuma forca tem
    # efeito, e o tiro nasce e fica parado no ar.
    x, y = celula(*CEL_TIRO)
    editor.objeto_ou_abre(x, y)
    comum.abre_fisica(); time.sleep(1.5)
    A.gesto("tiro_movable", "g06", (0, 0),
            lambda: comum.marca_caixa("movable", True), espera=1.2)
    comum.marca_caixa("affected by gravity", False)
    A.cap("p08_tiro_fisica")
    fecha_painel_objeto(); time.sleep(1.5)
    editor.objeto_ou_abre(x, y)
    confere_fisica(movable=True, gravidade=False)
    fecha_painel_objeto(); time.sleep(1.5)
    return True


@etapa
def atira():
    abre_mesa(*CEL_NAVE)
    blocos.abre_categoria("Components")
    # NA PALHETA ele e `Emit`; NA MESA o titulo e `Emitter`.
    em = blocos.bloco_ou_solta("Emit", 1500, 1150, titulo="Emitter")
    A.cap("p09_emitter")
    blocos.abre_ajustes(em); time.sleep(1.5)
    A.gesto("ajustes_do_tiro", "g07", (0, 0),
            lambda: blocos.escolhe_na_lista("object to emit", "Tiro"), espera=1.6)
    blocos.campo_ao_lado("emit angle", ANGULO_CIMA)
    blocos.campo_ao_lado("expire after", VIDA_DO_TIRO)
    blocos.fecha_ajustes(); time.sleep(1.0)
    A.cap("p10_ajustes")
    blocos.abre_categoria("Triggers")
    k = blocos.bloco_ou_solta("Keyboard", 1000, 1150)
    # O BLOCO NASCE SEM TECLA: `Current key:` vem vazio.
    blocos.abre_ajustes(k); time.sleep(1.3)
    b, _ = nav.captura("/tmp/_c4_key.png")
    q = nav.acha_texto("change key", arquivo=b)
    if not q:
        raise RuntimeError("nao achei o `Change Key` no painel do Keyboard")
    def troca_a_tecla():
        rs.clique_img(q[0], q[1], escala=2.0, janela=nav.janela())
        time.sleep(1.4)
        rs.tecla(49)              # 49 = barra de espaco
        time.sleep(1.2)
        return q

    A.gesto("muda_a_tecla", "g09", q, troca_a_tecla, espera=1.4)
    c, _ = nav.captura("/tmp/_c4_key2.png")
    if not rs.tem_texto("spacebar", arquivo=c):
        raise RuntimeError("apertei o espaco no `Change Key` e o painel nao "
                           "mostra `Spacebar`")
    print("   tecla = Spacebar", flush=True)
    blocos.fecha_ajustes(); time.sleep(1.2)
    em = blocos.acha_bloco("Emitter")
    blocos.liga_fixo(k, "down", em, "emit")
    A.cap("p11_fio_tiro")
    time.sleep(2)
    fecha_mesa()
    return True


@etapa
def prova_tiro():
    """A promessa do passo 16: apertar espaco faz um tiro SUBIR."""
    import numpy as np
    from PIL import Image
    cor_tiro, tol = rastreio("Tiro", "Nave", "Inimigo")
    print(f"   rastreando o tiro por {cor_tiro} (tol {tol})", flush=True)
    editor.volta_ao_editor(); time.sleep(2)
    editor.volta_ao_nivel()
    p = nav.acha_texto("play")
    if not p:
        raise RuntimeError("nao achei o botao Play (estou mesmo no editor?)")
    A.gesto("jogar", "g10", p, lambda: clique(*p), espera=6)
    editor.exige_jogo()
    clique(1470, 620); time.sleep(1.5)

    def tiros():
        """Quantos pixels de tiro ha na tela, e a altura do mais alto.

           A PECA PARADA DO CANTO conta como tiro: ela esta na linha 1, em
           cima a esquerda. Por isso eu meco so a coluna da nave."""
        a, _ = nav.captura("/tmp/_c4_j.png")
        im = np.asarray(Image.open(a).convert("RGB"), dtype=int)
        m = comum.mascara_cor(im, cor_tiro, tol)
        faixa = m[:, 1300:1700]
        ys, _xs = np.nonzero(faixa)
        return int(faixa.sum()), (int(ys.min()) if len(ys) else None)

    antes, _ = tiros()
    rs.segura_tecla(49, 0.12)
    serie = []
    for _ in range(5):
        serie.append(tiros())
    A.cap("p12_tiro")
    print(f"   antes do espaco: {antes} px de tiro na coluna da nave", flush=True)
    print(f"   depois: {serie}", flush=True)
    picos = [n for n, _ in serie]
    if max(picos) <= antes:
        raise RuntimeError(f"apertei espaco e nao nasceu tiro nenhum na coluna "
                           f"da nave (antes {antes}, depois {picos})")
    print("   PROVADO: o espaco faz nascer um tiro", flush=True)
    return True


@etapa
def inimigo():
    editor.volta_ao_editor(); time.sleep(2)
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    cria_objeto(*CEL_INIMIGO, "Inimigo", tipo="Inimigo")
    x, y = celula(*CEL_INIMIGO)
    editor.objeto_ou_abre(x, y)
    da_fisica(movable=True, gravidade=False, densidade=None, atrito=False)
    A.cap("p13_inimigo")
    fecha_painel_objeto(); time.sleep(1.5)
    return True


@etapa
def canhao():
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    cria_objeto(*CEL_CANHAO, "Canhao", tipo="Canhao")
    A.cap("p14_canhao")
    abre_mesa(*CEL_CANHAO)
    blocos.abre_categoria("Components")
    em = blocos.bloco_ou_solta("Emit", 1500, 1150, titulo="Emitter")
    blocos.abre_ajustes(em); time.sleep(1.5)
    blocos.escolhe_na_lista("object to emit", "Inimigo")
    blocos.campo_ao_lado("emit angle", ANGULO_BAIXO)
    blocos.campo_ao_lado("expire after", VIDA_DO_INIMIGO)
    blocos.fecha_ajustes(); time.sleep(1.0)
    blocos.abre_categoria("Triggers")
    t = blocos.bloco_ou_solta("Timer", 1000, 1150)
    blocos.abre_ajustes(t); time.sleep(1.3)
    blocos.marca_do_bloco("repeat forever", True)
    blocos.fecha_ajustes(); time.sleep(1.0)
    em = blocos.acha_bloco("Emitter")
    blocos.liga_fixo(t, "out", em, "emit")
    A.cap("p15_timer")
    time.sleep(2)
    fecha_mesa()
    return True


@etapa
def destroi():
    abre_mesa(*CEL_INIMIGO)
    blocos.abre_categoria("Triggers")
    c = blocos.bloco_ou_solta("Collision", 1120, 1150)
    d = blocos.bloco_ou_solta("Destroyer", 1700, 1150)
    blocos.liga_fixo(c, "hit", d, "in")
    # COM QUEM a batida conta. Em `Any Type` o inimigo se destroi ao encostar
    # em qualquer coisa — inclusive em outro inimigo.
    blocos.escolhe_tipo_da_colisao(c, "Tiro")
    A.cap("p16_fio_destroi")
    time.sleep(2)
    fecha_mesa()
    return True


@etapa
def prova():
    """As duas promessas do fim: os inimigos DESCEM sozinhos, e o tiro os APAGA."""
    import numpy as np
    from PIL import Image
    cor_inim, tol_i = rastreio("Inimigo", "Nave", "Tiro")
    print(f"   rastreando o inimigo por {cor_inim} (tol {tol_i})", flush=True)
    editor.volta_ao_editor(); time.sleep(2)
    editor.volta_ao_nivel()
    p = nav.acha_texto("play")
    clique(*p); time.sleep(7); nav.espera_parar(limite=20)
    editor.exige_jogo()
    clique(1470, 620); time.sleep(1.5)

    def inimigos():
        a, _ = nav.captura("/tmp/_c4_p.png")
        im = np.asarray(Image.open(a).convert("RGB"), dtype=int)
        m = comum.mascara_cor(im, cor_inim, tol_i)
        ys, _xs = np.nonzero(m)
        return int(m.sum()), (int(ys.mean()) if len(ys) else None)

    # 1) ELES DESCEM SOZINHOS: sem tecla nenhuma, a altura media do vermelho
    #    tem de aumentar (y cresce para baixo).
    alturas = []
    for _ in range(8):
        n, y = inimigos()
        if y is not None:
            alturas.append(y)
        time.sleep(0.5)
    print(f"   altura media do vermelho: {alturas}", flush=True)
    if len(alturas) < 3 or max(alturas) - min(alturas) < 60:
        raise RuntimeError(f"os inimigos nao desceram sozinhos: {alturas}")
    A.cap("p17_jogo")
    print(f"   PROVADO: os inimigos descem {max(alturas) - min(alturas)} px "
          "sem ninguem apertar tecla", flush=True)
    return True


def main():
    AC.main(sys.modules[__name__])


if __name__ == "__main__":
    main()
