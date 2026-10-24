#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aula 12 — Projeto livre e mostra. Fotografa o caminho de um projeto do comeco ao link.

   O projeto de exemplo: o jogo da Aula 11 (a estrela que gira) e CLONADO, ganha
   nome, outro ceu, outro jogador e mais estrelas, e e COMPARTILHADO por link.
   A turma faz o seu proprio jogo; o que a aula ensina e o CAMINHO — escolher o
   jogo-base, clonar, personalizar, jogar, mostrar.

   O que e NOVO (sem bloco novo hoje):
     - `Clone` no menu de tres pontos do cartao do jogo (`My Games`);
     - `Settings`: o NOME do jogo;
     - o botao de compartilhar do cartao e o `Share Game Link`.

   MEDIDO ANTES (PADRAO.md §2an):
     - o menu do cartao tem `Add Tag`, `Clone`, `Lock Version` e `Delete`;
     - `Clone` abre uma confirmacao (`Cancel` / `Clone Game`);
     - o dialogo `Share` mostra `https://flowlab.io/game/play/<ID>` e
       `Copy Link`;
     - `Settings` tem `Name`, `Gravity`, `Drag`, `Width`, `Height`.

       BANCADA=1 python3 fonte/roda_aula.py 12
"""
import os, shutil, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rs, nav, editor, blocos, comum

comum.pasta("aula12")
import aula_comum as AC
from aula_comum import (celula, clique, A, etapa, ETAPAS, cria_objeto, clona,
                        abre_mesa, fecha_mesa, rastreio, cor)
from comum import fecha_painel_objeto
ETAPAS.clear()

D = "aula12"
CEU = "2B1055"                    # um roxo de noite
NOME = "Estrelas da Noite"
AC.SPRITES = {
    "Jogador": ("Flowlab Sprites", "Characters", 1, 0),   # outro boneco
}
CEL_JOGADOR = (1, 8)
CEL_ESTRELA = (13, 9)
CLONES = [5, 8, 11]                # colunas das estrelas novas
F = 2940 / 2000                    # as medidas da pagina foram lidas na foto reduzida


def P(x, y):
    """Ponto da foto reduzida (2000 px) -> pixels da tela."""
    return (int(x * F), int(y * F))


def _id(url):
    return url.strip().rstrip("/").rsplit("/", 1)[-1].split("?")[0].strip()


BASE = _id(open("aula11/jogo.txt").read().strip())     # o jogo da Aula 11


def _gifs_comuns():
    os.makedirs(f"{D}/gifs", exist_ok=True)
    if not os.path.exists(f"{D}/gifs/abrir_my_games.gif") and os.path.exists("aula11/gifs/abrir_my_games.gif"):
        shutil.copy("aula11/gifs/abrir_my_games.gif", f"{D}/gifs/abrir_my_games.gif")


def _area_do_jogo(im):
    import numpy as _np
    rgb = tuple(int(CEU[i:i + 2], 16) for i in (0, 2, 4))
    ys, xs = _np.nonzero(comum.mascara_cor(im, rgb, 16))
    if len(ys) < 20000:
        raise RuntimeError(f"nao achei o ceu da fase na tela ({len(ys)} px)")
    return int(ys.min()), int(ys.max()), int(xs.min()), int(xs.max())


def _foto(nome):
    from PIL import Image
    import numpy as _np
    a, _ = nav.captura(f"/tmp/_c12_{nome}.png")
    return _np.asarray(Image.open(a).convert("RGB"), dtype=int)


def _estrelas_no_jogo():
    """[(x, y, area)] das manchas AMARELAS na fase, da esquerda para a direita."""
    import numpy as _np
    from scipy import ndimage
    im = _foto("e")
    y0, y1, x0, x1 = _area_do_jogo(im)
    reg = im[y0:y1 + 1, x0:x1 + 1]
    m = (reg[:, :, 0] > 200) & (reg[:, :, 1] > 150) & (reg[:, :, 2] < 150)
    m = ndimage.binary_closing(m, iterations=2)
    lab, n = ndimage.label(m)
    achados = []
    for i in range(1, n + 1):
        ys, xs = _np.nonzero(lab == i)
        if len(xs) >= 380:      # as estrelas medem ~465 px; o cabelo do boneco, bem menos
            achados.append((int(xs.mean()) + x0, int(ys.mean()) + y0, len(xs)))
    return sorted(achados)


def _ids_da_lista(k):
    """O id do jogo no cartao `k`, lido no dialogo de compartilhar. Fecha o dialogo."""
    col, lin = k % 2, k // 2
    clique(*P(182 + 898 * col, 694 + 531 * lin)); time.sleep(2.0)
    txt = nav.texto_da_tela()
    import re
    m = re.search(r"game/play/(\d{6,8})", txt.replace(" ", ""))
    clique(*P(1273, 857)); time.sleep(1.0)
    return m.group(1) if m else None


# ───────────────────────── do jogo-base ao clone ─────────────────────────

@etapa
def lista():
    nav.vai("https://flowlab.io/games/mine", espera=8); time.sleep(3)
    nav.fecha_dialogo()
    editor.espera_tela("my games", "new game", limite=25)
    _gifs_comuns()
    A.cap("p01_lista")
    achou = None
    for k in range(4):
        i = _ids_da_lista(k)
        print(f"   cartao {k}: jogo {i}", flush=True)
        if i == BASE:
            achou = k
            break
    if achou is None:
        raise RuntimeError(f"o jogo-base {BASE} (Aula 11) nao esta entre os 4 primeiros cartoes")
    open("/tmp/_c12_cartao.txt", "w").write(str(achou))
    print(f"   o jogo da Aula 11 e o cartao {achou}", flush=True)
    return True


@etapa
def menu():
    k = int(open("/tmp/_c12_cartao.txt").read())
    col, lin = k % 2, k // 2
    pt = P(932 + 898 * col, 331 + 531 * lin)
    A.gesto("abrir_o_menu", "g41", pt, lambda: clique(*pt), espera=1.5)
    A.cap("p02_menu")
    return True


@etapa
def clone():
    k = int(open("/tmp/_c12_cartao.txt").read())
    col, lin = k % 2, k // 2
    item = P(954 + 898 * col, 442 + 531 * lin)
    def clonar():
        clique(*item); time.sleep(2.0)
        A.cap("p03_dialogo")
        ok = nav.acha_texto("clone game")
        if not ok:
            raise RuntimeError("nao vi a confirmacao `Clone Game`")
        # o botao `Clone Game` de baixo (o titulo da janela tambem diz `Clone Game`)
        clique(*P(1238, 638)); time.sleep(5.0)
        return item
    A.gesto("clonar_o_jogo", "g42", item, clonar, espera=2.0)
    A.cap("p04_lista_clone")
    return True


@etapa
def edita():
    """Abre o clone: o cartao do alto, `Edit`."""
    pt = P(311, 564)
    def edit():
        clique(*pt); time.sleep(8.0)
        nav.espera_parar(limite=25)
        return pt
    A.gesto("editar_o_clone", "g43", pt, edit, espera=3.0)
    editor.espera_tela("library", "play", limite=30)
    url = nav.endereco()
    novo = _id(url)
    if not novo.isdigit() or int(novo) <= int(BASE):
        raise RuntimeError(f"abri {url}: nao e um jogo NOVO (base {BASE})")
    A.url = url
    print("   clone:", url, flush=True)
    A.guarda_url()
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    A.cap("p05_editor")
    return True


# ───────────────────────────── personalizar ─────────────────────────────

@etapa
def nome():
    editor.volta_ao_nivel()
    p = nav.acha_texto("settings")
    if not p:
        raise RuntimeError("nao achei o botao Settings")
    A.gesto("abrir_settings", "g44", p, lambda: clique(*p), espera=1.8)
    A.cap("p06_settings")
    campo = P(1353, 471)
    def escreve():
        clique(*campo); time.sleep(0.6)
        rs.tecla(0, cmd=True); time.sleep(0.3)
        rs.digita_teclas(NOME); time.sleep(0.8)
        return campo
    A.gesto("escrever_o_nome", "g45", campo, escreve, espera=1.0)
    lido = nav.texto_da_tela(regiao=comum_regiao(P(1100, 430), P(1500, 520))).lower()
    print("   campo Name:", lido, flush=True)
    if "estrelas" not in lido:
        raise RuntimeError(f"escrevi o nome e o campo mostra {lido!r}")
    A.cap("p07_nome")
    clique(*P(1285, 944)); time.sleep(2.0)                  # OK
    return True


def _meu_id():
    return _id(A.url or open(os.path.join(comum.pasta_atual() if hasattr(comum, "pasta_atual") else D, "jogo.txt")).read())


def comum_regiao(p0, p1):
    return (max(0.0, p0[0] / 2940), max(0.0, p0[1] / 1604),
            min(1.0, p1[0] / 2940), min(1.0, p1[1] / 1604))


@etapa
def ceu():
    editor.volta_ao_nivel()
    A.gesto("abrir_niveis", "g08a", (0, 0), lambda: editor.abre_niveis(), espera=1.8)
    A.gesto("pintar_o_ceu", "g08", (0, 0),
            lambda: editor.cor_do_ceu(CEU, abrir=False), espera=2.0)
    editor.volta_ao_nivel()
    A.cap("p08_ceu")
    return True


@etapa
def jogador():
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    x, y = celula(*CEL_JOGADOR)
    editor.objeto_ou_abre(x, y); time.sleep(2)
    comum.abre_sprite()
    pacote, sub, lin, col = AC.SPRITES["Jogador"]
    comum.abre_grade_sprite(pacote, sub)
    A.cap("p09_grade")
    A.gesto("escolher_sprite", "g13", (0, 0),
            lambda: AC.poe_sprite("Jogador", so_clique=True), espera=2.0)
    clique(*comum.SPRITE_OK); time.sleep(2); nav.espera_parar(limite=15)
    A.cap("p10_jogador")
    fecha_painel_objeto(); time.sleep(1.5)
    return True


@etapa
def estrelas():
    editor.volta_ao_nivel(); comum.calibra_grade(16, 12)
    x, y = celula(*CEL_ESTRELA)
    clique(x, y); time.sleep(1.5)
    A.cap("p11_menu_da_estrela")
    editor.fecha_roda()
    A.gesto("clonar_a_estrela", "g46", (0, 0),
            lambda: clona(CEL_ESTRELA[0], CEL_ESTRELA[1], "Estrela", CLONES), espera=2.0)
    A.cap("p12_estrelas")
    return True


# ─────────────────────────────── mostrar ───────────────────────────────

def _toca_o_play():
    editor.volta_ao_nivel(); time.sleep(1.5)
    p = nav.acha_texto("play")
    if not p:
        raise RuntimeError("nao achei o botao Play (estou mesmo no editor?)")
    clique(*p)
    time.sleep(2.0)
    editor.exige_jogo()
    clique(1470, 620)


def _corre(seg):
    rs.tecla_baixo(124)
    time.sleep(seg)
    rs.tecla_cima(124)


@etapa
def jogue():
    editor.volta_ao_nivel(); time.sleep(1.5)
    p = nav.acha_texto("play")
    antes = A.cap("g07_a")
    comum.CLIQUES.clear()
    clique(*p); time.sleep(1.5)
    depois = A.cap("g07_b")
    A.reg("jogar", antes=antes, depois=depois, alvo=[int(p[0]), int(p[1])],
          botao="esq", clicado=True)
    editor.exige_jogo()
    achadas = _estrelas_no_jogo()
    print("   estrelas no jogo:", achadas, flush=True)
    A.cap("p13_jogo")
    if len(achadas) < 4:
        raise RuntimeError(f"esperava 4 estrelas no jogo e achei {len(achadas)}: {achadas}")
    open("/tmp/_c12_estrelas.txt", "w").write(repr(achadas))
    editor.volta_ao_editor(); time.sleep(2)
    return True


@etapa
def prova():
    """Corre da esquerda para a direita e PROVA que as estrelas somem uma a uma."""
    antes = eval(open("/tmp/_c12_estrelas.txt").read())
    _toca_o_play()
    restantes = len(antes)
    serie = [restantes]
    for _ in range(24):
        # `corre_e_pula`: so a seta de andar, sem o pulo, nao moveu o boneco na
        # bancada (30 corridas, nenhum pixel). Em rajadas CURTAS, para o boneco
        # nao passar por cima das estrelas e sair da fase.
        rs.corre_e_pula(direcao=124, antes=0.05, segurando=0.2)
        n = len(_estrelas_no_jogo())
        serie.append(n)
        if n == 0:
            break
    A.cap("p14_prova")
    editor.exige_jogo()
    print(f"   estrelas restantes a cada corrida: {serie}", flush=True)
    if serie[-1] > restantes - 2:
        raise RuntimeError(f"o jogador correu e so pegou {restantes - serie[-1]} "
                           f"das {restantes} estrelas ({serie})")
    print(f"   PROVADO: das {restantes} estrelas, o jogador pegou {restantes - serie[-1]} "
          f"correndo da esquerda para a direita (serie {serie})", flush=True)
    editor.volta_ao_editor(); time.sleep(2)
    return True


@etapa
def lista_com_nome():
    nav.vai("https://flowlab.io/games/mine", espera=8); time.sleep(3)
    nav.fecha_dialogo()
    editor.espera_tela("my games", limite=25)
    txt = nav.texto_da_tela().lower()
    A.cap("p15_lista_nome")
    print("   cartao do alto:", txt[:160], flush=True)
    if "estrelas da noite" not in txt:
        raise RuntimeError("o nome do jogo novo nao aparece na lista")
    return True


@etapa
def compartilha():
    k = None
    for i in range(4):
        if _ids_da_lista(i) == _meu_id():
            k = i
            break
    if k is None:
        raise RuntimeError(f"o clone {_meu_id()} nao esta entre os 4 primeiros cartoes")
    pt = P(182 + 898 * (k % 2), 694 + 531 * (k // 2))
    clique(*pt); time.sleep(2.0)
    A.cap("p16_share")
    txt = nav.texto_da_tela().replace(" ", "")
    alvo = f"game/play/{_meu_id()}"
    if alvo not in txt:
        raise RuntimeError(f"o dialogo de compartilhar nao mostra {alvo}")
    copiar = P(1234, 348)               # o dialogo abre no CENTRO, onde quer que o cartao esteja
    def copia():
        clique(*copiar); time.sleep(1.5)
        return copiar
    subprocess.run(["pbcopy"], input=b"nada")
    A.gesto("copiar_o_link", "g47", copiar, copia, espera=1.0)
    A.cap("p17_copiado")
    colado = subprocess.run(["pbpaste"], capture_output=True, text=True).stdout.strip()
    print("   area de transferencia:", colado, flush=True)
    if not colado.endswith(f"/game/play/{_meu_id()}"):
        raise RuntimeError(f"o `Copy Link` nao copiou o endereco do jogo (copiou {colado!r})")
    clique(*P(1273, 857)); time.sleep(1.0)
    return True


@etapa
def abre_o_link():
    nav.vai(f"https://flowlab.io/game/play/{_meu_id()}", espera=10); time.sleep(3)
    txt = nav.texto_da_tela().lower()
    A.cap("p18_link")
    print("   pagina do link:", txt[:140], flush=True)
    if "estrelas da noite" not in txt:
        raise RuntimeError("a pagina do link nao mostra o nome do jogo")
    print(f"   PROVADO: o link https://flowlab.io/game/play/{_meu_id()} abre o jogo "
          f"'{NOME}'", flush=True)
    return True


def main():
    AC.main(sys.modules[__name__])


if __name__ == "__main__":
    main()
