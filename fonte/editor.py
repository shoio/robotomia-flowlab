#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Entra e sai das telas do Flowlab: jogo novo, objeto novo, editor de
   comportamento. Cada passo confere onde chegou antes de seguir."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rs, nav

VERDE = (41, 168, 70)              # o botao "+ New Game", medido em 04-10


def botao_novo_jogo(arquivo=None, regiao=(0.6, 0.05, 1.0, 0.22)):
    """O `+ New Game` achado pela PROPRIEDADE da cor, nao pelo valor exato.

       O verde dele mudou de (99,173,97) para (41,168,70) entre uma noite e a
       outra, e a busca por cor com tolerancia 26 passou a nao achar nada: a
       captura parava no `nao achei nada da cor`. Procurar "verde forte" — G
       bem maior que R e que B — sobrevive a mudanca de tom.

       Procurar pelo TEXTO tambem nao serve: a lista esta cheia de jogos
       chamados `New Game`, e a leitura acha o titulo de um cartao primeiro.

       A FAIXA E ESTREITA de proposito (y de 5% a 22%, x de 60% para a
       direita). A faixa larga de antes funcionava com a conta vazia e passou a
       errar quando ela encheu: a miniatura "No Screenshot Yet" de um jogo sem
       captura e VERDE, e caiu dentro da busca. O botao vive sozinho na tira de
       cima, a direita — e e o verde mais a DIREITA de todos, que e o criterio
       que ficou no desempate."""
    import numpy as _np
    from PIL import Image as _I
    a = arquivo or nav.captura("/tmp/_ed_verde.png")[0]
    im = _np.asarray(_I.open(a).convert("RGB"), dtype=int)
    A, L = im.shape[0], im.shape[1]
    x0, y0, x1, y1 = (int(regiao[0]*L), int(regiao[1]*A),
                      int(regiao[2]*L), int(regiao[3]*A))
    rec = im[y0:y1, x0:x1]
    m = ((rec[:, :, 1] > 120) & (rec[:, :, 1] - rec[:, :, 0] > 40) &
         (rec[:, :, 1] - rec[:, :, 2] > 40))
    ys, xs = _np.nonzero(m)
    if len(xs) < 2000:
        return None
    # fico com o aglomerado mais A DIREITA: se alguma miniatura verde entrar na
    # faixa, a MEDIA de todos os pixels cai no meio do caminho entre ela e o
    # botao — num lugar onde nao ha nada para clicar
    perto = xs >= (xs.max() - 0.12 * (x1 - x0))
    xs, ys = xs[perto], ys[perto]
    return (int(xs.mean()) + x0, int(ys.mean()) + y0)


def _clica_novo_jogo():
    b = botao_novo_jogo()
    if not b:
        raise RuntimeError("nao achei o botao verde `+ New Game`")
    rs.clique_img(b[0], b[1], escala=2.0, janela=nav.janela())
    time.sleep(6)
    nav.espera_parar(limite=20)
    return b
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


def _barrinha(rotulo):
    """(x_esquerda, x_direita, y) da barrinha daquele rotulo, medida pela COR.

       A barra e um retangulo cinza claro sobre o painel escuro, na mesma
       altura do rotulo. Medir as duas pontas dela da as duas ancoras que
       faltavam: a esquerda e o MINIMO do controle e a direita e o MAXIMO."""
    import numpy as _np
    from PIL import Image as _I
    a, _ = nav.captura("/tmp/_ed_barra.png")
    p = nav.acha_texto(rotulo, arquivo=a, regiao=(0.45, 0.1, 1.0, 0.9))
    if not p:
        return None
    im = _np.asarray(_I.open(a).convert("RGB"), dtype=int)
    linha = im[p[1], :, :]
    # o trilho e cinza (canais proximos) e mais claro que o fundo do painel
    cinza = ((linha.max(axis=1) - linha.min(axis=1)) < 30) & (linha.max(axis=1) > 60)
    xs = _np.nonzero(cinza[p[0]:p[0] + 700])[0]
    if len(xs) < 50:
        return None
    return p[0] + int(xs.min()), p[0] + int(xs.max()), p[1]


def colunas_do_nivel():
    """Quantas colunas o nivel TEM, medidas na folha — sem passar pelo que eu
       pedi. Ate 32 colunas o editor mantem a casa em 64 px."""
    import comum
    volta_ao_nivel()
    f = comum.folha_do_nivel()
    if not f:
        return None
    return int(round((f[1] - f[0]) / 64.0))


def tamanho_do_nivel(colunas, tentativas=6):
    """Poe o nivel com `colunas` colunas, pelo painel Settings.

       O Flowlab nasce com 16x12 e vai ate 48x32. Isso nao e so o tamanho da
       folha: e o tamanho do JOGO — a pagina desenha o nivel inteiro, entao
       fase mais comprida sai com as pecas um pouco menores (medido: 32 px por
       casa com 16 colunas, 29,6 com 48).

       Tem de ser feito ANTES de montar a fase: alargar depois CENTRALIZA o que
       ja existe, e nenhuma coluna continua onde estava.

       DOIS INSTRUMENTOS. Quem POE e a barrinha (o valor cai onde o mouse
       desce); quem CONFERE e a FOLHA, que nao sabe o que eu pedi. E a posicao
       do clique nao e calculada, e APRENDIDA: medir o trilho pela cor me deu
       um trilho mais largo que o verdadeiro, e clicar no meio dele resultou em
       26 colunas quando eu pedia 32. Com dois pontos (clique, colunas) a reta
       sai sozinha.

       A ALTURA nao se toca: querer fase mais COMPRIDA nao e querer fase mais
       alta, e mexer no que nao precisa so cria chance de estragar — tentando
       ajusta-la por OCR eu a deixei em 14."""
    import comum
    medidos = []
    for k in range(tentativas):
        agora = colunas_do_nivel()
        if agora == colunas:
            print(f"   nivel com {colunas} colunas, conferido na folha", flush=True)
            return colunas
        p = nav.acha_texto("settings")
        if not p:
            raise RuntimeError("nao achei o Settings na barra de baixo")
        comum.clique(*p); time.sleep(3)
        b = _barrinha("width")
        if not b:
            raise RuntimeError("nao achei a barrinha de Width no painel")
        x0, x1, y = b
        if len(medidos) >= 2 and medidos[-1][1] != medidos[-2][1]:
            (xa, va), (xb, vb) = medidos[-2], medidos[-1]
            x = xa + (xb - xa) * (colunas - va) / float(vb - va)
        else:
            # A FAIXA DA BARRINHA E 4 A 48, nao 16 a 48. O minimo nao e o
            # tamanho padrao: o padrao e 16, mas o controle desce ate 4 —
            # conferido no painel. Eu calculava a fracao sobre 16..48, e por
            # isso pedir 32 colocava 26.
            frac = (colunas - 4) / 44.0 + 0.12 * len(medidos)
            x = x0 + (x1 - x0) * frac
        x = int(max(x0, min(x1, x)))
        comum.clique(x, y); time.sleep(1.0)
        c = nav.acha_texto("cancel", arquivo=nav.captura("/tmp/_ed_ok.png")[0],
                           regiao=(0.45, 0.6, 1.0, 0.95))
        if not c:
            raise RuntimeError("nao achei o Cancel do painel de Settings")
        comum.clique(c[0] + 182, c[1]); time.sleep(3.5)
        deu = colunas_do_nivel()
        print(f"   cliquei em {x} (trilho {x0}..{x1}) -> {deu} colunas", flush=True)
        if deu:
            medidos.append((x, deu))
    raise RuntimeError(f"pedi {colunas} colunas e a folha mede "
                       f"{colunas_do_nivel()} (cliques: {medidos})")


def cor_do_ceu(hexa):
    """Pinta o fundo do NIVEL com uma cor, pelo painel `Game Levels`.

       O campo fica ao lado do nome do nivel e nasce com `FFFFFF` — e e por
       isso que todo jogo do curso era branco de folha de papel. Eu fotografei
       esse painel varias vezes e nunca olhei o que era aquele campo.

       Devolve o ponto clicado, para o clipe da aula apontar para ele."""
    import comum
    p = nav.acha_texto("game levels")
    if not p:
        raise RuntimeError("nao achei o Game Levels na barra de baixo")
    comum.clique(*p); time.sleep(2.5)
    a, _ = nav.captura("/tmp/_ed_ceu.png")
    q = None
    for alvo in ("ffffff", "level 1"):
        q = nav.acha_texto(alvo, arquivo=a)
        if q:
            if alvo == "level 1":      # o campo da cor fica a direita do nome
                q = (q[0] + 240, q[1])
            break
    if not q:
        raise RuntimeError("nao achei o campo da cor no painel Game Levels")
    nav.clique_seguro(*q); time.sleep(0.8)
    rs.tecla(0, cmd=True); time.sleep(0.3)
    rs.digita_teclas(hexa); time.sleep(0.5)
    rs.tecla(36); time.sleep(1.8)                  # Enter
    return q


def jogo_novo():
    """Cria um jogo novo e abre o projeto vazio. Devolve o endereco do jogo."""
    nav.vai("https://flowlab.io/games/mine", espera=4)
    nav.fecha_dialogo()
    espera_tela("new game", "my games", limite=25)
    _clica_novo_jogo()
    # o seletor demora a desenhar; se nao vier, clico de novo uma vez
    try:
        espera_tela("empty project", limite=30)
    except RuntimeError:
        nav.fecha_dialogo()
        if botao_novo_jogo():
            _clica_novo_jogo()
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


def fecha_roda():
    """Dispensa a roda `Create / Cancel`, se ela estiver aberta.

       Ela nasce de um clique que chegou ao NIVEL — e, quando a mesa de blocos
       esta aberta, ela fica POR CIMA dela, bem no meio, justamente onde eu
       solto bloco. O arrasto cai na roda e o bloco nao nasce, sem nada dizer
       por que: a mensagem que sobrava era "a mesa nao mudou ali"."""
    import comum
    a, _ = nav.captura("/tmp/_ed_roda.png")
    txt = " ".join(t for t, *_ in rs.ocr_forte(a, psm="6")).lower()
    if "cancel" not in txt or "create" not in txt:
        return False
    p = nav.acha_texto("cancel", arquivo=a)
    if not p:
        return False
    comum.clique(*p); time.sleep(1.2)
    return True


def no_editor_de_blocos():
    """Estou com a mesa de blocos aberta? A palheta da esquerda denuncia."""
    return bool(na_tela("triggers", "behavior bundles", regiao=(0, 0, 0.16, 1.0)))


def volta_ao_nivel(limite=20):
    """Fecha o que estiver aberto por cima do nivel: a mesa de blocos e o
       painel do objeto. Serve para uma etapa COMECAR de um estado conhecido.

       Sem isto, repetir uma etapa que ja tinha aberto a mesa de blocos fazia o
       clique na casa cair dentro da MESA — e eu procurava um menu radial que
       nunca ia aparecer, por 20 s, tres vezes seguidas."""
    if no_editor_de_blocos():
        fecha_comportamentos()
        time.sleep(1.5)
    import comum
    for _ in range(4):
        a, _ = nav.captura("/tmp/_ed_nivel.png")
        txt0 = " ".join(t for t, *_ in rs.ocr_forte(a, psm="6")).lower()
        # o EDITOR DE DESENHO tambem fica por cima do nivel, e o OK dele nao e
        # o azul do painel do objeto: e o do canto de baixo a esquerda. Sem
        # isto, `volta_ao_nivel` clicava no lugar errado tres vezes e desistia
        # dizendo que o painel do objeto nao fechava — com o painel do objeto
        # nem aberto.
        # QUALQUER marca do editor de desenho serve: exigir duas palavras
        # fazia a deteccao depender de o OCR ler as duas, e numa captura ele
        # leu `Upload Download` e nao leu `Browse`.
        if "edit sprite" in txt0 and any(w in txt0 for w in
                                         ("browse", "upload", "download",
                                          "animation editor", "snap to grid")):
            comum.clique(*comum.SPRITE_OK)
            time.sleep(2.5); nav.espera_parar(limite=15)
            continue
        # o painel do objeto tem duas caras: a de cima ('edit sprite', Name,
        # Type) e a da FISICA ('Collision Shape', 'Density'). Fechar so pela
        # primeira deixava a fisica aberta, e o clique seguinte na casa caia
        # dentro dela — eu procurava um menu radial que nunca ia aparecer.
        if not (nav.acha_texto("edit sprite", arquivo=a) or
                nav.acha_texto("collision shape", arquivo=a)):
            return True
        comum.fecha_painel_objeto()
        time.sleep(1.0)
    raise RuntimeError("nao consegui fechar o painel do objeto")


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
    if not p and ("cancel" in texto or "delete" in texto):
        # O MENU ESTA ABERTO, so que o OCR nao le a metade de cima dele
        # ('Clone' e 'Edit', branco sobre o circulo escuro). 'Cancel' e
        # 'Delete', embaixo, ele le. Entao me ancoro no que foi LIDO e ando o
        # deslocamento medido ate o Edit — ancorar no ponto do clique seria
        # supor que o menu nasce sempre centrado nele.
        c = nav.acha_texto("cancel", arquivo=a)
        if c:
            p = (c[0], c[1] - 169)
        else:
            d = nav.acha_texto("delete", arquivo=a)
            if d:
                p = (d[0] + 169, d[1] - 169)
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
