#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O que toda aula de Flowlab faz igual — para a proxima nascer curta.

   Medido: `cap2.py` e `cap3.py` tem 247 linhas IDENTICAS, 43% do menor dos
   dois. Cada conserto de instrumento precisava ser copiado nos dois, e as
   vezes ficava so num (a `refaz_clipes` restaurava o peso do jogador na Aula
   2 e NAO na 3 — o clipe sairia bonito e o boneco com a fisica errada).

   ⚠️ As aulas 1, 2 e 3 NAO foram migradas de proposito: elas estao capturadas,
   provadas e publicadas, e refatorar forma ja aprovada exige provar que a
   mudanca e neutra — o que aqui custa uma recaptura inteira. **Daqui para
   frente, aula nova importa deste modulo.** Quem mexer numa das tres na
   proxima vez, migra.

   O que este modulo garante e que nenhuma aula nova escreve sem LER DE VOLTA.
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rs, nav, editor, blocos, comum
from comum import (celula, clique, nomeia, nomeia_tipo, abre_sprite, marca_caixa,
                   arrasta_slider, fecha_painel_objeto, A, etapa, ETAPAS,
                   SPRITE_OK)

# cada aula poe aqui a sua tabela antes de usar o resto
SPRITES = {}
CORES = {}


def pasta():
    return comum.D


# ───────────────────────── as cores dos sprites ─────────────────────────
#
# A prova em jogo acha cada objeto na tela pela COR do desenho dele. As cores
# sao medidas na hora de escolher o sprite e guardadas em `aulaN/cores.json`,
# porque a prova roda numa sessao diferente da captura.

def _guardadas(quem):
    if quem in CORES and CORES[quem]:
        return CORES[quem]
    caminho = os.path.join(pasta(), "cores.json")
    if os.path.exists(caminho):
        g = json.load(open(caminho))
        if quem in g:
            return g[quem]
    raise RuntimeError(f"nao sei as cores de `{quem}` — o sprite dele ja foi escolhido?")


def cores(quem):
    return _guardadas(quem)


def cor(quem, indice=0):
    return tuple(_guardadas(quem)[indice])


def rastreio(quem, *outros):
    """(cor, tolerancia) para achar `quem` na tela sem achar `outros`.

       Os `outros` se escolhem a mao: chao, plataforma e degrau alto sao o
       MESMO desenho, e exigir que se distingam entre si reprovaria uma fase
       correta. Quem precisa ser distinguido e quem a prova mede."""
    return comum.cor_de_rastreio({q: cores(q) for q in (quem,) + outros}, quem)


def poe_sprite(quem, so_clique=False):
    """Escolhe o desenho na biblioteca e guarda as cores dele."""
    pacote, sub, lin, col = SPRITES[quem]
    ponto = (comum.clica_sprite(lin, col) if so_clique
             else comum.escolhe_sprite(pacote, sub, lin, col))
    CORES[quem] = comum.cores_do_sprite("/tmp/_sp_dep.png")
    os.makedirs(pasta(), exist_ok=True)
    caminho = os.path.join(pasta(), "cores.json")
    g = json.load(open(caminho)) if os.path.exists(caminho) else {}
    g[quem] = CORES[quem]
    json.dump(g, open(caminho, "w"), indent=1)
    print(f"   sprite de {quem}: cores {CORES[quem][:3]}", flush=True)
    return ponto


# ──────────────────────────── criar objeto ────────────────────────────

def cria_objeto(c, r, nome, tipo=None, clones=None):
    """Cria o objeto na casa (c, r): nome, TIPO, desenho — e clona se pedido.

       O TIPO nao e enfeite: e ele que aparece na lista do bloco `Collision`.
       Sem ele a lista mostra `New Type 1`, `New Type 2`… e nao ha como a
       crianca saber qual e qual. `nomeia_tipo` le de volta."""
    x, y = celula(c, r)
    editor.objeto_ou_abre(x, y)
    nomeia(nome)
    if tipo:
        nomeia_tipo(tipo)
    abre_sprite()
    poe_sprite(nome)
    clique(*SPRITE_OK); time.sleep(2); nav.espera_parar(limite=15)
    fecha_painel_objeto()
    if clones:
        clona(c, r, nome, clones)
    return (x, y)


def clona(c, r, nome, colunas):
    """Repete o objeto da casa (c, r) nas `colunas` da mesma fileira."""
    x, y = celula(c, r)
    clique(x, y); time.sleep(1.5)
    a, _ = nav.captura("/tmp/_ac_clone.png")
    p = nav.acha_texto("clone", arquivo=a)
    if not p:
        raise RuntimeError(f"nao achei Clone para {nome}")
    clique(*p); time.sleep(2)
    primeira = None
    for cc in colunas:
        if primeira is None:
            primeira = cc
        cx, cy = celula(cc, r)
        clique(cx, cy); time.sleep(1.0)
    q = nav.acha_texto("done cloning")
    if not q:
        raise RuntimeError("clonei e nao achei o `Done Cloning` para fechar")
    clique(*q); time.sleep(2); nav.espera_parar(limite=15)
    # DEVOLVE A PRIMEIRA CASA CLONADA, nao `True`: quando esta chamada e o
    # gesto de um clipe, e este ponto que vira a seta — e `True` deixava o alvo
    # em (0,0), com a seta no canto da tela. A primeira casa clonada e o melhor
    # alvo possivel: ela esta VAZIA no quadro de antes e tem bloco no de
    # depois, que e exatamente o que a crianca precisa ver.
    return celula(primeira, r) if primeira is not None else True


# ──────────────────────────────── fisica ────────────────────────────────

def da_fisica(movable=True, gravidade=None, solido=None, colisoes=None,
              densidade=None, atrito=True, faixa=(20, 45)):
    """Abre a fisica do objeto JA ABERTO e mexe no que for pedido, conferindo.

       Toda caixinha se confere pela COR dela (`marca_caixa` ja faz isso) e
       todo numero se LE DE VOLTA. Sem `movable` nenhuma forca tem efeito — e
       esse descuido ja custou tres vezes neste curso: o boneco que nao
       pulava, a lava que nao subia e o tiro que nao andava."""
    comum.abre_fisica(); time.sleep(1.5)
    if movable is not None:
        marca_caixa("movable", movable)
    if gravidade is not None:
        marca_caixa("affected by gravity", gravidade)
    if solido is not None:
        marca_caixa("is solid", solido)
    if colisoes is not None:
        marca_caixa("enable collisions", colisoes)
    if densidade is not None:
        pd = comum._acha_no_painel("density", nav.captura("/tmp/_ac_d.png")[0])
        if not pd:
            raise RuntimeError("nao achei o controle Density no painel de fisica")
        clique(int(pd[0] + 155 + 2.75 * densidade), pd[1]); time.sleep(1.2)
        lido = comum.le_numero_do_painel("density")
        if lido is None or not (faixa[0] <= lido <= faixa[1]):
            raise RuntimeError(f"pedi densidade {densidade} e o painel mostra "
                               f"{lido} — fora da faixa {faixa}")
        print(f"   peso = {lido}", flush=True)
    if atrito:
        arrasta_slider("friction")
    return True


def confere_fisica(**esperado):
    """REABRE a fisica e confere. Quem grava e o OK do painel: ja houve um dia
       em que o clique do `OK` caiu no CEU e desmarcou `movable`, e o jogo foi
       publicado com um boneco que corria e nao pulava."""
    comum.abre_fisica(); time.sleep(1.5)
    a, _ = nav.captura("/tmp/_ac_conf.png")
    for rotulo, quero in esperado.items():
        nome = {"movable": "movable", "gravidade": "affected by gravity",
                "solido": "is solid", "colisoes": "enable collisions"}[rotulo]
        p = comum._acha_no_painel(nome, a)
        c = comum._caixinha(a, p) if p else None
        if not c or c[2] != quero:
            raise RuntimeError(f"depois de fechar, `{nome}` esta {c} e eu "
                               f"esperava {quero}")
    print("   fisica conferida depois de fechar: " +
          ", ".join(f"{k}={v}" for k, v in esperado.items()), flush=True)
    return True


def _na_fila(b, regiao, quem):
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


# ──────────────────────────── a tecla do `Keyboard` ────────────────────────────

def ponto_change_key(arquivo=None):
    """O ponto do botao `Change Key`, achado pelo rotulo `Current key:`.

       Procurar o botao pelo PROPRIO nome nao funciona: a coluna da palheta
       cobre a primeira letra dele e o OCR le `ange Key`. O rotulo de cima
       nasce inteiro, entao o botao e o primeiro pedaco de `Change Key` ABAIXO
       dele."""
    a = arquivo or nav.captura("/tmp/_ac_key.png")[0]
    itens = rs.ocr_forte(a, psm="6")
    base = None
    for t, x, y, w, h in itens:
        if t.strip().lower().startswith("current"):
            base = y
    if base is None:
        raise RuntimeError("o painel do `Keyboard` nao mostra `Current key:` "
                           "— os ajustes nao abriram")
    alvos = [(x, y, w, h) for t, x, y, w, h in itens
             if t.strip().lower() in ("key", "ange", "change") and y > base + 20]
    if not alvos:
        raise RuntimeError("achei `Current key:` mas nao o botao `Change Key`")
    x, y, w, h = min(alvos, key=lambda it: it[1])
    return (x + w // 2, y + h // 2)


def poe_tecla(bloco, codigo, nome, clipe=None, gid=None):
    """Escolhe a tecla de um `Keyboard` e LE DE VOLTA o que o painel mostra.

       O bloco nasce SEM tecla (`Current key:` vem vazio), e um `Keyboard` sem
       tecla nao dispara nunca — sem acusar nada no editor.

       Com `clipe`, o gesto gravado e SO o clique no `Change Key` mais a tecla:
       o painel fica aberto nos dois quadros e a crianca ve o campo mudar.
    """
    blocos.abre_ajustes(bloco); time.sleep(1.3)
    p = ponto_change_key()

    def troca():
        rs.clique_img(p[0], p[1], escala=2.0, janela=nav.janela()); time.sleep(1.4)
        rs.tecla(codigo); time.sleep(1.2)
        return p

    if clipe:
        A.gesto(clipe, gid, p, troca, espera=1.4)
    else:
        troca()
    b, _ = nav.captura("/tmp/_ac_key2.png")
    if not rs.tem_texto(nome, arquivo=b):
        raise RuntimeError(f"apertei a tecla no `Change Key` e o painel nao "
                           f"mostra `{nome}`")
    print(f"   tecla = {nome}", flush=True)
    blocos.fecha_ajustes(); time.sleep(1.2)
    return p


# ──────────────────────────── mesa de blocos ────────────────────────────

def abre_mesa(c, r):
    """Abre a mesa de blocos do objeto da casa (c, r) e amarra o contexto."""
    x, y = celula(c, r)
    editor.objeto_ou_abre(x, y)
    editor.abre_comportamentos()
    blocos.contexto(A.url or open(os.path.join(pasta(), "jogo.txt")).read().strip(),
                    (x, y))
    return (x, y)


def fecha_mesa():
    """O OK azul da mesa e o que COMMITA os blocos: fechar de outro jeito
       descarta tudo o que foi solto desde que ela abriu."""
    editor.fecha_comportamentos(); time.sleep(2.5)
    fecha_painel_objeto(); time.sleep(1.5)
    return True


def main(modulo):
    """O corredor das etapas, igual para toda aula."""
    alvo = sys.argv[1] if len(sys.argv) > 1 else None
    nomes = [f.__name__ for f in ETAPAS]
    fns = ETAPAS if not alvo else ETAPAS[nomes.index(alvo):]
    for f in fns:
        print(f"== {f.__name__} ==", flush=True)
        try:
            f()
        except Exception:
            # A DIAGNOSE SAI JUNTO COM O ERRO, em texto. Sem isto toda
            # investigacao minha comecava com uma foto, e foto e a coisa mais
            # cara que eu leio.
            print(f"\n⛔ a etapa `{f.__name__}` parou. Onde eu estava:", flush=True)
            for l in comum.onde_estou():
                print("   " + l, flush=True)
            raise
    print("== fim ==", flush=True)
