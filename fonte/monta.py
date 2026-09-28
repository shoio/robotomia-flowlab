#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monta o obby de verdade no Roblox Studio, capturando e anotando cada passo.
   Toda anotação é MEDIDA por diferença de imagem — nenhuma é chutada."""
import os, time, json
from PIL import Image, ImageChops
import rs, anota

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aula1")
os.makedirs(D, exist_ok=True)
JAN = None
REG3D = (0, 340, 2550, 1720)          # área do mundo 3D, em pixels da captura


def jan():
    global JAN
    JAN = rs.principal()
    return JAN


def cap(nome):
    a, _ = rs.captura(JAN["id"], f"{D}/{nome}.png")
    return f"{D}/{nome}.png"


def mudou(antes, depois, regiao=REG3D, limiar=90, passo=2):
    """Devolve (cx, cy, x0, y0, x1, y1) do que mudou entre duas capturas."""
    a = Image.open(antes).convert("RGB").crop(regiao)
    b = Image.open(depois).convert("RGB").crop(regiao)
    dif = ImageChops.difference(a, b)
    px = dif.load()
    xs, ys = [], []
    for y in range(0, dif.height, passo):
        for x in range(0, dif.width, passo):
            r, g, bl = px[x, y]
            if r + g + bl > limiar:
                xs.append(x); ys.append(y)
    if not xs:
        return None
    ox, oy = regiao[0], regiao[1]
    x0, x1 = min(xs) + ox, max(xs) + ox
    y0, y1 = min(ys) + oy, max(ys) + oy
    return ((x0 + x1) // 2, (y0 + y1) // 2, x0, y0, x1, y1)


def marca_mudanca(img_depois, m, texto, saida, lado="baixo"):
    """Circula o que mudou e põe um rótulo ao lado."""
    im = anota.abrir(img_depois)
    cx, cy, x0, y0, x1, y1 = m
    r = max(x1 - x0, y1 - y0) // 2 + 34
    anota.circulo(im, cx, cy, r=r, larg=8)
    if lado == "baixo":
        tx, ty = max(30, cx - 240), min(im.height - 120, cy + r + 40)
    elif lado == "cima":
        tx, ty = max(30, cx - 240), max(30, cy - r - 110)
    else:
        tx, ty = min(im.width - 700, cx + r + 40), cy - 30
    anota.rotulo(im, tx, ty, texto)
    im.save(saida)
    return saida


def marca_alvo(img, x, y, texto, saida, r=52, dir_seta=None):
    """Circula um alvo de clique conhecido e rotula."""
    im = anota.abrir(img)
    anota.circulo(im, x, y, r=r, larg=8)
    if dir_seta:
        anota.seta(im, dir_seta[0], dir_seta[1], x, y + r + 16)
    anota.rotulo(im, max(30, x - 260), min(im.height - 130, y + r + 46), texto)
    im.save(saida)
    return saida


def recorta(src, saida, box, escala=1.0):
    im = Image.open(src).convert("RGB").crop(box)
    if escala != 1.0:
        im = im.resize((int(im.width * escala), int(im.height * escala)), Image.LANCZOS)
    im.save(saida)
    return saida


# ── pontos medidos na faixa de ferramentas (aba Modelo), em pixels da captura ──
BOTAO = {
    "Selecionar": (68, 118), "Mover": (173, 118), "Dimensionar": (290, 118),
    "Girar": (408, 118), "Transformar": (522, 118),
    "Parte": (1269, 118), "Material": (1841, 118), "Cor": (1946, 118),
    "Grupo": (2154, 118), "Bloquear": (2258, 118), "Âncora": (2362, 118),
}
ABA = {"Início": (966, 36), "Modelo": (1639, 36), "Teste": (60, 36),
       "Avatar": (1133, 36), "Script": (1471, 36)}


def acha_botao(nome, tol=6):
    """Localiza um botao da faixa PELO TEXTO e devolve o ponto do ICONE.
       A faixa se reorganiza, e a janela pode ganhar ou perder a barra de
       titulo — entao nem a coluna nem a linha podem ser fixas. Procuro o
       rotulo numa faixa generosa e subo 42 px ate o desenho."""
    a = cap("_btn")
    from PIL import Image as _I
    L, A = _I.open(a).size
    alvo = nome.lower()
    faixa = (0, 110 / A, 1, 300 / A)
    for t, x, y, w, h in rs.ocr(a, regiao=faixa, psm="11"):
        tl = t.strip().lower()
        if tl == alvo or (len(alvo) > 4 and alvo in tl):
            return (x + w // 2, y - 42)
    return None


def clica(nome_botao, espera=1.6):
    p = acha_botao(nome_botao)
    if p is None:
        raise RuntimeError(f"botao '{nome_botao}' nao encontrado na faixa atual")
    rs.clique_img(p[0], p[1], escala=2.0, janela=JAN)
    time.sleep(espera)
    return p


def clica_aba(nome, espera=1.2):
    x, y = ABA[nome]
    rs.clique_img(x, y, escala=2.0, janela=JAN)
    time.sleep(espera)
    return (x, y)


def explorer_pos(nome):
    """Acha um item pelo nome no Explorador. Devolve (x,y) em pixels da captura."""
    a = cap("_tmp_exp")
    for t, x, y, w, h in rs.ocr(a, regiao=(0.86, 0.13, 1, 0.58), psm="6", escala=2):
        if t.strip() == nome:
            return (x + w // 2, y + h // 2)
    return None
