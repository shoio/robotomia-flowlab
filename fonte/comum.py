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
        devolvido = acao()
        if isinstance(devolvido, (tuple, list)) and len(devolvido) == 2:
            alvo = devolvido
        time.sleep(espera)
        nav.espera_parar(limite=15)
        b = A.cap(base + "_b")
        A.reg(chave, antes=a, depois=b, alvo=[int(alvo[0]), int(alvo[1])], botao=botao)
        return b


def clique(x, y, duplo=False):
    """Todo clique da aula passa pelo guarda: acima da pagina esta o Chrome."""
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


def confere_fase():
    """Olha o nivel e confere que a fase FAZ SENTIDO antes de jogar:
       chao contiguo, e jogador e moeda EM CIMA dele, na mesma linha.

       Nasceu de uma fase que parecia pronta na foto e nao era: metade das
       pecas de chao nao tinha sido colocada, o jogador ficou no ar a esquerda
       do chao, e o jogo 'nao funcionava' sem que nada no editor acusasse."""
    from PIL import Image
    import numpy as np
    # tira o ponteiro da area do nivel: o Flowlab desenha uma CAIXINHA LARANJA
    # na celula sob o cursor, e ela entrava na conta como se fosse a moeda
    import Quartz
    J = nav.janela()
    rs._evento_mouse(Quartz.kCGEventMouseMoved, J["x"] + 60, J["y"] + 700)
    time.sleep(0.8)
    a, _ = nav.captura("/tmp/_fase.png")
    # SO a area do nivel: a interface do Flowlab tem azul e amarelo proprios, e
    # ler a janela inteira deu um 'jogador' de 1500 px de largura
    im = np.asarray(Image.open(a).convert("RGB"), dtype=int)
    im = im[GRADE_Y:GRADE_Y + CELULA * 12, GRADE_X:GRADE_X + CELULA * 16]
    verde = (im[:, :, 1] > 140) & (im[:, :, 1] - im[:, :, 0] > 40) & (im[:, :, 2] < 130)
    azul = (im[:, :, 2] > 100) & (im[:, :, 2] - im[:, :, 0] > 40) & (im[:, :, 1] < 120)
    amar = (im[:, :, 0] > 190) & (im[:, :, 1] > 130) & (im[:, :, 1] < 210) & (im[:, :, 2] < 120)
    def caixa(m, nome):
        ys, xs = np.nonzero(m)
        if len(xs) < 200:
            raise RuntimeError(f"a fase nao tem {nome} (achei {len(xs)} px)")
        return xs.min() + GRADE_X, xs.max() + GRADE_X, ys.min() + GRADE_Y, ys.max() + GRADE_Y
    cx0, cx1, cy0, cy1 = caixa(verde, "chao")
    jx0, jx1, jy0, jy1 = caixa(azul, "jogador")
    mx0, mx1, my0, my1 = caixa(amar, "moeda")
    largura_esperada = CELULA * len(COLS_CHAO)
    problemas = []
    if (cx1 - cx0) < largura_esperada * 0.9:
        problemas.append(f"o chao tem {cx1-cx0} px e devia ter ~{largura_esperada} "
                         f"({len(COLS_CHAO)} pecas): faltou peca")
    if not (cx0 <= jx0 and jx1 <= cx1):
        problemas.append(f"o jogador (x {jx0}..{jx1}) nao esta sobre o chao "
                         f"(x {cx0}..{cx1}): ele vai cair")
    if not (cx0 <= mx0 and mx1 <= cx1):
        problemas.append(f"a moeda (x {mx0}..{mx1}) nao esta sobre o chao")
    if abs(jy1 - my1) > CELULA // 2:
        problemas.append(f"jogador e moeda em linhas diferentes "
                         f"(base {jy1} contra {my1}): ele passa por baixo")
    if problemas:
        raise RuntimeError("a fase esta torta:\n  - " + "\n  - ".join(problemas))
    print(f"   fase conferida: chao {cx0}..{cx1}, jogador {jx0}, moeda {mx0}", flush=True)
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
                return True
        time.sleep(1.2)
    raise RuntimeError("nao achei o `Physics >` no painel do objeto")
