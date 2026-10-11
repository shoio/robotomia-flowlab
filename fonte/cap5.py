#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aula 5 — Um botao so. Constroi o jogo no Flowlab e fotografa cada gesto.

   O jogo: um passarinho que so sabe fazer uma coisa — subir quando voce
   aperta espaco. A gravidade faz o resto. Bolas de fogo vem da direita, cada
   uma numa altura sorteada, e um PLACAR na tela conta quanto tempo voce
   aguenta.

   TUDO O QUE E NOVO FOI MEDIDO ANTES (PADRAO.md §2s), no prototipo 3155537:

   - o placar e `Number.+` -> `Label.text`. Cada pulso no `+` SOMA 1 (nao soma
     o proprio valor), e o `out` do Number atualiza o Label sozinho;
   - ⛔ `Impulse` NAO move este corpo e `Velocity` move: mesma mesa, mesmo fio
     no `y`, `906,906,906,906` contra `906 -> 692 -> 597 -> 576`. O pulo e o
     MESMO TRIO da Aula 3, entao nao ha peca nova nele;
   - passaro com gravidade e SEM CHAO sai da fase antes de a crianca reagir —
     por isso o chao vem ANTES do primeiro Play;
   - a altura sorteada e `Once -> Random -> Position.+y`. O `+y` e
     DESLOCAMENTO, e por isso nao exige saber coordenada nenhuma da fase.
     Medido: 687 px de espalhamento, variando a cada amostra;
   - o `Random` nasce em `0-10`, que desloca dez pixels e nao da para ver.

       BANCADA=1 python3 fonte/roda_aula.py 5
"""
import os, shutil, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rs, nav, editor, blocos, comum

comum.pasta("aula5")
import aula_comum as AC
from aula_comum import (celula, clique, A, etapa, ETAPAS, cria_objeto, clona,
                        da_fisica, confere_fisica, abre_mesa, fecha_mesa,
                        rastreio, cor)
from comum import fecha_painel_objeto
ETAPAS.clear()

D = "aula5"
CEU = "7EC8E3"          # azul de dia: o fogo vermelho aparece de longe nele
AC.SPRITES = {
    "Passaro":  ("Flowlab Sprites", "Characters", 0, 0),   # o menino das aulas 1 a 3
    "Chao":     ("Flowlab Sprites", "Blocks", 0, 0),       # o bloco de grama
    "Fogo":     ("Flowlab Sprites", "Terrain", 6, 0),      # a lava com bolhas
    "Soltador": ("Flowlab Sprites", "Objects", 9, 1),      # a estrela dourada
}

CEL_PASSARO = (3, 5)
LINHA_CHAO = 11
CEL_FOGO = (14, 2)
CEL_SOLTADOR = (15, 1)

PULO = 25               # medido: -25 no Velocity.y levanta 330 px
VEL_FOGO = 4            # medido: -4 atravessa a tela num tempo jogavel
ESPALHA = 600           # medido: 687 px de espalhamento de altura
VIDA_DO_FOGO = 300      # trinta avos de segundo => 10 s, atravessa a tela toda

# Cada mesa com mais de um comportamento usa FILEIRAS com recorte proprio: dois
# blocos de mesmo nome na mesma mesa fazem `acha_bloco` devolver sempre o
# PRIMEIRO (§2p do PADRAO.md).
FILA_A = (0.12, 0.06, 1.0, 0.43)
FILA_B = (0.12, 0.43, 1.0, 0.70)
FILA_C = (0.12, 0.70, 1.0, 0.96)
Y_A, Y_B, Y_C = 520, 960, 1400


@etapa
def novo():
    A.url = editor.jogo_novo()
    print("   jogo:", A.url, flush=True)
    A.guarda_url()
    comum.calibra_grade(16, 12)
    A.cap("p01_vazio")
    # OS TRES CLIPES DE ABERTURA acontecem no SITE, antes de existir jogo
    # nenhum, e o gesto e identico em toda aula.
    for nome in ("abrir_my_games.gif", "novo_jogo.gif", "empty_project.gif"):
        os.makedirs(f"{D}/gifs", exist_ok=True)
        if not os.path.exists(f"{D}/gifs/{nome}"):
            shutil.copy(f"aula4/gifs/{nome}", f"{D}/gifs/{nome}")
    A.gesto("abrir_niveis", "g08a", (0, 0), lambda: editor.abre_niveis(), espera=1.8)
    A.gesto("pintar_o_ceu", "g08", (0, 0),
            lambda: editor.cor_do_ceu(CEU, abrir=False), espera=2.0)
    editor.volta_ao_nivel()
    A.cap("p02_ceu")
    return True


@etapa
def passaro():
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    x, y = celula(*CEL_PASSARO)
    A.gesto("criar_objeto", "g01", (x, y), lambda: clique(x, y), espera=1.5)
    a, _ = nav.captura("/tmp/_c5_rad.png")
    p = nav.acha_texto("create", arquivo=a)
    A.gesto("escolher_create", "g02", p, lambda: clique(*p), espera=3)
    editor.espera_tela("behaviors", limite=20)
    comum.nomeia("Passaro"); comum.nomeia_tipo("Passaro")
    A.cap("p03_nome")
    comum.abre_sprite()
    pacote, sub, lin, col = AC.SPRITES["Passaro"]
    comum.abre_grade_sprite(pacote, sub)
    A.gesto("escolher_sprite", "g13", (0, 0),
            lambda: AC.poe_sprite("Passaro", so_clique=True), espera=2.0)
    clique(*comum.SPRITE_OK); time.sleep(2); nav.espera_parar(limite=15)
    A.cap("p04_passaro")
    # AQUI A GRAVIDADE FICA LIGADA, ao contrario da Aula 4. Ela e metade do
    # jogo: o passaro cai sozinho, e o espaco e a unica coisa que o segura.
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
def chao():
    """O CHAO VEM ANTES DO PRIMEIRO PLAY, e nao e enfeite.

       Medido: com gravidade e sem chao, cinco segundos depois do Play a tela
       ja estava vazia — dez amostras seguidas sem achar o passaro. A crianca
       aperta Play e o bicho ja foi, sem ela ter visto nada."""
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    cria_objeto(0, LINHA_CHAO, "Chao", tipo="Chao")
    A.gesto("clonar_o_chao", "g05", (0, 0),
            lambda: clona(0, LINHA_CHAO, "Chao", range(1, 16)), espera=2.0)
    A.cap("p06_chao")
    return True


@etapa
def pulo():
    """O MESMO TRIO DA AULA 3, pela terceira vez: `Number` -> `Velocity`.

       Aqui quem manda e o `Keyboard` e o lado e o `y`. E o bloco final e o
       `Velocity`, NAO o `Impulse`: medido na bancada, o `Impulse` nao move
       este corpo (906, 906, 906, 906) e o `Velocity` move (906 -> 576)."""
    abre_mesa(*CEL_PASSARO)
    blocos.abre_categoria("Triggers")
    k = AC._na_fila(blocos.bloco_ou_solta("Keyboard", 900, Y_A, regiao=FILA_A),
                    FILA_A, "Keyboard do pulo")
    AC.poe_tecla(k, 49, "spacebar", clipe="muda_a_tecla", gid="g09")
    blocos.abre_categoria("Logic & Math")
    nu = AC._na_fila(blocos.bloco_ou_solta("Number", 1700, Y_A, regiao=FILA_A),
                     FILA_A, "Number do pulo")
    ponto = blocos.prepara_menos(nu, 0)
    blocos.clica_menos(ponto, PULO)
    blocos.fecha_ajustes(); time.sleep(0.8)
    lido = blocos.le_valor(nu)
    if lido != str(-PULO):
        raise RuntimeError(f"o Number do pulo mostra {lido!r} e eu esperava "
                           f"{-PULO!r}")
    blocos.abre_categoria("Properties")
    ve = AC._na_fila(blocos.bloco_ou_solta("Velocity", 2500, Y_A, regiao=FILA_A),
                     FILA_A, "Velocity do pulo")
    blocos.liga_fixo(k, "down", nu, "get")
    # NO `y`, que e para cima e para baixo. O `x` e o dos lados, da Aula 4.
    blocos.liga_fixo(nu, "out", ve, "y")
    print(f"   pulo: Keyboard -> Number({lido}) -> Velocity.y", flush=True)
    A.cap("p07_pulo")
    time.sleep(2)
    fecha_mesa()
    return True


@etapa
def prova_pulo():
    """A promessa do passo 12: o espaco LEVANTA o passaro, e ele volta."""
    import numpy as np
    from PIL import Image
    cor_passaro, tol = rastreio("Passaro", "Chao")
    print(f"   rastreando o passaro por {cor_passaro} (tol {tol})", flush=True)
    editor.volta_ao_editor(); time.sleep(2)
    editor.volta_ao_nivel()
    p = nav.acha_texto("play")
    if not p:
        raise RuntimeError("nao achei o botao Play")
    A.gesto("jogar", "g10", p, lambda: clique(*p), espera=6)
    editor.exige_jogo()
    clique(1470, 620); time.sleep(1.5)

    def altura():
        a, _ = nav.captura("/tmp/_c5_h.png")
        im = np.asarray(Image.open(a).convert("RGB"), dtype=int)
        m = comum.mascara_cor(im, cor_passaro, tol)
        ys, _xs = np.nonzero(m)
        return int(ys.mean()) if len(ys) else None

    parado = altura()
    rs.segura_tecla(49, 0.10)
    subida = [altura() for _ in range(3)]
    A.cap("p08_voando")
    time.sleep(1.6)
    voltou = altura()
    print(f"   y parado {parado}, subindo {subida}, 1,6 s depois {voltou}",
          flush=True)
    if parado is None or None in subida or voltou is None:
        raise RuntimeError("perdi o passaro de vista — ele saiu da fase?")
    if min(subida) > parado - 80:
        raise RuntimeError(f"apertei espaco e o passaro nao subiu "
                           f"({parado} -> {min(subida)})")
    if voltou < parado - 60:
        raise RuntimeError(f"o passaro subiu e NAO VOLTOU ({voltou}) — a "
                           "gravidade dele esta desligada?")
    print(f"   PROVADO: o espaco levanta {parado - min(subida)} px e a "
          "gravidade traz de volta", flush=True)
    editor.volta_ao_editor(); time.sleep(2)
    return True


@etapa
def fogo():
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    cria_objeto(*CEL_FOGO, "Fogo", tipo="Fogo")
    x, y = celula(*CEL_FOGO)
    editor.objeto_ou_abre(x, y)
    # SEM GRAVIDADE: o fogo atravessa a tela em linha reta. Com ela ele cai
    # numa parabola e a altura sorteada perde o sentido.
    da_fisica(movable=True, gravidade=False, atrito=False)
    A.cap("p09_fogo")
    fecha_painel_objeto(); time.sleep(1.5)
    editor.objeto_ou_abre(x, y)
    confere_fisica(movable=True, gravidade=False)
    fecha_painel_objeto(); time.sleep(1.5)
    return True


@etapa
def fogo_anda():
    abre_mesa(*CEL_FOGO)
    blocos.abre_categoria("Triggers")
    al = AC._na_fila(blocos.bloco_ou_solta("Always", 900, Y_A, regiao=FILA_A),
                     FILA_A, "Always do fogo")
    blocos.abre_categoria("Logic & Math")
    nu = AC._na_fila(blocos.bloco_ou_solta("Number", 1700, Y_A, regiao=FILA_A),
                     FILA_A, "Number do fogo")
    ponto = blocos.prepara_menos(nu, 0)
    blocos.clica_menos(ponto, VEL_FOGO)
    blocos.fecha_ajustes(); time.sleep(0.8)
    lido = blocos.le_valor(nu)
    if lido != str(-VEL_FOGO):
        raise RuntimeError(f"o Number do fogo mostra {lido!r}")
    blocos.abre_categoria("Properties")
    ve = AC._na_fila(blocos.bloco_ou_solta("Velocity", 2500, Y_A, regiao=FILA_A),
                     FILA_A, "Velocity do fogo")
    blocos.liga_fixo(al, "out", nu, "get")
    blocos.liga_fixo(nu, "out", ve, "x")
    print(f"   fogo anda: Always -> Number({lido}) -> Velocity.x", flush=True)
    A.cap("p10_fogo_anda")
    time.sleep(2)
    return True


@etapa
def fogo_sorteia():
    """Cada fogo numa altura, com `Position.+y` (DESLOCAMENTO, nao endereco).

       Usar o `+y` e o que livra a aula de saber coordenada nenhuma da fase: a
       copia nasce no soltador e desce um tanto sorteado a partir dali."""
    blocos.abre_categoria("Triggers")
    on = AC._na_fila(blocos.bloco_ou_solta("Once", 900, Y_B, regiao=FILA_B),
                     FILA_B, "Once do sorteio")
    blocos.abre_categoria("Logic & Math")
    rd = AC._na_fila(blocos.bloco_ou_solta("Random", 1700, Y_B, regiao=FILA_B),
                     FILA_B, "Random do sorteio")
    # O `Random` NASCE EM 0-10, que desloca dez pixels e nao da para ver.
    blocos.abre_ajustes(rd); time.sleep(1.4)
    A.gesto("faixa_do_sorteio", "g06", (0, 0),
            lambda: blocos.campo_abaixo("max value", ESPALHA), espera=1.4)
    blocos.fecha_ajustes(); time.sleep(1.0)
    b, _ = nav.captura("/tmp/_c5_rnd.png")
    if not rs.tem_texto(f"0-{ESPALHA}", arquivo=b):
        raise RuntimeError(f"ajustei a faixa e o bloco nao mostra `0-{ESPALHA}`")
    print(f"   faixa do sorteio = 0-{ESPALHA}", flush=True)
    blocos.abre_categoria("Properties")
    po = AC._na_fila(blocos.bloco_ou_solta("Position", 2500, Y_B, regiao=FILA_B),
                     FILA_B, "Position do sorteio")
    blocos.liga_fixo(on, "out", rd, "new")
    blocos.liga_fixo(rd, "out", po, "maisy")
    A.cap("p11_sorteio")
    time.sleep(2)
    fecha_mesa()
    return True


@etapa
def soltador():
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    cria_objeto(*CEL_SOLTADOR, "Soltador", tipo="Soltador")
    A.cap("p12_soltador")
    abre_mesa(*CEL_SOLTADOR)
    blocos.abre_categoria("Components")
    # NA PALHETA ele e `Emit`; NA MESA o titulo e `Emitter`.
    em = blocos.bloco_ou_solta("Emit", 1900, Y_A, titulo="Emitter", regiao=FILA_A)
    blocos.abre_ajustes(em); time.sleep(1.5)
    A.gesto("ajustes_do_fogo", "g07", (0, 0),
            lambda: blocos.escolhe_na_lista("object to emit", "Fogo"), espera=1.6)
    blocos.campo_ao_lado("expire after", VIDA_DO_FOGO)
    blocos.fecha_ajustes(); time.sleep(1.0)
    blocos.abre_categoria("Triggers")
    tm = AC._na_fila(blocos.bloco_ou_solta("Timer", 900, Y_A, regiao=FILA_A),
                     FILA_A, "Timer do soltador")
    blocos.abre_ajustes(tm); time.sleep(1.3)
    blocos.marca_do_bloco("repeat forever", True)
    blocos.fecha_ajustes(); time.sleep(1.0)
    em = blocos.acha_bloco("Emitter", regiao=FILA_A)
    blocos.liga_fixo(tm, "out", em, "emit")
    A.cap("p13_timer")
    time.sleep(2)
    fecha_mesa()
    return True


@etapa
def prova_fogo():
    """A promessa do passo 18: os fogos vem sozinhos, CADA UM NUMA ALTURA.

       A media nao serve e o par de extremos de UMA foto tambem nao: o que
       prova sorteio e a altura MUDAR de amostra para amostra."""
    import numpy as np
    from PIL import Image
    cor_fogo, tol = rastreio("Fogo", "Passaro", "Chao")
    print(f"   rastreando o fogo por {cor_fogo} (tol {tol})", flush=True)
    editor.volta_ao_editor(); time.sleep(2)
    editor.volta_ao_nivel()
    p = nav.acha_texto("play")
    clique(*p); time.sleep(7); nav.espera_parar(limite=20)
    editor.exige_jogo()
    clique(1470, 620); time.sleep(1.5)
    # O ESPALHAMENTO E DENTRO DE UM QUADRO SO.
    #
    # Medir o fogo mais BAIXO da tela nao serve, e eu tentei: com varios fogos
    # no ar ao mesmo tempo, o mais baixo fica quase sempre no pe da faixa
    # sorteada e o numero satura. Li `823..955` — 132 px — numa tela que a
    # foto mostrava com fogo no alto, no meio e embaixo. E a mesma armadilha
    # da Aula 4: fluxo constante nao se mede por extremo nem por media.
    #
    # Num quadro, se as alturas sao sorteadas, o fogo de cima e o de baixo
    # estao LONGE um do outro. Se viessem todos na mesma altura, a distancia
    # seria a altura de um desenho.
    espalha = []
    for i in range(14):
        a, _ = nav.captura("/tmp/_c5_f.png")
        im = np.asarray(Image.open(a).convert("RGB"), dtype=int)
        m = comum.mascara_cor(im, cor_fogo, tol)
        ys, _xs = np.nonzero(m)
        if len(ys):
            espalha.append(int(ys.max() - ys.min()))
        if i == 9:
            A.cap("p14_fogos")
        time.sleep(0.45)
    print(f"   distancia entre o fogo mais alto e o mais baixo, por quadro: "
          f"{espalha}", flush=True)
    if len(espalha) < 6:
        raise RuntimeError(f"so vi fogo em {len(espalha)} de 14 amostras — o "
                           "soltador esta soltando?")
    if max(espalha) < 250:
        raise RuntimeError(f"num mesmo quadro os fogos nunca ficaram longe uns "
                           f"dos outros (maximo {max(espalha)} px) — a faixa do "
                           "Random ficou pequena ou o fio do `+y` nao pegou")
    print(f"   PROVADO: num mesmo quadro ha fogo separado por "
          f"{max(espalha)} px de altura", flush=True)
    editor.volta_ao_editor(); time.sleep(2)
    return True


@etapa
def fim_de_jogo():
    abre_mesa(*CEL_PASSARO)
    blocos.abre_categoria("Triggers")
    c = AC._na_fila(blocos.bloco_ou_solta("Collision", 1000, Y_B, regiao=FILA_B),
                    FILA_B, "Collision do fim")
    blocos.abre_categoria("Game Flow")
    r = AC._na_fila(blocos.bloco_ou_solta("Restart Game", 1900, Y_B,
                                          titulo="RestartGame", regiao=FILA_B),
                    FILA_B, "RestartGame")
    blocos.liga_fixo(c, "hit", r, "go")
    # COM QUEM a batida conta: em `Any Type` o passaro reinicia ao encostar no
    # CHAO, e o jogo recomeca sozinho antes de a crianca apertar nada.
    blocos.escolhe_tipo_da_colisao(c, "Fogo")
    A.cap("p15_fim")
    time.sleep(2)
    return True


@etapa
def placar():
    """O DEGRAU DA AULA: `Timer` -> `Number.+` -> `Label.text`.

       Medido: cada pulso no `+` SOMA 1 (nao soma o proprio valor — seriam
       1,2,4,8), e o `out` do Number atualiza o Label sozinho, sem disparar o
       `get`. O Number comeca em 0."""
    blocos.abre_categoria("Triggers")
    tm = AC._na_fila(blocos.bloco_ou_solta("Timer", 900, Y_C, regiao=FILA_C),
                     FILA_C, "Timer do placar")
    blocos.abre_ajustes(tm); time.sleep(1.3)
    blocos.marca_do_bloco("repeat forever", True)
    blocos.fecha_ajustes(); time.sleep(1.0)
    blocos.abre_categoria("Logic & Math")
    nu = AC._na_fila(blocos.bloco_ou_solta("Number", 1700, Y_C, regiao=FILA_C),
                     FILA_C, "Number do placar")
    blocos.abre_categoria("GUI")
    # ⚠️ O `Label` ESCREVE O PROPRIO TEXTO DENTRO DA FASE, e `acha_bloco`
    # casaria com ela. O recorte da fileira e o que separa um do outro.
    lb = AC._na_fila(blocos.bloco_ou_solta("Label", 2500, Y_C, regiao=FILA_C),
                     FILA_C, "Label do placar")
    blocos.liga_fixo(tm, "out", nu, "mais")
    blocos.liga_fixo(nu, "out", lb, "text")
    print("   placar: Timer -> Number.+ -> Label.text", flush=True)
    A.cap("p16_placar")
    time.sleep(2)
    fecha_mesa()
    return True


@etapa
def prova():
    """A promessa do fim: o placar SOBE sozinho enquanto o jogo roda."""
    editor.volta_ao_editor(); time.sleep(2)
    editor.volta_ao_nivel()
    p = nav.acha_texto("play")
    clique(*p); time.sleep(7); nav.espera_parar(limite=20)
    editor.exige_jogo()
    clique(1470, 620); time.sleep(1.0)

    def numero_na_tela():
        """O que o Label mostra, lido da tela."""
        a, _ = nav.captura("/tmp/_c5_pl.png")
        achados = rs.ocr_forte(a, regiao=(0.33, 0.08, 0.55, 0.22), psm="7")
        for t, *_ in achados:
            t = "".join(ch for ch in t if ch.isdigit())
            if t:
                return int(t)
        return None

    # O passaro bate asa para nao bater no chao enquanto o placar sobe.
    serie = []
    for i in range(8):
        rs.segura_tecla(49, 0.08)
        n = numero_na_tela()
        if n is not None:
            serie.append(n)
        time.sleep(0.5)
    A.cap("p17_jogo")
    print(f"   placar lido na tela: {serie}", flush=True)
    if len(serie) < 3:
        raise RuntimeError(f"nao consegui ler o placar na tela ({serie}) — o "
                           "`Label` esta mostrando alguma coisa?")
    if max(serie) <= min(serie):
        raise RuntimeError(f"o placar nao subiu: {serie}")
    print(f"   PROVADO: o placar vai de {min(serie)} a {max(serie)} sozinho",
          flush=True)
    return True


def main():
    AC.main(sys.modules[__name__])


if __name__ == "__main__":
    main()
