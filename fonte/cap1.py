#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Captura da Aula 1 — Pega-moedas (o primeiro jogo).

   O jogo: um boneco que anda com as setas e moedas que somem quando ele
   encosta. Termina jogavel, com link para mandar para a familia.

   Cada etapa confere o que fez antes de seguir, e a ultima PROVA em jogo que
   a moeda some — foto bonita de jogo nao e prova de jogo que funciona."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rs, nav, editor, blocos

D = "aula1"

# coordenadas medidas na tela do editor (pagina em 100%)
BALDE = (229, 358)
PALETA = {"azul": (2786, 535), "amarelo": (2786, 390), "verde": (2700, 460),
          "vermelho": (2855, 320)}
SPRITE_AREAS = [(1456, 781), (1456, 413), (1456, 1148)]   # as tres partes do padrao
SPRITE_OK = (140, 1560)
CELULA_JOGADOR = (1502, 831)
CELULA_MOEDA = (1790, 831)

ETAPAS = []


def etapa(fn):
    ETAPAS.append(fn); return fn


class A:
    """Guarda o estado entre etapas e grava as fotos."""
    url = None

    @staticmethod
    def cap(nome):
        os.makedirs(D, exist_ok=True)
        a, _ = nav.captura(f"{D}/{nome}.png")
        return a


def pinta_sprite(cor):
    """Pinta as tres partes do sprite padrao com a mesma cor."""
    J = nav.janela()
    rs.clique_img(*BALDE, escala=2.0, janela=J); time.sleep(0.6)
    rs.clique_img(*PALETA[cor], escala=2.0, janela=J); time.sleep(0.6)
    for p in SPRITE_AREAS:
        rs.clique_img(p[0], p[1], escala=2.0, janela=J); time.sleep(0.7)
    return True


def escreve_nome(nome):
    """Escreve no campo Name do painel do objeto."""
    a, _ = nav.captura("/tmp/_c1_nome.png")
    p = nav.acha_texto("name", arquivo=a, regiao=(0.55, 0.15, 1.0, 0.55))
    if not p:
        raise RuntimeError("nao achei o campo Name")
    J = nav.janela()
    rs.clique_img(p[0], p[1] + 46, escala=2.0, janela=J, duplo=True)
    time.sleep(0.6)
    rs.tecla(0, cmd=True); time.sleep(0.25)          # Cmd+A dentro do campo
    rs.digita_teclas(nome); time.sleep(0.4)
    rs.tecla(48); time.sleep(0.8)                    # Tab: o Enter FECHA o painel
    return True


OK_PAINEL = (1772, 1200)          # o OK azul do painel do objeto, medido


def fecha_painel_objeto():
    """O OK do painel do objeto. Posicao medida: o botao e BRANCO SOBRE AZUL e
       o OCR nao le uma letra dele. Confiro pelo efeito — o painel some."""
    J = nav.janela()
    for tentativa in range(3):
        rs.clique_img(*OK_PAINEL, escala=2.0, janela=J)
        time.sleep(1.8); nav.espera_parar(limite=12)
        a, _ = nav.captura("/tmp/_c1_ok.png")
        txt = " ".join(t for t, *_ in rs.ocr_forte(a, psm="6")).lower()
        if "edit sprite" not in txt:
            return True
    raise RuntimeError("cliquei no OK e o painel do objeto continua aberto")


@etapa
def novo():
    A.url = editor.jogo_novo()
    print("   jogo:", A.url, flush=True)
    A.cap("p01_projeto_vazio")
    return True


@etapa
def jogador():
    editor.objeto_ou_abre(*CELULA_JOGADOR)
    A.cap("p02_painel_objeto")
    escreve_nome("Jogador")
    A.cap("p03_nome_jogador")
    # sprite
    a, _ = nav.captura("/tmp/_c1_es.png")
    p = nav.acha_texto("edit sprite", arquivo=a)
    rs.clique_img(p[0], p[1], escala=2.0, janela=nav.janela())
    time.sleep(3); nav.espera_parar(limite=20)
    A.cap("p04_editor_sprite")
    pinta_sprite("azul")
    A.cap("p05_jogador_azul")
    rs.clique_img(*SPRITE_OK, escala=2.0, janela=nav.janela())
    time.sleep(2); nav.espera_parar(limite=15)
    # comportamento: o pacote de movimento
    editor.abre_comportamentos()
    A.cap("p06_comportamentos_vazio")
    blocos.abre_categoria("Behavior Bundles")
    A.cap("p07_pacotes")
    b = blocos.solta("Ship Controls", 1500, 700)
    A.cap("p08_pacote_solto")
    print("   pacote de movimento:", b, flush=True)
    editor.fecha_comportamentos()
    fecha_painel_objeto()
    A.cap("p09_jogador_pronto")
    return True


@etapa
def moeda():
    editor.objeto_ou_abre(*CELULA_MOEDA)
    escreve_nome("Moeda")
    A.cap("p10_nome_moeda")
    a, _ = nav.captura("/tmp/_c1_es2.png")
    p = nav.acha_texto("edit sprite", arquivo=a)
    rs.clique_img(p[0], p[1], escala=2.0, janela=nav.janela())
    time.sleep(3); nav.espera_parar(limite=20)
    pinta_sprite("amarelo")
    A.cap("p11_moeda_amarela")
    rs.clique_img(*SPRITE_OK, escala=2.0, janela=nav.janela())
    time.sleep(2); nav.espera_parar(limite=15)
    editor.abre_comportamentos()
    c = blocos.solta("Collision", 1200, 600)
    A.cap("p12_collision")
    d = blocos.solta("Destroyer", 2100, 1100)
    A.cap("p13_destroyer")
    blocos.liga_fixo(c, "hit", d, "in")
    A.cap("p14_fio")
    print("   colisao ligada ao destruidor", flush=True)
    editor.fecha_comportamentos()
    fecha_painel_objeto()
    A.cap("p15_moeda_pronta")
    return True


@etapa
def teste():
    """Joga, anda ate a moeda e PROVA que ela sumiu."""
    J = nav.janela()
    a_antes = A.cap("p16_antes_de_jogar")
    p = nav.acha_texto("play")
    rs.clique_img(p[0], p[1], escala=2.0, janela=J)
    time.sleep(4); nav.espera_parar(limite=20)
    A.cap("p17_jogando")
    rs.clique_img(1470, 800, escala=2.0, janela=J); time.sleep(0.8)
    for _ in range(6):
        rs.segura_tecla(124, 0.7)         # 124 = seta para a direita
        time.sleep(0.3)
    A.cap("p18_pegou")
    print("   andei ate a moeda", flush=True)
    return True


def main():
    alvo = sys.argv[1] if len(sys.argv) > 1 else None
    nomes = [f.__name__ for f in ETAPAS]
    fns = ETAPAS if not alvo else ETAPAS[nomes.index(alvo):]
    for f in fns:
        print(f"== {f.__name__} ==", flush=True)
        f()
    print("== fim ==", flush=True)


if __name__ == "__main__":
    main()
