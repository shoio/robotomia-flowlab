#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Imprime cada aula do site em PDF, com o CSS de impressao da propria pagina.
   Os clipes viram a FOTO (o @media print troca), entao o PDF nao perde passo."""
import os, subprocess, glob
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def paginas(caminho):
    d = open(caminho, "rb").read()
    return d.count(b"/Type /Page") - d.count(b"/Type /Pages"), len(d)

def aulas_no_site():
    """As aulas que EXISTEM no site, tiradas do disco. Antes isto era
       range(1, 10) cravado: a Aula 10 entrou no site e o PDF dela nao saiu,
       sem ninguem reclamar — o jeito mais mudo de faltar uma peca."""
    ns = []
    for pasta in glob.glob(os.path.join(RAIZ, "aula*")):
        resto = os.path.basename(pasta)[4:]
        if resto.isdigit() and os.path.exists(os.path.join(pasta, "index.html")):
            ns.append(int(resto))
    return sorted(ns)


def main():
    achadas = aulas_no_site()
    if not achadas:
        raise RuntimeError("nenhuma aula no site: nao ha o que imprimir")
    for n in achadas:
        pasta = os.path.join(RAIZ, f"aula{n}")
        html = os.path.join(pasta, "index.html")
        pdf = os.path.join(pasta, f"aula{n}.pdf")
        if not os.path.exists(html):
            print("  sem", html); continue
        subprocess.run([CHROME, "--headless=new", "--disable-gpu",
                        "--no-pdf-header-footer", f"--print-to-pdf={pdf}",
                        f"file://{html}"], capture_output=True)
        if not os.path.exists(pdf):
            raise RuntimeError(f"nao saiu o PDF da aula {n}")
        p, b = paginas(pdf)
        print(f"  aula {n}: {p} paginas, {b/1e6:.1f} MB")

if __name__ == "__main__":
    main()
