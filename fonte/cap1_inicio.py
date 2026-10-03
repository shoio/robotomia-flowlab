#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Captura os PRIMEIROS passos da Aula 1, que a cap1.novo fazia sem fotografar:
   abrir o Flowlab, My Games, + New Game e escolher Empty Project.

   Cria um jogo extra de proposito (so para a foto); ele pode ser apagado
   depois, e esta anotado no ESTADO.md."""
import os, sys, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rs, nav, editor, cap1

A = cap1.A


def main():
    nav.vai("https://flowlab.io/", espera=4); nav.fecha_dialogo()
    A.cap("p00_site")
    p = nav.acha_texto("my games", regiao=(0.5, 0, 1, 0.12))
    A.gesto("abrir_my_games", "g10", p, lambda: cap1.clique(*p), espera=4)
    editor.espera_tela("new game", "my games", limite=25)
    A.cap("p00b_lista")
    q = nav.acha_cor(editor.VERDE, regiao=(0.5, 0.05, 1, 0.30), minimo=400)
    A.gesto("novo_jogo", "g11", (q[0], q[1]), lambda: cap1.clique(q[0], q[1]), espera=6)
    editor.espera_tela("empty project", limite=25)
    A.cap("p00c_escolher")
    A.gesto("empty_project", "g12", (1272, 860), lambda: cap1.clique(1272, 860), espera=5)
    editor.espera_tela("library", "play", limite=25)
    A.cap("p00d_editor_vazio")
    print("   primeiros passos capturados; jogo extra:", nav.endereco(), flush=True)


if __name__ == "__main__":
    main()
