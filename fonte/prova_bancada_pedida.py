#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prova que, com `BANCADA=1` pedida e os remendos NAO instalados, nenhum
   gesto escapa para a tela de verdade.

   O defeito que isto guarda: quem liga a bancada e `comum.py`. Um script que
   importasse so `nav` e `editor` ficava com a variavel de ambiente ligada e
   NENHUM remendo instalado — e o clique, o arrasto e a foto iam para o
   computador do dono. Fail-open mudo: o ambiente dizia uma coisa, o programa
   fazia outra, sem uma palavra.

       python3 fonte/prova_bancada_pedida.py
"""
import os, subprocess, sys

PASTA = os.path.dirname(os.path.abspath(__file__))

# Cada caso roda num processo SEPARADO: a marca de instalado e de modulo, e um
# caso contaminaria o outro dentro do mesmo interpretador.
CASOS = [
    ("clique sem comum",  "import rs; rs.clique_tela(10, 10)",            True),
    ("tecla sem comum",   "import rs; rs.tecla(53)",                      True),
    ("foto sem comum",    "import rs; rs.captura(arquivo='/tmp/_p.png')", True),
    ("arrasto sem comum", "import rs; rs.arrasta_tela(10, 10, 20, 20)",   True),
    # as duas que escaparam da primeira versao desta guarda
    ("tecla_baixo sem comum", "import rs; rs.tecla_baixo(124)",            True),
    ("tecla_cima sem comum",  "import rs; rs.tecla_cima(124)",             True),
    # o CONTROLE: sem BANCADA pedida, a tela e o caminho certo e nada barra
    ("sem BANCADA pedida", "import rs; rs._exige_bancada_instalada()",    False),
    # e o outro CONTROLE: com os remendos instalados, passa
    ("com a marca ligada",
     "import rs; rs._BANCADA_INSTALADA = True; rs._exige_bancada_instalada()", False),
]


def main():
    falhas = []
    for nome, codigo, deve_barrar in CASOS:
        amb = dict(os.environ)
        amb["BANCADA"] = "0" if nome == "sem BANCADA pedida" else "1"
        r = subprocess.run([sys.executable, "-c",
                            f"import sys; sys.path.insert(0, {PASTA!r}); {codigo}"],
                           capture_output=True, text=True, env=amb, timeout=60)
        barrou = "remendos da bancada NAO estao instalados" in r.stderr
        if barrou != deve_barrar:
            falhas.append(f"{nome}: {'NAO barrou' if deve_barrar else 'barrou sem motivo'}"
                          f" (saida {r.returncode})")
        else:
            print(f"   {nome}: {'barrou' if barrou else 'deixou passar'}", flush=True)
    for f in falhas:
        print("  !!", f)
    print(f"  {len(falhas)} problema(s)")
    return 1 if falhas else 0


if __name__ == "__main__":
    raise SystemExit(main())
