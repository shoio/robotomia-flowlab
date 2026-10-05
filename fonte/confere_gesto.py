#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Diz, EM PALAVRAS, para o que a seta de cada clipe aponta.

   O `confere_alvos.py` garante que a seta cai onde a tela mudou. Isso impede
   seta no vazio, mas nao impede seta no lugar ERRADO: mudou alguma coisa ali,
   so que nao era aquilo que o passo mandava clicar.

   Este aqui le o rotulo mais proximo do alvo e poe lado a lado com o titulo e
   o corpo do passo, para a leitura humana decidir. E a parte da engenharia
   reversa que nenhum guarda faz sozinho.

       python3 fonte/confere_gesto.py aula3
"""
import json, os, re, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rs

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def rotulo_perto(imagem, x, y, raio=150):
    """O que esta escrito em volta de (x, y), do mais perto para o mais longe."""
    im = Image.open(imagem).convert("L")
    L, A = im.size
    cx0, cy0 = max(0, x - raio), max(0, y - 60)
    cx1, cy1 = min(L, x + raio), min(A, y + 60)
    rec = im.crop((cx0, cy0, cx1, cy1))
    rec = rec.resize((rec.width * 2, rec.height * 2), Image.LANCZOS)
    rec.save("/tmp/_cg.png")
    itens = rs.ocr("/tmp/_cg.png", psm="6", escala=1)
    palavras = []
    for t, px, py, w, h in itens:
        t = t.strip()
        if len(t) < 2 or not re.search(r"[A-Za-zÀ-ÿ]", t):
            continue
        ax, ay = cx0 + px // 2 + w // 4, cy0 + py // 2 + h // 4
        palavras.append((abs(ax - x) + abs(ay - y), t))
    palavras.sort()
    return [t for _, t in palavras[:6]]


def confere(aula):
    mod = __import__(f"conteudo_a{aula[-1]}")
    passos = {p.get("clipe"): p for p in mod.AULA["passos"] if p.get("clipe")}
    alvos = json.load(open(f"{aula}/alvos.json"))
    print(f"=== {aula}: para o que cada seta aponta ===")
    for chave, dados in sorted(alvos.items()):
        gif = f"{chave}.gif"
        passo = passos.get(gif)
        antes = os.path.join(aula, dados["antes"])
        if not os.path.exists(antes):
            print(f"  {chave:<22} (sem quadro)"); continue
        perto = rotulo_perto(antes, *dados["alvo"])
        onde = ", ".join(perto) if perto else "— nada legivel —"
        if passo:
            print(f"  passo {passo['n']:>2}  {passo['titulo'][:40]:<40} "
                  f"seta em: {onde}")
        else:
            print(f"  {chave:<22} (clipe nao usado na aula)   seta em: {onde}")


if __name__ == "__main__":
    for a in (sys.argv[1:] or ["aula1", "aula2", "aula3"]):
        confere(a)
        print()
