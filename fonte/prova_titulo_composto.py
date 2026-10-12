#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PROVA: bloco de titulo com DUAS palavras tem de ser achado na mesa.

   O defeito que isto tranca: `acha_bloco` chama `procura_forte(exato=True)`,
   e o ramo exato comparava item por item do OCR — e o tesseract entrega UMA
   PALAVRA por item. Nenhum item e igual a 'global variable', entao o bloco
   `Global Variable` — que estava na mesa, aceso, legivel na foto — nunca era
   achado. A falha chegava com a frase «soltei e nao consegui LER o titulo na
   mesa», que e a MESMA de quando o bloco nao cai: dois diagnosticos opostos
   com uma frase so, e eu fui procurar o defeito no arrasto.

   Vale para `Global Variable`, `Object Variable`, `Toggle Switch`,
   `Logic Gate`, `Text Length` — metade da palheta.

   A foto: a mesa do prototipo 3155726, com `Global Variable` e `Switch`.

   O CONTROLE importa tanto quanto a sabotagem — casamento frouxo que achasse
   qualquer coisa passaria na primeira metade. Por isso o nome de mentira.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rs

# A MESMA JANELA que `blocos.acha_bloco` usa (`blocos.TELA`): a palheta da
# esquerda tem os mesmos nomes dos blocos, e procurar na tela inteira acha o
# ITEM DA PALHETA em vez do bloco da mesa. Escrito aqui como numero para a
# prova nao depender de importar o `blocos` (que puxa a bancada inteira).
MESA = (0.12, 0.0, 1.0, 0.95)

FOTO = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "provas", "fotos", "mesa_titulo_composto.png")

falhas = []

# 1. o titulo composto e achado, e no lugar certo (metade de cima da mesa)
achado = rs.procura_forte("Global Variable", arquivo=FOTO, regiao=MESA, exato=True)
if not achado:
    falhas.append("nao achei 'Global Variable' na mesa da foto")
else:
    t, x, y, w, h = achado
    if not (700 < x < 1400 and 200 < y < 700):
        falhas.append(f"achei 'Global Variable' em ({x},{y}), fora da mesa")

# 2. CONTROLE: o titulo de uma palavra continua sendo achado
if not rs.procura_forte("Switch", arquivo=FOTO, regiao=MESA, exato=True):
    falhas.append("perdi o bloco de uma palavra ('Switch')")

# 3. SABOTAGEM: nome parecido, que nao esta na mesa, nao pode ser achado
# (nao use 'Object Variable': ele esta na PALHETA da foto, e a palheta e
# tela de verdade. Sabotagem tem de ser nome que nao esta em lugar nenhum.)
for mentira in ("Globbal Variable", "Global Variables", "Mailbox Variable"):
    if rs.procura_forte(mentira, arquivo=FOTO, regiao=MESA, exato=True):
        falhas.append(f"achei '{mentira}', que nao esta na mesa")

# 3b. O TITULO DIVIDINDO A LINHA DO OCR COM O VIZINHO.
#
# Na foto `mesa_titulos_na_mesma_linha.png` o `Timer` e o `Global Variable`
# estao na mesma altura da mesa, e o tesseract devolve a linha inteira como
# 'timer global variable'. Com a regra de igualdade, o bloco — aceso, na
# tela — nao era achado, e `solta` desfazia o arrasto tres vezes.
FOTO2 = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "provas", "fotos", "mesa_titulos_na_mesma_linha.png")
achado2 = rs.procura_forte("Global Variable", arquivo=FOTO2, regiao=MESA, exato=True)
if not achado2:
    falhas.append("nao achei 'Global Variable' quando ele divide a linha "
                  "do OCR com o bloco vizinho")
else:
    t, x, y, w, h = achado2
    if x < 900:
        falhas.append(f"achei 'Global Variable' em x={x} — esse e o da "
                      "PALHETA, nao o da mesa")
# e o limite de palavra continua valendo nessa foto
for mentira2 in ("Global Variables", "lobal Variable", "Timer Globa"):
    if rs.procura_forte(mentira2, arquivo=FOTO2, regiao=MESA, exato=True):
        falhas.append(f"achei '{mentira2}' na foto da linha compartilhada")

# 4. SABOTAGEM da regra: sem o ramo da linha junta, a prova 1 tem de FALHAR
_linha = rs._por_linha
try:
    rs._por_linha = lambda itens: []          # mata so o ramo da linha junta
    if rs.procura_forte("Global Variable", arquivo=FOTO, regiao=MESA, exato=True):
        falhas.append("achei o titulo composto SEM o ramo da linha — "
                      "a prova nao esta medindo o conserto")
finally:
    rs._por_linha = _linha

print("\n".join(f"!! {f}" for f in falhas) if falhas else "prova ok")
sys.exit(1 if falhas else 0)
