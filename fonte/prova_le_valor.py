#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prova, SEM TELA, que `blocos.le_valor` le o numero de um bloco com o sinal.

   Por que existe: o hifen do Flowlab e uma barrinha curta; o tesseract come
   ou inventa. O sinal vem da GEOMETRIA (a mancha azul mais a esquerda, baixa
   e larga, e o menos). Ler '-1.7' como '1.7' deixaria a lava DESCENDO com o
   guarda verde — por isso o caso NEGATIVO e o controle que importa.

       python3 fonte/prova_le_valor.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import blocos, nav

CASOS = [("provas/numero_positivo.png", "0.3"),
         ("provas/numero_negativo.png", "-1.7")]
# o recorte guardado comeca em (1235, 842) da captura inteira
DX, DY = 1235, 842
BLOCO = (1295 - DX, 872 - DY)


def main():
    erros = []
    for arquivo, esperado in CASOS:
        nav.captura = lambda destino=None, _a=arquivo: (_a, 2.0)
        blocos.acha_bloco = lambda nome, **kw: blocos.Bloco("Number", *BLOCO)
        lido = blocos.le_valor(blocos.Bloco("Number", *BLOCO))
        ok = lido == esperado
        print(f"  {arquivo:<32} li {lido!r:>8}  esperava {esperado!r:>8}  "
              f"{'ok' if ok else '!! ERRADO'}")
        if not ok:
            erros.append(arquivo)
    print(f"  {len(erros)} problema(s)")
    raise SystemExit(1 if erros else 0)


if __name__ == "__main__":
    main()
