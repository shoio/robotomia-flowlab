#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prova as DUAS metades da porta: nenhum gesto escapa para a tela do dono.

   1. Com `BANCADA=1` pedida e os remendos NAO instalados.
      Quem liga a bancada e `comum.py`. Um script que importasse so `nav` e
      `editor` ficava com a variavel ligada e NENHUM remendo instalado — e o
      clique, o arrasto e a foto iam para o computador do dono. Fail-open
      mudo: o ambiente dizia uma coisa e o programa fazia outra, calado.

   2. Com o motor DE PE e `BANCADA` ausente.
      Esta e a metade que faltava, e e o caso que de fato se repetiu: a
      bandeira escrita para o caso dificil era a unica que nao o cobria. Eu
      rodei tres sondas de diagnostico sem por `BANCADA=1`, fotografei o
      Chrome do dono, cliquei nele e levei a aba dele para a pagina do jogo.

   O motor nao e simulado: a prova ABRE um socket de verdade e aponta
   `BANCADA_PORTA` para ele. Para o caso "motor caido" ela aponta para uma
   porta onde ninguem atende.

       python3 fonte/prova_bancada_pedida.py
"""
import os, socket, subprocess, sys

PASTA = os.path.dirname(os.path.abspath(__file__))

SEM_REMENDO = "remendos da bancada NAO estao instalados"
MOTOR_DE_PE = "esta DE PE"

GESTOS = [
    ("clique",      "rs.clique_tela(10, 10)"),
    ("tecla",       "rs.tecla(53)"),
    ("foto",        "rs.captura(arquivo='/tmp/_p.png')"),
    ("arrasto",     "rs.arrasta_tela(10, 10, 20, 20)"),
    # as duas que escaparam da primeira versao desta guarda
    ("tecla_baixo", "rs.tecla_baixo(124)"),
    ("tecla_cima",  "rs.tecla_cima(124)"),
]


def roda(codigo, **amb_extra):
    amb = {k: v for k, v in os.environ.items() if k not in ("BANCADA", "TELA_DE_VERDADE")}
    amb.update({k: v for k, v in amb_extra.items() if v is not None})
    r = subprocess.run([sys.executable, "-c",
                        f"import sys; sys.path.insert(0, {PASTA!r}); import rs; {codigo}"],
                       capture_output=True, text=True, env=amb, timeout=60)
    return r.stderr


def main():
    # uma porta onde NINGUEM atende, e uma onde alguem atende de verdade
    caida = socket.socket(); caida.bind(("127.0.0.1", 0))
    porta_caida = str(caida.getsockname()[1]); caida.close()
    de_pe = socket.socket(); de_pe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    de_pe.bind(("127.0.0.1", 0)); de_pe.listen(8)
    porta_de_pe = str(de_pe.getsockname()[1])

    casos = []
    # 1) BANCADA pedida, remendos ausentes: todo gesto para
    for nome, codigo in GESTOS:
        casos.append((f"{nome} com BANCADA=1 e sem comum", codigo,
                      dict(BANCADA="1", BANCADA_PORTA=porta_caida), SEM_REMENDO))
    # 2) motor de pe e BANCADA ausente: para tambem, com a OUTRA mensagem
    casos.append(("clique com o motor de pe e sem BANCADA", "rs.clique_tela(10, 10)",
                  dict(BANCADA_PORTA=porta_de_pe), MOTOR_DE_PE))
    casos.append(("foto com o motor de pe e sem BANCADA", "rs.captura(arquivo='/tmp/_p.png')",
                  dict(BANCADA_PORTA=porta_de_pe), MOTOR_DE_PE))

    # ── os CONTROLES: o que tem de continuar passando ─────────────────
    casos.append(("motor CAIDO e sem BANCADA (a tela e o alvo certo)",
                  "rs._exige_bancada_instalada()",
                  dict(BANCADA_PORTA=porta_caida), None))
    casos.append(("motor de pe, sem BANCADA, mas TELA_DE_VERDADE=1",
                  "rs._exige_bancada_instalada()",
                  dict(BANCADA_PORTA=porta_de_pe, TELA_DE_VERDADE="1"), None))
    casos.append(("BANCADA=1 com a marca ligada e o motor de pe",
                  "rs._BANCADA_INSTALADA = True; rs._exige_bancada_instalada()",
                  dict(BANCADA="1", BANCADA_PORTA=porta_de_pe), None))

    falhas = []
    try:
        for nome, codigo, amb, esperado in casos:
            err = roda(codigo, **amb)
            if esperado is None:
                if SEM_REMENDO in err or MOTOR_DE_PE in err:
                    falhas.append(f"{nome}: barrou sem motivo")
                else:
                    print(f"   {nome}: deixou passar", flush=True)
            elif esperado in err:
                print(f"   {nome}: barrou", flush=True)
            else:
                outra = SEM_REMENDO if esperado is MOTOR_DE_PE else MOTOR_DE_PE
                falhas.append(f"{nome}: NAO barrou"
                              + (" (barrou pela OUTRA razao)" if outra in err else ""))
    finally:
        de_pe.close()

    for f in falhas:
        print("  !!", f)
    print(f"  {len(falhas)} problema(s)")
    return 1 if falhas else 0


if __name__ == "__main__":
    raise SystemExit(main())
