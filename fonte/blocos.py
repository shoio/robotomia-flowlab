#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Opera o editor de comportamentos do Flowlab: abre categoria, solta bloco na
   tela e LIGA fio entre dois pinos — conferindo cada gesto.

   Medido no editor de verdade (27-09-2026):
   - a palheta da esquerda e TEXTO: da para achar 'Always', 'Impulse',
     'Collision' por OCR, e arrastar dali para a tela funciona;
   - o bloco nasce com o canto de cima-esquerda quase no ponto onde eu solto;
   - cada pino tem um ROTULO ('out', 'x', 'y', 'hit') e a bolinha fica ~26 px
     (na imagem 2x) para fora da borda, na mesma altura do rotulo;
   - arrastar de bolinha a bolinha cria o fio.
"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rs, nav
from PIL import Image

PALHETA = (0, 0, 0.115, 1.0)          # a coluna da esquerda, em fracao da tela
TELA = (0.12, 0.0, 1.0, 0.95)          # a area de trabalho dos blocos

# quanto a bolinha do pino fica fora da borda do bloco, em pixels da imagem 2x
FORA_ESQ, FORA_DIR = 27, 25

CATEGORIAS = ["Triggers", "Logic & Math", "Components", "Properties",
              "Text & Lists", "GUI", "Game Flow", "Mobile Device",
              "Multiplayer", "Behavior Bundles"]


class Bloco:
    def __init__(self, nome, x, y):
        self.nome = nome
        self.x, self.y = x, y          # onde eu soltei (canto de cima-esquerda)

    def __repr__(self):
        return f"<{self.nome} em ({self.x},{self.y})>"

    def regiao(self, folga_esq=360, folga_dir=420, folga_cima=200, folga_baixo=300):
        """A caixa em volta do bloco, em fracao da imagem — para OCR local.

           Generosa de proposito: o bloco nasce CENTRADO no ponto onde eu solto,
           nao pelo canto. Com a caixa estreita eu procurava o titulo 'Destroyer'
           40 px a direita de onde ele estava e concluia que o bloco nao existia
           — e o retry soltava outro. Tres Destroyers empilhados."""
        J = nav.janela(nav.titulo())
        L, A = J["w"] * 2, J["h"] * 2
        return (max(0, self.x - folga_esq) / L, max(0, self.y - folga_cima) / A,
                min(1.0, (self.x + folga_dir) / L), min(1.0, (self.y + folga_baixo) / A))

    def pino(self, rotulo, lado, arquivo=None):
        """(x, y) da BOLINHA do pino, em pixels da imagem.
           lado='dir' para saida, 'esq' para entrada."""
        a = arquivo or nav.captura("/tmp/_bl_pino.png")[0]
        alvo = rotulo.lower()
        cands, lidos = [], []
        # o rotulo do pino e texto PEQUENO e claro sobre escuro: leio ampliado e
        # binarizado, e aceito leitura truncada ('out' volta como 'ou')
        for esc, lim in ((3, 90), (3, None), (4, 110), (2, 90)):
            itens = rs.ocr(a, regiao=self.regiao(), psm="6", escala=esc, limiar=lim)
            lidos += [i[0] for i in itens]
            for t, x, y, w, h in itens:
                cru = t.strip().lower()
                # o OCR cola a BOLINHA no rotulo: 'start' volta como '@/start',
                # 'reset' como '@jreset'. Comparo so as letras, e anoto se veio
                # sujeira na frente — porque ai a caixa ja inclui a bolinha e o
                # deslocamento para fora seria para o lugar errado.
                so_letras = "".join(c for c in cru if c.isalpha())
                sujo = bool(cru) and not cru[0].isalpha()
                if not so_letras:
                    continue
                if so_letras == alvo or (len(so_letras) >= 2 and alvo.startswith(so_letras)) \
                        or (len(alvo) >= 2 and so_letras.startswith(alvo)):
                    cands.append((so_letras, x, y, w, h, sujo))
            if cands:
                break
        if not cands:
            raise RuntimeError(f"nao achei o pino '{rotulo}' no bloco {self.nome} "
                               f"(li {lidos[:14]})")
        # com pinos repetidos (o Impulse tem tres 'out'), o de cima e o primeiro
        cands.sort(key=lambda c: c[2])
        t, x, y, w, h, sujo = cands[0]
        if lado == "dir":
            return (x + w + (6 if sujo else FORA_DIR), y + h // 2)
        return (x + 8 if sujo else x - FORA_ESQ, y + h // 2)


def abre_categoria(nome):
    """Abre a categoria da palheta, se ela ja nao estiver aberta."""
    p = nav.acha_texto(nome.lower(), regiao=PALHETA)
    if not p:
        raise RuntimeError(f"nao achei a categoria '{nome}' na palheta")
    J = nav.janela(nav.titulo())
    rs.clique_img(p[0], p[1], escala=2.0, janela=J)
    time.sleep(1.2)
    return True


def item_palheta(nome, tentativas=3):
    """(x, y) do item da palheta, abrindo categoria se precisar."""
    for k in range(tentativas):
        p = nav.acha_texto(nome.lower(), regiao=PALHETA)
        if p:
            return p
        if k == 0:
            # a palheta e sanfona: abrir uma categoria fecha a outra. Entao
            # percorro TODAS, nao um punhado escolhido a dedo — foi assim que
            # 'Timer' (que mora em Triggers) sumiu de uma lista com cinco nomes.
            for cat in CATEGORIAS:
                try:
                    abre_categoria(cat)
                except RuntimeError:
                    continue
                p = nav.acha_texto(nome.lower(), regiao=PALHETA)
                if p:
                    return p
        time.sleep(0.8)
    raise RuntimeError(f"o bloco '{nome}' nao aparece na palheta")


def solta(nome, x, y, tentativas=3, titulo=None):
    """Arrasta um bloco da palheta para (x, y) e CONFERE que ele nasceu ali.
       Sem conferir, um arrasto que nao pegou deixa a tela igual e o resto da
       aula e capturado em cima de um bloco que nao existe."""
    J = nav.janela(nav.titulo())
    for k in range(tentativas):
        p = item_palheta(nome)
        rs.arrasta_img(p[0], p[1], x, y, escala=2.0, janela=J)
        time.sleep(1.4)
        # A conferencia e feita na MESA INTEIRA, nao num recorte em volta do
        # ponto onde eu soltei. Num recorte pequeno de uma tela escura com uma
        # palavra so, o tesseract volta lixo: ele lia 'EM' onde estava escrito
        # 'Always', e o solta() desfazia um bloco que tinha nascido certo —
        # tres vezes seguidas, e a captura parava ali.
        try:
            achado = acha_bloco(titulo or nome)
        except RuntimeError:
            achado = None
        if achado and abs(achado.x - x) < 600 and abs(achado.y - y) < 400:
            return achado
        # DESFAZ antes de tentar de novo: repetir sem desfazer empilha blocos
        # invisiveis para mim e visiveis para a crianca na foto da aula
        rs.tecla(6, cmd=True)          # 6 = Z
        time.sleep(1.0)
    raise RuntimeError(f"soltei '{nome}' em ({x},{y}) e ele nao apareceu ali")


def liga(origem, pino_saida, destino, pino_entrada):
    """Liga saida -> entrada e CONFERE que o fio existe.
       A prova e a propria imagem: comparo o caminho entre os dois pinos antes
       e depois; um fio branco muda pixels no meio do caminho."""
    J = nav.janela(nav.titulo())
    a_antes, _ = nav.captura("/tmp/_bl_antes.png")
    p1 = pino_por_nome(origem, pino_saida, "dir")
    p2 = pino_por_nome(destino, pino_entrada, "esq")
    # duas tentativas: saida->entrada e, se nao pegar, entrada->saida
    for ida, (a, b) in enumerate(((p1, p2), (p2, p1))):
        arrasta_devagar(a[0], a[1], b[0], b[1])
        time.sleep(0.8)
        a_dep, _ = nav.captura("/tmp/_bl_depois.png")
        if _mudou_no_caminho(a_antes, a_dep, p1, p2) or _mudou_perto(a_antes, a_dep, p2):
            return True
    raise RuntimeError(f"liguei {origem.nome}.{pino_saida} -> "
                       f"{destino.nome}.{pino_entrada} e nenhum fio apareceu")


def _mudou_no_caminho(antes, depois, p1, p2, raio=70, minimo=25):
    """Mudou alguma coisa no meio do caminho entre os dois pinos?"""
    A = Image.open(antes).convert("L")
    B = Image.open(depois).convert("L")
    mx, my = (p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2
    cx0, cy0 = max(0, mx - raio), max(0, my - raio)
    caixa = (cx0, cy0, min(A.width, mx + raio), min(A.height, my + raio))
    a, b = A.crop(caixa), B.crop(caixa)
    dif = sum(1 for x, y in zip(a.getdata(), b.getdata()) if abs(x - y) > 30)
    return dif >= minimo


def ok():
    """Fecha o editor de comportamentos pelo botao OK (canto de baixo-esquerda)."""
    J = nav.janela(nav.titulo())
    rs.clique_img(160, 1560, escala=2.0, janela=J)
    time.sleep(2.0)
    nav.espera_parar(limite=15)
    return True


def acha_bloco(nome, regiao=TELA, tentativas=3):
    """Acha um bloco JA na tela pelo titulo e devolve um Bloco posicionado.

       Guardar a coordenada onde eu soltei nao serve: qualquer zoom, rolagem ou
       arrasto move tudo, e eu continuaria procurando o pino no lugar velho.
       O titulo do bloco e o endereco estavel."""
    for k in range(tentativas):
        a, _ = nav.captura("/tmp/_bl_acha.png")
        achado = rs.procura_forte(nome, a, regiao=regiao, psm="6", exato=True)
        if achado:
            t, x, y, w, h = achado
            return Bloco(nome, x, y + h // 2)
        time.sleep(0.8)
    raise RuntimeError(f"nao achei o bloco '{nome}' na tela")


# A ORDEM dos pinos de cada bloco, de cima para baixo. Lida uma vez na tela e
# guardada aqui: o rotulo e texto minusculo e o OCR erra: 'start' virava
# '@/start', 'reset' virava '@jreset' e as vezes sumia. A bolinha, essa e um
# circulo claro — geometria, nao leitura.
PORTAS = {
    "Always":    {"esq": [],                       "dir": ["out"]},
    "Once":      {"esq": [],                       "dir": ["out"]},
    "Timer":     {"esq": ["delay", "reset", "start"], "dir": ["out", "done"]},
    "Impulse":   {"esq": ["x", "y", "forward"],    "dir": ["out", "out2", "out3"]},
    "Destroyer": {"esq": ["in"],                   "dir": ["out"]},
    "Collision": {"esq": [],                       "dir": ["hit"]},
    "Keyboard":  {"esq": [],                       "dir": ["up", "down"]},
    "Number":    {"esq": ["in"],                   "dir": ["out"]},
    "Label":     {"esq": ["text", "show", "hide"], "dir": ["out"]},
    "Mailbox":   {"esq": [],                       "dir": ["out"]},
    "Message":   {"esq": ["send"],                 "dir": ["out"]},
    "Spawn":     {"esq": ["spawn"],                "dir": ["out"]},
    "Sound":     {"esq": ["play", "stop"],         "dir": ["done"]},
}


def bolinhas(bloco, folga=(70, 620, 60, 340), claro=185, raio=(3, 11)):
    """As BOLINHAS dos pinos de um bloco, separadas em ('esq', 'dir').

       Acha aglomerados claros e pequenos na caixa do bloco e agrupa por
       coluna: a coluna mais a esquerda e a das entradas, a mais a direita a
       das saidas. Devolve listas ordenadas de cima para baixo."""
    import numpy as _np
    a, _ = nav.captura("/tmp/_bl_dots.png")
    im = _np.asarray(Image.open(a).convert("L"), dtype=int)
    fe, fd, fc, fb = folga
    x0, y0 = max(0, bloco.x - fe), max(0, bloco.y - fc)
    x1, y1 = min(im.shape[1], bloco.x + fd), min(im.shape[0], bloco.y + fb)
    rec = im[y0:y1, x0:x1]
    # bolinha solta e cinza-clara; sob o cursor ela fica AZUL. As duas contam.
    rgb = _np.asarray(Image.open(a).convert("RGB"), dtype=int)[y0:y1, x0:x1]
    azul = (rgb[:, :, 2] - rgb[:, :, 0] >= 55) & (rgb[:, :, 2] >= 150)
    mask = (rec >= claro) | azul
    vistos = _np.zeros_like(mask)
    achados = []
    ys, xs = _np.nonzero(mask)
    for yy, xx in zip(ys, xs):
        if vistos[yy, xx]:
            continue
        pilha, pontos = [(yy, xx)], []
        vistos[yy, xx] = True
        while pilha and len(pontos) < 400:
            cy, cx = pilha.pop()
            pontos.append((cy, cx))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < mask.shape[0] and 0 <= nx < mask.shape[1] \
                            and mask[ny, nx] and not vistos[ny, nx]:
                        vistos[ny, nx] = True
                        pilha.append((ny, nx))
        if not pontos:
            continue
        pys = [p[0] for p in pontos]; pxs = [p[1] for p in pontos]
        alt, larg = max(pys) - min(pys) + 1, max(pxs) - min(pxs) + 1
        cheio = len(pontos) / float(alt * larg)
        if raio[0] * 2 <= alt <= raio[1] * 2 and raio[0] * 2 <= larg <= raio[1] * 2 \
                and abs(alt - larg) <= 5 and len(pontos) >= 12 and cheio >= 0.55:
            achados.append((int(sum(pxs) / len(pxs)) + x0, int(sum(pys) / len(pys)) + y0))
    # a bolinha fica FORA da borda; o que cai dentro do bloco e icone ou letra
    achados = [p for p in achados if p[0] <= bloco.x - 8 or p[0] >= bloco.x + 60]
    if not achados:
        return {"esq": [], "dir": []}
    menor = min(p[0] for p in achados); maior = max(p[0] for p in achados)
    esq = sorted([p for p in achados if p[0] - menor <= 30 and p[0] <= bloco.x - 8],
                 key=lambda p: p[1])
    dir_ = sorted([p for p in achados if maior - p[0] <= 30 and p[0] >= bloco.x + 60],
                  key=lambda p: p[1])
    return {"esq": esq, "dir": dir_}


def pino_por_nome(bloco, rotulo, lado):
    """A bolinha do pino, pela ORDEM conhecida do bloco — sem ler texto."""
    ordem = PORTAS.get(bloco.nome, {}).get(lado)
    if not ordem or rotulo not in ordem:
        raise RuntimeError(f"nao sei a ordem dos pinos de '{bloco.nome}' "
                           f"({lado}) — acrescente em blocos.PORTAS")
    pts = bolinhas(bloco)[lado]
    i = ordem.index(rotulo)
    if i >= len(pts):
        raise RuntimeError(f"o bloco {bloco.nome} mostrou {len(pts)} bolinhas de "
                           f"{lado}, e eu queria a {i+1}a ('{rotulo}')")
    return pts[i]


def arrasta_devagar(x0, y0, x1, y1, passos=45, segura=0.45):
    """Arrasto lento, com pausa antes e depois e um tremor no fim.
       O editor do Flowlab e canvas: arrasto rapido demais entre bolinhas
       acende o pino de destino e nao cria fio nenhum."""
    import Quartz
    J = nav.janela(nav.titulo())
    tx0, ty0 = J["x"] + x0 / 2.0, J["y"] + y0 / 2.0
    tx1, ty1 = J["x"] + x1 / 2.0, J["y"] + y1 / 2.0
    rs._evento_mouse(Quartz.kCGEventMouseMoved, tx0, ty0); time.sleep(0.35)
    rs._evento_mouse(Quartz.kCGEventLeftMouseDown, tx0, ty0); time.sleep(segura)
    for k in range(1, passos + 1):
        x = tx0 + (tx1 - tx0) * k / passos
        y = ty0 + (ty1 - ty0) * k / passos
        e = Quartz.CGEventCreateMouseEvent(None, Quartz.kCGEventLeftMouseDragged,
                                           (x, y), Quartz.kCGMouseButtonLeft)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, e)
        time.sleep(0.03)
    for dx, dy in ((2, 0), (-2, 1), (0, 0)):      # tremor: o canvas percebe o alvo
        e = Quartz.CGEventCreateMouseEvent(None, Quartz.kCGEventLeftMouseDragged,
                                           (tx1 + dx, ty1 + dy), Quartz.kCGMouseButtonLeft)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, e)
        time.sleep(0.12)
    time.sleep(segura)
    rs._evento_mouse(Quartz.kCGEventLeftMouseUp, tx1, ty1)
    time.sleep(0.6)


def _mudou_perto(antes, depois, ponto, raio=26, minimo=12):
    A = Image.open(antes).convert("L"); B = Image.open(depois).convert("L")
    x, y = ponto
    caixa = (max(0, x - raio), max(0, y - raio),
             min(A.width, x + raio), min(A.height, y + raio))
    a, b = A.crop(caixa), B.crop(caixa)
    return sum(1 for p, q in zip(a.getdata(), b.getdata()) if abs(p - q) > 30) >= minimo


CORPO = (61, 66, 80)        # cor do corpo de um bloco
FUNDO = (32, 41, 56)        # cor do canvas atras dos blocos


def caixa_do_bloco(bloco, tol=14):
    """(x0, y0, x1, y1) do RETANGULO do bloco, medido na imagem.

       Herdado do que deu errado: caixa por folga fixa muda de tamanho com o
       zoom da pagina e passa a abracar o bloco vizinho, e ai as 'bolinhas' do
       bloco de baixo entram na conta do bloco de cima. O corpo do bloco tem
       cor propria (61,66,80) contra o fundo (32,41,56): da para medir."""
    import numpy as _np
    a, _ = nav.captura("/tmp/_bl_caixa.png")
    im = _np.asarray(Image.open(a).convert("RGB"), dtype=int)
    corpo = (_np.abs(im - _np.array(CORPO)) <= tol).all(axis=2)
    sx, sy = bloco.x + 12, bloco.y + 22          # semente dentro do corpo
    if not (0 <= sy < corpo.shape[0] and 0 <= sx < corpo.shape[1]) or not corpo[sy, sx]:
        for dy in (14, 30, 8, 40):
            if 0 <= bloco.y + dy < corpo.shape[0] and corpo[bloco.y + dy, sx]:
                sy = bloco.y + dy
                break
        else:
            raise RuntimeError(f"nao achei o corpo do bloco {bloco.nome} perto do titulo")
    x0 = x1 = sx
    while x0 > 0 and corpo[sy, x0 - 1]:
        x0 -= 1
    while x1 < corpo.shape[1] - 1 and corpo[sy, x1 + 1]:
        x1 += 1
    meio = (x0 + x1) // 2
    y0 = y1 = sy
    while y0 > 0 and corpo[y0 - 1, meio]:
        y0 -= 1
    while y1 < corpo.shape[0] - 1 and corpo[y1 + 1, meio]:
        y1 += 1
    return (x0, y0, x1, y1)


def bolinhas2(bloco, margem=34, claro=180):
    """As bolinhas dos pinos, procuradas SO nas faixas do lado de fora das
       bordas do bloco — nada de caixa por folga."""
    import numpy as _np
    x0, y0, x1, y1 = caixa_do_bloco(bloco)
    a, _ = nav.captura("/tmp/_bl_dots2.png")
    im = _np.asarray(Image.open(a).convert("RGB"), dtype=int)
    L = _np.asarray(Image.open(a).convert("L"), dtype=int)
    azul = (im[:, :, 2] - im[:, :, 0] >= 55) & (im[:, :, 2] >= 150)
    mask = (L >= claro) | azul

    def na_faixa(fx0, fx1):
        pts = []
        sub = mask[max(0, y0 - 6):y1 + 7, max(0, fx0):fx1]
        vistos = _np.zeros_like(sub)
        ys, xs = _np.nonzero(sub)
        for yy, xx in zip(ys, xs):
            if vistos[yy, xx]:
                continue
            pilha, pontos = [(yy, xx)], []
            vistos[yy, xx] = True
            while pilha and len(pontos) < 500:
                cy, cx = pilha.pop(); pontos.append((cy, cx))
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < sub.shape[0] and 0 <= nx < sub.shape[1] \
                                and sub[ny, nx] and not vistos[ny, nx]:
                            vistos[ny, nx] = True; pilha.append((ny, nx))
            pys = [p[0] for p in pontos]; pxs = [p[1] for p in pontos]
            alt, larg = max(pys) - min(pys) + 1, max(pxs) - min(pxs) + 1
            if 5 <= alt <= 26 and 5 <= larg <= 26 and abs(alt - larg) <= 6 \
                    and len(pontos) / float(alt * larg) >= 0.55:
                pts.append((int(sum(pxs) / len(pxs)) + max(0, fx0),
                            int(sum(pys) / len(pys)) + max(0, y0 - 6)))
        return sorted(pts, key=lambda p: p[1])

    return {"esq": na_faixa(x0 - margem, x0), "dir": na_faixa(x1 + 1, x1 + margem)}


def caixa2(bloco, limite=(700, 420)):
    """O retangulo do bloco, por CRESCIMENTO a partir de uma semente.

       A varredura por linha parava cedo: o miolo do bloco tem tom diferente do
       corpo (icone, barra de titulo). Aqui a regra e 'nao e o fundo do canvas',
       com uma erosao antes — senao o crescimento escapa pelo FIO, que encosta
       na borda, e engole o bloco vizinho."""
    import numpy as _np
    a, _ = nav.captura("/tmp/_bl_caixa2.png")
    im = _np.asarray(Image.open(a).convert("RGB"), dtype=int)
    fundo = (_np.abs(im - _np.array(FUNDO)) <= 12).all(axis=2)
    cheio = ~fundo
    # erosao 3x3: tira fio fino e deixa o corpo do bloco
    e = cheio.copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            e &= _np.roll(_np.roll(cheio, dy, axis=0), dx, axis=1)
    sx, sy = bloco.x + 12, bloco.y + 4
    if not e[sy, sx]:
        for dy in range(-6, 40, 4):
            if 0 <= bloco.y + dy < e.shape[0] and e[bloco.y + dy, sx]:
                sy = bloco.y + dy; break
        else:
            raise RuntimeError(f"nao achei o corpo de {bloco.nome} perto do titulo")
    x0 = x1 = sx; y0 = y1 = sy
    pilha = [(sy, sx)]
    vistos = set()
    while pilha:
        cy, cx = pilha.pop()
        if (cy, cx) in vistos:
            continue
        vistos.add((cy, cx))
        if abs(cx - sx) > limite[0] or abs(cy - sy) > limite[1]:
            continue
        x0, x1 = min(x0, cx), max(x1, cx)
        y0, y1 = min(y0, cy), max(y1, cy)
        for ny, nx in ((cy+1, cx), (cy-1, cx), (cy, cx+1), (cy, cx-1)):
            if 0 <= ny < e.shape[0] and 0 <= nx < e.shape[1] and e[ny, nx] \
                    and (ny, nx) not in vistos:
                pilha.append((ny, nx))
    return (x0 - 1, y0 - 1, x1 + 1, y1 + 1)


def caixa3(bloco, tol=12, limite=900):
    """O retangulo do bloco. Terceira tentativa, e a que funciona.

       As duas anteriores estao acima, com o defeito de cada uma: varredura no
       MEIO do bloco para cedo (o miolo tem outro tom por causa do icone), e
       crescimento de regiao VAZA pelo fio ate o bloco vizinho.

       Aqui: acho as bordas esquerda e direita na LINHA DO TITULO (que so tem
       corpo e letra), e a altura numa COLUNA a 3 px de dentro da borda
       esquerda, onde nao ha icone nem texto."""
    import numpy as _np
    a, _ = nav.captura("/tmp/_bl_caixa3.png")
    im = _np.asarray(Image.open(a).convert("RGB"), dtype=int)
    fundo = (_np.abs(im - _np.array(FUNDO)) <= tol).all(axis=2)
    A, L = fundo.shape
    ty = min(max(bloco.y, 0), A - 1)
    tx = min(max(bloco.x, 0), L - 1)
    if fundo[ty, tx]:                       # o titulo pode cair no vao da letra
        for dx in (4, 8, -4, 12):
            if 0 <= tx + dx < L and not fundo[ty, tx + dx]:
                tx += dx; break
    x0 = tx
    while x0 > 0 and not fundo[ty, x0 - 1] and tx - x0 < limite:
        x0 -= 1
    x1 = tx
    while x1 < L - 1 and not fundo[ty, x1 + 1] and x1 - tx < limite:
        x1 += 1
    col = min(x0 + 3, L - 1)
    y0 = ty
    while y0 > 0 and not fundo[y0 - 1, col] and ty - y0 < limite:
        y0 -= 1
    y1 = ty
    while y1 < A - 1 and not fundo[y1 + 1, col] and y1 - ty < limite:
        y1 += 1
    return (x0, y0, x1, y1)


def pinos(bloco, margem=22, claro=175, folga=4):
    """As bolinhas dos pinos, nas faixas de fora das bordas medidas por caixa3.
       Confere a CONTAGEM contra a tabela PORTAS — se o bloco devia ter tres
       entradas e eu achei duas, eu digo, em vez de ligar no pino errado."""
    import numpy as _np
    x0, y0, x1, y1 = caixa4(bloco)
    a, _ = nav.captura("/tmp/_bl_pinos.png")
    rgb = _np.asarray(Image.open(a).convert("RGB"), dtype=int)
    lum = _np.asarray(Image.open(a).convert("L"), dtype=int)
    azul = (rgb[:, :, 2] - rgb[:, :, 0] >= 55) & (rgb[:, :, 2] >= 150)
    mask = (lum >= claro) | azul

    def faixa(fx0, fx1):
        fx0, fx1 = max(0, fx0), max(0, fx1)
        sub = mask[max(0, y0 - 4):y1 + 5, fx0:fx1]
        if sub.size == 0:
            return []
        vistos = _np.zeros_like(sub); pts = []
        ys, xs = _np.nonzero(sub)
        for yy, xx in zip(ys, xs):
            if vistos[yy, xx]:
                continue
            pilha, pontos = [(yy, xx)], []
            vistos[yy, xx] = True
            while pilha and len(pontos) < 600:
                cy, cx = pilha.pop(); pontos.append((cy, cx))
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < sub.shape[0] and 0 <= nx < sub.shape[1] \
                                and sub[ny, nx] and not vistos[ny, nx]:
                            vistos[ny, nx] = True; pilha.append((ny, nx))
            pys = [p[0] for p in pontos]; pxs = [p[1] for p in pontos]
            alt, larg = max(pys) - min(pys) + 1, max(pxs) - min(pxs) + 1
            if 5 <= alt <= 24 and 5 <= larg <= 24 and abs(alt - larg) <= 5 \
                    and len(pontos) / float(alt * larg) >= 0.5:
                pts.append((int(sum(pxs) / len(pxs)) + fx0,
                            int(sum(pys) / len(pys)) + max(0, y0 - 4)))
        return sorted(pts, key=lambda p: p[1])

    # a bolinha encosta na borda (medido: 16 px de distancia). Faixa estreita,
    # senao eu pego a bolinha do bloco VIZINHO e ligo no lugar errado.
    # procuro numa faixa LARGA (senao o disco sai cortado e perde a redondeza)
    # e aceito pelo CENTRO, que e o que diz de quem e a bolinha
    largo = margem + 16
    esq = [p for p in faixa(x0 - largo, x0) if x0 - margem <= p[0] <= x0 - folga]
    dire = [p for p in faixa(x1, x1 + largo) if x1 + folga <= p[0] <= x1 + margem]
    achados = {"esq": esq, "dir": dire}
    esperado = PORTAS.get(bloco.nome)
    if esperado:
        for lado in ("esq", "dir"):
            if len(achados[lado]) != len(esperado[lado]):
                raise RuntimeError(
                    f"{bloco.nome}: achei {len(achados[lado])} bolinhas de "
                    f"{lado} e a tabela diz {len(esperado[lado])} "
                    f"({esperado[lado]}) — nao ligo no escuro")
    return achados


def caixa4(bloco, tol=14, claro=150, limite=700):
    """O retangulo do bloco — versao que aguenta o bloco em cima do retangulo
       de previsao do nivel.

       'Nao e o fundo' nao serve: a previsao do nivel tambem nao e o fundo, e a
       caixa crescia ate abracar o mundo inteiro (medi 1023x767 para um bloco
       de ~240x170). A regra que fecha: o pixel e CORPO DO BLOCO (61,66,80) ou
       e CLARO (letra, borda, icone). A previsao do nivel nao e nem um nem
       outro, entao a varredura para exatamente na borda."""
    import numpy as _np
    a, _ = nav.captura("/tmp/_bl_caixa4.png")
    rgb = _np.asarray(Image.open(a).convert("RGB"), dtype=int)
    lum = _np.asarray(Image.open(a).convert("L"), dtype=int)
    dentro = ((_np.abs(rgb - _np.array(CORPO)) <= tol).all(axis=2)) | (lum >= claro)
    A, L = dentro.shape
    ty, tx = min(max(bloco.y, 0), A - 1), min(max(bloco.x, 0), L - 1)
    if not dentro[ty, tx]:
        for dx in (4, 8, 12, -4):
            if 0 <= tx + dx < L and dentro[ty, tx + dx]:
                tx += dx; break
    x0 = tx
    while x0 > 0 and dentro[ty, x0 - 1] and tx - x0 < limite:
        x0 -= 1
    x1 = tx
    while x1 < L - 1 and dentro[ty, x1 + 1] and x1 - tx < limite:
        x1 += 1
    col = min(x0 + 4, L - 1)
    y0 = ty
    while y0 > 0 and dentro[y0 - 1, col] and ty - y0 < limite:
        y0 -= 1
    y1 = ty
    while y1 < A - 1 and dentro[y1 + 1, col] and y1 - ty < limite:
        y1 += 1
    return (x0, y0, x1, y1)


def discos(bloco, esq=45, dir_=430, cima=25, baixo=250, claro=175):
    """Os discos claros em volta do titulo de um bloco, separados em colunas.

       Depois de quatro tentativas de medir o retangulo do bloco pela cor
       (linha do titulo, crescimento de regiao, corpo-ou-claro), o que fecha e
       aceitar que a MEDIDA do retangulo e fragil — o antialias entre as letras
       tem a cor da previsao do nivel — e usar o que eu CONTROLO: a aula
       coloca os blocos longe uns dos outros, entao uma caixa generosa em volta
       do titulo so contem os pinos deste bloco. A contagem esperada confere."""
    import numpy as _np
    a, _ = nav.captura("/tmp/_bl_discos.png")
    rgb = _np.asarray(Image.open(a).convert("RGB"), dtype=int)
    lum = _np.asarray(Image.open(a).convert("L"), dtype=int)
    azul = (rgb[:, :, 2] - rgb[:, :, 0] >= 55) & (rgb[:, :, 2] >= 150)
    mask = (lum >= claro) | azul
    A, L = mask.shape
    x0, x1 = max(0, bloco.x - esq), min(L, bloco.x + dir_)
    y0, y1 = max(0, bloco.y - cima), min(A, bloco.y + baixo)
    sub = mask[y0:y1, x0:x1]
    vistos = _np.zeros_like(sub); pts = []
    ys, xs = _np.nonzero(sub)
    for yy, xx in zip(ys, xs):
        if vistos[yy, xx]:
            continue
        pilha, pontos = [(yy, xx)], []
        vistos[yy, xx] = True
        while pilha and len(pontos) < 600:
            cy, cx = pilha.pop(); pontos.append((cy, cx))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < sub.shape[0] and 0 <= nx < sub.shape[1] \
                            and sub[ny, nx] and not vistos[ny, nx]:
                        vistos[ny, nx] = True; pilha.append((ny, nx))
        pys = [p[0] for p in pontos]; pxs = [p[1] for p in pontos]
        alt, larg = max(pys) - min(pys) + 1, max(pxs) - min(pxs) + 1
        if 7 <= alt <= 22 and 7 <= larg <= 22 and abs(alt - larg) <= 4 \
                and len(pontos) / float(alt * larg) >= 0.62:
            pts.append((int(sum(pxs) / len(pxs)) + x0, int(sum(pys) / len(pys)) + y0))
    if not pts:
        return {"esq": [], "dir": []}
    # duas colunas: a da esquerda e a mais a esquerda de todas
    menor, maior = min(p[0] for p in pts), max(p[0] for p in pts)
    coluna_esq = [p for p in pts if p[0] - menor <= 24 and p[0] < bloco.x]
    coluna_dir = [p for p in pts if maior - p[0] <= 24 and p[0] > bloco.x + 60]
    return {"esq": sorted(coluna_esq, key=lambda p: p[1]),
            "dir": sorted(coluna_dir, key=lambda p: p[1])}


def pino(bloco, rotulo, lado):
    """A bolinha de um pino, pela ordem conhecida, com a contagem conferida."""
    ordem = PORTAS.get(bloco.nome, {}).get(lado)
    if ordem is None:
        raise RuntimeError(f"nao sei a ordem dos pinos de '{bloco.nome}' ({lado})")
    achados = discos(bloco)[lado]
    if len(achados) != len(ordem):
        raise RuntimeError(f"{bloco.nome}: achei {len(achados)} bolinhas de {lado} "
                           f"e a tabela diz {len(ordem)} ({ordem})")
    return achados[ordem.index(rotulo)]


# Deslocamento de cada pino em relacao ao TITULO do bloco, medido na tela com a
# pagina em 100%. Medir uma vez e guardar foi o que funcionou: detectar disco
# automaticamente falhou quatro vezes (a previsao do nivel, o antialias entre as
# letras e o icone do bloco entram na conta).
#   chave: nome do bloco -> lado -> rotulo -> (dx, dy)
DESLOC = {
    "Collision": {"esq": {}, "dir": {"hit": (247, 57)}},
    # medidos na captura de tela, no rascunho da Aula 3
    "Always":   {"esq": {}, "dir": {"out": (251, 54)}},
    "Velocity": {"esq": {"x": (-31, 40), "y": (-31, 76), "forward": (-31, 114)},
                 "dir": {"out": (249, 40), "out2": (249, 76), "out3": (249, 114)}},
    # o Number tem TRES entradas: 'set' (quadrada, recebe valor), 'get'
    # (redonda, e o gatilho que faz ele cuspir o valor) e '+' (soma 1).
    # Ligar o Always no 'set' nao faz nada sair: quem dispara e o 'get'.
    "Number":   {"esq": {"set": (-28, 39), "get": (-28, 75), "mais": (-28, 114)},
                 "dir": {"out": (249, 74)}},
    "Alert":    {"esq": {"show": (-26, 45), "hide": (-26, 86)},
                 "dir": {"click": (247, 65)}},
    "Destroyer": {"esq": {"in": (-28, 57)}, "dir": {"out": (248, 57)}},
    # o titulo no canvas e 'RestartGame' (sem espaco), mas na palheta ele
    # aparece como 'Restart Game' — por isso solta() aceita titulo diferente
    "RestartGame": {"esq": {"go": (-28, 57)}, "dir": {"out": (248, 57)}},
}


def pino_fixo(bloco, rotulo, lado):
    """(x, y) do pino pelo deslocamento medido do tipo do bloco."""
    tab = DESLOC.get(bloco.nome, {}).get(lado, {})
    if rotulo not in tab:
        raise RuntimeError(f"nao tenho o deslocamento do pino '{rotulo}' ({lado}) "
                           f"de '{bloco.nome}' — meça e acrescente em blocos.DESLOC")
    dx, dy = tab[rotulo]
    return (bloco.x + dx, bloco.y + dy)


def _ha_fio(arquivo, p1, p2, folga=34, claro=200, minimo=40):
    """Ja existe um fio ligando estes dois pinos?

       Olha a FAIXA entre eles e conta pixels claros — o fio e quase branco, e
       o fundo da mesa e escuro. A faixa e partida em tres fatias ao longo do
       eixo MAIS LONGO, e as tres precisam ter fio: assim um fio de outro par
       que cruze a regiao nao passa por ligacao.

       O eixo importa. A primeira versao sempre fatiava na horizontal, e para
       dois pinos quase um em cima do outro (Always.out -> Number.get, 86 px
       de distancia horizontal) a faixa ficava estreita demais e ela respondia
       'nao ha fio' com o fio desenhado na tela.

       Isto e o invariante ('ha um fio entre estes dois pinos'), e nao o proxy
       ('alguma coisa mudou no caminho'). O proxy reprovava quando o fio JA
       ESTAVA LA — que e o estado normal de uma etapa repetida depois de um
       erro no meio dela."""
    import numpy as _np
    im = _np.asarray(Image.open(arquivo).convert("L"), dtype=int)
    x0, x1 = sorted((p1[0], p2[0]))
    y0, y1 = sorted((p1[1], p2[1]))
    horizontal = (x1 - x0) >= (y1 - y0)
    if horizontal:
        x0, x1 = x0 + folga, x1 - folga
        y0, y1 = max(0, y0 - 60), min(im.shape[0], y1 + 60)
    else:
        y0, y1 = y0 + folga, y1 - folga
        x0, x1 = max(0, x0 - 60), min(im.shape[1], x1 + 60)
    if x1 - x0 < 20 or y1 - y0 < 20:
        return False
    passo = ((x1 - x0) if horizontal else (y1 - y0)) // 3
    if passo < 4:
        return False
    for k in range(3):
        if horizontal:
            rec = im[y0:y1, x0 + k * passo: x0 + (k + 1) * passo]
        else:
            rec = im[y0 + k * passo: y0 + (k + 1) * passo, x0:x1]
        if int((rec > claro).sum()) < minimo:
            return False
    return True


def liga_fixo(origem, pino_saida, destino, pino_entrada):
    """Liga usando os deslocamentos medidos, e CONFERE que o fio existe."""
    p1 = pino_fixo(origem, pino_saida, "dir")
    p2 = pino_fixo(destino, pino_entrada, "esq")
    a, _ = nav.captura("/tmp/_lf_antes.png")
    if _ha_fio(a, p1, p2):
        return "ja estava"
    for _ in range(2):
        arrasta_devagar(p1[0], p1[1], p2[0], p2[1])
        time.sleep(0.8)
        a_dep, _ = nav.captura("/tmp/_lf_depois.png")
        if _ha_fio(a_dep, p1, p2):
            return True
    raise RuntimeError(f"liguei {origem.nome}.{pino_saida} -> "
                       f"{destino.nome}.{pino_entrada} e nenhum fio apareceu")


# ---------------------------------------------------------------------------
# AJUSTES DE UM BLOCO
#
# Descoberto no rascunho da Aula 3, depois de meia duzia de tentativas erradas:
# o painel de ajustes de um bloco (Label, Current value, OK, Delete) NAO abre
# com clique comum nem com clique duplo — esses so SELECIONAM o bloco, e o
# arrasto o move. Quem abre e o clique LENTO (`rs.clique_lento`): parar o
# ponteiro em cima, apertar e segurar um instante antes de soltar.
#
# Enquanto eu insistia no clique rapido, o numero continuava 0 e nada na tela
# dizia por que — o bloco ate ficava com a borda azul, parecendo que tinha
# recebido o clique.
# ---------------------------------------------------------------------------

def abre_ajustes(bloco, tentativas=3):
    """Abre o painel de ajustes do bloco e devolve o ponto do campo de valor."""
    J = nav.janela()
    for k in range(tentativas):
        rs.clique_lento(J["x"] + bloco.x / 2.0 + 55, J["y"] + bloco.y / 2.0 + 33)
        time.sleep(1.4)
        a, _ = nav.captura("/tmp/_bl_aj.png")
        p = nav.acha_texto("current value", arquivo=a)
        if p:
            return p
        # o painel pode ter aberto sem o campo (blocos sem valor): aceito se o
        # OK/Delete do painel estiver la
        if nav.acha_texto("delete", arquivo=a):
            return None
        time.sleep(0.8)
    raise RuntimeError(f"nao consegui abrir os ajustes do bloco {bloco.nome}")


def escreve_valor(bloco, valor):
    """Abre os ajustes, escreve o valor em 'Current value' e fecha no OK.
       CONFERE lendo o numero que ficou no corpo do bloco."""
    p = abre_ajustes(bloco)
    if not p:
        raise RuntimeError(f"o bloco {bloco.nome} nao tem campo 'Current value'")
    # o campo fica logo ABAIXO do rotulo 'Current value'
    alvo = (p[0] + 30, p[1] + 68)
    nav.clique_seguro(*alvo); time.sleep(0.6)
    rs.tecla(0, cmd=True); time.sleep(0.25)          # Cmd+A
    # O CAMPO ENGOLE O MENOS QUANDO ELE E O PRIMEIRO. Com o conteudo todo
    # selecionado, digitar '-0.3' deixa '0.3' — sem erro nenhum, e o sinal e
    # justamente o que faz a lava SUBIR em vez de descer. (Nao e o teclado:
    # medi tecla por tecla no campo 'Label' e o codigo 27 produz hifen sim.)
    # Entao escrevo os algarismos, volto o cursor ate o comeco e so entao o
    # sinal. Pelo caminho UNICODE o campo nao recebe nada.
    texto = str(valor)
    negativo = texto.startswith("-")
    corpo = texto.lstrip("-")
    rs.digita_teclas(corpo); time.sleep(0.4)
    if negativo:
        for _ in range(len(corpo)):
            rs.tecla(123); time.sleep(0.08)          # seta esquerda
        rs.digita_teclas("-"); time.sleep(0.4)
    time.sleep(0.3)
    fecha_ajustes()
    lido = le_valor(bloco)
    if lido != str(valor):
        raise RuntimeError(f"escrevi {valor} em {bloco.nome} e o bloco mostra {lido!r}")
    return True


def fecha_ajustes():
    a, _ = nav.captura("/tmp/_bl_ok.png")
    p = nav.acha_texto("delete", arquivo=a)
    if not p:
        return False
    # o OK fica a ESQUERDA do Delete, na mesma altura
    nav.clique_seguro(p[0] - 200, p[1]); time.sleep(1.2)
    return True


AZUL_VALOR = None      # o numero do bloco e desenhado em azul claro


def _glifos_azuis(arquivo, bloco):
    """As manchas AZUIS dentro do bloco, da esquerda para a direita.
       Cada mancha e um sinal ou um algarismo."""
    import numpy as _np
    im = _np.asarray(Image.open(arquivo).convert("RGB"), dtype=int)
    y0, y1 = max(0, bloco.y - 10), min(im.shape[0], bloco.y + 140)
    x0, x1 = max(0, bloco.x - 10), min(im.shape[1], bloco.x + 300)
    sub = im[y0:y1, x0:x1]
    m = (sub[:, :, 2] > 170) & (sub[:, :, 2] - sub[:, :, 0] > 55) & (sub[:, :, 1] > 95)
    if not m.any():
        return [], None
    vistos = _np.zeros_like(m); grupos = []
    ys, xs = _np.nonzero(m)
    for yy, xx in zip(ys, xs):
        if vistos[yy, xx]:
            continue
        pilha, pts = [(yy, xx)], []
        vistos[yy, xx] = True
        while pilha:
            cy, cx = pilha.pop(); pts.append((cy, cx))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < m.shape[0] and 0 <= nx < m.shape[1] \
                            and m[ny, nx] and not vistos[ny, nx]:
                        vistos[ny, nx] = True; pilha.append((ny, nx))
        pys = [q[0] for q in pts]; pxs = [q[1] for q in pts]
        grupos.append(dict(x=min(pxs) + x0, y=min(pys) + y0,
                           w=max(pxs) - min(pxs) + 1, h=max(pys) - min(pys) + 1))
    grupos.sort(key=lambda g: g["x"])
    caixa = (min(g["x"] for g in grupos) - 8, min(g["y"] for g in grupos) - 8,
             max(g["x"] + g["w"] for g in grupos) + 8,
             max(g["y"] + g["h"] for g in grupos) + 8)
    return grupos, caixa


def le_valor(bloco, tentativas=3):
    """O numero escrito DENTRO do bloco, lido da tela.

       Cada glifo e classificado SOZINHO, e nao a frase inteira:
       - o menos e uma barrinha baixa e larga — geometria, nao OCR, porque o
         tesseract come ou inventa o hifen (e ler '-1.7' como '1.7' deixaria a
         lava DESCENDO com o guarda verde);
       - o ponto decimal e um quadradinho;
       - so os ALGARISMOS vao para o tesseract, um por um, com margem branca e
         em tamanho nativo. A linha inteira nao serve: '-1' volta vazio e
         '-1.7' volta '1' — o recorte curto derruba a segmentacao."""
    for k in range(tentativas):
        b = acha_bloco(bloco.nome)
        a, _ = nav.captura("/tmp/_bl_val.png")
        grupos, _caixa = _glifos_azuis(a, b)
        if not grupos:
            time.sleep(0.8); continue
        import numpy as _np
        from PIL import ImageOps
        rgb = _np.asarray(Image.open(a).convert("RGB"), dtype=int)
        alt = max(g["h"] for g in grupos)
        saida, falhou = "", False
        for g in grupos:
            if g["h"] <= alt * 0.45 and g["w"] >= g["h"] * 1.6:
                saida += "-"; continue
            if g["h"] <= alt * 0.33 and g["w"] <= alt * 0.33:
                saida += "."; continue
            rec = rgb[g["y"] - 4:g["y"] + g["h"] + 4, g["x"] - 4:g["x"] + g["w"] + 4]
            mk = (rec[:, :, 2] > 170) & (rec[:, :, 2] - rec[:, :, 0] > 55) & (rec[:, :, 1] > 95)
            im = Image.fromarray(_np.where(mk, 0, 255).astype("uint8"), "L")
            im = ImageOps.expand(im, border=40, fill=255)
            im.save("/tmp/_bl_glifo.png")
            lido = ""
            for psm in ("10", "8", "7"):
                r = [c for t, *_ in rs.ocr("/tmp/_bl_glifo.png", psm=psm, escala=1,
                                           idioma="eng") for c in t if c.isdigit()]
                if r:
                    lido = r[0]; break
            if not lido:
                falhou = True; break
            saida += lido
        if falhou or not saida.strip("-."):
            time.sleep(0.8); continue
        return saida
    return None


def escreve_textos(bloco, titulo, corpo="", botao=""):
    """Preenche as tres frases de um bloco `Alert` e fecha no OK.

       Os campos sao achados pelo texto-fantasma do PRIMEIRO ('Title
       Message'); os outros dois saem dali por deslocamento medido, porque
       assim que um campo recebe texto o fantasma some e nao da mais para
       procurar por ele."""
    abre_ajustes(bloco)
    a, _ = nav.captura("/tmp/_bl_alerta.png")
    p = nav.acha_texto("title message", arquivo=a)
    if not p:
        raise RuntimeError("nao achei o campo 'Title Message' do Alert")
    for i, texto in enumerate((titulo, corpo, botao)):
        if not texto:
            continue
        nav.clique_seguro(p[0], p[1] + 84 * i); time.sleep(0.5)
        rs.tecla(0, cmd=True); time.sleep(0.2)
        rs.digita_teclas(texto); time.sleep(0.4)
    a, _ = nav.captura("/tmp/_bl_alerta2.png")
    lido = " ".join(t for t, *_ in rs.ocr_forte(a, psm="6")).lower()
    if titulo.split()[0].lower() not in lido:
        raise RuntimeError(f"escrevi {titulo!r} no Alert e nao li de volta")
    fecha_ajustes()
    return True


def valor_com_botao_menos(bloco, positivo, cliques=1):
    """Escreve um valor POSITIVO e clica no botao `−` do painel.

       E este o gesto que a aula ensina, e nao o truque do cursor: o campo
       engole o hifen quando ele e o primeiro caractere, entao mandar a
       crianca digitar `-0.5` deixaria `0.5` na tela dela — a lava DESCENDO —
       sem nada acusar. O botao `−` tira 1 do valor a cada clique: de `0.5`,
       um clique da `-0.5`.

       Capturar pelo mesmo caminho que a crianca segue e o que faz o clipe
       mostrar o gesto certo."""
    p = abre_ajustes(bloco)
    if not p:
        raise RuntimeError(f"o bloco {bloco.nome} nao tem campo 'Current value'")
    nav.clique_seguro(p[0] + 30, p[1] + 68); time.sleep(0.6)
    rs.tecla(0, cmd=True); time.sleep(0.25)
    rs.digita_teclas(str(positivo)); time.sleep(0.5)
    # o `−` fica na propria linha do campo, bem a direita
    menos = (p[0] + 220, p[1] + 70)
    for _ in range(cliques):
        nav.clique_seguro(*menos); time.sleep(0.7)
    fecha_ajustes()
    esperado = round(float(positivo) - cliques, 6)
    texto = f"{esperado:g}"
    lido = le_valor(bloco)
    if lido != texto:
        raise RuntimeError(f"queria {texto} em {bloco.nome} (digitei {positivo} e "
                           f"cliquei {cliques}x no menos) e o bloco mostra {lido!r}")
    return menos


def bloco_ou_solta(nome, x, y, titulo=None):
    """O bloco, se ele JA estiver na mesa; senao solta um novo ali.

       Uma etapa de captura costuma ser repetida depois de um erro no meio
       dela. Sem isto, a repetição empilha um segundo bloco igual — e o
       segundo nao aparece na foto que a crianca vai comparar."""
    alvo = titulo or nome
    try:
        return acha_bloco(alvo)
    except RuntimeError:
        return solta(nome, x, y, titulo=titulo)


def escolhe_tipo_da_colisao(bloco, tipo):
    """No bloco `Collision`, escolhe COM QUEM a batida conta.

       Sem isto o bloco vem em 'Any Type' e dispara com QUALQUER coisa — e uma
       lava que sobe bate primeiro no CHAO, nao no jogador. O jogo reiniciava
       sozinho a cada poucos segundos e a fase ficava impossivel, sem nada no
       editor acusando. Medido em jogo, nao lido no editor.

       O nome que aparece aqui e o TIPO do objeto (o campo `Type` do painel),
       nao o nome dele — por isso a aula manda escrever `Jogador` nos dois."""
    p = abre_ajustes(bloco)
    a, _ = nav.captura("/tmp/_bl_col0.png")
    q = nav.acha_texto("any type", arquivo=a)
    if not q:
        raise RuntimeError("nao achei a lista de tipos no bloco Collision")
    nav.clique_seguro(q[0], q[1]); time.sleep(1.5)
    a2, _ = nav.captura("/tmp/_bl_col1.png")
    r = nav.acha_texto(tipo.lower(), arquivo=a2, regiao=(0.3, 0.1, 0.6, 0.7))
    if not r:
        raise RuntimeError(f"o tipo {tipo!r} nao aparece na lista do Collision — "
                           "o objeto tem esse nome no campo `Type`?")
    nav.clique_seguro(*r); time.sleep(1.2)
    # FECHA PRIMEIRO. O rotulo embaixo do bloco (onde estava 'Any') so troca
    # depois do OK: conferir com o painel ainda aberto reprovava uma escolha
    # que tinha dado certo. E e esse rotulo que a aula manda a crianca olhar.
    fecha_ajustes()
    for tentativa in range(4):
        time.sleep(1.0)
        b = acha_bloco(bloco.nome)
        a3, _ = nav.captura("/tmp/_bl_col2.png")
        lido = " ".join(t for t, *_ in rs.ocr_forte(
            a3, regiao=b.regiao(folga_esq=60, folga_dir=320,
                                folga_cima=60, folga_baixo=220), psm="6")).lower()
        if tipo.lower() in lido:
            return True
    raise RuntimeError(f"escolhi {tipo!r} e o bloco continua sem mostrar isso "
                       f"(li {lido[:70]!r})")


def prepara_menos(bloco, positivo):
    """Abre os ajustes e deixa o valor POSITIVO digitado, pronto para o `−`.

       Serve para gravar o clipe do gesto certo: com o painel ABERTO nos dois
       quadros. Gravando o gesto inteiro (abrir, digitar, clicar, fechar), o
       antes e o depois mostram os dois o painel FECHADO, e a seta aponta para
       um botao que nao existe em nenhum dos dois — foi o que aconteceu com o
       clipe do passo mais importante da Aula 3.

       Devolve o ponto do botao `−`."""
    p = abre_ajustes(bloco)
    if not p:
        raise RuntimeError(f"o bloco {bloco.nome} nao tem campo 'Current value'")
    nav.clique_seguro(p[0] + 30, p[1] + 68); time.sleep(0.6)
    rs.tecla(0, cmd=True); time.sleep(0.25)
    rs.digita_teclas(str(positivo)); time.sleep(0.5)
    return (p[0] + 220, p[1] + 70)


def clica_menos(ponto, cliques=1):
    """Clica no `−` do painel ja aberto. Nao fecha: quem fecha e o chamador."""
    for _ in range(cliques):
        nav.clique_seguro(*ponto); time.sleep(0.7)
    return ponto
