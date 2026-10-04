#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monta um jogo de rascunho para PROVAR as mecanicas da Aula 2 antes de
   escrever a aula: o pulo e o 'caiu, recomeca'."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rs, nav, editor, blocos, comum
from comum import celula, clique, pinta, nomeia, abre_sprite, marca_caixa, \
                  arrasta_slider, fecha_painel_objeto, A

comum.pasta("rascunho2")


def faz_objeto(c, r, nome, cor, pesado=False):
    x, y = celula(c, r)
    editor.objeto_ou_abre(x, y)
    nomeia(nome)
    abre_sprite(); pinta(cor)
    clique(*comum.SPRITE_OK); time.sleep(2); nav.espera_parar(limite=15)
    if pesado:
        a, _ = nav.captura("/tmp/_e2.png")
        q = nav.acha_texto("physics", arquivo=a)
        clique(*q); time.sleep(2.5); nav.espera_parar(limite=15)
        marca_caixa("movable", True)
        arrasta_slider("density"); arrasta_slider("friction")
    fecha_painel_objeto()
    return True


def main():
    url = editor.jogo_novo()
    print("rascunho:", url, flush=True)
    faz_objeto(5, 7, "Jogador", "azul", pesado=True)
    # chao de 4 a 12 na linha 8
    x, y = celula(4, 8)
    editor.objeto_ou_abre(x, y); nomeia("Chao"); abre_sprite(); pinta("verde")
    clique(*comum.SPRITE_OK); time.sleep(2); nav.espera_parar(limite=15)
    fecha_painel_objeto()
    clique(x, y); time.sleep(1.5)
    a, _ = nav.captura("/tmp/_e2b.png")
    p = nav.acha_texto("clone", arquivo=a)
    clique(*p); time.sleep(2)
    for c in range(5, 13):
        cx, cy = celula(c, 8); clique(cx, cy); time.sleep(1.0)
    q = nav.acha_texto("done cloning"); clique(*q); time.sleep(2)
    nav.espera_parar(limite=15)
    # o pacote de movimento no jogador
    x, y = celula(5, 7)
    editor.objeto_ou_abre(x, y); editor.abre_comportamentos()
    blocos.abre_categoria("Behavior Bundles")
    blocos.solta("Run & Jump", 1400, 700)
    time.sleep(2.5); editor.fecha_comportamentos(); time.sleep(2.5)
    fecha_painel_objeto()
    print("rascunho montado", flush=True)


if __name__ == "__main__":
    main()
