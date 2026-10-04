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
from comum import (celula, clique, pinta, nomeia, nomeia_tipo, abre_sprite, marca_caixa,
                   arrasta_slider, fecha_painel_objeto, A, etapa, ETAPAS,
                   CELULA, GRADE_X, GRADE_Y, SPRITE_OK)

comum.pasta("aula3")
ETAPAS.clear()
D = "aula3"

# O DESENHO DA FASE — uma escada, nao um salto de fe.
#
# A primeira versao tinha plataformas de 3 casas separadas por 2 colunas de
# vao. Medido em jogo: o pulo chegava la, mas o pouso caia em qualquer lugar
# entre a beirada esquerda e o vazio depois da direita — a mesma sequencia de
# teclas as vezes pousava, as vezes caia. Isso nao e dificuldade, e sorte.
#
# Agora cada degrau sobe 2 fileiras e anda 1 coluna, e as plataformas sao
# largas. A estrela fica na PONTA DIREITA do degrau de cima, para a crianca
# ANDAR ate ela — encostar andando e o toque que esta provado desde a Aula 1;
# cair em cima de uma peca de 1 casa, nao.
LINHA_CHAO  = 8
LINHA_MEIO  = 6
LINHA_ALTA  = 4
LINHA_LAVA  = 11
COL_JOGADOR = 3
COLS_CHAO   = [1, 2, 3, 4, 5, 6]
COLS_MEIO   = [7, 8, 9, 10, 11]
COLS_ALTA   = [12, 13, 14, 15]
COL_ESTRELA = 15
COLS_LAVA   = list(range(0, 16))

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
    A.guarda_url()
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
    # o TIPO tambem: e o nome do tipo que aparece na lista do bloco Collision,
    # nao o nome do objeto. Sem isto a lava nao tem como saber em quem bater.
    nomeia_tipo("Jogador")
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
    # SEM 'is solid' a lava ATRAVESSA as plataformas. Medido em jogo: com ela
    # solida, as pecas que ficam debaixo de uma plataforma travam e a parede
    # se parte — a lava vira pedacos em alturas diferentes e a crianca fica
    # em cima do chao sem perigo nenhum. O editor nao acusa nada disso.
    A.gesto("lava_atravessa", "g10", (0, 0),
            lambda: marca_caixa("is solid", False), espera=1.2)
    # ...mas desmarcar 'is solid' tambem desliga a BATIDA: a lava subia por
    # cima do boneco e nada acontecia. No lugar do 'is solid' nasce uma
    # caixinha nova, `enable collisions` — e ela que devolve o toque sem
    # devolver o empurrao. Medido: com ela, o jogo recomeca; sem ela, nao.
    A.gesto("lava_sente_o_toque", "g11", (0, 0),
            lambda: marca_caixa("enable collisions", True), espera=1.2)
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
    al = blocos.bloco_ou_solta("Always", 1150, 600)
    A.cap("p11_always")
    nu = blocos.bloco_ou_solta("Number", 1500, 900)
    A.cap("p12_number")
    ve = blocos.bloco_ou_solta("Velocity", 2000, 600)
    A.cap("p13_velocity")
    blocos.liga_fixo(al, "out", nu, "get")
    blocos.liga_fixo(nu, "out", ve, "y")
    A.cap("p14_fios")
    # O NUMERO: digitado positivo e levado ao negativo pelo botao `−`, que e o
    # unico caminho que funciona (o campo engole o hifen digitado primeiro)
    # Pelo `A.gesto`, nao pelo `A.reg` na mao: eu fotografava os DOIS quadros
    # depois do gesto ja feito, e o clipe saia uma figura parada — antes
    # identico a depois. O guarda dos alvos agora reprova isso.
    A.gesto("botao_menos", "g08", (0, 0),
            lambda: blocos.valor_com_botao_menos(nu, SUBIDA, 1), espera=1.6)
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
    # Longe da beirada direita de proposito: soltar um bloco perto dela faz a
    # mesa ROLAR sozinha, e os blocos que ja estavam la saem de vista — eu
    # media pinos de um bloco que nao estava mais onde eu pensava.
    c = blocos.bloco_ou_solta("Collision", 1120, 1220)
    r = blocos.bloco_ou_solta("Restart Game", 1700, 1220, titulo="RestartGame")
    blocos.liga_fixo(c, "hit", r, "go")
    # COM QUEM a batida conta. Em 'Any Type' o bloco dispara com qualquer
    # coisa — e uma lava que sobe bate primeiro no CHAO: o jogo reiniciava
    # sozinho a cada poucos segundos e a fase ficava impossivel, sem nada no
    # editor acusando.
    blocos.escolhe_tipo_da_colisao(c, "Jogador")
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
    c = blocos.bloco_ou_solta("Collision", 1120, 620)
    d = blocos.bloco_ou_solta("Destroyer", 1700, 620)
    blocos.liga_fixo(c, "hit", d, "in")
    # A estrela tambem precisa dizer COM QUEM a batida conta. Em 'Any Type' a
    # LAVA, ao subir, atravessa a estrela e a destroi — o jogo se ganha
    # sozinho, antes de a crianca chegar la, e o que ela ve e uma estrela que
    # some do nada. Foi isso que fez a minha sonda "subir a fase seis vezes
    # sem nunca pegar a estrela": ela ja tinha sido comida pela lava.
    blocos.escolhe_tipo_da_colisao(c, "Jogador")
    A.cap("p18_fio_estrela")
    # Aqui havia um `Alert` com as frases da vitoria. Tirei depois de ver em
    # jogo: o Alert ESCURECE a tela e nao desenha a caixa dentro do canvas da
    # pagina do jogo — a crianca encostaria na estrela e veria a tela apagar,
    # sem uma palavra. A estrela que SOME e a mesma peca da Aula 1, ja provada,
    # e diz 'peguei' sem ambiguidade.
    A.cap("p19_estrela_pronta")
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
    print("   serie da lava:", serie, flush=True)
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
    """Prova que ENCOSTAR NA ESTRELA faz ela sumir.

       A aula promete isso no passo 19, e promessa de pagina sem execucao que
       a contradiga e a que envelhece sem ninguem ver. Entao subo a fase de
       verdade.

       Duas coisas que a primeira versao desta sonda errou:
       - ela tocava a seta de ANDAR e depois a de PULAR. Separadas, o boneco
         pula parado e cai no mesmo lugar: 'subi a fase tres vezes' sem ter
         saido do chao. `rs.corre_e_pula` segura uma e toca a outra.
       - e ela conferia sem olhar se o boneco ainda estava vivo. Depois de
         cair, as teclas vao para o vazio e a sonda conclui que a fase nao tem
         saida."""
    from PIL import Image
    import numpy as np

    azul = lambda im: ((im[:, :, 2] > 100) & (im[:, :, 2] - im[:, :, 0] > 40) &
                       (im[:, :, 1] < 120))
    amar = lambda im: ((im[:, :, 0] > 190) & (im[:, :, 1] > 130) &
                       (im[:, :, 1] < 210) & (im[:, :, 2] < 120))

    def mancha(mascara, minimo=600):
        a, _ = nav.captura("/tmp/_c3_v.png")
        im = np.asarray(Image.open(a).convert("RGB"), dtype=int)
        g = comum.maior_mancha(mascara(im))
        return g if g and g[2] > minimo else None

    def espera_comeco(limite=40):
        for _ in range(limite):
            q = mancha(azul)
            if q and abs(q[0] - inicio[0]) < 40:
                return True
            time.sleep(0.8)
        return False

    editor.volta_ao_editor(); time.sleep(2)
    editor.volta_ao_nivel()
    p = nav.acha_texto("play")
    if not p:
        raise RuntimeError("nao achei o botao Play (estou mesmo no editor?)")
    clique(*p); time.sleep(6)
    editor.exige_jogo()
    clique(1470, 620); time.sleep(1.2)
    if not mancha(amar):
        raise RuntimeError("nao achei a estrela amarela no jogo")
    # ONDE o boneco nasce, medido na hora. Numero fixo aqui envelhece: bastou
    # mudar a coluna onde a fase comeca para a sonda ficar esperando um boneco
    # que estava na tela, parado, 60 px ao lado.
    inicio = mancha(azul)
    if not inicio:
        raise RuntimeError("nao achei o boneco azul no comeco do jogo")
    print(f"   o boneco nasce em x={inicio[0]}", flush=True)

    for tentativa in range(6):
        if not espera_comeco():
            raise RuntimeError("o boneco nao voltou ao comeco: o jogo travou?")
        rs.corre_e_pula(antes=0.25)                    # chao -> plataforma do meio
        rs.corre_e_pula(antes=0.02, segurando=0.12)    # meio -> plataforma alta
        for k in range(10):
            if not mancha(amar):
                A.cap("p24_pegou_a_estrela")
                print(f"   encostei na estrela e ela SUMIU "
                      f"(tentativa {tentativa + 1}, passo {k})", flush=True)
                return True
            q = mancha(azul)
            if not q or q[1] > 520:        # caiu da plataforma alta
                break
            rs.segura_tecla(123, 0.08)     # seta esquerda, ate tocar a estrela
    raise RuntimeError("subi ate a plataforma alta seis vezes e a estrela nao sumiu")


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
