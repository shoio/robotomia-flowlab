#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aula 11 — Som, animacao e brilho. Constroi o jogo no Flowlab e fotografa cada gesto.

   O jogo: o corredor da fase de NOITE pega estrelas. Mas agora a estrela tem
   VIDA: ela GIRA (animacao), BRILHA (mistura) e faz um SOM de moeda quando e
   pega.

   O que e NOVO:
     - o editor de animacao dentro do editor de sprite: criar a animacao
       `gira`, somar um quadro e INVERTER esse quadro de cabeca para baixo;
     - o bloco `Animation`: escolhe a animacao e marca `Loop animation`;
     - o `SoundEffect`: `Choose Sound` -> `Sound Effects` -> busca -> OK;
     - o `Blending`: o numero que chega diz como a peca se mistura ao fundo
       (0 normal, 1 SOMA — a peca clareia o que esta atras).

   MEDIDO ANTES (PADRAO.md §2am), nos prototipos 3166105:
     - o quadro novo (`+`) NASCE COMO COPIA do anterior; a ferramenta `flip
       vertical` vira a copia de cabeca para baixo;
     - `Animation` tem `start/stop/go to` na entrada e `play/done/go to` na
       saida; o painel traz `Pick Animation`, `Loop animation`, `Stay on last
       frame when done` e `Priority`;
     - `SoundEffect`: `Choose Sound` abre o dialogo `SELECT SOUND`, que tem
       pastas; dentro de `Sound Effects` ha uma BUSCA ("coin" acha 8-bit/coins);
     - `Blending`: `Input Sets Blending` 0 normal, 1 add, 2 subtract, 3
       multiply, 4 screen.

       BANCADA=1 python3 fonte/roda_aula.py 11
"""
import os, shutil, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rs, nav, editor, blocos, comum

comum.pasta("aula11")
import aula_comum as AC
from aula_comum import (celula, clique, A, etapa, ETAPAS, cria_objeto, clona,
                        clona_casas, da_fisica, confere_fisica, abre_mesa,
                        fecha_mesa, rastreio, cor)
from comum import fecha_painel_objeto
ETAPAS.clear()

D = "aula11"
CEU = "1B2A4A"                    # a noite: azul bem escuro, mas nao preto
AC.SPRITES = {
    "Jogador": ("Flowlab Sprites", "Characters", 0, 0),
    "Chao":    ("Flowlab Sprites", "Blocks", 0, 0),
    "Estrela": ("Flowlab Sprites", "Objects", 9, 1),       # a estrela dourada
}

LINHA_CHAO = 10
CEL_JOGADOR = (1, 8)
CEL_ESTRELA = (13, 9)            # no chao: basta andar
Y_A, Y_B, Y_C, Y_D = 400, 700, 1380, 1000
SOM_BUSCA = "coin"
SOM_NOME = "coins sound effect 1"


def _area_do_jogo(im):
    import numpy as _np
    rgb = tuple(int(CEU[i:i + 2], 16) for i in (0, 2, 4))
    ys, xs = _np.nonzero(comum.mascara_cor(im, rgb, 16))
    if len(ys) < 20000:
        raise RuntimeError(f"nao achei o ceu da fase na tela ({len(ys)} px)")
    return int(ys.min()), int(ys.max()), int(xs.min()), int(xs.max())


def _foto(nome):
    from PIL import Image
    import numpy as _np
    a, _ = nav.captura(f"/tmp/_c11_{nome}.png")
    return _np.asarray(Image.open(a).convert("RGB"), dtype=int)


def _gifs_comuns():
    os.makedirs(f"{D}/gifs", exist_ok=True)
    for nome in ("abrir_my_games.gif", "novo_jogo.gif", "empty_project.gif"):
        if not os.path.exists(f"{D}/gifs/{nome}") and os.path.exists(f"aula10/gifs/{nome}"):
            shutil.copy(f"aula10/gifs/{nome}", f"{D}/gifs/{nome}")


def _grava_o_play(chave="jogar", gid="g07"):
    """Grava o clipe do Play desta aula (editor -> jogo) e volta ao editor."""
    editor.volta_ao_nivel(); time.sleep(1.5)
    p = nav.acha_texto("play")
    if not p:
        raise RuntimeError("nao achei o botao Play (estou mesmo no editor?)")
    antes = A.cap(gid + "_a")
    comum.CLIQUES.clear()
    clique(*p); time.sleep(1.5)
    depois = A.cap(gid + "_b")
    clicado = any(abs(p[0] - cx) <= 6 and abs(p[1] - cy) <= 6
                  for cx, cy in comum.CLIQUES)
    A.reg(chave, antes=antes, depois=depois, alvo=[int(p[0]), int(p[1])],
          botao="esq", clicado=clicado)
    editor.volta_ao_editor(); time.sleep(2)


def _toca_o_play():
    editor.volta_ao_nivel(); time.sleep(1.5)
    p = nav.acha_texto("play")
    if not p:
        raise RuntimeError("nao achei o botao Play (estou mesmo no editor?)")
    clique(*p)
    time.sleep(2.0)
    editor.exige_jogo()
    clique(1470, 620)



def _livre(depois_de=None, w=520, h=400, dx=470, dy=300):
    """Um ponto da mesa onde cabe um bloco, SEM tocar em nenhum outro nem em fio.

       ⛔ MEDIDO: a mesa ANDA entre uma soltura e outra (o ponto onde eu mirei
       para o 3o bloco ja era o do 2o: o `Number` caiu em cima do `Animation`
       e a leitura do valor falhou). Mirar em coordenadas fixas so funciona na
       mesa vazia; depois da primeira soltura, olha-se a tela e acha-se um
       vazio. `ocupado` = corpo de bloco (cinza-azulado) ou branco (titulo,
       pino, fio). Com `depois_de`, procura-se a DIREITA dele, na mesma faixa
       — o fio sai pela direita e entra pela esquerda."""
    import numpy as _np
    from PIL import Image
    a, _ = nav.captura("/tmp/_c11_livre.png")
    im = _np.asarray(Image.open(a).convert("RGB"), dtype=int)
    ocupado = ((_np.abs(im - _np.array((59, 66, 82))) <= 6).all(axis=2)
               | (im > 190).all(axis=2)).astype(_np.int64)
    ii = _np.zeros((ocupado.shape[0] + 1, ocupado.shape[1] + 1), _np.int64)
    ii[1:, 1:] = ocupado.cumsum(0).cumsum(1)

    def soma(x0, y0, x1, y1):
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(ocupado.shape[1], x1), min(ocupado.shape[0], y1)
        return int(ii[y1, x1] - ii[y0, x1] - ii[y1, x0] + ii[y0, x0])

    cand = []
    for y in range(420, 1180, 60):
        for x in range(700, 2400, 60):
            if x + w - 120 > 2900 or y + h - 100 > 1440:
                continue
            if soma(x - 120, y - 100, x - 120 + w, y - 100 + h) <= 120:
                cand.append((x, y))
    if depois_de is not None:
        perto = [(x, y) for x, y in cand
                 if x >= depois_de.x + dx and abs(y - depois_de.y) <= dy]
        cand = sorted(perto, key=lambda p: (p[0] - depois_de.x) + 2 * abs(p[1] - depois_de.y)) or cand
    if not cand:
        raise RuntimeError("nao achei um vazio na mesa para soltar o bloco")
    return cand[0]


def _livre_fila(n, dx=480, w=320, h=250):
    """`n` pontos em FILA (mesma altura, `dx` de distancia) onde cabem blocos.

       Planeja a fila INTEIRA antes da primeira soltura: depois de soltar o
       primeiro, o que sobra de mesa livre a direita pode nao dar para os
       outros (medido: o `Blending` foi parar em cima do `Number`)."""
    import numpy as _np
    from PIL import Image
    a, _ = nav.captura("/tmp/_c11_fila.png")
    im = _np.asarray(Image.open(a).convert("RGB"), dtype=int)
    ocupado = ((_np.abs(im - _np.array((59, 66, 82))) <= 6).all(axis=2)
               | (im > 190).all(axis=2)).astype(_np.int64)
    ii = _np.zeros((ocupado.shape[0] + 1, ocupado.shape[1] + 1), _np.int64)
    ii[1:, 1:] = ocupado.cumsum(0).cumsum(1)

    def livre(x, y):
        # o titulo cai em (x - 170, y - 58) e o bloco mede ~235 x 170 (medido)
        x0, y0 = max(0, x - 200), max(0, y - 90)
        x1, y1 = min(ocupado.shape[1], x0 + w), min(ocupado.shape[0], y0 + h)
        return int(ii[y1, x1] - ii[y0, x1] - ii[y1, x0] + ii[y0, x0]) <= 120

    for y in range(420, 1180, 60):
        for x in range(700, 2500, 60):
            if x + (n - 1) * dx + 120 > 2900:
                continue
            if all(livre(x + k * dx, y) for k in range(n)):
                return [(x + k * dx, y) for k in range(n)]
    raise RuntimeError(f"nao achei uma fila livre de {n} blocos na mesa")


# ─────────────────────────── a fase e o jogador ───────────────────────────

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
    a, _ = nav.captura("/tmp/_c11_rad.png")
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


# ─────────────────────────────── a estrela ───────────────────────────────

@etapa
def estrela():
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    cria_objeto(*CEL_ESTRELA, "Estrela", tipo="Estrela")
    A.cap("p08_estrela")
    return True


@etapa
def pega():
    """PEGAR: `Collision(Jogador)` -> `Destroyer` (a Aula 1, de novo)."""
    abre_mesa(*CEL_ESTRELA)
    blocos.abre_categoria("Triggers")
    blocos.bloco_ou_solta("Collision", 800, Y_A)
    co = blocos.acha_bloco("Collision")
    blocos.escolhe_tipo_da_colisao(co, "Jogador")
    blocos.abre_categoria("Components")
    blocos.bloco_ou_solta("Destroyer", 1700, Y_A)
    co = blocos.acha_bloco("Collision")
    de = blocos.acha_bloco("Destroyer")
    blocos.liga_fixo(co, "hit", de, "in")
    print("   estrela: Collision(Jogador).hit -> Destroyer.in", flush=True)
    A.cap("p09_pega")
    time.sleep(2)
    fecha_mesa()
    return True


def _titulo_do_dialogo():
    """(x, y) do titulo `SELECT SOUND`. O dialogo abre ao lado do painel — por
       cima ou por baixo, conforme o espaco — entao tudo nele se mede a partir
       do TITULO (medido: a distancia titulo -> OK e sempre a mesma)."""
    for _ in range(3):
        t = nav.acha_texto("select sound")
        if t:
            return t
        time.sleep(1.0)
    raise RuntimeError("nao achei o dialogo SELECT SOUND")


def _escolhe_o_som():
    """Painel do `SoundEffect`: Choose Sound -> Sound Effects -> busca -> 1o -> OK."""
    se = blocos.acha_bloco("SoundEffect")
    blocos.abre_ajustes(se); time.sleep(1.8)
    p = nav.acha_texto("choose sound")
    if not p:
        raise RuntimeError("nao achei o botao Choose Sound no painel do SoundEffect")
    clique(*p); time.sleep(2.0)
    escolhido = (int(p[0]), int(p[1]))     # onde a seta do clipe aponta: o botao
    tx, ty = _titulo_do_dialogo()
    clique(tx + 88, ty + 146); time.sleep(2.0)             # a linha Sound Effects
    tx, ty = _titulo_do_dialogo()
    clique(tx + 288, ty + 138); time.sleep(0.8)            # o campo de busca
    rs.digita_teclas(SOM_BUSCA); time.sleep(2.5)
    clique(tx + 122, ty + 234); time.sleep(0.8)            # o primeiro resultado
    A.cap("p10b_busca")
    clique(tx + 589, ty + 855); time.sleep(1.5)            # OK do dialogo
    return escolhido


@etapa
def som():
    """O SOM: `Collision.hit` tambem liga no `SoundEffect.play`."""
    abre_mesa(*CEL_ESTRELA)
    blocos.abre_categoria("Components")
    co = blocos.acha_bloco("Collision")
    blocos.bloco_ou_solta("Sound", *_livre(co, dx=650, dy=650), titulo="SoundEffect")
    A.gesto("escolher_o_som", "g31", (0, 0), _escolhe_o_som, espera=1.5)
    A.cap("p10_painel_som")
    achou = "coins sound effect" in nav.texto_da_tela().lower()
    print("   som escolhido:", SOM_NOME, "| lido no painel:", bool(achou), flush=True)
    if not achou:
        raise RuntimeError("o painel do SoundEffect nao mostra o nome do som escolhido")
    blocos.fecha_ajustes(); time.sleep(1.0)
    co = blocos.acha_bloco("Collision")
    se = blocos.acha_bloco("SoundEffect")
    blocos.liga_fixo(co, "hit", se, "play")
    print("   estrela: Collision.hit -> SoundEffect.play", flush=True)
    A.cap("p11_fio_som")
    time.sleep(2)
    fecha_mesa()
    return True


# ───────────────────────────── a animacao ─────────────────────────────

def _cria_a_animacao():
    """No editor de sprite: Animation Editor -> Pick Animation -> Create New -> `gira`."""
    p = nav.acha_texto("animation editor")
    if not p:
        raise RuntimeError("nao achei o Animation Editor no editor de sprite")
    clique(*p); time.sleep(2.0)
    aberto = (int(p[0]), int(p[1]))        # a seta aponta o Animation Editor
    q = nav.acha_texto("pick animation")
    if not q:
        raise RuntimeError("nao achei o Pick Animation")
    clique(*q); time.sleep(1.8)
    cn = nav.acha_texto("create new")
    if not cn:
        raise RuntimeError("nao achei o Create New na lista de animacoes")
    clique(*cn); time.sleep(2.0)
    clique(1470, 805); time.sleep(0.6)                     # o campo do nome
    rs.tecla(0, cmd=True); time.sleep(0.3)
    rs.digita_teclas("gira"); time.sleep(0.6)
    clique(1590, 902); time.sleep(2.0)                     # OK do dialogo
    return aberto


def _novo_quadro_invertido():
    """`+` (quadro 2, copia do 1) e `flip vertical` nele."""
    clique(689, 1480); time.sleep(1.5)                     # o `+`: nasce o quadro 2
    clique(520, 1480); time.sleep(1.0)                     # seleciona o quadro 1
    clique(689, 1480); time.sleep(1.0)                     # e volta ao quadro 2
    clique(229, 629); time.sleep(1.5)                      # ferramenta flip vertical
    return (689, 1480)                                     # a seta: o `+` (onde nasce o quadro)


@etapa
def animacao():
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    x, y = celula(*CEL_ESTRELA)
    editor.objeto_ou_abre(x, y); time.sleep(2)
    comum.abre_sprite()
    A.cap("p12_editor_sprite")
    A.gesto("criar_animacao", "g32", (0, 0), _cria_a_animacao, espera=1.5)
    A.cap("p13_gira")
    A.gesto("inverter_o_quadro", "g33", (0, 0), _novo_quadro_invertido, espera=1.5)
    A.cap("p14_dois_quadros")
    clique(*comum.SPRITE_OK); time.sleep(2.5); nav.espera_parar(limite=15)
    fecha_painel_objeto(); time.sleep(1.5)
    return True


@etapa
def gira():
    """GIRAR: `Once` -> `Animation.start`, com `gira` e `Loop animation`."""
    abre_mesa(*CEL_ESTRELA)
    blocos.abre_categoria("Triggers")
    blocos.bloco_ou_solta("Once", *_livre())
    on = blocos.acha_bloco("Once")
    blocos.abre_categoria("Properties")
    blocos.bloco_ou_solta("Animation", *_livre(on, dx=620, dy=250))
    an = blocos.acha_bloco("Animation")
    blocos.abre_ajustes(an); time.sleep(1.8)

    def escolher():
        blocos.escolhe_na_lista("pick animation", "gira")
        return blocos.marca_do_bloco("loop animation", True)   # a seta: a caixinha

    A.gesto("escolher_a_animacao", "g34", (0, 0), escolher, espera=1.5)
    A.cap("p15_painel_animacao")
    blocos.fecha_ajustes(); time.sleep(1.0)
    on = blocos.acha_bloco("Once")
    an = blocos.acha_bloco("Animation")
    blocos.liga_fixo(on, "out", an, "start")
    print("   estrela: Once.out -> Animation.start (gira, loop)", flush=True)
    A.cap("p16_gira")
    time.sleep(2)
    fecha_mesa()
    return True


def _estrela_agora():
    """(x, y, cor media) da estrela amarela no jogo, ou None."""
    import numpy as _np
    im = _foto("e")
    y0, y1, x0, x1 = _area_do_jogo(im)
    reg = im[y0:y1 + 1, x0:x1 + 1]
    m = (reg[:, :, 0] > 200) & (reg[:, :, 1] > 150) & (reg[:, :, 2] < 150)
    ys, xs = _np.nonzero(m)
    if len(xs) < 40:
        return None
    cx, cy = int(xs.mean()) + x0, int(ys.mean()) + y0
    recorte = im[cy - 45:cy + 45, cx - 45:cx + 45].copy()
    return (cx, cy, tuple(int(v) for v in reg[m].mean(axis=0)), len(xs), recorte)


@etapa
def prova_gira():
    """A promessa do passo da animacao: a estrela MUDA de pose sozinha."""
    _grava_o_play()
    _toca_o_play()
    pos = []
    for _ in range(14):
        e = _estrela_agora()
        if e:
            pos.append(e)
        time.sleep(0.18)
    A.cap("p17_jogo_gira")
    import numpy as _np
    ys = [p[1] for p in pos]
    editor.exige_jogo()
    if len(pos) < 6:
        raise RuntimeError(f"so achei a estrela em {len(pos)} quadros")
    # a POSE, nao o centro: virada de cabeca para baixo, a estrela quase nao
    # muda de lugar — muda o desenho. Mede-se a diferenca entre os recortes.
    base = pos[0][4]
    difs = [float(_np.abs(p[4] - base).mean()) for p in pos]
    print(f"   serie y da estrela: {ys}", flush=True)
    print(f"   diferenca de pose em relacao ao 1o quadro: "
          f"{[round(d, 1) for d in difs]}", flush=True)
    # sem animacao os quadros saem IDENTICOS (diferenca 0,0 em todos): qualquer
    # valor acima de 1 e a estrela trocando de pose
    if max(difs) < 1.0:
        raise RuntimeError(f"a estrela nao mudou de pose (diferenca maxima "
                           f"{max(difs):.1f})")
    cor_antes = [p[2] for p in pos]
    media = tuple(int(sum(c[i] for c in cor_antes) / len(cor_antes)) for i in range(3))
    open("/tmp/_c11_cor_sem_brilho.txt", "w").write(repr(media))
    print(f"   PROVADO: a estrela GIRA sozinha (a pose mudou ate {max(difs):.1f} "
          f"em {len(pos)} quadros); cor media sem brilho {media}", flush=True)
    editor.volta_ao_editor(); time.sleep(2)
    return True


# ─────────────────────────────── o brilho ───────────────────────────────

@etapa
def brilho():
    """BRILHAR: `Once` -> `Number(1)` -> `Blending.mode` (1 = soma)."""
    abre_mesa(*CEL_ESTRELA)
    n_once = len(blocos.acha_todos("Once"))
    p_once, p_num, p_bl = _livre_fila(3)
    blocos.abre_categoria("Triggers")
    # `solta`, e nao `bloco_ou_solta`: este devolve o Once que JA existe (da gira)
    blocos.solta("Once", *p_once)
    blocos.abre_categoria("Logic & Math")
    blocos.bloco_ou_solta("Number", *p_num)
    nu = blocos.acha_bloco("Number")
    blocos.escreve_valor(nu, 1)
    blocos.abre_categoria("Properties")
    blocos.bloco_ou_solta("Blending", *p_bl)
    ons = blocos.acha_todos("Once")
    if len(ons) != n_once + 1:
        raise RuntimeError(f"soltei um Once e a mesa tem {len(ons)} (eram {n_once})")
    nu = blocos.acha_bloco("Number")
    bl = blocos.acha_bloco("Blending")
    # o Once NOVO e o que fica na mesma fila do Number, a esquerda dele
    on = min(ons, key=lambda b: abs(b.y - nu.y) + abs(b.x - (nu.x - 480)))
    print(f"   [fila] Once ({on.x},{on.y}) Number ({nu.x},{nu.y}) Blending ({bl.x},{bl.y})", flush=True)
    blocos.liga_fixo(on, "out", nu, "get")
    nu = blocos.acha_bloco("Number")
    bl = blocos.acha_bloco("Blending")
    blocos.liga_fixo(nu, "out", bl, "mode")
    print("   estrela: Once -> Number(1) -> Blending.mode", flush=True)
    A.cap("p18_brilho")
    time.sleep(2)
    fecha_mesa()
    return True


@etapa
def prova_brilho():
    """A estrela fica MAIS CLARA com o `Blending` em 1: a cor media sobe."""
    _toca_o_play()
    pos = []
    for _ in range(10):
        e = _estrela_agora()
        if e:
            pos.append(e)
        time.sleep(0.2)
    A.cap("p19_jogo_brilho")
    editor.exige_jogo()
    if len(pos) < 4:
        raise RuntimeError(f"so achei a estrela em {len(pos)} quadros")
    antes = eval(open("/tmp/_c11_cor_sem_brilho.txt").read())
    depois = tuple(int(sum(p[2][i] for p in pos) / len(pos)) for i in range(3))
    print(f"   cor media da estrela: sem brilho {antes} -> com brilho {depois}",
          flush=True)
    if sum(depois) - sum(antes) < 15:
        raise RuntimeError("a estrela nao clareou com o Blending em soma")
    print(f"   PROVADO: com o Blending em 1 a estrela clareou "
          f"({sum(antes)} -> {sum(depois)})", flush=True)
    editor.volta_ao_editor(); time.sleep(2)
    return True


@etapa
def prova_tudo():
    """Joga: corre ate a estrela e PROVA que ela some (a batida continua valendo)."""
    _toca_o_play()
    n0 = _estrela_agora()
    if not n0:
        raise RuntimeError("nao achei a estrela no inicio do jogo")
    sumiu = False
    # corridas CURTAS, conferindo a estrela depois de cada uma: numa corrida
    # longa o jogador passa por cima da estrela (o pacote tambem pula) e sai
    # da fase pela direita — a estrela fica e o jogador some.
    for volta in range(16):
        rs.corre_e_pula(direcao=124, antes=0.05, segurando=0.25)
        if not _estrela_agora():
            sumiu = True
            break
    A.cap("p20_final")
    editor.exige_jogo()
    if not sumiu:
        raise RuntimeError("o jogador correu e a estrela continua na tela")
    print("   PROVADO: o jogador encostou na estrela e ela SUMIU (a animacao, "
          "o brilho e o som nao quebraram a batida)", flush=True)
    editor.volta_ao_editor(); time.sleep(2)
    return True


def main():
    AC.main(sys.modules[__name__])


if __name__ == "__main__":
    main()
