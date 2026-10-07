#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regrava os clipes que o `confere_alvos.py` reprovou.

   Nao refaz a aula inteira: abre o jogo que ja existe e repete SO o gesto,
   com um quadro de verdade antes e outro depois.

   O truque para ter um "antes" honesto numa caixinha que ja esta no estado
   certo: deixo ela no estado OPOSTO (sem gravar) e gravo a volta. O clipe
   mostra o gesto que a aula pede, e o jogo termina do jeito que estava.

       BANCADA=1 python3 fonte/refaz_clipes.py aula3
"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rs, nav, editor, blocos, comum
from comum import celula, clique, marca_caixa, A

# O endereco de cada jogo vive em aulaN/jogo.txt. Antes ele so era impresso
# durante a captura e se perdia: fui regravar um clipe da Aula 2 e abri o
# RASCUNHO que eu usara para medir, porque o unico numero escrito em algum
# lugar era o do comentario do codigo. Na conta todos se chamam `New Game` e
# nenhum tem miniatura — nao ha como descobrir pelo nome.
def _jogo(aula):
    with open(f"{aula}/jogo.txt") as f:
        return f.read().strip()


JOGOS = {a: _jogo(a) for a in ("aula2", "aula3")}


def do_zero(aula):
    """Recarrega o jogo antes de cada bloco.

       Sem isto a bancada herda o estado da tentativa anterior: numa delas o
       menu da conta ficou aberto e eu procurei o `Physics >` numa tela que
       dizia 'droneiscool / Log out / My games'. O finder estava certo; a tela
       e que era outra."""
    nav.vai(JOGOS[aula], espera=7)
    editor.espera_tela("library", "game levels", limite=30)
    time.sleep(1.5)


def abre(col, lin):
    editor.volta_ao_nivel(); time.sleep(1.2)
    x, y = celula(col, lin)
    editor.objeto_ou_abre(x, y)


fisica = comum.abre_fisica


def regrava(chave, base, rotulo, quero):
    """Poe a caixinha no estado OPOSTO e grava a volta ao estado certo."""
    marca_caixa(rotulo, not quero)
    time.sleep(0.8)
    A.gesto(chave, base, (0, 0), lambda: marca_caixa(rotulo, quero), espera=1.4)
    print(f"   clipe {chave} refeito", flush=True)


def restaura_peso(densidade):
    """DESMARCAR `movable` ZERA o peso e o atrito de volta ao padrao (50/50).

       Medido na Aula 2: ela estava em 34.4/100 e voltou para 50/50 so de eu
       piscar a caixinha para gravar o clipe. O peso e o que decide se o
       boneco pula — entao toda regravacao de `movable` do JOGADOR tem de
       restaurar, com o mesmo gesto que a aula ensina.

       Isto vivia so dentro de `aula2()`. A `aula3()` pisca a mesma caixinha
       do mesmo jeito e NAO restaurava: o clipe sairia bonito e o jogo ficaria
       com um boneco de peso errado, sem nada acusando."""
    pd = comum._acha_no_painel("density", nav.captura("/tmp/_rc_d0.png")[0])
    if not pd:
        raise RuntimeError("nao achei o Density para restaurar o peso")
    clique(int(pd[0] + 155 + 2.75 * densidade), pd[1]); time.sleep(1.2)
    comum.arrasta_slider("friction")
    a, _ = nav.captura("/tmp/_rc_d.png")
    txt = " ".join(t for t, *_ in rs.ocr_forte(a, regiao=(0.0, 0.05, 1.0, 0.9), psm="6"))
    import re as _re
    nums = [float(x) for x in _re.findall(r"\d+\.\d", txt)]
    peso = next((n for n in nums if 20 <= n <= 45), None)
    if peso is None or 100.0 not in nums:
        raise RuntimeError(f"o peso NAO voltou ao que a aula precisa (li {nums[:5]})")
    print(f"   peso {peso}, atrito 100 — dentro da faixa", flush=True)
    return peso


def lava3():
    """SO as quatro caixinhas da lava da Aula 3.

       Separado de `aula3()` de proposito: aquela funcao pisca tambem o
       `movable` do JOGADOR, e piscar essa caixinha zera o peso dele."""
    comum.pasta("aula3")
    import cap3
    do_zero("aula3")
    abre(cap3.COLS_LAVA[0], cap3.LINHA_LAVA)
    fisica()
    regrava("lava_movable", "g12", "movable", True)
    regrava("desligar_gravidade", "g07", "affected by gravity", False)
    regrava("lava_atravessa", "g10", "is solid", False)
    regrava("lava_sente_o_toque", "g11", "enable collisions", True)
    editor.volta_ao_nivel()


def aula3():
    comum.pasta("aula3")
    import cap3
    # 1) o jogador: movable
    do_zero("aula3")
    abre(cap3.COL_JOGADOR, cap3.LINHA_CHAO - 1)
    fisica()
    regrava("marcar_movable", "g04", "movable", True)
    restaura_peso(cap3.DENSIDADE)
    # 2) a lava: as tres caixinhas, na ordem em que a aula manda
    do_zero("aula3")
    abre(cap3.COLS_LAVA[0], cap3.LINHA_LAVA)
    fisica()
    # `lava_movable` PRIMEIRO: desmarcar `movable` esconde as outras caixinhas
    # e devolve o peso ao padrao, entao as tres regravacoes seguintes
    # restauram o estado certo em cima dela.
    regrava("lava_movable", "g12", "movable", True)
    regrava("desligar_gravidade", "g07", "affected by gravity", False)
    regrava("lava_atravessa", "g10", "is solid", False)
    regrava("lava_sente_o_toque", "g11", "enable collisions", True)
    # 3) o numero que faz subir
    do_zero("aula3")
    abre(cap3.COLS_LAVA[0], cap3.LINHA_LAVA)
    editor.abre_comportamentos(); time.sleep(1.5)
    nu = blocos.acha_bloco("Number")
    blocos.escreve_valor(nu, 0)        # volta ao zero
    # com o painel ABERTO nos dois quadros: o clipe mostra o campo com 0.5, o
    # cursor indo ate o `−` e o numero virando -0.5
    ponto = blocos.prepara_menos(nu, cap3.SUBIDA)
    A.gesto("botao_menos", "g08", ponto,
            lambda: blocos.clica_menos(ponto, 1), espera=1.4)
    blocos.fecha_ajustes(); time.sleep(1.0)
    print("   clipe botao_menos refeito; valor:", blocos.le_valor(nu), flush=True)
    editor.fecha_comportamentos(); time.sleep(2)
    editor.volta_ao_nivel()


def aula2():
    comum.pasta("aula2")
    import cap2
    do_zero("aula2")
    abre(cap2.COL_JOGADOR, cap2.LINHA_CHAO - 1)
    fisica()
    regrava("marcar_movable", "g04", "movable", True)
    # DESMARCAR `movable` ZERA o peso e o atrito de volta ao padrao (50/50).
    # Medido: a Aula 2 estava em 34.4/100 e voltou para 50/50 so de eu piscar a
    # caixinha para gravar o clipe. Entao restauro, e com o mesmo gesto que a
    # aula ensina.
    restaura_peso(cap2.DENSIDADE)
    editor.volta_ao_nivel()


def ceu(aula, base, cor):
    """Regrava os DOIS clipes do passo do ceu, no jogo que ja existe.

       O "antes" honesto aqui nao precisa de truque: abrir o painel muda a
       tela, e escrever a cor muda o campo E o nivel. O que havia de errado
       era um clipe SO para os dois gestos — a seta apontava para o campo da
       cor, que no quadro de antes nem esta na tela.

       Escrever a MESMA cor que ja esta la nao muda o jogo; muda so a foto."""
    comum.pasta(aula)
    do_zero(aula)
    editor.volta_ao_nivel(); time.sleep(1.0)
    A.gesto("abrir_niveis", base + "a", (0, 0),
            lambda: editor.abre_niveis(), espera=1.8)
    A.gesto("pintar_o_ceu", base, (0, 0),
            lambda: editor.cor_do_ceu(cor, abrir=False), espera=2.0)
    editor.volta_ao_nivel(); time.sleep(1.0)
    print(f"   clipes do ceu refeitos em {aula} (#{cor})", flush=True)


def ceu2():
    import cap2
    ceu("aula2", "g08", cap2.CEU)


def ceu3():
    import cap3
    ceu("aula3", "g14", cap3.CEU)


if __name__ == "__main__":
    alvo = sys.argv[1] if len(sys.argv) > 1 else "aula3"
    {"aula2": aula2, "aula3": aula3, "lava3": lava3,
     "ceu2": ceu2, "ceu3": ceu3}[alvo]()
    print("== fim ==")
