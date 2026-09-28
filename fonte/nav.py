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

LISTA_JANELAS = '''tell application "Google Chrome"
 set saida to ""
 repeat with i from 1 to (count of windows)
  set b to bounds of window i
  set saida to saida & i & "\t" & (URL of active tab of window i) & "\t" & ¬
   ((item 3 of b) - (item 1 of b)) & "x" & ((item 4 of b) - (item 2 of b)) & linefeed
 end repeat
 return saida
end tell'''

LEVANTA = '''tell application "Google Chrome" to set index of window %d to 1'''


def osa(*linhas):
    cmd = []
    for l in linhas:
        cmd += ["-e", l]
    r = subprocess.run(["osascript"] + cmd, capture_output=True, text=True)
    return (r.stdout or "").strip(), (r.stderr or "").strip()


def foca():
    """Traz a janela do Flowlab para a frente e devolve o TITULO da aba.

       Escolhe a MAIOR janela com o Flowlab, nao a primeira: havia uma janela
       pequena (825x418) com o flowlab.io aberto que o sistema nem consegue
       fotografar. Eu dirigia ela pelo AppleScript e fotografava a grande —
       o URL dizia uma coisa e a imagem mostrava outra."""
    osa('tell application "Google Chrome" to activate')
    lista, _ = osa(LISTA_JANELAS)
    melhor, area = None, 0
    for linha in lista.splitlines():
        partes = linha.split("\t")
        if len(partes) < 3 or ALVO not in partes[1]:
            continue
        try:
            larg, alt = (int(v) for v in partes[2].lower().split("x"))
        except ValueError:
            continue
        if larg * alt > area and larg >= 900 and alt >= 500:
            melhor, area = int(partes[0]), larg * alt
    achou = "ok" if melhor else "nao"
    if melhor:
        osa(LEVANTA % melhor)
    if achou != "ok":
        osa('tell application "Google Chrome" to make new window',
            f'tell application "Google Chrome" to set URL of active tab of front window to "https://{ALVO}/"')
        time.sleep(5)
    time.sleep(0.8)
    t, _ = osa('tell application "Google Chrome" to get title of active tab of front window')
    return t


def janela(titulo_esperado=None, tentativas=6):
    """A janela do Flowlab, casada pelo titulo da aba.
       Enquanto a pagina troca, o titulo fica VAZIO por um instante e duas
       janelas passam a ter o mesmo titulo vazio: ai eu espero, em vez de
       chutar qual delas e — chutar seria clicar na janela errada."""
    for k in range(tentativas):
        try:
            return _janela1(titulo_esperado)
        except RuntimeError as e:
            if k == tentativas - 1:
                raise
            time.sleep(1.0)
            titulo_esperado = None


def _janela1(titulo_esperado=None):
    """Casa pelo TITULO quando ha titulo; quando nao ha, usa a ordem do sistema
       DEPOIS de levantar a janela.

       Paginas do Flowlab as vezes ficam com o titulo vazio (o /games/mine fica).
       Regra: foca() levanta a janela certa, e a lista do sistema vem da frente
       para o fundo — entao a primeira janela grande do Chrome e ela. O titulo,
       quando existe, continua valendo como conferencia."""
    t = titulo_esperado
    if t is None:
        t = foca()
    c = [j for j in rs.janelas(APP) if j["camada"] == 0 and j["w"] > 600 and j["h"] > 400]
    if not c:
        raise RuntimeError("nenhuma janela de conteudo do Chrome")
    if t and t.strip():
        iguais = [j for j in c if j["nome"].strip() == t.strip()]
        if len(iguais) == 1:
            return iguais[0]
        if len(iguais) > 1:
            raise RuntimeError(f"{len(iguais)} janelas do Chrome com o titulo {t!r} — "
                               "nao da para saber qual eu estaria clicando")
    # sem titulo: a da frente, depois de foca(). Confiro que o Chrome esta na
    # frente — senao 'a primeira' seria a janela de outro app.
    frente, _ = osa('tell application "System Events" to get name of first '
                    'process whose frontmost is true')
    if frente.strip() != "Google Chrome":
        raise RuntimeError(f"o app na frente e {frente!r}, nao o Chrome")
    return c[0]


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
    """Captura o que esta NA TELA na area da janela — inclui dialogo do Chrome."""
    J = janela(titulo())
    if wid:
        return rs.captura(wid, arquivo)
    for k in range(6):
        try:
            return cap_tela(J, arquivo)
        except rs.TelaCega:
            osa('tell application "Google Chrome" to activate')
            time.sleep(0.6 + 0.3 * k)
    return cap_tela(J, arquivo)


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


def cap_tela(J=None, arquivo="/tmp/_nav_tela.png"):
    """Captura o RETANGULO da tela onde a janela esta — nao a janela.

       Por que: o Chrome desenha os dialogos ('Sair do site? As alteracoes
       podem nao ser salvas') em cima da pagina, numa camada que a captura POR
       JANELA nao enxerga. Eu passei quase uma hora vendo a tela 'congelada'
       enquanto um dialogo invisivel para mim segurava a navegacao."""
    import Quartz
    J = J or janela()
    rect = Quartz.CGRectMake(J["x"], J["y"], J["w"], J["h"])
    img = Quartz.CGWindowListCreateImage(rect, Quartz.kCGWindowListOptionOnScreenOnly,
                                         Quartz.kCGNullWindowID, Quartz.kCGWindowImageDefault)
    if img is None:
        raise RuntimeError("nao consegui capturar a area da janela")
    W, H = Quartz.CGImageGetWidth(img), Quartz.CGImageGetHeight(img)
    dados = bytes(Quartz.CGDataProviderCopyData(Quartz.CGImageGetDataProvider(img)))
    im = Image.frombuffer("RGBA", (W, H), dados, "raw", "BGRA",
                          Quartz.CGImageGetBytesPerRow(img), 1).convert("RGB")
    motivo = rs._quadro_cego(im)
    if motivo:
        raise rs.TelaCega(f"area da janela: {motivo}")
    im.save(arquivo)
    return arquivo, (W / J["w"]) if J["w"] else 2.0


DIALOGOS = [("sair do site", "sair"), ("leave site", "leave"),
            ("sair da pagina", "sair"), ("reload site", "reload")]


def fecha_dialogo(espera=1.5):
    """Se houver um dialogo do Chrome na frente, clica no botao que segue em
       frente e devolve qual era. Devolve None se nao havia nenhum."""
    J = janela()
    a, _ = cap_tela(J, "/tmp/_nav_dlg.png")
    texto = " ".join(t for t, *_ in rs.ocr_forte(a, psm="6")).lower()
    for pergunta, botao in DIALOGOS:
        if pergunta in texto:
            p = acha_texto(botao, arquivo=a)
            if p:
                rs.clique_img(p[0], p[1], escala=2.0, janela=J)
                time.sleep(espera)
                return pergunta
    return None
