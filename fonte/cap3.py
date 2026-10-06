#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Captura da Aula 3 — A lava que sobe.

   O jogo: o mesmo boneco que corre e pula, mas agora a lava NAO FICA PARADA.
   Ela sobe sozinha, do pe da tela para o alto, e quem nao subir a tempo
   recomeca. No alto fica a estrela, e encostar nela abre um aviso de vitoria.

   O que e NOVO em relacao a Aula 2: uma coisa que se mexe SEM ninguem apertar
   tecla nenhuma — `Always` + `Velocity` — e o fim de jogo com `Alert`.

   O que foi MEDIDO antes de escrever a aula (rascunho 3150191):
   - `Always.out -> Number.get -> Number.out -> Velocity.y` move o objeto, com
     `movable` marcado e `affected by gravity` DESMARCADO;
   - `+y` e para BAIXO: para subir, o numero e NEGATIVO;
   - com `-0.5` a lava sobe 27,2 px de tela por segundo — as 7 casas entre ela
     e a estrela levam ~16 s, que e o tempo de fuga da crianca (com `-1`
     seriam 8 s, tenso demais para quem esta aprendendo a pular);
   - o campo do valor ENGOLE o hifen digitado em primeiro lugar: o caminho e o
     botao `−`, que tira 1 por clique (0.5 e um clique = -0.5)."""
import os, sys, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rs, nav, editor, blocos, comum
from comum import (celula, clique, pinta, nomeia, nomeia_tipo, abre_sprite, marca_caixa,
                   arrasta_slider, fecha_painel_objeto, A, etapa, ETAPAS,
                   CELULA, GRADE_X, GRADE_Y, SPRITE_OK)

comum.pasta("aula3")
ETAPAS.clear()
D = "aula3"

# O DESENHO DA FASE — uma escada, nao um salto de fe.
#
# A primeira versao tinha plataformas de 3 casas separadas por 2 colunas de
# vao. Medido em jogo: o pulo chegava la, mas o pouso caia em qualquer lugar
# entre a beirada esquerda e o vazio depois da direita — a mesma sequencia de
# teclas as vezes pousava, as vezes caia. Isso nao e dificuldade, e sorte.
#
# Agora cada degrau sobe 2 fileiras e anda 1 coluna, e as plataformas sao
# largas. A estrela fica na PONTA DIREITA do degrau de cima, para a crianca
# ANDAR ate ela — encostar andando e o toque que esta provado desde a Aula 1;
# cair em cima de uma peca de 1 casa, nao.
LINHA_CHAO  = 8
LINHA_MEIO  = 6
LINHA_ALTA  = 4
LINHA_LAVA  = 11
COL_JOGADOR = 3
COLS_CHAO   = [1, 2, 3, 4, 5, 6]
COLS_MEIO   = [7, 8, 9, 10, 11]
COLS_ALTA   = [12, 13, 14, 15]
COL_ESTRELA = 15
COLS_LAVA   = list(range(0, 16))

DENSIDADE = 30          # medido na Aula 2: pula 273 px e anda 60 px por toque
CEU = "1A1A40"          # noite; a lava que sobe pede um ceu escuro
SUBIDA    = "0.5"       # digitado positivo; um clique no `−` deixa -0.5

# OS DESENHOS, da biblioteca do Flowlab (pacote do ENDESGA). Ate a Aula 2 todo
# objeto era um quadrado pintado com a latinha; agora sao sprites de verdade,
# os MESMOS da Aula 2 — a Aula 3 muda o que a lava FAZ, nao o que ela parece.
SPRITES = {
    "Jogador":    ("Flowlab Sprites", "Characters", 0, 0),   # o menino
    "Chao":       ("Flowlab Sprites", "Blocks", 0, 0),       # bloco de grama
    "Plataforma": ("Flowlab Sprites", "Blocks", 0, 0),
    "Alta":       ("Flowlab Sprites", "Blocks", 0, 0),
    "Estrela":    ("Flowlab Sprites", "Objects", 9, 1),      # a estrela dourada
    "Lava":       ("Flowlab Sprites", "Terrain", 6, 0),      # lava com bolhas
}
CORES = {}


def _cor_de(quem, indice=0):
    if quem in CORES and CORES[quem]:
        return tuple(CORES[quem][indice])
    caminho = os.path.join(D, "cores.json")
    if os.path.exists(caminho):
        g = json.load(open(caminho))
        if quem in g:
            return tuple(g[quem][indice])
    raise RuntimeError(f"nao sei a cor de `{quem}`")


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

       Os `outros` sao escolhidos a mao porque chao, plataforma e degrau alto
       sao o MESMO desenho: exigir que se distingam entre si reprovaria uma
       fase correta. Quem precisa ser distinguido e quem a prova mede."""
    return comum.cor_de_rastreio({q: _cores(q) for q in (quem,) + outros}, quem)


def _poe_sprite(quem, so_clique=False):
    """Escolhe o desenho na biblioteca e guarda as cores com que a prova em
       jogo vai achar esse objeto na tela."""
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
       colunas pedidas. `cor` ficou no lugar so por compatibilidade: quem
       manda agora e a tabela SPRITES."""
    x, y = celula(c, r)
    editor.objeto_ou_abre(x, y)
    nomeia(nome)
    abre_sprite()
    _poe_sprite(nome)
    clique(*SPRITE_OK); time.sleep(2); nav.espera_parar(limite=15)
    fecha_painel_objeto()
    if cols_clone:
        clique(x, y); time.sleep(1.5)
        a, _ = nav.captura("/tmp/_c3_clone.png")
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
    comum.calibra_grade(16, 12)
    A.cap("p01_vazio")
    # O CEU. O campo de cor do nivel nasce em FFFFFF — e e por isso que todos
    # os jogos do curso eram brancos de folha de papel. Um campo so, no painel
    # `Game Levels`, ao lado do nome do nivel.
    A.gesto("pintar_o_ceu", "g14", (0, 0),
            lambda: editor.cor_do_ceu(CEU), espera=2.0)
    editor.volta_ao_nivel()
    A.cap("p01b_ceu")
    print(f"   ceu em #{CEU}", flush=True)
    return True


@etapa
def jogador():
    editor.volta_ao_nivel()
    x, y = celula(COL_JOGADOR, LINHA_CHAO - 1)
    A.gesto("criar_objeto", "g01", (x, y), lambda: clique(x, y), espera=1.5)
    a, _ = nav.captura("/tmp/_c3_rad.png")
    p = nav.acha_texto("create", arquivo=a)
    A.gesto("escolher_create", "g02", p, lambda: clique(*p), espera=3)
    editor.espera_tela("behaviors", limite=20)
    nomeia("Jogador")
    # o TIPO tambem: e o nome do tipo que aparece na lista do bloco Collision,
    # nao o nome do objeto. Sem isto a lava nao tem como saber em quem bater.
    nomeia_tipo("Jogador")
    A.cap("p02_nome")
    abre_sprite()
    pacote, sub, lin, col = SPRITES["Jogador"]
    comum.abre_grade_sprite(pacote, sub)
    A.gesto("escolher_sprite", "g13", (0, 0),
            lambda: _poe_sprite("Jogador", so_clique=True), espera=2.0)
    A.cap("p03_azul")
    clique(*SPRITE_OK); time.sleep(2); nav.espera_parar(limite=15)
    A.gesto("abrir_physics", "g03", (0, 0),
            lambda: comum.abre_fisica(), espera=2.5)
    A.gesto("marcar_movable", "g04", (0, 0),
            lambda: marca_caixa("movable", True), espera=1.2)
    # O PAINEL NASCE DO LADO DA CASA CLICADA, e com a folha mais larga ele
    # muda de lado: numa fase de 28 colunas o `density` apareceu em x=1033,
    # fora da metade direita que eu procurava. `_acha_no_painel` olha os dois
    # lados — existe para isso, e so a Aula 1 a usava para as caixinhas.
    pd = comum._acha_no_painel("density", nav.captura("/tmp/_c3_d.png")[0])
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
    x, y = celula(COL_JOGADOR, LINHA_CHAO - 1)
    editor.objeto_ou_abre(x, y)
    editor.abre_comportamentos()
    blocos.abre_categoria("Behavior Bundles")
    b = blocos.bloco_ou_solta("Run & Jump", 1500, 760)
    A.cap("p05_run_and_jump")
    print("   pacote:", b, flush=True)
    time.sleep(2.5)
    editor.fecha_comportamentos(); time.sleep(2.5)
    fecha_painel_objeto(); time.sleep(2)
    return True


@etapa
def plataformas():
    editor.volta_ao_nivel()
    faz_peca(COLS_CHAO[0], LINHA_CHAO, "Chao", "verde", COLS_CHAO[1:])
    A.cap("p06_chao")
    faz_peca(COLS_MEIO[0], LINHA_MEIO, "Plataforma", "verde", COLS_MEIO[1:])
    A.cap("p07_plataforma")
    faz_peca(COLS_ALTA[0], LINHA_ALTA, "Alta", "verde", COLS_ALTA[1:])
    A.cap("p08_tres_plataformas")
    return True


@etapa
def lava():
    """A lava: a barra do pe da tela, que vai SUBIR."""
    editor.volta_ao_nivel()
    faz_peca(COLS_LAVA[0], LINHA_LAVA, "Lava", "vermelho", COLS_LAVA[1:])
    A.cap("p09_lava")
    return True


@etapa
def lava_fisica():
    """Separada da criacao de proposito: sao dois gestos bem diferentes, e
       assim da para repetir um sem refazer o outro."""
    editor.volta_ao_nivel()
    x, y = celula(COLS_LAVA[0], LINHA_LAVA)
    editor.objeto_ou_abre(x, y)
    # para a lava se mexer ela precisa de fisica — e SEM gravidade, senao ela
    # cai em vez de subir
    A.gesto("fisica_da_lava", "g06", (0, 0),
            lambda: comum.abre_fisica(), espera=2.5)
    marca_caixa("movable", True)
    A.gesto("desligar_gravidade", "g07", (0, 0),
            lambda: marca_caixa("affected by gravity", False), espera=1.2)
    # SEM 'is solid' a lava ATRAVESSA as plataformas. Medido em jogo: com ela
    # solida, as pecas que ficam debaixo de uma plataforma travam e a parede
    # se parte — a lava vira pedacos em alturas diferentes e a crianca fica
    # em cima do chao sem perigo nenhum. O editor nao acusa nada disso.
    A.gesto("lava_atravessa", "g10", (0, 0),
            lambda: marca_caixa("is solid", False), espera=1.2)
    # ...mas desmarcar 'is solid' tambem desliga a BATIDA: a lava subia por
    # cima do boneco e nada acontecia. No lugar do 'is solid' nasce uma
    # caixinha nova, `enable collisions` — e ela que devolve o toque sem
    # devolver o empurrao. Medido: com ela, o jogo recomeca; sem ela, nao.
    A.gesto("lava_sente_o_toque", "g11", (0, 0),
            lambda: marca_caixa("enable collisions", True), espera=1.2)
    A.cap("p10_lava_sem_gravidade")
    fecha_painel_objeto(); time.sleep(1.5)
    return True


@etapa
def lava_sobe():
    """O coracao da aula: tres blocos que fazem a lava subir sozinha."""
    editor.volta_ao_nivel()
    x, y = celula(COLS_LAVA[0], LINHA_LAVA)
    editor.objeto_ou_abre(x, y)
    editor.abre_comportamentos()
    al = blocos.bloco_ou_solta("Always", 1150, 600)
    A.cap("p11_always")
    nu = blocos.bloco_ou_solta("Number", 1500, 900)
    A.cap("p12_number")
    ve = blocos.bloco_ou_solta("Velocity", 2000, 600)
    A.cap("p13_velocity")
    blocos.liga_fixo(al, "out", nu, "get")
    blocos.liga_fixo(nu, "out", ve, "y")
    A.cap("p14_fios")
    # O NUMERO: digitado positivo e levado ao negativo pelo botao `−`, que e o
    # unico caminho que funciona (o campo engole o hifen digitado primeiro)
    # Pelo `A.gesto`, nao pelo `A.reg` na mao: eu fotografava os DOIS quadros
    # depois do gesto ja feito, e o clipe saia uma figura parada — antes
    # identico a depois. O guarda dos alvos agora reprova isso.
    # O CLIPE GRAVA SO O CLIQUE NO `−`, nao o gesto inteiro.
    #
    # Gravando abrir-digitar-clicar-fechar, o antes e o depois mostram os dois
    # o painel FECHADO, e a seta aponta para um botao que nao esta em quadro
    # nenhum. `prepara_menos` deixa o painel aberto com o valor positivo ja
    # digitado; o clipe e so o clique, que e o gesto que a crianca precisa ver.
    ponto = blocos.prepara_menos(nu, SUBIDA)
    A.gesto("botao_menos", "g08", ponto,
            lambda: blocos.clica_menos(ponto, 1), espera=1.6)
    blocos.fecha_ajustes(); time.sleep(0.8)
    A.cap("p15_menos_meio")
    print("   lava com velocidade", blocos.le_valor(nu), flush=True)
    time.sleep(2)
    editor.fecha_comportamentos(); time.sleep(2.5)
    fecha_painel_objeto(); time.sleep(1.5)
    return True


@etapa
def lava_mata():
    editor.volta_ao_nivel()
    x, y = celula(COLS_LAVA[0], LINHA_LAVA)
    editor.objeto_ou_abre(x, y)
    editor.abre_comportamentos()
    # Longe da beirada direita de proposito: soltar um bloco perto dela faz a
    # mesa ROLAR sozinha, e os blocos que ja estavam la saem de vista — eu
    # media pinos de um bloco que nao estava mais onde eu pensava.
    c = blocos.bloco_ou_solta("Collision", 1120, 1220)
    r = blocos.bloco_ou_solta("Restart Game", 1700, 1220, titulo="RestartGame")
    blocos.liga_fixo(c, "hit", r, "go")
    # COM QUEM a batida conta. Em 'Any Type' o bloco dispara com qualquer
    # coisa — e uma lava que sobe bate primeiro no CHAO: o jogo reiniciava
    # sozinho a cada poucos segundos e a fase ficava impossivel, sem nada no
    # editor acusando.
    blocos.escolhe_tipo_da_colisao(c, "Jogador")
    A.cap("p16_lava_reinicia")
    print("   lava ligada ao reinicio", flush=True)
    time.sleep(2)
    editor.fecha_comportamentos(); time.sleep(2.5)
    fecha_painel_objeto(); time.sleep(1.5)
    return True


@etapa
def estrela():
    editor.volta_ao_nivel()
    x, y = celula(COL_ESTRELA, LINHA_ALTA - 1)
    editor.objeto_ou_abre(x, y)
    nomeia("Estrela")
    abre_sprite()
    _poe_sprite("Estrela")
    clique(*SPRITE_OK); time.sleep(2); nav.espera_parar(limite=15)
    A.cap("p17_estrela")
    editor.abre_comportamentos()
    c = blocos.bloco_ou_solta("Collision", 1120, 620)
    d = blocos.bloco_ou_solta("Destroyer", 1700, 620)
    blocos.liga_fixo(c, "hit", d, "in")
    # A estrela tambem precisa dizer COM QUEM a batida conta. Em 'Any Type' a
    # LAVA, ao subir, atravessa a estrela e a destroi — o jogo se ganha
    # sozinho, antes de a crianca chegar la, e o que ela ve e uma estrela que
    # some do nada. Foi isso que fez a minha sonda "subir a fase seis vezes
    # sem nunca pegar a estrela": ela ja tinha sido comida pela lava.
    blocos.escolhe_tipo_da_colisao(c, "Jogador")
    A.cap("p18_fio_estrela")
    # Aqui havia um `Alert` com as frases da vitoria. Tirei depois de ver em
    # jogo: o Alert ESCURECE a tela e nao desenha a caixa dentro do canvas da
    # pagina do jogo — a crianca encostaria na estrela e veria a tela apagar,
    # sem uma palavra. A estrela que SOME e a mesma peca da Aula 1, ja provada,
    # e diz 'peguei' sem ambiguidade.
    A.cap("p19_estrela_pronta")
    time.sleep(2)
    editor.fecha_comportamentos(); time.sleep(2.5)
    fecha_painel_objeto(); time.sleep(1.5)
    A.cap("p20_fase_pronta")
    return True


@etapa
def prova():
    """Prova em jogo as TRES promessas da aula:
       1) a lava SOBE sozinha, sem ninguem apertar tecla;
       2) quando ela alcanca o boneco, o jogo RECOMECA;
       3) o boneco pula (senao nao ha como fugir).

       As duas primeiras saem da MESMA serie de leituras. A primeira versao
       mediu a altura da lava em dois instantes separados por 4 s e leu -15 px:
       no meio dos 4 s o jogo tinha recomecado e a lava voltado para o pe da
       tela. Dois instantes nao distinguem 'nao subiu' de 'subiu e recomecou'.
    """
    from PIL import Image
    import numpy as np

    # As cores saem dos SPRITES, medidas na hora em que o desenho foi escolhido
    # — nao de uma faixa de tom escrita a mao. Com quadrados pintados dava para
    # dizer "o vermelho e a lava"; com sprite de verdade o heroi TAMBEM tem
    # vermelho na roupa, e a faixa larga pegaria os dois.
    cor_jog, tol_jog = _rastreio("Jogador", "Lava", "Estrela")
    cor_lava, tol_lava = _rastreio("Lava", "Jogador", "Estrela")
    print(f"   rastreando o boneco por {cor_jog} (tol {tol_jog}) e a lava por "
          f"{cor_lava} (tol {tol_lava})", flush=True)

    def boneco():
        """O centro de TODOS os pixels da cor do heroi: no jogo o sprite sai
           pequeno e PARTIDO, e exigir mancha unica dizia que ele sumiu."""
        a, _ = nav.captura("/tmp/_c3_j.png")
        g = comum.centro_por_cor(a, cor_jog, tol=tol_jog, minimo=60)
        return (g[0], g[1]) if g else None

    def topo_da_lava(largura=200):
        """A BEIRADA DE CIMA da lava, nao o centro de uma mancha.

           A lava e a unica coisa da fase que atravessa a tela inteira: procuro
           a primeira fileira de pixels que tem pelo menos `largura` pixels da
           cor dela. Assim um pedaco de roupa vermelha do heroi nunca e lido
           como lava, e o numero que sai e exatamente o que a aula promete —
           ate onde a lava CHEGOU."""
        a, _ = nav.captura("/tmp/_c3_j.png")
        im = np.asarray(Image.open(a).convert("RGB"), dtype=int)
        por_fileira = comum.mascara_cor(im, cor_lava, tol_lava).sum(axis=1)
        fileiras = np.nonzero(por_fileira >= largura)[0]
        return int(fileiras.min()) if len(fileiras) else None

    editor.volta_ao_editor(); time.sleep(2)
    editor.volta_ao_nivel()
    p = nav.acha_texto("play")
    if not p:
        raise RuntimeError("nao achei o botao Play (estou mesmo no editor?)")
    A.gesto("jogar", "g09", p, lambda: clique(*p), espera=6)
    editor.exige_jogo()
    clique(1470, 620); time.sleep(1.5)
    A.cap("p21_jogo")

    # 1) o boneco pula — medido LOGO no comeco, enquanto a lava ainda esta
    # longe. Medindo no fim, um reinicio no meio das leituras teleporta o
    # boneco e o guarda passa por motivo errado: li 611 px de "pulo" uma vez,
    # quase o dobro do que este pacote consegue.
    b0 = boneco()
    if not b0:
        raise RuntimeError("nao achei o boneco no jogo")
    alt = []
    rs.segura_tecla(126, 0.2)
    for _ in range(6):
        time.sleep(0.12)
        q = boneco()
        alt.append(q[1] if q else None)
    validos = [h for h in alt if h]
    pulo = b0[1] - min(validos) if validos else 0
    print(f"   pulo: subiu {pulo} px", flush=True)
    if pulo < 60:
        raise RuntimeError(f"o boneco subiu so {pulo} px: sem pulo nao ha fuga")

    serie = []
    for k in range(24):
        serie.append(topo_da_lava())
        if k == 3:
            A.cap("p22_lava_subindo")
        time.sleep(0.6)
    print("   serie da lava:", serie, flush=True)
    alturas = [y for y in serie if y is not None]
    if len(alturas) < 10:
        raise RuntimeError(f"nao achei a faixa da lava no jogo ({len(alturas)} "
                           "leituras de 24)")

    # 2) a maior SUBIDA seguida: y diminuindo de uma leitura para a outra
    melhor = atual = 0
    for a1, a2 in zip(alturas, alturas[1:]):
        atual = atual + (a1 - a2) if a2 < a1 else 0
        melhor = max(melhor, atual)
    print(f"   a lava subiu {melhor} px de uma vez", flush=True)
    if melhor < 60:
        raise RuntimeError(f"a maior subida seguida da lava foi {melhor} px — "
                           "a aula promete uma lava que sobe sozinha")

    # 3) o salto de volta para o pe da tela: o jogo RECOMECOU
    quedas = [a2 - a1 for a1, a2 in zip(alturas, alturas[1:]) if a2 - a1 > 100]
    print(f"   o jogo recomecou {len(quedas)} vez(es) "
          f"(a lava voltou {max(quedas) if quedas else 0} px)", flush=True)
    if not quedas:
        raise RuntimeError("a lava subiu e o jogo nunca recomecou — a aula "
                           "promete que encostar nela volta ao comeco")
    A.cap("p23_recomecou")

    return True


@etapa
def prova_vitoria():
    """Prova que ENCOSTAR NA ESTRELA faz ela sumir.

       A aula promete isso no passo 19, e promessa de pagina sem execucao que
       a contradiga e a que envelhece sem ninguem ver. Entao subo a fase de
       verdade.

       Duas coisas que a primeira versao desta sonda errou:
       - ela tocava a seta de ANDAR e depois a de PULAR. Separadas, o boneco
         pula parado e cai no mesmo lugar: 'subi a fase tres vezes' sem ter
         saido do chao. `rs.corre_e_pula` segura uma e toca a outra.
       - e ela conferia sem olhar se o boneco ainda estava vivo. Depois de
         cair, as teclas vao para o vazio e a sonda conclui que a fase nao tem
         saida."""
    cor_jog, tol_jog = _rastreio("Jogador", "Lava", "Estrela")
    cor_lava, tol_lava = _rastreio("Lava", "Jogador", "Estrela")
    cor_estrela, tol_estrela = _rastreio("Estrela", "Jogador", "Lava")
    print(f"   boneco {cor_jog}/{tol_jog}  lava {cor_lava}/{tol_lava}  "
          f"estrela {cor_estrela}/{tol_estrela}", flush=True)

    import numpy as np
    from PIL import Image

    def leitura():
        """UMA foto so, e as tres medidas saem dela. Devolve (arquivo, boneco,
           estrela, lava).

           Por que juntas: cada medida tirava a SUA propria foto, e entre uma e
           outra passava meio segundo. O jogo pisca entre aceso e apagado (o
           Flowlab escurece tudo quando a pagina perde o foco), entao eu lia
           'a estrela nao esta' no quadro ESCURO e 'o boneco esta' no quadro
           ACESO — dois instantes diferentes — e chamava isso de vitoria. A
           foto que a sonda guardou como prova tinha o canvas inteiro preto."""
        a, _ = nav.captura("/tmp/_c3_v.png")
        im = np.asarray(Image.open(a).convert("RGB"), dtype=int)

        def centro(cor, tol, minimo):
            m = comum.mascara_cor(im, cor, tol)
            ys, xs = np.nonzero(m)
            if len(xs) < minimo:
                return None
            return (int(xs.mean()), int(ys.mean()))

        # O JOGO ESTA ACESO NESTE QUADRO?
        #
        # Isto importa porque o Flowlab ESCURECE o jogo inteiro quando a pagina
        # perde o foco, e o escurecimento nao atinge as cores por igual: o azul
        # do boneco sobrevive a tolerancia 46, o dourado da estrela nao
        # sobrevive a 25. Entao "a estrela sumiu" num quadro escuro nao e uma
        # leitura ruim, e leitura NENHUMA.
        #
        # QUEM RESPONDE E A LAVA. A versao anterior contava BRANCO PURO no
        # fundo do nivel (569.000 aceso contra 0 apagado) — e isso parou de
        # valer no dia em que a aula passou a PINTAR O CEU: com fundo de noite
        # nao ha um pixel branco, e a sonda reprovaria todo quadro. A lava
        # atravessa o nivel inteiro, nunca sai de cena, e e a cor mais saturada
        # da fase: se ela aparece com a cor CHEIA, o quadro esta aceso. E ela ja
        # estava sendo medida aqui, para dar as beiradas.
        ml = comum.mascara_cor(im, cor_lava, tol_lava)
        ys, xs = np.nonzero(ml)
        aceso, beiradas = False, None
        if len(xs) >= 400:
            aceso = True
            beiradas = (int(xs.min()), int(xs.max()))

        return (a, centro(cor_jog, tol_jog, 60),
                centro(cor_estrela, tol_estrela, 100), beiradas, aceso)

    def espera_comeco(limite=40):
        for _ in range(limite):
            _a, q, _e, _l, _ac = leitura()
            if q and abs(q[0] - inicio[0]) < 40:
                return True
            time.sleep(0.8)
        return False

    # ABRIR O JOGO ATE ELE DESENHAR. Medido: abrir a pagina do jogo logo depois
    # da outra prova devolve, as vezes, um canvas PRETO — a pagina carrega, o
    # titulo esta certo, `exige_jogo` aprova, e nao ha um pixel do nivel. Dali
    # toda leitura de ausencia vira falsa vitoria.
    for arranque in range(3):
        editor.volta_ao_editor(); time.sleep(2)
        editor.volta_ao_nivel()
        p = nav.acha_texto("play")
        if not p:
            raise RuntimeError("nao achei o botao Play (estou mesmo no editor?)")
        clique(*p); time.sleep(6)
        editor.exige_jogo()
        clique(1470, 620); time.sleep(1.5)
        _a, _q, e, l, ac = leitura()
        if e and l and ac:
            break
        print(f"   (abertura {arranque + 1}: a pagina do jogo nao desenhou)",
              flush=True)
    else:
        raise RuntimeError("abri o jogo tres vezes e o nivel nunca desenhou — "
                           "daqui nenhuma medida de ausencia vale")
    # ONDE o boneco nasce, medido na hora. Numero fixo aqui envelhece: bastou
    # mudar a coluna onde a fase comeca para a sonda ficar esperando um boneco
    # que estava na tela, parado, 60 px ao lado.
    _a, inicio, _e, _l, _ac = leitura()
    if not inicio:
        raise RuntimeError("nao achei o boneco no comeco do jogo")
    print(f"   o boneco nasce em x={inicio[0]}", flush=True)

    def acorda():
        """Clique dentro do jogo ANTES de cada gesto e de cada leitura.

           Medido, e e a chave de tudo: com o jogo apagado as TECLAS NAO
           CHEGAM NELE. O mesmo corre-e-pula que, com o jogo aceso, leva o
           boneco 373 px para a direita e 128 px para cima — dois degraus —
           levava 163 px e nenhum degrau quando o quadro estava escuro. Era por
           isso que ele empacava na coluna 6, a beirada do chao, catorze pulos
           seguidos: metade dos meus comandos ia para um jogo pausado.

           O escurecimento nao e esporadico: no registro ele aparece a CADA
           gesto, e some a cada clique."""
        clique(1470, 620)
        time.sleep(0.6)

    # ONDE O BONECO ESTA, EM DEGRAUS. Medido na propria tela, nao decorado: o
    # canvas vai da beirada esquerda a direita da LAVA, que atravessa o nivel
    # inteiro, e o nivel tem 16 colunas. A altura diz em que degrau ele esta —
    # os tres ficam 128 px um acima do outro.
    #
    # Isto existe porque a sonda apertava teclas as CEGAS, com tempo fixo:
    # `antes=0.12` fazia ela pular no meio do chao e cair de volta, e
    # `antes=0.45` fazia andar ate a beirada e cair no vao. Medido, o acerto
    # era de uma vez em duas — e uma subida unica nao distingue gesto certo de
    # sorte. A crianca nao joga assim: ela OLHA onde esta. Entao a sonda anda
    # ate perto da ponta do degrau em que esta, e so entao pula.
    DEGRAUS = [(LINHA_CHAO - 1, COLS_CHAO[-1]),
               (LINHA_MEIO - 1, COLS_MEIO[-1]),
               (LINHA_ALTA - 1, COLS_ALTA[-1])]

    def degrau_de(q, base_y, altura=128, folga=45):
        """Em que degrau ele esta, pela altura. None se nao da para dizer."""
        for i in range(len(DEGRAUS)):
            if abs(q[1] - (base_y - i * altura)) <= folga:
                return i
        return None

    for tentativa in range(8):
        if not espera_comeco():
            raise RuntimeError("o boneco nao voltou ao comeco: o jogo travou?")
        acorda()
        arq, q, viva, lava, ac = leitura()
        if not (ac and q and lava):
            continue
        base_y = q[1]                      # a altura do chao, medida na hora
        canvas0, largura = lava[0], (lava[1] - lava[0]) / 16.0

        for passo in range(26):
            acorda()
            arq, q, viva, _l, ac = leitura()
            if not ac:
                continue                   # quadro apagado nao e leitura
            if not viva and q:
                import shutil
                os.makedirs(D, exist_ok=True)
                shutil.copy(arq, os.path.join(D, "p24_pegou_a_estrela.png"))
                print(f"   encostei na estrela e ela SUMIU "
                      f"(tentativa {tentativa + 1}, passo {passo})", flush=True)
                return True
            if not viva and not q:
                acorda()
                _a, q2, e2, _l2, ac2 = leitura()
                if q2 or e2 or not ac2:
                    continue
                A.cap("p24_jogo_apagado")
                raise RuntimeError("a estrela sumiu E o boneco tambem, e clicar "
                                   "dentro do jogo nao acordou: o jogo esta "
                                   "pausado ou parou de desenhar — isso nao e "
                                   "vitoria")
            if not q:
                break                      # caiu; o laco de fora recomeca
            i = degrau_de(q, base_y)
            col = (q[0] - canvas0) / largura
            if i is None:
                print(f"     t{tentativa+1} p{passo}: col {col:.1f} y {q[1]} "
                      f"NO AR", flush=True)
                continue                   # entre dois degraus
            ponta = DEGRAUS[i][1]
            if i == len(DEGRAUS) - 1:
                gesto = "anda ate a estrela"
                rs.segura_tecla(124, 0.12)
            elif col < ponta - 0.8:
                gesto = f"anda (ponta em {ponta})"
                rs.segura_tecla(124, 0.18)
            else:
                # PULA JA, sem corrida antes.
                #
                # `antes` e quanto tempo o boneco CORRE antes de o pulo ser
                # apertado. Perto da ponta do degrau isso e fatal: com 0,35 s
                # ele percorre duas colunas, sai da beirada, e quando o pulo
                # chega ele ja esta NO AR — e o pacote `Run & Jump` so deixa
                # pular com o boneco TOCANDO alguma coisa. O comando vai para o
                # vazio e ele cai na lava. Medido: 26 passos vezes 8 tentativas,
                # sempre «col 5,8 -> PULA -> col 3,5», que e morrer e renascer.
                #
                # A corrida de impulso ja aconteceu nos passos de andar. Aqui o
                # pulo e imediato, e a seta de lado fica segurada DURANTE o voo,
                # que e o que leva o boneco para cima do degrau seguinte.
                gesto = "PULA"
                rs.corre_e_pula(direcao=124, antes=0.02, segurando=0.6)
            print(f"     t{tentativa+1} p{passo}: col {col:.1f} y {q[1]} "
                  f"degrau {i} -> {gesto}", flush=True)
            time.sleep(0.25)
    raise RuntimeError("subi a escada oito vezes e a estrela nao sumiu")


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
