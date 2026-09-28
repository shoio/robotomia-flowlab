#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mantem a tela ACESA e DESTRAVADA enquanto a captura roda a noite.

   Nao basta ligar o caffeinate uma vez: se ele morrer, a tela dorme e o
   bloqueio entra atras dela — e captura com sessao bloqueada devolve quadro
   preto. Este vigia re-arma o caffeinate, reafirma o protetor de tela
   desligado, e escreve uma linha a cada MUDANCA.
"""
import subprocess, time, sys

def rodando():
    r = subprocess.run(["pgrep", "-f", "caffeinate -disu"], capture_output=True, text=True)
    return bool(r.stdout.strip())

def bloqueada():
    import Quartz
    d = Quartz.CGSessionCopyCurrentDictionary() or {}
    return bool(d.get("CGSSessionScreenIsLocked"))

def tela_presa():
    r = subprocess.run(["pmset", "-g", "assertions"], capture_output=True, text=True)
    return "PreventUserIdleDisplaySleep    1" in r.stdout

def main(saida):
    f = open(saida, "a", buffering=1)
    anterior = None
    while True:
        try:
            if not rodando():
                subprocess.Popen(["caffeinate", "-disu", "-t", "43200"],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                f.write(f"{time.strftime('%d-%m %H:%M:%S')}  RE-ARMEI o caffeinate\n")
                time.sleep(2)
            subprocess.run(["defaults", "-currentHost", "write", "com.apple.screensaver",
                            "idleTime", "-int", "0"], capture_output=True)
            estado = (tela_presa(), bloqueada())
            if estado != anterior:
                f.write(f"{time.strftime('%d-%m %H:%M:%S')}  tela_presa={estado[0]} "
                        f"bloqueada={estado[1]}\n")
                anterior = estado
        except Exception as e:
            f.write(f"{time.strftime('%d-%m %H:%M:%S')}  !! {e}\n")
        time.sleep(30)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "tela.log")
