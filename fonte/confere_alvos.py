#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O GUARDA DOS CLIPES: a seta tem de apontar para onde a tela MUDOU.

   Por que este arquivo foi reescrito do zero: a versao herdada do curso de
   Roblox conferia por uma TABELA DE NOMES de gesto ('ancorar', 'material',
   'cor'). Nenhum desses nomes existe no Flowlab, entao ela percorria os
   clipes, nao reconhecia nenhum, e passava com zero problemas. Guarda verde
   que nao olha nada. E ninguem a chamava no build.

   A regra nova nao precisa saber o nome de gesto nenhum:

       o ponto da seta tem de cair onde a imagem ANTES e a imagem DEPOIS
       sao diferentes.

   E o invariante do que um clipe é. Foi assim que cinco clipes com a seta
   fincada no CANTO DA TELA (0,0) passaram despercebidos — quatro na Aula 3 e
   um na Aula 2, ja publicado, com o texto mandando marcar quatro caixinhas
   enquanto a animacao clicava no vazio.

       python3 fonte/confere_alvos.py
"""
import json, os, sys
import numpy as np
from PIL import Image

os.chdir(os.path.dirname(os.path.abspath(__file__)))

RAIO = 170          # o quanto em volta da seta eu aceito como "foi ali"
MINIMO = 400        # pixels mudados dentro desse raio
CANTO = 60          # perto demais de um canto e sinal de alvo nao preenchido


def mudou_perto(pasta, dados, raio=RAIO):
    """(quantos pixels mudaram perto da seta, quantos mudaram na tela toda)"""
    a = os.path.join(pasta, dados["antes"])
    b = os.path.join(pasta, dados["depois"])
    if not (os.path.exists(a) and os.path.exists(b)):
        return None, None
    A = np.asarray(Image.open(a).convert("L"), dtype=int)
    B = np.asarray(Image.open(b).convert("L"), dtype=int)
    if A.shape != B.shape:
        return None, None
    dif = np.abs(A - B) > 30
    x, y = dados["alvo"]
    y0, y1 = max(0, y - raio), min(A.shape[0], y + raio)
    x0, x1 = max(0, x - raio), min(A.shape[1], x + raio)
    return int(dif[y0:y1, x0:x1].sum()), int(dif.sum())


def confere(pastas=None):
    pastas = pastas or sorted(p for p in os.listdir(".")
                              if p.startswith("aula") and os.path.isdir(p))
    problemas = []
    for pasta in pastas:
        caminho = f"{pasta}/alvos.json"
        if not os.path.exists(caminho):
            continue
        for chave, dados in sorted(json.load(open(caminho)).items()):
            alvo = dados.get("alvo")
            if not alvo or len(alvo) != 2:
                problemas.append(f"{pasta}/{chave}: sem alvo")
                continue
            x, y = alvo
            # 1. o alvo nunca pode ser o canto: e o cheiro de alvo que ninguem
            #    preencheu (o (0,0) que eu passava quando a acao nao devolvia
            #    ponto nenhum)
            if x < CANTO and y < CANTO:
                problemas.append(f"{pasta}/{chave}: a seta aponta para o CANTO "
                                 f"da tela {alvo} — alvo nao preenchido")
                continue
            perto, total = mudou_perto(pasta, dados)
            if perto is None:
                problemas.append(f"{pasta}/{chave}: faltam os quadros do clipe")
                continue
            # 2. e o invariante: ali tem de ter mudado alguma coisa
            if total < 200:
                problemas.append(f"{pasta}/{chave}: a tela nao mudou entre os "
                                 f"dois quadros ({total} px) — clipe sem gesto")
            elif perto < MINIMO and not dados.get("clicado"):
                # Quando o gesto REGISTROU o clique, o alvo e o lugar onde a
                # maquina clicou — invariante melhor do que "ali mudou". Ha
                # gesto em que o que muda fica do outro lado da tela: ao
                # escolher um boneco na grade de sprites, muda o DESENHO, e a
                # celula clicada continua igual.
                problemas.append(f"{pasta}/{chave}: a seta aponta para {alvo}, "
                                 f"onde quase nada mudou ({perto} px num raio de "
                                 f"{RAIO}; a tela toda mudou {total}) e o gesto "
                                 "nao registrou clique ali")
    return problemas


if __name__ == "__main__":
    e = confere(sys.argv[1:] or None)
    for m in e:
        print("  !!", m)
    print(f"  {len(e)} problema(s)")
    raise SystemExit(1 if e else 0)
