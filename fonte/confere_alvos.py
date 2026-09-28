#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Confere, para cada gesto gravado, se o alvo do cursor cai mesmo em cima do
   botao que o texto manda clicar. Le a captura ANTES na posicao do alvo."""
import json, os, sys, rs
from PIL import Image

# os caminhos de conteudo sao relativos a fonte/: rode de onde quiser
import os as _os; _os.chdir(_os.path.dirname(_os.path.abspath(__file__)))

def rotulo_em(imagem, x, y, raio=90):
    """O que esta escrito perto de (x,y) na captura."""
    im = Image.open(imagem).convert("L")
    L, A = im.size
    cx0, cy0 = max(0, x - raio), max(0, y - 10)
    cx1, cy1 = min(L, x + raio), min(A, y + 95)
    rec = im.crop((cx0, cy0, cx1, cy1))
    rec = rec.resize((rec.width * 3, rec.height * 3), Image.LANCZOS)
    rec.save("/tmp/_rot.png")
    achados = [t.strip() for t, *_ in rs.ocr("/tmp/_rot.png", psm="6", escala=1) if len(t.strip()) > 2]
    return achados


ESPERADO = {
    "criar": "parte", "aba_modelo": None, "ancorar": "ancora",
    "material": "material", "cor": "cor", "tamanho": None,
    "renomear": None, "inserir_script": None, "voltar": None,
    "jogar": None, "parar": None, "publicar": None,
}


def confere(pasta):
    caminho = f"{pasta}/alvos.json"
    if not os.path.exists(caminho):
        return []
    A = json.load(open(caminho))
    problemas = []
    for chave, dados in A.items():
        esperado = ESPERADO.get(chave)
        if not esperado:
            continue
        alvo = dados.get("alvo") or dados.get("alvo_seta")
        antes = dados.get("antes")
        if not alvo or not antes:
            continue
        img = os.path.join(pasta, antes)
        if not os.path.exists(img):
            continue
        perto = rotulo_em(img, alvo[0], alvo[1])
        juntos = " ".join(perto).lower().replace("â", "a").replace("ã", "a").replace("ç", "c")
        ok = esperado in juntos
        print(f"  {pasta}/{chave:<16} alvo={alvo} -> {perto}  {'OK' if ok else '<<< ERRADO'}")
        if not ok:
            problemas.append((pasta, chave, alvo, perto))
    return problemas


if __name__ == "__main__":
    todos = []
    for n in range(2, 10):
        todos += confere(f"aula{n}")
    print(f"\nproblemas: {len(todos)}")
    for p in todos:
        print("  ", p)
