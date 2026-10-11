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
    for cc in colunas:
        cx, cy = celula(cc, r)
        clique(cx, cy); time.sleep(1.0)
    q = nav.acha_texto("done cloning")
    if not q:
        raise RuntimeError("clonei e nao achei o `Done Cloning` para fechar")
    clique(*q); time.sleep(2); nav.espera_parar(limite=15)
    return True


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
