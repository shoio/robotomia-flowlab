#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Opera o editor de comportamentos do Flowlab: abre categoria, solta bloco na
   tela e LIGA fio entre dois pinos — conferindo cada gesto.

   Medido no editor de verdade (27-09-2026):
   - a palheta da esquerda e TEXTO: da para achar 'Always', 'Impulse',
     'Collision' por OCR, e arrastar dali para a tela funciona;
   - o bloco nasce com o canto de cima-esquerda quase no ponto onde eu solto;
   - cada pino tem um ROTULO ('out', 'x', 'y', 'hit') e a bolinha fica ~26 px
     (na imagem 2x) para fora da borda, na mesma altura do rotulo;
   - arrastar de bolinha a bolinha cria o fio.
"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rs, nav, comum
from PIL import Image

PALHETA = (0, 0, 0.115, 1.0)          # a coluna da esquerda, em fracao da tela
TELA = (0.12, 0.0, 1.0, 0.95)          # a area de trabalho dos blocos

# quanto a bolinha do pino fica fora da borda do bloco, em pixels da imagem 2x
FORA_ESQ, FORA_DIR = 27, 25

CATEGORIAS = ["Triggers", "Logic & Math", "Components", "Properties",
              "Text & Lists", "GUI", "Game Flow", "Mobile Device",
              "Multiplayer", "Behavior Bundles"]


class Bloco:
    # `tipo` e o nome do bloco NA PALHETA; `nome` e o que ele mostra na mesa.
    # Quase sempre sao o mesmo texto — mas o `Global Variable`, depois de
    # apontar para uma variavel, passa a se chamar pelo NOME DELA ('Recorde'),
    # e as tabelas de pinos (DESLOC/PORTAS) sao por TIPO. Sem esta separacao,
    # `liga_fixo` dizia "nao tenho o deslocamento do pino 'get' de 'Recorde'".
    def __init__(self, nome, x, y, confirmado=True, tipo=None):
        self.nome = nome
        self.tipo = tipo or nome
        self.x, self.y = x, y          # onde eu soltei (canto de cima-esquerda)
        # `confirmado` = este bloco foi LIDO na tela, nao suposto.
        #
        # Existe porque `solta` tinha uma saida de emergencia que, quando nao
        # conseguia achar o titulo, devolvia um Bloco nas coordenadas onde eu
        # tinha MIRADO. Na Aula 3 o Collision nunca nasceu — a mesa rolou, os
        # pixels perto do ponto mudaram, o guarda por pixel aprovou, e o
        # fantasma viajou ate `liga_fixo`, que arrastou de um pino de um bloco
        # que nao existe. O erro so apareceu tres gestos depois, no fio.
        self.confirmado = confirmado

    def __repr__(self):
        marca = "" if self.confirmado else " ?NAO-ACHADO"
        return f"<{self.nome} em ({self.x},{self.y}){marca}>"

    def exige_achado(self, para_que):
        """A porta do DANO: usar a coordenada de um bloco que ninguem viu."""
        if not self.confirmado:
            raise RuntimeError(
                f"ia {para_que} do bloco '{self.nome}', mas ele nunca foi achado "
                f"na mesa — a coordenada ({self.x},{self.y}) e so onde eu mirei. "
                "Solte o bloco de novo, ou confira se a mesa rolou.")

    def regiao(self, folga_esq=360, folga_dir=420, folga_cima=200, folga_baixo=300):
        """A caixa em volta do bloco, em fracao da imagem — para OCR local.

           Generosa de proposito: o bloco nasce CENTRADO no ponto onde eu solto,
           nao pelo canto. Com a caixa estreita eu procurava o titulo 'Destroyer'
           40 px a direita de onde ele estava e concluia que o bloco nao existia
           — e o retry soltava outro. Tres Destroyers empilhados."""
        J = nav.janela(nav.titulo())
        L, A = J["w"] * 2, J["h"] * 2
        return (max(0, self.x - folga_esq) / L, max(0, self.y - folga_cima) / A,
                min(1.0, (self.x + folga_dir) / L), min(1.0, (self.y + folga_baixo) / A))

    def pino(self, rotulo, lado, arquivo=None):
        """(x, y) da BOLINHA do pino, em pixels da imagem.
           lado='dir' para saida, 'esq' para entrada."""
        self.exige_achado(f"ler o pino '{rotulo}'")
        a = arquivo or nav.captura("/tmp/_bl_pino.png")[0]
        alvo = rotulo.lower()
        cands, lidos = [], []
        # o rotulo do pino e texto PEQUENO e claro sobre escuro: leio ampliado e
        # binarizado, e aceito leitura truncada ('out' volta como 'ou')
        for esc, lim in ((3, 90), (3, None), (4, 110), (2, 90)):
            itens = rs.ocr(a, regiao=self.regiao(), psm="6", escala=esc, limiar=lim)
            lidos += [i[0] for i in itens]
            for t, x, y, w, h in itens:
                cru = t.strip().lower()
                # o OCR cola a BOLINHA no rotulo: 'start' volta como '@/start',
                # 'reset' como '@jreset'. Comparo so as letras, e anoto se veio
                # sujeira na frente — porque ai a caixa ja inclui a bolinha e o
                # deslocamento para fora seria para o lugar errado.
                so_letras = "".join(c for c in cru if c.isalpha())
                sujo = bool(cru) and not cru[0].isalpha()
                if not so_letras:
                    continue
                if so_letras == alvo or (len(so_letras) >= 2 and alvo.startswith(so_letras)) \
                        or (len(alvo) >= 2 and so_letras.startswith(alvo)):
                    cands.append((so_letras, x, y, w, h, sujo))
            if cands:
                break
        if not cands:
            raise RuntimeError(f"nao achei o pino '{rotulo}' no bloco {self.nome} "
                               f"(li {lidos[:14]})")
        # com pinos repetidos (o Impulse tem tres 'out'), o de cima e o primeiro
        cands.sort(key=lambda c: c[2])
        t, x, y, w, h, sujo = cands[0]
        if lado == "dir":
            return (x + w + (6 if sujo else FORA_DIR), y + h // 2)
        return (x + 8 if sujo else x - FORA_ESQ, y + h // 2)


def abre_categoria(nome):
    """Abre a categoria da palheta, se ela ja nao estiver aberta."""
    p = nav.acha_texto(nome.lower(), regiao=PALHETA)
    if not p:
        raise RuntimeError(f"nao achei a categoria '{nome}' na palheta")
    J = nav.janela(nav.titulo())
    rs.clique_img(p[0], p[1], escala=2.0, janela=J)
    time.sleep(1.2)
    return True


# O texto dos itens da palheta comeca por volta de x=70 (antes vem o icone) e
# acaba antes de x=330. Ponto fora dessa faixa nao e o item: e o icone, a
# beirada, ou uma leitura que juntou a linha errada.
PALHETA_X = (62, 330)


def _ponto_de_item(p):
    """O ponto esta mesmo sobre o TEXTO de um item da palheta?"""
    return bool(p) and PALHETA_X[0] <= p[0] <= PALHETA_X[1]


def item_palheta(nome, tentativas=3):
    """(x, y) do item da palheta, abrindo categoria se precisar.

       CONFERE a faixa do x. Medido: a mesma chamada devolveu (115,474) — em
       cima do texto — e (42,1116), que e o icone na beirada. Arrastar do ponto
       errado nao da erro: ele arrasta a PALHETA, o bloco nao nasce, e a falha
       aparece como "a mesa nao mudou ali" — que foi o que me fez procurar a
       causa na mesa, no fundo, no motor e no ponto de soltura durante horas."""
    for k in range(tentativas):
        p = nav.acha_texto(nome.lower(), regiao=PALHETA)
        if _ponto_de_item(p):
            return p
        if p:
            # leu o nome, mas num x que nao e o do item: insiste, que a proxima
            # leitura costuma vir limpa
            time.sleep(0.8)
            p2 = nav.acha_texto(nome.lower(), regiao=PALHETA)
            if _ponto_de_item(p2):
                return p2
        if k == 0:
            # a palheta e sanfona: abrir uma categoria fecha a outra. Entao
            # percorro TODAS, nao um punhado escolhido a dedo — foi assim que
            # 'Timer' (que mora em Triggers) sumiu de uma lista com cinco nomes.
            for cat in CATEGORIAS:
                try:
                    abre_categoria(cat)
                except RuntimeError:
                    continue
                p = nav.acha_texto(nome.lower(), regiao=PALHETA)
                if p:
                    return p
        time.sleep(0.8)
    raise RuntimeError(f"o bloco '{nome}' nao aparece na palheta")


# O CONTEXTO DA MESA, para poder RECARREGAR entre um bloco e outro.
#
# Medido, e e a restricao mais cara que o Flowlab me impos: **so o PRIMEIRO
# arrasto da palheta depois de carregar a pagina funciona**. O segundo nao cai,
# e dali em diante a mesa nao aceita mais nada da palheta — embora continue
# aceitando mover bloco que ja esta nela e desfazer com cmd+Z.
#
# Isso explica a sequencia que me confundiu por horas: a captura punha os tres
# blocos de uma etapa (cada um numa mesa recem-aberta), e a etapa seguinte, que
# precisa de dois blocos na MESMA mesa, so conseguia o primeiro. E explica por
# que "repetir a etapa" as vezes resolvia: a repeticao vinha depois de uma
# navegacao.
CONTEXTO = {"url": None, "celula": None, "soltou": 0}


def contexto(url=None, celula=None):
    """Diz ao `solta` como voltar a esta mesa depois de recarregar a pagina."""
    if url:
        CONTEXTO["url"] = url
    if celula:
        CONTEXTO["celula"] = tuple(celula)
    CONTEXTO["soltou"] = 0
    return CONTEXTO


def _recarrega_e_reabre():
    """SALVA, recarrega a pagina e volta para a mesma mesa de blocos.

       O `fecha_comportamentos` (o OK azul da mesa) e o que COMMITA os blocos.
       Sem ele, o recarregamento DESCARTA tudo o que foi solto desde que a mesa
       abriu — e foi exatamente isso que o meu proprio conserto causou: eu
       soltava o `Collision`, recarregava para poder soltar o `RestartGame`, e
       o recarregamento levava o `Collision` embora. Os dois blocos "sumiam" e
       eu procurava a causa no gesto do fio, que estava certo o tempo todo."""
    import editor as _ed, comum as _cm
    if not (CONTEXTO["url"] and CONTEXTO["celula"]):
        return False
    _ed.fecha_comportamentos(); time.sleep(2.5)      # OK: commita os blocos
    _cm.fecha_painel_objeto(); time.sleep(1.5)
    nav.vai(CONTEXTO["url"], espera=10)
    time.sleep(2)
    _ed.recupera()
    _ed.volta_ao_nivel()
    _cm.calibra_grade(16, 12)
    cx, cy = CONTEXTO["celula"]
    _ed.objeto_ou_abre(cx, cy)
    _ed.abre_comportamentos()
    time.sleep(2.5)
    _ed.recupera()
    _ed.fecha_roda()
    CONTEXTO["soltou"] = 0
    return True


def solta(nome, x, y, tentativas=3, titulo=None, exige_titulo=True, regiao=None):
    """Arrasta um bloco da palheta para (x, y) e CONFERE que ele nasceu ali.

       A conferencia e por PIXEL, nao por leitura do titulo. Ler o titulo
       falhava de dois jeitos: num recorte pequeno de tela escura o tesseract
       volta lixo, e o painel de ajustes — que o proprio arrasto lento abre ao
       terminar com uma pressao demorada — cobria a mesa e fazia o OCR ler
       'Help / Note'. Nos dois casos eu dava por falhado um bloco que tinha
       nascido certo, desfazia e tentava de novo: tres pacotes empilhados.

       O invariante e simples: ONDE EU SOLTEI, a mesa tem de ter mudado.

       `regiao` estreita a leitura do titulo. Ele e obrigatorio quando a mesa
       ja tem OUTRO bloco do mesmo nome: `acha_bloco` devolve o PRIMEIRO que
       achar, e sem recorte o segundo `Keyboard` de uma mesa devolve a
       coordenada do primeiro — os fios iriam todos para o bloco errado, sem
       erro nenhum na tela."""
    import numpy as _np
    for k in range(tentativas):
        import editor as _ed
        # UM BLOCO POR CARREGAMENTO: se ja soltei nesta pagina, recarrego antes
        # de tentar o proximo. Sem isso o segundo bloco de uma mesa nunca nasce.
        # RECARREGAR E ULTIMO RECURSO, nao rotina.
        #
        # Eu cheguei a recarregar a pagina antes de CADA bloco, convencido de
        # que o Flowlab so aceitava um arrasto da palheta por carregamento.
        # Esse modelo era errado: o que falhava era o PONTO DE ORIGEM do
        # arrasto — `item_palheta` devolvia (42,1116), o icone na beirada, em
        # vez de (115,474), o texto do item. Arrastar do ponto errado arrasta a
        # PALHETA, o bloco nao nasce, e o erro sai como "a mesa nao mudou ali",
        # apontando para o destino quando o defeito estava na origem.
        #
        # Com a guarda de faixa no `item_palheta`, o arrasto normal funciona.
        # O recarregamento fica como recuperacao da ULTIMA tentativa, que custa
        # 12 segundos e so se paga quando tudo o mais falhou.
        if k == tentativas - 1 and CONTEXTO["url"]:
            print(f"   [solta {nome}] ultima tentativa: recarregando a pagina",
                  flush=True)
            print(f"   [solta {nome}] recarregou? {_recarrega_e_reabre()}",
                  flush=True)
        _ed.fecha_roda()          # a roda Create/Cancel tapa o meio da mesa
        antes, _ = nav.captura("/tmp/_bl_antes_solta.png")
        p = item_palheta(nome)
        # ARRASTO LENTO sempre: o rapido nao pega os pacotes de
        # `Behavior Bundles` — a mesa ficava vazia e a captura parava ali.
        #
        # E a PRESSAO CRESCE a cada tentativa. Medido: com 0,45 s de pressao
        # antes de mover, a palheta do Flowlab nao registra o arrasto — a mesa
        # fica igual, sem um erro em lugar nenhum. Com 1,2 s o mesmo gesto, do
        # mesmo ponto, para o mesmo alvo, solta o bloco. Era por isso que o
        # Collision da Aula 3 nunca nascia: nao era o ponto, era o TEMPO. Um
        # numero fixo aqui e aposta; escalar e medida.
        espera = (0.6, 1.2, 2.0)[min(k, 2)]
        print(f"   [solta {nome} #{k}] palheta={p} -> ({x},{y}) pressao={espera}",
              flush=True)
        arrasta_devagar(p[0], p[1], x, y, passos=90, segura=espera)
        time.sleep(1.2)
        fecha_ajustes()          # o arrasto lento costuma abrir os ajustes
        time.sleep(0.6)
        dep, _ = nav.captura("/tmp/_bl_dep_solta.png")
        A = _np.asarray(Image.open(antes).convert("L"), dtype=int)
        B = _np.asarray(Image.open(dep).convert("L"), dtype=int)
        y0, y1 = max(0, y - 160), min(A.shape[0], y + 220)
        x0, x1 = max(0, x - 220), min(A.shape[1], x + 320)
        mudou = int((_np.abs(A[y0:y1, x0:x1] - B[y0:y1, x0:x1]) > 30).sum())
        print(f"   [solta {nome} #{k}] mudou {mudou} px (precisa > 3000)",
              flush=True)
        if mudou > 3000:
            try:
                return acha_bloco(titulo or nome, regiao=regiao or TELA)
            except RuntimeError:
                # A MUDANCA DE PIXEL NAO BASTA quando o bloco vai levar FIO.
                #
                # Desde que a aula pinta o ceu, o fundo da mesa de blocos e
                # azul-acinzentado em vez de quase preto, e a conta de "mudou
                # perto de onde soltei" passa com o ruido do fundo. O bloco
                # nao nascia, o guarda aprovava, e so la na frente o fantasma
                # era barrado. Para quem precisa de pino, o titulo LIDO e a
                # unica prova que vale: desfaco e tento de novo.
                if exige_titulo and k < tentativas - 1:
                    rs.tecla(6, cmd=True)       # desfaz o que quer que tenha mudado
                    time.sleep(1.0)
                    continue
                # NAO consegui ler o titulo. Isso e normal para os pacotes de
                # `Behavior Bundles`, cujo nome o OCR nao pega — e eles nunca
                # tem fio ligado. Devolvo o bloco MARCADO: quem for usar a
                # coordenada dele (pino, ajustes) reprova na hora, em vez de
                # arrastar no vazio tres gestos depois.
                print(f"   (!) soltei '{nome}' em ({x},{y}) e nao consegui LER "
                      "o titulo na mesa", flush=True)
                return Bloco(titulo or nome, x, y, confirmado=False)
        # so desfaz quando NADA mudou — desfazer um bloco que nasceu e o que
        # empilhava copias
        rs.tecla(6, cmd=True)
        time.sleep(1.0)
    # GUARDA AS DUAS FOTOS DA ULTIMA TENTATIVA. Sem isto, a proxima captura
    # sobrescreve `/tmp/_bl_*_solta.png` e a falha vira ghost: eu sabia que o
    # bloco nao nasceu e nao tinha como ver o que havia na tela na hora.
    import shutil as _sh
    guardadas = []
    for orig, dest in (("/tmp/_bl_antes_solta.png", f"/tmp/falhou_{nome.replace(' ', '_')}_antes.png"),
                       ("/tmp/_bl_dep_solta.png",   f"/tmp/falhou_{nome.replace(' ', '_')}_depois.png")):
        if os.path.exists(orig):
            _sh.copy(orig, dest); guardadas.append(dest)
    raise RuntimeError(f"soltei '{nome}' em ({x},{y}) e a mesa nao mudou ali"
                       + (f" — fotos: {', '.join(guardadas)}" if guardadas else ""))


def liga(origem, pino_saida, destino, pino_entrada):
    """Liga saida -> entrada e CONFERE que o fio existe.
       A prova e a propria imagem: comparo o caminho entre os dois pinos antes
       e depois; um fio branco muda pixels no meio do caminho."""
    J = nav.janela(nav.titulo())
    a_antes, _ = nav.captura("/tmp/_bl_antes.png")
    p1 = pino_por_nome(origem, pino_saida, "dir")
    p2 = pino_por_nome(destino, pino_entrada, "esq")
    # duas tentativas: saida->entrada e, se nao pegar, entrada->saida
    for ida, (a, b) in enumerate(((p1, p2), (p2, p1))):
        arrasta_devagar(a[0], a[1], b[0], b[1])
        time.sleep(0.8)
        a_dep, _ = nav.captura("/tmp/_bl_depois.png")
        if _mudou_no_caminho(a_antes, a_dep, p1, p2) or _mudou_perto(a_antes, a_dep, p2):
            return True
    raise RuntimeError(f"liguei {origem.nome}.{pino_saida} -> "
                       f"{destino.nome}.{pino_entrada} e nenhum fio apareceu")


def _mudou_no_caminho(antes, depois, p1, p2, raio=70, minimo=25):
    """Mudou alguma coisa no meio do caminho entre os dois pinos?"""
    A = Image.open(antes).convert("L")
    B = Image.open(depois).convert("L")
    mx, my = (p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2
    cx0, cy0 = max(0, mx - raio), max(0, my - raio)
    caixa = (cx0, cy0, min(A.width, mx + raio), min(A.height, my + raio))
    a, b = A.crop(caixa), B.crop(caixa)
    dif = sum(1 for x, y in zip(a.getdata(), b.getdata()) if abs(x - y) > 30)
    return dif >= minimo


def ok():
    """Fecha o editor de comportamentos pelo botao OK (canto de baixo-esquerda)."""
    J = nav.janela(nav.titulo())
    rs.clique_img(160, 1560, escala=2.0, janela=J)
    time.sleep(2.0)
    nav.espera_parar(limite=15)
    return True


def acha_todos(nome, regiao=TELA, tipo=None):
    """TODOS os blocos com este titulo na mesa, de cima para baixo.

       Existe porque a mesa ANDA: cada arrasto da palheta recarrega a pagina, e
       o editor recentra os blocos. Fileira em fracao da tela (`_na_fila`)
       deixa de valer depois de alguns arrastos, e o `acha_bloco` sozinho
       devolve sempre o PRIMEIRO de dois blocos de mesmo nome — os dois
       `Timer` de uma mesa, por exemplo. Com a lista, quem escolhe e a ORDEM
       na tela, que e o que a crianca ve.

       Devolve [] quando nao ha nenhum."""
    a, _ = nav.captura("/tmp/_bl_todos.png")
    alvo = nome.lower()
    for escala, limiar in rs.ESCADA:
        achados = []
        itens = rs.ocr(a, regiao=regiao, psm="6", escala=escala, limiar=limiar)
        for junto, palavras in rs._por_linha(itens):
            i = junto.find(alvo)
            while i >= 0:
                fim = i + len(alvo)
                antes_ok = i == 0 or not junto[i - 1].isalnum()
                depois_ok = fim >= len(junto) or not junto[fim].isalnum()
                if antes_ok and depois_ok:
                    t, x, y, w, h = rs.palavras_do_trecho(
                        palavras, junto, junto[i:fim])[0]
                    achados.append(Bloco(nome, x, y + h // 2, tipo=tipo))
                i = junto.find(alvo, i + 1)
        if achados:
            return sorted(achados, key=lambda b: (b.y, b.x))
    return []


def acha_bloco(nome, regiao=TELA, tentativas=3, tipo=None):
    """Acha um bloco JA na tela pelo titulo e devolve um Bloco posicionado.

       Guardar a coordenada onde eu soltei nao serve: qualquer zoom, rolagem ou
       arrasto move tudo, e eu continuaria procurando o pino no lugar velho.
       O titulo do bloco e o endereco estavel."""
    for k in range(tentativas):
        a, _ = nav.captura("/tmp/_bl_acha.png")
        achado = rs.procura_forte(nome, a, regiao=regiao, psm="6", exato=True)
        if achado:
            t, x, y, w, h = achado
            return Bloco(nome, x, y + h // 2, tipo=tipo)
        time.sleep(0.8)
    raise RuntimeError(f"nao achei o bloco '{nome}' na tela")


# A ORDEM dos pinos de cada bloco, de cima para baixo. Lida uma vez na tela e
# guardada aqui: o rotulo e texto minusculo e o OCR erra: 'start' virava
# '@/start', 'reset' virava '@jreset' e as vezes sumia. A bolinha, essa e um
# circulo claro — geometria, nao leitura.
PORTAS = {
    "Emitter": {"esq": ["angle", "emit"], "dir": ["out"]},
    "Always":    {"esq": [],                       "dir": ["out"]},
    "Once":      {"esq": [],                       "dir": ["out"]},
    "Timer":     {"esq": ["delay", "reset", "start"], "dir": ["out", "done"]},
    "Impulse":   {"esq": ["x", "y", "forward"],    "dir": ["out", "out2", "out3"]},
    "Destroyer": {"esq": ["in"],                   "dir": ["out"]},
    "Collision": {"esq": [],                       "dir": ["hit"]},
    "Keyboard":  {"esq": [],                       "dir": ["up", "down"]},
    "Label":     {"esq": ["text", "alpha", "x", "y"],
                  "dir": ["text", "alpha", "x", "y"]},
    "Random":    {"esq": ["min", "max", "new"],    "dir": ["out"]},
    "Position":  {"esq": ["x", "y", "maisx", "maisy"], "dir": ["x", "y"]},
    # MEDIDOS com `mede_pinos` no prototipo 3155726 (Aula 8).
    "Global Variable": {"esq": ["set", "get", "mais"], "dir": ["out"]},
    # MEDIDOS com `mede_pinos` no prototipo 3166005 (Aula 9).
    "Object Variable": {"esq": ["set", "get", "mais"], "dir": ["out"]},
    "LoadLevel": {"esq": ["go", "get"], "dir": ["out", "out2"]},
    "MouseClick": {"esq": [], "dir": ["down", "up", "over", "out"]},
    "Proximity": {"esq": ["dist", "check"], "dir": ["x", "y", "miss"]},
    "PointAt":   {"esq": ["x", "y"],        "dir": ["rot"]},
    "Expression": {"esq": ["A", "B", "eval"], "dir": ["out"]},
    "Bar":       {"esq": ["value"],         "dir": ["out"]},
    "Switch":    {"esq": ["off", "on", "in"],      "dir": ["out"]},
    # Aula 11, MEDIDOS com `mede_pinos` no prototipo 3166105.
    "SoundEffect": {"esq": ["play", "pause", "stop", "vol"],
                    "dir": ["playing", "pause", "stop", "vol", "done"]},
    "Animation": {"esq": ["start", "stop", "goto"], "dir": ["play", "done", "goto"]},
    "Blending":  {"esq": ["mode"], "dir": ["out"]},
    # ⚠️ `Once`, `Impulse` e `Label` ESTAVAM REPETIDOS AQUI, e em Python a
    # segunda chave apaga a primeira sem avisar. As que venciam eram as
    # escritas de cabeca: o `Label` ficava com `text/show/hide`, quando na tela
    # ele tem `text/alpha/x/y` dos DOIS lados, e o `Impulse` perdia duas
    # saidas. As medidas estao acima; estas foram apagadas, e a
    # `prova_tabela_sem_duplicata` passa a reprovar o build se voltarem.
    "Number":    {"esq": ["in"],                   "dir": ["out"]},
    "Mailbox":   {"esq": [],                       "dir": ["out"]},
    "Message":   {"esq": ["send"],                 "dir": ["done"]},
    "Filter":    {"esq": ["set", "in"],            "dir": ["pass", "fail"]},
    "Spawn":     {"esq": ["spawn"],                "dir": ["out"]},
    "Sound":     {"esq": ["play", "stop"],         "dir": ["done"]},
    "Camera":    {"esq": ["set x", "set y", "move x", "move y", "zoom",
                          "rotate"],               "dir": []},
}


def bolinhas(bloco, folga=(70, 620, 60, 340), claro=185, raio=(3, 11)):
    """As BOLINHAS dos pinos de um bloco, separadas em ('esq', 'dir').

       Acha aglomerados claros e pequenos na caixa do bloco e agrupa por
       coluna: a coluna mais a esquerda e a das entradas, a mais a direita a
       das saidas. Devolve listas ordenadas de cima para baixo."""
    import numpy as _np
    a, _ = nav.captura("/tmp/_bl_dots.png")
    im = _np.asarray(Image.open(a).convert("L"), dtype=int)
    fe, fd, fc, fb = folga
    x0, y0 = max(0, bloco.x - fe), max(0, bloco.y - fc)
    x1, y1 = min(im.shape[1], bloco.x + fd), min(im.shape[0], bloco.y + fb)
    rec = im[y0:y1, x0:x1]
    # bolinha solta e cinza-clara; sob o cursor ela fica AZUL. As duas contam.
    rgb = _np.asarray(Image.open(a).convert("RGB"), dtype=int)[y0:y1, x0:x1]
    azul = (rgb[:, :, 2] - rgb[:, :, 0] >= 55) & (rgb[:, :, 2] >= 150)
    mask = (rec >= claro) | azul
    vistos = _np.zeros_like(mask)
    achados = []
    ys, xs = _np.nonzero(mask)
    for yy, xx in zip(ys, xs):
        if vistos[yy, xx]:
            continue
        pilha, pontos = [(yy, xx)], []
        vistos[yy, xx] = True
        while pilha and len(pontos) < 400:
            cy, cx = pilha.pop()
            pontos.append((cy, cx))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < mask.shape[0] and 0 <= nx < mask.shape[1] \
                            and mask[ny, nx] and not vistos[ny, nx]:
                        vistos[ny, nx] = True
                        pilha.append((ny, nx))
        if not pontos:
            continue
        pys = [p[0] for p in pontos]; pxs = [p[1] for p in pontos]
        alt, larg = max(pys) - min(pys) + 1, max(pxs) - min(pxs) + 1
        cheio = len(pontos) / float(alt * larg)
        if raio[0] * 2 <= alt <= raio[1] * 2 and raio[0] * 2 <= larg <= raio[1] * 2 \
                and abs(alt - larg) <= 5 and len(pontos) >= 12 and cheio >= 0.55:
            achados.append((int(sum(pxs) / len(pxs)) + x0, int(sum(pys) / len(pys)) + y0))
    # a bolinha fica FORA da borda; o que cai dentro do bloco e icone ou letra
    achados = [p for p in achados if p[0] <= bloco.x - 8 or p[0] >= bloco.x + 60]
    if not achados:
        return {"esq": [], "dir": []}
    menor = min(p[0] for p in achados); maior = max(p[0] for p in achados)
    esq = sorted([p for p in achados if p[0] - menor <= 30 and p[0] <= bloco.x - 8],
                 key=lambda p: p[1])
    dir_ = sorted([p for p in achados if maior - p[0] <= 30 and p[0] >= bloco.x + 60],
                  key=lambda p: p[1])
    return {"esq": esq, "dir": dir_}


def pino_por_nome(bloco, rotulo, lado):
    """A bolinha do pino, pela ORDEM conhecida do bloco — sem ler texto."""
    bloco.exige_achado(f"medir o pino '{rotulo}'")
    ordem = PORTAS.get(bloco.tipo, {}).get(lado)
    if not ordem or rotulo not in ordem:
        raise RuntimeError(f"nao sei a ordem dos pinos de '{bloco.nome}' "
                           f"({lado}) — acrescente em blocos.PORTAS")
    pts = bolinhas(bloco)[lado]
    i = ordem.index(rotulo)
    if i >= len(pts):
        raise RuntimeError(f"o bloco {bloco.nome} mostrou {len(pts)} bolinhas de "
                           f"{lado}, e eu queria a {i+1}a ('{rotulo}')")
    return pts[i]


def arrasta_devagar(x0, y0, x1, y1, passos=45, segura=0.45):
    """Arrasto lento, com pausa antes e depois e um tremor no fim.
       O editor do Flowlab e canvas: arrasto rapido demais entre bolinhas
       acende o pino de destino e nao cria fio nenhum.

       NA BANCADA, QUEM ARRASTA E O MOTOR — e a escolha e feita AQUI DENTRO, a
       cada chamada, nao por remendo no import.

       O `bancada.instala()` trocava esta funcao por uma lambda que fala com o
       motor. So que `bancada.liga_se_pedido()` mora dentro do `comum.py`, e na
       ordem de import das capturas (`import rs, nav, editor, blocos, comum`)
       quem carrega primeiro e o `blocos`: ele importa `comum` no meio do seu
       proprio carregamento, o `instala()` poe a lambda num modulo PELA METADE,
       e logo depois o `def` daqui de baixo sobrescreve a lambda. O remendo
       sumia sem deixar rastro.

       O estrago era mudo e caro: `rs._evento_mouse` CONTINUAVA remendado (so o
       MOVER sobrevive, o apertar e o soltar sao engolidos), mas os eventos de
       ARRASTO daqui iam crus para a tela de verdade, na origem — fora da
       pagina. A mesa nao mudava, zero pixels, sem erro nenhum. A foto tirada
       com o botao apertado mostrou o item da palheta so ACESO, com balaozinho
       de ajuda e nenhum bloco fantasma: o apertar nunca chegou ao navegador.
       Passei a noite medindo altura de soltura, posicao na palheta, foco de
       janela e "um arrasto por carregamento" — e as sondas davam verde porque
       elas importam `comum` primeiro, que e a ordem em que a lambda vence."""
    if getattr(rs, "_BANCADA_INSTALADA", False):
        import bancada
        return bancada._chama("arrastar", x0=x0, y0=y0, x1=x1, y1=y1,
                              passos=passos, segura=segura)
    import Quartz
    J = nav.janela(nav.titulo())
    tx0, ty0 = J["x"] + x0 / 2.0, J["y"] + y0 / 2.0
    tx1, ty1 = J["x"] + x1 / 2.0, J["y"] + y1 / 2.0
    rs._evento_mouse(Quartz.kCGEventMouseMoved, tx0, ty0); time.sleep(0.35)
    rs._evento_mouse(Quartz.kCGEventLeftMouseDown, tx0, ty0); time.sleep(segura)
    for k in range(1, passos + 1):
        x = tx0 + (tx1 - tx0) * k / passos
        y = ty0 + (ty1 - ty0) * k / passos
        e = Quartz.CGEventCreateMouseEvent(None, Quartz.kCGEventLeftMouseDragged,
                                           (x, y), Quartz.kCGMouseButtonLeft)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, e)
        time.sleep(0.03)
    for dx, dy in ((2, 0), (-2, 1), (0, 0)):      # tremor: o canvas percebe o alvo
        e = Quartz.CGEventCreateMouseEvent(None, Quartz.kCGEventLeftMouseDragged,
                                           (tx1 + dx, ty1 + dy), Quartz.kCGMouseButtonLeft)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, e)
        time.sleep(0.12)
    time.sleep(segura)
    rs._evento_mouse(Quartz.kCGEventLeftMouseUp, tx1, ty1)
    time.sleep(0.6)


def _mudou_perto(antes, depois, ponto, raio=26, minimo=12):
    A = Image.open(antes).convert("L"); B = Image.open(depois).convert("L")
    x, y = ponto
    caixa = (max(0, x - raio), max(0, y - raio),
             min(A.width, x + raio), min(A.height, y + raio))
    a, b = A.crop(caixa), B.crop(caixa)
    return sum(1 for p, q in zip(a.getdata(), b.getdata()) if abs(p - q) > 30) >= minimo


CORPO = (61, 66, 80)        # cor do corpo de um bloco
FUNDO = (32, 41, 56)        # cor do canvas atras dos blocos


def caixa_do_bloco(bloco, tol=14):
    """(x0, y0, x1, y1) do RETANGULO do bloco, medido na imagem.

       Herdado do que deu errado: caixa por folga fixa muda de tamanho com o
       zoom da pagina e passa a abracar o bloco vizinho, e ai as 'bolinhas' do
       bloco de baixo entram na conta do bloco de cima. O corpo do bloco tem
       cor propria (61,66,80) contra o fundo (32,41,56): da para medir."""
    import numpy as _np
    a, _ = nav.captura("/tmp/_bl_caixa.png")
    im = _np.asarray(Image.open(a).convert("RGB"), dtype=int)
    corpo = (_np.abs(im - _np.array(CORPO)) <= tol).all(axis=2)
    sx, sy = bloco.x + 12, bloco.y + 22          # semente dentro do corpo
    if not (0 <= sy < corpo.shape[0] and 0 <= sx < corpo.shape[1]) or not corpo[sy, sx]:
        for dy in (14, 30, 8, 40):
            if 0 <= bloco.y + dy < corpo.shape[0] and corpo[bloco.y + dy, sx]:
                sy = bloco.y + dy
                break
        else:
            raise RuntimeError(f"nao achei o corpo do bloco {bloco.nome} perto do titulo")
    x0 = x1 = sx
    while x0 > 0 and corpo[sy, x0 - 1]:
        x0 -= 1
    while x1 < corpo.shape[1] - 1 and corpo[sy, x1 + 1]:
        x1 += 1
    meio = (x0 + x1) // 2
    y0 = y1 = sy
    while y0 > 0 and corpo[y0 - 1, meio]:
        y0 -= 1
    while y1 < corpo.shape[0] - 1 and corpo[y1 + 1, meio]:
        y1 += 1
    return (x0, y0, x1, y1)


def bolinhas2(bloco, margem=34, claro=180):
    """As bolinhas dos pinos, procuradas SO nas faixas do lado de fora das
       bordas do bloco — nada de caixa por folga."""
    import numpy as _np
    x0, y0, x1, y1 = caixa_do_bloco(bloco)
    a, _ = nav.captura("/tmp/_bl_dots2.png")
    im = _np.asarray(Image.open(a).convert("RGB"), dtype=int)
    L = _np.asarray(Image.open(a).convert("L"), dtype=int)
    azul = (im[:, :, 2] - im[:, :, 0] >= 55) & (im[:, :, 2] >= 150)
    mask = (L >= claro) | azul

    def na_faixa(fx0, fx1):
        pts = []
        sub = mask[max(0, y0 - 6):y1 + 7, max(0, fx0):fx1]
        vistos = _np.zeros_like(sub)
        ys, xs = _np.nonzero(sub)
        for yy, xx in zip(ys, xs):
            if vistos[yy, xx]:
                continue
            pilha, pontos = [(yy, xx)], []
            vistos[yy, xx] = True
            while pilha and len(pontos) < 500:
                cy, cx = pilha.pop(); pontos.append((cy, cx))
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < sub.shape[0] and 0 <= nx < sub.shape[1] \
                                and sub[ny, nx] and not vistos[ny, nx]:
                            vistos[ny, nx] = True; pilha.append((ny, nx))
            pys = [p[0] for p in pontos]; pxs = [p[1] for p in pontos]
            alt, larg = max(pys) - min(pys) + 1, max(pxs) - min(pxs) + 1
            if 5 <= alt <= 26 and 5 <= larg <= 26 and abs(alt - larg) <= 6 \
                    and len(pontos) / float(alt * larg) >= 0.55:
                pts.append((int(sum(pxs) / len(pxs)) + max(0, fx0),
                            int(sum(pys) / len(pys)) + max(0, y0 - 6)))
        return sorted(pts, key=lambda p: p[1])

    return {"esq": na_faixa(x0 - margem, x0), "dir": na_faixa(x1 + 1, x1 + margem)}


def caixa2(bloco, limite=(700, 420)):
    """O retangulo do bloco, por CRESCIMENTO a partir de uma semente.

       A varredura por linha parava cedo: o miolo do bloco tem tom diferente do
       corpo (icone, barra de titulo). Aqui a regra e 'nao e o fundo do canvas',
       com uma erosao antes — senao o crescimento escapa pelo FIO, que encosta
       na borda, e engole o bloco vizinho."""
    import numpy as _np
    a, _ = nav.captura("/tmp/_bl_caixa2.png")
    im = _np.asarray(Image.open(a).convert("RGB"), dtype=int)
    fundo = (_np.abs(im - _np.array(FUNDO)) <= 12).all(axis=2)
    cheio = ~fundo
    # erosao 3x3: tira fio fino e deixa o corpo do bloco
    e = cheio.copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            e &= _np.roll(_np.roll(cheio, dy, axis=0), dx, axis=1)
    sx, sy = bloco.x + 12, bloco.y + 4
    if not e[sy, sx]:
        for dy in range(-6, 40, 4):
            if 0 <= bloco.y + dy < e.shape[0] and e[bloco.y + dy, sx]:
                sy = bloco.y + dy; break
        else:
            raise RuntimeError(f"nao achei o corpo de {bloco.nome} perto do titulo")
    x0 = x1 = sx; y0 = y1 = sy
    pilha = [(sy, sx)]
    vistos = set()
    while pilha:
        cy, cx = pilha.pop()
        if (cy, cx) in vistos:
            continue
        vistos.add((cy, cx))
        if abs(cx - sx) > limite[0] or abs(cy - sy) > limite[1]:
            continue
        x0, x1 = min(x0, cx), max(x1, cx)
        y0, y1 = min(y0, cy), max(y1, cy)
        for ny, nx in ((cy+1, cx), (cy-1, cx), (cy, cx+1), (cy, cx-1)):
            if 0 <= ny < e.shape[0] and 0 <= nx < e.shape[1] and e[ny, nx] \
                    and (ny, nx) not in vistos:
                pilha.append((ny, nx))
    return (x0 - 1, y0 - 1, x1 + 1, y1 + 1)


def caixa3(bloco, tol=12, limite=900):
    """O retangulo do bloco. Terceira tentativa, e a que funciona.

       As duas anteriores estao acima, com o defeito de cada uma: varredura no
       MEIO do bloco para cedo (o miolo tem outro tom por causa do icone), e
       crescimento de regiao VAZA pelo fio ate o bloco vizinho.

       Aqui: acho as bordas esquerda e direita na LINHA DO TITULO (que so tem
       corpo e letra), e a altura numa COLUNA a 3 px de dentro da borda
       esquerda, onde nao ha icone nem texto."""
    import numpy as _np
    a, _ = nav.captura("/tmp/_bl_caixa3.png")
    im = _np.asarray(Image.open(a).convert("RGB"), dtype=int)
    fundo = (_np.abs(im - _np.array(FUNDO)) <= tol).all(axis=2)
    A, L = fundo.shape
    ty = min(max(bloco.y, 0), A - 1)
    tx = min(max(bloco.x, 0), L - 1)
    if fundo[ty, tx]:                       # o titulo pode cair no vao da letra
        for dx in (4, 8, -4, 12):
            if 0 <= tx + dx < L and not fundo[ty, tx + dx]:
                tx += dx; break
    x0 = tx
    while x0 > 0 and not fundo[ty, x0 - 1] and tx - x0 < limite:
        x0 -= 1
    x1 = tx
    while x1 < L - 1 and not fundo[ty, x1 + 1] and x1 - tx < limite:
        x1 += 1
    col = min(x0 + 3, L - 1)
    y0 = ty
    while y0 > 0 and not fundo[y0 - 1, col] and ty - y0 < limite:
        y0 -= 1
    y1 = ty
    while y1 < A - 1 and not fundo[y1 + 1, col] and y1 - ty < limite:
        y1 += 1
    return (x0, y0, x1, y1)


def pinos(bloco, margem=22, claro=175, folga=4):
    """As bolinhas dos pinos, nas faixas de fora das bordas medidas por caixa3.
       Confere a CONTAGEM contra a tabela PORTAS — se o bloco devia ter tres
       entradas e eu achei duas, eu digo, em vez de ligar no pino errado."""
    import numpy as _np
    x0, y0, x1, y1 = caixa4(bloco)
    a, _ = nav.captura("/tmp/_bl_pinos.png")
    rgb = _np.asarray(Image.open(a).convert("RGB"), dtype=int)
    lum = _np.asarray(Image.open(a).convert("L"), dtype=int)
    azul = (rgb[:, :, 2] - rgb[:, :, 0] >= 55) & (rgb[:, :, 2] >= 150)
    mask = (lum >= claro) | azul

    def faixa(fx0, fx1):
        fx0, fx1 = max(0, fx0), max(0, fx1)
        sub = mask[max(0, y0 - 4):y1 + 5, fx0:fx1]
        if sub.size == 0:
            return []
        vistos = _np.zeros_like(sub); pts = []
        ys, xs = _np.nonzero(sub)
        for yy, xx in zip(ys, xs):
            if vistos[yy, xx]:
                continue
            pilha, pontos = [(yy, xx)], []
            vistos[yy, xx] = True
            while pilha and len(pontos) < 600:
                cy, cx = pilha.pop(); pontos.append((cy, cx))
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < sub.shape[0] and 0 <= nx < sub.shape[1] \
                                and sub[ny, nx] and not vistos[ny, nx]:
                            vistos[ny, nx] = True; pilha.append((ny, nx))
            pys = [p[0] for p in pontos]; pxs = [p[1] for p in pontos]
            alt, larg = max(pys) - min(pys) + 1, max(pxs) - min(pxs) + 1
            if 5 <= alt <= 24 and 5 <= larg <= 24 and abs(alt - larg) <= 5 \
                    and len(pontos) / float(alt * larg) >= 0.5:
                pts.append((int(sum(pxs) / len(pxs)) + fx0,
                            int(sum(pys) / len(pys)) + max(0, y0 - 4)))
        return sorted(pts, key=lambda p: p[1])

    # a bolinha encosta na borda (medido: 16 px de distancia). Faixa estreita,
    # senao eu pego a bolinha do bloco VIZINHO e ligo no lugar errado.
    # procuro numa faixa LARGA (senao o disco sai cortado e perde a redondeza)
    # e aceito pelo CENTRO, que e o que diz de quem e a bolinha
    largo = margem + 16
    esq = [p for p in faixa(x0 - largo, x0) if x0 - margem <= p[0] <= x0 - folga]
    dire = [p for p in faixa(x1, x1 + largo) if x1 + folga <= p[0] <= x1 + margem]
    achados = {"esq": esq, "dir": dire}
    esperado = PORTAS.get(bloco.tipo)
    if esperado:
        for lado in ("esq", "dir"):
            if len(achados[lado]) != len(esperado[lado]):
                raise RuntimeError(
                    f"{bloco.nome}: achei {len(achados[lado])} bolinhas de "
                    f"{lado} e a tabela diz {len(esperado[lado])} "
                    f"({esperado[lado]}) — nao ligo no escuro")
    return achados


def caixa4(bloco, tol=14, claro=150, limite=700):
    """O retangulo do bloco — versao que aguenta o bloco em cima do retangulo
       de previsao do nivel.

       'Nao e o fundo' nao serve: a previsao do nivel tambem nao e o fundo, e a
       caixa crescia ate abracar o mundo inteiro (medi 1023x767 para um bloco
       de ~240x170). A regra que fecha: o pixel e CORPO DO BLOCO (61,66,80) ou
       e CLARO (letra, borda, icone). A previsao do nivel nao e nem um nem
       outro, entao a varredura para exatamente na borda."""
    import numpy as _np
    a, _ = nav.captura("/tmp/_bl_caixa4.png")
    rgb = _np.asarray(Image.open(a).convert("RGB"), dtype=int)
    lum = _np.asarray(Image.open(a).convert("L"), dtype=int)
    dentro = ((_np.abs(rgb - _np.array(CORPO)) <= tol).all(axis=2)) | (lum >= claro)
    A, L = dentro.shape
    ty, tx = min(max(bloco.y, 0), A - 1), min(max(bloco.x, 0), L - 1)
    if not dentro[ty, tx]:
        for dx in (4, 8, 12, -4):
            if 0 <= tx + dx < L and dentro[ty, tx + dx]:
                tx += dx; break
    x0 = tx
    while x0 > 0 and dentro[ty, x0 - 1] and tx - x0 < limite:
        x0 -= 1
    x1 = tx
    while x1 < L - 1 and dentro[ty, x1 + 1] and x1 - tx < limite:
        x1 += 1
    col = min(x0 + 4, L - 1)
    y0 = ty
    while y0 > 0 and dentro[y0 - 1, col] and ty - y0 < limite:
        y0 -= 1
    y1 = ty
    while y1 < A - 1 and dentro[y1 + 1, col] and y1 - ty < limite:
        y1 += 1
    return (x0, y0, x1, y1)


def discos(bloco, esq=45, dir_=430, cima=25, baixo=250, claro=175):
    """Os discos claros em volta do titulo de um bloco, separados em colunas.

       Depois de quatro tentativas de medir o retangulo do bloco pela cor
       (linha do titulo, crescimento de regiao, corpo-ou-claro), o que fecha e
       aceitar que a MEDIDA do retangulo e fragil — o antialias entre as letras
       tem a cor da previsao do nivel — e usar o que eu CONTROLO: a aula
       coloca os blocos longe uns dos outros, entao uma caixa generosa em volta
       do titulo so contem os pinos deste bloco. A contagem esperada confere."""
    import numpy as _np
    a, _ = nav.captura("/tmp/_bl_discos.png")
    rgb = _np.asarray(Image.open(a).convert("RGB"), dtype=int)
    lum = _np.asarray(Image.open(a).convert("L"), dtype=int)
    azul = (rgb[:, :, 2] - rgb[:, :, 0] >= 55) & (rgb[:, :, 2] >= 150)
    mask = (lum >= claro) | azul
    A, L = mask.shape
    x0, x1 = max(0, bloco.x - esq), min(L, bloco.x + dir_)
    y0, y1 = max(0, bloco.y - cima), min(A, bloco.y + baixo)
    sub = mask[y0:y1, x0:x1]
    vistos = _np.zeros_like(sub); pts = []
    ys, xs = _np.nonzero(sub)
    for yy, xx in zip(ys, xs):
        if vistos[yy, xx]:
            continue
        pilha, pontos = [(yy, xx)], []
        vistos[yy, xx] = True
        while pilha and len(pontos) < 600:
            cy, cx = pilha.pop(); pontos.append((cy, cx))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < sub.shape[0] and 0 <= nx < sub.shape[1] \
                            and sub[ny, nx] and not vistos[ny, nx]:
                        vistos[ny, nx] = True; pilha.append((ny, nx))
        pys = [p[0] for p in pontos]; pxs = [p[1] for p in pontos]
        alt, larg = max(pys) - min(pys) + 1, max(pxs) - min(pxs) + 1
        if 7 <= alt <= 22 and 7 <= larg <= 22 and abs(alt - larg) <= 4 \
                and len(pontos) / float(alt * larg) >= 0.62:
            pts.append((int(sum(pxs) / len(pxs)) + x0, int(sum(pys) / len(pys)) + y0))
    if not pts:
        return {"esq": [], "dir": []}
    # duas colunas: a da esquerda e a mais a esquerda de todas
    menor, maior = min(p[0] for p in pts), max(p[0] for p in pts)
    coluna_esq = [p for p in pts if p[0] - menor <= 24 and p[0] < bloco.x]
    coluna_dir = [p for p in pts if maior - p[0] <= 24 and p[0] > bloco.x + 60]
    return {"esq": sorted(coluna_esq, key=lambda p: p[1]),
            "dir": sorted(coluna_dir, key=lambda p: p[1])}


def pino(bloco, rotulo, lado):
    """A bolinha de um pino, pela ordem conhecida, com a contagem conferida."""
    ordem = PORTAS.get(bloco.tipo, {}).get(lado)
    if ordem is None:
        raise RuntimeError(f"nao sei a ordem dos pinos de '{bloco.nome}' ({lado})")
    achados = discos(bloco)[lado]
    if len(achados) != len(ordem):
        raise RuntimeError(f"{bloco.nome}: achei {len(achados)} bolinhas de {lado} "
                           f"e a tabela diz {len(ordem)} ({ordem})")
    return achados[ordem.index(rotulo)]


# Deslocamento de cada pino em relacao ao TITULO do bloco, medido na tela com a
# pagina em 100%. Medir uma vez e guardar foi o que funcionou: detectar disco
# automaticamente falhou quatro vezes (a previsao do nivel, o antialias entre as
# letras e o icone do bloco entram na conta).
#   chave: nome do bloco -> lado -> rotulo -> (dx, dy)
DESLOC = {
    "Collision": {"esq": {}, "dir": {"hit": (247, 57)}},
    # ⚠️ NA PALHETA ele se chama `Emit`; NA MESA o titulo e `Emitter` — e o
    # pino de entrada tambem se chama `emit`. `acha_bloco("Emit")` casa com o
    # ROTULO DO PINO, 86 px abaixo do titulo, e todos os deslocamentos saem
    # errados. Procure sempre por `Emitter`.
    "Emitter":  {"esq": {"angle": (-27, 46), "emit": (-27, 87)},
                 "dir": {"out": (246, 66)}},
    # medidos na captura de tela, no rascunho da Aula 3
    "Always":   {"esq": {}, "dir": {"out": (251, 54)}},
    "Velocity": {"esq": {"x": (-31, 40), "y": (-31, 76), "forward": (-31, 114)},
                 "dir": {"out": (249, 40), "out2": (249, 76), "out3": (249, 114)}},
    # o Number tem TRES entradas: 'set' (quadrada, recebe valor), 'get'
    # (redonda, e o gatilho que faz ele cuspir o valor) e '+' (soma 1).
    # Ligar o Always no 'set' nao faz nada sair: quem dispara e o 'get'.
    "Number":   {"esq": {"set": (-28, 39), "get": (-28, 75), "mais": (-28, 114)},
                 "dir": {"out": (249, 74)}},
    "Alert":    {"esq": {"show": (-26, 45), "hide": (-26, 86)},
                 "dir": {"click": (247, 65)}},
    # medidos no rascunho da Aula 4
    "Keyboard": {"esq": {}, "dir": {"down": (245, 43), "up": (245, 85)}},
    # ── as tres pecas da Aula 5, medidas na foto da mesa ──
    # ⚠️ O `Label` ESCREVE O PROPRIO TEXTO NA FASE: um `Label` recem-solto
    # desenha a palavra "Label" em letra grande dentro do retangulo do nivel, e
    # `acha_bloco("Label")` casa com ELA, nao com o titulo do bloco (medido:
    # devolveu x=959 quando o bloco estava em x=1460). Procure sempre com
    # `regiao=` fora do retangulo do nivel.
    "Label":   {"esq": {"text": (-30, 38), "alpha": (-30, 74),
                        "x": (-30, 110), "y": (-30, 146)},
                "dir": {"text": (242, 38), "alpha": (242, 74),
                        "x": (242, 110), "y": (242, 146)}},
    # MEDIDOS PELA MAQUINA (`mede_pinos`), nao a olho. Os que eu tinha estimado
    # de um recorte erravam ate 26 px — o `Once.out` ficava em (254,31) quando
    # esta em (244,57) — e um fio que erra o pino nao da erro: ele simplesmente
    # nao nasce.
    "Random":  {"esq": {"min": (-27, 41), "max": (-27, 79), "new": (-27, 117)},
                "dir": {"out": (244, 77)}},
    "Once":    {"esq": {}, "dir": {"out": (244, 57)}},
    "Message": {"esq": {"send": (-27, 55)}, "dir": {"done": (244, 55)}},
    "Filter":  {"esq": {"set": (-27, 45), "in": (-27, 87)},
                "dir": {"pass": (244, 45), "fail": (244, 87)}},
    "Mailbox": {"esq": {}, "dir": {"out": (244, 57)}},
    "Position": {"esq": {"x": (-27, 37), "y": (-27, 73),
                         "maisx": (-27, 109), "maisy": (-27, 145)},
                 "dir": {"x": (244, 61), "y": (244, 119)}},
    "Impulse": {"esq": {"x": (-32, 42), "y": (-32, 78), "forward": (-32, 114)},
                "dir": {"out": (242, 42), "out2": (242, 78), "out3": (242, 114)}},
    "MouseClick": {"esq": {}, "dir": {"down": (244, 37), "up": (244, 73),
                                      "over": (244, 109), "out": (244, 145)}},
    "LoadLevel": {"esq": {"go": (-27, 45), "get": (-27, 87)},
                  "dir": {"out": (244, 45), "out2": (244, 87)}},
    "Timer":    {"esq": {"delay": (-28, 39), "reset": (-28, 76), "start": (-28, 114)},
                 "dir": {"out": (247, 50), "done": (247, 103)}},
    "Spawn":    {"esq": {"x": (-25, 41), "y": (-25, 76), "spawn": (-25, 116)},
                 "dir": {"out": (246, 76)}},
    # Aula 8, medidos na mesa (o ponto do meio do `Switch` e o ICONE, nao
    # pino: `mede_pinos` devolve (109,66) junto, e ele nao entra aqui).
    # Aula 9, medidos na mesa (a leitura do `Expression` veio suja porque o
    # bloco caiu em cima do `Proximity`: os tres pinos da esquerda a partir de
    # (-27, 39) sao A, B e eval, e a saida e (244, 75) — conferido na foto).
    "Object Variable": {"esq": {"set": (-25, 39), "get": (-25, 77),
                                "mais": (-25, 115)},
                        "dir": {"out": (246, 75)}},
    "Proximity": {"esq": {"dist": (-27, 51), "check": (-27, 101)},
                  "dir": {"x": (244, 39), "y": (244, 77), "miss": (244, 115)}},
    "PointAt":   {"esq": {"x": (-27, 45), "y": (-27, 87)},
                  "dir": {"rot": (244, 65)}},
    "Expression": {"esq": {"A": (-27, 39), "B": (-27, 77), "eval": (-27, 115)},
                   "dir": {"out": (244, 75)}},
    "Bar":       {"esq": {"value": (-27, 57)}, "dir": {"out": (244, 57)}},
    "Global Variable": {"esq": {"set": (-27, 41), "get": (-27, 79),
                                "mais": (-27, 117)},
                        "dir": {"out": (244, 77)}},
    "Switch":   {"esq": {"off": (-26, 42), "on": (-26, 80), "in": (-26, 118)},
                 "dir": {"out": (245, 78)}},
    "Destroyer": {"esq": {"in": (-28, 57)}, "dir": {"out": (248, 57)}},
    # Aula 11. `Animation` e `Blending` saem do `mede_pinos`; o `SoundEffect`
    # tem cinco saidas e foi medido na foto da mesa (titulo -> bolinha).
    "SoundEffect": {"esq": {"play": (-26, 43), "pause": (-26, 83),
                            "stop": (-26, 123), "vol": (-26, 163)},
                    "dir": {"playing": (247, 37), "pause": (247, 71),
                            "stop": (247, 104), "vol": (247, 138),
                            "done": (247, 174)}},
    "Animation": {"esq": {"start": (-26, 41), "stop": (-26, 79), "goto": (-26, 117)},
                  "dir": {"play": (245, 41), "done": (245, 79), "goto": (245, 117)}},
    "Blending":  {"esq": {"mode": (-27, 55)}, "dir": {"out": (244, 55)}},
    # o titulo no canvas e 'RestartGame' (sem espaco), mas na palheta ele
    # aparece como 'Restart Game' — por isso solta() aceita titulo diferente
    "RestartGame": {"esq": {"go": (-28, 57)}, "dir": {"out": (248, 57)}},
    # O Camera tem SEIS entradas, medidas com `blocos.pinos` na tela — nao
    # contadas no olho num print reduzido. As saidas ficaram de fora de
    # proposito: a leitura delas veio suja (dx de 22 a 38, incoerente), e
    # numero que eu nao medi direito nao entra em tabela de onde clicar.
    "Camera": {"esq": {"set x": (-27, 36), "set y": (-27, 68),
                       "move x": (-27, 102), "move y": (-27, 134),
                       "zoom": (-27, 168), "rotate": (-27, 200)}},
}


def pino_fixo(bloco, rotulo, lado):
    """(x, y) do pino pelo deslocamento medido do tipo do bloco."""
    bloco.exige_achado(f"medir o pino '{rotulo}'")
    tab = DESLOC.get(bloco.tipo, {}).get(lado, {})
    if rotulo not in tab:
        raise RuntimeError(f"nao tenho o deslocamento do pino '{rotulo}' ({lado}) "
                           f"de '{bloco.nome}' — meça e acrescente em blocos.DESLOC")
    dx, dy = tab[rotulo]
    return (bloco.x + dx, bloco.y + dy)


def _toca_o_pino(im, p, lado, longe=(16, 42), alto=10, claro=150):
    """Sai (ou chega) fio DESTE pino?

       A faixa entre dois pinos nao basta: um fio VIZINHO que cruze a regiao
       passa por ligacao. Medido, e foi assim que `liga_fixo` aprovou um fio
       que nunca existiu — `Timer.out -> Destroyer.in` dava True com o fio de
       `Keyboard.down -> Destroyer.in` cruzando o caminho, e o Flowlab tinha
       RECUSADO a segunda ligacao na mesma entrada.

       O invariante que separa os dois e o pedacinho logo DEPOIS do pino: o
       fio sai dele na horizontal. Medido na mesma foto: no `out` ligado o
       brilho continua 233 ate 56 px adiante; no `done` ao lado, 53 px abaixo,
       ele cai para 71 (o fundo) ja aos 12 px. O circulo do pino e claro nos
       dois casos — por isso a faixa comeca depois dele."""
    x, y = int(p[0]), int(p[1])
    a0, a1 = max(0, y - alto), y + alto + 1
    if lado == "dir":
        faixa = im[a0:a1, x + longe[0]: x + longe[1]]
    else:
        faixa = im[a0:a1, max(0, x - longe[1]): max(0, x - longe[0])]
    return faixa.size > 0 and int(faixa.max()) >= claro


def _ha_fio(arquivo, p1, p2, folga=34, claro=200, minimo=40, blocos_=()):
    """Ja existe um fio ligando estes dois pinos?

       Olha a FAIXA entre eles e conta pixels claros — o fio e quase branco, e
       o fundo da mesa e escuro. A faixa e partida em tres fatias ao longo do
       eixo MAIS LONGO, e as tres precisam ter fio: assim um fio de outro par
       que cruze a regiao nao passa por ligacao.

       O eixo importa. A primeira versao sempre fatiava na horizontal, e para
       dois pinos quase um em cima do outro (Always.out -> Number.get, 86 px
       de distancia horizontal) a faixa ficava estreita demais e ela respondia
       'nao ha fio' com o fio desenhado na tela.

       Isto e o invariante ('ha um fio entre estes dois pinos'), e nao o proxy
       ('alguma coisa mudou no caminho'). O proxy reprovava quando o fio JA
       ESTAVA LA — que e o estado normal de uma etapa repetida depois de um
       erro no meio dela."""
    import numpy as _np
    im = _np.asarray(Image.open(arquivo).convert("L"), dtype=int)
    # A MESA TEM DE ESTAR PARADA. Quando a simulacao do editor de blocos esta
    # rodando, o fundo do canvas fica BRANCO — e ai todo pixel e claro, o
    # detector responde "ha fio" para qualquer par de pinos, e `liga_fixo`
    # aprova uma ligacao que nao existe. Aconteceu: dei por ligado um fio que
    # a tela nao mostrava.
    miolo = im[im.shape[0] // 4: im.shape[0] * 3 // 4,
               im.shape[1] // 3: im.shape[1] * 3 // 4]
    if float(_np.median(miolo)) > 150:
        raise RuntimeError("a mesa de blocos esta com a SIMULACAO rodando "
                           "(fundo claro): pare antes de conferir fio")
    # O FIO TEM DE TOCAR OS DOIS PINOS. A faixa entre eles sozinha aprova o fio
    # do vizinho que cruza a regiao.
    if not (_toca_o_pino(im, p1, "dir") and _toca_o_pino(im, p2, "esq")):
        return False
    x0, x1 = sorted((p1[0], p2[0]))
    y0, y1 = sorted((p1[1], p2[1]))
    horizontal = (x1 - x0) >= (y1 - y0)
    if horizontal:
        x0, x1 = x0 + folga, x1 - folga
        y0, y1 = max(0, y0 - 60), min(im.shape[0], y1 + 60)
    else:
        y0, y1 = y0 + folga, y1 - folga
        x0, x1 = max(0, x0 - 60), min(im.shape[1], x1 + 60)
    if x1 - x0 < 20 or y1 - y0 < 20:
        return False
    # APAGA O CORPO DOS BLOCOS da conta. Sem isto eu contava a tecla branca do
    # icone do `Keyboard` e as bordas claras dos proprios blocos como se
    # fossem fio: o detector aprovou uma ligacao que NAO EXISTIA na tela, e eu
    # so vi quando a simulacao mostrou os dois blocos soltos.
    im = im.copy()
    for b in blocos_:
        bx0, by0 = max(0, b.x - 60), max(0, b.y - 40)
        bx1, by1 = min(im.shape[1], b.x + 280), min(im.shape[0], b.y + 170)
        im[by0:by1, bx0:bx1] = 0
    passo = ((x1 - x0) if horizontal else (y1 - y0)) // 3
    if passo < 4:
        return False
    for k in range(3):
        if horizontal:
            rec = im[y0:y1, x0 + k * passo: x0 + (k + 1) * passo]
        else:
            rec = im[y0 + k * passo: y0 + (k + 1) * passo, x0:x1]
        if int((rec > claro).sum()) < minimo:
            return False
    return True


def mede_pinos(bloco, arquivo=None):
    """Os pinos de um bloco, MEDIDOS na tela, em deslocamento relativo ao titulo.

       Serve para escrever uma linha nova de `DESLOC` sem estimar nada a olho.
       Estimar de um recorte ja me custou uma noite: um deslocamento 26 px fora
       faz `liga_fixo` dizer "nenhum fio apareceu", que e o mesmo erro de dez
       outras causas.

       Devolve a lista ordenada da esquerda para a direita, de cima para baixo.
       Os de x negativo sao ENTRADAS; os de x ~+244, SAIDAS."""
    import numpy as _np
    a = arquivo or nav.captura("/tmp/_bl_pinos.png")[0]
    im = _np.asarray(Image.open(a).convert("RGB"), dtype=int)
    bx, by = bloco.x, bloco.y
    y0, y1 = max(0, by - 60), min(im.shape[0], by + 230)
    x0, x1 = max(0, bx - 80), min(im.shape[1], bx + 330)
    rec = im[y0:y1, x0:x1]
    m = (rec[:, :, 0] > 195) & (rec[:, :, 1] > 195) & (rec[:, :, 2] > 195)
    vis = _np.zeros(m.shape, bool)
    achados = []
    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            if not m[i, j] or vis[i, j]:
                continue
            pilha, pix = [(i, j)], []
            vis[i, j] = True
            while pilha:
                p, q = pilha.pop(); pix.append((p, q))
                for dp, dq in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    np_, nq = p + dp, q + dq
                    if 0 <= np_ < m.shape[0] and 0 <= nq < m.shape[1] \
                       and m[np_, nq] and not vis[np_, nq]:
                        vis[np_, nq] = True; pilha.append((np_, nq))
            if not (120 <= len(pix) <= 900):
                continue
            ys = [p[0] for p in pix]; xs = [p[1] for p in pix]
            alt, larg = max(ys) - min(ys) + 1, max(xs) - min(xs) + 1
            if 0.7 <= alt / larg <= 1.4:          # bolinha e REDONDA
                achados.append((int(x0 + sum(xs) / len(xs) - bx),
                                int(y0 + sum(ys) / len(ys) - by)))
    return sorted(achados, key=lambda p: (p[0], p[1]))


def liga_fixo(origem, pino_saida, destino, pino_entrada):
    """Liga usando os deslocamentos medidos, e CONFERE que o fio existe."""
    p1 = pino_fixo(origem, pino_saida, "dir")
    p2 = pino_fixo(destino, pino_entrada, "esq")
    a, _ = nav.captura("/tmp/_lf_antes.png")
    if _ha_fio(a, p1, p2, blocos_=(origem, destino)):
        return "ja estava"
    for _ in range(2):
        arrasta_devagar(p1[0], p1[1], p2[0], p2[1])
        time.sleep(0.8)
        a_dep, _ = nav.captura("/tmp/_lf_depois.png")
        if _ha_fio(a_dep, p1, p2, blocos_=(origem, destino)):
            return True
    raise RuntimeError(f"liguei {origem.nome}.{pino_saida} -> "
                       f"{destino.nome}.{pino_entrada} e nenhum fio apareceu")


# ---------------------------------------------------------------------------
# AJUSTES DE UM BLOCO
#
# Descoberto no rascunho da Aula 3, depois de meia duzia de tentativas erradas:
# o painel de ajustes de um bloco (Label, Current value, OK, Delete) NAO abre
# com clique comum nem com clique duplo — esses so SELECIONAM o bloco, e o
# arrasto o move. Quem abre e o clique LENTO (`rs.clique_lento`): parar o
# ponteiro em cima, apertar e segurar um instante antes de soltar.
#
# Enquanto eu insistia no clique rapido, o numero continuava 0 e nada na tela
# dizia por que — o bloco ate ficava com a borda azul, parecendo que tinha
# recebido o clique.
# ---------------------------------------------------------------------------

def abre_ajustes(bloco, tentativas=3):
    """Abre o painel de ajustes do bloco e devolve o ponto do campo de valor."""
    bloco.exige_achado("abrir os ajustes")
    J = nav.janela()
    for k in range(tentativas):
        rs.clique_lento(J["x"] + bloco.x / 2.0 + 55, J["y"] + bloco.y / 2.0 + 33)
        time.sleep(1.4)
        a, _ = nav.captura("/tmp/_bl_aj.png")
        p = nav.acha_texto("current value", arquivo=a)
        if p:
            return p
        # o painel pode ter aberto sem o campo (blocos sem valor): aceito se o
        # OK/Delete do painel estiver la
        if nav.acha_texto("delete", arquivo=a):
            return None
        time.sleep(0.8)
    raise RuntimeError(f"nao consegui abrir os ajustes do bloco {bloco.nome}")


def escreve_valor(bloco, valor):
    """Abre os ajustes, escreve o valor em 'Current value' e fecha no OK.
       CONFERE lendo o numero que ficou no corpo do bloco."""
    p = abre_ajustes(bloco)
    if not p:
        raise RuntimeError(f"o bloco {bloco.nome} nao tem campo 'Current value'")
    # o campo fica logo ABAIXO do rotulo 'Current value'
    alvo = (p[0] + 30, p[1] + 68)
    nav.clique_seguro(*alvo); time.sleep(0.6)
    rs.tecla(0, cmd=True); time.sleep(0.25)          # Cmd+A
    # O CAMPO ENGOLE O MENOS QUANDO ELE E O PRIMEIRO. Com o conteudo todo
    # selecionado, digitar '-0.3' deixa '0.3' — sem erro nenhum, e o sinal e
    # justamente o que faz a lava SUBIR em vez de descer. (Nao e o teclado:
    # medi tecla por tecla no campo 'Label' e o codigo 27 produz hifen sim.)
    # Entao escrevo os algarismos, volto o cursor ate o comeco e so entao o
    # sinal. Pelo caminho UNICODE o campo nao recebe nada.
    texto = str(valor)
    negativo = texto.startswith("-")
    corpo = texto.lstrip("-")
    rs.digita_teclas(corpo); time.sleep(0.4)
    if negativo:
        for _ in range(len(corpo)):
            rs.tecla(123); time.sleep(0.08)          # seta esquerda
        rs.digita_teclas("-"); time.sleep(0.4)
    time.sleep(0.3)
    fecha_ajustes()
    lido = le_valor(bloco)
    if lido != str(valor):
        raise RuntimeError(f"escrevi {valor} em {bloco.nome} e o bloco mostra {lido!r}")
    return True


def fecha_ajustes():
    a, _ = nav.captura("/tmp/_bl_ok.png")
    p = nav.acha_texto("delete", arquivo=a)
    if not p:
        return False
    # o OK fica a ESQUERDA do Delete, na mesma altura
    nav.clique_seguro(p[0] - 200, p[1]); time.sleep(1.2)
    return True


AZUL_VALOR = None      # o numero do bloco e desenhado em azul claro


def _glifos_azuis(arquivo, bloco):
    """As manchas AZUIS dentro do bloco, da esquerda para a direita.
       Cada mancha e um sinal ou um algarismo."""
    import numpy as _np
    im = _np.asarray(Image.open(arquivo).convert("RGB"), dtype=int)
    y0, y1 = max(0, bloco.y - 10), min(im.shape[0], bloco.y + 140)
    x0, x1 = max(0, bloco.x - 10), min(im.shape[1], bloco.x + 300)
    sub = im[y0:y1, x0:x1]
    m = (sub[:, :, 2] > 170) & (sub[:, :, 2] - sub[:, :, 0] > 55) & (sub[:, :, 1] > 95)
    if not m.any():
        return [], None
    vistos = _np.zeros_like(m); grupos = []
    ys, xs = _np.nonzero(m)
    for yy, xx in zip(ys, xs):
        if vistos[yy, xx]:
            continue
        pilha, pts = [(yy, xx)], []
        vistos[yy, xx] = True
        while pilha:
            cy, cx = pilha.pop(); pts.append((cy, cx))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < m.shape[0] and 0 <= nx < m.shape[1] \
                            and m[ny, nx] and not vistos[ny, nx]:
                        vistos[ny, nx] = True; pilha.append((ny, nx))
        pys = [q[0] for q in pts]; pxs = [q[1] for q in pts]
        grupos.append(dict(x=min(pxs) + x0, y=min(pys) + y0,
                           w=max(pxs) - min(pxs) + 1, h=max(pys) - min(pys) + 1))
    grupos.sort(key=lambda g: g["x"])
    caixa = (min(g["x"] for g in grupos) - 8, min(g["y"] for g in grupos) - 8,
             max(g["x"] + g["w"] for g in grupos) + 8,
             max(g["y"] + g["h"] for g in grupos) + 8)
    return grupos, caixa


def le_valor(bloco, tentativas=3):
    """O numero escrito DENTRO do bloco, lido da tela.

       Cada glifo e classificado SOZINHO, e nao a frase inteira:
       - o menos e uma barrinha baixa e larga — geometria, nao OCR, porque o
         tesseract come ou inventa o hifen (e ler '-1.7' como '1.7' deixaria a
         lava DESCENDO com o guarda verde);
       - o ponto decimal e um quadradinho;
       - so os ALGARISMOS vao para o tesseract, um por um, com margem branca e
         em tamanho nativo. A linha inteira nao serve: '-1' volta vazio e
         '-1.7' volta '1' — o recorte curto derruba a segmentacao."""
    for k in range(tentativas):
        # PROCURA NA FAIXA DO PROPRIO BLOCO. Reprocurar so pelo NOME devolve o
        # primeiro `Number` da mesa — e a Aula 4 tem dois, um por sentido. O
        # bloco de baixo mostrava `3` na tela, certinho, e a leitura trazia o
        # `-3` do de cima: a guarda reprovava um valor correto e parava a
        # captura. Reprocurar continua valendo (zoom e rolagem movem tudo), mas
        # perto de onde o bloco estava.
        a, _ = nav.captura("/tmp/_bl_val.png")
        alt = Image.open(a).size[1]
        faixa = (TELA[0], max(0.0, (bloco.y - 140) / alt),
                 TELA[2], min(1.0, (bloco.y + 200) / alt))
        b = acha_bloco(bloco.nome, regiao=faixa)
        grupos, _caixa = _glifos_azuis(a, b)
        if not grupos:
            time.sleep(0.8); continue
        import numpy as _np
        from PIL import ImageOps
        rgb = _np.asarray(Image.open(a).convert("RGB"), dtype=int)
        alt = max(g["h"] for g in grupos)
        saida, falhou = "", False
        for g in grupos:
            if g["h"] <= alt * 0.45 and g["w"] >= g["h"] * 1.6:
                saida += "-"; continue
            if g["h"] <= alt * 0.33 and g["w"] <= alt * 0.33:
                saida += "."; continue
            rec = rgb[g["y"] - 4:g["y"] + g["h"] + 4, g["x"] - 4:g["x"] + g["w"] + 4]
            mk = (rec[:, :, 2] > 170) & (rec[:, :, 2] - rec[:, :, 0] > 55) & (rec[:, :, 1] > 95)
            im = Image.fromarray(_np.where(mk, 0, 255).astype("uint8"), "L")
            im = ImageOps.expand(im, border=40, fill=255)
            im.save("/tmp/_bl_glifo.png")
            lido = ""
            for psm in ("10", "8", "7"):
                r = [c for t, *_ in rs.ocr("/tmp/_bl_glifo.png", psm=psm, escala=1,
                                           idioma="eng") for c in t if c.isdigit()]
                if r:
                    lido = r[0]; break
            if not lido:
                falhou = True; break
            saida += lido
        if falhou or not saida.strip("-."):
            time.sleep(0.8); continue
        return saida
    return None


def escreve_textos(bloco, titulo, corpo="", botao=""):
    """Preenche as tres frases de um bloco `Alert` e fecha no OK.

       Os campos sao achados pelo texto-fantasma do PRIMEIRO ('Title
       Message'); os outros dois saem dali por deslocamento medido, porque
       assim que um campo recebe texto o fantasma some e nao da mais para
       procurar por ele."""
    abre_ajustes(bloco)
    a, _ = nav.captura("/tmp/_bl_alerta.png")
    p = nav.acha_texto("title message", arquivo=a)
    if not p:
        raise RuntimeError("nao achei o campo 'Title Message' do Alert")
    for i, texto in enumerate((titulo, corpo, botao)):
        if not texto:
            continue
        nav.clique_seguro(p[0], p[1] + 84 * i); time.sleep(0.5)
        rs.tecla(0, cmd=True); time.sleep(0.2)
        rs.digita_teclas(texto); time.sleep(0.4)
    a, _ = nav.captura("/tmp/_bl_alerta2.png")
    lido = " ".join(t for t, *_ in rs.ocr_forte(a, psm="6")).lower()
    if titulo.split()[0].lower() not in lido:
        raise RuntimeError(f"escrevi {titulo!r} no Alert e nao li de volta")
    fecha_ajustes()
    return True


def valor_com_botao_menos(bloco, positivo, cliques=1):
    """Escreve um valor POSITIVO e clica no botao `−` do painel.

       E este o gesto que a aula ensina, e nao o truque do cursor: o campo
       engole o hifen quando ele e o primeiro caractere, entao mandar a
       crianca digitar `-0.5` deixaria `0.5` na tela dela — a lava DESCENDO —
       sem nada acusar. O botao `−` tira 1 do valor a cada clique: de `0.5`,
       um clique da `-0.5`.

       Capturar pelo mesmo caminho que a crianca segue e o que faz o clipe
       mostrar o gesto certo."""
    p = abre_ajustes(bloco)
    if not p:
        raise RuntimeError(f"o bloco {bloco.nome} nao tem campo 'Current value'")
    nav.clique_seguro(p[0] + 30, p[1] + 68); time.sleep(0.6)
    rs.tecla(0, cmd=True); time.sleep(0.25)
    rs.digita_teclas(str(positivo)); time.sleep(0.5)
    # o `−` fica na propria linha do campo, bem a direita
    menos = (p[0] + 220, p[1] + 70)
    for _ in range(cliques):
        nav.clique_seguro(*menos); time.sleep(0.7)
    fecha_ajustes()
    esperado = round(float(positivo) - cliques, 6)
    texto = f"{esperado:g}"
    lido = le_valor(bloco)
    if lido != texto:
        raise RuntimeError(f"queria {texto} em {bloco.nome} (digitei {positivo} e "
                           f"cliquei {cliques}x no menos) e o bloco mostra {lido!r}")
    return menos


def campo_do_painel(rotulo, valor, abaixo=67, folga=10):
    """Escreve `valor` no campo que fica ABAIXO de `rotulo`, num painel de
       ajustes de bloco. Devolve o ponto clicado.

       Serve para os limites da `Viewable Area` do `Camera` (left/top/right/
       bottom). Da para mexer neles pelos botoes `-` e `+`, mas isso seriam
       doze cliques para ir de 15 a 27; o campo aceita texto, que e um gesto
       so — e um gesto so e o que cabe num passo de aula."""
    a, _ = nav.captura("/tmp/_bl_campo.png")
    p = nav.acha_texto(rotulo, arquivo=a)
    if not p:
        raise RuntimeError(f"nao achei o campo '{rotulo}' no painel do bloco")
    alvo = (p[0] + folga, p[1] + abaixo)
    nav.clique_seguro(*alvo); time.sleep(0.8)
    rs.tecla(0, cmd=True); time.sleep(0.3)        # cmd+A
    rs.digita_teclas(str(valor)); time.sleep(0.8)
    # TAB ANTES DE LER. Com o campo ainda em foco o cursor fica piscando dentro
    # dele e entra na leitura: medido, "27" saiu como "2A". O Tab fecha a
    # edicao sem fechar o painel (o Enter fecharia).
    rs.tecla(48); time.sleep(0.6)
    # LE DE VOLTA, no proprio campo.
    #
    # Esta funcao escrevia e voltava sem olhar — e a irma dela (`cor_do_ceu`)
    # fez exatamente o que se teme: digitou no campo do NOME do nivel em vez do
    # campo da COR, disse que tinha pintado, e uma aula inteira foi capturada
    # de um jogo branco. Aqui o campo e o limite da camera: errado, a fase fica
    # cortada em 15 colunas e so o jogo denuncia.
    # REACHA O ROTULO depois do Tab, em vez de reusar o ponto de antes: o Tab
    # move o foco para o campo seguinte e o painel ANDA. Medido — com a
    # coordenada velha o guarda reprovou um `right` que estava escrito 27,
    # certinho, na tela. Guarda que reprova o caso CERTO e pior que guarda
    # nenhum: ele aborta uma captura boa.
    b, _ = nav.captura("/tmp/_bl_campo2.png")
    p2 = nav.acha_texto(rotulo, arquivo=b) or p
    campo = (p2[0] + folga, p2[1] + abaixo)
    perto = (max(0.0, (campo[0] - 150) / 2940), max(0.0, (campo[1] - 30) / 1604),
             min(1.0, (campo[0] + 230) / 2940), min(1.0, (campo[1] + 34) / 1604))
    # `tem_texto`, nao `ocr_forte`: o `ocr_forte` para na PRIMEIRA leitura com
    # conteudo, e aqui a primeira veio `['o','|']` — lixo das bordas do campo.
    # `tem_texto` percorre a escada inteira atras DO VALOR. Este projeto ja
    # tropecou nisso em cinco lugares; aqui eu repeti o tropeco.
    if not rs.tem_texto(str(valor), arquivo=b, regiao=perto):
        lido = [t.strip() for t, *_ in rs.ocr_forte(b, regiao=perto, psm="7")]
        raise RuntimeError(f"escrevi '{valor}' no campo '{rotulo}' e li {lido} "
                           "de volta — o texto nao entrou no campo certo")
    print(f"   {rotulo} = {valor}", flush=True)
    return alvo


def campo_ao_lado(rotulo, valor, folga=230):
    """Escreve num campo que fica A DIREITA do rotulo, e le de volta.

       `campo_do_painel` serve ao painel do `Camera`, onde o campo fica ABAIXO
       do rotulo. No painel do `Emitter` e do `Timer` ele fica AO LADO:
       `Emit Angle:` [270] [-] [+]."""
    a, _ = nav.captura("/tmp/_bl_lado.png")
    p = nav.acha_texto(rotulo, arquivo=a)
    if not p:
        raise RuntimeError(f"nao achei o campo '{rotulo}' no painel do bloco")
    nav.clique_seguro(p[0] + folga, p[1]); time.sleep(0.6)
    rs.tecla(0, cmd=True); time.sleep(0.3)
    rs.digita_teclas(str(valor)); time.sleep(0.6)
    rs.tecla(48); time.sleep(0.6)                 # Tab tira o cursor de dentro
    b, _ = nav.captura("/tmp/_bl_lado2.png")
    p2 = nav.acha_texto(rotulo, arquivo=b) or p
    campo = (p2[0] + folga, p2[1])
    perto = (max(0.0, (campo[0] - 120) / 2940), max(0.0, (campo[1] - 26) / 1604),
             min(1.0, (campo[0] + 120) / 2940), min(1.0, (campo[1] + 30) / 1604))
    if not rs.tem_texto(str(valor), arquivo=b, regiao=perto):
        lido = [t.strip() for t, *_ in rs.ocr_forte(b, regiao=perto, psm="7")]
        raise RuntimeError(f"escrevi '{valor}' em '{rotulo}' e li {lido} de volta")
    print(f"   {rotulo} = {valor}", flush=True)
    return campo


def escolhe_na_lista(rotulo, nome, dy=0):
    """Abre um seletor do painel de um bloco e escolhe um item pelo nome.

       Serve ao `Object to Emit` do `Emitter` e a lista de tipos do
       `Collision`. Devolve so depois de CONFERIR que o seletor passou a
       mostrar o nome escolhido — clicar na lista e sair sem olhar ja me
       deixou um `Emitter` apontado para o tipo errado.

       `dy` desce do rotulo ate o seletor. Ha duas geometrias de painel no
       Flowlab: no `Emitter` o seletor fica na MESMA linha do rotulo (dy=0), e
       no `Send To` do `Message` ele fica na linha de BAIXO — clicar no rotulo
       ali nao abre lista nenhuma, e o erro que sobra ("nao achei na lista")
       manda procurar o defeito na lista, que nunca chegou a abrir."""
    a, _ = nav.captura("/tmp/_bl_lista0.png")
    p = nav.acha_texto(rotulo, arquivo=a)
    if not p:
        # JA ESCOLHIDO? O seletor deixa de mostrar o ROTULO assim que recebe um
        # valor: `Select Type` vira `Porta`. Repetir uma etapa e rotina aqui, e
        # na segunda vez o erro que sobrava — "nao achei o seletor" — manda
        # procurar o defeito no painel, que estava certo e preenchido.
        #
        # A busca e ancorada no botao `Delete`, que e do PROPRIO painel: sem
        # isso eu estaria procurando a palavra na tela inteira, que e o que me
        # fez aprovar uma escolha que nunca aconteceu.
        d = nav.acha_texto("delete", arquivo=a)
        if d:
            larg, alt = Image.open(a).size
            caixa = (max(0.0, (d[0] - 700) / larg), max(0.0, (d[1] - 700) / alt),
                     min(1.0, (d[0] + 300) / larg), min(1.0, (d[1] + 60) / alt))
            if rs.tem_texto(nome, arquivo=a, regiao=caixa):
                print(f"   {rotulo} ja estava em {nome}", flush=True)
                return True
        raise RuntimeError(f"nao achei o seletor '{rotulo}' no painel")
    p = (p[0], p[1] + dy)
    rs.clique_img(p[0], p[1], escala=2.0, janela=nav.janela()); time.sleep(1.8)
    b, _ = nav.captura("/tmp/_bl_lista1.png")
    # A LISTA PENDURA NO SELETOR, e so nela eu procuro o item.
    #
    # Procurando na tela inteira, esta chamada clicava na primeira ocorrencia
    # da palavra — e numa mesa de blocos ela mora tambem no RÓTULO de um
    # bloco vizinho. Na Aula 7 o `Select Type` do `Message` ficou no texto de
    # fabrica porque o clique foi parar no rotulo `Alvo` do `Collision` ao
    # lado. Nada acusou: tres etapas adiante o placar simplesmente nao subia.
    larg, alt = Image.open(b).size
    lista = (max(0.0, (p[0] - 300) / larg), max(0.0, (p[1] - 30) / alt),
             min(1.0, (p[0] + 450) / larg), min(1.0, (p[1] + 560) / alt))
    q = nav.acha_texto(nome.lower(), arquivo=b, regiao=lista)
    if not q:
        # a lista ROLA quando ha muitos itens
        for _ in range(3):
            rs.roda_img(p[0], p[1] + 200, cliques=3)
            time.sleep(1.0)
            b, _ = nav.captura("/tmp/_bl_lista1.png")
            q = nav.acha_texto(nome.lower(), arquivo=b, regiao=lista)
            if q:
                break
    if not q:
        raise RuntimeError(f"abri a lista de '{rotulo}' e nao achei '{nome}' "
                           "nela, nem rolando")
    rs.clique_img(q[0], q[1], escala=2.0, janela=nav.janela()); time.sleep(1.5)
    c, _ = nav.captura("/tmp/_bl_lista2.png")
    # CONFERE DENTRO DO PAINEL, nao na tela inteira.
    #
    # Com a tela toda, esta leitura de volta aprovava o que nao aconteceu: na
    # Aula 7 o `Select Type` do `Message` ficou no texto de fabrica, e o
    # `tem_texto("alvo")` achou a palavra `Alvo` no rotulo do bloco `Collision`
    # ali do lado. O jogo saiu com a caixa mandando recado para NINGUEM, e a
    # unica coisa que denunciou foi o placar que nao subia, tres etapas
    # adiante — longe da causa.
    larg, alt = Image.open(c).size
    # A FAIXA E GENEROSA MAS AINDA E O PAINEL. Escolher `Choose objects` faz o
    # painel CRESCER (aparecem `Select Type` e `Any Object`), e tudo desce;
    # com a faixa curta a conferencia reprovava uma escolha que estava feita e
    # visivel na tela. Largo o bastante para o painel inteiro, estreito o
    # bastante para nao alcancar o rotulo de um bloco vizinho — que foi o que
    # aprovou o que nao aconteceu.
    painel = (max(0.0, (p[0] - 520) / larg), max(0.0, (p[1] - 160) / alt),
              min(1.0, (p[0] + 520) / larg), min(1.0, (p[1] + 300) / alt))
    achou = rs.tem_texto(nome, arquivo=c, regiao=painel)
    if not achou:
        time.sleep(1.2)          # o painel pode estar terminando de crescer
        c, _ = nav.captura("/tmp/_bl_lista2.png")
        achou = rs.tem_texto(nome, arquivo=c, regiao=painel)
    if not achou:
        raise RuntimeError(f"escolhi '{nome}' em '{rotulo}' e o painel nao o "
                           "mostra (conferido dentro do painel)")
    print(f"   {rotulo} = {nome}", flush=True)
    # DEVOLVE O PONTO DO SELETOR, nao `True`: quando esta chamada e o gesto de
    # um clipe, e este ponto que vira a seta. Com `True` o alvo ficava em
    # (0,0) e a seta apontava para o canto da tela — o guarda dos alvos pegou.
    # O seletor, e nao o item da lista: ele aparece nos DOIS quadros, e o item
    # so existe num estado que nenhum quadro mostra.
    return p


def caixa_do_painel(arquivo=None):
    """A caixa do painel de ajustes ABERTO, achada pelo par `Help`/`Note`.

       Existe porque o rotulo de um campo do painel costuma ter o mesmo texto
       de um PINO do bloco — `delay` e o caso exemplar. Procurando na tela
       inteira, `acha_texto('delay')` ora devolvia o campo, ora o pino, e no
       segundo caso a escrita ia para a mesa: um `Timer` ficou com o atraso de
       fabrica e eu li de volta o painel inteiro como se fosse o campo.

       `Help` e `Note` so existem dentro do painel, e ficam no pe dele."""
    a = arquivo or nav.captura("/tmp/_bl_painel.png")[0]
    ph = nav.acha_texto("help", arquivo=a)
    pn = nav.acha_texto("note", arquivo=a)
    if not (ph and pn):
        return None
    x0 = min(ph[0], pn[0]) - 140
    x1 = max(ph[0], pn[0]) + 260
    y1 = max(ph[1], pn[1]) + 30
    y0 = y1 - 560
    return _regiao_px(x0, y0, x1, y1)


def campo_abaixo(rotulo, valor, dy=55, meia=75):
    """Escreve num campo que fica ABAIXO do seu rotulo, e confere.

       O `campo_ao_lado` serve aos campos do `Emitter`, que ficam na MESMA
       linha do rotulo. Ja o `Max value` do `Random` fica na linha de baixo:
       ali o `campo_ao_lado` escrevia no vazio e lia `['|']` de volta."""
    a, _ = nav.captura("/tmp/_bl_abaixo.png")
    # DENTRO DO PAINEL primeiro: o mesmo texto costuma estar tambem num pino
    # do bloco, e escrever no pino nao acusa nada.
    caixa = caixa_do_painel(a)
    p = nav.acha_texto(rotulo, arquivo=a, regiao=caixa) if caixa else None
    if not p:
        p = nav.acha_texto(rotulo, arquivo=a)
    if not p:
        raise RuntimeError(f"nao achei o rotulo '{rotulo}' no painel")
    nav.clique_seguro(p[0] + 10, p[1] + dy); time.sleep(0.5)
    rs.tecla(0, cmd=True); time.sleep(0.25)
    rs.digita_teclas(str(valor)); time.sleep(0.6)
    b, _ = nav.captura("/tmp/_bl_abaixo2.png")
    # NO CAMPO, nao na tela: `tem_texto` na tela inteira aprovava um '50' que
    # estivesse em qualquer outro lugar do editor — e o campo errado nao
    # acusa nada. A faixa e a do proprio campo, com o cursor ainda dentro
    # dele (sem foco, o cinza claro sobre cinza escuro nao e lido).
    # `meia` e a meia-altura da faixa de leitura. 75 serve ao `Timer`; num
    # painel de campos EMPILHADOS (a `Bar`) a faixa larga apanha o rotulo do
    # campo de cima e a leitura volta `Current value: ...` em vez do numero.
    faixa = (max(0.0, (p[0] - 340) / 2940), max(0.0, (p[1] + dy - meia) / 1604),
             min(1.0, (p[0] + 460) / 2940), min(1.0, (p[1] + dy + meia) / 1604))
    # DUAS LEITURAS da mesma faixa, com psm diferente. Nao e superstic~ao: o
    # mesmo campo com `50` escrito saiu como '50 - +' numa e como 'a +' na
    # outra, e reprovar aqui e reprovar uma escrita que esta certa na tela.
    lido = " ".join([nav.texto_da_tela(regiao=faixa),
                     nav.texto_da_tela(regiao=faixa, psm="7")])
    if (str(valor) not in lido.replace(" ", "")
            and not rs.procura_forte(str(valor), b, regiao=faixa, psm="7")):
        raise RuntimeError(f"escrevi '{valor}' em '{rotulo}' e o campo mostra {lido!r}")
    print(f"   {rotulo} = {valor}", flush=True)
    # O PONTO DO CAMPO, nao `True`: quando esta chamada e o gesto de um clipe,
    # e ele que vira a seta. Com `True` o alvo ficava em (0,0).
    return (p[0] + 10, p[1] + dy)


def _regiao_px(x0, y0, x1, y1):
    """Caixa em PIXELS da tela virada em fracoes, que e o que `regiao` quer."""
    return (max(0.0, x0 / 2940), max(0.0, y0 / 1604),
            min(1.0, x1 / 2940), min(1.0, y1 / 1604))


CONDICOES = {"greater than": ">", "less than": "<", "equal to": "=",
             "not equal to": "!=", "less than or equal to": "<=",
             "greater than or equal to": ">="}


def escolhe_condicao_no_painel(bloco, condicao):
    """Troca a comparacao COM O PAINEL JA ABERTO, e devolve o ponto clicado.

       Existe separada de `poe_condicao` por causa do CLIPE: o gesto que a
       crianca ve e clicar no seletor e escolher a linha, com o painel aberto
       nos dois quadros. Com o painel fechando no meio, a diferenca entre o
       antes e o depois era de 93 px — um `>` virando `<` — e o
       `confere_alvos` (com razao) chamava aquilo de «clipe sem gesto»."""
    condicao = condicao.lower()
    if condicao not in CONDICOES:
        raise RuntimeError(f"nao conheco a comparacao '{condicao}'")
    a, _ = nav.captura("/tmp/_bl_cond.png")
    atual = next((c for c in CONDICOES if nav.acha_texto(c, arquivo=a)), None)
    if atual == condicao:
        print(f"   a comparacao ja e '{condicao}'", flush=True)
        return (bloco.x + 80, bloco.y + 60)
    p = nav.acha_texto(atual or "greater than", arquivo=a)
    if not p:
        raise RuntimeError("nao achei o seletor de comparacao do Filter")
    nav.clique_seguro(*p); time.sleep(1.5)
    b, _ = nav.captura("/tmp/_bl_cond2.png")
    lista = _regiao_px(p[0] - 300, p[1] - 200, p[0] + 400, p[1] + 420)
    achado = rs.procura_forte(condicao, b, regiao=lista, exato=True)
    if not achado:
        raise RuntimeError(f"a comparacao '{condicao}' nao esta na lista")
    t, x, y, w, h = achado
    ponto = (x + w // 2, y + h // 2)
    nav.clique_seguro(*ponto); time.sleep(1.5)
    return ponto


def confere_condicao(bloco, condicao):
    """LE DE VOLTA a comparacao na cara do bloco (com o painel ja fechado)."""
    simbolo = CONDICOES[condicao.lower()]
    c, _ = nav.captura("/tmp/_bl_cond3.png")
    perto = _regiao_px(bloco.x - 60, bloco.y - 40, bloco.x + 330, bloco.y + 180)
    lido = nav.texto_da_tela(regiao=perto)
    if f"input {simbolo}" not in lido.replace("  ", " "):
        raise RuntimeError(f"escolhi '{condicao}' e o bloco mostra {lido!r}")
    print(f"   comparacao = input {simbolo}", flush=True)
    return (bloco.x + 80, bloco.y + 60)


def poe_condicao(bloco, condicao):
    """Troca a comparacao de um `Filter` ('less than', 'equal to'...).

       MEDIDO: o painel do `Filter` tem um SELETOR com as seis comparacoes e,
       embaixo, o numero. Quando o pino `set` tem fio, quem manda e o fio — o
       numero do painel fica de reserva.

       ⚠️ 'less than' esta DENTRO de 'less than or equal to'. Procurar o texto
       solto clica na linha errada, e o bloco passa a comparar outra coisa sem
       nenhum erro na tela. Por isso a linha da lista e casada INTEIRA."""
    abre_ajustes(bloco); time.sleep(1.5)
    escolhe_condicao_no_painel(bloco, condicao)
    fecha_ajustes(); time.sleep(1.0)
    return confere_condicao(bloco, condicao)


def usa_global(bloco, nome, inicial=0):
    """Aponta este `Global Variable` para a global `nome`, criando-a se
       preciso, com `inicial` como valor de partida.

       MEDIDO no prototipo 3155726, e sao quatro telas, nao uma:
         1. o painel do `Global Variable` tem um campo `Global Name` que e uma
            LISTA — clicar no texto dele ja abre;
         2. a lista traz as globais que existem mais `+ Add New Name`;
         3. o `+ Add New Name` abre um DIALOGO proprio, a direita do painel,
            com `Name`, `Type: Number` e **`Default Value`**;
         4. o OK azul do dialogo e OUTRO botao, abaixo do campo do valor — o
            `OK` do painel fica a esquerda e NAO salva a variavel nova.

       O `Default Value` e o que dispensa semear o recorde com `Once` +
       `Number`: a variavel ja nasce em 99, e nenhum tempo de verdade perde
       para ela."""
    abre_ajustes(bloco); time.sleep(1.5)
    a, _ = nav.captura("/tmp/_bl_gv.png")
    if rs.procura_forte(nome, a, regiao=(0.2, 0.05, 1.0, 0.95)):
        print(f"   o bloco ja aponta para '{nome}'", flush=True)
        fecha_ajustes(); time.sleep(0.8)
        return (bloco.x + 80, bloco.y + 60)
    # O CAMPO, nao o texto dele: enquanto nenhuma variavel esta escolhida ele
    # diz `Global Name`, mas depois de escolhida passa a dizer o NOME dela — e
    # procurar pelo texto de fabrica falha exatamente quando o bloco ja tem
    # variavel (que e o caso de todo bloco que se vai TROCAR). O endereco
    # estavel e o rotulo `Name:` do painel, com o campo 70 px abaixo.
    cx = caixa_do_painel(a)
    pr = nav.acha_texto("name:", arquivo=a, regiao=cx)
    p = (pr[0] + 120, pr[1] + 70) if pr else nav.acha_texto("global name", arquivo=a)
    if not p:
        raise RuntimeError("nao achei o campo da variavel no painel da global")
    nav.clique_seguro(*p); time.sleep(1.5)
    a, _ = nav.captura("/tmp/_bl_gv2.png")
    # A LISTA, nao a tela: o nome da global tambem aparece no proprio bloco e
    # no rotulo do `Label`, e procurar na tela inteira clica em outro lugar.
    lista = _regiao_px(p[0] - 300, p[1], p[0] + 300, p[1] + 420)
    ja = nav.acha_texto(nome, arquivo=a, regiao=lista)
    if ja:
        nav.clique_seguro(*ja); time.sleep(1.5)
        c, _ = nav.captura("/tmp/_bl_gv6.png")
        if not rs.procura_forte(nome, c, regiao=(0.2, 0.05, 1.0, 0.95)):
            raise RuntimeError(f"escolhi '{nome}' e o painel nao a mostra")
        print(f"   global escolhida: {nome}", flush=True)
        bloco.nome = str(nome)      # o titulo na mesa passa a ser o da variavel
        fecha_ajustes(); time.sleep(0.8)
        return (bloco.x + 80, bloco.y + 60)

    # `Add New Name` na global e `Add New Variable` na variavel DO OBJETO:
    # procura-se o pedaco que e comum aos dois.
    q = nav.acha_texto("add new", arquivo=a, regiao=lista)
    if not q:
        raise RuntimeError("a lista de globais nao abriu")
    nav.clique_seguro(*q); time.sleep(2.0)

    a, _ = nav.captura("/tmp/_bl_gv3.png")
    # DUAS FORMAS de dialogo, medidas: a da GLOBAL tem `Name`, `Type` e
    # `Default Value`; a da variavel DO OBJETO so tem `Name` e `Type` — o valor
    # de partida dela e sempre 0, e quem quiser outro tem de `set`ar.
    pd = nav.acha_texto("default value", arquivo=a)
    pt = nav.acha_texto("type:", arquivo=a, regiao=(0.3, 0.0, 1.0, 0.7))
    if not pt:
        raise RuntimeError("o dialogo da variavel nova nao abriu")
    if pd:
        # Os tres campos ficam 82 px ABAIXO do rotulo. O dialogo nao nasce
        # sempre do mesmo lado (perto da beirada ele abre para a esquerda): a
        # coluna e a do `Default Value`.
        pn = (pd[0], pt[1] - 82)
        pv = (pd[0], pd[1] + 82)
    else:
        pn = (pt[0] + 150, pt[1] - 82)
        pv = None
        if inicial not in (0, None):
            raise RuntimeError(f"a variavel do objeto nao tem valor de partida "
                               f"({inicial}): ligue um Once -> Number -> set")

    def _escreve_e_le(ponto, texto, quem):
        """Escreve no campo e le DE VOLTA COM ELE AINDA EM FOCO.

           ⚠️ O texto de um campo SEM foco deste dialogo nao e lido pelo OCR —
           cinza claro sobre cinza escuro. A leitura de depois trazia so os
           rotulos, e eu reprovava uma escrita que estava certa na tela. Com o
           foco o campo fica realcado e a leitura sai limpa."""
        nav.clique_seguro(*ponto); time.sleep(0.6)
        rs.tecla(0, cmd=True); time.sleep(0.3)
        rs.digita_teclas(str(texto)); time.sleep(0.8)
        f, _ = nav.captura("/tmp/_bl_gv4.png")
        faixa = _regiao_px(ponto[0] - 350, ponto[1] - 60,
                           ponto[0] + 350, ponto[1] + 60)
        lido = nav.texto_da_tela(regiao=faixa)
        if (str(texto).lower() not in lido.lower().replace(" ", "")
                and not rs.procura_forte(str(texto), f, regiao=faixa, psm="7")):
            raise RuntimeError(f"escrevi {quem} '{texto}' e o campo mostra {lido!r}")
        return f

    b = _escreve_e_le(pn, nome, "o nome")
    if pv:
        b = _escreve_e_le(pv, inicial, "o valor inicial")
    # o OK azul do dialogo: abaixo do ultimo campo, na coluna dos campos
    ancora = pv or (pn[0], pt[1] + 82)
    pok = nav.acha_texto("ok", arquivo=b, regiao=_regiao_px(
        ancora[0] - 500, ancora[1] + 40, ancora[0] + 600, ancora[1] + 400))
    if not pok:
        raise RuntimeError("nao achei o OK azul do dialogo da variavel")
    nav.clique_seguro(*pok); time.sleep(2.0)

    c, _ = nav.captura("/tmp/_bl_gv5.png")
    if not rs.tem_texto(str(nome), arquivo=c):
        raise RuntimeError(f"criei a global '{nome}' e o painel nao a mostra")
    print(f"   global '{nome}' criada, comecando em {inicial}", flush=True)
    bloco.nome = str(nome)
    fecha_ajustes(); time.sleep(0.8)
    # o ponto do BLOCO: o titulo dele acabou de virar o nome da variavel
    return (bloco.x + 80, bloco.y + 60)


def apaga_bloco(bloco):
    """Apaga um bloco da mesa pelo botao `Delete` do painel dele, e confere.

       Serve para sonda e para conserto: um bloco solto em cima de outro nao
       da erro nenhum — os dois ficam empilhados, e o arrasto do fio sai do
       pino errado."""
    abre_ajustes(bloco); time.sleep(1.4)
    a, _ = nav.captura("/tmp/_bl_del.png")
    caixa = caixa_do_painel(a)
    p = nav.acha_texto("delete", arquivo=a, regiao=caixa)
    if not p:
        raise RuntimeError(f"nao achei o Delete no painel de {bloco.nome}")
    nav.clique_seguro(*p); time.sleep(1.8)
    b, _ = nav.captura("/tmp/_bl_del2.png")
    if rs.procura_forte(bloco.nome, b, regiao=bloco.regiao(), exato=True):
        raise RuntimeError(f"apaguei {bloco.nome} e ele continua na mesa")
    print(f"   apaguei o bloco {bloco.nome}", flush=True)
    return True


def campo_acima(rotulo, valor, dy=76):
    """Escreve no campo que fica ACIMA de um rotulo, e le de volta.

       Nasceu do `Delay` do `Timer`: o rotulo dele é COMPRIDO
       (`Delay (1/10th of a second):`) e, em painel estreito, QUEBRA EM DUAS
       LINHAS. Com isso a distancia do rotulo ate o campo muda — `campo_abaixo`
       escrevia na segunda linha do proprio rotulo e lia o rotulo de volta.

       O `Repeat Forever`, logo abaixo do campo, nao quebra nunca: a distancia
       dele ate o campo e fixa, e e por ele que o campo se acha."""
    a, _ = nav.captura("/tmp/_bl_acima.png")
    caixa = caixa_do_painel(a)
    p = nav.acha_texto(rotulo, arquivo=a, regiao=caixa) if caixa else None
    if not p:
        p = nav.acha_texto(rotulo, arquivo=a)
    if not p:
        raise RuntimeError(f"nao achei o rotulo '{rotulo}' no painel")
    ponto = (p[0] + 10, p[1] - dy)
    nav.clique_seguro(*ponto); time.sleep(0.5)
    rs.tecla(0, cmd=True); time.sleep(0.25)
    rs.digita_teclas(str(valor)); time.sleep(0.6)
    b, _ = nav.captura("/tmp/_bl_acima2.png")
    faixa = (max(0.0, (ponto[0] - 350) / 2940), max(0.0, (ponto[1] - 60) / 1604),
             min(1.0, (ponto[0] + 450) / 2940), min(1.0, (ponto[1] + 60) / 1604))
    lido = " ".join([nav.texto_da_tela(regiao=faixa),
                     nav.texto_da_tela(regiao=faixa, psm="7")])
    if (str(valor) not in lido.replace(" ", "")
            and not rs.procura_forte(str(valor), b, regiao=faixa, psm="7")):
        raise RuntimeError(f"escrevi '{valor}' acima de '{rotulo}' e o campo "
                           f"mostra {lido!r}")
    print(f"   campo acima de '{rotulo}' = {valor}", flush=True)
    return ponto


def escreve_texto_do_label(texto):
    """Escreve o TEXTO do `Label` no painel dele, e LE DE VOLTA.

       A caixa de texto fica no ALTO do painel, que e comprido (~800 px); o
       ponto estavel para achar o painel e o rotulo `alignment`, e a caixa fica
       ~290 px acima dele e ~240 px a direita (medido na Aula 8: caixa em
       (1195, 80) numa tela de 2000 px; `alignment` em (1031, 278))."""
    a, _ = nav.captura("/tmp/_bl_lbl.png")
    p = nav.acha_texto("alignment", arquivo=a)
    if not p:
        raise RuntimeError("nao achei o rotulo `alignment` no painel do Label")
    caixa = (p[0] + 240, p[1] - 290)
    nav.clique_seguro(*caixa); time.sleep(0.6)
    rs.tecla(0, cmd=True); time.sleep(0.3)
    rs.digita_teclas(texto); time.sleep(0.8)
    b, _ = nav.captura("/tmp/_bl_lbl2.png")
    # A LEITURA E NA TELA TODA, parte de cima: o texto aparece DUAS vezes — na
    # caixa do painel e, em letra grande, no canto da fase (o `Label` escreve
    # o proprio texto la). Ler so a caixa (branco sobre cinza, varias linhas)
    # devolvia `q` com a palavra certa escrita.
    if not rs.procura_forte(texto, b, regiao=(0.2, 0.05, 1.0, 0.55), psm="6"):
        lido = nav.texto_da_tela(regiao=(0.2, 0.05, 1.0, 0.55))
        raise RuntimeError(f"escrevi {texto!r} no Label e a tela mostra {lido!r}")
    print(f"   texto do Label = {texto}", flush=True)
    return caixa


def cor_do_texto_do_label(hexa):
    """Troca a COR do texto do `Label` (campo hex, ao lado de `text`).

       O `Label` nasce com uma cor ALEATORIA (7872A7, AF6A69…): num titulo
       azul-escuro o roxo some. O campo fica ~172 px acima e ~44 px a direita
       do rotulo `alignment`. Le de volta com o campo ainda em foco."""
    a, _ = nav.captura("/tmp/_bl_lblc.png")
    p = nav.acha_texto("alignment", arquivo=a)
    if not p:
        raise RuntimeError("nao achei o rotulo `alignment` no painel do Label")
    campo = (p[0] + 44, p[1] - 172)
    nav.clique_seguro(*campo); time.sleep(0.6)
    rs.tecla(0, cmd=True); time.sleep(0.3)
    rs.digita_teclas(hexa); time.sleep(0.8)
    b, _ = nav.captura("/tmp/_bl_lblc2.png")
    faixa = _regiao_px(campo[0] - 120, campo[1] - 45, campo[0] + 260, campo[1] + 45)
    lido = nav.texto_da_tela(regiao=faixa).replace(" ", "")
    if hexa.lower() not in lido.lower():
        raise RuntimeError(f"escrevi a cor {hexa} no Label e o campo mostra {lido!r}")
    rs.tecla(48); time.sleep(0.6)
    print(f"   cor do texto do Label = {hexa}", flush=True)
    return campo


def marca_do_bloco(rotulo, quero=True, folga=150):
    """Marca/desmarca uma caixinha do painel de AJUSTES de um bloco.

       (O `comum.marca_caixa` serve ao painel de FISICA, que tem outra
       geometria.) A caixinha fica a esquerda do rotulo; a conferencia e a cor
       dela, como la."""
    for _ in range(3):
        a, _ = nav.captura("/tmp/_bl_cx.png")
        p = nav.acha_texto(rotulo, arquivo=a)
        if not p:
            raise RuntimeError(f"nao achei '{rotulo}' no painel do bloco")
        c = comum_caixinha(a, (p[0], p[1]), folga)
        if c is None:
            raise RuntimeError(f"achei '{rotulo}' e nao a caixinha dele")
        if c[2] == quero:
            print(f"   {rotulo} = {'marcado' if quero else 'desmarcado'}", flush=True)
            return (c[0], c[1])
        rs.clique_img(c[0], c[1], escala=2.0, janela=nav.janela()); time.sleep(1.0)
    raise RuntimeError(f"cliquei tres vezes em '{rotulo}' e ele nao ficou "
                       f"{'marcado' if quero else 'desmarcado'}")


def comum_caixinha(arquivo, ponto, folga=150):
    """(x, y, marcada) da caixinha a ESQUERDA deste rotulo, achada pela cor."""
    import numpy as _np
    im = _np.asarray(Image.open(arquivo).convert("RGB"), dtype=int)
    x0 = max(0, ponto[0] - folga)
    faixa = im[max(0, ponto[1] - 22): ponto[1] + 22, x0: ponto[0]]
    for cor, marcada in ((comum.CAIXA_MARCADA, True), (comum.CAIXA_DESMARCADA, False)):
        m = (_np.abs(faixa - _np.array(cor)) <= 30).all(axis=2)
        if m.sum() >= 150:
            ys, xs = _np.nonzero(m)
            return (x0 + int(xs.mean()), ponto[1] - 22 + int(ys.mean()), marcada)
    return None


# Os PACOTES de `Behavior Bundles` nao desenham um titulo que o OCR leia, e
# nunca levam fio — para eles a mudanca de pixel e a unica prova possivel.
# LISTA EXPLICITA, nao regra pela forma do nome: a minha primeira versao
# isentava "todo nome com espaco", e isso pegava o `Restart Game`, cujo titulo
# na mesa e `RestartGame` e le perfeitamente. Regra pela forma da palavra erra
# o alvo; a lista diz exatamente quem.
SEM_TITULO_LEGIVEL = {"Run & Jump", "Top Down Movement", "Platformer",
                      "Follow Player", "Health Bar", "Ship Controls",
                      "Dangerous"}


def bloco_ou_solta(nome, x, y, titulo=None, exige_titulo=None, regiao=None):
    """O bloco, se ele JA estiver na mesa; senao solta um novo ali.

       Uma etapa de captura costuma ser repetida depois de um erro no meio
       dela. Sem isto, a repetição empilha um segundo bloco igual — e o
       segundo nao aparece na foto que a crianca vai comparar."""
    alvo = titulo or nome
    try:
        return acha_bloco(alvo, regiao=regiao or TELA)
    except RuntimeError:
        # Os pacotes de `Behavior Bundles` nao tem titulo que o OCR leia, e
        # nunca levam fio: para eles a mudanca de pixel e a unica prova
        # possivel. Para todo o resto, o titulo lido e obrigatorio.
        if exige_titulo is None:
            exige_titulo = nome not in SEM_TITULO_LEGIVEL
        return solta(nome, x, y, titulo=titulo, exige_titulo=exige_titulo,
                     regiao=regiao)


def escolhe_tipo_da_colisao(bloco, tipo):
    """No bloco `Collision`, escolhe COM QUEM a batida conta.

       Sem isto o bloco vem em 'Any Type' e dispara com QUALQUER coisa — e uma
       lava que sobe bate primeiro no CHAO, nao no jogador. O jogo reiniciava
       sozinho a cada poucos segundos e a fase ficava impossivel, sem nada no
       editor acusando. Medido em jogo, nao lido no editor.

       O nome que aparece aqui e o TIPO do objeto (o campo `Type` do painel),
       nao o nome dele — por isso a aula manda escrever `Jogador` nos dois."""
    # JA ESTA ESCOLHIDO? Entao nao ha o que fazer.
    #
    # Repetir uma etapa e rotina aqui, e na segunda vez o seletor ja nao diz
    # `Any Type`: diz o tipo escolhido. O erro que sobrava — "nao achei a
    # lista de tipos" — parecia defeito do painel, quando o painel estava
    # certo e o trabalho, feito.
    ja, _ = nav.captura("/tmp/_bl_col_ja.png")
    if rs.procura_forte(tipo.lower(), ja,
                        regiao=bloco.regiao(folga_esq=60, folga_dir=320,
                                            folga_cima=60, folga_baixo=220),
                        psm="6"):
        print(f"   colisao ja estava em {tipo!r}", flush=True)
        return True
    p = abre_ajustes(bloco)
    a, _ = nav.captura("/tmp/_bl_col0.png")
    q = nav.acha_texto("any type", arquivo=a)
    if not q:
        # Sem `Any Type` no painel, o seletor ja mostra ALGUM tipo. Se for o
        # que eu quero, o trabalho esta feito — e foi assim que uma etapa
        # repetida parou com «nao achei a lista de tipos», que soa como painel
        # quebrado quando o painel estava certo e a escolha, no lugar.
        cx = caixa_do_painel(a)
        if cx and rs.procura_forte(tipo.lower(), a, regiao=cx, psm="6"):
            print(f"   colisao ja estava em {tipo!r} (lido no painel)", flush=True)
            fecha_ajustes(); time.sleep(0.8)
            return True
        raise RuntimeError("nao achei a lista de tipos no bloco Collision")
    nav.clique_seguro(q[0], q[1]); time.sleep(1.5)
    a2, _ = nav.captura("/tmp/_bl_col1.png")
    # A LISTA PENDURA NO CABECALHO que acabei de clicar, e e por ele que eu a
    # procuro. O recorte fixo (0.3 .. 0.6) valia so para um `Collision` solto
    # no meio da mesa: com ele mais a esquerda, a lista abre mais a esquerda
    # tambem, e o `Fogo` da Aula 5 caiu em x=800 com a busca comecando em 882.
    # O erro que sobrava — "o tipo nao aparece na lista" — mandava procurar o
    # defeito no campo `Type` do objeto, que estava certo o tempo todo.
    larg, alt = Image.open(a2).size
    faixa = (max(0.0, (q[0] - 250) / larg), max(0.0, (q[1] - 20) / alt),
             min(1.0, (q[0] + 450) / larg), min(1.0, (q[1] + 520) / alt))
    r = nav.acha_texto(tipo.lower(), arquivo=a2, regiao=faixa)
    if not r:
        # A LISTA ROLA. Com quatro ou cinco tipos no jogo ela passa a ter barra
        # e mostra so parte — e o erro que sobrava ("o tipo nao aparece") manda
        # conferir o campo `Type` do objeto, que estava certo o tempo todo (eu
        # fui olhar: o painel do Alvo dizia `Type: Alvo`).
        for _ in range(3):
            rs.roda_img(q[0], q[1] + 200, cliques=3)
            time.sleep(1.0)
            a2, _ = nav.captura("/tmp/_bl_col1.png")
            r = nav.acha_texto(tipo.lower(), arquivo=a2, regiao=faixa)
            if r:
                break
    if not r:
        raise RuntimeError(f"o tipo {tipo!r} nao aparece na lista do Collision, "
                           "nem rolando — o objeto tem esse nome no campo `Type`?")
    nav.clique_seguro(*r); time.sleep(1.2)
    # FECHA PRIMEIRO. O rotulo embaixo do bloco (onde estava 'Any') so troca
    # depois do OK: conferir com o painel ainda aberto reprovava uma escolha
    # que tinha dado certo. E e esse rotulo que a aula manda a crianca olhar.
    fecha_ajustes()
    for tentativa in range(4):
        time.sleep(1.0)
        a3, _ = nav.captura("/tmp/_bl_col2.png")
        # NA FAIXA DO PROPRIO BLOCO, pelo mesmo motivo do `le_valor`: reprocurar
        # so pelo nome devolve o primeiro bloco daquele tipo na mesa.
        alt = Image.open(a3).size[1]
        b = acha_bloco(bloco.nome,
                       regiao=(TELA[0], max(0.0, (bloco.y - 140) / alt),
                               TELA[2], min(1.0, (bloco.y + 200) / alt)))
        lido = " ".join(t for t, *_ in rs.ocr_forte(
            a3, regiao=b.regiao(folga_esq=60, folga_dir=320,
                                folga_cima=60, folga_baixo=220), psm="6")).lower()
        if tipo.lower() in lido:
            return True
    raise RuntimeError(f"escolhi {tipo!r} e o bloco continua sem mostrar isso "
                       f"(li {lido[:70]!r})")


def prepara_menos(bloco, positivo):
    """Abre os ajustes e deixa o valor POSITIVO digitado, pronto para o `−`.

       Serve para gravar o clipe do gesto certo: com o painel ABERTO nos dois
       quadros. Gravando o gesto inteiro (abrir, digitar, clicar, fechar), o
       antes e o depois mostram os dois o painel FECHADO, e a seta aponta para
       um botao que nao existe em nenhum dos dois — foi o que aconteceu com o
       clipe do passo mais importante da Aula 3.

       Devolve o ponto do botao `−`.

       O DESLOCAMENTO E MEDIDO NA FOTO, nao estimado: com `p` no CENTRO do
       rotulo `Current value:`, o `−` fica em +186 e o `+` em +249, a 63 px um
       do outro. O numero antigo, +220, caia bem no VAO entre os dois, mais
       perto do `+` — e e o `+` que ele acertava: tres cliques num `Number`
       zerado devolviam `3` em vez de `-3`, e o bloco ficava mandando a nave
       para o lado errado. Na Aula 3 o mesmo +220 pegou o `−` por pouco, e por
       isso o defeito atravessou uma aula inteira sem aparecer."""
    p = abre_ajustes(bloco)
    if not p:
        raise RuntimeError(f"o bloco {bloco.nome} nao tem campo 'Current value'")
    nav.clique_seguro(p[0] + 30, p[1] + 68); time.sleep(0.6)
    rs.tecla(0, cmd=True); time.sleep(0.25)
    rs.digita_teclas(str(positivo)); time.sleep(0.5)
    return (p[0] + 186, p[1] + 70)


def clica_menos(ponto, cliques=1):
    """Clica no `−` do painel ja aberto. Nao fecha: quem fecha e o chamador."""
    for _ in range(cliques):
        nav.clique_seguro(*ponto); time.sleep(0.7)
    return ponto


def para_simulacao():
    """Para a simulacao da mesa de blocos, se estiver rodando.

       O `Esc` dentro do editor de blocos a LIGA (descobri sem querer, duas
       vezes). Com ela rodando o fundo fica branco, o OCR muda e o detector de
       fio da positivo falso."""
    import numpy as _np
    a, _ = nav.captura("/tmp/_bl_sim.png")
    im = _np.asarray(Image.open(a).convert("L"), dtype=int)
    miolo = im[im.shape[0] // 4: im.shape[0] * 3 // 4,
               im.shape[1] // 3: im.shape[1] * 3 // 4]
    if float(_np.median(miolo)) <= 150:
        return False
    nav.clique_seguro(165, 1473)        # o quadrado de PARAR, canto de baixo
    time.sleep(2.0)
    return True
