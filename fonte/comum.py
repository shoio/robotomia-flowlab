#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ajudantes que TODA aula do curso usa: a grade do nivel, os pontos medidos
   da tela, e os gestos (nomear, pintar, marcar caixinha, mexer no controle
   deslizante, fechar painel) com as suas armadilhas ja resolvidas.

   Cada aula importa daqui e so escreve o que e dela. Antes isto vivia dentro
   da cap1.py; com doze aulas pela frente, copiar seria garantir que uma delas
   envelhecesse sozinha."""
import os, sys, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rs, nav, editor, blocos

# A BANCADA. Com `BANCADA=1` no ambiente, as pecas de entrada e captura passam
# a falar com um Chrome fora da tela, em vez do mouse e do teclado do sistema.
# Fica aqui porque toda aula importa `comum`, e porque so vale depois de `rs`,
# `nav`, `editor` e `blocos` ja estarem carregados — a troca e nos objetos de
# modulo, que sao os mesmos para todo mundo.
import bancada
bancada.liga_se_pedido()

D = "aula1"          # a aula que esta sendo capturada; cada capN.py muda isto


def pasta(nome=None):
    global D
    if nome:
        D = nome
    return D


GRADE_X, GRADE_Y, CELULA = 958, 415, 64


def celula(c, r):
    """Centro da celula (coluna, linha) em pixels da tela."""
    return (GRADE_X + CELULA * c + CELULA // 2, GRADE_Y + CELULA * r + CELULA // 2)


LINHA_CHAO = 8
LINHA_ANDAR = 7
COL_JOGADOR = 6
COL_MOEDA = 8
COLS_CHAO = list(range(5, 15))

BALDE = (229, 358)
PALETA = {"azul": (2786, 535), "amarelo": (2786, 390), "verde": (2700, 460),
          "vermelho": (2855, 320)}
SPRITE_AREAS = [(1456, 781), (1456, 413), (1456, 1148)]
SPRITE_OK = (140, 1560)
AZUL_OK = (126, 168, 224)
OK_PAINEL = (1772, 1200)

ETAPAS = []


def etapa(fn):
    ETAPAS.append(fn); return fn


class A:
    url = None

    @staticmethod
    def guarda_url(endereco=None):
        """Grava o endereco do jogo da aula em `aulaN/jogo.txt`.

           Antes ele so era IMPRESSO durante a captura. Quando precisei
           regravar um clipe da Aula 2, abri o rascunho que eu usara para
           medir, porque o unico numero escrito em algum lugar era o do
           comentario do codigo — e na conta todos os jogos se chamam
           `New Game` e nenhum tem miniatura."""
        endereco = endereco or A.url
        if not endereco:
            return None
        os.makedirs(D, exist_ok=True)
        with open(os.path.join(D, "jogo.txt"), "w") as f:
            f.write(endereco.strip() + "\n")
        return endereco

    @staticmethod
    def cap(nome):
        os.makedirs(D, exist_ok=True)
        nav.captura(f"{D}/{nome}.png")
        return f"{nome}.png"

    @staticmethod
    def reg(chave, **kw):
        tudo = json.load(open(os.path.join(D, "alvos.json"))) if os.path.exists(os.path.join(D, "alvos.json")) else {}
        tudo[chave] = kw
        json.dump(tudo, open(os.path.join(D, "alvos.json"), "w"), indent=1, ensure_ascii=False)
        print(f"   clipe {chave}", flush=True)

    @staticmethod
    def gesto(chave, base, alvo, acao, botao="esq", espera=1.6):
        """Captura ANTES, faz o gesto, captura DEPOIS e registra o par.
           Se a acao devolver um ponto, e ELE que vale como alvo do clipe —
           senao a seta da animacao aponta para onde eu PENSEI em clicar, e
           nao para onde cliquei (ja aconteceu com a caixinha 'movable')."""
        a = A.cap(base + "_a")
        CLIQUES.clear()
        devolvido = acao()
        if isinstance(devolvido, (tuple, list)) and len(devolvido) == 2:
            alvo = devolvido
        time.sleep(espera)
        nav.espera_parar(limite=15)
        b = A.cap(base + "_b")
        alvo = (int(alvo[0]), int(alvo[1]))
        # o alvo saiu de um clique de verdade?
        clicado = any(abs(alvo[0] - cx) <= 6 and abs(alvo[1] - cy) <= 6
                      for cx, cy in CLIQUES)
        A.reg(chave, antes=a, depois=b, alvo=list(alvo), botao=botao,
              clicado=clicado)
        return b


CLIQUES = []            # onde a maquina clicou desde o ultimo `gesto`


def clique(x, y, duplo=False):
    """Todo clique da aula passa pelo guarda: acima da pagina esta o Chrome.

       E fica REGISTRADO. O alvo da seta de um clipe tem de ser um lugar onde
       a maquina clicou de verdade — e esse o invariante. A regra anterior
       ('a seta aponta onde a tela mudou') errava no gesto de escolher sprite:
       ao clicar no boneco da grade, o que muda e o DESENHO, do outro lado da
       tela, e a celula clicada fica igual."""
    CLIQUES.append((int(x), int(y)))
    nav.clique_seguro(x, y, duplo=duplo)


def fecha_painel_objeto():
    """Fecha o painel do objeto pelo OK azul, achado pela COR.

       O painel nasce do LADO da casa clicada: para a lava, que comeca na
       coluna 1, ele abre a ESQUERDA da tela. Procurando o azul so na metade
       direita eu caia no ponto de reserva — espaco vazio — e o painel ficava
       aberto, com o clique seguinte caindo dentro dele."""
    for _ in range(3):
        p = (nav.acha_cor(AZUL_OK, tol=40, regiao=(0.0, 0.45, 1.0, 0.98), minimo=800)
             or nav.acha_cor(AZUL_OK, tol=40, regiao=(0.0, 0.05, 1.0, 0.98), minimo=800))
        alvo = (p[0], p[1]) if p else OK_PAINEL
        clique(*alvo)
        time.sleep(1.8); nav.espera_parar(limite=12)
        a, _ = nav.captura("/tmp/_c1_ok.png")
        texto = " ".join(t for t, *_ in rs.ocr_forte(a, psm="6")).lower()
        if "edit sprite" not in texto and "collision shape" not in texto:
            return True
    raise RuntimeError("cliquei no OK e o painel do objeto continua aberto")


def pinta(cor):
    clique(*BALDE); time.sleep(0.6)
    clique(*PALETA[cor]); time.sleep(0.6)
    for p in SPRITE_AREAS:
        clique(*p); time.sleep(0.7)


def nomeia(nome):
    a, _ = nav.captura("/tmp/_c1_nome.png")
    # o painel muda de altura e de lado conforme a celula do objeto: procuro
    # numa faixa larga, e so desisto depois de tentar de novo
    p = None
    for regiao in ((0.45, 0.05, 1.0, 0.9), (0.3, 0.05, 1.0, 0.95), None):
        p = nav.acha_texto("name", arquivo=a, regiao=regiao)
        if p:
            break
    if not p:
        time.sleep(1.5)
        a, _ = nav.captura("/tmp/_c1_nome2.png")
        p = nav.acha_texto("name", arquivo=a, regiao=(0.3, 0.05, 1.0, 0.95))
    if not p:
        raise RuntimeError("nao achei o campo Name")
    clique(p[0], p[1] + 46, duplo=True); time.sleep(0.6)
    rs.tecla(0, cmd=True); time.sleep(0.25)
    rs.digita_teclas(nome); time.sleep(0.4)
    rs.tecla(48); time.sleep(0.8)          # Tab: o Enter FECHA o painel
    return True


def abre_sprite():
    a, _ = nav.captura("/tmp/_c1_es.png")
    p = nav.acha_texto("edit sprite", arquivo=a)
    if not p:
        raise RuntimeError("nao achei 'edit sprite'")
    clique(*p); time.sleep(3); nav.espera_parar(limite=20)
    return p


# O painel do objeto nasce do LADO da casa clicada: para um objeto do meio da
# tela ele abre a direita, para um da beirada esquerda (a lava, que comeca na
# coluna 1) ele abre a ESQUERDA. Procurar so na metade direita fazia o
# 'movable' da lava "nao existir".
PAINEL = [(0.45, 0.05, 1.0, 0.9), (0.0, 0.05, 0.55, 0.9), None]


def _acha_no_painel(alvo, arquivo):
    for regiao in PAINEL:
        p = nav.acha_texto(alvo, arquivo=arquivo, regiao=regiao)
        if p:
            return p
    return None


# As duas caras de uma caixinha do painel de fisica, medidas na tela:
CAIXA_MARCADA   = (131, 183, 249)      # azul
CAIXA_DESMARCADA = (69, 76, 93)        # cinza (o fundo do painel e 47,52,63)


def _caixinha(arquivo, ponto_rotulo):
    """(x, y, marcada) da caixinha que pertence a este rotulo.

       Acha a caixinha pela COR, na faixa a esquerda do rotulo, e fica com a
       mais PERTO dele. O deslocamento fixo que eu usava antes (90 px) so
       valia para 'movable': o rotulo e achado pelo CENTRO do texto, e o
       centro anda com o tamanho da palavra. Para 'is solid' o deslocamento
       certo e 54, e para 'affected by gravity' e 84 — com os 90 eu amostrava
       o fundo do painel, lia 'desmarcada' e saia sem clicar. A funcao
       devolvia True sem ter feito nada."""
    import numpy as _np
    from PIL import Image as _I
    im = _np.asarray(_I.open(arquivo).convert("RGB"), dtype=int)
    x, y = ponto_rotulo
    x0 = max(0, x - 200)
    faixa = im[max(0, y - 8):y + 9, x0:max(x0 + 1, x - 20)]
    def perto(cor, tol=26):
        return ((abs(faixa[:, :, 0] - cor[0]) < tol) &
                (abs(faixa[:, :, 1] - cor[1]) < tol) &
                (abs(faixa[:, :, 2] - cor[2]) < tol))
    for cor, marcada in ((CAIXA_MARCADA, True), (CAIXA_DESMARCADA, False)):
        m = perto(cor)
        colunas = m.sum(axis=0)
        # junto colunas vizinhas em FAIXAS e fico com a faixa mais a direita
        # que tenha largura de caixinha. Pegar simplesmente o pixel mais a
        # direita apanhava a borda do texto do rotulo, 50 px fora da caixa.
        faixas, inicio = [], None
        for i, n_px in enumerate(list(colunas) + [0]):
            if n_px >= 6 and inicio is None:
                inicio = i
            elif n_px < 6 and inicio is not None:
                faixas.append((inicio, i - 1)); inicio = None
        boas = [f for f in faixas if 14 <= (f[1] - f[0] + 1) <= 70]
        if not boas:
            continue
        a_, b_ = boas[-1]
        # faixa larga = a caixinha COLADA na borda do texto do rotulo; a
        # caixinha e a ponta DIREITA dela
        meio = (a_ + b_) // 2 if (b_ - a_ + 1) <= 34 else b_ - 13
        return (x0 + meio, y, marcada)
    return None


def marca_caixa(rotulo, quero=True):
    """Marca/desmarca uma caixinha do painel, achando-a pelo ROTULO.

       O painel do objeto MUDA de posicao na tela conforme o objeto e o que
       esta aberto; coordenada fixa aqui ja deixou 'movable' desmarcado sem
       ninguem notar — e com ele desmarcado a Densidade fica desabilitada, o
       jogador corre e a moeda nao some. Conferido pela COR da caixinha."""
    from PIL import Image as _I
    for tentativa in range(3):
        a, _ = nav.captura("/tmp/_c1_caixa.png")
        p = _acha_no_painel(rotulo.lower(), a)
        if not p:
            raise RuntimeError(f"nao achei a caixinha '{rotulo}' no painel")
        achado = _caixinha(a, p)
        if not achado:
            raise RuntimeError(f"achei o rotulo '{rotulo}' mas nao a caixinha dele")
        cx, cy, marcada = achado
        # DEVOLVE O PONTO, nao True — e so DEPOIS de conferir que a caixinha
        # ficou como eu queria. Quem grava o clipe usa o que esta funcao
        # devolver como alvo da seta; devolvendo True, o alvo ficava no (0,0)
        # que o chamador tinha passado, e a animacao mostrava o cursor
        # clicando no CANTO DA TELA enquanto o texto mandava marcar quatro
        # caixinhas. Cinco clipes sairam assim, um deles ja publicado.
        if marcada == quero:
            return (cx, cy)
        clique(cx, cy)
        time.sleep(1.0)
    raise RuntimeError(f"nao consegui deixar '{rotulo}' como {quero}")


def arrasta_slider(rotulo, ate_direita=True):
    """Arrasta um controle deslizante do painel de fisica ate a ponta.
       Acha pela ETIQUETA (Density, Friction) porque o painel MUDA de altura:
       marcar 'movable' faz nascer uma linha nova e empurra tudo para baixo."""
    a, _ = nav.captura("/tmp/_c1_slider.png")
    p = _acha_no_painel(rotulo.lower(), a)
    if not p:
        raise RuntimeError(f"nao achei o controle '{rotulo}' no painel de fisica")
    # este controle fixa o valor ONDE O MOUSE DESCE — arrastar a partir da
    # esquerda zera o valor em vez de aumentar (medi 3.0 depois de 'arrastar
    # para a direita'). Entao: clique direto na ponta.
    alvo = p[0] + 430 if ate_direita else p[0] + 155
    clique(alvo, p[1])
    time.sleep(1.0)
    return p


def confere_fase(cores=None, minimo=120):
    """Olha o nivel e confere que a fase FAZ SENTIDO antes de jogar:
       chao contiguo, e jogador e moeda EM CIMA dele, na mesma linha.

       Nasceu de uma fase que parecia pronta na foto e nao era: metade das
       pecas de chao nao tinha sido colocada, o jogador ficou no ar a esquerda
       do chao, e o jogo 'nao funcionava' sem que nada no editor acusasse.

       `cores` = {"chao": (r,g,b), "jogador": …, "moeda": …}, medidas dos
       SPRITES. Antes eu procurava verde, azul e amarelo chapados porque era eu
       quem pintava os quadrados; com sprite de verdade o jogador e um boneco,
       e so a camisa dele e azul — a versao antiga achava 192 px e dizia que a
       fase nao tinha jogador."""
    from PIL import Image
    import numpy as np
    import Quartz
    if not cores:
        raise RuntimeError("confere_fase precisa das cores medidas dos sprites")
    # tira o ponteiro da area do nivel: o Flowlab desenha uma CAIXINHA LARANJA
    # na celula sob o cursor, e ela entrava na conta como se fosse a moeda
    J = nav.janela()
    rs._evento_mouse(Quartz.kCGEventMouseMoved, J["x"] + 60, J["y"] + 700)
    time.sleep(0.8)
    a, _ = nav.captura("/tmp/_fase.png")
    # SO a area do nivel: a interface do Flowlab tem azul e amarelo proprios, e
    # ler a janela inteira deu um 'jogador' de 1500 px de largura
    im = np.asarray(Image.open(a).convert("RGB"), dtype=int)
    im = im[GRADE_Y:GRADE_Y + CELULA * 12, GRADE_X:GRADE_X + CELULA * 16]

    def caixa(cor, nome):
        m = mascara_cor(im, cor)
        ys, xs = np.nonzero(m)
        if len(xs) < minimo:
            raise RuntimeError(f"a fase nao tem {nome} (achei {len(xs)} px da "
                               f"cor {cor})")
        return (xs.min() + GRADE_X, xs.max() + GRADE_X,
                ys.min() + GRADE_Y, ys.max() + GRADE_Y)

    cx0, cx1, cy0, cy1 = caixa(cores["chao"], "chao")
    jx0, jx1, jy0, jy1 = caixa(cores["jogador"], "jogador")
    mx0, mx1, my0, my1 = caixa(cores["moeda"], "moeda")
    largura_esperada = CELULA * len(COLS_CHAO)
    problemas = []
    if (cx1 - cx0) < largura_esperada * 0.9:
        problemas.append(f"o chao tem {cx1-cx0} px e devia ter ~{largura_esperada}")
    for nome, x0, x1 in (("jogador", jx0, jx1), ("moeda", mx0, mx1)):
        if not (cx0 - CELULA <= x0 and x1 <= cx1 + CELULA):
            problemas.append(f"o {nome} esta fora do chao (x {x0}..{x1}, "
                             f"chao {cx0}..{cx1})")
    if problemas:
        raise RuntimeError("a fase nao esta montada: " + "; ".join(problemas))
    print(f"   fase conferida: chao {cx0}..{cx1}, jogador {jx0}, moeda {mx0}",
          flush=True)
    return True




def maior_mancha(mascara):
    """(x, y, tamanho) do MAIOR aglomerado conexo da mascara, ou None.

       A media de TODOS os pixels da cor nao serve na pagina do jogo: a
       selecao de texto do Chrome pinta as palavras do menu de azul, e a media
       do 'azul' passou a cair no meio do caminho entre o boneco e o topo da
       pagina. O boneco e um quadrado inteiro; o realce e um risco fino — a
       maior mancha e ele."""
    import numpy as _np
    vistos = _np.zeros_like(mascara)
    ys, xs = _np.nonzero(mascara)
    melhor = None
    H, L = mascara.shape
    for yy, xx in zip(ys, xs):
        if vistos[yy, xx]:
            continue
        pilha, pts = [(yy, xx)], []
        vistos[yy, xx] = True
        while pilha:
            cy, cx = pilha.pop()
            pts.append((cy, cx))
            for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < H and 0 <= nx < L and mascara[ny, nx] and not vistos[ny, nx]:
                    vistos[ny, nx] = True
                    pilha.append((ny, nx))
        if melhor is None or len(pts) > melhor[2]:
            melhor = (int(sum(p[1] for p in pts) / len(pts)),
                      int(sum(p[0] for p in pts) / len(pts)), len(pts))
    return melhor


def nomeia_tipo(nome):
    """Escreve o TIPO do objeto (o campo `Type`, ao lado do `Name`).

       E o nome do TIPO que aparece na lista do bloco `Collision` — o nome do
       objeto nao aparece la. Sem isto a lista mostra 'New Type 1', 'New Type
       2'… e nao ha como a crianca saber qual e qual."""
    a, _ = nav.captura("/tmp/_c1_tipo.png")
    p = None
    for regiao in ((0.3, 0.05, 0.75, 0.9), (0.0, 0.05, 1.0, 0.95), None):
        p = nav.acha_texto("type", arquivo=a, regiao=regiao)
        if p:
            break
    if not p:
        raise RuntimeError("nao achei o campo Type")
    clique(p[0] + 40, p[1] + 54, duplo=True); time.sleep(0.6)
    rs.tecla(0, cmd=True); time.sleep(0.25)
    rs.digita_teclas(nome); time.sleep(0.4)
    rs.tecla(48); time.sleep(0.8)          # Tab: o Enter FECHA o painel
    return True


LINK_FISICA = (108, 170, 233)      # o azul claro do texto "Physics >"


def abre_fisica(tentativas=4):
    """Entra na fisica do objeto.

       O `Physics >` e texto pequeno, fino e azul claro sobre fundo escuro, no
       canto do painel: o OCR o perde — lia 'Behaviors', 'edit sprite', 'Type',
       'Name', 'Reset', 'Display Order' e justamente ele nao. Entao acho pela
       COR do proprio link, dentro da area do painel.

       O QUE ESTA FUNCAO NAO FAZ MAIS: chutar. A primeira versao, quando nao
       achava, clicava num ponto deduzido do botao OK — e o azul do OK casou
       com o AVATAR DA CONTA, no canto de baixo. O clique abriu o menu
       `droneiscool / Log out`, que ficou por cima de tudo, e as tentativas
       seguintes procuraram o painel numa tela que era outra. Palpite que
       clica estraga o estado; guarda que para, nao."""
    for k in range(tentativas):
        a, _ = nav.captura("/tmp/_c1_fis0.png")
        txt = " ".join(t for t, *_ in rs.ocr_forte(a, psm="6")).lower()
        if "collision shape" in txt:
            return True                       # ja estou na fisica
        if "edit sprite" not in txt:
            # o painel pode so nao ter sido lido: insisto em vez de abortar
            time.sleep(1.2)
            continue
        # A FAIXA A DIREITA DO OK — do OK DAQUELE painel, nao de um pedaco
        # fixo da tela. Dois motivos:
        #  - o azul do link (108,170,233) e quase o do botao OK (126,168,224),
        #    e procurando na largura toda a media das duas manchas caia em
        #    cima do OK, que ao ser clicado FECHA o painel;
        #  - e o painel nasce do lado da casa clicada: para a lava, que fica
        #    no canto de baixo a esquerda, ele abre a ESQUERDA, e uma regiao
        #    fixa na direita da tela nao o alcanca.
        from PIL import Image as _I
        L, A_ = _I.open(a).size
        ok = nav.acha_cor(AZUL_OK, tol=40, regiao=(0.0, 0.3, 1.0, 0.98),
                          minimo=800, arquivo=a)
        p = None
        if ok:
            # DEPOIS da borda direita do OK, nao a partir do meio dele.
            # Medido: o OK vai de x=652 a 955 com 23.932 pixels azuis; o link
            # sao oito manchinhas de letra entre 1120 e 1224, somando 597. Uma
            # faixa que comece dentro do OK afoga o link na media.
            borda = ok[0] + ok[2] // 2 + 60
            faixa = (min(0.99, borda / L), max(0.0, (ok[1] - 70) / A_),
                     min(1.0, (borda + 560) / L), min(1.0, (ok[1] + 70) / A_))
            p = nav.acha_cor(LINK_FISICA, tol=34, regiao=faixa,
                             minimo=200, arquivo=a)
        if not p:
            p = nav.acha_texto("physics", arquivo=a)
        if p:
            clique(p[0], p[1]); time.sleep(2.5)
            a2, _ = nav.captura("/tmp/_c1_fis1.png")
            if "collision shape" in " ".join(
                    t for t, *_ in rs.ocr_forte(a2, psm="6")).lower():
                # devolve o PONTO, para quem grava o clipe apontar a seta nele
                return (int(p[0]), int(p[1]))
        time.sleep(1.2)
    raise RuntimeError("nao achei o `Physics >` no painel do objeto")


# ─────────────────────────── sprites de verdade ───────────────────────────
#
# Ate a Aula 3 todo objeto era um QUADRADO PINTADO com a latinha. Funcionava e
# era facil de medir, mas um jogo de quadrados azuis nao motiva ninguem de 10
# anos — e o Flowlab tem sete bibliotecas de sprite embutidas:
#
#   Flowlab Sprites (ENDESGA)  Blocks · Characters · Objects · Terrain · Town
#   Kenney Sprites             1 Bit · 1 Bit Platformer · Tiny Dungeon · …
#   Sproutland (Cupnooble)     Animals · Characters · Farming · Terrain · …
#   Sodacoma · Gustavo (Ships · Projectiles · Misc.) · PixelPizza UI · Cute Planet
#
# O gesto e: `Browse` → `< Menu` → pacote → sub-pacote → clicar no boneco.
#
# A LISTA SE REORGANIZA conforme o pacote aberto, entao pacote e sub-pacote se
# acham pelo TEXTO. So a grade de bonecos e por coordenada, e ela e regular.

GRADE_SPRITE = (2307, 180, 87, 85)      # x0, y0, passo em x, passo em y


def _botao_menu():
    """O `< Menu` azul no alto da coluna da direita."""
    return nav.acha_cor((122, 170, 224), tol=45, regiao=(0.72, 0.02, 0.95, 0.10),
                        minimo=600)


def _subpacotes(abaixo, cor=(122, 170, 224), tol=45):
    """Os botoes azuis de sub-pacote que ficam ABAIXO do nome do pacote,
       de cima para baixo. Devolve os centros."""
    import numpy as _np
    from PIL import Image as _I
    a, _ = nav.captura("/tmp/_sp_sub.png")
    _ = rs
    im = _np.asarray(_I.open(a).convert("RGB"), dtype=int)
    rec = im[:, 2300:2700]
    m = ((abs(rec[:, :, 0] - cor[0]) < tol) & (abs(rec[:, :, 1] - cor[1]) < tol) &
         (abs(rec[:, :, 2] - cor[2]) < tol))
    linhas = m.sum(axis=1)
    faixas, ini = [], None
    for y, n_ in enumerate(list(linhas) + [0]):
        if n_ > 150 and ini is None:
            ini = y
        elif n_ <= 150 and ini is not None:
            if 30 <= (y - ini) <= 90 and ini > abaixo:
                faixas.append((ini + y) // 2)
            ini = None
    # o NOME de cada botao: texto BRANCO sobre azul claro, que o OCR comum nao
    # le. Binarizo guardando so o muito claro e leio uma linha de cada vez.
    im_rgb = _I.open(a).convert("L")
    saida = []
    for y in faixas:
        rec = _np.asarray(im_rgb.crop((2320, y - 22, 2680, y + 22)), dtype=int)
        bn = _I.fromarray(_np.where(rec > 225, 0, 255).astype("uint8"), "L")
        bn = bn.resize((bn.width * 2, bn.height * 2), _I.LANCZOS)
        bn.save("/tmp/_sp_nome.png")
        nome = " ".join(t for t, *_ in rs.ocr("/tmp/_sp_nome.png", psm="7",
                                              escala=1, idioma="eng")).strip()
        saida.append((nome, (2500, y)))
    return saida


def abre_grade_sprite(pacote, subpacote):
    """Navega ate a grade de bonecos de um sub-pacote. NAO escolhe nada.

       Existe separado de `escolhe_sprite` por causa do CLIPE: o gesto inteiro
       atravessa quatro telas (Browse, Menu, pacote, sub-pacote), e um clipe e
       um par antes-e-depois — a seta apontaria para um lugar que nao existe
       em nenhum dos dois quadros. Entao a aula grava so o clique final, com a
       grade ja aberta, que e o que a crianca precisa ver."""
    def _na_tela(alvo):
        c, _ = nav.captura("/tmp/_sp_c.png")
        return nav.acha_texto(alvo.lower(), arquivo=c, regiao=(0.72, 0.0, 1.0, 1.0))

    if not _na_tela(pacote):
        a, _ = nav.captura("/tmp/_sp_b.png")
        b = nav.acha_texto("browse", arquivo=a)
        if b:
            clique(*b); time.sleep(3)
        m = _botao_menu()
        if m:
            clique(m[0], m[1]); time.sleep(3)

    # CLICAR NUM PACOTE JA ABERTO O FECHA: clico e confiro se os sub-pacotes
    # apareceram; se nao, clico de novo.
    botoes = []
    for _ in range(3):
        p = _na_tela(pacote)
        if not p:
            raise RuntimeError(f"nao achei `{pacote}` na biblioteca de sprites")
        botoes = _subpacotes(abaixo=p[1])
        if botoes:
            break
        clique(*p); time.sleep(3.5)
    if isinstance(subpacote, int):
        if subpacote >= len(botoes):
            raise RuntimeError(f"`{pacote}` mostrou {len(botoes)} sub-pacotes e "
                               f"eu queria o {subpacote + 1}o")
        alvo = botoes[subpacote][1]
    else:
        casa = [pt for nome, pt in botoes if subpacote.lower()[:6] in nome.lower()]
        if not casa:
            raise RuntimeError(f"`{subpacote}` nao esta em `{pacote}` — ha "
                               f"{[n for n, _ in botoes]}")
        alvo = casa[0]
    clique(*alvo); time.sleep(3.5)
    return True


def clica_sprite(linha, coluna):
    """Clica num boneco da grade ja aberta e CONFERE que o desenho mudou.
       Devolve o ponto do clique — e ele que a seta do clipe aponta."""
    import numpy as _np
    from PIL import Image as _I
    antes, _ = nav.captura("/tmp/_sp_antes.png")
    x0, y0, px, py = GRADE_SPRITE
    ponto = (x0 + px * coluna, y0 + py * linha)
    clique(*ponto); time.sleep(2.5)
    dep, _ = nav.captura("/tmp/_sp_dep.png")
    A_ = _np.asarray(_I.open(antes).convert("RGB"), dtype=int)
    B_ = _np.asarray(_I.open(dep).convert("RGB"), dtype=int)
    tela = (slice(300, 1300), slice(900, 2000))
    if int((_np.abs(A_[tela] - B_[tela]).sum(axis=2) > 40).sum()) < 2000:
        raise RuntimeError(f"cliquei no sprite ({linha},{coluna}) e o desenho "
                           "nao mudou — ja era esse?")
    return ponto


def escolhe_sprite(pacote, subpacote, linha, coluna, tentativas=3):
    """O gesto inteiro: navegar ate a grade e escolher o boneco."""
    abre_grade_sprite(pacote, subpacote)
    return clica_sprite(linha, coluna)


def cor_dominante(arquivo, tela=(slice(300, 1300), slice(900, 2000))):
    """A cor que mais aparece no desenho, ignorando o xadrez de transparencia
       e os cinzas da interface. E por ela que a prova acha o objeto no jogo."""
    import numpy as _np
    from PIL import Image as _I
    im = _np.asarray(_I.open(arquivo).convert("RGB"), dtype=int)[tela]
    px = im.reshape(-1, 3)
    # fora o xadrez (cinzas quase iguais nos tres canais) e o quase-preto
    vivo = ((px.max(axis=1) - px.min(axis=1)) > 40) & (px.max(axis=1) > 60)
    px = px[vivo]
    if len(px) < 200:
        return None
    # agrupa grosso, em caixas de 32, e devolve a caixa mais cheia
    chave = (px // 32) * 32
    vistos = {}
    for c in map(tuple, chave):
        vistos[c] = vistos.get(c, 0) + 1
    melhor = max(vistos.items(), key=lambda kv: kv[1])[0]
    dentro = px[(chave == melhor).all(axis=1)]
    return tuple(int(v) for v in dentro.mean(axis=0))


def cores_do_sprite(arquivo, quantas=5, tela=(slice(300, 1300), slice(900, 2000))):
    """As cores mais presentes no desenho, da mais comum para a menos.

       `cor_dominante` devolve so a primeira, e as vezes ela nao serve para
       RASTREAR: o heroi do ENDESGA tem mais pele que camisa, e pele puxa para
       o mesmo tom da moeda de ouro. Com a lista, quem monta a aula escolhe uma
       cor que nao se confunda com a dos vizinhos."""
    import numpy as _np
    from PIL import Image as _I
    im = _np.asarray(_I.open(arquivo).convert("RGB"), dtype=int)[tela]
    px = im.reshape(-1, 3)
    vivo = ((px.max(axis=1) - px.min(axis=1)) > 40) & (px.max(axis=1) > 60)
    px = px[vivo]
    if len(px) < 200:
        return []
    chave = (px // 32) * 32
    contas = {}
    for c in map(tuple, chave):
        contas[c] = contas.get(c, 0) + 1
    saida = []
    for caixa, _n in sorted(contas.items(), key=lambda kv: -kv[1])[:quantas]:
        dentro = px[(chave == caixa).all(axis=1)]
        saida.append(tuple(int(v) for v in dentro.mean(axis=0)))
    return saida


def distantes(cores, minimo=90):
    """As cores de rastreio sao distinguiveis entre si?

       Guarda, nao suposicao: se dois objetos da fase tiverem cores parecidas,
       a prova em jogo acha um pensando que achou o outro — e o numero sai
       bonito e errado."""
    for i, a in enumerate(cores):
        for b in cores[i + 1:]:
            if a is None or b is None:
                return False
            if sum(abs(x - y) for x, y in zip(a, b)) < minimo:
                return False
    return True


def mascara_cor(im, cor, tol=46):
    """Mascara dos pixels proximos de uma cor. `im` e array RGB inteiro."""
    return ((abs(im[:, :, 0] - cor[0]) < tol) &
            (abs(im[:, :, 1] - cor[1]) < tol) &
            (abs(im[:, :, 2] - cor[2]) < tol))


def acha_por_cor(arquivo, cor, tol=46, minimo=600):
    """(x, y, tamanho) da MAIOR mancha daquela cor, ou None."""
    import numpy as _np
    from PIL import Image as _I
    im = _np.asarray(_I.open(arquivo).convert("RGB"), dtype=int)
    g = maior_mancha(mascara_cor(im, cor, tol))
    return g if g and g[2] >= minimo else None


def centro_por_cor(arquivo, cor, tol=46, minimo=60):
    """O centro de TODOS os pixels daquela cor, nao o da maior mancha.

       Com quadrado pintado, o objeto era uma mancha so de 4096 px. Com sprite
       de verdade ele e pequeno e PARTIDO: a camisa do heroi sao 192 px em
       pedacos de 80. Exigir mancha unica fazia a prova dizer que o boneco nao
       estava na tela quando ele estava."""
    import numpy as _np
    from PIL import Image as _I
    im = _np.asarray(_I.open(arquivo).convert("RGB"), dtype=int)
    m = mascara_cor(im, cor, tol)
    ys, xs = _np.nonzero(m)
    if len(xs) < minimo:
        return None
    return (int(xs.mean()), int(ys.mean()), int(len(xs)))
