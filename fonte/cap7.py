#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aula 7 — Empurra-blocos. Constroi o jogo no Flowlab e fotografa cada gesto.

   O jogo: tres caixas no chao, um alvo marcado e uma porta fechando a saida.
   Empurrar cada caixa ate o alvo faz o PLACAR subir. Quando ele passa de 2 —
   ou seja, na terceira caixa — a porta abre sozinha.

   O que e NOVO: o numero passa a DECIDIR. Na Aula 5 ele so aparecia na tela;
   aqui o `Filter` olha para ele e deixa passar, ou nao.

   MEDIDO ANTES (PADRAO.md §2w), no prototipo 3155615:
   - `Filter` tem `set` e `in` na entrada, `pass` e `fail` na saida, e mostra a
     condicao embaixo do dado: nasce em `input > 0`. O painel e um seletor
     (`greater than`) mais um campo de numero com `-` e `+`;
   - o boneco EMPURRA uma caixa `movable`: em 4 s segurando a seta ele a levou
     para fora da tela. Nao e preciso bloco nenhum para isso — e a fisica;
   - ⚠️ a caixa de madeira tem as MESMAS cores da terra do chao, entao
     rastrea-la pela cor nao serve. Quem prova a entrega e o PLACAR na tela,
     lido por OCR, que e a tecnica que a Aula 5 validou.

       BANCADA=1 python3 fonte/roda_aula.py 7
"""
import os, shutil, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rs, nav, editor, blocos, comum

comum.pasta("aula7")
import aula_comum as AC
from aula_comum import (celula, clique, A, etapa, ETAPAS, cria_objeto, clona,
                        clona_casas, da_fisica, confere_fisica, abre_mesa,
                        fecha_mesa, rastreio, cor)
from comum import fecha_painel_objeto
ETAPAS.clear()

D = "aula7"
CEU = "A8DADC"
AC.SPRITES = {
    "Jogador": ("Flowlab Sprites", "Characters", 0, 0),
    "Chao":    ("Flowlab Sprites", "Blocks", 0, 0),
    "Caixa":   ("Flowlab Sprites", "Blocks", 0, 1),      # a caixa de madeira
    "Alvo":    ("Flowlab Sprites", "Blocks", 4, 0),      # o tijolo rosa, que marca o lugar
    "Porta":   ("Flowlab Sprites", "Blocks", 3, 0),      # o vao escuro, igual ao da Aula 6
}

LINHA_CHAO = 10
CEL_JOGADOR = (1, 9)
CEL_CAIXA = (3, 9)
COLUNAS_DAS_CAIXAS = (5, 7)
CEL_ALVO = (11, 9)
CEL_PORTA = (13, 9)
CASAS_DA_PORTA = [(13, 8), (13, 7)]
QUANTAS_CAIXAS = 3
CONDICAO = QUANTAS_CAIXAS - 1          # `input > 2` e o mesmo que "tres ou mais"

FILA_A = (0.12, 0.06, 1.0, 0.50)
FILA_B = (0.12, 0.50, 1.0, 0.96)
Y_A, Y_B = 560, 1150


def _area_do_jogo(im):
    """A caixa (y0, y1, x0, x1) da fase, achada pela COR DO CEU.

       Sem recorte a medida pega a barra escura do NAVEGADOR, que nunca muda —
       foi assim que, na Aula 6, o "topo do escuro" ficou preso em y=31 antes e
       depois, numa tela em que a porta tinha sumido."""
    import numpy as _np
    rgb = tuple(int(CEU[i:i + 2], 16) for i in (0, 2, 4))
    ys, xs = _np.nonzero(comum.mascara_cor(im, rgb, 16))
    if len(ys) < 20000:
        raise RuntimeError(f"nao achei o ceu da fase na tela ({len(ys)} px)")
    return int(ys.min()), int(ys.max()), int(xs.min()), int(xs.max())


def _placar():
    """O numero que o `Label` mostra, lido da tela do jogo."""
    a, _ = nav.captura("/tmp/_c7_pl.png")
    for t, *_ in rs.ocr_forte(a, regiao=(0.33, 0.08, 0.55, 0.22), psm="7"):
        so_digitos = "".join(ch for ch in t if ch.isdigit())
        if so_digitos:
            return int(so_digitos)
    return None


@etapa
def novo():
    A.url = editor.jogo_novo()
    print("   jogo:", A.url, flush=True)
    A.guarda_url()
    comum.calibra_grade(16, 12)
    A.cap("p01_vazio")
    for nome in ("abrir_my_games.gif", "novo_jogo.gif", "empty_project.gif"):
        os.makedirs(f"{D}/gifs", exist_ok=True)
        if not os.path.exists(f"{D}/gifs/{nome}"):
            shutil.copy(f"aula6/gifs/{nome}", f"{D}/gifs/{nome}")
    A.gesto("abrir_niveis", "g08a", (0, 0), lambda: editor.abre_niveis(), espera=1.8)
    A.gesto("pintar_o_ceu", "g08", (0, 0),
            lambda: editor.cor_do_ceu(CEU, abrir=False), espera=2.0)
    editor.volta_ao_nivel()
    A.cap("p02_ceu")
    return True


@etapa
def jogador():
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    x, y = celula(*CEL_JOGADOR)
    A.gesto("criar_objeto", "g01", (x, y), lambda: clique(x, y), espera=1.5)
    a, _ = nav.captura("/tmp/_c7_rad.png")
    p = nav.acha_texto("create", arquivo=a)
    A.gesto("escolher_create", "g02", p, lambda: clique(*p), espera=3)
    editor.espera_tela("behaviors", limite=20)
    comum.nomeia("Jogador"); comum.nomeia_tipo("Jogador")
    A.cap("p03_nome")
    comum.abre_sprite()
    pacote, sub, lin, col = AC.SPRITES["Jogador"]
    comum.abre_grade_sprite(pacote, sub)
    A.gesto("escolher_sprite", "g13", (0, 0),
            lambda: AC.poe_sprite("Jogador", so_clique=True), espera=2.0)
    clique(*comum.SPRITE_OK); time.sleep(2); nav.espera_parar(limite=15)
    A.cap("p04_jogador")
    A.gesto("abrir_physics", "g03", (0, 0), lambda: comum.abre_fisica(), espera=2.5)
    A.gesto("marcar_movable", "g04", (0, 0),
            lambda: comum.marca_caixa("movable", True), espera=1.2)
    comum.marca_caixa("affected by gravity", True)
    A.cap("p05_fisica")
    fecha_painel_objeto(); time.sleep(1.5)
    editor.objeto_ou_abre(x, y)
    confere_fisica(movable=True, gravidade=True)
    fecha_painel_objeto(); time.sleep(1.5)
    return True


@etapa
def anda():
    abre_mesa(*CEL_JOGADOR)
    blocos.abre_categoria("Behavior Bundles")
    blocos.bloco_ou_solta("Run & Jump", 1500, 760)
    A.cap("p06_correr")
    time.sleep(2.5)
    fecha_mesa()
    return True


@etapa
def chao():
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    cria_objeto(0, LINHA_CHAO, "Chao", tipo="Chao")
    A.gesto("clonar_o_chao", "g05", (0, 0),
            lambda: clona(0, LINHA_CHAO, "Chao", range(1, 16)), espera=2.0)
    A.cap("p07_chao")
    return True


@etapa
def caixas():
    """As caixas EMPURRAVEIS. Nao ha bloco nenhum nelas: e a fisica.

       `movable` marcado e gravidade ligada — e so. Medido no prototipo: em 4 s
       segurando a seta, o boneco levou a caixa para fora da tela."""
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    cria_objeto(*CEL_CAIXA, "Caixa", tipo="Caixa")
    x, y = celula(*CEL_CAIXA)
    editor.objeto_ou_abre(x, y)
    da_fisica(movable=True, gravidade=True, atrito=False)
    A.cap("p08_caixa")
    fecha_painel_objeto(); time.sleep(1.5)
    editor.objeto_ou_abre(x, y)
    confere_fisica(movable=True, gravidade=True)
    fecha_painel_objeto(); time.sleep(1.5)
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    A.gesto("clonar_as_caixas", "g06", (0, 0),
            lambda: clona(*CEL_CAIXA, "Caixa", COLUNAS_DAS_CAIXAS), espera=2.0)
    A.cap("p09_tres_caixas")
    return True


@etapa
def alvo():
    """O ALVO FICA SOLIDO, e isso foi medido do jeito mais barato possivel: o
       proprio Flowlab escreveu na mesa, num aviso amarelo,

           "This object has disabled collisions, so Collision will not trigger"

       Eu tinha desmarcado `is solid` para a caixa ENTRAR no alvo, e descobri
       que no Flowlab `is solid` desligado nao e "atravessa mas sente": e
       colisao DESLIGADA. Um `Collision` naquele objeto nunca dispararia.

       O conserto melhorou a aula: quem sente a batida e a CAIXA (que tem
       colisao ligada), e ela manda um recado para o alvo — a mesma dupla
       `Message`/`Mailbox` da Aula 6. O alvo nem precisa de fisica."""
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    cria_objeto(*CEL_ALVO, "Alvo", tipo="Alvo")
    A.cap("p10_alvo")
    return True


@etapa
def caixa_entrega():
    """A caixa e a CHAVE da Aula 6: encostou, manda o recado, some."""
    abre_mesa(*CEL_CAIXA)
    blocos.abre_categoria("Triggers")
    c = AC._na_fila(blocos.bloco_ou_solta("Collision", 900, Y_A, regiao=FILA_A),
                    FILA_A, "Collision da caixa")
    blocos.abre_categoria("Components")
    ms = AC._na_fila(blocos.bloco_ou_solta("Message", 1750, Y_A, regiao=FILA_A),
                     FILA_A, "Message da caixa")
    de = AC._na_fila(blocos.bloco_ou_solta("Destroyer", 2500, Y_A, regiao=FILA_A),
                     FILA_A, "Destroyer da caixa")
    blocos.liga_fixo(c, "hit", ms, "send")
    blocos.liga_fixo(ms, "done", de, "in")
    blocos.escolhe_tipo_da_colisao(c, "Alvo")
    blocos.abre_ajustes(ms); time.sleep(1.5)
    A.gesto("recado_para_o_alvo", "g12", (0, 0),
            lambda: blocos.escolhe_na_lista("send to", "choose objects", dy=55),
            espera=1.6)
    time.sleep(1.0)
    blocos.escolhe_na_lista("select type", "alvo")
    blocos.fecha_ajustes(); time.sleep(1.0)
    A.cap("p11_caixa_entrega")
    time.sleep(2)
    fecha_mesa()
    return True


@etapa
def alvo_conta():
    """O trio do placar da Aula 5, agora disparado por um RECADO."""
    abre_mesa(*CEL_ALVO)
    blocos.abre_categoria("Triggers")
    mb = AC._na_fila(blocos.bloco_ou_solta("Mailbox", 900, Y_A, regiao=FILA_A),
                     FILA_A, "Mailbox do alvo")
    blocos.abre_categoria("Logic & Math")
    nu = AC._na_fila(blocos.bloco_ou_solta("Number", 1700, Y_A, regiao=FILA_A),
                     FILA_A, "Number do alvo")
    blocos.abre_categoria("GUI")
    lb = AC._na_fila(blocos.bloco_ou_solta("Label", 2500, Y_A, regiao=FILA_A),
                     FILA_A, "Label do alvo")
    blocos.liga_fixo(mb, "out", nu, "mais")
    blocos.liga_fixo(nu, "out", lb, "text")
    print("   alvo: Mailbox -> Number.+ -> Label.text", flush=True)
    A.cap("p12_alvo_conta")
    time.sleep(2)
    fecha_mesa()
    return True


@etapa
def prova_conta():
    """A promessa do passo 17: empurrar uma caixa faz o placar subir."""
    editor.volta_ao_editor(); time.sleep(2)
    editor.volta_ao_nivel()
    p = nav.acha_texto("play")
    if not p:
        raise RuntimeError("nao achei o botao Play")
    A.gesto("jogar", "g10", p, lambda: clique(*p), espera=6)
    editor.exige_jogo()
    clique(1470, 620); time.sleep(1.5)
    antes = _placar()
    serie = []
    for _ in range(10):
        rs.segura_tecla(rs.DIR, 0.6)
        time.sleep(0.4)
        n = _placar()
        if n is not None:
            serie.append(n)
        if n and n >= 1:
            # A FOTO SAI AQUI, com o numero ainda em 1.
            #
            # Tirada depois do laco ela saia mostrando 2: as caixas andam em
            # TREM, e a segunda chega logo atras da primeira. O quadro verde do
            # passo promete "o numero vira 1", e a crianca compara a tela dela
            # com a figura.
            A.cap("p13_placar_um")
            break
    print(f"   placar: antes {antes}, empurrando {serie}", flush=True)
    if not serie or max(serie) < 1:
        raise RuntimeError(f"empurrei a caixa ate o alvo e o placar nao subiu "
                           f"({antes} -> {serie})")
    print(f"   PROVADO: entregar uma caixa leva o placar a {max(serie)}",
          flush=True)
    editor.volta_ao_editor(); time.sleep(2)
    return True


@etapa
def porta():
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    cria_objeto(*CEL_PORTA, "Porta", tipo="Porta")
    A.gesto("levantar_a_porta", "g09", (0, 0),
            lambda: clona_casas(*CEL_PORTA, "Porta", CASAS_DA_PORTA), espera=2.0)
    A.cap("p14_porta")
    return True


@etapa
def condicao():
    """O DEGRAU DA AULA: o numero passa a DECIDIR.

       `Number.out -> Filter.in`, e o `pass` do filtro manda o recado. A
       condicao nasce em `input > 0` e vira `input > 2` — que e o mesmo que
       "tres ou mais", e o proprio bloco passa a mostrar isso embaixo do dado.
    """
    abre_mesa(*CEL_ALVO)
    nu = blocos.acha_bloco("Number", regiao=FILA_A)
    blocos.abre_categoria("Logic & Math")
    fi = AC._na_fila(blocos.bloco_ou_solta("Filter", 1000, Y_B, regiao=FILA_B),
                     FILA_B, "Filter do alvo")
    blocos.abre_ajustes(fi); time.sleep(1.5)
    a, _ = nav.captura("/tmp/_c7_fi.png")
    q = nav.acha_texto("greater than", arquivo=a)
    if not q:
        raise RuntimeError("nao achei o seletor `greater than` no painel do Filter")
    # O `+` E ACHADO POR LEITURA, nao por deslocamento decorado.
    #
    # Eu tinha estimado (+152, +82) a partir do rotulo, e `acha_texto` devolve
    # o CENTRO da frase, nao a ponta: os dois cliques caiam fora do botao. A
    # condicao ficou em `input > 0` — a porta abria na PRIMEIRA caixa — e a
    # leitura de volta nao pegou porque ela casava `input > 2` com a palavra
    # `input`. Dois erros que se escondiam um atras do outro.
    mais = None
    for t, tx, ty, tw, th in rs.ocr_forte(a, psm="6"):
        if t.strip() == "+" and q[1] + 30 < ty < q[1] + 140 and tx > q[0] - 200:
            if mais is None or tx < mais[0]:
                mais = (tx + tw // 2, ty + th // 2)
    if not mais:
        raise RuntimeError("nao achei o botao `+` do numero no painel do Filter")
    print(f"   botao + do filtro em {mais}", flush=True)

    def poe_a_condicao():
        # CLICA ATE BATER, e nao um numero fixo de vezes.
        #
        # O `+` so SOBE. Repetir a etapa com um numero fixo levava um filtro
        # que ja estava em 2 para 4, e a leitura de volta — essa agora de
        # verdade — reprovava. Quem decide quantos cliques faltam e o proprio
        # bloco.
        for _ in range(CONDICAO + 4):
            blocos.fecha_ajustes(); time.sleep(0.8)
            b, _ = nav.captura("/tmp/_c7_fi2.png")
            if rs.tem_texto(f"input > {CONDICAO}", arquivo=b):
                return mais
            blocos.abre_ajustes(fi); time.sleep(1.2)
            nav.clique_seguro(*mais); time.sleep(0.7)
        return mais

    A.gesto("condicao_do_filtro", "g11", (0, 0), poe_a_condicao, espera=1.4)
    blocos.fecha_ajustes(); time.sleep(1.0)
    b, _ = nav.captura("/tmp/_c7_fi2.png")
    if not rs.tem_texto(f"input > {CONDICAO}", arquivo=b):
        raise RuntimeError(f"ajustei a condicao e o bloco nao mostra "
                           f"`input > {CONDICAO}`")
    print(f"   condicao = input > {CONDICAO}", flush=True)
    blocos.abre_categoria("Components")
    ms = AC._na_fila(blocos.bloco_ou_solta("Message", 1900, Y_B, regiao=FILA_B),
                     FILA_B, "Message do alvo")
    blocos.liga_fixo(nu, "out", fi, "in")
    blocos.liga_fixo(fi, "pass", ms, "send")
    blocos.abre_ajustes(ms); time.sleep(1.5)
    blocos.escolhe_na_lista("send to", "choose objects", dy=55)
    time.sleep(1.0)
    blocos.escolhe_na_lista("select type", "porta")
    blocos.fecha_ajustes(); time.sleep(1.0)
    A.cap("p15_condicao")
    time.sleep(2)
    fecha_mesa()
    return True


@etapa
def porta_escuta():
    abre_mesa(*CEL_PORTA)
    blocos.abre_categoria("Triggers")
    mb = AC._na_fila(blocos.bloco_ou_solta("Mailbox", 1000, Y_A, regiao=FILA_A),
                     FILA_A, "Mailbox da porta")
    blocos.abre_categoria("Components")
    de = AC._na_fila(blocos.bloco_ou_solta("Destroyer", 1900, Y_A, regiao=FILA_A),
                     FILA_A, "Destroyer da porta")
    blocos.liga_fixo(mb, "out", de, "in")
    print("   porta: Mailbox -> Destroyer", flush=True)
    A.cap("p16_porta_escuta")
    time.sleep(2)
    fecha_mesa()
    return True


@etapa
def prova():
    """O fim: tres caixas entregues e a porta abre SOZINHA."""
    import numpy as np
    from PIL import Image
    editor.volta_ao_editor(); time.sleep(2)
    editor.volta_ao_nivel()
    p = nav.acha_texto("play")
    clique(*p); time.sleep(7); nav.espera_parar(limite=20)
    editor.exige_jogo()
    clique(1470, 620); time.sleep(1.5)

    def nao_ceu_em_cima():
        """O que NAO e ceu na metade de cima: com a porta de pe ha um bloco
           alto ali; sem ela, e so ceu. O chao e o boneco ficam abaixo."""
        a, _ = nav.captura("/tmp/_c7_p.png")
        im = np.asarray(Image.open(a).convert("RGB"), dtype=int)
        y0, y1, x0, x1 = _area_do_jogo(im)
        rgb = tuple(int(CEU[i:i + 2], 16) for i in (0, 2, 4))
        ceu = comum.mascara_cor(im, rgb, 16)
        corte = y0 + int((y1 - y0) * 0.75)
        return int((~ceu[y0:corte, x0:x1]).sum())

    porta_antes = nao_ceu_em_cima()
    A.cap("p17_tres_caixas")
    # TRINTA EMPURROES, nao dezoito: sao TRES caixas para levar de uma ponta a
    # outra, e com dezoito o placar parava em 2 — o jogo estava certo, faltava
    # fôlego na prova.
    serie, porta_depois = [], porta_antes
    for _ in range(34):
        rs.segura_tecla(rs.DIR, 0.6)
        time.sleep(0.4)
        n = _placar()
        if n is not None:
            serie.append(n)
        porta_depois = nao_ceu_em_cima()
        if porta_depois <= porta_antes * 0.25:
            # A PORTA CAIU: le o placar mais uma vez antes de sair.
            #
            # Entre a terceira entrega e a queda da porta passam fracoes de
            # segundo, e eu amostro a cada ~1 s: o laco saia com o ultimo
            # numero LIDO, que era 2, e a prova reprovava um jogo em que o
            # filtro tinha acabado de funcionar. Quem prova a condicao e a
            # PORTA; o placar e a testemunha.
            n = _placar()
            if n is not None:
                serie.append(n)
            break
        if n is not None and n < QUANTAS_CAIXAS:
            A.cap("p18_jogo")
    print(f"   placar durante a partida: {serie}", flush=True)
    print(f"   nao-ceu em cima: antes {porta_antes}, depois {porta_depois}",
          flush=True)
    if porta_antes < 1500:
        raise RuntimeError(f"a metade de cima ja estava quase so ceu ANTES "
                           f"({porta_antes} px) — a porta nasceu de pe mesmo?")
    if not serie or max(serie) < 2:
        raise RuntimeError(f"o placar mal subiu durante a partida ({serie}) — "
                           "as caixas estao chegando ao alvo?")
    if porta_depois > porta_antes * 0.25:
        raise RuntimeError(f"o placar chegou a {max(serie)} e a porta continua "
                           f"de pe ({porta_antes} -> {porta_depois} px) — a "
                           "condicao do filtro deixou passar?")
    if max(serie) < QUANTAS_CAIXAS:
        print(f"   (!) a porta caiu com o placar lido em {max(serie)}: a "
              f"{QUANTAS_CAIXAS}a entrega e a queda aconteceram entre duas "
              "amostras", flush=True)
    print(f"   PROVADO: o placar sobe ate {max(serie)} e a porta cai sozinha "
          f"({porta_antes} -> {porta_depois} px de nao-ceu)", flush=True)
    return True


def main():
    AC.main(sys.modules[__name__])


if __name__ == "__main__":
    main()
