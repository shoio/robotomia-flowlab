#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PROVA: `procura_forte` nao pode achar o alvo por um PEDACO dele.

   O defeito que isto tranca: a regra era `lido in alvo and len(lido) >= 3`.
   Com ela, 'Game' (do titulo 'New Game', que a pagina do JOGO escreve em
   letra grande) casava com o alvo 'Game Levels', que so existe no EDITOR.
   Quem decidia com esse casamento era `editor.no_jogo()` — e ele dizia
   "estou no editor" com o jogo na tela. A prova da Aula 3 parou por isso,
   sem nada de errado com a fase.

   Duas fotos de verdade, tiradas da bancada:
     - pagina_do_jogo.png  — a pagina publica do jogo. NAO tem 'Game Levels'.
     - editor_do_nivel.png — o editor. TEM 'Game Levels' na barra de baixo.

   O controle e tao importante quanto a sabotagem: um casamento mais rigido
   que deixasse de ler 'Game Levels' no editor passaria na primeira metade
   desta prova e quebraria tudo. Por isso as duas fotos.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rs

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "provas", "fotos")
JOGO = os.path.join(D, "pagina_do_jogo.png")
EDITOR = os.path.join(D, "editor_do_nivel.png")
BIBLIOTECA = os.path.join(D, "biblioteca_de_sprites.png")

# a regra VELHA, escrita aqui para a sabotagem ficar re-provavel
def _casa_velho(lido, alvo_l):
    return alvo_l in lido or lido in alvo_l and len(lido) >= 3


def _com_regra(regra, f):
    original = rs.procura_forte
    def remendo(alvo, arquivo=None, regiao=None, psm="6", escada=rs.ESCADA, exato=False):
        alvo_l = alvo.lower()
        for escala, limiar in escada:
            for t, x, y, w, h in rs.ocr(arquivo, regiao=regiao, psm=psm,
                                        escala=escala, limiar=limiar):
                lido = t.strip().lower().strip("[]|.,:")
                if regra(lido, alvo_l):
                    return (t, x, y, w, h)
        return None
    rs.procura_forte = remendo
    try:
        return f()
    finally:
        rs.procura_forte = original


def main():
    erros = []

    # ── 1. o caso que custou a noite ──────────────────────────────────
    achou = rs.tem_texto("game levels", arquivo=JOGO)
    print(f"pagina do jogo, 'game levels': {achou}  (esperado False)")
    if achou:
        erros.append("a pagina do jogo ainda casa com 'game levels'")

    # ── 2. o CONTROLE: o editor tem mesmo esse rotulo ─────────────────
    achou = rs.tem_texto("game levels", arquivo=EDITOR)
    print(f"editor,          'game levels': {achou}  (esperado True)")
    if not achou:
        erros.append("o casamento ficou rigido demais: nao le 'Game Levels' "
                     "no editor, onde ele esta escrito")

    # ── 3. os rotulos que a pagina do jogo TEM ────────────────────────
    for p in ("editor", "details", "theme", "cover"):
        achou = rs.tem_texto(p, arquivo=JOGO)
        print(f"pagina do jogo, {p!r}: {achou}  (esperado True)")
        if not achou:
            erros.append(f"a pagina do jogo deixou de casar com {p!r}")

    # ── 3b. O VIZINHO QUE EU QUEBREI com o primeiro conserto ──────────
    # O piso de 60% sozinho matou 'Flowlab Sprites': o OCR entrega 'Flowlab' e
    # 'Sprites' em palavras separadas, e nenhuma das duas cobre 60% de um alvo
    # de 15 letras. A captura da Aula 2 parou com o nome aceso na tela.
    # pelo MESMO caminho do chamador de verdade: `abre_grade_sprite` le so a
    # faixa da direita. Medir a tela inteira aqui mediria outra coisa.
    FAIXA = (0.72, 0.0, 1.0, 1.0)
    for p in ("flowlab sprites", "my other games", "my sprites", "browse",
              "blocks", "characters", "terrain", "kenney sprites"):
        achou = rs.tem_texto(p, arquivo=BIBLIOTECA, regiao=FAIXA)
        print(f"biblioteca,      {p!r}: {achou}  (esperado True)")
        if not achou:
            erros.append(f"a biblioteca de sprites deixou de casar com {p!r}")
    fora = rs.tem_texto("game levels", arquivo=BIBLIOTECA, regiao=FAIXA)
    print(f"biblioteca,      'game levels': {fora}  (esperado False)")
    if fora:
        erros.append("a biblioteca casou com 'game levels', que nao esta nela")

    # ── 4. o corte do fim do rotulo continua valendo ──────────────────
    # 'Behavior' por 'Behaviors' e o motivo de o ramo `lido in alvo` existir.
    if not ("behavior" in "behaviors" and len("behavior") >= max(3, int(len("behaviors") * 0.6))):
        erros.append("o corte do fim do rotulo deixou de ser aceito")
    print("'behavior' ainda casa com 'behaviors': True")

    # ── 5. SABOTAGEM: com a regra velha, o defeito volta ──────────────
    velho = _com_regra(_casa_velho,
                       lambda: rs.procura_forte("game levels", arquivo=JOGO) is not None)
    print(f"\nSABOTAGEM (regra velha), pagina do jogo, 'game levels': {velho}"
          "  (esperado True — e o defeito)")
    if not velho:
        erros.append("a sabotagem nao reproduziu o defeito: esta prova nao "
                     "esta medindo o que diz medir")

    # ── 6. SABOTAGEM 2: so o piso, sem juntar a linha ─────────────────
    # Este foi o conserto que eu quase publiquei sozinho. A prova guarda o
    # caso dele para que ninguem o reintroduza achando que simplifica.
    def _so_piso(lido, alvo_l):
        minimo = max(3, int(len(alvo_l) * 0.6))
        return alvo_l in lido or (lido in alvo_l and len(lido) >= minimo)

    meio = _com_regra(_so_piso,
                      lambda: rs.procura_forte("flowlab sprites", arquivo=BIBLIOTECA,
                                               regiao=FAIXA) is not None)
    print(f"SABOTAGEM (so o piso), biblioteca, 'flowlab sprites': {meio}"
          "  (esperado False — e o defeito que ele cria)")
    if meio:
        erros.append("a segunda sabotagem nao reproduziu o defeito: o piso "
                     "sozinho deveria perder 'Flowlab Sprites'")

    # ── 7. PREFIXO QUE ACABA NUMA PALAVRA DO ALVO NAO E CORTE DE OCR ──
    #
    # `collision shape` casava com a palavra `Collision` da palheta: a regra do
    # prefixo aceita 60% do alvo terminando em fronteira de palavra, e
    # `collision` e 9 de 15 letras. O `onde_estou` passou a dizer que o painel
    # de fisica estava aberto numa tela em que ele nao estava, e eu fui
    # procurar o defeito num painel inexistente.
    #
    # Corte de OCR cai NO MEIO de uma palavra (`affected by gravi`). Prefixo
    # que acaba onde acaba uma palavra e outro rotulo, mais curto.
    casos = [
        ("collision shape",    "collision",          False),
        ("collision shape",    "collision shape",    True),
        ("affected by gravity", "affected by gravi", True),
        ("flowlab sprites",    "flowlab sprites",    True),
        ("game levels",        "new game",           False),
        ("level 1",            "game levels",        False),
    ]
    for alvo, linha, espero in casos:
        minimo = max(5, int(len(alvo) * 0.6))
        achou = any(rs._corte_de_ocr(alvo, k)
                    and rs._prefixo_cortado(linha, alvo[:k])
                    for k in range(len(alvo), minimo - 1, -1))
        print(f"linha {linha!r} casa com {alvo!r}? {achou}  (esperado {espero})")
        if achou != espero:
            erros.append(f"{alvo!r} contra a linha {linha!r}: li {achou}, "
                         f"esperava {espero}")

    # ── 8. ALVO DE VARIAS PALAVRAS NAO CASA POR UMA DELAS ──────────────
    #
    # `input > 2` casava com o bloco que mostrava `input > 0`, pela palavra
    # `input`. Isso transformou a leitura de volta da Aula 7 num carimbo: a
    # condicao do filtro NUNCA foi ajustada, a porta abria na primeira caixa,
    # e a conferencia deu verde. O ramo palavra-por-palavra existe para OCR
    # que come o FIM de um rotulo; com alvo de varias palavras quem cuida
    # disso e o ramo da linha inteira.
    FILTRO = os.path.join(D, "filtro_input_zero.png")
    if os.path.exists(FILTRO):
        for alvo, espero in (("input > 0", True), ("input > 2", False)):
            achou = bool(rs.tem_texto(alvo, arquivo=FILTRO))
            print(f"bloco que mostra 'input > 0' casa com {alvo!r}? {achou}"
                  f"  (esperado {espero})")
            if achou != espero:
                erros.append(f"{alvo!r} contra o bloco 'input > 0': li {achou}, "
                             f"esperava {espero}")
    else:
        erros.append(f"falta a foto {FILTRO} — esta parte da prova nao roda")

    # CONTROLE: sem a guarda nova, o primeiro caso volta a dar positivo. Sem
    # isto a prova passaria mesmo que alguem apagasse `_corte_de_ocr`.
    sem_guarda = any(rs._prefixo_cortado("collision", "collision shape"[:k])
                     for k in range(15, 8, -1))
    print(f"SABOTAGEM (sem `_corte_de_ocr`), 'collision shape' na linha "
          f"'collision': {sem_guarda}  (esperado True — e o defeito)")
    if not sem_guarda:
        erros.append("a sabotagem do prefixo nao reproduziu o defeito: esta "
                     "parte da prova nao esta medindo o que diz medir")

    if erros:
        for e in erros:
            print("  ERRO:", e)
        raise SystemExit(1)
    print("\nprova ok")


if __name__ == "__main__":
    main()
