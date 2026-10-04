#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O GUARDA do conteudo. Roda no comeco de todo build e PARA o build se
   reprovar.

   Cada regra nasceu de um defeito real do curso de Roblox ou desta noite de
   Flowlab — nenhuma e preferencia de estilo.
"""
import os, re, sys, glob

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# frases que EMPURRAM o trabalho para outro lugar. O aluno le um passo por vez:
# um passo que delega parece completo na leitura continua e deixa a crianca
# parada na frente da tela.
DELEGA = ["como na aula passada", "igual ao de cima", "use a receita",
          "voce ja sabe", "do mesmo jeito de antes", "como antes"]


def confere(aulas=None):
    erros = []
    if aulas is None:
        import conteudo_a1, conteudo_a2
        aulas = [conteudo_a1.AULA, conteudo_a2.AULA]

    for A in aulas:
        n, slug = A["n"], A["slug"]

        def erra(m):
            erros.append(f"aula {n}: {m}")

        passos = A["passos"]
        if not (19 <= len(passos) <= 20):
            erra(f"tem {len(passos)} passos; o padrao e 19 ou 20 (o que cabe em 50 min)")

        # 1. numeracao sem buraco
        for i, p in enumerate(passos, 1):
            if p["n"] != i:
                erra(f"passo na posicao {i} esta numerado {p['n']}")

        for p in passos:
            onde = f"passo {p['n']}"

            # 2. toda foto existe
            img = p.get("img")
            if not img:
                erra(f"{onde}: sem foto")
            elif not os.path.exists(img):
                erra(f"{onde}: foto sumida {img}")

            # 3. todo clipe citado existe
            cl = p.get("clipe")
            if cl and not os.path.exists(os.path.join(slug, "gifs", cl)):
                erra(f"{onde}: clipe sumido {cl}")

            # 4. quadro verde e quadro laranja obrigatorios
            if not p.get("ck", "").strip():
                erra(f"{onde}: sem quadro verde (como saber que deu certo)")
            if not p.get("sos"):
                erra(f"{onde}: sem quadro laranja (o que fazer se travar)")
            for s in p.get("sos", []):
                if len(s) != 2 or not s[0].strip() or not s[1].strip():
                    erra(f"{onde}: socorro incompleto {s!r}")

            # 5. nenhum passo delega
            corpo = (p.get("corpo", "") + " " + p.get("ck", "")).lower()
            for frase in DELEGA:
                if frase in corpo:
                    erra(f"{onde}: delega com '{frase}' — repita o procedimento")

            # 6. passo que manda clicar tem de dizer ONDE.
            # So o CORPO conta: juntar o quadro verde aqui fazia a regra passar
            # por causa de um <span class=ui> que estava no quadro, nao na ordem.
            so_corpo = p.get("corpo", "").lower()
            if re.search(r"\bclique\b", so_corpo) and not re.search(
                    r"(em <span class=ui>|no <span class=ui>|na <span class=ui>|dentro|canto|coluna|fileira|linha|casa|bolinha|figura|caixinha|ponta|barrinha|quadradinho|metade)", so_corpo):
                erra(f"{onde}: manda clicar e nao diz onde")

        # 7. o fim da aula promete alguma coisa jogavel
        if "link" not in A.get("fim", "").lower():
            erra("o fecho da aula nao fala do link do jogo")

    return erros


if __name__ == "__main__":
    e = confere()
    for m in e:
        print("  !!", m)
    print(f"  {len(e)} problema(s)")
    raise SystemExit(1 if e else 0)
