#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rascunho da Aula 3. Primeiro passo: INVENTARIO da palheta de blocos.

   Por que: ate agora eu abria a categoria que eu *achava* que tinha o bloco.
   'Timer' mora em Triggers, nao em Logic — e isso so apareceu depois de um
   erro. Com a lista medida de uma vez, as nove aulas que faltam escolhem o
   bloco pelo nome certo e pela categoria certa."""
import os, sys, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rs, nav, editor, blocos


def inventario(saida="palheta.json"):
    tudo = {}
    for cat in blocos.CATEGORIAS:
        try:
            blocos.abre_categoria(cat)
        except RuntimeError as e:
            tudo[cat] = ["!! " + str(e)]
            continue
        time.sleep(1.0)
        a, _ = nav.captura("/tmp/_inv.png")
        itens = rs.ocr_forte(a, regiao=blocos.PALHETA, psm="6")
        nomes, vistos = [], set()
        for t, x, y, w, h in sorted(itens, key=lambda i: i[2]):
            t = t.strip()
            if len(t) < 3 or t.lower() in vistos:
                continue
            vistos.add(t.lower())
            nomes.append(t)
        tudo[cat] = nomes
        print(f"  {cat}: {', '.join(nomes)}", flush=True)
    json.dump(tudo, open(saida, "w"), indent=1, ensure_ascii=False)
    return tudo


if __name__ == "__main__":
    print("== jogo de rascunho ==", flush=True)
    url = editor.jogo_novo()
    print("   rascunho:", url, flush=True)
    editor.objeto_novo()
    editor.espera_tela("behaviors", limite=20)
    editor.abre_comportamentos()
    print("== inventario da palheta ==", flush=True)
    inventario()
