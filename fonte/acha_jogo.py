#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Descobre QUAL jogo da conta e o de uma aula, comparando o nivel com a foto.

   Por que isto existe: o endereco do jogo de cada aula era impresso durante a
   captura e nunca guardado. Na conta todos se chamam `New Game` e nenhum tem
   miniatura — nao ha como saber qual e qual pelo nome. Eu fui regravar um
   clipe da Aula 2 e abri o RASCUNHO que eu tinha usado para medir, porque o
   unico numero escrito em algum lugar era o do comentario do codigo.

   A partir de agora `capN.py` grava o endereco em `aulaN/jogo.txt`. Isto aqui
   e para os que ja existiam.

       BANCADA=1 python3 fonte/acha_jogo.py aula2
"""
import os, sys, time
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rs, nav, editor, comum

os.chdir(os.path.dirname(os.path.abspath(__file__)))
GRADE = (comum.GRADE_X, comum.GRADE_Y,
         comum.GRADE_X + comum.CELULA * 16, comum.GRADE_Y + comum.CELULA * 12)


def pinta_do_nivel(arquivo):
    """A assinatura do nivel: quanto de cada cor, casa por casa."""
    im = np.asarray(Image.open(arquivo).convert("RGB"), dtype=int)
    x0, y0, x1, y1 = GRADE
    rec = im[y0:y1, x0:x1]
    verde = (rec[:, :, 1] > 140) & (rec[:, :, 1] - rec[:, :, 0] > 40) & (rec[:, :, 2] < 130)
    azul = (rec[:, :, 2] > 100) & (rec[:, :, 2] - rec[:, :, 0] > 40) & (rec[:, :, 1] < 120)
    amar = (rec[:, :, 0] > 190) & (rec[:, :, 1] > 130) & (rec[:, :, 1] < 210) & (rec[:, :, 2] < 120)
    verm = (rec[:, :, 0] > 150) & (rec[:, :, 0] - rec[:, :, 1] > 60) & (rec[:, :, 2] < 120)
    C = comum.CELULA
    assinatura = []
    for m in (verde, azul, amar, verm):
        grade = m.reshape(12, C, 16, C).sum(axis=(1, 3)) > (C * C * 0.4)
        assinatura.append(grade)
    return np.stack(assinatura)


def parecido(a, b):
    """Fracao das casas que batem entre duas assinaturas."""
    return float((a == b).mean())


def procura(aula, ids, foto):
    alvo = pinta_do_nivel(foto)
    print(f"procurando o jogo da {aula} (referencia: {foto})", flush=True)
    melhor = (0.0, None)
    for n in ids:
        try:
            nav.vai(f"https://flowlab.io/game/view/{n}", espera=7)
            editor.espera_tela("library", "game levels", limite=30)
            time.sleep(1.5)
            a, _ = nav.captura("/tmp/_aj.png")
            s = parecido(pinta_do_nivel(a), alvo)
        except Exception as e:
            print(f"  {n}: nao abriu ({str(e)[:40]})", flush=True)
            continue
        print(f"  {n}: {s*100:.1f}% igual", flush=True)
        if s > melhor[0]:
            melhor = (s, n)
    print(f"\nmelhor: {melhor[1]} com {melhor[0]*100:.1f}%")
    return melhor


if __name__ == "__main__":
    aula = sys.argv[1] if len(sys.argv) > 1 else "aula2"
    ids = sys.argv[2:] or ["3150184", "3150182", "3150181", "3150180", "3150179",
                           "3150178", "3150177", "3150176", "3150175", "3150174",
                           "3150173", "3150051"]
    fotos = {"aula2": "aula2/p15_fase_pronta.jpg", "aula3": "aula3/p20_fase_pronta.jpg"}
    procura(aula, ids, fotos[aula])
