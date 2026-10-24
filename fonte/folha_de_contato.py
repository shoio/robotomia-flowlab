#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monta UMA imagem com tudo o que a aula mostra, para o olho conferir de uma vez.

   Por que existe: nesta noite o olho achou dois defeitos que nenhum guarda
   via, e os dois so apareceram quando as figuras ficaram LADO A LADO.

   - `lava_movable.gif` mostrava o nivel BRANCO no meio de dezesseis clipes de
     ceu escuro: era de uma captura de tres dias antes. O arquivo existia,
     abria, e a seta apontava para onde a tela tinha mudado.
   - tres passos da Aula 2 mostravam o cenario PRONTO onde o texto promete o
     cenario pela metade, porque eu reexecutei etapas do meio num jogo
     completo.

   Nenhum dos dois tem assinatura mecanica obvia. O que os denuncia e a
   PROGRESSAO: a aula conta uma historia, e as figuras tem de contar a mesma.

       python3 fonte/folha_de_contato.py aula2
       python3 fonte/folha_de_contato.py aula3 /tmp/a3.png
"""
import os, sys
from PIL import Image, ImageDraw

os.chdir(os.path.dirname(os.path.abspath(__file__)))
import gera_curso as G

CEL = (420, 236)
COLS = 4


def _ultimo_quadro(cam):
    im = Image.open(cam)
    try:
        im.seek(im.n_frames - 1)
    except Exception:
        pass
    return im.convert("RGB")


def monta(slug, saida=None):
    mod = __import__("conteudo_a" + slug.replace("aula", ""))   # `slug[-1]` lia so o ultimo digito: aula10 virava a0
    A = mod.AULA
    pecas = []
    for p in A["passos"]:
        img = p.get("img")
        if img and os.path.exists(img):
            pecas.append((f'{p["n"]}· foto {os.path.basename(img)}', img))
        elif img:
            pecas.append((f'{p["n"]}· foto {os.path.basename(img)}', None))
        for rot, cl in G.clipes_do(p):
            cam = os.path.join(slug, "gifs", cl)
            pecas.append((f'{p["n"]}· {cl}', cam if os.path.exists(cam) else None))

    linhas = (len(pecas) + COLS - 1) // COLS
    folha = Image.new("RGB", (COLS * CEL[0], linhas * (CEL[1] + 18)), (24, 24, 30))
    d = ImageDraw.Draw(folha)
    for i, (rotulo, cam) in enumerate(pecas):
        x, y = (i % COLS) * CEL[0], (i // COLS) * (CEL[1] + 18)
        d.text((x + 4, y + 3), rotulo[:52], fill=(190, 190, 205))
        if cam is None:
            d.text((x + 8, y + 80), "AUSENTE", fill=(255, 90, 90))
            continue
        im = _ultimo_quadro(cam) if cam.endswith(".gif") else Image.open(cam).convert("RGB")
        im.thumbnail(CEL)
        folha.paste(im, (x, y + 16))
    saida = saida or f"/tmp/contato_{slug}.png"
    folha.save(saida)
    print(f"  {len(pecas)} figuras -> {saida}")
    return saida


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    monta(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
