#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A BANCADA: o mesmo curso, capturado num navegador que NAO e a tela dele.

   Por que existe: enquanto a captura rodava, eu dirigia o mouse e o teclado do
   sistema — e o Julio nao podia usar o proprio computador. Isso custava mais
   caro do que qualquer token. O `bancada/motor.mjs` sobe um Chrome de verdade
   posicionado fora da area visivel e manda clique e tecla pelo protocolo do
   navegador: a janela nao precisa de foco, e a tela fica livre.

   O truque que faz isso sair barato: a janela da bancada tem o MESMO tamanho
   da que eu fotografava (1470x802 com retina 2x = foto de 2940x1604). Toda
   coordenada ja medida — a grade do nivel, a paleta de cores, o OK do painel,
   os deslocamentos dos pinos — continua valendo sem recalibrar nada.

   Como ligar:
       node fonte/bancada/motor.mjs &          # sobe a bancada
       BANCADA=1 python3 fonte/cap4.py         # a captura usa ela

   Sem `BANCADA=1`, tudo continua funcionando como antes, pela tela.
"""
import json, os, sys, time, urllib.request, urllib.error

PORTA = int(os.environ.get("BANCADA_PORTA", "8765"))
BASE = f"http://127.0.0.1:{PORTA}"
AREA = {"id": 0, "nome": "bancada", "x": 0, "y": 0, "w": 1470, "h": 802, "camada": 0}


def ligada(limite=0.7):
    """A bancada esta de pe?"""
    try:
        with urllib.request.urlopen(BASE + "/endereco", timeout=limite):
            return True
    except Exception:
        return False


def _chama(rota, **kw):
    dados = json.dumps(kw).encode()
    req = urllib.request.Request(BASE + "/" + rota, data=dados,
                                 headers={"content-type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"bancada /{rota}: {e.read().decode()[:200]}")


# ─── de codigo de tecla do macOS para nome de tecla do navegador ───
# O mapa antigo era de codigo CRU, e era ele que nao sabia escrever '!' nem
# acento. Aqui o navegador recebe o NOME da tecla e digita de verdade.
TECLAS = {123: "ArrowLeft", 124: "ArrowRight", 125: "ArrowDown", 126: "ArrowUp",
          36: "Enter", 48: "Tab", 53: "Escape", 51: "Backspace", 49: " ",
          0: "a", 6: "z", 8: "c", 9: "v", 7: "x", 45: "n", 15: "r"}


def _nome_tecla(codigo, cmd=False, shift=False, alt=False, ctrl=False):
    nome = TECLAS.get(codigo)
    if nome is None:
        raise ValueError(f"a bancada nao sabe a tecla de codigo {codigo}")
    partes = []
    if cmd:   partes.append("Meta")
    if ctrl:  partes.append("Control")
    if alt:   partes.append("Alt")
    if shift: partes.append("Shift")
    partes.append(nome)
    return "+".join(partes)


def instala():
    """Troca as pecas de ENTRADA e CAPTURA de `rs` e `nav` pelas da bancada.

       O que NAO muda: o OCR, a procura por cor, e todas as aulas. Elas falam
       com `nav.captura`, `nav.clique_seguro`, `rs.tecla`… e continuam falando
       — so que do outro lado agora esta o navegador, e nao a tela."""
    import rs, nav
    from PIL import Image

    # A MARCA que `rs._exige_bancada_instalada` procura. Sem ela, qualquer
    # gesto com `BANCADA=1` no ambiente e sem estes remendos para na hora, em
    # vez de ir para a tela de verdade.
    rs._BANCADA_INSTALADA = True

    # ── captura ──
    def captura(arquivo=None, wid=None):
        # CAMINHO ABSOLUTO sempre. Quem salva a foto e o motor, que roda noutra
        # pasta: um caminho relativo como 'aula3/p17.png' ia parar em
        # fonte/bancada/aula3/, e a aula ficava sem a foto com um erro que
        # falava de arquivo inexistente, nao de pasta errada.
        arquivo = os.path.abspath(arquivo or "/tmp/_bancada.png")
        pasta = os.path.dirname(arquivo)
        if pasta:
            os.makedirs(pasta, exist_ok=True)
        _chama("foto", arquivo=arquivo)
        motivo = rs._quadro_cego(Image.open(arquivo).convert("RGB"))
        if motivo:
            raise rs.TelaCega(f"bancada: {motivo} — a pagina nao desenhou")
        return arquivo, 2.0

    nav.captura = lambda arquivo, wid=None: captura(arquivo, wid)
    nav.cap_tela = lambda J, arquivo: captura(arquivo)
    nav.cap_bruta = lambda J, arquivo, tentativas=8: captura(arquivo)
    rs.captura = lambda wid=None, arquivo=None: captura(arquivo, wid)

    # ── janela: a bancada e sempre a mesma area, na origem ──
    nav.janela = lambda titulo_esperado=None, tentativas=6: dict(AREA)
    nav._janela1 = lambda titulo_esperado=None: dict(AREA)
    nav.foca = lambda: _chama("titulo")["titulo"]
    rs.janelas = lambda dono=None: [dict(AREA)]
    rs.principal = lambda: dict(AREA)

    # ── navegacao ──
    nav.endereco = lambda: _chama("endereco")["url"]
    nav.titulo = lambda: _chama("titulo")["titulo"]
    nav.carregando = lambda: False

    def vai(url, espera=2.0):
        _chama("ir", url=url, espera=int(espera * 1000))
        nav.espera_parar()
        return nav.endereco()
    nav.vai = vai

    # O dialogo do Chrome chega ao motor como EVENTO e e aceito la. Aqui ele
    # deixa de existir — e com ele some a conferencia por OCR que nao lia os
    # botoes e achava a palavra do botao dentro da pergunta.
    nav.fecha_dialogo = lambda espera=1.5: None

    # ── mouse ──
    def clique_tela(x, y, duplo=False):
        _chama("clique", x=x * 2, y=y * 2, duplo=duplo)

    def clique_img(px, py, escala=None, janela=None, duplo=False):
        _chama("clique", x=px, y=py, duplo=duplo)

    rs.clique_tela = clique_tela
    rs.clique_img = clique_img
    rs.clique_lento = lambda x, y, hover=0.6, segura=0.18: _chama("lento", x=x * 2, y=y * 2)
    rs.clique_direito_img = lambda px, py, escala=2.0, janela=None: _chama(
        "clique", x=px, y=py, botao="right")

    def _evento_mouse(tipo, x, y, botao=None):
        # so o MOVER sobrevive: os demais viravam clique solto sem alvo
        _chama("mover", x=x * 2, y=y * 2)
    rs._evento_mouse = _evento_mouse

    def arrasta_img(px0, py0, px1, py1, escala=2.0, janela=None, passos=26):
        _chama("arrastar", x0=px0, y0=py0, x1=px1, y1=py1, passos=passos, segura=0.25)
    rs.arrasta_img = arrasta_img

    import blocos
    blocos.arrasta_devagar = lambda x0, y0, x1, y1, passos=45, segura=0.45: _chama(
        "arrastar", x0=x0, y0=y0, x1=x1, y1=y1, passos=passos, segura=segura)

    # ── teclado ──
    rs.tecla = lambda codigo, cmd=False, shift=False, alt=False, ctrl=False: _chama(
        "tecla", nome=_nome_tecla(codigo, cmd, shift, alt, ctrl))
    rs.tecla_rapida = lambda codigo, cmd=False, shift=False: _chama(
        "tecla", nome=_nome_tecla(codigo, cmd, shift))
    rs.segura_tecla = lambda codigo, segundos=1.0: _chama(
        "segura", nome=_nome_tecla(codigo), segundos=segundos)
    # digitar pelo navegador aceita o que o mapa de codigo cru nao aceitava:
    # pontuacao e ACENTO
    rs.digita_teclas = lambda texto: _chama("digita", texto=texto)
    rs.digita = lambda texto: _chama("digita", texto=texto)
    rs.corre_e_pula = lambda direcao=124, pulo=126, antes=0.25, segurando=0.45, depois=0.25: _chama(
        "duas", anda=TECLAS[direcao], pula=TECLAS[pulo],
        antes=antes, segurando=segurando, depois=depois)

    return True


def liga_se_pedido():
    """Chamado pelos modulos: liga a bancada se `BANCADA=1` e ela estiver de pe."""
    if os.environ.get("BANCADA") != "1":
        return False
    if not ligada():
        raise RuntimeError("BANCADA=1 mas o motor nao esta de pe — rode "
                           "`node fonte/bancada/motor.mjs &` antes")
    return instala()


if __name__ == "__main__":
    print("bancada de pe:", ligada())
