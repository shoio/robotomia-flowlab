#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prova, SEM TELA, que `comum._caixinha` acha a caixinha certa de cada rotulo
   do painel de fisica, e le se ela esta marcada.

   Por que existe: o deslocamento fixo de 90 px que eu usava antes so valia
   para `movable`. O rotulo e achado pelo CENTRO do texto, e o centro anda com
   o tamanho da palavra — para `affected by gravity` os 90 px caiam no FUNDO
   do painel, a leitura dava 'desmarcada', e a funcao voltava True sem ter
   clicado em nada. Guarda que aprova sem olhar e pior do que guarda nenhum.

       python3 fonte/prova_caixinha.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import comum

ARQUIVO = "provas/painel_fisica.png"
DX, DY = 640, 220                      # de onde o recorte foi tirado
# (rotulo, x da caixinha na captura inteira, marcada?)
CASOS = [("movable", 777, True),
         ("affected by gravity", 1097, False),
         ("is solid", 777, True),
         ("allow spin", 1093, False)]


def main():
    erros = []
    for rotulo, x_real, marcada in CASOS:
        p = comum._acha_no_painel(rotulo, ARQUIVO)
        if not p:
            erros.append(rotulo)
            print(f"  {rotulo:<22} nao achei o rotulo                 !! ERRADO")
            continue
        c = comum._caixinha(ARQUIVO, p)
        ok = bool(c) and c[2] == marcada and abs(c[0] - (x_real - DX)) <= 14
        if not ok:
            erros.append(rotulo)
        print(f"  {rotulo:<22} achei={c} esperava x~{x_real - DX} marcada={marcada}"
              f"  {'ok' if ok else '!! ERRADO'}")
    print(f"  {len(erros)} problema(s)")
    raise SystemExit(1 if erros else 0)


if __name__ == "__main__":
    main()
