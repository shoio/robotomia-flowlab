#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PROVA: nenhuma tabela do `blocos.py` tem chave repetida.

   O defeito que isto tranca: `PORTAS` tinha `Once`, `Impulse` e `Label` duas
   vezes cada. Em Python a segunda chave apaga a primeira **sem um aviso
   sequer** — e as que venciam eram as escritas de cabeca, nao as medidas na
   tela: o `Label` ficava com `text/show/hide` quando ele tem `text/alpha/x/y`
   dos dois lados, e o `Impulse` perdia duas saidas.

   O dicionario pronto nao denuncia nada: `len(PORTAS)` ja vem certo e
   `PORTAS["Label"]` devolve a errada com cara de verdade. Quem precisa ser
   lido e o CODIGO-FONTE, e e por isso que esta prova usa `ast` em vez de
   importar o modulo.
"""
import ast, os, sys

AQUI = os.path.dirname(os.path.abspath(__file__))


def duplicatas(caminho):
    """[(tabela, chave, linha)] para toda chave repetida num dict literal."""
    arvore = ast.parse(open(caminho, encoding="utf-8").read())
    achados = []
    for no in ast.walk(arvore):
        if not isinstance(no, ast.Assign) or not isinstance(no.value, ast.Dict):
            continue
        nome = getattr(no.targets[0], "id", "?")
        vistas = {}
        for ch in no.value.keys:
            if not isinstance(ch, ast.Constant) or not isinstance(ch.value, str):
                continue
            if ch.value in vistas:
                achados.append((nome, ch.value, vistas[ch.value], ch.lineno))
            else:
                vistas[ch.value] = ch.lineno
    return achados


def main():
    erros = []
    for arquivo in ("blocos.py", "comum.py", "editor.py", "rs.py", "nav.py"):
        caminho = os.path.join(AQUI, arquivo)
        if not os.path.exists(caminho):
            continue
        for tabela, chave, antes, depois in duplicatas(caminho):
            erros.append(f"{arquivo}: `{tabela}` tem {chave!r} nas linhas "
                         f"{antes} e {depois} — a de baixo apaga a de cima")
        print(f"{arquivo}: ok")

    # CONTROLE: a prova precisa saber achar uma duplicata, senao ela so sabe
    # dizer "ok". Um arquivo de mentira, com o defeito dentro.
    teste = os.path.join("/tmp", "_tabela_com_duplicata.py")
    open(teste, "w").write('T = {\n "a": 1,\n "b": 2,\n "a": 3,\n}\n')
    if not duplicatas(teste):
        erros.append("a sabotagem nao reproduziu o defeito: esta prova nao "
                     "esta medindo o que diz medir")
    else:
        print("SABOTAGEM (arquivo com 'a' repetido): achou  (esperado achar)")
    os.remove(teste)

    if erros:
        for e in erros:
            print("  ERRO:", e)
        raise SystemExit(1)
    print("\nprova ok")


if __name__ == "__main__":
    main()
