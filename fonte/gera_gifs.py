#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monta os clipes de uma aula a partir do `alvos.json` que a captura gravou.

   Cada entrada traz o quadro ANTES, o quadro DEPOIS, o PONTO do clique e
   QUAL BOTAO foi usado — e e dai que sai a animacao com o mouse do botao
   aceso, que e como a crianca sabe se e clique comum ou botao direito.

       python3 fonte/gera_gifs.py aula1
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import gif

# recorte e largura de saida por tipo de tela, para o clipe nao sair minusculo
LARGURA = 900


def monta(pasta, so=None):
    gif.D = pasta
    gif.OUT = os.path.join(pasta, "gifs")
    os.makedirs(gif.OUT, exist_ok=True)
    alvos = json.load(open(os.path.join(pasta, "alvos.json")))
    feitos = []
    for chave, c in sorted(alvos.items()):
        if so and chave != so:
            continue
        antes, depois = c["antes"], c["depois"]
        for f in (antes, depois):
            if not os.path.exists(os.path.join(pasta, f)):
                raise SystemExit(f"{chave}: falta o quadro {f}")
        saida = f"{chave}.gif"
        nome, quadros, bytes_ = gif.gesto(saida, antes, depois, c["alvo"],
                                          larg=LARGURA, botao=c.get("botao", "esq"))
        feitos.append((saida, quadros, bytes_, c.get("botao", "esq")))
    return feitos


if __name__ == "__main__":
    pasta = sys.argv[1] if len(sys.argv) > 1 else "aula1"
    so = sys.argv[2] if len(sys.argv) > 2 else None
    for nome, q, b, botao in monta(pasta, so):
        print(f"  {nome:<26} {q:>3} quadros  {b//1024:>4} KB  botao {botao}")
