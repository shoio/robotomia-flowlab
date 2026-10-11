#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aula 4 — Nave e tiro. Constroi o jogo no Flowlab e fotografa cada gesto.

   Primeira aula escrita sobre o `aula_comum.py`: tudo o que ela faz igual as
   anteriores vem de la, e ja com leitura de volta. O que sobra aqui e so o
   que e DESTA aula.

   As tres pecas novas foram medidas antes de a aula ser escrita (§2k e §2l do
   PADRAO.md), num jogo de prototipo:
     - `Keyboard` dispara pela bancada, e nasce SEM tecla;
     - `Timer` dispara sozinho (`auto start`), em decimos de segundo;
     - `Emit` nasce no proprio objeto, ja sai andando e EXPIRA sozinho — por
       isso nao ha "limpar o que sai da tela" nesta aula. Angulo: 0 e direita,
       90 e BAIXO, 270 e cima. `Expire After` e em trinta avos de segundo.

       BANCADA=1 python3 fonte/roda_aula.py 4
"""
import os, shutil, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rs, nav, editor, blocos, comum

comum.pasta("aula4")
import aula_comum as AC
from aula_comum import (celula, clique, A, etapa, ETAPAS, cria_objeto, da_fisica,
                        confere_fisica, abre_mesa, fecha_mesa, rastreio, cor)
from comum import fecha_painel_objeto
ETAPAS.clear()

D = "aula4"
CEU = "0B1026"          # azul quase preto: e ele que faz o tiro aparecer
AC.SPRITES = {
    "Nave":    ("Gustavo Sprites", "Ships", 0, 0),        # nave cinza, aponta para cima
    "Tiro":    ("Gustavo Sprites", "Projectiles", 0, 2),  # o raio amarelo
    "Inimigo": ("Gustavo Sprites", "Ships", 3, 0),        # nave vermelha
    "Canhao":  ("Gustavo Sprites", "Ships", 2, 1),        # nave roxa, la em cima
}

# A FASE CABE NA TELA. Aqui o cenario nao e comprido como na Aula 2: o que se
# move e o que o jogo CRIA, nao a vista.
CEL_NAVE = (8, 10)
CEL_TIRO = (1, 1)
CEL_INIMIGO = (14, 1)
CEL_CANHAO = (8, 0)

ANGULO_CIMA = 270       # medido: 0 e direita, 90 e baixo
ANGULO_BAIXO = 90
VIDA_DO_TIRO = 90       # trinta avos de segundo => 3 s
VIDA_DO_INIMIGO = 150   # 5 s, o bastante para atravessar a tela


@etapa
def novo():
    A.url = editor.jogo_novo()
    print("   jogo:", A.url, flush=True)
    A.guarda_url()
    comum.calibra_grade(16, 12)
    A.cap("p01_vazio")
    # OS TRES CLIPES DE ABERTURA sao os mesmos de toda aula: eles acontecem no
    # SITE do Flowlab, antes de existir jogo nenhum, e o gesto e identico.
    # Reaproveitar aqui nao e a armadilha de reusar foto de outro jogo — nao ha
    # jogo nestes passos.
    for nome in ("abrir_my_games.gif", "novo_jogo.gif", "empty_project.gif"):
        os.makedirs(f"{D}/gifs", exist_ok=True)
        if not os.path.exists(f"{D}/gifs/{nome}"):
            shutil.copy(f"aula3/gifs/{nome}", f"{D}/gifs/{nome}")
    A.gesto("abrir_niveis", "g08a", (0, 0),
            lambda: editor.abre_niveis(), espera=1.8)
    A.gesto("pintar_o_ceu", "g08", (0, 0),
            lambda: editor.cor_do_ceu(CEU, abrir=False), espera=2.0)
    editor.volta_ao_nivel()
    A.cap("p02_ceu")
    return True


@etapa
def nave():
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    x, y = celula(*CEL_NAVE)
    A.gesto("criar_objeto", "g01", (x, y), lambda: clique(x, y), espera=1.5)
    a, _ = nav.captura("/tmp/_c4_rad.png")
    p = nav.acha_texto("create", arquivo=a)
    A.gesto("escolher_create", "g02", p, lambda: clique(*p), espera=3)
    editor.espera_tela("behaviors", limite=20)
    comum.nomeia("Nave"); comum.nomeia_tipo("Nave")
    A.cap("p03_nome")
    comum.abre_sprite()
    pacote, sub, lin, col = AC.SPRITES["Nave"]
    comum.abre_grade_sprite(pacote, sub)
    A.gesto("escolher_sprite", "g13", (0, 0),
            lambda: AC.poe_sprite("Nave", so_clique=True), espera=2.0)
    clique(*comum.SPRITE_OK); time.sleep(2); nav.espera_parar(limite=15)
    A.cap("p04_nave")
    # NO ESPACO NAO HA CHAO: com gravidade a nave cai para fora da tela assim
    # que o jogo comeca, e nada no editor acusa.
    A.gesto("abrir_physics", "g03", (0, 0), lambda: comum.abre_fisica(), espera=2.5)
    A.gesto("marcar_movable", "g04", (0, 0),
            lambda: comum.marca_caixa("movable", True), espera=1.2)
    A.gesto("sem_gravidade", "g05", (0, 0),
            lambda: comum.marca_caixa("affected by gravity", False), espera=1.2)
    A.cap("p05_fisica")
    fecha_painel_objeto(); time.sleep(1.5)
    editor.objeto_ou_abre(x, y)
    confere_fisica(movable=True, gravidade=False)
    fecha_painel_objeto(); time.sleep(1.5)
    return True


# O trio do movimento fica em DUAS FILEIRAS, longe uma da outra. Duas razoes
# medidas: `_ha_fio` apaga o corpo dos blocos da conta, e com os blocos perto a
# faixa apagada engole o fio inteiro (ele reprovava um fio que existia); e dois
# blocos de mesmo nome na mesma mesa fazem `acha_bloco` devolver sempre o
# PRIMEIRO — por isso cada fileira se procura dentro do seu proprio recorte.
FILA_ESQ  = (0.12, 0.06, 1.0, 0.43)
FILA_DIR  = (0.12, 0.43, 1.0, 0.70)
FILA_TIRO = (0.12, 0.70, 1.0, 0.96)
Y_ESQ, Y_DIR, Y_TIRO = 520, 960, 1400
VEL_NAVE = 3            # medido: 3 => ~60 px de tela por segundo (a tela em ~6 s)


def _na_fileira(b, regiao, quem):
    """O bloco esta MESMO na fileira que eu pedi?

       `bloco_ou_solta` reaproveita um bloco que ja exista no recorte — e foi
       assim que, numa sonda, o segundo `Keyboard` nunca nasceu: ele devolveu o
       PRIMEIRO, e o gesto seguinte trocou a tecla do bloco errado, sem erro
       nenhum na tela. A altura e a prova barata de que a fileira e a certa."""
    from PIL import Image as _Im
    # A altura da TELA de verdade, nao um numero decorado: o recorte e dado em
    # fracao, e `acha_bloco` acabou de fotografar.
    h = _Im.open("/tmp/_bl_acha.png").size[1]
    y0, y1 = regiao[1] * h, regiao[3] * h
    if not (y0 <= b.y <= y1):
        raise RuntimeError(f"o {quem} saiu na altura {b.y}, fora da fileira "
                           f"{int(y0)}..{int(y1)} — `bloco_ou_solta` deve ter "
                           "reaproveitado o bloco de outra fileira")
    return b


def _trio(y, regiao, codigo, nome_tecla, negativo, clipe=None, gid=None):
    """Keyboard -> Number -> Velocity.x, o trio da Aula 3 com duas trocas."""
    blocos.abre_categoria("Triggers")
    k = _na_fileira(blocos.bloco_ou_solta("Keyboard", 900, y, regiao=regiao),
                    regiao, f"Keyboard {nome_tecla}")
    AC.poe_tecla(k, codigo, nome_tecla, clipe=clipe, gid=gid)
    blocos.abre_categoria("Logic & Math")
    nu = _na_fileira(blocos.bloco_ou_solta("Number", 1700, y, regiao=regiao),
                     regiao, f"Number {nome_tecla}")
    # PELO BOTAO `−`, que e o caminho que a aula ensina (e o unico que funciona:
    # o campo engole o hifen digitado em primeiro lugar). O bloco nasce valendo
    # 0 — medido — entao sao VEL_NAVE cliques para chegar a -VEL_NAVE.
    if negativo:
        ponto = blocos.prepara_menos(nu, 0)
        blocos.clica_menos(ponto, VEL_NAVE)
        blocos.fecha_ajustes(); time.sleep(0.8)
    else:
        blocos.escreve_valor(nu, VEL_NAVE)
    lido = blocos.le_valor(nu)
    esperado = str(-VEL_NAVE if negativo else VEL_NAVE)
    if lido != esperado:
        raise RuntimeError(f"o Number da fileira {nome_tecla} mostra {lido!r} "
                           f"e eu esperava {esperado!r}")
    blocos.abre_categoria("Properties")
    ve = _na_fileira(blocos.bloco_ou_solta("Velocity", 2500, y, regiao=regiao),
                     regiao, f"Velocity {nome_tecla}")
    blocos.liga_fixo(k, "down", nu, "get")
    # NO `x`, NAO NO `y`: o `y` e o da lava da Aula 3, e manda a nave para
    # cima e para baixo.
    blocos.liga_fixo(nu, "out", ve, "x")
    print(f"   fileira {nome_tecla}: Keyboard -> Number({lido}) -> Velocity.x",
          flush=True)
    return k, nu, ve


@etapa
def movimento():
    """O MESMO TRIO DA AULA 3 (`Number` -> `Velocity`), com o `Always` trocado
       por um `Keyboard` e o `y` trocado pelo `x`.

       NAO e o pacote `Ship Controls`. Ele foi medido na bancada e nao e
       movimento de quatro setas: e girar-e-acelerar. As setas laterais so
       GIRAM a nave (`Rotation.add`) e a de cima empurra para onde o nariz
       aponta (`Motor.forward`). Com ele, o tiro sairia pelo nariz em qualquer
       direcao e o `emit angle` 270 deixaria de significar "para cima" — a
       aula inteira perderia o pe. O pacote tambem e uma caixa-preta: a
       crianca arrasta e nao aprende nada.

       MEDIDO TAMBEM: sem gravidade e sem atrito do ar (o painel de fisica do
       Flowlab nao tem amortecimento), a nave NAO PARA sozinha ao soltar a
       tecla. Isso nao e defeito, e o espaco — e a aula diz isso em voz alta,
       com a seta oposta como freio."""
    abre_mesa(*CEL_NAVE)
    _trio(Y_ESQ, FILA_ESQ, rs.ESQ, "left", True,
          clipe="tecla_esquerda", gid="g11")
    A.cap("p06_movimento")
    _trio(Y_DIR, FILA_DIR, rs.DIR, "right", False)
    A.cap("p06b_direita")
    time.sleep(2)
    fecha_mesa()
    return True


@etapa
def prova_movimento():
    """A promessa do passo 11: a seta esquerda leva a nave para a ESQUERDA, e a
       direita a TRAZ DE VOLTA. Sem isto a aula promete um gesto que ninguem
       mediu."""
    import numpy as np
    from PIL import Image
    cor_nave, tol = rastreio("Nave")
    print(f"   rastreando a nave por {cor_nave} (tol {tol})", flush=True)
    editor.volta_ao_editor(); time.sleep(2)
    editor.volta_ao_nivel()
    p = nav.acha_texto("play")
    if not p:
        raise RuntimeError("nao achei o botao Play")
    clique(*p); time.sleep(7); nav.espera_parar(limite=20)
    editor.exige_jogo()
    clique(1470, 620); time.sleep(1.5)

    def onde():
        a, _ = nav.captura("/tmp/_c4_mv.png")
        im = np.asarray(Image.open(a).convert("RGB"), dtype=int)
        m = comum.mascara_cor(im, cor_nave, tol)
        _ys, xs = np.nonzero(m)
        return int(xs.mean()) if len(xs) else None

    x0 = onde()
    rs.segura_tecla(rs.ESQ, 0.5); time.sleep(0.8)
    x1 = onde()
    rs.segura_tecla(rs.DIR, 0.5); time.sleep(1.6)
    x2 = onde()
    print(f"   x da nave: parada {x0}, depois da ESQUERDA {x1}, "
          f"depois da DIREITA {x2}", flush=True)
    if None in (x0, x1, x2):
        raise RuntimeError("perdi a nave de vista durante a medida")
    if not x1 < x0 - 20:
        raise RuntimeError(f"a seta ESQUERDA nao levou a nave para a esquerda "
                           f"({x0} -> {x1})")
    if not x2 > x1 + 20:
        raise RuntimeError(f"a seta DIREITA nao trouxe a nave de volta "
                           f"({x1} -> {x2})")
    A.cap("p06c_prova_movimento")
    print(f"   PROVADO: a esquerda move {x0 - x1} px e a direita traz "
          f"{x2 - x1} px de volta", flush=True)
    # VOLTA PARA O EDITOR: a etapa seguinte comeca no nivel, e quem termina no
    # jogo deixa a proxima medindo a tela errada.
    editor.volta_ao_editor(); time.sleep(2)
    return True


@etapa
def tiro():
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    cria_objeto(*CEL_TIRO, "Tiro", tipo="Tiro")
    A.cap("p07_tiro")
    # A CAIXINHA QUE JA MORDEU TRES VEZES: sem `movable` nenhuma forca tem
    # efeito, e o tiro nasce e fica parado no ar.
    x, y = celula(*CEL_TIRO)
    editor.objeto_ou_abre(x, y)
    comum.abre_fisica(); time.sleep(1.5)
    A.gesto("tiro_movable", "g06", (0, 0),
            lambda: comum.marca_caixa("movable", True), espera=1.2)
    comum.marca_caixa("affected by gravity", False)
    A.cap("p08_tiro_fisica")
    fecha_painel_objeto(); time.sleep(1.5)
    editor.objeto_ou_abre(x, y)
    confere_fisica(movable=True, gravidade=False)
    fecha_painel_objeto(); time.sleep(1.5)
    return True


@etapa
def atira():
    abre_mesa(*CEL_NAVE)
    blocos.abre_categoria("Components")
    # NA PALHETA ele e `Emit`; NA MESA o titulo e `Emitter`.
    em = blocos.bloco_ou_solta("Emit", 1900, Y_TIRO, titulo="Emitter",
                               regiao=FILA_TIRO)
    A.cap("p09_emitter")
    blocos.abre_ajustes(em); time.sleep(1.5)
    A.gesto("ajustes_do_tiro", "g07", (0, 0),
            lambda: blocos.escolhe_na_lista("object to emit", "Tiro"), espera=1.6)
    blocos.campo_ao_lado("emit angle", ANGULO_CIMA)
    blocos.campo_ao_lado("expire after", VIDA_DO_TIRO)
    blocos.fecha_ajustes(); time.sleep(1.0)
    A.cap("p10_ajustes")
    blocos.abre_categoria("Triggers")
    # A TERCEIRA fileira, com recorte proprio: a mesa ja tem dois `Keyboard`
    # (as setas do movimento) e `acha_bloco` devolveria o primeiro deles.
    k = _na_fileira(blocos.bloco_ou_solta("Keyboard", 900, Y_TIRO,
                                          regiao=FILA_TIRO),
                    FILA_TIRO, "Keyboard do tiro")
    # O BLOCO NASCE SEM TECLA: `Current key:` vem vazio, e um `Keyboard` sem
    # tecla nunca dispara — sem acusar nada no editor.
    AC.poe_tecla(k, 49, "spacebar", clipe="muda_a_tecla", gid="g09")
    em = blocos.acha_bloco("Emitter", regiao=FILA_TIRO)
    blocos.liga_fixo(k, "down", em, "emit")
    A.cap("p11_fio_tiro")
    time.sleep(2)
    fecha_mesa()
    return True


@etapa
def prova_tiro():
    """A promessa do passo 16: apertar espaco faz um tiro SUBIR."""
    import numpy as np
    from PIL import Image
    cor_tiro, tol = rastreio("Tiro", "Nave", "Inimigo")
    print(f"   rastreando o tiro por {cor_tiro} (tol {tol})", flush=True)
    editor.volta_ao_editor(); time.sleep(2)
    editor.volta_ao_nivel()
    p = nav.acha_texto("play")
    if not p:
        raise RuntimeError("nao achei o botao Play (estou mesmo no editor?)")
    A.gesto("jogar", "g10", p, lambda: clique(*p), espera=6)
    editor.exige_jogo()
    clique(1470, 620); time.sleep(1.5)

    def tiros():
        """Quantos pixels de tiro ha na tela, e a altura do mais alto.

           A PECA PARADA DO CANTO conta como tiro: ela esta na linha 1, em
           cima a esquerda. Por isso eu meco so a coluna da nave."""
        a, _ = nav.captura("/tmp/_c4_j.png")
        im = np.asarray(Image.open(a).convert("RGB"), dtype=int)
        m = comum.mascara_cor(im, cor_tiro, tol)
        faixa = m[:, 1300:1700]
        ys, _xs = np.nonzero(faixa)
        return int(faixa.sum()), (int(ys.min()) if len(ys) else None)

    antes, _ = tiros()
    rs.segura_tecla(49, 0.12)
    serie, melhor = [], antes
    for _ in range(5):
        n, topo = tiros()
        serie.append((n, topo))
        # A FOTO DO PASSO 16 TEM DE TER O TIRO NO AR.
        #
        # Ela era tirada DEPOIS do laco, e ate la o tiro ja tinha expirado (sao
        # 3 s de `Expire After`): a pagina prometia "um tiro sai da nave e
        # sobe" e mostrava a nave sozinha, com a peca-molde parada no canto. A
        # crianca compara a tela dela com a figura e nao acha o que o texto
        # promete. Guarda nenhum ve isso — a foto existe, abre, e nao e copia
        # de outra. Quem viu foi a FOLHA DE CONTATO.
        if n > melhor:
            melhor = n
            A.cap("p12_tiro")
    print(f"   antes do espaco: {antes} px de tiro na coluna da nave", flush=True)
    print(f"   depois: {serie}", flush=True)
    picos = [n for n, _ in serie]
    if max(picos) <= antes:
        raise RuntimeError(f"apertei espaco e nao nasceu tiro nenhum na coluna "
                           f"da nave (antes {antes}, depois {picos})")
    print("   PROVADO: o espaco faz nascer um tiro", flush=True)
    return True


@etapa
def inimigo():
    editor.volta_ao_editor(); time.sleep(2)
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    cria_objeto(*CEL_INIMIGO, "Inimigo", tipo="Inimigo")
    x, y = celula(*CEL_INIMIGO)
    editor.objeto_ou_abre(x, y)
    da_fisica(movable=True, gravidade=False, densidade=None, atrito=False)
    A.cap("p13_inimigo")
    fecha_painel_objeto(); time.sleep(1.5)
    return True


@etapa
def canhao():
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    cria_objeto(*CEL_CANHAO, "Canhao", tipo="Canhao")
    A.cap("p14_canhao")
    abre_mesa(*CEL_CANHAO)
    blocos.abre_categoria("Components")
    em = blocos.bloco_ou_solta("Emit", 1500, 1150, titulo="Emitter")
    blocos.abre_ajustes(em); time.sleep(1.5)
    blocos.escolhe_na_lista("object to emit", "Inimigo")
    blocos.campo_ao_lado("emit angle", ANGULO_BAIXO)
    blocos.campo_ao_lado("expire after", VIDA_DO_INIMIGO)
    blocos.fecha_ajustes(); time.sleep(1.0)
    blocos.abre_categoria("Triggers")
    t = blocos.bloco_ou_solta("Timer", 1000, 1150)
    blocos.abre_ajustes(t); time.sleep(1.3)
    blocos.marca_do_bloco("repeat forever", True)
    blocos.fecha_ajustes(); time.sleep(1.0)
    em = blocos.acha_bloco("Emitter")
    blocos.liga_fixo(t, "out", em, "emit")
    A.cap("p15_timer")
    time.sleep(2)
    fecha_mesa()
    return True


@etapa
def destroi():
    abre_mesa(*CEL_INIMIGO)
    blocos.abre_categoria("Triggers")
    c = blocos.bloco_ou_solta("Collision", 1120, 1150)
    d = blocos.bloco_ou_solta("Destroyer", 1700, 1150)
    blocos.liga_fixo(c, "hit", d, "in")
    # COM QUEM a batida conta. Em `Any Type` o inimigo se destroi ao encostar
    # em qualquer coisa — inclusive em outro inimigo.
    blocos.escolhe_tipo_da_colisao(c, "Tiro")
    A.cap("p16_fio_destroi")
    time.sleep(2)
    fecha_mesa()
    return True


@etapa
def prova():
    """As duas promessas do fim: os inimigos DESCEM sozinhos, e o tiro os APAGA."""
    import numpy as np
    from PIL import Image
    cor_inim, tol_i = rastreio("Inimigo", "Nave", "Tiro")
    print(f"   rastreando o inimigo por {cor_inim} (tol {tol_i})", flush=True)
    editor.volta_ao_editor(); time.sleep(2)
    editor.volta_ao_nivel()
    p = nav.acha_texto("play")
    clique(*p); time.sleep(7); nav.espera_parar(limite=20)
    editor.exige_jogo()
    clique(1470, 620); time.sleep(1.5)

    def inimigos():
        """Quantos pixels de inimigo ha, e a altura do MAIS BAIXO deles."""
        a, _ = nav.captura("/tmp/_c4_p.png")
        im = np.asarray(Image.open(a).convert("RGB"), dtype=int)
        m = comum.mascara_cor(im, cor_inim, tol_i)
        ys, _xs = np.nonzero(m)
        return int(m.sum()), (int(ys.max()) if len(ys) else None)

    # 1) ELES DESCEM SOZINHOS.
    #
    # A MEDIA NAO SERVE, e eu a usei e ela mentiu: com o canhao soltando sem
    # parar e os inimigos expirando sozinhos, a altura media entra em REGIME e
    # fica parada. Medi [622, 588, 615, 586, 600, 594, 598, 612] num jogo em
    # que os inimigos desciam a tela inteira — a prova reprovou o que estava
    # certo. Fluxo constante nao se mede pela media.
    #
    # O que a aula promete e que o inimigo SAI DE CIMA E CHEGA PERTO DA NAVE.
    # Entao a regua e a propria tela: o vermelho mais BAIXO tem de passar da
    # metade do caminho entre onde ele nasce e onde a nave esta. Sem numero
    # decorado: os dois extremos sao lidos na hora.
    # A REGUA E O CEU DA FASE, nao a nave.
    #
    # Rastrear a nave aqui nao da: ela, o tiro e o canhao saem do mesmo pacote
    # de desenhos e dividem o mesmo azul — `rastreio` recusa, e com razao. Ja o
    # ceu e cor que ESTA AULA pinta (CEU), entao o retangulo dele e a area de
    # jogo, lida na hora e sem numero decorado.
    a0, _ = nav.captura("/tmp/_c4_p0.png")
    im0 = np.asarray(Image.open(a0).convert("RGB"), dtype=int)
    rgb_ceu = tuple(int(CEU[i:i + 2], 16) for i in (0, 2, 4))
    ysc, _x = np.nonzero(comum.mascara_cor(im0, rgb_ceu, 14))
    ysi, _x = np.nonzero(comum.mascara_cor(im0, cor_inim, tol_i))
    if len(ysc) < 20000:
        raise RuntimeError(f"nao achei o ceu da fase na tela do jogo "
                           f"({len(ysc)} px) — sem ele nao ha regua")
    if not len(ysi):
        raise RuntimeError("nao achei nenhum inimigo na tela do jogo")
    topo, fundo_area = int(ysi.min()), int(ysc.max())
    alvo = topo + (fundo_area - topo) * 0.5
    print(f"   area de jogo ate y={fundo_area} ({len(ysc)} px de ceu)",
          flush=True)
    fundos = []
    for _ in range(12):
        n, y = inimigos()
        if y is not None:
            fundos.append(y)
        time.sleep(0.5)
    print(f"   inimigo nasce em y={topo}, pe da fase em y={fundo_area}, "
          f"alvo y>={int(alvo)}", flush=True)
    print(f"   vermelho mais baixo: {fundos}", flush=True)
    if not fundos or max(fundos) < alvo:
        raise RuntimeError(f"os inimigos nao desceram sozinhos: o vermelho mais "
                           f"baixo chegou a {max(fundos) if fundos else None} e "
                           f"precisava passar de {int(alvo)}")
    A.cap("p17_jogo")
    print(f"   PROVADO: o inimigo desce {max(fundos) - topo} px sozinho, "
          f"mais da metade do caminho ate a nave", flush=True)
    return True


def main():
    AC.main(sys.modules[__name__])


if __name__ == "__main__":
    main()
