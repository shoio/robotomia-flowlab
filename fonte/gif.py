#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monta GIFs a partir das capturas REAIS do Studio.
   O cursor é desenhado por cima; as telas são fotografias do aplicativo."""
import os, math
from PIL import Image, ImageDraw

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aula1")
OUT = os.path.join(D, "gifs")
os.makedirs(OUT, exist_ok=True)


def cursor(im, x, y, escala=1.0):
    """Desenha uma seta de mouse em (x,y)."""
    d = ImageDraw.Draw(im, "RGBA")
    s = 34 * escala
    p = [(x, y), (x, y + s), (x + .26*s, y + .74*s), (x + .46*s, y + 1.12*s),
         (x + .62*s, y + 1.03*s), (x + .43*s, y + .66*s), (x + .72*s, y + .64*s)]
    d.polygon(p, fill=(255, 255, 255, 255), outline=(20, 20, 24, 255))
    d.line(p + [p[0]], fill=(20, 20, 24, 255), width=max(1, int(2*escala)), joint="curve")
    return im


def anel(im, x, y, r, alpha=220, larg=7):
    d = ImageDraw.Draw(im, "RGBA")
    d.ellipse([x-r, y-r, x+r, y+r], outline=(232, 60, 60, alpha), width=larg)
    return im


def _prep(caminho, box, larg):
    im = Image.open(caminho).convert("RGB")
    if box:
        im = im.crop(box)
    if larg and im.width != larg:
        im = im.resize((larg, round(im.height * larg / im.width)), Image.LANCZOS)
    return im


def gesto(nome, antes, depois, alvo, box=None, larg=900,
          origem=None, n_mov=9, n_clique=3, n_fim=7, ms=110):
    """antes/depois = arquivos; alvo = (x,y) em pixels da captura ORIGINAL."""
    a0 = Image.open(os.path.join(D, antes)).convert("RGB")
    esc = larg / (box[2]-box[0] if box else a0.width)
    ox, oy = (box[0], box[1]) if box else (0, 0)
    ax, ay = (alvo[0]-ox)*esc, (alvo[1]-oy)*esc
    A = _prep(os.path.join(D, antes), box, larg)
    B = _prep(os.path.join(D, depois), box, larg)
    if origem is None:
        origem = (max(20, ax - 240), min(A.height - 40, ay + 200))
    q = []
    # cursor andando
    for k in range(n_mov):
        t = k / max(1, n_mov - 1)
        t = t*t*(3-2*t)                      # suaviza
        f = A.copy()
        cursor(f, origem[0] + (ax-origem[0])*t, origem[1] + (ay-origem[1])*t)
        q.append(f)
    # clique
    for k in range(n_clique):
        f = A.copy()
        anel(f, ax, ay, 14 + k*14, alpha=220 - k*60)
        cursor(f, ax, ay)
        q.append(f)
    # resultado
    for k in range(n_fim):
        f = B.copy()
        if k < 2:
            anel(f, ax, ay, 44 + k*16, alpha=150 - k*60, larg=5)
        cursor(f, ax, ay)
        q.append(f)
    return _grava(nome, q, ms)


def _grava(nome, quadros, ms, cores=200):
    """Paleta unica + disposal=1: o PIL grava so o retangulo que mudou.
       A paleta se calcula sobre quadros ESPALHADOS pelo clipe — amostrar so
       o primeiro e o ultimo deixava a paleta de cores do Studio acinzentada."""
    n = len(quadros)
    amostras = sorted({0, n//5, 2*n//5, 3*n//5, 4*n//5, n-1})
    w, h = quadros[0].size
    tira = Image.new("RGB", (w, h*len(amostras)))
    for k, i in enumerate(amostras):
        tira.paste(quadros[i], (0, h*k))
    base = tira.quantize(colors=cores, method=Image.MEDIANCUT)
    pal = [q.quantize(palette=base, dither=Image.NONE) for q in quadros]
    cam = os.path.join(OUT, nome)
    pal[0].save(cam, save_all=True, append_images=pal[1:], duration=ms,
                loop=0, optimize=True, disposal=1)
    return cam, len(pal), os.path.getsize(cam)


def arraste(nome, antes, depois, de, ate, box=None, larg=900, n=12, ms=110):
    """Arrasto: o cursor pressionado vai de 'de' ate 'ate' sobre a tela ANTES,
       deixando um rastro; a tela DEPOIS entra so no fim (nada de fantasma)."""
    a0 = Image.open(os.path.join(D, antes)).convert("RGB")
    esc = larg / (box[2]-box[0] if box else a0.width)
    ox, oy = (box[0], box[1]) if box else (0, 0)
    dx, dy = (de[0]-ox)*esc, (de[1]-oy)*esc
    tx, ty = (ate[0]-ox)*esc, (ate[1]-oy)*esc
    A = _prep(os.path.join(D, antes), box, larg)
    B = _prep(os.path.join(D, depois), box, larg)
    q = []
    for _ in range(4):
        f = A.copy(); cursor(f, dx, dy); q.append(f)
    for k in range(n):
        t = (k+1)/n
        f = A.copy()
        d = ImageDraw.Draw(f, "RGBA")
        d.line([dx, dy, dx + (tx-dx)*t, dy + (ty-dy)*t], fill=(232,60,60,210), width=6)
        cursor(f, dx + (tx-dx)*t, dy + (ty-dy)*t)
        q.append(f)
    for k in range(8):
        f = B.copy()
        if k < 2:
            anel(f, tx, ty, 30 + k*16, alpha=170 - k*70, larg=5)
        cursor(f, tx, ty)
        q.append(f)
    return _grava(nome, q, ms)


def sequencia(nome, passos, box=None, larg=900, ms=110, n_mov=8, n_fim=8,
              origem=None, extras=None):
    """passos = [(arquivo, alvo|None), ...]. O cursor caminha ate o alvo do passo,
       clica, e so entao a tela do passo SEGUINTE aparece.
       extras = arquivos extras exibidos no fim (ex.: jogo rodando)."""
    prim = Image.open(os.path.join(D, passos[0][0]))
    esc = larg / (box[2]-box[0] if box else prim.width)
    ox, oy = (box[0], box[1]) if box else (0, 0)
    conv = lambda p: ((p[0]-ox)*esc, (p[1]-oy)*esc)
    telas = [_prep(os.path.join(D, a), box, larg) for a, _ in passos]
    q = []
    cur = conv(origem) if origem else None
    for i, (_, alvo) in enumerate(passos):
        if alvo is None:
            continue
        ax, ay = conv(alvo)
        if cur is None:
            cur = (max(20, ax-260), min(telas[i].height-40, ay+220))
        for k in range(n_mov):
            t = k/max(1, n_mov-1); t = t*t*(3-2*t)
            f = telas[i].copy()
            cursor(f, cur[0]+(ax-cur[0])*t, cur[1]+(ay-cur[1])*t)
            q.append(f)
        for k in range(3):                       # o clique
            f = telas[i].copy()
            anel(f, ax, ay, 14+k*14, alpha=220-k*60)
            cursor(f, ax, ay)
            q.append(f)
        cur = (ax, ay)
    fim = telas[-1]
    for k in range(n_fim):
        f = fim.copy()
        if k < 2 and cur:
            anel(f, cur[0], cur[1], 44+k*16, alpha=150-k*60, larg=5)
        if cur: cursor(f, *cur)
        q.append(f)
    for extra in (extras or []):
        e = _prep(os.path.join(D, extra), box, larg)
        for _ in range(4):
            f = e.copy()
            if cur: cursor(f, *cur)
            q.append(f)
    return _grava(nome, q, ms)
