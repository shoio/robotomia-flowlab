#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PROVA do leitor de numero do painel de fisica.

   A regra que ele serve: **toda etapa que ESCREVE tem de LER DE VOLTA**. As
   duas recapturas inteiras da Aula 2 tiveram a mesma forma — uma escrita
   silenciosa que so apareceu no fim, ou depois de publicada.

   Este leitor e o que permite `arrasta_slider` e o clique do `density`
   conferirem o que escreveram. Ele tem uma armadilha propria, achada aqui: a
   primeira versao pegava "o primeiro numero a direita, na mesma fileira" e
   leu `density = 1.0` — um "1" solto na beira da janela, a 1365 px do rotulo.
   Agora pega o MAIS PERTO, e so dentro de uma largura de linha.

       python3 fonte/prova_ler_de_volta.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import comum

FOTO = "provas/fotos/fisica_com_ceu_azul.png"
# o que esta escrito nesta foto, conferido com o olho
ESPERADO = {"density": 34.4, "bounce": 0.0, "friction": 100.0}


def main():
    erros = []
    for rotulo, valor in ESPERADO.items():
        lido = comum.le_numero_do_painel(rotulo, arquivo=FOTO)
        print(f"  {rotulo:10} lido={lido}  esperado={valor}")
        if lido != valor:
            erros.append(f"{rotulo}: li {lido}, a foto mostra {valor}")

    # ── SABOTAGEM: a versao original pegava o PRIMEIRO da fileira, nao o mais
    # perto — e assim leu `density = 1.0`, um "1" solto na beira da janela.
    import rs
    def primeiro_da_fileira(rotulo, arquivo, folga=22):
        p = comum._acha_no_painel(rotulo.lower(), arquivo)
        for t, x, y, w, h in rs.ocr_forte(arquivo, psm="6"):
            if abs((y + h // 2) - p[1]) > folga or x <= p[0]:
                continue
            try:
                return float(t.strip().replace(",", "."))
            except ValueError:
                continue
        return None

    solto = primeiro_da_fileira("density", FOTO)
    print(f"\nSABOTAGEM (o PRIMEIRO da fileira), density: {solto}"
          f"  (esperado != 34.4 — e o defeito)")
    if solto == 34.4:
        erros.append("a sabotagem nao reproduziu o defeito: esta prova nao "
                     "esta medindo o que diz medir")

    # ── CONTROLE: rotulo que nao existe devolve None, nao um numero qualquer ──
    nada = comum.le_numero_do_painel("velocidade da luz", arquivo=FOTO)
    print(f"rotulo inexistente: {nada}  (esperado None)")
    if nada is not None:
        erros.append("rotulo inexistente devolveu um numero")

    if erros:
        for e in erros:
            print("  ERRO:", e)
        raise SystemExit(1)
    print("\nprova ok")


if __name__ == "__main__":
    main()
