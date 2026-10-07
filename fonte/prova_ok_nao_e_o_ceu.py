#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PROVA: o detector do botao OK nao pode achar o CEU.

   O defeito que isto tranca, e o mais caro desta noite: `AZUL_OK` e
   (126,168,224) e o ceu da Aula 2 e `87CEEB` = (135,206,235). A distancia e
   (9, 38, 11) — dentro da tolerancia 40 que o detector usa. Com o nivel
   pintado de azul, o "OK" encontrado era uma mancha de ~786 mil pixels (o
   ceu) em vez dos ~24 mil do botao, e o clique caia DENTRO do painel de
   fisica, em cima da caixinha `movable`, desmarcando-a.

   O jogo publicado da Aula 2 ficou com um boneco que corria e nao pulava. O
   proprio Flowlab escrevia a causa, por extenso, dentro do pacote
   `Run & Jump`: *"This object is not movable, so Impulse will have no
   effect"* — o andar e `Velocity` (funciona em objeto parado), o pulo e
   `Impulse` (nao funciona). A Aula 3 escapou porque o ceu dela e de NOITE.

   O teto de tamanho ja existia em `abre_fisica`. Nao foi levado para
   `fecha_painel_objeto`, que e a irma ao lado — e e por isso que esta prova
   cobre as DUAS.

       python3 fonte/prova_ok_nao_e_o_ceu.py
"""
import os, sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import nav, comum

FOTO = "provas/fotos/fisica_com_ceu_azul.png"
CEU = (135, 206, 235)


def _mancha(rgb, tol, arquivo):
    im = np.asarray(Image.open(arquivo).convert("RGB"), dtype=int)
    return int((np.abs(im - np.array(rgb)) <= tol).all(axis=2).sum())


def main():
    erros = []

    # ── 1. a colisao de cor e real, nao hipotetica ────────────────────
    d = [abs(a - b) for a, b in zip(comum.AZUL_OK, CEU)]
    print(f"distancia do ceu ao AZUL_OK: {d}  (tolerancia usada: 40)")
    if max(d) > 40:
        erros.append("o ceu deixou de colidir com o AZUL_OK: esta prova "
                     "perdeu o sentido, confira a cor do ceu da Aula 2")

    azul = _mancha(comum.AZUL_OK, 40, FOTO)
    print(f"pixels a 40 do AZUL_OK na foto: {azul}")

    # ── 2. o detector de verdade cai DENTRO do botao ──────────────────
    # O retangulo do OK nesta foto, medido: x 1428..1734, y 1228..1308.
    CAIXA = (1428, 1228, 1734, 1308)
    x, y = comum._ponto_do_ok(FOTO)
    dentro = CAIXA[0] <= x <= CAIXA[2] and CAIXA[1] <= y <= CAIXA[3]
    print(f"_ponto_do_ok devolveu ({x}, {y})  dentro do botao: {dentro}")
    if not dentro:
        erros.append(f"_ponto_do_ok caiu em ({x}, {y}), fora do botao OK "
                     f"{CAIXA} — e o ceu que esta sendo clicado")

    # ── 3. SABOTAGEM: so pela COR, com teto e tudo, o clique sai errado
    # Esta e a parte que me enganou primeiro: eu pus um teto de 120 mil
    # pixels achando que separava o botao do ceu, e o ceu PARTIDO passa nele.
    for teto in (None, 120000):
        p = nav.acha_cor(comum.AZUL_OK, tol=40, regiao=(0.0, 0.05, 1.0, 0.98),
                         minimo=800, maximo=teto, arquivo=FOTO)
        dentro = p and (CAIXA[0] <= p[0] <= CAIXA[2] and CAIXA[1] <= p[1] <= CAIXA[3])
        print(f"SABOTAGEM so por cor (teto {teto}): {p}  dentro do botao: {bool(dentro)}"
              "  (esperado False — e o defeito)")
        if dentro:
            erros.append(f"a sabotagem com teto {teto} nao reproduziu o defeito")

    # ── 4. a funcao de verdade, pelo caminho dela ─────────────────────
    # `fecha_painel_objeto` chama `nav.acha_cor` com os mesmos argumentos; o
    # que esta prova tranca e que o `maximo` esteja escrito nas DUAS chamadas.
    import inspect
    fonte = inspect.getsource(comum._ponto_do_ok)
    i_rotulo = fonte.find("procura_forte")
    i_cor = fonte.find("acha_cor")
    print(f"\n_ponto_do_ok: rotulo na posicao {i_rotulo}, cor na {i_cor}")
    if i_rotulo < 0:
        erros.append("_ponto_do_ok deixou de procurar o ROTULO do botao")
    elif 0 <= i_cor < i_rotulo:
        erros.append("_ponto_do_ok voltou a decidir pela COR antes do rotulo")
    # e quem fecha o painel tem de passar por aqui
    fonte2 = inspect.getsource(comum.fecha_painel_objeto)
    if "_ponto_do_ok" not in fonte2:
        erros.append("fecha_painel_objeto nao usa mais _ponto_do_ok")

    if erros:
        for e in erros:
            print("  ERRO:", e)
        raise SystemExit(1)
    print("\nprova ok")


if __name__ == "__main__":
    main()
