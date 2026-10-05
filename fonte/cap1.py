#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Captura da Aula 1 — Pega-moedas.

   O jogo: um boneco que corre num chao, e uma moeda que some quando ele
   encosta. Termina jogavel, com link para mandar para a familia.

   Cada gesto que a aula pede fica registrado em `alvos.json` com o PONTO do
   clique e QUAL BOTAO — e dai sai a animacao com o mouse do botao aceso.

   Medidas da tela (pagina em 100%):
   - a area do nivel comeca em (958, 415) e cada celula tem 64 px;
   - o OK do painel do objeto e branco sobre AZUL (o OCR nao le) e muda de
     altura quando o Physics esta aberto: acha-se pela cor."""
import os, sys, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rs, nav, editor, blocos

D = "aula1"
ALVOS = os.path.join(D, "alvos.json")

import comum
from comum import (celula, clique, pinta, nomeia, abre_sprite, marca_caixa,
                   arrasta_slider, fecha_painel_objeto, confere_fase,
                   LINHA_CHAO, LINHA_ANDAR, COL_JOGADOR, COL_MOEDA, COLS_CHAO,
                   CELULA, GRADE_X, GRADE_Y, A, etapa, ETAPAS,
                   SPRITE_OK)

comum.pasta("aula1")
ETAPAS.clear()      # a lista vive em comum.py: cada aula comeca a sua
D = "aula1"

def _cor_de(quem, indice=0):
    """A cor de rastreio de um objeto. Vem do arquivo, para a PROVA poder rodar
       sozinha depois, sem ter acabado de escolher o sprite."""
    import json
    if quem in CORES and CORES[quem]:
        return tuple(CORES[quem][indice])
    caminho = os.path.join(D, "cores.json")
    if os.path.exists(caminho):
        guardado = json.load(open(caminho))
        if quem in guardado:
            return tuple(guardado[quem][indice])
    raise RuntimeError(f"nao sei a cor de `{quem}` — rode a captura do sprite "
                       "antes, ou apague aulaN/cores.json e refaca")


def _cor_mais_distinta(quem, longe_de):
    """Entre as cores do sprite, a que mais se afasta das dos vizinhos."""
    opcoes = []
    for i in range(5):
        try:
            opcoes.append(_cor_de(quem, i))
        except (RuntimeError, IndexError):
            break
    if not opcoes:
        raise RuntimeError(f"nao tenho cor nenhuma de `{quem}`")
    def dist(c):
        return min(sum(abs(a - b) for a, b in zip(c, o)) for o in longe_de)
    return max(opcoes, key=dist)


def _poe_sprite(quem, so_clique=False):
    """Escolhe o desenho do objeto e guarda a cor com que a prova vai acha-lo.

       A cor nao e mais suposta: ela sai do sprite. E a lista toda e guardada,
       nao so a dominante — a pele do heroi puxa para o mesmo tom da moeda de
       ouro, e rastrear os dois por ai daria numero bonito e errado."""
    pacote, sub, lin, col = SPRITES[quem]
    if so_clique:
        ponto = comum.clica_sprite(lin, col)
    else:
        ponto = comum.escolhe_sprite(pacote, sub, lin, col)
    CORES[quem] = comum.cores_do_sprite("/tmp/_sp_dep.png")
    import json
    os.makedirs(D, exist_ok=True)
    caminho = os.path.join(D, "cores.json")
    guardado = json.load(open(caminho)) if os.path.exists(caminho) else {}
    guardado[quem] = CORES[quem]
    json.dump(guardado, open(caminho, "w"), indent=1)
    print(f"   sprite de {quem}: cores {CORES[quem][:3]}", flush=True)
    return ponto


@etapa
def novo():
    A.url = editor.jogo_novo()
    print("   jogo:", A.url, flush=True)
    A.guarda_url()
    A.cap("p01_vazio")
    return True


@etapa
def jogador():
    x, y = celula(COL_JOGADOR, LINHA_ANDAR)
    A.gesto("criar_objeto", "g01", (x, y), lambda: clique(x, y), espera=1.5)
    a, _ = nav.captura("/tmp/_rad.png")
    p = nav.acha_texto("create", arquivo=a)
    A.gesto("escolher_create", "g02", p, lambda: clique(*p), espera=3)
    editor.espera_tela("behaviors", limite=20)
    A.cap("p02_painel")
    nomeia("Jogador")
    A.cap("p03_nome")
    abre_sprite()
    A.cap("p04_sprite")
    # a navegacao ate a grade NAO entra no clipe: o gesto atravessa quatro
    # telas e um clipe e um par antes-e-depois. Gravo o clique no boneco.
    pacote, sub, lin, col = SPRITES["Jogador"]
    comum.abre_grade_sprite(pacote, sub)
    A.gesto("escolher_sprite", "g13", (0, 0),
            lambda: _poe_sprite("Jogador", so_clique=True), espera=2.0)
    A.cap("p05_azul")
    clique(*SPRITE_OK); time.sleep(2); nav.espera_parar(limite=15)
    A.gesto("abrir_physics", "g03", (0, 0),
            lambda: comum.abre_fisica(), espera=2.5)
    A.gesto("marcar_movable", "g04", (1681, 476),
            lambda: marca_caixa("movable", True), espera=1.2)
    A.cap("p06_movable")
    fecha_painel_objeto()
    A.cap("p07_jogador_pronto")
    return True


DENSIDADE = 30     # medido: pega a moeda E ainda pula. Ver peso() abaixo.

# OS DESENHOS. Ate aqui todo objeto era um quadrado pintado com a latinha:
# funcionava e era facil de medir, mas um jogo de quadrados azuis nao motiva
# ninguem de 10 anos. Agora vem da biblioteca do Flowlab (pacote do ENDESGA).
SPRITES = {
    "Jogador": ("Flowlab Sprites", "Characters", 0, 0),   # o menino de camisa azul
    "Moeda":   ("Flowlab Sprites", "Objects", 1, 2),      # a moeda de ouro
    "Chao":    ("Flowlab Sprites", "Blocks", 0, 0),       # o bloco de grama
}
CORES = {}          # a cor de rastreio de cada um, MEDIDA do proprio sprite


@etapa
def peso():
    """Deixa o jogador PESADO -- mas nao pesado DEMAIS.

       Sem peso nenhum ele corre 180 px por quadro e atravessa a moeda sem a
       fisica registrar contato: a moeda nao some e nada no editor acusa.

       Mas com densidade 100 ele passa a nao PULAR, e o passo 15 desta mesma
       aula manda arrastar o pacote `Run & Jump` e diz que ele faz o boneco
       "correr com as setas e pular". A pagina prometia um pulo que o arquivo
       nao dava. Medido no rascunho da Aula 2: com densidade 30 o pulo sobe
       273 px (quatro casas) e o passo horizontal fica em 60 px -- menos que
       uma casa, entao a colisao com a moeda continua valendo.

       A friccao fica no maximo: e ela que impede o boneco de deslizar."""
    editor.volta_ao_nivel()
    x, y = celula(COL_JOGADOR, LINHA_ANDAR)
    editor.objeto_ou_abre(x, y)
    A.gesto("abrir_physics2", "g07", (0, 0),
            lambda: comum.abre_fisica(), espera=2.5)
    marca_caixa("movable", True)      # sem isto a Densidade fica desabilitada
    pd = nav.acha_texto("density", arquivo=nav.captura("/tmp/_c1_d.png")[0],
                        regiao=(0.45, 0.1, 1.0, 0.85))
    if not pd:
        raise RuntimeError("nao achei o controle 'Density' no painel de fisica")
    alvo = (int(pd[0] + 155 + 2.75 * DENSIDADE), pd[1])
    A.gesto("peso_do_pulo", "g08", alvo, lambda: clique(*alvo), espera=1.2)
    A.cap("p21_densidade")
    arrasta_slider("friction")
    A.cap("p22_friccao")
    fecha_painel_objeto()
    return True


@etapa
def movimento():
    editor.volta_ao_nivel()
    x, y = celula(COL_JOGADOR, LINHA_ANDAR)
    editor.objeto_ou_abre(x, y)
    editor.abre_comportamentos()
    A.cap("p08_comportamentos")
    blocos.abre_categoria("Behavior Bundles")
    A.cap("p09_pacotes")
    b = blocos.bloco_ou_solta("Run & Jump", 1500, 760)
    A.cap("p10_run_and_jump")
    print("   pacote:", b, flush=True)
    time.sleep(2.5)                     # o Flowlab precisa de tempo para guardar
    editor.fecha_comportamentos()
    time.sleep(2.5)
    fecha_painel_objeto()
    time.sleep(2.0)
    # PROVA de que ficou salvo: reabre e procura. Sem isto, o pacote some em
    # silencio, o jogador nao anda, e nada no editor acusa — foi o que fez a
    # Aula 1 falhar tres vezes seguidas.
    editor.objeto_ou_abre(x, y)
    editor.abre_comportamentos()
    # o canvas demora a desenhar: tento algumas vezes antes de acusar sumico,
    # senao eu reprovo um pacote que esta la e so nao foi pintado ainda
    lido = ""
    for tentativa in range(4):
        time.sleep(1.5)
        a, _ = nav.captura("/tmp/_c1_persist.png")
        lido = " ".join(t for t, *_ in rs.ocr_forte(a, regiao=(0.2, 0.05, 1, 0.9),
                                                    psm="6")).lower()
        if "run" in lido or "jump" in lido:
            break
    if "run" not in lido and "jump" not in lido:
        raise RuntimeError("o pacote Run & Jump NAO ficou salvo no jogador "
                           f"(li {lido[:80]!r})")
    print("   pacote conferido depois de reabrir", flush=True)
    editor.fecha_comportamentos()
    time.sleep(2.0)
    fecha_painel_objeto()
    return True


@etapa
def chao():
    """Chao CONTIGUO: pecas coladas, de 64 em 64 px. Na primeira montagem elas
       sairam espacadas e o jogador caiu pelo vao."""
    editor.volta_ao_nivel()
    x, y = celula(COLS_CHAO[0], LINHA_CHAO)
    editor.objeto_ou_abre(x, y)
    nomeia("Chao")
    abre_sprite()
    _poe_sprite("Chao")
    A.cap("p11_chao_verde")
    clique(*SPRITE_OK); time.sleep(2); nav.espera_parar(limite=15)
    fecha_painel_objeto()
    clique(x, y); time.sleep(1.5)
    a, _ = nav.captura("/tmp/_rad2.png")
    p = nav.acha_texto("clone", arquivo=a)
    A.gesto("clonar", "g05", p, lambda: clique(*p), espera=2)
    for c in COLS_CHAO[1:]:
        cx, cy = celula(c, LINHA_CHAO)
        clique(cx, cy); time.sleep(1.1)        # devagar: clique rapido nao coloca
    A.cap("p12_chao")
    q = nav.acha_texto("done cloning")
    clique(*q); time.sleep(2); nav.espera_parar(limite=15)
    A.cap("p13_chao_pronto")
    return True


@etapa
def moeda():
    editor.volta_ao_nivel()
    x, y = celula(COL_MOEDA, LINHA_ANDAR)
    editor.objeto_ou_abre(x, y)
    nomeia("Moeda")
    abre_sprite()
    _poe_sprite("Moeda")
    A.cap("p14_moeda_amarela")
    clique(*SPRITE_OK); time.sleep(2); nav.espera_parar(limite=15)
    editor.abre_comportamentos()
    c = blocos.solta("Collision", 1100, 500)
    A.cap("p15_collision")
    d = blocos.solta("Destroyer", 1900, 950)
    A.cap("p16_destroyer")
    blocos.liga_fixo(c, "hit", d, "in")
    A.cap("p17_fio")
    editor.fecha_comportamentos()
    fecha_painel_objeto()
    A.cap("p18_moeda_pronta")
    return True


@etapa
def prova():
    """Joga, anda para a direita e PROVA que a moeda sumiu."""
    from PIL import Image
    import numpy as np

    # AS CORES VEM DOS SPRITES, nao de um palpite meu. E antes de usar, confiro
    # que elas se distinguem: com dois objetos de cor parecida, a prova acha um
    # pensando que achou o outro, e o numero sai bonito e errado.
    cor_moeda = _cor_de("Moeda")
    # A MAIS DISTINTA, nao a primeira: a cor mais comum do heroi e a PELE, que
    # puxa para o mesmo tom da moeda de ouro. A camisa azul distingue.
    cor_jog = _cor_mais_distinta("Jogador", [cor_moeda])
    if not comum.distantes([cor_moeda, cor_jog]):
        raise RuntimeError(f"a moeda {cor_moeda} e o jogador {cor_jog} tem cores "
                           "parecidas demais para a prova distinguir")
    print(f"   rastreando moeda por {cor_moeda} e jogador por {cor_jog}", flush=True)

    def amarelo(f):
        im = np.asarray(Image.open(os.path.join(D, f)).convert("RGB"), dtype=int)
        return int(comum.mascara_cor(im, cor_moeda).sum())

    def azul():
        """Onde esta o boneco agora, em pixels da tela."""
        a, _ = nav.captura("/tmp/_c1_j.png")
        # O CENTRO DE TODOS OS PIXELS da cor, e com minimo baixo: no jogo o
        # sprite e desenhado pequeno e a camisa sai PARTIDA — 192 px em
        # pedacos de 80. Exigir uma mancha de 600 px dizia que o boneco nao
        # estava na tela com ele na tela.
        g = comum.centro_por_cor(a, cor_jog, minimo=60)
        return (g[0], g[1]) if g else None

    editor.volta_ao_editor(); time.sleep(2)
    editor.volta_ao_nivel()
    confere_fase({"chao": _cor_de("Chao"), "jogador": cor_jog, "moeda": cor_moeda})
    p = nav.acha_texto("play")
    A.gesto("jogar", "g06", p, lambda: clique(*p), espera=6)
    editor.exige_jogo()
    clique(1470, 640); time.sleep(1.5)
    antes = A.cap("p19_jogo")
    n0 = amarelo(antes)

    # PROMESSA DO PASSO 15: o pacote faz o boneco "correr com as setas e
    # PULAR". Com densidade 100 ele nao saia do chao e a aula mentia. Entao a
    # prova mede o pulo ANTES de andar -- depois de pegar a moeda ele ja pode
    # estar na beirada do chao.
    base = azul()
    if not base:
        raise RuntimeError("nao achei o boneco azul no jogo")
    alturas = []
    rs.segura_tecla(126, 0.2)           # 126 = seta para cima
    for _ in range(6):
        time.sleep(0.12)
        q = azul()
        alturas.append(q[1] if q else None)
    validos = [h for h in alturas if h]
    sobe = base[1] - min(validos) if validos else 0
    print(f"   pulo: subiu {sobe} px", flush=True)
    if sobe < 60:
        raise RuntimeError(f"o boneco subiu so {sobe} px: o passo 15 promete "
                           "que o pacote faz ele PULAR, e com este peso ele "
                           "nao sai do chao")
    time.sleep(1.5)
    # toques CURTOS, conferindo a cada um: segurando, o boneco passa correndo
    # pela moeda e cai no fim do chao antes de a colisao valer
    n1 = n0
    for k in range(14):
        rs.segura_tecla(124, 0.12); time.sleep(0.45)   # 124 = seta direita
        n1 = amarelo(A.cap("p20_pegou"))
        if n1 < n0 * 0.5:
            print(f"   a moeda sumiu no toque {k+1}", flush=True)
            break
    print(f"   moeda: {n0} px antes, {n1} px depois", flush=True)
    if n1 >= n0 * 0.5:
        raise RuntimeError(f"a moeda NAO sumiu ({n0} -> {n1} px amarelos): "
                           "o jogo nao faz o que a aula promete")
    print("   PROVADO: a moeda sumiu quando o jogador encostou", flush=True)
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
