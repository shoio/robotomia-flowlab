#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aula 10 — Menu, fases e fim de jogo. Constroi o jogo no Flowlab e fotografa cada gesto.

   O jogo: TELA DE TITULO com um botao JOGAR -> FASE 1 -> FASE 2 -> VITORIA.
   Cada tela e um NIVEL do jogo; quem leva de um para o outro e um bloco so, o
   `Load Level`, que por padrao carrega o PROXIMO nivel.

   O que e NOVO:
     - o painel `Game Levels`: varios niveis, cada um com nome e cor de ceu;
     - `MouseClick` (o clique do mouse NO objeto) e `Load Level`;
     - a Biblioteca: o tipo que voce criou numa fase e ARRASTADO para a outra,
       com os mesmos blocos — fase nova sem montar tudo de novo.

   MEDIDO ANTES (PADRAO.md §2ak), nos prototipos 3166077 a 3166085:
     - `New Level` cria um nivel VAZIO, chamado `New Level`, de ceu branco;
     - `Load Level` nasce em `Next Level`: nao precisa mexer no painel;
     - `MouseClick` so dispara no objeto (sem `capture clicks anywhere`), e o
       clique da bancada o dispara: botao -> nivel 2 mudou o ceu de 1D3557
       para FFE5B4;
     - a Biblioteca lista os TIPOS; clicar no cartao nao faz nada, ARRASTAR
       solta uma instancia na casa;
     - o painel `Game Levels` cresce para CIMA: as linhas se contam a partir
       do `Loading Screen` (ultima linha: -91 px; cada anterior: +74).

       BANCADA=1 python3 fonte/roda_aula.py 10
"""
import os, shutil, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rs, nav, editor, blocos, comum

comum.pasta("aula10")
import aula_comum as AC
from aula_comum import (celula, clique, A, etapa, ETAPAS, cria_objeto, clona,
                        clona_casas, da_fisica, confere_fisica, abre_mesa,
                        fecha_mesa, rastreio, cor)
from comum import fecha_painel_objeto
ETAPAS.clear()

D = "aula10"
CEUS = {"Titulo": "1D3557", "Fase 1": "A8DADC", "Fase 2": "F1FAEE",
        "Vitoria": "FFE5B4"}
AC.SPRITES = {
    "Botao":   ("Flowlab Sprites", "Blocks", 4, 0),        # o tijolo rosa
    "Jogador": ("Flowlab Sprites", "Characters", 0, 0),
    "Chao":    ("Flowlab Sprites", "Blocks", 0, 0),
    "Estrela": ("Flowlab Sprites", "Objects", 9, 1),       # a estrela dourada
    "Faixa":   ("Flowlab Sprites", "Objects", 9, 1),
}

LINHA_CHAO = 10
CEL_BOTAO = (7, 5)
CEL_JOGADOR = (1, 8)
CEL_ESTRELA_1 = (13, 9)          # no chao: basta andar
CEL_ESTRELA_2 = (12, 7)          # no ar: exige o pulo
CEL_FAIXA = (6, 5)
Y_A, Y_B = 450, 1000


def _ceu_agora():
    """A cor do ceu na pagina do jogo, num ponto do alto e da direita da folha
       (o texto da fase e os rotulos ficam do outro lado)."""
    import numpy as np
    from PIL import Image
    a, _ = nav.captura("/tmp/_c10_ceu.png")
    im = np.asarray(Image.open(a).convert("RGB"), dtype=int)
    reg = im[270:320, 1700:1760].reshape(-1, 3)
    return tuple(int(v) for v in np.median(reg, axis=0))


def _e(hexa):
    return tuple(int(hexa[i:i + 2], 16) for i in (0, 2, 4))


def _parece(cor_lida, hexa, tol=18):
    return max(abs(a - b) for a, b in zip(cor_lida, _e(hexa))) <= tol


def _gifs_comuns():
    os.makedirs(f"{D}/gifs", exist_ok=True)
    for nome in ("abrir_my_games.gif", "novo_jogo.gif", "empty_project.gif"):
        if not os.path.exists(f"{D}/gifs/{nome}") and os.path.exists(f"aula9/gifs/{nome}"):
            shutil.copy(f"aula9/gifs/{nome}", f"{D}/gifs/{nome}")


def _toca_o_play():
    """Aperta Play e DEVOLVE NA HORA (ver §2ai: prova de coisa em movimento
       comeca no clique)."""
    editor.volta_ao_nivel(); time.sleep(1.5)
    p = nav.acha_texto("play")
    if not p:
        raise RuntimeError("nao achei o botao Play (estou mesmo no editor?)")
    clique(*p)


def _acha_o_botao(im):
    """(x, y) do botao na tela do titulo, por COR (o tijolo rosa)."""
    import numpy as np
    cor_b, tol = rastreio("Botao")
    m = comum.mascara_cor(im, cor_b, tol)
    ys, xs = np.nonzero(m[150:1000, 900:2050])
    if len(xs) < 60:
        return None
    return int(xs.mean()) + 900, int(ys.mean()) + 150


@etapa
def novo():
    A.url = editor.jogo_novo()
    print("   jogo:", A.url, flush=True)
    A.guarda_url()
    comum.calibra_grade(16, 12)
    A.cap("p01_vazio")
    _gifs_comuns()
    return True


@etapa
def titulo():
    """A primeira tela: nome `Titulo` e ceu azul-escuro."""
    editor.volta_ao_nivel()
    A.gesto("abrir_niveis", "g08a", (0, 0), lambda: editor.abre_niveis(), espera=1.8)
    A.gesto("nome_do_nivel", "g08n", (0, 0),
            lambda: editor.escreve_no_nivel(0, 1, "nome", "Titulo"), espera=1.5)
    editor.abre_niveis()
    A.gesto("pintar_o_ceu", "g08", (0, 0),
            lambda: editor.escreve_no_nivel(0, 1, "cor", CEUS["Titulo"]), espera=2.0)
    editor.volta_ao_nivel()
    lida = editor.cor_da_folha()
    if max(abs(a - b) for a, b in zip(lida, _e(CEUS["Titulo"]))) > 20:
        raise RuntimeError(f"o ceu do Titulo ficou {lida}, e eu pedi {CEUS['Titulo']}")
    editor.abre_niveis()
    editor.confere_nome_do_nivel(0, 1, "Titulo")
    A.cap("p02_titulo")
    p = nav.acha_texto("ok")
    clique(*p) if p else clique(1345, 1389)
    time.sleep(1.2)
    return True


@etapa
def botao():
    """O objeto BOTAO, no meio do Titulo."""
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    x, y = celula(*CEL_BOTAO)
    A.gesto("criar_objeto", "g01", (x, y), lambda: clique(x, y), espera=1.5)
    a, _ = nav.captura("/tmp/_c10_rad.png")
    p = nav.acha_texto("create", arquivo=a)
    A.gesto("escolher_create", "g02", p, lambda: clique(*p), espera=3)
    editor.espera_tela("behaviors", limite=20)
    comum.nomeia("Botao"); comum.nomeia_tipo("Botao")
    A.cap("p03_nome")
    comum.abre_sprite()
    pacote, sub, lin, col = AC.SPRITES["Botao"]
    comum.abre_grade_sprite(pacote, sub)
    A.gesto("escolher_sprite", "g13", (0, 0),
            lambda: AC.poe_sprite("Botao", so_clique=True), espera=2.0)
    clique(*comum.SPRITE_OK); time.sleep(2); nav.espera_parar(limite=15)
    A.cap("p04_botao")
    fecha_painel_objeto(); time.sleep(1.5)
    return True


def _nivel_novo(total, nome, sufixo):
    """New Level + nome + cor, com os TRES gestos gravados em clipes.

       O `sufixo` torna a CHAVE do clipe unica por fase: com a mesma chave a
       Vitoria sobrescrevia, em `alvos.json`, o clipe da Fase 1."""
    editor.abre_niveis()
    A.gesto(f"novo_nivel_{sufixo}", f"g17n{sufixo}", (0, 0),
            lambda: editor.novo_nivel(), espera=1.5)
    A.gesto(f"nome_da_fase_{sufixo}", f"g17m{sufixo}", (0, 0),
            lambda: editor.escreve_no_nivel(total - 1, total, "nome", nome),
            espera=1.5)
    editor.abre_niveis()
    A.gesto(f"cor_da_fase_{sufixo}", f"g17c{sufixo}", (0, 0),
            lambda: editor.escreve_no_nivel(total - 1, total, "cor", CEUS[nome]),
            espera=2.0)


def _carrega_gravando(n, total, chave, base):
    """Abre o painel e carrega a fase `n`, gravando o `Load` como clipe."""
    editor.volta_ao_nivel()
    editor.abre_niveis()
    A.gesto(chave, base, (0, 0),
            lambda: editor.carrega_com_painel_aberto(n, total), espera=2.0)
    editor.volta_ao_nivel(); time.sleep(1)


@etapa
def fase1():
    """A SEGUNDA tela: `Fase 1`, de ceu azul-claro."""
    _nivel_novo(2, "Fase 1", "f1")
    editor.abre_niveis()
    editor.confere_nome_do_nivel(1, 2, "Fase 1")
    A.cap("p05_fase1")
    clique(1345, 1389); time.sleep(1.2)
    return True


@etapa
def clique_do_botao():
    """O botao manda para a PROXIMA fase: `MouseClick.down` -> `Load Level.go`."""
    editor.carrega_nivel(0, 2)
    abre_mesa(*CEL_BOTAO)
    blocos.abre_categoria("Triggers")
    blocos.bloco_ou_solta("MouseClick", 800, Y_A)
    blocos.abre_categoria("Game Flow")
    blocos.bloco_ou_solta("Load Level", 1700, Y_A, titulo="LoadLevel")
    mc = blocos.acha_bloco("MouseClick")
    ll = blocos.acha_bloco("LoadLevel")
    blocos.liga_fixo(mc, "down", ll, "go")
    print("   botao: MouseClick.down -> Load Level.go (Next Level)", flush=True)
    A.cap("p06_clique")
    time.sleep(2)
    fecha_mesa()
    return True


@etapa
def rotulo():
    """O TEXTO do botao: um `Label` GRUDADO no objeto (`attach to object`)."""
    abre_mesa(*CEL_BOTAO)
    blocos.abre_categoria("GUI")
    # o `Label` ESCREVE O PROPRIO TEXTO dentro da fase e `acha_bloco` casaria com
    # ela: o recorte, a direita da tela, deixa so a mesa de blocos
    blocos.bloco_ou_solta("Label", 2500, Y_B, regiao=(0.62, 0.45, 1.0, 0.98))
    lb = blocos.acha_bloco("Label", regiao=(0.62, 0.45, 1.0, 0.98))
    blocos.abre_ajustes(lb); time.sleep(1.6)
    A.gesto("escrever_o_texto", "g18", (0, 0),
            lambda: blocos.escreve_texto_do_label("JOGAR"), espera=1.2)
    A.gesto("cor_do_texto", "g18c", (0, 0),
            lambda: blocos.cor_do_texto_do_label("FFFFFF"), espera=1.2)
    blocos.marca_do_bloco("attach to object", True)
    blocos.fecha_ajustes(); time.sleep(1.0)
    A.cap("p07_rotulo")
    time.sleep(2)
    fecha_mesa()
    return True


@etapa
def prova_titulo():
    """A promessa do passo 11: clicar no JOGAR leva a Fase 1 (o ceu muda)."""
    import numpy as np
    from PIL import Image
    editor.volta_ao_nivel(); time.sleep(1.5)
    p = nav.acha_texto("play")
    antes = A.cap("g19_a")
    comum.CLIQUES.clear()
    clique(*p); time.sleep(3.0)
    im = np.asarray(Image.open(nav.captura("/tmp/_c10_t.png")[0]).convert("RGB"), dtype=int)
    cor_titulo = _ceu_agora()
    A.cap("p08_titulo")
    bx = _acha_o_botao(im)
    print(f"   ceu do titulo {cor_titulo}; botao em {bx}", flush=True)
    if not _parece(cor_titulo, CEUS["Titulo"]):
        raise RuntimeError(f"o jogo nao comecou no Titulo: ceu {cor_titulo}")
    if not bx:
        raise RuntimeError("nao achei o botao na tela do titulo")
    clique(*bx); time.sleep(2.5)
    depois = A.cap("g19_b")
    cor_f1 = _ceu_agora()
    print(f"   ceu depois do clique: {cor_f1}", flush=True)
    A.reg("clicar_no_botao", antes=antes, depois=depois,
          alvo=[int(bx[0]), int(bx[1])], botao="esq", clicado=True)
    if not _parece(cor_f1, CEUS["Fase 1"]):
        raise RuntimeError(f"cliquei no botao e o ceu e {cor_f1}, nao o da Fase 1 "
                           f"({CEUS['Fase 1']})")
    print("   PROVADO: o clique no JOGAR trocou o ceu do Titulo pelo da Fase 1",
          flush=True)
    editor.volta_ao_editor(); time.sleep(2)
    return True


@etapa
def jogador():
    """O JOGADOR, na Fase 1 (a carregada no editor)."""
    _carrega_gravando(1, 2, "carregar_a_fase_1", "g21a")
    comum.calibra_grade(16, 12)
    x, y = celula(*CEL_JOGADOR)
    cria_objeto(*CEL_JOGADOR, "Jogador", tipo="Jogador")
    editor.objeto_ou_abre(x, y)
    da_fisica(movable=True, gravidade=True, atrito=False)
    A.cap("p09_jogador")
    fecha_painel_objeto(); time.sleep(1.5)
    editor.objeto_ou_abre(x, y)
    confere_fisica(movable=True, gravidade=True)
    fecha_painel_objeto(); time.sleep(1.5)
    return True


@etapa
def anda():
    abre_mesa(*CEL_JOGADOR)
    blocos.abre_categoria("Behavior Bundles")
    blocos.bloco_ou_solta("Run & Jump", 1500, 760)
    A.cap("p10_correr")
    time.sleep(2.5)
    fecha_mesa()
    return True


@etapa
def chao():
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    cria_objeto(0, LINHA_CHAO, "Chao", tipo="Chao")
    A.gesto("clonar_o_chao", "g05", (0, 0),
            lambda: clona(0, LINHA_CHAO, "Chao", range(1, 16)), espera=2.0)
    A.cap("p11_chao")
    return True


@etapa
def estrela():
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    cria_objeto(*CEL_ESTRELA_1, "Estrela", tipo="Estrela")
    A.cap("p12_estrela")
    return True


@etapa
def fase2():
    """A TERCEIRA tela, ja criada antes da estrela: ela precisa ter para onde
       levar."""
    _nivel_novo(3, "Fase 2", "f2")
    editor.abre_niveis()
    editor.confere_nome_do_nivel(2, 3, "Fase 2")
    A.cap("p13_fase2")
    clique(1345, 1389); time.sleep(1.2)
    return True


@etapa
def vai():
    """A ESTRELA leva a proxima fase: `Collision(Jogador)` -> `Load Level.go`."""
    editor.carrega_nivel(1, 3)
    abre_mesa(*CEL_ESTRELA_1)
    blocos.abre_categoria("Triggers")
    blocos.bloco_ou_solta("Collision", 800, Y_A)
    co = blocos.acha_bloco("Collision")
    blocos.escolhe_tipo_da_colisao(co, "Jogador")
    blocos.abre_categoria("Game Flow")
    blocos.bloco_ou_solta("Load Level", 1700, Y_A, titulo="LoadLevel")
    co = blocos.acha_bloco("Collision")
    ll = blocos.acha_bloco("LoadLevel")
    blocos.liga_fixo(co, "hit", ll, "go")
    print("   estrela: Collision(Jogador).hit -> Load Level.go", flush=True)
    A.cap("p14_vai")
    time.sleep(2)
    fecha_mesa()
    return True


def _corre_ate_o_ceu_mudar(ceu_de_chegada, limite=14):
    """Corre para a direita ate o ceu virar `ceu_de_chegada`."""
    for k in range(limite):
        rs.corre_e_pula(direcao=124, antes=0.05, segurando=0.55)
        time.sleep(0.4)
        c = _ceu_agora()
        if _parece(c, ceu_de_chegada):
            return True, k + 1
    return False, limite


def _do_titulo_a_fase(total, gravando=None):
    """Carrega o TITULO, aperta Play, clica no botao -> (na Fase 1).

       ⛔ MEDIDO: o Play comeca na fase que esta ABERTA NO EDITOR, nao na
       primeira. Eu jogava depois de ter editado a Fase 1 e o jogo abria nela,
       sem botao nenhum — a prova dizia `nao achei o botao no Titulo`. Quem
       quer testar a corrente inteira tem de CARREGAR o Titulo antes."""
    import numpy as np
    from PIL import Image
    if gravando:
        _carrega_gravando(0, total, *gravando)
    else:
        editor.carrega_nivel(0, total)
    _toca_o_play(); time.sleep(3.0)
    im = np.asarray(Image.open(nav.captura("/tmp/_c10_t2.png")[0]).convert("RGB"), dtype=int)
    bx = _acha_o_botao(im)
    if not bx:
        raise RuntimeError("nao achei o botao no Titulo")
    clique(*bx); time.sleep(2.5)
    clique(1470, 620)
    return bx


@etapa
def prova_fase1():
    """A promessa do passo 18: a estrela da Fase 1 leva a Fase 2."""
    _do_titulo_a_fase(3, gravando=("carregar_o_titulo", "g22"))
    chegou, n = _corre_ate_o_ceu_mudar(CEUS["Fase 2"])
    A.cap("p15_fase1_vencida")
    print(f"   chegou na estrela em {n} corridas: {chegou}", flush=True)
    editor.exige_jogo()
    if not chegou:
        raise RuntimeError("corri ate o fim da Fase 1 e o ceu nao virou o da Fase 2")
    print("   PROVADO: tocar a estrela da Fase 1 carregou a Fase 2 (ceu "
          f"{CEUS['Fase 2']})", flush=True)
    editor.volta_ao_editor(); time.sleep(2)
    return True


@etapa
def biblioteca():
    """A FASE 2: os mesmos tipos, arrastados da Biblioteca — e os blocos vem
       junto, porque pertencem ao TIPO."""
    _carrega_gravando(2, 3, "carregar_a_fase_2", "g21b")
    comum.calibra_grade(16, 12)
    # o chao primeiro, numa casa FORA do painel da Biblioteca (a faixa de baixo
    # e coberta por ele), e depois clonado ate a ponta esquerda
    A.gesto("arrastar_da_biblioteca", "g20", (0, 0),
            lambda: editor.arrasta_da_biblioteca("Chao", 15, LINHA_CHAO), espera=1.5)
    editor.fecha_biblioteca()
    editor.arrasta_da_biblioteca("Jogador", *CEL_JOGADOR)
    editor.fecha_biblioteca()
    editor.arrasta_da_biblioteca("Estrela", *CEL_ESTRELA_2)
    editor.fecha_biblioteca()
    clona(15, LINHA_CHAO, "Chao", range(14, -1, -1))
    A.cap("p16_biblioteca")
    return True


@etapa
def vitoria():
    """A QUARTA tela e o objeto que a escreve: `Faixa` com um `Label`."""
    _nivel_novo(4, "Vitoria", "vit")
    editor.abre_niveis()
    editor.confere_nome_do_nivel(3, 4, "Vitoria")
    clique(1345, 1389); time.sleep(1.2)
    _carrega_gravando(3, 4, "carregar_a_vitoria", "g21c")
    comum.calibra_grade(16, 12)
    cria_objeto(*CEL_FAIXA, "Faixa", tipo="Faixa")
    abre_mesa(*CEL_FAIXA)
    blocos.abre_categoria("GUI")
    # Y_B, e nao Y_A: o recorte (0.45..0.98 da altura) so enxerga a metade de
    # BAIXO da mesa. Com Y_A o bloco caia fora dele, a leitura do titulo falhava,
    # `solta` RECARREGAVA a pagina — e o editor reabria no primeiro nivel (o
    # Titulo), com a mesa do objeto errado.
    blocos.bloco_ou_solta("Label", 2000, Y_B, regiao=(0.62, 0.45, 1.0, 0.98))
    lb = blocos.acha_bloco("Label", regiao=(0.62, 0.45, 1.0, 0.98))
    blocos.abre_ajustes(lb); time.sleep(1.6)
    blocos.escreve_texto_do_label("VOCE VENCEU")
    blocos.cor_do_texto_do_label("7A4F00")
    blocos.marca_do_bloco("attach to object", True)
    blocos.fecha_ajustes(); time.sleep(1.0)
    A.cap("p17_vitoria")
    time.sleep(2)
    fecha_mesa()
    return True


@etapa
def prova_tudo():
    """A promessa do passo 21: titulo -> fase 1 -> fase 2 -> vitoria."""
    _do_titulo_a_fase(4)
    ok1, n1 = _corre_ate_o_ceu_mudar(CEUS["Fase 2"])
    if not ok1:
        raise RuntimeError("a Fase 1 nao levou a Fase 2")
    time.sleep(1.0)
    clique(1470, 620)
    ok2, n2 = _corre_ate_o_ceu_mudar(CEUS["Vitoria"], limite=18)
    time.sleep(1.0)
    A.cap("p18_final")
    print(f"   Fase 1 em {n1} corridas, Fase 2 em {n2}", flush=True)
    editor.exige_jogo()
    if not ok2:
        raise RuntimeError("a Fase 2 nao levou a Vitoria")
    print("   PROVADO: Titulo -> Fase 1 -> Fase 2 -> Vitoria, tudo jogado do "
          "comeco ao fim", flush=True)
    editor.volta_ao_editor(); time.sleep(2)
    return True


def main():
    AC.main(sys.modules[__name__])


if __name__ == "__main__":
    main()
