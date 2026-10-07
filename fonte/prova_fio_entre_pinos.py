#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PROVA: o detector de fio nao pode contar o fio do VIZINHO.

   O defeito, medido ao vivo: `liga_fixo` aprovou `Timer.out -> Destroyer.in`
   e o fio NUNCA existiu. O Flowlab tinha recusado a ligacao, porque a entrada
   `in` do `Destroyer` ja tinha um fio vindo do `Keyboard` — e era esse fio,
   cruzando a mesma regiao, que o detector contava.

   O custo possivel: uma aula publicada com um fio faltando, com a captura
   dizendo que ligou. Foi exatamente assim que a Aula 2 foi ao ar com um
   boneco que nao pulava.

   O invariante que separa os dois casos e o pedacinho logo DEPOIS do pino: o
   fio sai dele na horizontal. A foto `mesa_fio_timer.png` tem os dois casos
   lado a lado, a 53 px um do outro:

     Timer.out  -> Destroyer.in   ligado   (o fio esta desenhado)
     Timer.done -> Destroyer.in   NAO ligado

   Os dois pares atravessam quase a mesma regiao da mesa. Se o detector
   acertar os dois nesta foto, ele nao esta contando vizinho.

       python3 fonte/prova_fio_entre_pinos.py
"""
import os, sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import blocos

FOTO = "provas/fotos/mesa_fio_timer.png"
TIMER = (1024, 626)
DESTRUIDOR = (1745, 404)
OUT = (TIMER[0] + 247, TIMER[1] + 50)
DONE = (TIMER[0] + 247, TIMER[1] + 103)
ENTRADA = (DESTRUIDOR[0] - 28, DESTRUIDOR[1] + 57)


def main():
    erros = []

    ligado = blocos._ha_fio(FOTO, OUT, ENTRADA)
    print(f"Timer.out  -> Destroyer.in : {ligado}  (esperado True)")
    if not ligado:
        erros.append("o detector deixou de ver um fio que ESTA desenhado")

    solto = blocos._ha_fio(FOTO, DONE, ENTRADA)
    print(f"Timer.done -> Destroyer.in : {solto}  (esperado False)")
    if solto:
        erros.append("o detector conta o fio do VIZINHO: `done` nao esta ligado")

    # ── o pedacinho depois do pino, medido ────────────────────────────
    im = np.asarray(Image.open(FOTO).convert("L"), dtype=int)
    for nome, p, esperado in (("out", OUT, True), ("done", DONE, False)):
        sai = blocos._toca_o_pino(im, p, "dir")
        print(f"sai fio de Timer.{nome}: {sai}  (esperado {esperado})")
        if sai != esperado:
            erros.append(f"`_toca_o_pino` errou o pino {nome}")

    # ── SABOTAGEM: sem a conferencia do pino, o defeito volta ─────────
    original = blocos._toca_o_pino
    blocos._toca_o_pino = lambda *a, **k: True
    try:
        voltou = blocos._ha_fio(FOTO, DONE, ENTRADA)
    finally:
        blocos._toca_o_pino = original
    print(f"\nSABOTAGEM (sem conferir o pino): {voltou}  (esperado True — e o defeito)")
    if not voltou:
        erros.append("a sabotagem nao reproduziu o defeito: esta prova nao esta "
                     "medindo o que diz medir")

    if erros:
        for e in erros:
            print("  ERRO:", e)
        raise SystemExit(1)
    print("\nprova ok")


if __name__ == "__main__":
    main()
