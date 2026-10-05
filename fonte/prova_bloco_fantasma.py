#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prova, SEM tela, que um bloco que nunca foi achado nao chega a ser usado.

   O defeito que isto guarda: na Aula 3 o `Collision` nunca nasceu na mesa. O
   arrasto rolou a mesa, o guarda por PIXEL ("perto de onde soltei mudou
   alguma coisa") aprovou, e `solta` devolveu um Bloco inventado nas
   coordenadas onde eu tinha MIRADO. O fantasma viajou calado por dois gestos
   e so estourou em `liga_fixo`, com a mensagem errada — "nenhum fio apareceu",
   quando o problema era que nao havia bloco nenhum de onde puxar o fio.

   A sabotagem: fabrico o fantasma na mao e cobro reprovacao nas QUATRO portas
   por onde a coordenada de um bloco e usada.

       python3 fonte/prova_bloco_fantasma.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blocos

PORTAS = [
    ("Bloco.pino",      lambda b: b.pino("hit", "dir")),
    ("pino_por_nome",   lambda b: blocos.pino_por_nome(b, "hit", "dir")),
    ("pino_fixo",       lambda b: blocos.pino_fixo(b, "hit", "dir")),
    ("abre_ajustes",    lambda b: blocos.abre_ajustes(b)),
]


def main():
    falhas = []

    # 1) o fantasma: tem de reprovar em todas as portas, com a razao certa
    for nome, usar in PORTAS:
        fantasma = blocos.Bloco("Collision", 1120, 1220, confirmado=False)
        try:
            usar(fantasma)
            falhas.append(f"{nome}: ACEITOU um bloco nunca achado")
        except RuntimeError as e:
            if "nunca foi achado" not in str(e):
                falhas.append(f"{nome}: reprovou por outro motivo — {e}")
            else:
                print(f"   {nome}: reprovou o fantasma", flush=True)
        except Exception as e:
            falhas.append(f"{nome}: estourou errado ({type(e).__name__}: {e})")

    # 2) o CONTROLE: um bloco achado de verdade nao pode ser barrado por este
    #    guarda. Sem isto eu teria um guarda que reprova tudo e parece verde.
    for nome, usar in PORTAS:
        real = blocos.Bloco("Collision", 1120, 1220)
        try:
            usar(real)
        except Exception as e:
            if "nunca foi achado" in str(e):
                falhas.append(f"{nome}: barrou um bloco ACHADO")
                continue
        print(f"   {nome}: deixou passar o bloco achado", flush=True)

    # 3) e a marca aparece no repr, para quem for ler um log
    if "NAO-ACHADO" not in repr(blocos.Bloco("X", 1, 1, confirmado=False)):
        falhas.append("o repr nao mostra que o bloco nao foi achado")
    if "NAO-ACHADO" in repr(blocos.Bloco("X", 1, 1)):
        falhas.append("o repr marca um bloco que FOI achado")

    for f in falhas:
        print("  !!", f)
    print(f"  {len(falhas)} problema(s)")
    return 1 if falhas else 0


if __name__ == "__main__":
    raise SystemExit(main())
