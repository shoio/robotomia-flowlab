#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aula 8 — Contra o relogio. Constroi o jogo no Flowlab e fotografa cada gesto.

   O jogo: um percurso com dois buracos, um cronometro correndo na tela e um
   RECORDE que sobrevive ao recomeco.

   O que e NOVO: a `Global Variable` — um numero com NOME, que dois objetos
   leem, e que nao zera quando o jogo recomeca. E o `Filter` comparando com
   OUTRO NUMERO DO JOGO, por um fio no `set`, em vez do numero do painel.

   MEDIDO ANTES (PADRAO.md §2ac), nos prototipos 3155765/3155819/3155846:
   - o painel da global tem `Name`, `Type: Number` e **`Default Value`** — e e
     o Default que dispensa semear o recorde com blocos;
   - depois de escolhida a variavel, o TITULO do bloco vira o nome dela;
   - a global **sobrevive ao `Restart Game`**: com 99 de fabrica, ela foi a 7,
     o jogo recomecou e ela continuou 7 (nunca voltou a 99);
   - o `Filter` tem seis comparacoes, entre elas `less than`;
   - ⭐ **o fio no `set` manda** — provado com um numero 50 no fio contra o 0
     do painel: com o fio, o bicho viveu os 26 s; sem ele, morria no 1o seg;
   - ⚠️ mas o fio so manda **depois de ter entregue alguma coisa**: se o
     primeiro `in` chega antes do primeiro `set`, quem decide e o painel;
   - o `Timer` nasce com atraso **10 decimos = 1 segundo**: nao precisa mexer;
   - o `Label` nasce salmao e desenha no canto de cima do nivel. Dois Labels
     nascem UM EM CIMA DO OUTRO — o segundo desce pelo pino `y`. E em ceu
     ESCURO ninguem le o salmao: o ceu desta aula e claro de proposito.

       BANCADA=1 python3 fonte/roda_aula.py 8
"""
import os, shutil, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rs, nav, editor, blocos, comum

comum.pasta("aula8")
import aula_comum as AC
from aula_comum import (celula, clique, A, etapa, ETAPAS, cria_objeto, clona,
                        clona_casas, da_fisica, confere_fisica, abre_mesa,
                        fecha_mesa, rastreio, cor)
from comum import fecha_painel_objeto
ETAPAS.clear()

D = "aula8"
CEU = "FFE5B4"          # areia clara: o Label nasce salmao e so se le em ceu claro
AC.SPRITES = {
    "Corredor": ("Flowlab Sprites", "Characters", 0, 0),
    "Chao":     ("Flowlab Sprites", "Blocks", 0, 0),
    "Bandeira": ("Flowlab Sprites", "Blocks", 4, 0),     # o tijolo rosa, que marca a chegada
}

LINHA_CHAO = 10
LINHA_FUNDO = 11
CEL_CORREDOR = (1, 9)
CEL_BANDEIRA = (15, 9)
# ⛔ MEDIDO DUAS VEZES: bandeira de uma casa so NAO para ninguem. O corredor
# pula por cima dela e cai fora do nivel pela direita — some do jogo, e o
# recorde nunca e tocado. Com tres andares ela vira parede: passar por ela
# exige ENCOSTAR, que e o que a aula precisa.
CASAS_DA_BANDEIRA = [(15, 8), (15, 7)]
BURACOS = (6, 10)
COLUNAS_DO_CHAO = [c for c in range(1, 16) if c not in BURACOS]
# ⛔ MEDIDO na primeira captura: buraco SEM FUNDO nao custa tempo, custa o
# jogo. O corredor caiu no primeiro, saiu do nivel e sumiu — e a foto do passo
# 13 (que promete "você corre, pula os buracos e chega") saiu com o percurso
# vazio. Com uma casa de chao uma fileira abaixo, cair vira o que um percurso
# cronometrado quer: um prejuizo de SEGUNDOS, de onde se sai pulando.
CASAS_DO_FUNDO = [(c, LINHA_FUNDO) for c in BURACOS]
RECORDE_DE_FABRICA = 99
DESCE_O_RECORDE = 80

FILA_A = (0.12, 0.06, 1.0, 0.50)
FILA_B = (0.12, 0.50, 1.0, 0.96)
# ⛔ A TELA TEM 1604 px: `Y_C` dava 1620 e o bloco caia FORA dela —
# o erro que sobra e «soltei e a mesa nao mudou ali», que manda procurar
# o defeito no arrasto. Tres fileiras, todas dentro da tela.
Y_A, Y_B, Y_C = 500, 1020, 1480


# AS DUAS FAIXAS onde os numeros aparecem, medidas na tela do jogo:
#  - o Label parado desenha no CANTO DE CIMA do nivel (y por volta de 250);
#  - o Label com `attach to object` desenha em cima do objeto — o corredor
#    anda no chao, por volta de y 800.
# Faixa larga demais estraga a leitura: com (0.18..0.70) o tesseract nao leu
# NENHUM numero numa tela em que o 43 estava aceso e legivel na foto.
REGIAO_CANTO = (0.20, 0.04, 0.85, 0.30)
REGIAO_PISTA = (0.20, 0.30, 0.90, 0.72)


def _numero(regiao):
    """O primeiro numero lido nesta faixa da tela do jogo."""
    a, _ = nav.captura("/tmp/_c8_num.png")
    for t, x, y, w, h in rs.ocr_forte(a, regiao=regiao, psm="6"):
        d = "".join(c for c in t if c.isdigit())
        if d:
            return int(d)
    return None


def _um_numero():
    """O relogio enquanto ele ainda e o UNICO Label, parado no canto."""
    return _numero(REGIAO_CANTO)


def _recorde_na_tela():
    return _numero(REGIAO_CANTO)


def _tempo_na_tela():
    return _numero(REGIAO_PISTA)


def _global_ou_solta(nome, inicial, x, y):
    """O bloco da global `nome`, achando-o pelo TITULO (que e o nome dela) ou
       soltando um novo e apontando para ela.

       Existe porque repetir uma etapa e rotina: `bloco_ou_solta('Global
       Variable')` nao acha o que ja existe (ele se chama `Recorde` agora) e
       solta um SEGUNDO bloco, que fica na mesa sem fio nenhum — e aparece na
       foto da aula."""
    try:
        return blocos.acha_bloco(nome, tipo="Global Variable")
    except RuntimeError:
        pass
    blocos.bloco_ou_solta("Global Variable", x, y)
    g = blocos.acha_bloco("Global Variable", tipo="Global Variable")
    blocos.usa_global(g, nome, inicial)
    return blocos.acha_bloco(nome, tipo="Global Variable")


def _joga_do_zero():
    """Abre o jogo PELO ENDERECO e aperta Play: partida nova de verdade.

       ⛔ MEDIDO: apertar Play logo depois de outra partida CONTINUA a de
       antes. A variavel global `Tempo` guarda o tempo da partida anterior, e
       a etapa que promete «o relogio comeca em 0» fotografou **43**. Abrindo
       o endereco de novo, a mesma mesa marca 0, 1, 2, 3… (medido: a serie
       inteira, de segundo em segundo)."""
    url = open(os.path.join(D, "jogo.txt")).read().strip()
    nav.vai(url, espera=12); time.sleep(3); nav.fecha_dialogo()
    # ⚠️ O ENDERECO DO JOGO JA COMECA A JOGAR. Sem passar pelo editor, o
    # `Play` que eu achava era o contador da propria pagina do jogo, o clique
    # nao fazia nada, e eu media a partida que tinha comecado no CARREGAMENTO
    # — o relogio aparecia em 34 na primeira leitura.
    editor.volta_ao_editor(); time.sleep(2)
    editor.volta_ao_nivel(); time.sleep(1.5)
    p = nav.acha_texto("play")
    if not p:
        raise RuntimeError("nao achei o botao Play depois de reabrir o jogo")
    # ⚠️ NADA DE `espera_parar(20)` AQUI: o relogio da aula corre desde o
    # primeiro quadro, e cada segundo gasto antes da primeira leitura aparece
    # na foto. Com 5 s de sono mais 20 de espera mais dois OCR, a «primeira»
    # leitura saia em 34.
    clique(*p); time.sleep(2.5)
    editor.exige_jogo()
    clique(1470, 620); time.sleep(0.8)
    return True


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
            shutil.copy(f"aula7/gifs/{nome}", f"{D}/gifs/{nome}")
    A.gesto("abrir_niveis", "g08a", (0, 0), lambda: editor.abre_niveis(), espera=1.8)
    A.gesto("pintar_o_ceu", "g08", (0, 0),
            lambda: editor.cor_do_ceu(CEU, abrir=False), espera=2.0)
    editor.volta_ao_nivel()
    A.cap("p02_ceu")
    return True


@etapa
def corredor():
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    x, y = celula(*CEL_CORREDOR)
    A.gesto("criar_objeto", "g01", (x, y), lambda: clique(x, y), espera=1.5)
    a, _ = nav.captura("/tmp/_c8_rad.png")
    p = nav.acha_texto("create", arquivo=a)
    A.gesto("escolher_create", "g02", p, lambda: clique(*p), espera=3)
    editor.espera_tela("behaviors", limite=20)
    comum.nomeia("Corredor"); comum.nomeia_tipo("Corredor")
    A.cap("p03_nome")
    comum.abre_sprite()
    pacote, sub, lin, col = AC.SPRITES["Corredor"]
    comum.abre_grade_sprite(pacote, sub)
    A.gesto("escolher_sprite", "g13", (0, 0),
            lambda: AC.poe_sprite("Corredor", so_clique=True), espera=2.0)
    clique(*comum.SPRITE_OK); time.sleep(2); nav.espera_parar(limite=15)
    A.cap("p04_corredor")
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
    """O mesmo pacote da Aula 7: `Run & Jump`, um bloco so."""
    abre_mesa(*CEL_CORREDOR)
    blocos.abre_categoria("Behavior Bundles")
    blocos.bloco_ou_solta("Run & Jump", 1500, 760)
    A.cap("p06_correr")
    time.sleep(2.5)
    fecha_mesa()
    return True


@etapa
def chao():
    """O chao COM BURACOS: e o buraco que faz o percurso valer tempo."""
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    cria_objeto(0, LINHA_CHAO, "Chao", tipo="Chao")
    casas = [(c, LINHA_CHAO) for c in COLUNAS_DO_CHAO] + CASAS_DO_FUNDO
    A.gesto("clonar_o_chao", "g05", (0, 0),
            lambda: clona_casas(0, LINHA_CHAO, "Chao", casas), espera=2.0)
    A.cap("p07_chao")
    print(f"   chao com buracos nas colunas {BURACOS}, com fundo em "
          f"{[c for c, _ in CASAS_DO_FUNDO]}", flush=True)
    return True


@etapa
def bandeira():
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    cria_objeto(*CEL_BANDEIRA, "Bandeira", tipo="Bandeira")
    A.gesto("levantar_a_bandeira", "g16", (0, 0),
            lambda: clona_casas(*CEL_BANDEIRA, "Bandeira", CASAS_DA_BANDEIRA),
            espera=2.0)
    A.cap("p08_bandeira")
    return True


def _onde_esta_o_corredor(cor_c, tol):
    """O x medio do corredor na tela, ou None se ele nao esta la."""
    import numpy as np
    from PIL import Image
    a, _ = nav.captura("/tmp/_c8_cor.png")
    im = np.asarray(Image.open(a).convert("RGB"), dtype=int)
    _ys, xs = np.nonzero(comum.mascara_cor(im, cor_c, tol))
    return int(xs.mean()) if len(xs) else None


@etapa
def corrida():
    """Jogar o percurso ANTES de ter relogio: e a aula que promete isso.

       A foto deste passo so vale se o CORREDOR estiver nela — foi justamente
       essa a falha da primeira captura, e nenhum guarda de forma a pegaria."""
    cor_c, tol = rastreio("Corredor", "Chao", "Bandeira")
    editor.volta_ao_nivel(); time.sleep(1.5)
    p = nav.acha_texto("play")
    A.gesto("jogar", "g07", p, lambda: clique(*p), espera=6)
    editor.exige_jogo()
    clique(1470, 620); time.sleep(1.0)
    partida = _onde_esta_o_corredor(cor_c, tol)
    # ⛔ MEDIDO: com oito pulos ele passa da bandeira, pula POR CIMA dela e sai
    # do nivel pela direita — e ai some. Nesta etapa a bandeira ainda nao faz
    # nada (o recomeco so nasce no passo 20), entao a corrida para ANTES dela:
    # o que esta foto promete e «você corre e pula os buracos», nao a chegada.
    chegada = partida
    for _ in range(10):
        rs.corre_e_pula(direcao=124, antes=0.05, segurando=0.55)
        agora = _onde_esta_o_corredor(cor_c, tol)
        if agora is None:
            break
        chegada = agora
        if partida is not None and chegada - partida > 480:
            break
    A.cap("p09_corrida")
    print(f"   corredor: x {partida} -> {chegada}", flush=True)
    if chegada is None:
        raise RuntimeError("o corredor sumiu da tela durante a corrida — "
                           "buraco sem fundo tira o boneco do nivel")
    if partida is None or chegada <= partida + 40:
        raise RuntimeError(f"o corredor nao andou ({partida} -> {chegada})")
    editor.volta_ao_editor(); time.sleep(2)
    return True


@etapa
def tempo():
    """O CRONOMETRO: `Timer` -> `Tempo.+` -> `Label.text`.

       `Tempo` e uma variavel GLOBAL, e nao um `Number`, porque quem vai ler o
       tempo no fim e OUTRO objeto — a bandeira."""
    abre_mesa(*CEL_CORREDOR)
    blocos.abre_categoria("Logic & Math")
    try:
        blocos.acha_bloco("Tempo", tipo="Global Variable")
    except RuntimeError:
        blocos.bloco_ou_solta("Global Variable", 1500, Y_A, regiao=FILA_A)
        g = blocos.acha_bloco("Global Variable", tipo="Global Variable")
        A.gesto("criar_variavel_global", "g14", (0, 0),
                lambda: blocos.usa_global(g, "Tempo", 0), espera=1.5)
    blocos.abre_categoria("Triggers")
    blocos.bloco_ou_solta("Timer", 800, Y_A, regiao=FILA_A)
    t = blocos.acha_bloco("Timer", regiao=FILA_A)
    blocos.abre_ajustes(t); time.sleep(1.3)
    blocos.marca_do_bloco("repeat forever", True)
    blocos.fecha_ajustes(); time.sleep(1.0)
    blocos.abre_categoria("GUI")
    blocos.bloco_ou_solta("Label", 2400, Y_A, regiao=FILA_A)

    t = blocos.acha_bloco("Timer", regiao=FILA_A)
    tp = blocos.acha_bloco("Tempo", regiao=FILA_A, tipo="Global Variable")
    lb = blocos.acha_bloco("Label", regiao=FILA_A)
    blocos.liga_fixo(t, "out", tp, "mais")
    tp = blocos.acha_bloco("Tempo", regiao=FILA_A, tipo="Global Variable")
    lb = blocos.acha_bloco("Label", regiao=FILA_A)
    blocos.liga_fixo(tp, "out", lb, "text")
    print("   relogio: Timer -> Tempo.+ -> Label.text", flush=True)
    A.cap("p10_tempo")
    time.sleep(2)
    fecha_mesa()
    return True


@etapa
def zera():
    """`Once` -> `Number(0)` -> `Tempo.set`, no MESMO bloco da global.

       Variavel global NAO ESQUECE — e e por isso que ela precisa ser zerada
       no comeco da partida. O bloco que ja esta na mesa serve: o `+` recebe o
       relogio e o `set` recebe o zero."""
    abre_mesa(*CEL_CORREDOR)
    blocos.abre_categoria("Triggers")
    blocos.bloco_ou_solta("Once", 800, Y_B)
    blocos.abre_categoria("Logic & Math")
    blocos.bloco_ou_solta("Number", 1500, Y_B)
    on = blocos.acha_bloco("Once")
    nu = blocos.acha_bloco("Number")
    blocos.liga_fixo(on, "out", nu, "get")
    nu = blocos.acha_bloco("Number")
    tp = blocos.acha_bloco("Tempo", regiao=FILA_A, tipo="Global Variable")
    blocos.liga_fixo(nu, "out", tp, "set")
    print("   zerar: Once -> Number(0) -> Tempo.set", flush=True)
    A.cap("p11_zera")
    time.sleep(2)
    fecha_mesa()
    return True


@etapa
def relogio():
    """PROVA do meio: o numero na tela sobe sozinho, e comeca em 0."""
    _joga_do_zero()
    serie = []
    for _ in range(8):
        n = _um_numero()
        if n is not None:
            serie.append(n)
            if len(serie) == 1:
                # ⚠️ A FOTO SAI AGORA, na primeira leitura. Tirada no fim do
                # laco, ela mostrava 43: cada leitura de OCR custa segundos, e
                # o relogio corre o tempo todo. O passo promete um numero que
                # SOBE, e e isso que a foto tem de mostrar — nao o cansaco da
                # minha propria medicao.
                A.cap("p12_relogio")
        time.sleep(0.4)
    print(f"   relogio lido na tela: {serie}", flush=True)
    if len(serie) < 3:
        raise RuntimeError(f"nao consegui ler o relogio na tela ({serie})")
    if max(serie) <= min(serie):
        raise RuntimeError(f"o relogio nao andou: {serie}")
    # O `Once` zera o Tempo no comeco da partida — medido numa sonda que leu
    # 2,3,4,5,6,7,8,9… de segundo em segundo. Aqui o piso e frouxo de
    # proposito: a pagina do jogo ja comeca a rodar enquanto carrega, e a
    # primeira leitura chega uns segundos depois.
    if serie[0] > 15:
        raise RuntimeError(f"o relogio ja estava em {serie[0]} na primeira "
                           f"leitura ({serie}) — esta partida nao e nova")
    print(f"   PROVADO: o relogio vai de {min(serie)} a {max(serie)} sozinho",
          flush=True)
    editor.volta_ao_editor(); time.sleep(2)
    return True


@etapa
def recorde():
    """Na BANDEIRA: a global `Recorde`, que nasce em 99, na tela."""
    abre_mesa(*CEL_BANDEIRA)
    blocos.abre_categoria("Logic & Math")
    _global_ou_solta("Recorde", RECORDE_DE_FABRICA, 1500, Y_A)
    blocos.abre_categoria("Triggers")
    blocos.bloco_ou_solta("Timer", 800, Y_A, regiao=FILA_A)
    t = blocos.acha_bloco("Timer", regiao=FILA_A)
    blocos.abre_ajustes(t); time.sleep(1.3)
    blocos.marca_do_bloco("repeat forever", True)
    blocos.fecha_ajustes(); time.sleep(1.0)
    blocos.abre_categoria("GUI")
    blocos.bloco_ou_solta("Label", 2400, Y_A, regiao=FILA_A)
    t = blocos.acha_bloco("Timer", regiao=FILA_A)
    rc = blocos.acha_bloco("Recorde", tipo="Global Variable")
    blocos.liga_fixo(t, "out", rc, "get")
    rc = blocos.acha_bloco("Recorde", tipo="Global Variable")
    lb = blocos.acha_bloco("Label", regiao=FILA_A)
    blocos.liga_fixo(rc, "out", lb, "text")
    print(f"   recorde: Timer -> Recorde({RECORDE_DE_FABRICA}).get -> Label.text",
          flush=True)
    A.cap("p13_recorde")
    time.sleep(2)
    fecha_mesa()
    return True


@etapa
def na_cabeca():
    """O cronometro vai para CIMA DO CORREDOR, com uma caixinha so.

       ⛔ MEDIDO, e e o contrario do que eu tinha desenhado: os pinos `x` e `y`
       do `Label` NAO movem o texto. Liguei `Number(80)` no `y` pelo `Once` e
       depois pelo `Timer`, e nas duas vezes os dois numeros continuaram
       empilhados no mesmo canto do nivel. Quem move e a caixinha
       `attach to object` do painel: marcada, o texto passa a ser desenhado em
       cima do OBJETO. Entao o tempo vai com o corredor e o recorde fica no
       canto — e nenhum bloco a mais entra na mesa."""
    abre_mesa(*CEL_CORREDOR)
    lb = blocos.acha_bloco("Label")
    blocos.abre_ajustes(lb); time.sleep(1.6)
    A.gesto("grudar_no_corredor", "g15", (0, 0),
            lambda: blocos.marca_do_bloco("attach to object", True), espera=1.4)
    blocos.fecha_ajustes(); time.sleep(1.2)
    A.cap("p14_na_cabeca")
    time.sleep(2)
    fecha_mesa()
    return True


@etapa
def compara():
    """O CORACAO da aula: `Filter` comparando com um fio no `set`.

       Medido no prototipo 3155846: o numero que vem pelo fio manda no numero
       do painel — mas so depois de ter chegado uma vez. Aqui quem alimenta o
       `set` e o `Timer` da bandeira, de segundo em segundo, desde o comeco da
       partida; o `in` so chega quando o corredor encosta."""
    abre_mesa(*CEL_BANDEIRA)
    blocos.abre_categoria("Triggers")
    blocos.bloco_ou_solta("Collision", 800, Y_C)
    co = blocos.acha_bloco("Collision")
    blocos.escolhe_tipo_da_colisao(co, "Corredor")
    blocos.abre_categoria("Logic & Math")
    _global_ou_solta("Tempo", 0, 1500, Y_C)
    blocos.bloco_ou_solta("Filter", 2250, Y_C)
    fi = blocos.acha_bloco("Filter")
    # O CLIPE E COM O PAINEL ABERTO nos dois quadros: fechado, a diferenca
    # entre antes e depois e um `>` virando `<` (93 px), e o `confere_alvos`
    # chama isso de «clipe sem gesto» — com razao, porque nao da para ver
    # gesto nenhum ali.
    blocos.abre_ajustes(fi); time.sleep(1.5)
    # volta para o padrao de fabrica antes de gravar: numa etapa repetida a
    # comparacao ja estaria em `less than` e o gesto nao mudaria nada.
    blocos.escolhe_condicao_no_painel(fi, "greater than")
    A.gesto("condicao_menor", "g11", (0, 0),
            lambda: blocos.escolhe_condicao_no_painel(fi, "less than"),
            espera=1.4)
    blocos.fecha_ajustes(); time.sleep(1.2)
    blocos.confere_condicao(fi, "less than")

    co = blocos.acha_bloco("Collision")
    tp = blocos.acha_bloco("Tempo", tipo="Global Variable")
    blocos.liga_fixo(co, "hit", tp, "get")
    tp = blocos.acha_bloco("Tempo", tipo="Global Variable")
    fi = blocos.acha_bloco("Filter")
    blocos.liga_fixo(tp, "out", fi, "in")
    rc = blocos.acha_bloco("Recorde", tipo="Global Variable")
    fi = blocos.acha_bloco("Filter")
    blocos.liga_fixo(rc, "out", fi, "set")
    fi = blocos.acha_bloco("Filter")
    rc = blocos.acha_bloco("Recorde", tipo="Global Variable")
    blocos.liga_fixo(fi, "pass", rc, "set")
    # (a leitura de volta da comparacao e do proprio `poe_condicao`, ancorada
    #  na cara do bloco; repetir aqui na tela inteira so acrescentava um `<`
    #  que o OCR nem sempre devolve — e reprovava uma condicao que esta certa)
    print("   comparacao: Tempo -> Filter(input <) <- Recorde ; pass -> Recorde.set",
          flush=True)
    A.cap("p15_compara")
    time.sleep(2)
    fecha_mesa()
    return True


@etapa
def volta():
    """Encostou na bandeira: espera UM SEGUNDO e recomeca.

       O segundo de espera nao e enfeite: e o tempo de a bandeira guardar o
       recorde antes de tudo recomecar. E o fio no `start` do `Timer` e o que
       tira dele o `auto start` — sem isso ele dispararia sozinho no comeco."""
    abre_mesa(*CEL_CORREDOR)
    blocos.abre_categoria("Triggers")
    blocos.bloco_ou_solta("Collision", 800, Y_C)
    co = blocos.acha_bloco("Collision")
    blocos.escolhe_tipo_da_colisao(co, "Bandeira")
    # ⛔ `bloco_ou_solta` NAO SERVE AQUI: ja existe um `Timer` nesta mesa (o do
    # relogio), ele reaproveita o primeiro que acha e o segundo nunca nasce —
    # e o erro so aparece tres linhas depois, como «nao achei o Timer da
    # volta». Quando a mesa ja tem um bloco do mesmo nome, o certo e SOLTAR.
    blocos.solta("Timer", 1500, Y_C)
    blocos.abre_categoria("Game Flow")
    blocos.bloco_ou_solta("Restart Game", 2250, Y_C, titulo="RestartGame")

    co = blocos.acha_bloco("Collision")
    tms = blocos.acha_todos("Timer")
    if len(tms) < 2:
        raise RuntimeError(f"a mesa do corredor tem {len(tms)} Timer(s): o do "
                           "relogio e o da volta t~em de estar os dois la")
    # O DA VOLTA e o que esta na altura do `Collision` que acabei de soltar —
    # nao «o de baixo», que depende de a mesa nao ter rolado.
    tv = min(tms, key=lambda b: abs(b.y - co.y))
    blocos.liga_fixo(co, "hit", tv, "start")
    tv = min(blocos.acha_todos("Timer"), key=lambda b: abs(b.y - co.y))
    rg = blocos.acha_bloco("RestartGame")
    blocos.liga_fixo(tv, "out", rg, "go")
    b, _ = nav.captura("/tmp/_c8_tv.png")
    perto = (max(0.0, (tv.x - 60) / 2940), max(0.0, (tv.y - 40) / 1604),
             min(1.0, (tv.x + 330) / 2940), min(1.0, (tv.y + 200) / 1604))
    if rs.tem_texto("auto start", arquivo=b, regiao=perto):
        raise RuntimeError("o Timer da volta continua em `auto start` — o fio "
                           "no `start` nao pegou, e ele vai disparar sozinho")
    print("   volta: Collision(Bandeira) -> Timer.start -> RestartGame.go",
          flush=True)
    A.cap("p16_volta")
    time.sleep(2)
    fecha_mesa()
    return True


@etapa
def prova():
    """As duas promessas, medidas em jogo:

       1. chegar na bandeira TROCA o recorde (99 -> o tempo da corrida);
       2. chegar mais devagar na segunda vez NAO troca — e o lado `fail`.

       ⚠️ QUEM DIZ QUE EU CHEGUEI nao pode ser o recorde: na segunda corrida
       ele ja esta abaixo de 99 desde o primeiro instante, e o laco voltaria
       na primeira volta sem o corredor ter andado. Quem avisa a chegada e o
       CORREDOR VOLTANDO PARA A LARGADA — o recomeco, visto pela posicao dele,
       que e medida por cor e nao tem nada a ver com o numero sob teste.
    """
    import numpy as np
    from PIL import Image
    cor_c, tol = rastreio("Corredor", "Chao", "Bandeira")

    def onde():
        a, _ = nav.captura("/tmp/_c8_pos.png")
        im = np.asarray(Image.open(a).convert("RGB"), dtype=int)
        _ys, xs = np.nonzero(comum.mascara_cor(im, cor_c, tol))
        return int(xs.mean()) if len(xs) else None

    _joga_do_zero()

    def corre_ate_voltar(limite=30, parada=0.0):
        """Corre para a direita ate o corredor VOLTAR para a largada."""
        anterior = onde()
        partida = anterior
        for _ in range(limite):
            rs.corre_e_pula(direcao=124, antes=0.05, segurando=0.55)
            if parada:
                time.sleep(parada)
            agora = onde()
            if (agora is not None and anterior is not None
                    and agora < anterior - 250):
                return True
            if agora is not None:
                anterior = agora
        print(f"   (o corredor ficou em {anterior}, partiu de {partida})",
              flush=True)
        return False

    chegou = corre_ate_voltar()
    time.sleep(2)
    primeiro = _recorde_na_tela()
    A.cap("p17_jogo")
    print(f"   primeira corrida: chegou={chegou} recorde={primeiro}", flush=True)
    if not chegou:
        raise RuntimeError("nao cheguei na bandeira na primeira corrida — o "
                           "corredor nunca voltou para a largada")
    if primeiro is None or primeiro >= RECORDE_DE_FABRICA:
        raise RuntimeError(f"cheguei na bandeira e o recorde continua {primeiro}")

    # SEGUNDA corrida, de proposito mais lenta: o recorde tem de FICAR
    time.sleep(primeiro + 6)
    chegou2 = corre_ate_voltar(parada=0.35)
    time.sleep(2)
    segundo = _recorde_na_tela()
    print(f"   segunda corrida (lenta): chegou={chegou2} recorde={segundo}",
          flush=True)
    if not chegou2:
        raise RuntimeError("nao cheguei na bandeira na segunda corrida")
    if segundo != primeiro:
        raise RuntimeError(f"a corrida lenta trocou o recorde de {primeiro} "
                           f"para {segundo} — o funil nao esta comparando")
    print(f"   PROVADO: o recorde virou {primeiro} na primeira corrida e NAO "
          f"mudou na corrida lenta", flush=True)
    editor.volta_ao_editor(); time.sleep(2)
    return True


@etapa
def fim():
    editor.volta_ao_nivel(); time.sleep(1.5)
    A.cap("p18_fim")
    return True


def main():
    AC.main(sys.modules[__name__])


if __name__ == "__main__":
    main()
