#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Roda a aula inteira e termina com UM VEREDITO. Nao se acompanha pelo caminho.

   Por que existe: numa noite de trabalho eu gastei uma fatia enorme do meu
   orcamento OLHANDO a captura rodar — dezenas de leituras de log e de foto
   enquanto um processo de vinte minutos avancava sozinho. Nenhuma delas mudou
   nada do que eu fiz depois.

   A regra que isto impoe: **a captura e assincrona e muda. Eu leio o veredito
   no fim, e a folha de contato, e mais nada.**

       python3 fonte/roda_aula.py 2           # a aula inteira, do zero
       python3 fonte/roda_aula.py 2 prova     # de uma etapa em diante
       python3 fonte/roda_aula.py 3 --so-fecha  # pula a captura, so fecha

   O que ele faz, em ordem, parando no primeiro erro:
     1. a captura (`capN.py`), com `BANCADA=1`;
     2. os clipes e os JPEG;
     3. os dois guardas de conteudo;
     4. a folha de contato;
   e imprime, no fim, as MEDIDAS que a captura tirou em jogo.
"""
import os, re, subprocess, sys, time

AQUI = os.path.dirname(os.path.abspath(__file__))
os.chdir(AQUI)

# as linhas da captura que sao MEDIDA, e nao recado de progresso
MEDIDAS = re.compile(
    r"(pulo:|lava subiu|recomecou|deslizou|PROVADO|estrela e ela SUMIU|"
    r"ceu em #|peso =|friction =|tipo =|right =|serie d[eo])", re.I)


def roda(titulo, cmd, amb=None, registro=None):
    ambiente = dict(os.environ); ambiente.update(amb or {})
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True, env=ambiente)
    saida = (r.stdout or "") + (r.stderr or "")
    if registro:
        open(registro, "w").write(saida)
    return r.returncode, saida, time.time() - t0


def veredito(linhas):
    print("\n" + "=" * 62)
    for l in linhas:
        print(l)
    print("=" * 62)


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    n = sys.argv[1]
    resto = sys.argv[2:]
    so_fecha = "--so-fecha" in resto
    etapa = next((a for a in resto if not a.startswith("--")), None)
    slug = f"aula{n}"
    registro = f"/tmp/roda_{slug}.log"
    passos, medidas = [], []

    if not so_fecha:
        cmd = [sys.executable, "-u", f"cap{n}.py"] + ([etapa] if etapa else [])
        cod, saida, seg = roda("captura", cmd, {"BANCADA": "1"}, registro)
        etapas = re.findall(r"^== (\w+) ==$", saida, re.M)
        medidas = [l.strip() for l in saida.splitlines() if MEDIDAS.search(l)]
        passos.append(f"captura   : {len(etapas)} etapas em {seg/60:.0f} min "
                      f"({', '.join(etapas[:12])}{'…' if len(etapas) > 12 else ''})")
        if cod != 0:
            erro = [l for l in saida.splitlines() if l.strip()][-1]
            veredito(passos + [f"⛔ A CAPTURA PAROU: {erro}",
                               f"   registro inteiro: {registro}"] +
                     ([""] + ["medidas ate parar:"] + medidas if medidas else []))
            return 1

    for titulo, cmd in (("clipes", [sys.executable, "gera_gifs.py", slug]),
                        ("jpeg  ", [sys.executable, "para_jpeg.py", slug])):
        cod, saida, seg = roda(titulo, cmd)
        if cod != 0:
            veredito(passos + [f"⛔ {titulo} falhou:", saida[-500:]])
            return 1
        passos.append(f"{titulo}    : ok")

    falhas = []
    for titulo, cmd in (("confere_aulas", [sys.executable, "confere_aulas.py"]),
                        ("confere_alvos", [sys.executable, "confere_alvos.py"])):
        cod, saida, _ = roda(titulo, cmd)
        marca = "ok" if cod == 0 else "REPROVOU"
        passos.append(f"{titulo}: {marca}")
        if cod != 0:
            falhas += [l for l in saida.splitlines() if l.strip().startswith("!!")]

    cod, saida, _ = roda("contato", [sys.executable, "folha_de_contato.py", slug])
    folha = saida.strip().split("->")[-1].strip() if cod == 0 else "(nao saiu)"
    passos.append(f"folha de contato: {folha}")

    linhas = passos + ([""] + ["MEDIDO EM JOGO:"] + [f"   {m}" for m in medidas]
                       if medidas else [])
    if falhas:
        linhas += [""] + ["⛔ OS GUARDAS ACUSARAM:"] + [f"   {f}" for f in falhas]
    linhas += ["", "👁  OLHE A FOLHA DE CONTATO — e o unico passo que nenhum "
               "guarda faz por mim."]
    veredito(linhas)
    return 1 if falhas else 0


if __name__ == "__main__":
    raise SystemExit(main())
