#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prova que a mascara de cor REJEITA cinza sem perder os sprites de verdade.

   O defeito: `mascara_cor` so media distancia canal a canal. A pele do heroi
   e (234,179,146), e um cinza (190,190,190) cai dentro de 46 nos tres canais.
   Quando o Flowlab escurece o jogo — ele faz isso quando a pagina perde o foco
   — a pagina inteira vira esse cinza, e a sonda achou 667.424 pixels de
   "boneco" contra 432 com o jogo aceso. Com isso ela declarou vitoria com a
   estrela visivel na foto que guardou como prova.

   Duas coisas sao provadas aqui, e a segunda importa tanto quanto a primeira:
   1. SABOTAGEM: cinza, em varias claridades, nao casa com cor nenhuma viva.
   2. NEUTRALIDADE: nas fotos JA aprovadas das tres aulas, a contagem de cada
      sprite nao muda — senao eu teria consertado a sonda quebrando as aulas
      que ja estao no ar.

       python3 fonte/prova_mascara_cinza.py
"""
import json, os, sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import comum


def velha(im, cor, tol=46):
    """A mascara como era antes — a referencia da neutralidade."""
    return ((abs(im[:, :, 0] - cor[0]) < tol) &
            (abs(im[:, :, 1] - cor[1]) < tol) &
            (abs(im[:, :, 2] - cor[2]) < tol))


def main():
    falhas = []

    # ── 1. sabotagem: cinza nao e sprite ──────────────────────────────────
    vivas = [(234, 179, 146), (255, 181, 44), (255, 0, 66), (101, 201, 77),
             (0, 98, 176)]
    for claro in (60, 120, 160, 190, 210, 240):
        cinza = np.full((40, 40, 3), claro, dtype=int)
        for cor in vivas:
            n = int(comum.mascara_cor(cinza, cor).sum())
            if n:
                falhas.append(f"cinza {claro} casou {n} px com {cor}")
    print("   cinza de 60 a 240: nao casa com nenhuma das cinco cores vivas",
          flush=True)

    # ── 2. neutralidade NAS FOTOS QUE AS SONDAS LEEM ─────────────────────
    #
    # A primeira versao desta parte comparava TODAS as fotos da aula e
    # reprovava. Ela estava medindo a coisa errada: nas fotos do EDITOR a
    # mascara velha contava 525.176 pixels de "Chao" que eram o cinza do
    # fundo, e perder esse cinza e o conserto, nao um estrago. O que as aulas
    # dependem e da leitura na PAGINA DO JOGO — e o que importa la e que o
    # sprite continue achavel e no mesmo lugar.
    JOGO = ("p19_jogo", "p20_pegou", "p16_jogo", "p17_pulo", "p18_recomecou",
            "p21_jogo", "p22_lava_subindo", "p23_recomecou", "p24_pegou_a_estrela")
    MINIMO = 60          # o menor limiar que qualquer sonda usa
    vistas = 0
    for aula in ("aula1", "aula2", "aula3"):
        caminho = f"{aula}/cores.json"
        if not os.path.exists(caminho):
            continue
        cores = json.load(open(caminho))
        for foto in sorted(os.listdir(aula)):
            if not foto.endswith((".png", ".jpg")):
                continue
            if os.path.splitext(foto)[0] not in JOGO:
                continue
            im = np.asarray(Image.open(os.path.join(aula, foto)).convert("RGB"),
                            dtype=int)
            for quem, lista in cores.items():
                cor = tuple(lista[0])
                ma, mb = velha(im, cor), comum.mascara_cor(im, cor)
                a, b = int(ma.sum()), int(mb.sum())
                if a < MINIMO:
                    continue
                vistas += 1
                if b < MINIMO:
                    falhas.append(f"{aula}/{foto} {quem}: sumiu da foto do JOGO "
                                  f"({a} -> {b} px)")
                    continue
                # o centro e o que a sonda usa; ele nao pode andar
                ca = (int(np.nonzero(ma)[1].mean()), int(np.nonzero(ma)[0].mean()))
                cb = (int(np.nonzero(mb)[1].mean()), int(np.nonzero(mb)[0].mean()))
                anda = max(abs(ca[0] - cb[0]), abs(ca[1] - cb[1]))
                if anda > 20:
                    falhas.append(f"{aula}/{foto} {quem}: o centro andou {anda} px "
                                  f"({ca} -> {cb}), com {a} -> {b} px")
    print(f"   {vistas} medidas de sprite nas fotos da PAGINA DO JOGO", flush=True)

    for f in falhas[:20]:
        print("  !!", f)
    print(f"  {len(falhas)} problema(s)")
    return 1 if falhas else 0


if __name__ == "__main__":
    raise SystemExit(main())
