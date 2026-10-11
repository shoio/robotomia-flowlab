#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aula 6 — Chave e porta. Constroi o jogo no Flowlab e fotografa cada gesto.

   O jogo: um boneco que corre e pula, uma PORTA fechando o caminho e uma
   CHAVE no chao. Encostar na chave manda um RECADO para a porta, e a porta
   some. Atras dela, a estrela.

   O que e NOVO: dois objetos CONVERSANDO. Ate aqui cada peca so sabia de si.

   MEDIDO ANTES (PADRAO.md §2u), no prototipo 3155573:
   - `Message` tem `send` e `done`; `Mailbox` so tem `out`. Os dois nascem
     combinados em `Hello`, entao a aula nao precisa criar nome de recado;
   - o `Send To` nasce em `Myself` e NAO tem opcao de "todo mundo": o caminho
     e `Choose objects` -> `Select Type` -> `Porta`, que cobra o `Type` que o
     curso ensina desde a Aula 1;
   - o seletor do `Send To` fica na linha de BAIXO do rotulo (dai o `dy=55`);
   - PROVADO: com `Once -> Message` na chave e `Mailbox -> Destroyer` na porta,
     no editor havia dois objetos e no jogo so um — a porta some.

   E uma decisao de fiacao: o `hit` do `Collision` nao se divide em dois. A
   corrente e `Collision.hit -> Message.send` e `Message.done -> Destroyer.in`,
   que alem de nao supor nada sobre fio que se reparte, le-se melhor: *quando
   encostarem em mim, mande o recado; quando o recado sair, suma*.

       BANCADA=1 python3 fonte/roda_aula.py 6
"""
import os, shutil, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rs, nav, editor, blocos, comum

comum.pasta("aula6")
import aula_comum as AC
from aula_comum import (celula, clique, A, etapa, ETAPAS, cria_objeto, clona,
                        clona_casas, da_fisica, confere_fisica, abre_mesa,
                        fecha_mesa, rastreio, cor)
from comum import fecha_painel_objeto
ETAPAS.clear()

D = "aula6"
CEU = "A8DADC"          # azul claro: a porta e escura e precisa aparecer nele
AC.SPRITES = {
    "Jogador": ("Flowlab Sprites", "Characters", 0, 0),   # o menino das outras aulas
    "Chao":    ("Flowlab Sprites", "Blocks", 0, 0),       # o bloco de grama
    "Porta":   ("Flowlab Sprites", "Blocks", 3, 0),       # o vao escuro com batente
    "Chave":   ("Flowlab Sprites", "Objects", 6, 2),      # a chave dourada
    "Estrela": ("Flowlab Sprites", "Objects", 9, 1),      # a estrela dourada
}

LINHA_CHAO = 10
CEL_JOGADOR = (2, 9)
CEL_CHAVE = (6, 9)
CEL_PORTA = (9, 9)
CASAS_DA_PORTA = [(9, 8), (9, 7)]      # a porta sobe tres casas e fecha a passagem
CEL_ESTRELA = (13, 9)

FILA_A = (0.12, 0.06, 1.0, 0.50)
FILA_B = (0.12, 0.50, 1.0, 0.96)
Y_A, Y_B = 560, 1150


def _area_do_jogo(im):
    """A caixa (y0, y1, x0, x1) do retangulo da fase, achada pela COR DO CEU.

       Sem este recorte eu media a tela inteira — inclusive a barra escura do
       navegador, no alto da pagina. O escuro da porta casava com ela, e o
       "topo do escuro" ficava preso em y=31 antes e depois: 31 -> 31, numa
       tela em que a porta tinha sumido. Medida que nao muda NUNCA e sintoma
       de instrumento apontado para o lugar errado.

       O ceu serve de regua porque e cor que ESTA AULA pinta."""
    import numpy as _np
    rgb = tuple(int(CEU[i:i + 2], 16) for i in (0, 2, 4))
    ys, xs = _np.nonzero(comum.mascara_cor(im, rgb, 16))
    if len(ys) < 20000:
        raise RuntimeError(f"nao achei o ceu da fase na tela ({len(ys)} px) — "
                           "sem ele nao ha onde medir")
    return int(ys.min()), int(ys.max()), int(xs.min()), int(xs.max())


@etapa
def novo():
    A.url = editor.jogo_novo()
    print("   jogo:", A.url, flush=True)
    A.guarda_url()
    comum.calibra_grade(16, 12)
    A.cap("p01_vazio")
    for nome in ("abrir_my_games.gif", "novo_jogo.gif", "empty_project.gif"):
        os.makedirs(f"{D}/gifs", exist_ok=True)
        if not os.path.exists(f"{D}/gifs/{nome}"):
            shutil.copy(f"aula5/gifs/{nome}", f"{D}/gifs/{nome}")
    A.gesto("abrir_niveis", "g08a", (0, 0), lambda: editor.abre_niveis(), espera=1.8)
    A.gesto("pintar_o_ceu", "g08", (0, 0),
            lambda: editor.cor_do_ceu(CEU, abrir=False), espera=2.0)
    editor.volta_ao_nivel()
    A.cap("p02_ceu")
    return True


@etapa
def jogador():
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    x, y = celula(*CEL_JOGADOR)
    A.gesto("criar_objeto", "g01", (x, y), lambda: clique(x, y), espera=1.5)
    a, _ = nav.captura("/tmp/_c6_rad.png")
    p = nav.acha_texto("create", arquivo=a)
    A.gesto("escolher_create", "g02", p, lambda: clique(*p), espera=3)
    editor.espera_tela("behaviors", limite=20)
    comum.nomeia("Jogador"); comum.nomeia_tipo("Jogador")
    A.cap("p03_nome")
    comum.abre_sprite()
    pacote, sub, lin, col = AC.SPRITES["Jogador"]
    comum.abre_grade_sprite(pacote, sub)
    A.gesto("escolher_sprite", "g13", (0, 0),
            lambda: AC.poe_sprite("Jogador", so_clique=True), espera=2.0)
    clique(*comum.SPRITE_OK); time.sleep(2); nav.espera_parar(limite=15)
    A.cap("p04_jogador")
    A.gesto("abrir_physics", "g03", (0, 0), lambda: comum.abre_fisica(), espera=2.5)
    A.gesto("marcar_movable", "g04", (0, 0),
            lambda: comum.marca_caixa("movable", True), espera=1.2)
    comum.marca_caixa("affected by gravity", True)
    A.cap("p05_fisica")
    fecha_painel_objeto(); time.sleep(1.5)
    editor.objeto_ou_abre(x, y)
    confere_fisica(movable=True, gravidade=True)
    fecha_painel_objeto(); time.sleep(1.5)
    return True


@etapa
def anda():
    """O pacote `Run & Jump`, o mesmo da Aula 2: um arrasto so."""
    abre_mesa(*CEL_JOGADOR)
    blocos.abre_categoria("Behavior Bundles")
    b = blocos.bloco_ou_solta("Run & Jump", 1500, 760)
    print("   pacote:", b.nome, flush=True)
    A.cap("p06_correr")
    time.sleep(2.5)
    fecha_mesa()
    return True


@etapa
def chao():
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    cria_objeto(0, LINHA_CHAO, "Chao", tipo="Chao")
    A.gesto("clonar_o_chao", "g05", (0, 0),
            lambda: clona(0, LINHA_CHAO, "Chao", range(1, 16)), espera=2.0)
    A.cap("p07_chao")
    return True


@etapa
def prova_anda():
    """A promessa do passo 12: a seta da direita leva o boneco para a direita."""
    import numpy as np
    from PIL import Image
    cor_j, tol = rastreio("Jogador", "Chao")
    print(f"   rastreando o jogador por {cor_j} (tol {tol})", flush=True)
    editor.volta_ao_editor(); time.sleep(2)
    editor.volta_ao_nivel()
    p = nav.acha_texto("play")
    if not p:
        raise RuntimeError("nao achei o botao Play")
    A.gesto("jogar", "g10", p, lambda: clique(*p), espera=6)
    editor.exige_jogo()
    clique(1470, 620); time.sleep(1.5)

    def onde():
        a, _ = nav.captura("/tmp/_c6_j.png")
        im = np.asarray(Image.open(a).convert("RGB"), dtype=int)
        m = comum.mascara_cor(im, cor_j, tol)
        _ys, xs = np.nonzero(m)
        return int(xs.mean()) if len(xs) else None

    antes = onde()
    rs.segura_tecla(rs.DIR, 1.2); time.sleep(0.5)
    depois = onde()
    A.cap("p08_andando")
    print(f"   x do jogador: {antes} -> {depois}", flush=True)
    if antes is None or depois is None:
        raise RuntimeError("perdi o jogador de vista")
    if depois <= antes + 40:
        raise RuntimeError(f"segurei a seta da direita e o jogador nao andou "
                           f"({antes} -> {depois})")
    print(f"   PROVADO: a seta da direita leva o jogador {depois - antes} px",
          flush=True)
    editor.volta_ao_editor(); time.sleep(2)
    return True


@etapa
def chave():
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    cria_objeto(*CEL_CHAVE, "Chave", tipo="Chave")
    A.cap("p09_chave")
    return True


@etapa
def porta():
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    cria_objeto(*CEL_PORTA, "Porta", tipo="Porta")
    A.gesto("levantar_a_porta", "g06", (0, 0),
            lambda: clona_casas(*CEL_PORTA, "Porta", CASAS_DA_PORTA), espera=2.0)
    A.cap("p10_porta")
    return True


@etapa
def chave_fala():
    """A CORRENTE DA CHAVE: encostaram -> mande o recado -> suma.

       O `done` do `Message` no lugar de repartir o `hit` do `Collision`: assim
       a aula nao supoe nada sobre fio que se divide, e a leitura em voz alta
       fica melhor."""
    abre_mesa(*CEL_CHAVE)
    blocos.abre_categoria("Triggers")
    c = AC._na_fila(blocos.bloco_ou_solta("Collision", 900, Y_A, regiao=FILA_A),
                    FILA_A, "Collision da chave")
    blocos.abre_categoria("Components")
    ms = AC._na_fila(blocos.bloco_ou_solta("Message", 1750, Y_A, regiao=FILA_A),
                     FILA_A, "Message da chave")
    de = AC._na_fila(blocos.bloco_ou_solta("Destroyer", 2500, Y_A, regiao=FILA_A),
                     FILA_A, "Destroyer da chave")
    blocos.liga_fixo(c, "hit", ms, "send")
    blocos.liga_fixo(ms, "done", de, "in")
    blocos.escolhe_tipo_da_colisao(c, "Jogador")
    # PARA QUEM VAI O RECADO. Ele nasce para `Myself` — a chave falando sozinha.
    blocos.abre_ajustes(ms); time.sleep(1.5)
    A.gesto("para_quem_vai", "g07", (0, 0),
            lambda: blocos.escolhe_na_lista("send to", "choose objects", dy=55),
            espera=1.6)
    time.sleep(1.0)
    blocos.escolhe_na_lista("select type", "porta")
    blocos.fecha_ajustes(); time.sleep(1.0)
    A.cap("p11_chave_fala")
    time.sleep(2)
    fecha_mesa()
    return True


@etapa
def porta_escuta():
    abre_mesa(*CEL_PORTA)
    blocos.abre_categoria("Triggers")
    mb = AC._na_fila(blocos.bloco_ou_solta("Mailbox", 1000, Y_A, regiao=FILA_A),
                     FILA_A, "Mailbox da porta")
    blocos.abre_categoria("Components")
    de = AC._na_fila(blocos.bloco_ou_solta("Destroyer", 1900, Y_A, regiao=FILA_A),
                     FILA_A, "Destroyer da porta")
    blocos.liga_fixo(mb, "out", de, "in")
    print("   porta: Mailbox -> Destroyer", flush=True)
    A.cap("p12_porta_escuta")
    time.sleep(2)
    fecha_mesa()
    return True


@etapa
def prova_recado():
    """A promessa do passo 19: encostar na chave ABRE a porta.

       O molde manda nas copias: a porta tem tres pedacos e os tres escutam o
       mesmo recado, entao o muro inteiro some de uma vez."""
    import numpy as np
    from PIL import Image
    # NAO RASTREIO A COR DA PORTA, e tentei duas vezes.
    #
    # Ela e um vao ESCURO, e o escuro dela mora em dois lugares que nao tem
    # nada a ver: a terra do chao (faixa larga, que fez a contagem cair so 13%
    # numa tela sem porta) e a barra do NAVEGADOR (que prendeu o "topo do
    # escuro" em y=31 antes e depois). Depois, recortando so a fase, a cor
    # escolhida nao aparecia em pixel nenhum.
    #
    # O que e inequivoco e o CEU, que esta aula pinta: com a porta de pe ha um
    # bloco alto no meio da fase; sem ela, aquela parte e so ceu. Entao eu
    # conto o que NAO e ceu na metade de cima — onde o chao, o boneco e a
    # chave nao chegam.
    editor.volta_ao_editor(); time.sleep(2)
    editor.volta_ao_nivel()
    p = nav.acha_texto("play")
    clique(*p); time.sleep(7); nav.espera_parar(limite=20)
    editor.exige_jogo()
    clique(1470, 620); time.sleep(1.5)

    def porta_na_tela():
        """Quantos pixels da METADE DE CIMA da fase nao sao ceu."""
        a, _ = nav.captura("/tmp/_c6_p.png")
        im = np.asarray(Image.open(a).convert("RGB"), dtype=int)
        y0, y1, x0, x1 = _area_do_jogo(im)
        rgb = tuple(int(CEU[i:i + 2], 16) for i in (0, 2, 4))
        ceu = comum.mascara_cor(im, rgb, 16)
        corte = y0 + int((y1 - y0) * 0.75)       # o chao e o boneco ficam abaixo
        return int((~ceu[y0:corte, x0:x1]).sum())

    antes = porta_na_tela()
    A.cap("p13_porta_fechada")
    # CORRE EM PASSINHOS E PARA ASSIM QUE A PORTA CAI.
    #
    # Com uma corrida unica de 3 s o boneco atravessava e saia pela beirada, e
    # a foto do passo 18 ficava um nivel VAZIO: sem porta, mas tambem sem
    # jogador e sem nada que a crianca reconheca. Quem decide a hora da foto e
    # a propria medida.
    depois = antes
    for _ in range(8):
        rs.segura_tecla(rs.DIR, 0.5)
        time.sleep(0.35)
        depois = porta_na_tela()
        if depois <= antes * 0.25:
            break
    A.cap("p14_porta_aberta")
    print(f"   pixels que nao sao ceu na metade de cima: antes {antes}, "
          f"depois {depois}", flush=True)
    if antes < 1500:
        raise RuntimeError(f"a metade de cima ja estava quase so ceu ANTES "
                           f"({antes} px) — a porta nasceu de pe mesmo?")
    if depois > antes * 0.25:
        raise RuntimeError(f"peguei a chave e a porta continua de pe "
                           f"({antes} -> {depois} px de nao-ceu)")
    print(f"   PROVADO: a metade de cima vai de {antes} a {depois} px de "
          "nao-ceu — a porta caiu quando a chave mandou o recado", flush=True)
    editor.volta_ao_editor(); time.sleep(2)
    return True


@etapa
def estrela():
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    cria_objeto(*CEL_ESTRELA, "Estrela", tipo="Estrela")
    A.cap("p15_estrela")
    abre_mesa(*CEL_ESTRELA)
    blocos.abre_categoria("Triggers")
    c = AC._na_fila(blocos.bloco_ou_solta("Collision", 1000, Y_A, regiao=FILA_A),
                    FILA_A, "Collision da estrela")
    blocos.abre_categoria("Components")
    # ⛔ NAO E `Alert`. A Aula 3 ja mediu isso em jogo: o `Alert` ESCURECE a
    # tela e nao desenha a caixa dentro do canvas da pagina do jogo — a
    # crianca encostaria na estrela e veria a tela apagar, sem uma palavra. A
    # estrela que SOME e a mesma peca da Aula 1, ja provada, e diz "peguei"
    # sem ambiguidade.
    de = AC._na_fila(blocos.bloco_ou_solta("Destroyer", 1900, Y_A, regiao=FILA_A),
                     FILA_A, "Destroyer da estrela")
    blocos.liga_fixo(c, "hit", de, "in")
    blocos.escolhe_tipo_da_colisao(c, "Jogador")
    A.cap("p16_estrela_ganha")
    time.sleep(2)
    fecha_mesa()
    return True


@etapa
def prova():
    """O fim: a porta abre e o caminho ate a estrela fica livre."""
    import numpy as np
    from PIL import Image
    cor_e, tol_e = rastreio("Estrela", "Chao", "Jogador", "Porta")
    editor.volta_ao_editor(); time.sleep(2)
    editor.volta_ao_nivel()
    p = nav.acha_texto("play")
    clique(*p); time.sleep(7); nav.espera_parar(limite=20)
    editor.exige_jogo()
    clique(1470, 620); time.sleep(1.5)

    def estrela_na_tela():
        a, _ = nav.captura("/tmp/_c6_e.png")
        im = np.asarray(Image.open(a).convert("RGB"), dtype=int)
        y0, y1, x0, x1 = _area_do_jogo(im)
        return int(comum.mascara_cor(im, cor_e, tol_e)[y0:y1, x0:x1].sum())

    antes = estrela_na_tela()
    # A FOTO DO PASSO 21 E O ULTIMO QUADRO COM A ESTRELA AINDA LA: porta
    # aberta, caminho livre e o premio a vista. Fotografar ANTES da corrida
    # mostrava a porta de pe, que e o contrario do que o passo promete;
    # fotografar DEPOIS mostrava um nivel vazio.
    depois = antes
    for _ in range(10):
        rs.segura_tecla(rs.DIR, 0.5)
        time.sleep(0.35)
        atual = estrela_na_tela()
        if atual <= antes * 0.2:
            depois = atual
            break
        A.cap("p17_jogo")
        depois = atual
    print(f"   pixels de estrela: antes {antes}, depois da corrida {depois}",
          flush=True)
    if antes < 400:
        raise RuntimeError(f"nao vi a estrela na tela nem ANTES ({antes} px) — "
                           "o rastreio esta cego, nao ha o que provar")
    if depois > antes * 0.2:
        raise RuntimeError(f"o jogador atravessou e a estrela continua la "
                           f"({antes} -> {depois} px)")
    print(f"   PROVADO: a estrela vai de {antes} a {depois} px — o caminho "
          "inteiro funciona: chave, porta que abre e estrela", flush=True)
    return True


def main():
    AC.main(sys.modules[__name__])


if __name__ == "__main__":
    main()
