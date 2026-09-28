#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Converte as capturas de UMA aula de PNG para JPEG e reescreve o alvos.json.

   Por que existe: a captura sai em PNG (~1 MB cada) e as aulas 2 a 9 estao
   em JPEG q92 na fonte. A conversao era feita na mao, fora do repositorio —
   e o que nao esta no repositorio nao tem guarda e nao sobrevive ao /tmp.

   Recorte estreito de proposito: mexe SO na pasta da aula que recebe no
   argumento. Nada de varrer a arvore.

       python3 fonte/para_jpeg.py aula10
"""
import json, os, sys
from PIL import Image

os.chdir(os.path.dirname(os.path.abspath(__file__)))

Q = 92


def converte(pasta):
    if not os.path.isdir(pasta) or not pasta.startswith("aula"):
        raise SystemExit(f"'{pasta}' nao e uma pasta de aula aqui dentro")
    pngs = sorted(f for f in os.listdir(pasta) if f.endswith(".png"))
    feitos, pulados = [], []
    for f in pngs:
        origem = os.path.join(pasta, f)
        destino = origem[:-4] + ".jpg"
        Image.open(origem).convert("RGB").save(destino, quality=Q, optimize=True)
        # so apago o PNG depois de o JPEG existir e abrir
        with Image.open(destino) as im:
            im.load()
        os.remove(origem)
        feitos.append(f)
    # as referencias do alvos.json apontam para os arquivos que o gif usa
    alvos = os.path.join(pasta, "alvos.json")
    trocas = 0
    if os.path.exists(alvos):
        txt = open(alvos).read()
        novo = txt.replace(".png", ".jpg")
        trocas = txt.count(".png")
        if trocas:
            open(alvos, "w").write(novo)
        # um arquivo citado que nao existe e um clipe que vai nascer torto
        A = json.load(open(alvos))
        faltam = sorted({v for c in A.values() for k, v in c.items()
                         if isinstance(v, str) and v.endswith(".jpg")
                         and not os.path.exists(os.path.join(pasta, v))}
                        | {v for c in A.values() for lista in
                           ([c["quadros"]] if isinstance(c.get("quadros"), list) else [])
                           for v in lista if not os.path.exists(os.path.join(pasta, v))})
        if faltam:
            raise SystemExit(f"o alvos.json cita arquivos que nao existem: {faltam}")
    return feitos, trocas


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    feitos, trocas = converte(sys.argv[1])
    print(f"  {len(feitos)} PNG viraram JPEG q{Q}; {trocas} referencias do alvos.json trocadas")
