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
    for _ in range(3):
        p = nav.acha_cor(AZUL_OK, tol=40, regiao=(0.45, 0.45, 0.9, 0.98), minimo=800)
        alvo = (p[0], p[1]) if p else OK_PAINEL
        clique(*alvo)
        time.sleep(1.8); nav.espera_parar(limite=12)
        a, _ = nav.captura("/tmp/_c1_ok.png")
        if "edit sprite" not in " ".join(t for t, *_ in rs.ocr_forte(a, psm="6")).lower():
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


def marca_caixa(rotulo, quero=True):
    """Marca/desmarca uma caixinha do painel, achando-a pelo ROTULO.

       O painel do objeto MUDA de posicao na tela conforme o objeto e o que
       esta aberto; coordenada fixa aqui ja deixou 'movable' desmarcado sem
       ninguem notar — e com ele desmarcado a Densidade fica desabilitada, o
       jogador corre e a moeda nao some. Conferido pela COR da caixinha."""
    from PIL import Image
    for tentativa in range(3):
        a, _ = nav.captura("/tmp/_c1_caixa.png")
        p = nav.acha_texto(rotulo.lower(), arquivo=a, regiao=(0.45, 0.1, 1.0, 0.85))
        if not p:
            raise RuntimeError(f"nao achei a caixinha '{rotulo}' no painel")
        cx, cy = p[0] - 90, p[1]
        cor = Image.open(a).convert("RGB").getpixel((cx, cy))
        marcada = cor[2] > 150 and cor[2] - cor[0] > 40
        if marcada == quero:
            return True
        clique(cx, cy)
        time.sleep(1.0)
    raise RuntimeError(f"nao consegui deixar '{rotulo}' como {quero}")


def arrasta_slider(rotulo, ate_direita=True):
    """Arrasta um controle deslizante do painel de fisica ate a ponta.
       Acha pela ETIQUETA (Density, Friction) porque o painel MUDA de altura:
       marcar 'movable' faz nascer uma linha nova e empurra tudo para baixo."""
    a, _ = nav.captura("/tmp/_c1_slider.png")
    p = nav.acha_texto(rotulo.lower(), arquivo=a, regiao=(0.45, 0.1, 1.0, 0.85))
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


