#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Entra e sai das telas do Flowlab: jogo novo, objeto novo, editor de
   comportamento. Cada passo confere onde chegou antes de seguir."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rs, nav

VERDE = (99, 173, 97)              # o botao "+ New Game"
CENTRO_CANVAS = (1502, 831)        # meio da grade branca do nivel


# A BARRA DE BAIXO e quem diz em que tela estou: no editor ela traz
# 'Library / Game Levels / Layer / Settings'; na pagina do jogo, nao.
RODAPE = (0, 0.93, 1.0, 1.0)


def le_tela(regiao=None):
    """O texto da tela, lido de um jeito que aguenta a tela quase vazia.

       A leitura da tela INTEIRA volta vazia no editor do Flowlab: e uma
       imagem escura com pouquissimo texto, e o limiar do tesseract afunda.
       Isso me fez esperar 40s por uma palavra que estava la, duas vezes.
       Entao, alem da tela inteira, leio sempre a barra de baixo ampliada."""
    a, _ = nav.captura("/tmp/_ed_tela.png")
    txt = " ".join(t for t, *_ in rs.ocr_forte(a, regiao=regiao, psm="6")).lower()
    if regiao is None:
        rodape = " ".join(t for t, *_ in rs.ocr(a, regiao=RODAPE, psm="6", escala=2))
        txt = txt + " " + rodape.lower()
    return txt


def na_tela(*palavras, regiao=None):
    """Alguma dessas palavras esta na tela agora?"""
    txt = le_tela(regiao)
    return [p for p in palavras if p.lower() in txt]


def espera_tela(*palavras, limite=25, regiao=None):
    """Espera ATE alguma palavra aparecer. Devolve qual apareceu."""
    fim = time.time() + limite
    while time.time() < fim:
        achou = na_tela(*palavras, regiao=regiao)
        if achou:
            return achou[0]
        nav.fecha_dialogo()
        recupera()            # o 'Recover unsaved work' aparece DEPOIS do clique
        time.sleep(1.2)
    raise RuntimeError(f"esperei {limite}s e nenhuma de {palavras} apareceu na tela")


def jogo_novo():
    """Cria um jogo novo e abre o projeto vazio. Devolve o endereco do jogo."""
    nav.vai("https://flowlab.io/games/mine", espera=4)
    nav.fecha_dialogo()
    espera_tela("new game", "my games", limite=25)
    nav.clica_cor(VERDE, regiao=(0.5, 0.05, 1, 0.30), espera=6)
    # o seletor demora a desenhar; se nao vier, clico de novo uma vez
    try:
        espera_tela("empty project", limite=30)
    except RuntimeError:
        nav.fecha_dialogo()
        if na_tela("new game"):
            nav.clica_cor(VERDE, regiao=(0.5, 0.05, 1, 0.30), espera=6)
        espera_tela("empty project", limite=30)
    J = nav.janela()
    rs.clique_img(1272, 860, escala=2.0, janela=J)     # miniatura do Empty Project
    time.sleep(3); nav.espera_parar(limite=25)
    espera_tela("library", "play", limite=25)
    return nav.endereco()


def objeto_novo(x=None, y=None):
    """Clica na grade, escolhe Create e para no painel do objeto."""
    J = nav.janela()
    px, py = x or CENTRO_CANVAS[0], y or CENTRO_CANVAS[1]
    rs.clique_img(px, py, escala=2.0, janela=J)
    time.sleep(1.5)
    a, _ = nav.captura("/tmp/_ed_radial.png")
    p = nav.acha_texto("create", arquivo=a)
    if not p:
        raise RuntimeError("o menu radial nao abriu (nao vi 'Create')")
    rs.clique_img(p[0], p[1], escala=2.0, janela=J)
    time.sleep(3); nav.espera_parar(limite=20)
    espera_tela("behaviors", limite=20)
    return True


def abre_objeto(x=None, y=None):
    """Abre um objeto que JA existe no nivel: clique -> Edit."""
    J = nav.janela()
    px, py = x or CENTRO_CANVAS[0], y or CENTRO_CANVAS[1]
    rs.clique_img(px, py, escala=2.0, janela=J)
    time.sleep(1.5)
    a, _ = nav.captura("/tmp/_ed_radial2.png")
    p = nav.acha_texto("edit", arquivo=a)
    if not p:
        raise RuntimeError("o menu radial do objeto nao abriu (nao vi 'Edit')")
    rs.clique_img(p[0], p[1], escala=2.0, janela=J)
    time.sleep(2.5); nav.espera_parar(limite=20)
    recupera()
    espera_tela("behaviors", limite=20)
    return True


def recupera(escolha="recover"):
    """Responde ao 'Recover unsaved work' quando ele aparece."""
    a, _ = nav.captura("/tmp/_ed_rec.png")
    txt = " ".join(t for t, *_ in rs.ocr_forte(a, psm="6")).lower()
    if "recover unsaved" not in txt and "unsaved work" not in txt:
        return False
    # o titulo do dialogo tambem diz "Recover": o BOTAO e a ocorrencia de baixo
    achados = [(t, x, y, w, h) for t, x, y, w, h in rs.ocr_forte(a, psm="6")
               if escolha in t.strip().lower()]
    if not achados:
        return False
    t, x, y, w, h = max(achados, key=lambda i: i[2])
    rs.clique_img(x + w // 2, y + h // 2, escala=2.0, janela=nav.janela())
    time.sleep(2); nav.espera_parar(limite=15)
    return True


def abre_comportamentos():
    """Do painel do objeto para o editor de comportamento."""
    a, _ = nav.captura("/tmp/_ed_obj.png")
    p = nav.acha_texto("behaviors", arquivo=a)
    if not p:
        raise RuntimeError("nao achei o botao Behaviors")
    rs.clique_img(p[0], p[1], escala=2.0, janela=nav.janela())
    time.sleep(3); nav.espera_parar(limite=25)
    recupera()
    espera_tela("triggers", "behavior bundles", limite=25, regiao=(0, 0, 0.16, 1.0))
    return True


def fecha_comportamentos():
    """O OK do canto de baixo-esquerda do editor de comportamento."""
    J = nav.janela()
    rs.clique_img(160, 1560, escala=2.0, janela=J)
    time.sleep(2); nav.espera_parar(limite=15)
    return True


def objeto_ou_abre(x=None, y=None):
    """Clica na celula: se estiver vazia escolhe Create, se ja tiver objeto
       escolhe Edit. Serve para retomar uma etapa sem criar objeto duplicado."""
    J = nav.janela()
    px, py = x or CENTRO_CANVAS[0], y or CENTRO_CANVAS[1]
    rs.clique_img(px, py, escala=2.0, janela=J)
    time.sleep(1.5)
    a, _ = nav.captura("/tmp/_ed_radial3.png")
    texto = " ".join(t for t, *_ in rs.ocr_forte(a, psm="6")).lower()
    escolha = "edit" if "edit" in texto and "create" not in texto else "create"
    p = nav.acha_texto(escolha, arquivo=a)
    if not p:
        raise RuntimeError(f"o menu radial nao abriu (nao vi '{escolha}')")
    rs.clique_img(p[0], p[1], escala=2.0, janela=J)
    time.sleep(3); nav.espera_parar(limite=20)
    recupera()
    espera_tela("behaviors", limite=20)
    return escolha


def no_jogo():
    """Estou na PAGINA DO JOGO (nao no editor)?

       O Flowlab tem duas telas parecidas. No editor a barra de baixo diz
       'Library'; na pagina do jogo ela diz 'Editor / Details / Theme / Cover'.
       Medir no editor achando que se mede no jogo produz numero bonito e
       falso: as teclas vao para o editor e o objeto ANDA porque esta sendo
       arrastado."""
    vistas = na_tela("library", "game levels", "editor", "details")
    if "library" in vistas or "game levels" in vistas:
        return False
    return ("editor" in vistas) or ("details" in vistas)


def volta_ao_editor(limite=25):
    """Da pagina do jogo de volta para o editor."""
    if not no_jogo():
        return True
    p = nav.acha_texto("editor")
    if not p:
        raise RuntimeError("nao achei o botao Editor na pagina do jogo")
    rs.clique_img(p[0], p[1], escala=2.0, janela=nav.janela())
    time.sleep(4); nav.espera_parar(limite=20); nav.fecha_dialogo()
    espera_tela("library", "play", limite=limite)
    return True


def rejoga():
    """Reinicia o jogo: volta ao editor e aperta Play. Recarregar a pagina NAO
       serve — o mesmo endereco serve as duas telas e a recarga cai no editor."""
    volta_ao_editor()
    return joga()


def joga(limite=30):
    """Do editor para o jogo rodando, conferindo a TROCA DE TELA."""
    if no_jogo():
        return True
    p = nav.acha_texto("play")
    if not p:
        raise RuntimeError("nao achei o botao Play (estou mesmo no editor?)")
    rs.clique_img(p[0], p[1], escala=2.0, janela=nav.janela())
    time.sleep(5)
    nav.espera_parar(limite=20)
    nav.fecha_dialogo()
    fim = time.time() + limite
    while time.time() < fim:
        if no_jogo():
            return True
        nav.fecha_dialogo()
        time.sleep(1.5)
    raise RuntimeError("cliquei no Play e continuo no editor — nao vou medir daqui")


def exige_jogo():
    if not no_jogo():
        raise RuntimeError("estou no EDITOR, nao no jogo: qualquer medida daqui e mentira")
    return True
