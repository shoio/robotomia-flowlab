#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Captura da Aula 1 — Pega-moedas.

   O jogo: um boneco que corre num chao, e uma moeda que some quando ele
   encosta. Termina jogavel, com link para mandar para a familia.

   Cada gesto que a aula pede fica registrado em `alvos.json` com o PONTO do
   clique e QUAL BOTAO — e dai sai a animacao com o mouse do botao aceso.

   Medidas da tela (pagina em 100%):
   - a area do nivel comeca em (958, 415) e cada celula tem 64 px;
   - o OK do painel do objeto e branco sobre AZUL (o OCR nao le) e muda de
     altura quando o Physics esta aberto: acha-se pela cor."""
import os, sys, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rs, nav, editor, blocos

D = "aula1"
ALVOS = os.path.join(D, "alvos.json")

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
PALETA = {"azul": (2786, 535), "amarelo": (2786, 390), "verde": (2700, 460)}
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
        tudo = json.load(open(ALVOS)) if os.path.exists(ALVOS) else {}
        tudo[chave] = kw
        json.dump(tudo, open(ALVOS, "w"), indent=1, ensure_ascii=False)
        print(f"   clipe {chave}", flush=True)

    @staticmethod
    def gesto(chave, base, alvo, acao, botao="esq", espera=1.6):
        """Captura ANTES, faz o gesto, captura DEPOIS e registra o par."""
        a = A.cap(base + "_a")
        acao()
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
    p = nav.acha_texto("name", arquivo=a, regiao=(0.55, 0.15, 1.0, 0.6))
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


@etapa
def novo():
    A.url = editor.jogo_novo()
    print("   jogo:", A.url, flush=True)
    A.cap("p01_vazio")
    return True


@etapa
def jogador():
    x, y = celula(COL_JOGADOR, LINHA_ANDAR)
    A.gesto("criar_objeto", "g01", (x, y), lambda: clique(x, y), espera=1.5)
    a, _ = nav.captura("/tmp/_rad.png")
    p = nav.acha_texto("create", arquivo=a)
    A.gesto("escolher_create", "g02", p, lambda: clique(*p), espera=3)
    editor.espera_tela("behaviors", limite=20)
    A.cap("p02_painel")
    nomeia("Jogador")
    A.cap("p03_nome")
    abre_sprite()
    A.cap("p04_sprite")
    pinta("azul")
    A.cap("p05_azul")
    clique(*SPRITE_OK); time.sleep(2); nav.espera_parar(limite=15)
    a, _ = nav.captura("/tmp/_fis.png")
    q = nav.acha_texto("physics", arquivo=a)
    A.gesto("abrir_physics", "g03", q, lambda: clique(*q), espera=2.5)
    A.gesto("marcar_movable", "g04", (1681, 476),
            lambda: marca_caixa("movable", True), espera=1.2)
    A.cap("p06_movable")
    fecha_painel_objeto()
    A.cap("p07_jogador_pronto")
    return True


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


@etapa
def peso():
    """Deixa o jogador PESADO. Sem isto ele corre 180 px por quadro e atravessa
       a moeda sem a fisica registrar contato: a moeda nao some e nada no
       editor acusa. Medido: com densidade e friccao no maximo o passo cai
       para 52 px e a colisao vale."""
    x, y = celula(COL_JOGADOR, LINHA_ANDAR)
    editor.objeto_ou_abre(x, y)
    a, _ = nav.captura("/tmp/_c1_fis.png")
    q = nav.acha_texto("physics", arquivo=a)
    A.gesto("abrir_physics2", "g07", q, lambda: clique(*q), espera=2.5)
    marca_caixa("movable", True)      # sem isto a Densidade fica desabilitada
    arrasta_slider("density")
    A.cap("p21_densidade")
    arrasta_slider("friction")
    A.cap("p22_friccao")
    fecha_painel_objeto()
    return True


@etapa
def movimento():
    x, y = celula(COL_JOGADOR, LINHA_ANDAR)
    editor.objeto_ou_abre(x, y)
    editor.abre_comportamentos()
    A.cap("p08_comportamentos")
    blocos.abre_categoria("Behavior Bundles")
    A.cap("p09_pacotes")
    b = blocos.solta("Run & Jump", 1400, 700)
    A.cap("p10_run_and_jump")
    print("   pacote:", b, flush=True)
    time.sleep(2.5)                     # o Flowlab precisa de tempo para guardar
    editor.fecha_comportamentos()
    time.sleep(2.5)
    fecha_painel_objeto()
    time.sleep(2.0)
    # PROVA de que ficou salvo: reabre e procura. Sem isto, o pacote some em
    # silencio, o jogador nao anda, e nada no editor acusa — foi o que fez a
    # Aula 1 falhar tres vezes seguidas.
    editor.objeto_ou_abre(x, y)
    editor.abre_comportamentos()
    # o canvas demora a desenhar: tento algumas vezes antes de acusar sumico,
    # senao eu reprovo um pacote que esta la e so nao foi pintado ainda
    lido = ""
    for tentativa in range(4):
        time.sleep(1.5)
        a, _ = nav.captura("/tmp/_c1_persist.png")
        lido = " ".join(t for t, *_ in rs.ocr_forte(a, regiao=(0.2, 0.05, 1, 0.9),
                                                    psm="6")).lower()
        if "run" in lido or "jump" in lido:
            break
    if "run" not in lido and "jump" not in lido:
        raise RuntimeError("o pacote Run & Jump NAO ficou salvo no jogador "
                           f"(li {lido[:80]!r})")
    print("   pacote conferido depois de reabrir", flush=True)
    editor.fecha_comportamentos()
    time.sleep(2.0)
    fecha_painel_objeto()
    return True


@etapa
def chao():
    """Chao CONTIGUO: pecas coladas, de 64 em 64 px. Na primeira montagem elas
       sairam espacadas e o jogador caiu pelo vao."""
    x, y = celula(COLS_CHAO[0], LINHA_CHAO)
    editor.objeto_ou_abre(x, y)
    nomeia("Chao")
    abre_sprite()
    pinta("verde")
    A.cap("p11_chao_verde")
    clique(*SPRITE_OK); time.sleep(2); nav.espera_parar(limite=15)
    fecha_painel_objeto()
    clique(x, y); time.sleep(1.5)
    a, _ = nav.captura("/tmp/_rad2.png")
    p = nav.acha_texto("clone", arquivo=a)
    A.gesto("clonar", "g05", p, lambda: clique(*p), espera=2)
    for c in COLS_CHAO[1:]:
        cx, cy = celula(c, LINHA_CHAO)
        clique(cx, cy); time.sleep(1.1)        # devagar: clique rapido nao coloca
    A.cap("p12_chao")
    q = nav.acha_texto("done cloning")
    clique(*q); time.sleep(2); nav.espera_parar(limite=15)
    A.cap("p13_chao_pronto")
    return True


@etapa
def moeda():
    x, y = celula(COL_MOEDA, LINHA_ANDAR)
    editor.objeto_ou_abre(x, y)
    nomeia("Moeda")
    abre_sprite()
    pinta("amarelo")
    A.cap("p14_moeda_amarela")
    clique(*SPRITE_OK); time.sleep(2); nav.espera_parar(limite=15)
    editor.abre_comportamentos()
    c = blocos.solta("Collision", 1100, 500)
    A.cap("p15_collision")
    d = blocos.solta("Destroyer", 1900, 950)
    A.cap("p16_destroyer")
    blocos.liga_fixo(c, "hit", d, "in")
    A.cap("p17_fio")
    editor.fecha_comportamentos()
    fecha_painel_objeto()
    A.cap("p18_moeda_pronta")
    return True


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


@etapa
def prova():
    """Joga, anda para a direita e PROVA que a moeda sumiu."""
    from PIL import Image
    import numpy as np

    def amarelo(f):
        im = np.asarray(Image.open(os.path.join(D, f)).convert("RGB"), dtype=int)
        return int(((im[:, :, 0] > 200) & (im[:, :, 1] > 140) &
                    (im[:, :, 1] < 200) & (im[:, :, 2] < 110)).sum())

    confere_fase()
    p = nav.acha_texto("play")
    A.gesto("jogar", "g06", p, lambda: clique(*p), espera=6)
    clique(1470, 640); time.sleep(1.5)
    antes = A.cap("p19_jogo")
    n0 = amarelo(antes)
    # toques CURTOS, conferindo a cada um: segurando, o boneco passa correndo
    # pela moeda e cai no fim do chao antes de a colisao valer
    n1 = n0
    for k in range(14):
        rs.segura_tecla(124, 0.12); time.sleep(0.45)   # 124 = seta direita
        n1 = amarelo(A.cap("p20_pegou"))
        if n1 < n0 * 0.5:
            print(f"   a moeda sumiu no toque {k+1}", flush=True)
            break
    print(f"   moeda: {n0} px antes, {n1} px depois", flush=True)
    if n1 >= n0 * 0.5:
        raise RuntimeError(f"a moeda NAO sumiu ({n0} -> {n1} px amarelos): "
                           "o jogo nao faz o que a aula promete")
    print("   PROVADO: a moeda sumiu quando o jogador encostou", flush=True)
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
