#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Captura da Aula 3 — A lava que sobe.

   O jogo: o mesmo boneco que corre e pula, mas agora a lava NAO FICA PARADA.
   Ela sobe sozinha, do pe da tela para o alto, e quem nao subir a tempo
   recomeca. No alto fica a estrela, e encostar nela abre um aviso de vitoria.

   O que e NOVO em relacao a Aula 2: uma coisa que se mexe SEM ninguem apertar
   tecla nenhuma — `Always` + `Velocity` — e o fim de jogo com `Alert`.

   O que foi MEDIDO antes de escrever a aula (rascunho 3150191):
   - `Always.out -> Number.get -> Number.out -> Velocity.y` move o objeto, com
     `movable` marcado e `affected by gravity` DESMARCADO;
   - `+y` e para BAIXO: para subir, o numero e NEGATIVO;
   - com `-0.5` a lava sobe 27,2 px de tela por segundo — as 7 casas entre ela
     e a estrela levam ~16 s, que e o tempo de fuga da crianca (com `-1`
     seriam 8 s, tenso demais para quem esta aprendendo a pular);
   - o campo do valor ENGOLE o hifen digitado em primeiro lugar: o caminho e o
     botao `−`, que tira 1 por clique (0.5 e um clique = -0.5)."""
import os, sys, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rs, nav, editor, blocos, comum
from comum import (celula, clique, pinta, nomeia, abre_sprite, marca_caixa,
                   arrasta_slider, fecha_painel_objeto, A, etapa, ETAPAS,
                   CELULA, GRADE_X, GRADE_Y, SPRITE_OK)

comum.pasta("aula3")
ETAPAS.clear()
D = "aula3"

# o desenho da fase
LINHA_CHAO  = 8
LINHA_MEIO  = 6
LINHA_ALTA  = 4
LINHA_LAVA  = 11
COL_JOGADOR = 4
COLS_CHAO   = [3, 4, 5, 6]
COLS_MEIO   = [8, 9, 10]
COLS_ALTA   = [12, 13, 14]
COL_ESTRELA = 13
COLS_LAVA   = list(range(1, 16))

DENSIDADE = 30          # medido na Aula 2: pula 273 px e anda 60 px por toque
SUBIDA    = "0.5"       # digitado positivo; um clique no `−` deixa -0.5


def faz_peca(c, r, nome, cor, cols_clone=None):
    """Cria um objeto na casa (c, r), pinta, e clona para as colunas pedidas."""
    x, y = celula(c, r)
    editor.objeto_ou_abre(x, y)
    nomeia(nome)
    abre_sprite()
    pinta(cor)
    clique(*SPRITE_OK); time.sleep(2); nav.espera_parar(limite=15)
    fecha_painel_objeto()
    if cols_clone:
        clique(x, y); time.sleep(1.5)
        a, _ = nav.captura("/tmp/_c3_clone.png")
        p = nav.acha_texto("clone", arquivo=a)
        if not p:
            raise RuntimeError(f"nao achei Clone para {nome}")
        clique(*p); time.sleep(2)
        for cc in cols_clone:
            cx, cy = celula(cc, r)
            clique(cx, cy); time.sleep(1.0)
        q = nav.acha_texto("done cloning")
        clique(*q); time.sleep(2); nav.espera_parar(limite=15)
    return True


@etapa
def novo():
    A.url = editor.jogo_novo()
    print("   jogo:", A.url, flush=True)
    A.cap("p01_vazio")
    return True


@etapa
def jogador():
    x, y = celula(COL_JOGADOR, LINHA_CHAO - 1)
    A.gesto("criar_objeto", "g01", (x, y), lambda: clique(x, y), espera=1.5)
    a, _ = nav.captura("/tmp/_c3_rad.png")
    p = nav.acha_texto("create", arquivo=a)
    A.gesto("escolher_create", "g02", p, lambda: clique(*p), espera=3)
    editor.espera_tela("behaviors", limite=20)
    nomeia("Jogador")
    A.cap("p02_nome")
    abre_sprite()
    pinta("azul")
    A.cap("p03_azul")
    clique(*SPRITE_OK); time.sleep(2); nav.espera_parar(limite=15)
    a, _ = nav.captura("/tmp/_c3_fis.png")
    q = nav.acha_texto("physics", arquivo=a)
    A.gesto("abrir_physics", "g03", q, lambda: clique(*q), espera=2.5)
    A.gesto("marcar_movable", "g04", (0, 0),
            lambda: marca_caixa("movable", True), espera=1.2)
    pd = nav.acha_texto("density", arquivo=nav.captura("/tmp/_c3_d.png")[0],
                        regiao=(0.45, 0.1, 1.0, 0.85))
    alvo = (int(pd[0] + 155 + 2.75 * DENSIDADE), pd[1])
    A.gesto("peso_do_pulo", "g05", alvo, lambda: clique(*alvo), espera=1.2)
    arrasta_slider("friction")
    A.cap("p04_fisica")
    fecha_painel_objeto()
    return True


@etapa
def movimento():
    x, y = celula(COL_JOGADOR, LINHA_CHAO - 1)
    editor.objeto_ou_abre(x, y)
    editor.abre_comportamentos()
    blocos.abre_categoria("Behavior Bundles")
    b = blocos.solta("Run & Jump", 1400, 700)
    A.cap("p05_run_and_jump")
    print("   pacote:", b, flush=True)
    time.sleep(2.5)
    editor.fecha_comportamentos(); time.sleep(2.5)
    fecha_painel_objeto(); time.sleep(2)
    return True


@etapa
def plataformas():
    faz_peca(COLS_CHAO[0], LINHA_CHAO, "Chao", "verde", COLS_CHAO[1:])
    A.cap("p06_chao")
    faz_peca(COLS_MEIO[0], LINHA_MEIO, "Plataforma", "verde", COLS_MEIO[1:])
    A.cap("p07_plataforma")
    faz_peca(COLS_ALTA[0], LINHA_ALTA, "Alta", "verde", COLS_ALTA[1:])
    A.cap("p08_tres_plataformas")
    return True


@etapa
def lava():
    """A lava: barra vermelha no pe da tela, que vai SUBIR."""
    faz_peca(COLS_LAVA[0], LINHA_LAVA, "Lava", "vermelho", COLS_LAVA[1:])
    A.cap("p09_lava")
    return True


@etapa
def lava_fisica():
    """Separada da criacao de proposito: sao dois gestos bem diferentes, e
       assim da para repetir um sem refazer o outro."""
    editor.volta_ao_nivel()
    x, y = celula(COLS_LAVA[0], LINHA_LAVA)
    editor.objeto_ou_abre(x, y)
    # para a lava se mexer ela precisa de fisica — e SEM gravidade, senao ela
    # cai em vez de subir
    a, _ = nav.captura("/tmp/_c3_lf.png")
    q = nav.acha_texto("physics", arquivo=a)
    A.gesto("fisica_da_lava", "g06", q, lambda: clique(*q), espera=2.5)
    marca_caixa("movable", True)
    A.gesto("desligar_gravidade", "g07", (0, 0),
            lambda: marca_caixa("affected by gravity", False), espera=1.2)
    A.cap("p10_lava_sem_gravidade")
    fecha_painel_objeto(); time.sleep(1.5)
    return True


@etapa
def lava_sobe():
    """O coracao da aula: tres blocos que fazem a lava subir sozinha."""
    editor.volta_ao_nivel()
    x, y = celula(COLS_LAVA[0], LINHA_LAVA)
    editor.objeto_ou_abre(x, y)
    editor.abre_comportamentos()
    al = blocos.solta("Always", 1150, 600)
    A.cap("p11_always")
    nu = blocos.solta("Number", 1500, 900)
    A.cap("p12_number")
    ve = blocos.solta("Velocity", 2000, 600)
    A.cap("p13_velocity")
    blocos.liga_fixo(al, "out", nu, "get")
    blocos.liga_fixo(nu, "out", ve, "y")
    A.cap("p14_fios")
    # O NUMERO: digitado positivo e levado ao negativo pelo botao `−`, que e o
    # unico caminho que funciona (o campo engole o hifen digitado primeiro)
    ponto = blocos.valor_com_botao_menos(nu, SUBIDA, 1)
    A.reg("botao_menos", antes=A.cap("g08_a"), depois=A.cap("g08_b"),
          alvo=[int(ponto[0]), int(ponto[1])], botao="esq")
    A.cap("p15_menos_meio")
    print("   lava com velocidade", blocos.le_valor(nu), flush=True)
    time.sleep(2)
    editor.fecha_comportamentos(); time.sleep(2.5)
    fecha_painel_objeto(); time.sleep(1.5)
    return True


@etapa
def lava_mata():
    editor.volta_ao_nivel()
    x, y = celula(COLS_LAVA[0], LINHA_LAVA)
    editor.objeto_ou_abre(x, y)
    editor.abre_comportamentos()
    c = blocos.bloco_ou_solta("Collision", 1150, 1150)
    r = blocos.bloco_ou_solta("Restart Game", 1950, 1150, titulo="RestartGame")
    blocos.liga_fixo(c, "hit", r, "go")
    A.cap("p16_lava_reinicia")
    print("   lava ligada ao reinicio", flush=True)
    time.sleep(2)
    editor.fecha_comportamentos(); time.sleep(2.5)
    fecha_painel_objeto(); time.sleep(1.5)
    return True


@etapa
def estrela():
    editor.volta_ao_nivel()
    x, y = celula(COL_ESTRELA, LINHA_ALTA - 1)
    editor.objeto_ou_abre(x, y)
    nomeia("Estrela")
    abre_sprite(); pinta("amarelo")
    clique(*SPRITE_OK); time.sleep(2); nav.espera_parar(limite=15)
    A.cap("p17_estrela")
    editor.abre_comportamentos()
    c = blocos.bloco_ou_solta("Collision", 1150, 600)
    al = blocos.bloco_ou_solta("Alert", 1950, 600)
    blocos.liga_fixo(c, "hit", al, "show")
    A.cap("p18_fio_alerta")
    # as frases do aviso: SEM ACENTO de proposito — o caminho de teclado da
    # captura nao alcanca 'ê' nem 'ç', e a aula manda a crianca digitar
    # exatamente estas, para a tela dela bater com a foto
    blocos.escreve_textos(al, "GANHOU!", "Chegou na estrela antes da lava!",
                          "Fechar")
    A.cap("p19_aviso")
    time.sleep(2)
    editor.fecha_comportamentos(); time.sleep(2.5)
    fecha_painel_objeto(); time.sleep(1.5)
    A.cap("p20_fase_pronta")
    return True


@etapa
def prova():
    """Prova em jogo as TRES promessas da aula:
       1) a lava SOBE sozinha, sem ninguem apertar tecla;
       2) quando ela alcanca o boneco, o jogo RECOMECA;
       3) o boneco pula (senao nao ha como fugir).

       As duas primeiras saem da MESMA serie de leituras. A primeira versao
       mediu a altura da lava em dois instantes separados por 4 s e leu -15 px:
       no meio dos 4 s o jogo tinha recomecado e a lava voltado para o pe da
       tela. Dois instantes nao distinguem 'nao subiu' de 'subiu e recomecou'.
    """
    from PIL import Image
    import numpy as np

    def cor(mascara, minimo=600):
        """O MAIOR aglomerado da cor — nao a media de todos os pixels dela.

           Na pagina do jogo o Chrome pinta de azul as palavras selecionadas
           do menu, e a media do 'azul' caia no meio do caminho entre o boneco
           e o topo da pagina: eu lia o boneco a 300 px de onde ele estava."""
        a, _ = nav.captura("/tmp/_c3_j.png")
        im = np.asarray(Image.open(a).convert("RGB"), dtype=int)
        m = comum.maior_mancha(mascara(im))
        return m if m and m[2] >= minimo else None

    azul = lambda im: ((im[:, :, 2] > 100) & (im[:, :, 2] - im[:, :, 0] > 40) &
                       (im[:, :, 1] < 120))
    verm = lambda im: ((im[:, :, 0] > 150) & (im[:, :, 0] - im[:, :, 1] > 60) &
                       (im[:, :, 2] < 120))

    editor.volta_ao_editor(); time.sleep(2)
    editor.volta_ao_nivel()
    p = nav.acha_texto("play")
    if not p:
        raise RuntimeError("nao achei o botao Play (estou mesmo no editor?)")
    A.gesto("jogar", "g09", p, lambda: clique(*p), espera=6)
    editor.exige_jogo()
    clique(1470, 620); time.sleep(1.5)
    A.cap("p21_jogo")

    # 1) o boneco pula — medido LOGO no comeco, enquanto a lava ainda esta
    # longe. Medindo no fim, um reinicio no meio das leituras teleporta o
    # boneco e o guarda passa por motivo errado: li 611 px de "pulo" uma vez,
    # quase o dobro do que este pacote consegue.
    b0 = cor(azul)
    if not b0:
        raise RuntimeError("nao achei o boneco azul no jogo")
    alt = []
    rs.segura_tecla(126, 0.2)
    for _ in range(6):
        time.sleep(0.12)
        q = cor(azul)
        alt.append(q[1] if q else None)
    validos = [h for h in alt if h]
    pulo = b0[1] - min(validos) if validos else 0
    print(f"   pulo: subiu {pulo} px", flush=True)
    if pulo < 60:
        raise RuntimeError(f"o boneco subiu so {pulo} px: sem pulo nao ha fuga")

    serie = []
    for k in range(24):
        l = cor(verm)
        serie.append(l[1] if l else None)
        if k == 3:
            A.cap("p22_lava_subindo")
        time.sleep(0.6)
    alturas = [y for y in serie if y is not None]
    if len(alturas) < 10:
        raise RuntimeError(f"nao achei a lava vermelha no jogo ({len(alturas)} "
                           "leituras de 24)")

    # 2) a maior SUBIDA seguida: y diminuindo de uma leitura para a outra
    melhor = atual = 0
    for a1, a2 in zip(alturas, alturas[1:]):
        atual = atual + (a1 - a2) if a2 < a1 else 0
        melhor = max(melhor, atual)
    print(f"   a lava subiu {melhor} px de uma vez", flush=True)
    if melhor < 60:
        raise RuntimeError(f"a maior subida seguida da lava foi {melhor} px — "
                           "a aula promete uma lava que sobe sozinha")

    # 3) o salto de volta para o pe da tela: o jogo RECOMECOU
    quedas = [a2 - a1 for a1, a2 in zip(alturas, alturas[1:]) if a2 - a1 > 100]
    print(f"   o jogo recomecou {len(quedas)} vez(es) "
          f"(a lava voltou {max(quedas) if quedas else 0} px)", flush=True)
    if not quedas:
        raise RuntimeError("a lava subiu e o jogo nunca recomecou — a aula "
                           "promete que encostar nela volta ao comeco")
    A.cap("p23_recomecou")

    return True


@etapa
def prova_vitoria():
    """Prova que ENCOSTAR NA ESTRELA abre o aviso de vitoria.

       A aula promete isso no passo 19, e promessa de pagina sem execucao que
       a contradiga e justamente a que envelhece sem ninguem ver. Entao eu
       subo a fase de verdade — seta para a direita e seta para cima — e
       procuro a palavra GANHOU na tela."""
    editor.volta_ao_editor(); time.sleep(2)
    editor.volta_ao_nivel()
    p = nav.acha_texto("play")
    if not p:
        raise RuntimeError("nao achei o botao Play (estou mesmo no editor?)")
    clique(*p); time.sleep(6)
    editor.exige_jogo()
    clique(1470, 620); time.sleep(1.5)
    for tentativa in range(3):
        for _ in range(26):
            rs.segura_tecla(124, 0.30)       # direita
            rs.segura_tecla(126, 0.12)       # cima
            a, _ = nav.captura("/tmp/_c3_win.png")
            lido = " ".join(t for t, *_ in rs.ocr_forte(a, psm="6")).lower()
            if "ganhou" in lido:
                A.cap("p24_ganhou")
                print(f"   encostei na estrela e o aviso APARECEU "
                      f"(tentativa {tentativa+1})", flush=True)
                return True
        time.sleep(1.0)                      # a lava me pegou: comeca de novo
    raise RuntimeError("subi a fase tres vezes e o aviso de vitoria nao apareceu")


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
