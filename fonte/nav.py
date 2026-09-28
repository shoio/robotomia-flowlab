#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dirige o Google Chrome para capturar o Flowlab: navega, espera a pagina
   ASSENTAR, captura a janela e le por OCR.

   Por que nao um navegador automatizado separado: a conta do Flowlab esta
   logada no Chrome DELE. Um Chrome novo com perfil proprio entraria deslogado,
   e as capturas do curso tem de ser do editor de verdade — do mesmo jeito que
   as do curso de Roblox sao do Studio de verdade.

   Duas coisas que este arquivo nao faz, e que custaram caro no curso de
   Roblox:
   - nao supoe que a pagina carregou depois de um sleep: `espera_parar` compara
     quadros ate a tela ficar quieta;
   - nao escolhe a janela por 'a maior' nem por 'a primeira'. As duas listas de
     janelas do Chrome DISCORDAM (para o sistema a do Flowlab era a primeira,
     para o AppleScript a da frente era um PDF): eu navegaria numa e
     fotografaria a outra. A janela se casa pelo TITULO da aba."""
import subprocess, time, os, sys
import Quartz
from PIL import Image, ImageChops

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rs

APP = "Google Chrome"
ALVO = "flowlab.io"

ACHA_JANELA = '''tell application "Google Chrome"
 repeat with i from 1 to (count of windows)
  if URL of active tab of window i contains "%s" then
   set index of window i to 1
   return "ok"
  end if
 end repeat
 return "nao"
end tell'''


def osa(*linhas):
    cmd = []
    for l in linhas:
        cmd += ["-e", l]
    r = subprocess.run(["osascript"] + cmd, capture_output=True, text=True)
    return (r.stdout or "").strip(), (r.stderr or "").strip()


def foca():
    """Traz a janela do Flowlab para a frente e devolve o TITULO da aba."""
    osa('tell application "Google Chrome" to activate')
    achou, _ = osa(ACHA_JANELA % ALVO)
    if achou != "ok":
        osa('tell application "Google Chrome" to make new window',
            f'tell application "Google Chrome" to set URL of active tab of front window to "https://{ALVO}/"')
        time.sleep(5)
    time.sleep(0.8)
    t, _ = osa('tell application "Google Chrome" to get title of active tab of front window')
    return t


def janela(titulo_esperado=None):
    """A janela do Flowlab, casada pelo titulo da aba."""
    t = titulo_esperado or foca()
    c = [j for j in rs.janelas(APP) if j["camada"] == 0 and j["w"] > 600 and j["h"] > 400]
    if not c:
        raise RuntimeError("nenhuma janela de conteudo do Chrome")
    iguais = [j for j in c if j["nome"].strip() == t.strip()]
    if len(iguais) == 1:
        return iguais[0]
    if not iguais:
        raise RuntimeError(f"nenhuma janela do Chrome com o titulo {t!r} "
                           f"(vi {[j['nome'][:30] for j in c]})")
    raise RuntimeError(f"{len(iguais)} janelas do Chrome com o titulo {t!r} — "
                       "nao da para saber qual eu estaria clicando")


def cap_bruta(J, arquivo, tentativas=8):
    """Captura teimosa: logo depois de levantar a janela, o Chrome devolve um
       quadro PRETO por uns instantes (o servidor de janelas ainda nao redesenhou).
       Nao afrouxo o guarda de quadro cego — eu repito, e so desisto falando."""
    for k in range(tentativas):
        try:
            return rs.captura(J["id"], arquivo)
        except rs.TelaCega:
            if k == tentativas - 1:
                raise
            osa('tell application "Google Chrome" to activate')
            time.sleep(0.6 + 0.3 * k)


def endereco():
    out, _ = osa('tell application "Google Chrome" to get URL of active tab of front window')
    return out


def titulo():
    out, _ = osa('tell application "Google Chrome" to get title of active tab of front window')
    return out


def carregando():
    out, _ = osa('tell application "Google Chrome" to get loading of active tab of front window')
    return out.strip().lower() == "true"


def vai(url, espera=2.0):
    """Navega e espera a pagina parar de carregar E de se mexer."""
    foca()
    osa(f'tell application "Google Chrome" to set URL of active tab of front window to "{url}"')
    time.sleep(espera)
    for _ in range(40):
        if not carregando():
            break
        time.sleep(0.5)
    espera_parar()
    return endereco()


def captura(arquivo, wid=None):
    J = janela(titulo())
    if wid:
        return rs.captura(wid, arquivo)
    return cap_bruta(J, arquivo)


def espera_parar(limite=25.0, quieto=1.2, passo=0.4):
    """Espera a tela PARAR de mudar; devolve os segundos gastos.
       Quem mede o fim do carregamento e a propria imagem: o Flowlab desenha o
       editor bem depois de o 'loading' do Chrome ja ter acabado."""
    J = janela(titulo())
    time.sleep(0.5)                      # deixa o Chrome assentar depois de levantar
    inicio = time.time()
    ultimo, parado_desde = None, None
    while time.time() - inicio < limite:
        a, _ = cap_bruta(J, "/tmp/_nav_espera.png")
        im = Image.open(a).convert("L")
        im = im.resize((im.width // 4, im.height // 4))
        if ultimo is not None:
            dif = ImageChops.difference(im, ultimo)
            mudou = sum(1 for p in dif.getdata() if p > 18)
            if mudou < 40:
                parado_desde = parado_desde or time.time()
                if time.time() - parado_desde >= quieto:
                    return round(time.time() - inicio, 1)
            else:
                parado_desde = None
        ultimo = im
        time.sleep(passo)
    return limite


def texto_da_tela(regiao=None, limiar=None, psm="6"):
    a, _ = captura("/tmp/_nav_ocr.png")
    return " ".join(t for t, *_ in rs.ocr_forte(a, regiao=regiao, psm=psm))


def acha_texto(alvo, regiao=None, limiar=None, psm="6", arquivo=None):
    """(x, y) em pixels da imagem do primeiro texto que casa, ou None.
       Junta as palavras da mesma linha antes de comparar: o OCR quebra
       'My Games' em duas."""
    a = arquivo or captura("/tmp/_nav_ocr.png")[0]
    alvo = alvo.lower()
    itens = (rs.ocr(a, regiao=regiao, psm=psm, escala=2, limiar=limiar)
             if limiar is not None else rs.ocr_forte(a, regiao=regiao, psm=psm))
    linhas = {}
    for t, x, y, w, h in itens:
        linhas.setdefault(round(y / 14), []).append((x, t, y, w, h))
    for _, palavras in sorted(linhas.items()):
        palavras.sort()
        junto = " ".join(p[1] for p in palavras).lower()
        if alvo in junto:
            primeira = alvo.split()[0]
            for x, t, y, w, h in palavras:
                if primeira in t.lower():
                    return (x + w // 2, y + h // 2)
            x, t, y, w, h = palavras[0]
            return (x + w // 2, y + h // 2)
    # a leitura por linhas usa UMA escala; se nao achou, percorro a escada
    achado = rs.procura_forte(alvo, a, regiao=regiao, psm=psm)
    if achado:
        t, x, y, w, h = achado
        return (x + w // 2, y + h // 2)
    return None


def clica_texto(alvo, regiao=None, limiar=None, espera=1.2, psm="6"):
    p = acha_texto(alvo, regiao=regiao, limiar=limiar, psm=psm)
    if not p:
        raise RuntimeError(f"nao achei '{alvo}' na tela")
    J = janela(titulo())
    rs.clique_img(p[0], p[1], escala=2.0, janela=J)
    time.sleep(espera)
    espera_parar()
    return p


def olha(nome="/tmp/_olha.png", largura=1280):
    """Captura e devolve tambem uma copia reduzida, para eu OLHAR."""
    a, _ = captura(nome)
    im = Image.open(a)
    im.thumbnail((largura, largura))
    pequena = nome.replace(".png", "_s.png")
    im.save(pequena)
    return a, pequena


if __name__ == "__main__":
    t = foca()
    print("titulo :", t)
    print("janela :", janela(t))
    print("url    :", endereco())
    print("quieto :", espera_parar(), "s")


def acha_cor(rgb, tol=26, regiao=None, minimo=400, arquivo=None):
    """Acha o maior aglomerado de uma COR na tela e devolve (x, y, largura,
       altura) em pixels da imagem, ou None.

       Existe porque botao de site e texto BRANCO sobre cor: o OCR nao le nada
       ali (medido — 'New Game' em branco sobre verde deu lista vazia em quatro
       modos de segmentacao). A cor do botao, essa nao muda."""
    import numpy as _np
    a = arquivo or captura("/tmp/_nav_cor.png")[0]
    im = _np.asarray(Image.open(a).convert("RGB"), dtype=int)
    A, L = im.shape[0], im.shape[1]
    y0, x0 = 0, 0
    if regiao:
        fx0, fy0, fx1, fy1 = regiao
        x0, y0 = int(fx0 * L), int(fy0 * A)
        im = im[y0:int(fy1 * A), x0:int(fx1 * L)]
    mask = (_np.abs(im - _np.array(rgb)) <= tol).all(axis=2)
    if mask.sum() < minimo:
        return None
    ys, xs = _np.nonzero(mask)
    # o maior bloco: fico com o aglomerado em volta da mediana
    for _ in range(4):
        cx, cy = _np.median(xs), _np.median(ys)
        perto = (_np.abs(xs - cx) < 260) & (_np.abs(ys - cy) < 120)
        if perto.sum() < minimo:
            break
        xs, ys = xs[perto], ys[perto]
    return (int(xs.mean()) + x0, int(ys.mean()) + y0,
            int(xs.max() - xs.min()), int(ys.max() - ys.min()))


def clica_cor(rgb, tol=26, regiao=None, espera=1.5, minimo=400):
    p = acha_cor(rgb, tol=tol, regiao=regiao, minimo=minimo)
    if not p:
        raise RuntimeError(f"nao achei nada da cor {rgb} na tela")
    J = janela(titulo())
    rs.clique_img(p[0], p[1], escala=2.0, janela=J)
    time.sleep(espera)
    espera_parar()
    return p
