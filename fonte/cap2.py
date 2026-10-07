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

# O DESENHO DA FASE, numa folha de 28 colunas.
#
# O Flowlab nasce com 16x12 e vai ate 48x32 — eu construi tres aulas sem nunca
# ter procurado esse controle, e tratei o padrao como se fosse o limite. Com 28
# colunas a fase fica quase duas vezes mais comprida, e o preco esta medido: a
# pagina desenha o nivel inteiro, entao cada peca sai ~8% menor.
#
# Os VAOS continuam de UMA casa, que e a dificuldade ja provada na versao de 16
# colunas. Fase mais comprida nao e fase mais dificil: o que cresce e o caminho,
# nao o salto.
COLUNAS = 28            # as colunas do NIVEL (a tela continua com 16)
CEU = "87CEEB"          # azul de ceu; o padrao do Flowlab e FFFFFF

LINHA_CHAO = 8          # a plataforma onde o boneco comeca
LINHA_MEIO = 6          # a segunda plataforma
LINHA_ALTA = 4          # a terceira, onde fica a estrela
LINHA_LAVA = 11
# O BURACO DA ESQUERDA E PARTE DA AULA. O passo 20 manda a crianca errar de
# proposito — "ande para a esquerda ate cair do chao" — e para isso tem de
# haver chao ONDE CAIR. Na primeira versao desta fase comprida eu estiquei o
# chao ate a coluna 1, encostado na beirada do nivel: medido em jogo, o boneco
# andava ate x=628, batia no limite do nivel e ficava parado. A promessa do
# passo 20 virava mentira, e o guarda da prova foi quem disse.
COL_JOGADOR = 5
COLS_CHAO = list(range(3, 12))      # 3..11, com as colunas 0..2 VAZIAS
COLS_MEIO = list(range(13, 21))     # 13..20, vao na 12
COLS_ALTA = list(range(22, 28))     # 22..27, vao na 21
COL_ESTRELA = 25
COLS_LAVA = list(range(0, 28))

DENSIDADE = 30          # medido: pula 273 px e anda 60 px por toque

# OS DESENHOS, da biblioteca do Flowlab (pacote do ENDESGA). Ate aqui todo
# objeto era um quadrado pintado com a latinha.
SPRITES = {
    "Jogador":    ("Flowlab Sprites", "Characters", 0, 0),   # o menino
    "Chao":       ("Flowlab Sprites", "Blocks", 0, 0),       # bloco de grama
    "Plataforma": ("Flowlab Sprites", "Blocks", 0, 0),
    "Alta":       ("Flowlab Sprites", "Blocks", 0, 0),
    "Estrela":    ("Flowlab Sprites", "Objects", 9, 1),      # a estrela amarela
    "Lava":       ("Flowlab Sprites", "Terrain", 6, 0),      # lava com bolhas
}
CORES = {}


def _cores(quem):
    """Todas as cores medidas daquele sprite, da mais comum para a menos."""
    if quem in CORES and CORES[quem]:
        return CORES[quem]
    caminho = os.path.join(D, "cores.json")
    if os.path.exists(caminho):
        g = json.load(open(caminho))
        if quem in g:
            return g[quem]
    raise RuntimeError(f"nao sei as cores de `{quem}`")


def _rastreio(quem, *outros):
    """(cor, tolerancia) para achar `quem` sem achar `outros`.

       Uma porta so para as tres aulas: `comum.cor_de_rastreio`. Aqui havia
       uma copia que comparava so a PRIMEIRA cor de cada vizinho e media
       distancia pela SOMA dos canais — os dois errados. Na Aula 3 isso fez a
       sonda "procurar a estrela" e medir a lava, que tem respingos da mesma
       cor dourada. Duas copias do mesmo juizo, uma delas com o criterio
       defeituoso, e o lado sozinho que volta a morder."""
    return comum.cor_de_rastreio({q: _cores(q) for q in (quem,) + outros}, quem)


def _cor_de(quem, indice=0):
    import json
    if quem in CORES and CORES[quem]:
        return tuple(CORES[quem][indice])
    caminho = os.path.join(D, "cores.json")
    if os.path.exists(caminho):
        g = json.load(open(caminho))
        if quem in g:
            return tuple(g[quem][indice])
    raise RuntimeError(f"nao sei a cor de `{quem}`")


def _poe_sprite(quem, so_clique=False):
    """Escolhe o desenho e guarda as cores com que a prova vai acha-lo."""
    import json
    pacote, sub, lin, col = SPRITES[quem]
    if so_clique:
        ponto = comum.clica_sprite(lin, col)
    else:
        ponto = comum.escolhe_sprite(pacote, sub, lin, col)
    CORES[quem] = comum.cores_do_sprite("/tmp/_sp_dep.png")
    os.makedirs(D, exist_ok=True)
    caminho = os.path.join(D, "cores.json")
    g = json.load(open(caminho)) if os.path.exists(caminho) else {}
    g[quem] = CORES[quem]
    json.dump(g, open(caminho, "w"), indent=1)
    print(f"   sprite de {quem}: cores {CORES[quem][:3]}", flush=True)
    return ponto


def faz_peca(c, r, nome, cor, cols_clone=None):
    """Cria um objeto na casa (c, r), escolhe o desenho, e clona para as
       colunas pedidas. `cor` ficou no lugar por compatibilidade: quem manda
       agora e a tabela SPRITES."""
    x, y = celula(c, r)
    editor.objeto_ou_abre(x, y)
    nomeia(nome)
    abre_sprite()
    _poe_sprite(nome)
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
    # A TELA FICA NO PADRAO (16x12). O que e comprido e o NIVEL.
    #
    # Eu tinha alargado a tela achando que alargava a fase — e `Width` em
    # Settings e o tamanho da TELA, nao do nivel (o guia oficial diz "change
    # the screen width and height"). O resultado era a pagina desenhando tudo
    # menor, sem nada rolando. O nivel e tao grande quanto se constroi: da para
    # por peca FORA da folha branca, e a camera leva a vista ate la.
    comum.calibra_grade(16, 12)
    A.cap("p01_vazio")
    # O CEU. O campo da cor de fundo do nivel nasce em FFFFFF, e e por isso que
    # todos os jogos do curso eram brancos de folha de papel. Um campo so.
    A.gesto("pintar_o_ceu", "g08", (0, 0),
            lambda: editor.cor_do_ceu(CEU), espera=2.0)
    editor.volta_ao_nivel()
    A.cap("p02_ceu")
    print(f"   ceu em #{CEU}", flush=True)
    return True


@etapa
def jogador():
    editor.volta_ao_nivel()
    comum.calibra_grade(16, 12)
    x, y = celula(COL_JOGADOR, LINHA_CHAO - 1)
    A.gesto("criar_objeto", "g01", (x, y), lambda: clique(x, y), espera=1.5)
    a, _ = nav.captura("/tmp/_c2_rad.png")
    p = nav.acha_texto("create", arquivo=a)
    A.gesto("escolher_create", "g02", p, lambda: clique(*p), espera=3)
    editor.espera_tela("behaviors", limite=20)
    nomeia("Jogador")
    A.cap("p02_nome")
    abre_sprite()
    pacote, sub, lin, col = SPRITES["Jogador"]
    comum.abre_grade_sprite(pacote, sub)
    A.gesto("escolher_sprite", "g13", (0, 0),
            lambda: _poe_sprite("Jogador", so_clique=True), espera=2.0)
    A.cap("p03_azul")
    clique(*comum.SPRITE_OK); time.sleep(2); nav.espera_parar(limite=15)
    A.gesto("abrir_physics", "g03", (0, 0),
            lambda: comum.abre_fisica(), espera=2.5)
    A.gesto("marcar_movable", "g04", (0, 0),
            lambda: marca_caixa("movable", True), espera=1.2)
    # o peso: medido, e o que decide se ele pula
    # O PAINEL NASCE DO LADO DA CASA CLICADA, e com a folha mais larga ele
    # muda de lado: numa fase de 28 colunas o `density` apareceu em x=1033,
    # fora da metade direita que eu procurava. `_acha_no_painel` olha os dois
    # lados — existe para isso, e so a Aula 1 a usava para as caixinhas.
    pd = comum._acha_no_painel("density", nav.captura("/tmp/_c2_d.png")[0])
    if not pd:
        raise RuntimeError("nao achei o controle Density no painel de fisica")
    alvo = (int(pd[0] + 155 + 2.75 * DENSIDADE), pd[1])
    A.gesto("peso_do_pulo", "g05", alvo, lambda: clique(*alvo), espera=1.2)
    arrasta_slider("friction")
    A.cap("p04_fisica")
    fecha_painel_objeto()
    return True


@etapa
def movimento():
    editor.volta_ao_nivel()
    comum.calibra_grade(16, 12)
    x, y = celula(COL_JOGADOR, LINHA_CHAO - 1)
    editor.objeto_ou_abre(x, y)
    editor.abre_comportamentos()
    blocos.contexto(A.url or open(f"{D}/jogo.txt").read().strip(), (x, y))
    blocos.abre_categoria("Behavior Bundles")
    b = blocos.bloco_ou_solta("Run & Jump", 1500, 760)
    A.cap("p05_run_and_jump")
    print("   pacote:", b, flush=True)
    time.sleep(2.5)
    editor.fecha_comportamentos(); time.sleep(2.5)
    fecha_painel_objeto(); time.sleep(2)
    return True


@etapa
def camera():
    """A CAMERA: e ela que faz a fase comprida virar um caminho.

       Sem ela a pagina mostra so o pedaco do nivel que cabe na tela e o boneco
       anda para fora de vista. Com ela, a vista segue o boneco e o cenario
       entra em cena conforme ele avanca.

       O bloco ja vem com `autoscroll X` e `autoscroll Y` marcados — nao ha fio
       nem gatilho. O unico ajuste e o limite da direita, que nasce igual a
       largura da TELA (15) e precisa ir ate o fim do NIVEL.

       Do handbook: o `Camera` so funciona na camada do jogo, e so UM objeto do
       nivel deve ter um ("com mais de uma camera ativa o resultado e
       indefinido")."""
    editor.volta_ao_nivel()
    comum.calibra_grade(16, 12)
    x, y = celula(COL_JOGADOR, LINHA_CHAO - 1)
    editor.objeto_ou_abre(x, y)
    editor.abre_comportamentos()
    blocos.contexto(A.url or open(f"{D}/jogo.txt").read().strip(), (x, y))
    cam = blocos.bloco_ou_solta("Camera", 1200, 1150)
    A.cap("p12_camera")
    p = blocos.abre_ajustes(cam)
    A.gesto("limite_da_camera", "g07", (0, 0),
            lambda: blocos.campo_do_painel("right", COLUNAS - 1), espera=1.4)
    blocos.fecha_ajustes(); time.sleep(0.8)
    A.cap("p13_limite")
    print(f"   camera com limite direito em {COLUNAS - 1}", flush=True)
    time.sleep(2)
    editor.fecha_comportamentos(); time.sleep(2.5)
    fecha_painel_objeto(); time.sleep(2)
    return True


@etapa
def plataformas():
    editor.volta_ao_nivel()
    comum.calibra_grade(16, 12)
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
        nomeia("Alta"); abre_sprite(); _poe_sprite("Alta")
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
    editor.volta_ao_nivel()
    comum.calibra_grade(16, 12)
    faz_peca(COLS_LAVA[0], LINHA_LAVA, "Lava", "vermelho", COLS_LAVA[1:])
    A.cap("p09_lava")
    x, y = celula(COLS_LAVA[0], LINHA_LAVA)
    editor.objeto_ou_abre(x, y)
    editor.abre_comportamentos()
    blocos.contexto(A.url or open(f"{D}/jogo.txt").read().strip(), (x, y))
    c = blocos.bloco_ou_solta("Collision", 1120, 1220)
    A.cap("p10_collision")
    # NA MESMA FILEIRA do Collision, de proposito. O detector de fio
    # (`blocos._ha_fio`) fatia o caminho ao longo do eixo mais longo: num fio
    # RETO ele e confiavel, numa DIAGONAL ele erra. Com o Restart 580 px a
    # direita e 530 abaixo, o fio existia e ele dizia que nao — a captura
    # parava com "nenhum fio apareceu" e passava na repeticao, pela sorte do
    # tracado. A Aula 3 ja punha os dois na mesma fileira, e la isso nao
    # acontece.
    r = blocos.bloco_ou_solta("Restart Game", 1700, 1220, titulo="RestartGame")
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
    editor.volta_ao_nivel()
    comum.calibra_grade(16, 12)
    x, y = celula(COL_ESTRELA, LINHA_ALTA - 1)
    editor.objeto_ou_abre(x, y)
    nomeia("Estrela")
    abre_sprite(); _poe_sprite("Estrela")
    clique(*comum.SPRITE_OK); time.sleep(2); nav.espera_parar(limite=15)
    A.cap("p13_estrela")
    editor.abre_comportamentos()
    blocos.contexto(A.url or open(f"{D}/jogo.txt").read().strip(), (x, y))
    c = blocos.bloco_ou_solta("Collision", 1120, 1220)
    d = blocos.bloco_ou_solta("Destroyer", 1700, 1220)     # mesma fileira
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

    # as cores saem dos SPRITES, e a do jogador e a que mais se distingue da
    # lava e da estrela — a mais comum dele e a pele, que puxa para o amarelo
    cor_jog, tol_jog = _rastreio("Jogador", "Lava", "Estrela")
    print(f"   rastreando o boneco por {cor_jog} (tol {tol_jog})", flush=True)

    def pos():
        """O centro de TODOS os pixels da cor: no jogo o sprite sai pequeno e
           partido, e exigir uma mancha unica dizia que o boneco sumiu."""
        a, _ = nav.captura("/tmp/_c2_j.png")
        g = comum.centro_por_cor(a, cor_jog, tol=tol_jog, minimo=60)
        return (g[0], g[1]) if g else None

    editor.volta_ao_editor(); time.sleep(2)
    editor.volta_ao_nivel()
    comum.calibra_grade(16, 12)
    p = nav.acha_texto("play")
    if not p:
        raise RuntimeError("nao achei o botao Play (estou mesmo no editor?)")
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


@etapa
def prova_camera():
    """Prova a promessa do passo 12: a CAMERA segue o boneco.

       A assinatura e inconfundivel e precisa das DUAS medidas no mesmo quadro:
       o boneco fica mais ou menos parado na tela enquanto o CHAO desliza
       debaixo dele. Medir so o boneco nao distingue "ele andou" de "o mundo
       andou" — foi esse o furo que me fez dar a camera por morta durante
       horas."""
    from PIL import Image
    import numpy as np

    cor_jog, tol_jog = _rastreio("Jogador", "Lava", "Estrela")
    cor_chao = tuple(_cores("Chao")[0])

    def ler():
        a, _ = nav.captura("/tmp/_c2cam.png")
        im = np.asarray(Image.open(a).convert("RGB"), dtype=int)
        mj = comum.mascara_cor(im, cor_jog, tol_jog); ys, xs = np.nonzero(mj)
        jog = None if len(xs) < 60 else int(xs.mean())
        mc = comum.mascara_cor(im, cor_chao, 46); yc, xc = np.nonzero(mc)
        chao = None if len(xc) < 400 else int(xc.min())
        return jog, chao

    editor.volta_ao_editor(); time.sleep(2)
    editor.volta_ao_nivel()
    p = nav.acha_texto("play")
    if not p:
        raise RuntimeError("nao achei o botao Play")
    clique(*p); time.sleep(7)
    editor.exige_jogo()
    clique(1470, 620); time.sleep(1.5)

    j0, c0 = ler()
    if j0 is None or c0 is None:
        raise RuntimeError("nao achei o boneco e o chao no comeco do jogo")
    jogs, chaos = [j0], [c0]
    for _ in range(8):
        clique(1470, 620); time.sleep(0.3)
        rs.segura_tecla(124, 0.6)          # 124 = seta direita
        j, c = ler()
        if j is not None and c is not None:
            jogs.append(j); chaos.append(c)
    andou_boneco = max(jogs) - min(jogs)
    andou_chao = max(chaos) - min(chaos)
    print(f"   o boneco variou {andou_boneco} px na tela; o chao deslizou "
          f"{andou_chao} px", flush=True)
    A.cap("p19_camera")
    if andou_chao < 150:
        raise RuntimeError(f"o chao so deslizou {andou_chao} px: a camera nao "
                           "esta seguindo o boneco")
    if andou_boneco > andou_chao:
        raise RuntimeError(f"o boneco andou {andou_boneco} px e o chao so "
                           f"{andou_chao}: quem se mexeu foi ele, nao a vista")
    print("   PROVADO: a vista segue o boneco e o cenario entra em cena",
          flush=True)
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
