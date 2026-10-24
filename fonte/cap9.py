#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aula 9 — Inimigo que persegue. Constroi o jogo no Flowlab e fotografa cada gesto.

   O jogo: um corredor numa fase plana, e um morcego que VOA ATRAS DELE. Cada
   encontrao tira um ponto de uma BARRA DE VIDA; sem vida, o jogo recomeca.

   O que e NOVO:
     - a IA mais simples que existe: `Proximity` olha onde o jogador esta,
       `PointAt` vira o morcego para la, `Velocity.forward` o faz andar;
     - a `Bar`, que mostra um numero como barra;
     - o `+` com valor NEGATIVO: `Number(-1)` ligado no `+` de uma variavel
       SUBTRAI um.

   MEDIDO ANTES (PADRAO.md §2ah), nos prototipos 3166005:
     - `Proximity` tem `dist` e `check` na entrada e `x`, `y`, `miss` na saida; o
       painel traz `Select Type`, `Distance` (de fabrica 32 px — pequeno
       demais) e a escolha do que devolver. `PointAt` tem `x`, `y` e a saida
       `rot`; a caixinha `Rotate sprite` nasce marcada;
     - `Expression` existe mas NAO entra na aula: a documentacao diz que o `+`
       de `Number`/variavel SOMA O VALOR QUE CHEGA, entao `Number(-1)` ligado
       nele ja subtrai — um bloco a menos, e sem o risco de a conta ler um
       valor velho;
     - a `Bar` mostra `value / max` e nasce com 5 de 10;
     - `Collision` dispara uma vez por batida: encostar e ficar nao drena.

       BANCADA=1 python3 fonte/roda_aula.py 9
"""
import os, shutil, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rs, nav, editor, blocos, comum

comum.pasta("aula9")
import aula_comum as AC
from aula_comum import (celula, clique, A, etapa, ETAPAS, cria_objeto, clona,
                        clona_casas, da_fisica, confere_fisica, abre_mesa,
                        fecha_mesa, rastreio, cor)
from comum import fecha_painel_objeto
ETAPAS.clear()

D = "aula9"
CEU = "A8DADC"
AC.SPRITES = {
    "Jogador": ("Flowlab Sprites", "Characters", 0, 0),
    "Chao":    ("Flowlab Sprites", "Blocks", 0, 0),
    "Inimigo": ("Flowlab Sprites", "Characters", 4, 0),     # o morcego
}

LINHA_CHAO = 10
CEL_JOGADOR = (1, 9)
CEL_INIMIGO = (13, 3)
VEL_INIMIGO = 2                   # medido: 3 chegou no jogador antes da 1a leitura
VIDA = 3
VERMELHO = "E63946"
PERTO = 40                        # px: o jogador SENTE o morcego a menos disso

# `Y_B` e `Y_C` ficam DENTRO da tela (1604 px): na Aula 8 um bloco soltou em
# y=1620 e a mesa nao mudou ali.
Y_A, Y_B, Y_C = 400, 900, 1380


def _area_do_jogo(im):
    """A caixa (y0, y1, x0, x1) da fase na pagina do jogo, pela COR DO CEU."""
    import numpy as _np
    rgb = tuple(int(CEU[i:i + 2], 16) for i in (0, 2, 4))
    ys, xs = _np.nonzero(comum.mascara_cor(im, rgb, 16))
    if len(ys) < 20000:
        raise RuntimeError(f"nao achei o ceu da fase na tela ({len(ys)} px)")
    return int(ys.min()), int(ys.max()), int(xs.min()), int(xs.max())


def _acha(quem, outros, im, area=None):
    """(x, y) medio de `quem` na tela do jogo, ou None. Por COR, na fase."""
    import numpy as _np
    cor_q, tol = rastreio(quem, *outros)
    y0, y1, x0, x1 = area or _area_do_jogo(im)
    m = comum.mascara_cor(im, cor_q, tol)[y0:y1 + 1, x0:x1 + 1]
    ys, xs = _np.nonzero(m)
    if len(xs) < 25:
        return None
    return int(xs.mean()) + x0, int(ys.mean()) + y0


def _barra(im, area=None):
    """Quantos pixels VERMELHOS ha na barra de vida, no canto de cima da fase.

       Devolve None quando nao ha ceu na tela — e o instante em que o
       `Restart Game` recarrega a fase (medido: `nao achei o ceu da fase (0
       px)` derrubava a prova justo no recomeco que ela queria ver)."""
    import numpy as _np
    try:
        y0, y1, x0, x1 = area or _area_do_jogo(im)
    except RuntimeError:
        return None
    rgb = tuple(int(VERMELHO[i:i + 2], 16) for i in (0, 2, 4))
    faixa = comum.mascara_cor(im, rgb, 40)[y0:y0 + 140, x0:x0 + 520]
    return int(faixa.sum())


def _foto(nome):
    from PIL import Image
    import numpy as _np
    a, _ = nav.captura(f"/tmp/_c9_{nome}.png")
    return _np.asarray(Image.open(a).convert("RGB"), dtype=int)


def _grava_o_play():
    """Grava o clipe `jogar` DESTA aula: o antes (editor) e o depois (jogo).

       Nao usa `A.gesto`: ele espera a tela PARAR (ate 15 s) e, numa fase em
       que o morcego voa, ela nunca para — e e justamente essa espera que
       atrasava a primeira leitura das provas. Aqui sao 1,2 s entre os dois
       quadros, e depois o jogo volta ao editor: a prova comeca num Play novo."""
    editor.volta_ao_nivel(); time.sleep(1.5)
    p = nav.acha_texto("play")
    if not p:
        raise RuntimeError("nao achei o botao Play (estou mesmo no editor?)")
    antes = A.cap("g07_a")
    comum.CLIQUES.clear()
    clique(*p); time.sleep(1.2)
    depois = A.cap("g07_b")
    clicado = any(abs(p[0] - cx) <= 6 and abs(p[1] - cy) <= 6
                  for cx, cy in comum.CLIQUES)
    A.reg("jogar", antes=antes, depois=depois, alvo=[int(p[0]), int(p[1])],
          botao="esq", clicado=clicado)
    editor.volta_ao_editor(); time.sleep(2)


def _entra_no_jogo():
    """Aperta Play e DEVOLVE NA HORA — o relogio do morcego ja esta correndo.

       ⛔ MEDIDO: o que vinha depois do clique (`exige_jogo`, que le a tela
       varias vezes, e o clique de foco) custava ate 38 s, e o morcego, que
       leva 8,5 s para cruzar a fase, ja estava em cima do jogador na PRIMEIRA
       leitura. Quem chama le o que tem de ler logo, e so depois confere com
       `editor.exige_jogo()` que estava mesmo no jogo."""
    _gifs_comuns()
    editor.volta_ao_nivel(); time.sleep(1.5)
    p = nav.acha_texto("play")
    if not p:
        raise RuntimeError("nao achei o botao Play (estou mesmo no editor?)")
    clique(*p)


def _gifs_comuns():
    """Os clipes que sao IGUAIS em toda aula (abrir a lista, novo jogo e projeto
       vazio) vem da aula anterior.

       O `jogar` NAO: o clipe mostraria o ceu e o chao da aula de onde foi
       copiado — a primeira copia, da Aula 8, aparecia areia com bandeira
       numa pagina cujo jogo e azul com morcego. Ele se grava em
       `_grava_o_play`, sem esperar a tela parar."""
    os.makedirs(f"{D}/gifs", exist_ok=True)
    for nome in ("abrir_my_games.gif", "novo_jogo.gif", "empty_project.gif"):
        if not os.path.exists(f"{D}/gifs/{nome}"):
            shutil.copy(f"aula8/gifs/{nome}", f"{D}/gifs/{nome}")


@etapa
def novo():
    A.url = editor.jogo_novo()
    print("   jogo:", A.url, flush=True)
    A.guarda_url()
    comum.calibra_grade(16, 12)
    A.cap("p01_vazio")
    _gifs_comuns()
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
    a, _ = nav.captura("/tmp/_c9_rad.png")
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
    """O mesmo pacote das Aulas 2, 6, 7 e 8: `Run & Jump`, um bloco so."""
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
def inimigo():
    """O morcego: movel e SEM gravidade — ele voa. Com gravidade ele cairia
       no chao assim que o jogo comecasse, e nao haveria perseguicao."""
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    cria_objeto(*CEL_INIMIGO, "Inimigo", tipo="Inimigo")
    x, y = celula(*CEL_INIMIGO)
    editor.objeto_ou_abre(x, y)
    # ⛔ MEDIDO na primeira captura: o morcego SOLIDO empurra o jogador. Parado
    # no chao, o jogador foi arrastado ate a beirada da fase, caiu fora dela e
    # SUMIU — e o morcego ficou pregado na borda. Vale o mesmo da lava da Aula
    # 3: sem `is solid` o morcego atravessa (nao empurra), e a caixinha que
    # nasce no lugar, `enable collisions`, devolve o toque sem o empurrao.
    da_fisica(movable=True, gravidade=False, solido=False, colisoes=True,
              densidade=None, atrito=False)
    A.cap("p08_inimigo")
    fecha_painel_objeto(); time.sleep(1.5)
    editor.objeto_ou_abre(x, y)
    confere_fisica(movable=True, gravidade=False, solido=False, colisoes=True)
    fecha_painel_objeto(); time.sleep(1.5)
    return True


@etapa
def olha():
    """OLHAR: `Timer` -> `Proximity.check`, e `x`/`y` -> `PointAt`.

       O `Proximity` so olha quando recebe o `check`, por isso o `Timer`. A
       distancia de fabrica (32 px) so acha quem esta ENCOSTADO: sobe-se para
       3000 e o morcego enxerga a fase inteira."""
    abre_mesa(*CEL_INIMIGO)
    blocos.abre_categoria("Triggers")
    blocos.bloco_ou_solta("Timer", 800, Y_A)
    t = blocos.acha_bloco("Timer")
    blocos.abre_ajustes(t); time.sleep(1.3)
    blocos.marca_do_bloco("repeat forever", True)
    blocos.campo_acima("repeat forever", 2)           # 2 decimos = olha 5x por s
    blocos.fecha_ajustes(); time.sleep(1.0)
    blocos.abre_categoria("Components")
    blocos.bloco_ou_solta("Proximity", 1700, Y_A)
    px = blocos.acha_bloco("Proximity")
    blocos.abre_ajustes(px); time.sleep(1.5)
    blocos.escolhe_na_lista("select type", "Jogador")
    blocos.campo_ao_lado("distance", 3000, folga=150)
    blocos.fecha_ajustes(); time.sleep(1.0)
    blocos.bloco_ou_solta("PointAt", 2500, Y_A)

    t = blocos.acha_bloco("Timer")
    px = blocos.acha_bloco("Proximity")
    blocos.liga_fixo(t, "out", px, "check")
    px = blocos.acha_bloco("Proximity")
    pa = blocos.acha_bloco("PointAt")
    blocos.liga_fixo(px, "x", pa, "x")
    px = blocos.acha_bloco("Proximity")
    pa = blocos.acha_bloco("PointAt")
    blocos.liga_fixo(px, "y", pa, "y")
    print("   olhar: Timer -> Proximity(Jogador) -> PointAt", flush=True)
    A.cap("p09_olha")
    time.sleep(2)
    fecha_mesa()
    return True


@etapa
def segue():
    """ANDAR: `Always` -> `Number(3)` -> `Velocity.forward`.

       O trio das Aulas 3 e 4, mas na entrada `forward` — a direcao para onde o
       `PointAt` esta virando o morcego."""
    abre_mesa(*CEL_INIMIGO)
    blocos.abre_categoria("Triggers")
    blocos.bloco_ou_solta("Always", 800, Y_B)
    blocos.abre_categoria("Logic & Math")
    blocos.bloco_ou_solta("Number", 1700, Y_B)
    nu = blocos.acha_bloco("Number")
    blocos.escreve_valor(nu, VEL_INIMIGO)
    blocos.abre_categoria("Properties")
    blocos.bloco_ou_solta("Velocity", 2500, Y_B)
    al = blocos.acha_bloco("Always")
    nu = blocos.acha_bloco("Number")
    blocos.liga_fixo(al, "out", nu, "get")
    nu = blocos.acha_bloco("Number")
    ve = blocos.acha_bloco("Velocity")
    blocos.liga_fixo(nu, "out", ve, "forward")
    print(f"   andar: Always -> Number({VEL_INIMIGO}) -> Velocity.forward", flush=True)
    A.cap("p10_segue")
    time.sleep(2)
    fecha_mesa()
    return True


@etapa
def persegue():
    """A promessa do passo 15: o morcego VAI ATE o jogador — e VIRA quando ele corre.

       Mede por COR a distancia entre os dois, e depois manda o jogador correr
       para o outro lado: se o morcego muda de rumo e vai atras, ele esta mesmo
       OLHANDO (e nao so voando em linha reta para onde o jogador estava)."""
    import math
    _grava_o_play()
    _entra_no_jogo()

    def pos():
        im = _foto("d")
        return (_acha("Inimigo", ("Chao",), im), _acha("Jogador", ("Chao",), im))

    def dist(i, j):
        return None if not i or not j else math.hypot(i[0] - j[0], i[1] - j[1])

    i0, j0 = pos()
    d0 = dist(i0, j0)
    serie, melhor, foto_tirada = [], d0, False
    ultimo_i, ultimo_j = i0, j0
    for _ in range(40):
        i, j = pos()
        ultimo_i, ultimo_j = i or ultimo_i, j or ultimo_j
        d = dist(i, j)
        serie.append(None if d is None else int(d))
        if d is not None and d0 and not foto_tirada and d < d0 * 0.6:
            A.cap("p11_persegue")
            foto_tirada = True
        if d is not None and (melhor is None or d < melhor):
            melhor = d
        if d is not None and d < 90:
            break
        time.sleep(0.4)
    if not foto_tirada:
        A.cap("p11_persegue")
    print(f"   distancia morcego-jogador: inicio {None if d0 is None else int(d0)}"
          f" -> {serie}", flush=True)
    if d0 is None:
        raise RuntimeError("nao achei o morcego e o jogador na tela do jogo")
    if d0 < 250:
        raise RuntimeError(f"o morcego ja estava a {int(d0)} px na primeira "
                           "leitura: a prova nao viu a viagem")
    if melhor > 120:
        raise RuntimeError(f"o morcego nao chegou perto: {int(d0)} px no inicio, "
                           f"{int(melhor)} no melhor momento ({serie})")
    # so AGORA confiro que estou na pagina do jogo (a leitura da tela custa
    # ~30 s, e antes disso o morcego ja teria chegado) e dou foco ao jogo
    editor.exige_jogo()
    clique(1470, 620)
    # FASE 2: o jogador corre para a DIREITA e o morcego tem de ir atras
    # o morcego SOME da leitura quando fica por cima do jogador (as cores se
    # misturam): vale o ultimo lugar onde ele foi visto
    i1, j1 = ultimo_i, ultimo_j
    for _ in range(2):
        rs.corre_e_pula(direcao=124, antes=0.05, segurando=0.55)
    # AMOSTRA durante 3 s, e nao uma leitura so: o morcego some da leitura
    # quando alcanca o jogador de novo, e o ultimo quadro sairia vazio.
    xs_morcego, xs_jogador = [], []
    for _ in range(8):
        i, j = pos()
        if i:
            xs_morcego.append(i[0])
        if j:
            xs_jogador.append(j[0])
        time.sleep(0.3)
    print(f"   o jogador correu para a direita: morcego x {i1 and i1[0]} -> "
          f"{xs_morcego}  (jogador {j1 and j1[0]} -> {xs_jogador[-1:] or None})",
          flush=True)
    if not (i1 and j1 and xs_morcego and xs_jogador):
        raise RuntimeError("perdi o morcego ou o jogador na fase 2 da prova")
    if max(xs_jogador) < j1[0] + 150:
        raise RuntimeError("o jogador nao correu para a direita")
    if max(xs_morcego) < i1[0] + 100:
        raise RuntimeError(f"o jogador foi para a direita e o morcego nao o "
                           f"seguiu (x {i1[0]} -> {max(xs_morcego)})")
    print(f"   PROVADO: o morcego chegou a {int(melhor)} px do jogador e, quando "
          f"ele correu, VIROU e foi atras (x {i1[0]} -> {max(xs_morcego)})",
          flush=True)
    editor.volta_ao_editor(); time.sleep(2)
    return True


@etapa
def vida():
    """A VIDA: uma variavel DO OBJETO (`Vida`) que COMECA em 3 por um `Once`.

       Variavel DO OBJETO, e nao global, de proposito: quando o jogo recomeca
       ela volta para o valor de fabrica — o contrario da Aula 8, onde o
       recorde tinha de SOBREVIVER ao recomeco.

       ⚠️ O dialogo da variavel do objeto NAO tem `Default Value` (a global
       tem): ela nasce valendo 0. O 3 entra por `Once` -> `Number(3)` ->
       `set`, o mesmo par que zerava o relogio da Aula 8."""
    abre_mesa(*CEL_JOGADOR)
    blocos.abre_categoria("Logic & Math")
    blocos.bloco_ou_solta("Object Variable", 800, Y_A)
    ov = blocos.acha_bloco("Object Variable", tipo="Object Variable")
    A.gesto("criar_vida", "g14", (0, 0),
            lambda: blocos.usa_global(ov, "Vida", 0), espera=1.5)
    blocos.abre_categoria("Triggers")
    blocos.bloco_ou_solta("Once", 800, Y_B)
    blocos.abre_categoria("Logic & Math")
    blocos.bloco_ou_solta("Number", 1700, Y_B)
    nu = blocos.acha_bloco("Number")
    blocos.escreve_valor(nu, VIDA)
    on = blocos.acha_bloco("Once")
    nu = blocos.acha_bloco("Number")
    blocos.liga_fixo(on, "out", nu, "get")
    nu = blocos.acha_bloco("Number")
    ov = blocos.acha_bloco("Vida", tipo="Object Variable")
    blocos.liga_fixo(nu, "out", ov, "set")
    print(f"   vida: Once -> Number({VIDA}) -> Vida.set", flush=True)
    A.cap("p12_vida")
    time.sleep(2)
    fecha_mesa()
    return True


@etapa
def barra():
    """A BARRA: `Vida.out` -> `Bar.value`, com 3 de maximo e vermelha."""
    abre_mesa(*CEL_JOGADOR)
    blocos.abre_categoria("GUI")
    blocos.bloco_ou_solta("Bar", 1700, Y_A)
    br = blocos.acha_bloco("Bar")
    blocos.abre_ajustes(br); time.sleep(1.5)
    blocos.campo_abaixo("current value", VIDA, dy=70, meia=38)
    blocos.campo_abaixo("max value", VIDA, dy=70, meia=38)
    blocos.campo_ao_lado("bar:", VERMELHO, folga=150)
    blocos.fecha_ajustes(); time.sleep(1.0)
    ov = blocos.acha_bloco("Vida", tipo="Object Variable")
    br = blocos.acha_bloco("Bar")
    blocos.liga_fixo(ov, "out", br, "value")
    print(f"   barra: Vida.out -> Bar.value (3 de 3, vermelha)", flush=True)
    A.cap("p13_barra")
    time.sleep(2)
    fecha_mesa()
    return True


@etapa
def batida():
    """O PERIGO: `Timer` -> `Proximity(Inimigo, 40 px)` -> `Number(-1)` -> `Vida.+`.

       ⛔ MEDIDO, e e o que mudou o desenho: com `Collision(Inimigo)` a barra
       desceu UMA vez (5096 -> 3404 px) e parou, com o morcego em cima do
       jogador por 40 s. O `Collision` dispara uma vez por batida, e um morcego
       que atravessa (nao e solido) fica ali dentro sem fazer uma batida nova.

       O `Proximity` que deu olhos ao morcego da o sentido de perigo ao
       jogador: de segundo em segundo ele pergunta `tem um Inimigo a menos de
       40 px?` e, se tem, a vida perde um ponto. Quem fica perto perde vida a
       cada segundo; quem foge para de perder.

       A documentacao diz que o `+` SOMA O VALOR QUE CHEGA; com `Number(-1)` ele
       subtrai um — e a variavel avisa a barra sozinha, pela saida `out`."""
    abre_mesa(*CEL_JOGADOR)
    blocos.abre_categoria("Triggers")
    blocos.bloco_ou_solta("Timer", 800, Y_C)
    t = blocos.acha_bloco("Timer")
    blocos.abre_ajustes(t); time.sleep(1.3)
    blocos.marca_do_bloco("repeat forever", True)
    blocos.fecha_ajustes(); time.sleep(1.0)
    blocos.abre_categoria("Components")
    blocos.bloco_ou_solta("Proximity", 1700, Y_C)
    px = blocos.acha_bloco("Proximity")
    blocos.abre_ajustes(px); time.sleep(1.5)
    blocos.escolhe_na_lista("select type", "Inimigo")
    blocos.campo_ao_lado("distance", PERTO, folga=150)
    blocos.fecha_ajustes(); time.sleep(1.0)
    blocos.abre_categoria("Logic & Math")
    # `solta`, NAO `bloco_ou_solta`: a mesa ja tem um `Number` (o do 3), e
    # `bloco_ou_solta` reaproveitaria ele em vez de soltar o do -1.
    blocos.solta("Number", 2500, Y_C)
    nu = max(blocos.acha_todos("Number"), key=lambda b: b.y)   # o de baixo: -1
    ponto = blocos.prepara_menos(nu, 0)
    blocos.clica_menos(ponto, 1)
    blocos.fecha_ajustes(); time.sleep(0.8)
    nu = max(blocos.acha_todos("Number"), key=lambda b: b.y)
    lido = blocos.le_valor(nu)
    if lido != "-1":
        raise RuntimeError(f"o Number do perigo mostra {lido!r} e eu esperava '-1'")
    t = blocos.acha_bloco("Timer")
    px = blocos.acha_bloco("Proximity")
    blocos.liga_fixo(t, "out", px, "check")
    px = blocos.acha_bloco("Proximity")
    nu = max(blocos.acha_todos("Number"), key=lambda b: b.y)
    blocos.liga_fixo(px, "x", nu, "get")
    nu = max(blocos.acha_todos("Number"), key=lambda b: b.y)
    ov = blocos.acha_bloco("Vida", tipo="Object Variable")
    blocos.liga_fixo(nu, "out", ov, "mais")
    print(f"   perigo: Timer -> Proximity(Inimigo, {PERTO} px) -> Number(-1) "
          "-> Vida.+", flush=True)
    A.cap("p14_batida")
    time.sleep(2)
    fecha_mesa()
    return True


@etapa
def prova_barra():
    """A promessa do passo 19: cada batida DESCE a barra.

       Mede os pixels vermelhos da barra no canto da fase: cheia no inicio,
       mais curta depois que o morcego encosta."""
    _entra_no_jogo()
    cheia = _barra(_foto("b0"))
    serie, menor, foto_tirada = [], cheia, False
    for _ in range(26):
        n = _barra(_foto("b"))
        if n is None:
            time.sleep(0.4)
            continue
        serie.append(n)
        if n < menor:
            menor = n
        if not foto_tirada and cheia and n < cheia * 0.85 and n > cheia * 0.3:
            A.cap("p15_barra_desce")
            foto_tirada = True
        time.sleep(0.4)
    if not foto_tirada:
        A.cap("p15_barra_desce")
    editor.exige_jogo()          # retrospectivo: a leitura da tela custa ~30 s
    print(f"   barra (px vermelhos): cheia {cheia} -> {serie}", flush=True)
    if cheia < 300:
        raise RuntimeError(f"a barra nao aparece cheia no inicio ({cheia} px "
                           "vermelhos) — a cor ou o canto estao errados")
    if menor > cheia * 0.85:
        raise RuntimeError(f"o morcego encostou e a barra nao desceu "
                           f"({cheia} -> {menor})")
    print(f"   PROVADO: a barra desceu de {cheia} para {menor} px", flush=True)
    editor.volta_ao_editor(); time.sleep(2)
    return True


@etapa
def fim():
    """FIM DE JOGO: `Vida.out` -> `Filter(input < 1)` -> `Restart Game`."""
    abre_mesa(*CEL_JOGADOR)
    blocos.abre_categoria("Logic & Math")
    blocos.bloco_ou_solta("Filter", 2500, Y_B)
    fi = blocos.acha_bloco("Filter")
    # O CLIPE E COM O PAINEL ABERTO nos dois quadros (como na Aula 8): fechado
    # no meio do gesto, o `confere_alvos` nao ve mudanca no ponto da seta.
    blocos.abre_ajustes(fi); time.sleep(1.5)
    blocos.escolhe_condicao_no_painel(fi, "greater than")   # ponto de partida
    A.gesto("condicao_menor", "g11", (0, 0),
            lambda: blocos.escolhe_condicao_no_painel(fi, "less than"), espera=1.4)
    _escreve_o_numero(fi)
    blocos.confere_condicao(fi, "less than")
    blocos.abre_categoria("Game Flow")
    blocos.bloco_ou_solta("Restart Game", 2500, Y_C, titulo="RestartGame")
    ov = blocos.acha_bloco("Vida", tipo="Object Variable")
    fi = blocos.acha_bloco("Filter")
    blocos.liga_fixo(ov, "out", fi, "in")
    fi = blocos.acha_bloco("Filter")
    rg = blocos.acha_bloco("RestartGame")
    blocos.liga_fixo(fi, "pass", rg, "go")
    print("   fim: Vida.out -> Filter(input < 1) -> Restart Game", flush=True)
    A.cap("p16_fim")
    time.sleep(2)
    fecha_mesa()
    return True


def _escreve_o_numero(fi):
    """Com o painel do `Filter` aberto e `less than` escolhido: o numero vira 1.

       O numero se ESCREVE no campo, em vez de clicar no `+`: o OCR nao le o `+`
       do painel (ele nao e uma palavra). Positivo nao sofre do problema do
       hifen. Fecha o painel e confere a CARA DO BLOCO."""
    a, _ = nav.captura("/tmp/_c9_fi.png")
    q = nav.acha_texto("less than", arquivo=a)
    if not q:
        raise RuntimeError("nao achei o seletor `less than` no painel do Filter")
    # o campo do numero fica ~82 px ABAIXO do seletor; -25 px do CENTRO da
    # frase cai no texto do campo, antes do `-` (com -60 o clique caia na
    # borda esquerda, fora dele)
    campo = (q[0] - 25, q[1] + 82)
    for _ in range(3):
        nav.clique_seguro(*campo); time.sleep(0.6)
        rs.tecla(0, cmd=True); time.sleep(0.25)
        rs.digita_teclas("1"); time.sleep(0.5)
        rs.tecla(48); time.sleep(0.6)
        blocos.fecha_ajustes(); time.sleep(0.9)
        # A CARA DO BLOCO, sem espacos: o OCR entrega `input` e `<1` como duas
        # palavras (`tem_texto('input < 1')` reprovava uma condicao CERTA).
        nav.captura("/tmp/_c9_fi2.png")
        perto = blocos._regiao_px(fi.x - 60, fi.y - 40, fi.x + 330, fi.y + 180)
        lido = nav.texto_da_tela(regiao=perto).replace(" ", "")
        if "input<1" in lido:
            return True
        blocos.abre_ajustes(fi); time.sleep(1.2)
    raise RuntimeError("escrevi 1 no campo do Filter e o bloco nao mostra "
                       "`input < 1`")


@etapa
def prova_fim():
    """A promessa do passo 21: com a vida no fim, o jogo RECOMECA.

       O sinal de recomeco e a BARRA VOLTANDO A ENCHER depois de ter ficado
       baixa — independente do numero que esta sendo testado."""
    _entra_no_jogo()
    cheia = _barra(_foto("f0"))
    serie, baixou, voltou = [], False, False
    for _ in range(80):
        n = _barra(_foto("f"))
        if n is None:
            time.sleep(0.4)
            continue
        serie.append(n)
        if n < cheia * 0.4:
            baixou = True
        if baixou and n > cheia * 0.9:
            voltou = True
            A.cap("p17_recomecou")
            break
        time.sleep(0.4)
    editor.exige_jogo()          # retrospectivo: a leitura da tela custa ~30 s
    print(f"   barra: cheia {cheia} -> {serie}", flush=True)
    if not baixou:
        raise RuntimeError("a barra nunca ficou baixa — o morcego nao alcancou "
                           "o jogador ou a batida nao desce a vida")
    if not voltou:
        raise RuntimeError("a barra baixou e o jogo nao recomecou")
    print("   PROVADO: a barra desceu ate quase zero e o jogo recomecou com ela "
          "cheia", flush=True)
    editor.volta_ao_editor(); time.sleep(2)
    return True


def main():
    AC.main(sys.modules[__name__])


if __name__ == "__main__":
    main()
