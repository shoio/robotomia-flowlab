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


def folha_do_nivel(arquivo=None, minimo=400):
    """(x0, x1, y0, y1) da folha do nivel — a area da TELA — medida na tela.

       NAO pela cor dela. A primeira versao procurava BRANCO, e funcionou ate o
       dia em que a aula passou a pintar o ceu: a folha virou azul e a regua
       disse que nao havia folha nenhuma. Regua que depende da cor do que mede
       quebra no dia em que a cor vira conteudo.

       O invariante que ficou: a folha e tudo o que NAO e o xadrez escuro do
       fundo do editor. O xadrez eu leio do proprio canto de cima a esquerda,
       que nunca tem folha — entao a referencia se mede a cada foto, em vez de
       ser um numero meu.

       Tambem ignoro a barra de baixo (os botoes Play/Library/...), que e
       escura mas nao e xadrez."""
    import numpy as _np
    from PIL import Image as _I
    a = arquivo or nav.captura("/tmp/_folha.png")[0]
    im = _np.asarray(_I.open(a).convert("RGB"), dtype=int)
    alt = im.shape[0]
    canto = im[0:140, 0:140].reshape(-1, 3)        # xadrez puro
    lo, hi = canto.min(axis=0) - 12, canto.max(axis=0) + 12
    fundo = ((im >= lo) & (im <= hi)).all(axis=2)
    nao_fundo = ~fundo
    nao_fundo[int(alt * 0.93):, :] = False         # a barra de baixo fica fora
    if nao_fundo.sum() < 5000:
        return None
    porfila = nao_fundo.sum(axis=1)
    porcol = nao_fundo.sum(axis=0)
    lim_f = max(minimo * 0.25, porfila.max() * 0.3)
    lim_c = max(minimo * 0.25, porcol.max() * 0.3)
    ys = _np.nonzero(porfila >= lim_f)[0]
    xs = _np.nonzero(porcol >= lim_c)[0]
    if not len(ys) or not len(xs):
        return None
    return int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())


def enquadra_nivel(colunas=16, linhas=12, giros=8):
    """Afasta o zoom ate a folha INTEIRA caber na janela, e calibra a grade.

       O editor de nivel do Flowlab nao tem a ferramenta mao — ela e do editor
       de blocos — e a roda do mouse da ZOOM, nao rolagem. Entao o jeito de
       alcancar a coluna 40 de um nivel de 48 e afastar ate tudo caber.

       Qualquer coisa pode devolver o zoom ao padrao (um `Esc` basta), por isso
       isto e uma peca e nao um passo solto: quem precisa da grade chama aqui,
       e recebe uma grade MEDIDA no enquadramento de agora."""
    for k in range(giros):
        try:
            return calibra_grade(colunas, linhas)
        except RuntimeError:
            nav.rola(1470, 900, 0, 400)
            time.sleep(1.0)
    return calibra_grade(colunas, linhas)      # a ultima tentativa fala por si


def calibra_grade(colunas=16, linhas=12):
    """MEDE a grade do nivel na tela em vez de supor 64 px por casa.

       Por que: `GRADE_X/GRADE_Y/CELULA` nasceram cravados do nivel padrao de
       16x12. O Flowlab permite ate 48x32, e com o zoom afastado para alcancar
       as colunas de la o 64 deixa de valer — e clique fora da casa nao da
       erro, so nao faz nada. Foi assim que o passo da grade de sprites (85
       supostos contra 89 medidos) deixou a estrela da Aula 2 com o desenho
       padrao do Flowlab.

       A regua e a LARGURA da folha branca, nao a altura. A primeira versao
       usava as duas e exigia que concordassem: numa fase com lava na fileira
       de baixo elas nao concordam, porque a lava TAPA o branco — a altura deu
       59,6 px por fileira contra 63,9 da largura, a tolerancia deixou passar
       raspando, e a media saiu 62. Objeto que encosta na beirada de baixo e o
       caso normal, nao a excecao; ja na horizontal as fases comecam e terminam
       com ceu.

       A guarda que ficou no lugar e outra, e essa e invariante: as duas
       beiradas brancas tem de estar DENTRO da janela. Encostada na borda, a
       folha esta cortada, e dividir a largura visivel pelo numero de colunas
       da um numero menor — bonito e errado.

       Devolve (x0, y0, lado) e deixa `celula` calibrada."""
    global GRADE_X, GRADE_Y, CELULA
    f = folha_do_nivel()
    if not f:
        raise RuntimeError("nao achei a folha branca do nivel na tela")
    x0, x1, y0, _y1 = f
    J = nav.janela()
    larga = J["w"] * 2
    if x0 <= 2 or x1 >= larga - 3:
        raise RuntimeError(
            f"a folha branca vai de {x0} a {x1} numa tela de {larga} px: ela "
            "esta CORTADA pela janela, e a medida nao vale (afaste o zoom)")
    lado = (x1 - x0) / float(colunas)
    GRADE_X, GRADE_Y, CELULA = x0, y0, int(round(lado))
    return GRADE_X, GRADE_Y, CELULA



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
        # ÂNCORA NUM TEXTO QUE O OCR LÊ, e nao na cor do botao OK.
        #
        # A cor parou de servir no dia em que a aula passou a pintar o CEU: o
        # azul do ceu fica a 38 do azul do OK, dentro da tolerancia 40, e o
        # "OK" que o detector achava era um pedaco de ceu de 431x229 px (o
        # botao tem 303x60). Pus um teto de tamanho e nem assim — o pedaco
        # cabia no teto. Cor que distinguia deixou de distinguir porque a
        # aula ganhou uma cor nova, e nenhuma tolerancia conserta isso.
        #
        # `Multiplayer` e o rotulo legivel mais proximo do link: medido, o
        # `Physics >` fica 190 px abaixo e 85 px a direita dele. `Display
        # Order` serve de reserva, do outro lado da mesma fileira.
        for rotulo, (dx, dy) in (("multiplayer", (85, 190)),
                                 ("display order", (475, 190))):
            anc = _acha_no_painel(rotulo, a)
            if anc:
                p = (anc[0] + dx, anc[1] + dy)
                break
        else:
            p = None
        if p:
            clique(p[0], p[1]); time.sleep(2.5)
            a2, _ = nav.captura("/tmp/_c1_fis1.png")
            if "collision shape" in " ".join(
                    t for t, *_ in rs.ocr_forte(a2, psm="6")).lower():
                return (int(p[0]), int(p[1]))
            time.sleep(1.0)
            continue

        from PIL import Image as _I
        L, A_ = _I.open(a).size
        # `maximo`: o OK tem ~24 mil pixels azuis. Desde que a aula pinta o
        # CEU, o fundo do nivel e azul tambem — 786 mil pixels a 38 de
        # distancia do OK, dentro da tolerancia. Sem o teto, o "OK" encontrado
        # era o ceu, e a faixa onde eu procuro o `Physics >` ia parar longe.
        ok = nav.acha_cor(AZUL_OK, tol=40, regiao=(0.0, 0.3, 1.0, 0.98),
                          minimo=800, maximo=120000, arquivo=a)
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

GRADE_SPRITE = (2307, 180, 87, 89)      # x0, y0, passo em x, passo em y


def linhas_da_grade():
    """As alturas REAIS das fileiras de bonecos, medidas na tela.

       O passo que eu supunha (85 px) estava errado por 4 px, e o erro
       acumula: na nona fileira o clique caia no VAO entre duas, nao aplicava
       nada — e a estrela da Aula 2 ficou com o desenho padrao do Flowlab sem
       ninguem perceber. Medir cada corrida custa uma captura e nao erra."""
    import numpy as _np
    from PIL import Image as _I
    a, _ = nav.captura("/tmp/_sp_grade.png")
    im = _np.asarray(_I.open(a).convert("RGB"), dtype=int)[:, 2270:2680]
    fundo = _np.median(im.reshape(-1, 3), axis=0)
    m = (_np.abs(im - fundo).sum(axis=2) > 60)
    conta = m.sum(axis=1)
    faixas, ini = [], None
    for i, n in enumerate(list(conta) + [0]):
        if n > 12 and ini is None:
            ini = i
        elif n <= 12 and ini is not None:
            if i - ini > 15:
                faixas.append((ini + i) // 2)
            ini = None
    # a primeira faixa pode ser o botao `< Menu`, acima da grade
    return [y for y in faixas if y >= GRADE_SPRITE[1] - 20]


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


def clica_sprite(linha, coluna, exige_mudanca=True):
    """Clica num boneco da grade ja aberta e CONFERE que o desenho mudou.
       Devolve o ponto do clique — e ele que a seta do clipe aponta.

       `exige_mudanca=False` para quando a captura esta sendo RETOMADA: o
       objeto ja pode ter o desenho certo da corrida anterior, e ai nada muda.
       Para gravar CLIPE o padrao vale — um clipe cujo antes e igual ao depois
       e uma figura parada."""
    import numpy as _np
    from PIL import Image as _I
    antes, _ = nav.captura("/tmp/_sp_antes.png")
    x0, y0, px, py = GRADE_SPRITE
    ys = linhas_da_grade()
    # a altura MEDIDA da fileira, quando ela existe; o passo suposto so como
    # reserva
    cy = ys[linha] if linha < len(ys) else y0 + py * linha
    ponto = (x0 + px * coluna, cy)
    clique(*ponto); time.sleep(2.5)
    dep, _ = nav.captura("/tmp/_sp_dep.png")
    A_ = _np.asarray(_I.open(antes).convert("RGB"), dtype=int)
    B_ = _np.asarray(_I.open(dep).convert("RGB"), dtype=int)
    tela = (slice(300, 1300), slice(900, 2000))
    if int((_np.abs(A_[tela] - B_[tela]).sum(axis=2) > 40).sum()) < 2000:
        if exige_mudanca:
            raise RuntimeError(f"cliquei no sprite ({linha},{coluna}) e o "
                               "desenho nao mudou — ja era esse?")
        print(f"   (o sprite ({linha},{coluna}) ja era esse)", flush=True)
    return ponto


def escolhe_sprite(pacote, subpacote, linha, coluna, tentativas=3):
    """O gesto inteiro: navegar ate a grade e escolher o boneco."""
    abre_grade_sprite(pacote, subpacote)
    try:
        return clica_sprite(linha, coluna)
    except RuntimeError:
        # Nao mudou. Pode ser que o objeto JA tivesse esse desenho (retomada)
        # — ou que eu tenha clicado na celula errada. Aceitar calado esconde o
        # segundo caso: foi assim que a estrela saiu bege e eu so descobri
        # quando a prova em jogo nao achou amarelo nenhum.
        # Entao: ponho o vizinho, volto ao alvo, e EXIJO a mudanca.
        clica_sprite(linha, coluna + 1, exige_mudanca=False)
        time.sleep(0.8)
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


def cor_de_rastreio(cores, quem, tols=(46, 34, 25, 18)):
    """(cor, tolerancia) com que achar `quem` sem achar os vizinhos.

       `cores` e o {nome: [cor, ...]} medido na hora de escolher os sprites, da
       cor mais comum para a menos. Devolve tambem a TOLERANCIA porque ela faz
       parte da resposta: a mesma cor serve ou nao conforme a folga.

       O criterio e exato, nao um numero escolhido a dedo. Duas mascaras com
       tolerancia `tol` so podem pegar o mesmo pixel se as duas cores estiverem
       a menos de `2*tol` em TODOS os canais. Entao a cor serve quando existe
       pelo menos um canal em que ela esta a `2*tol` ou mais de cada cor dos
       outros atores. Somar os tres canais — que era o que eu fazia — responde
       outra pergunta: (255,235,97) e (254,176,49) somam 108 de distancia e
       MESMO ASSIM dividem pixels, porque nenhum canal sozinho abre folga.

       Por que isto existe: a lava do Flowlab tem respingos DOURADOS de
       (254,176,49) e a estrela e (255,181,44) — a mesma cor. A guarda velha
       comparava so a PRIMEIRA cor de cada sprite, viu (255,181,44) contra
       (255,0,66) e aprovou. A sonda entao "procurava a estrela" e media a
       LAVA, no pe da tela, descendo junto com ela — e a fase nunca podia ser
       dada por vencida, porque a lava nunca sai de cena.

       Duas outras exigencias, que tambem ja custaram caro:
       - ABUNDANTE: pegar a mais distante escolheu um ciano de uma duzia de
         pixels, e o pulo mediu 50 px em vez de 428. Por isso percorro na
         ordem em que vieram, da mais comum para a menos.
       - VIVA: cor de tom medio casa com cinza, e quando o Flowlab escurece o
         jogo a pagina inteira vira "boneco"."""
    minhas = [tuple(c) for c in cores.get(quem, [])]
    if not minhas:
        raise RuntimeError(f"nao tenho cor nenhuma de `{quem}`")
    outras = [tuple(c) for nome, lista in cores.items() if nome != quem
              for c in lista]

    def folga(c):
        """O menor, entre os vizinhos, do MAIOR afastamento de canal."""
        return min((max(abs(a - b) for a, b in zip(c, o)) for o in outras),
                   default=999)

    for tol in tols:                       # da folga mais generosa para a menor
        for c in minhas:                   # da cor mais comum para a menos
            if (max(c) - min(c)) >= 40 and folga(c) >= 2 * tol:
                return c, tol
    raise RuntimeError(
        f"nenhuma cor de `{quem}` se separa das dos vizinhos nem com "
        f"tolerancia {tols[-1]}: "
        + ", ".join(f"{c} (folga {folga(c)})" for c in minhas))


def mascara_cor(im, cor, tol=46):
    """Mascara dos pixels proximos de uma cor. `im` e array RGB inteiro.

       Alem da distancia canal a canal, o pixel tem de ser tao COLORIDO quanto
       o alvo. Sem isso, uma cor de tom medio casa com CINZA: a pele do heroi
       e (234,179,146), e um cinza (190,190,190) cai dentro de 46 nos tres
       canais. Quando o Flowlab escurece o jogo (ele faz isso quando a pagina
       perde o foco), a pagina inteira vira esse cinza — e a sonda que
       procurava o boneco achou 667.424 pixels dele, contra 432 com o jogo
       aceso. Dai ela concluiu que a crianca tinha pegado a estrela, com a
       estrela visivel na propria foto que guardou como prova.

       A regra: a diferenca entre o canal mais alto e o mais baixo do pixel tem
       de ser pelo menos METADE da do alvo. Para um alvo que ja e cinza, a
       exigencia e zero e nada muda."""
    perto = ((abs(im[:, :, 0] - cor[0]) < tol) &
             (abs(im[:, :, 1] - cor[1]) < tol) &
             (abs(im[:, :, 2] - cor[2]) < tol))
    viva = max(cor) - min(cor)
    if viva < 20:
        return perto
    return perto & ((im.max(axis=2) - im.min(axis=2)) >= viva // 2)


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


def clica_sprite_por_cor(cor, tol=60, minimo=150):
    """Clica no boneco da grade que tem MAIS daquela cor.

       Contar linha e coluna no olho erra: a grade rola, e um clique entre
       celulas nao aplica nada — a estrela ficou com o desenho PADRAO do
       Flowlab (o losango bege) e eu so descobri quando a prova em jogo nao
       achou amarelo. Aqui o alvo e medido na propria grade."""
    import numpy as _np
    from PIL import Image as _I
    antes, _ = nav.captura("/tmp/_sp_antes.png")
    im = _np.asarray(_I.open(antes).convert("RGB"), dtype=int)
    x0, y0, px, py = GRADE_SPRITE
    melhor = None
    for lin in range(16):
        for col in range(4):
            cx, cy = x0 + px * col, y0 + py * lin
            if cy + 30 >= im.shape[0] or cx + 30 >= im.shape[1]:
                continue
            rec = im[cy - 30:cy + 30, cx - 30:cx + 30]
            n = int(mascara_cor(rec, cor, tol).sum())
            if n >= minimo and (melhor is None or n > melhor[0]):
                melhor = (n, cx, cy, lin, col)
    if not melhor:
        raise RuntimeError(f"nenhum boneco da grade tem a cor {cor}")
    n, cx, cy, lin, col = melhor
    print(f"   boneco com {cor}: linha {lin} coluna {col} ({n} px)", flush=True)
    clique(cx, cy); time.sleep(2.5)
    dep, _ = nav.captura("/tmp/_sp_dep.png")
    A_ = _np.asarray(_I.open(antes).convert("RGB"), dtype=int)
    B_ = _np.asarray(_I.open(dep).convert("RGB"), dtype=int)
    tela = (slice(300, 1300), slice(900, 2000))
    if int((_np.abs(A_[tela] - B_[tela]).sum(axis=2) > 40).sum()) < 2000:
        raise RuntimeError(f"cliquei no boneco de cor {cor} e o desenho nao mudou")
    return (cx, cy)
