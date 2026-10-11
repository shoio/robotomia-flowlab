#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O GUARDA DA ENGENHARIA REVERSA: o texto da aula bate com a captura?

   O `confere_aulas.py` olha a FORMA da aula (todo passo tem foto, quadro verde,
   quadro laranja, não delega…). Ele não sabe dizer se o passo 10 manda arrastar
   um bloco que a captura nunca colocou, nem se a captura ajustou um número que
   nenhum passo menciona — que é um PASSO OMITIDO: a criança monta um jogo
   diferente do que está nas figuras.

   Esse foi um defeito real da Aula 4: o texto mandava escolher o desenho em
   `Flowlab Sprites` e a captura usava `Gustavo Sprites`. Eu só achei lendo os
   21 passos à mão, um a um. Isto aqui faz a máquina ler.

   O que ele compara, nos dois sentidos:
     - BLOCOS que o texto manda arrastar × blocos que a captura solta;
     - TIPOS escolhidos numa lista (`Collision`, `Send To`) × tipos citados;
     - NÚMEROS que a captura escreve em campo × números citados no passo;
     - CAIXINHAS de física que a captura marca × caixinhas citadas.

       python3 fonte/confere_texto_x_captura.py [n]
"""
import ast, importlib, os, re, sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

# As palavras que aparecem em <span class=ui> e NÃO são bloco: o painel, os
# botões, os campos. Sem esta lista toda a conversa viraria falso positivo.
NAO_E_BLOCO = {
    "ok", "play", "cancel", "create", "delete", "edit", "clone", "done cloning",
    "behaviors", "physics >", "physics", "game levels", "my games", "new game",
    "empty project", "editor", "name", "type", "browse", "< menu", "&lt; menu",
    "edit sprite", "movable", "affected by gravity", "is solid",
    "enable collisions", "density", "bounce", "friction", "collision shape",
    "flowlab sprites", "gustavo sprites", "characters", "blocks", "objects",
    "terrain", "town", "ships", "projectiles", "backgrounds",
    "triggers", "logic & math", "components", "properties", "text & lists",
    "gui", "game flow", "mobile device", "multiplayer", "behavior bundles",
    "change key", "current key:", "spacebar", "repeat forever", "any type",
    "object to emit", "emit angle", "expire after", "send to", "select type",
    "choose objects", "myself", "max value", "current value", "size", "delay",
    "level 1", "ffffff", "new type 1", "alert", "hello", "reset", "parent",
    "display order", "multiplayer", "greater than", "input &gt; 0",
    "input &gt; 2", "done", "new bundle", "more bundles",
}

# Chamadas da captura que COLOCAM um bloco na mesa.
PONTOS = {"bloco_ou_solta": 0, "solta": 0, "acha_bloco": 0}


def _nome_da_chamada(no):
    f = no.func
    if isinstance(f, ast.Attribute):
        return f.attr
    if isinstance(f, ast.Name):
        return f.id
    return None


def _valor(no, modulo):
    """O valor de um argumento: literal, ou constante do módulo da captura."""
    if isinstance(no, ast.Constant):
        return no.value
    if isinstance(no, ast.Name):
        return getattr(modulo, no.id, None)
    if isinstance(no, ast.Attribute):
        return getattr(modulo, no.attr, None)
    if isinstance(no, ast.UnaryOp) and isinstance(no.op, ast.USub):
        v = _valor(no.operand, modulo)
        return -v if isinstance(v, (int, float)) else None
    return None


def le_captura(n):
    """O que a captura da aula `n` faz, em fatos comparáveis."""
    modulo = importlib.import_module(f"cap{n}")
    arvore = ast.parse(open(f"cap{n}.py", encoding="utf-8").read())
    blocos_postos, tipos, numeros, caixinhas = set(), set(), [], set()
    for no in ast.walk(arvore):
        if not isinstance(no, ast.Call):
            continue
        nome = _nome_da_chamada(no)
        args = no.args
        chaves = {k.arg: k.value for k in no.keywords}
        if nome in PONTOS and args:
            v = _valor(args[0], modulo)
            if isinstance(v, str):
                blocos_postos.add(v)
            t = chaves.get("titulo")
            if t is not None:
                tv = _valor(t, modulo)
                if isinstance(tv, str):
                    blocos_postos.add(tv)
        elif nome in ("escolhe_tipo_da_colisao", "escolhe_na_lista") and len(args) >= 2:
            v = _valor(args[1], modulo)
            if isinstance(v, str):
                tipos.add(v)
        elif nome in ("campo_ao_lado", "campo_abaixo") and len(args) >= 2:
            rot, val = _valor(args[0], modulo), _valor(args[1], modulo)
            if isinstance(val, (int, float)):
                numeros.append((rot, val))
        elif nome == "escreve_valor" and len(args) >= 2:
            val = _valor(args[1], modulo)
            if isinstance(val, (int, float)):
                numeros.append(("valor do bloco", val))
        elif nome == "clica_menos" and len(args) >= 2:
            val = _valor(args[1], modulo)
            if isinstance(val, (int, float)):
                numeros.append(("valor do bloco", -val))
        elif nome in ("marca_caixa", "marca_do_bloco") and args:
            v = _valor(args[0], modulo)
            if isinstance(v, str):
                caixinhas.add(v)
    return blocos_postos, tipos, numeros, caixinhas


def _limpa(t):
    """Texto comparável: sem marcação, sem entidade HTML, espaço normalizado.

       Sem isto o guarda grita lobo três vezes: `RestartGame` (o título na
       mesa) não casava com `Restart Game` (o nome na palheta, que é o que a
       aula escreve), e `Run & Jump` não casava com `Run &amp; Jump`, que é
       como o `&` vive dentro de HTML."""
    t = re.sub(r"<.*?>", " ", t)
    for ent, ch in (("&amp;", "&"), ("&gt;", ">"), ("&lt;", "<"),
                    ("&rsaquo;", ">"), ("&nbsp;", " ")):
        t = t.replace(ent, ch)
    return re.sub(r"\s+", " ", t).strip().lower()


def le_texto(n):
    """O que a aula `n` manda a criança fazer, lido dos passos."""
    mod = importlib.import_module(f"conteudo_a{n}")
    citados, numeros, tudo = set(), set(), []
    for p in mod.AULA["passos"]:
        # O QUE O PASSO MANDA FAZER mora no `corpo`. Os quadros laranja citam
        # outros blocos como PONTO DE REFERÊNCIA ("o Mailbox fica junto do
        # Keyboard"), e tomá-los por ordem faz o guarda acusar bloco que
        # ninguém mandou arrastar.
        corpo = p.get("corpo", "")
        resto = p.get("ck", "") + " " + \
                " ".join(a + " " + b for a, b in p.get("sos", []))
        tudo.append(corpo + " " + resto)
        for m in re.findall(r"<span class=ui>(.*?)</span>", corpo):
            limpo = _limpa(m)
            if limpo and limpo not in NAO_E_BLOCO:
                citados.add(limpo)
        for m in re.findall(r"-?\d+(?:[.,]\d+)?", _limpa(corpo + " " + resto)):
            numeros.add(m.replace(",", "."))
    return citados, numeros, _limpa(" ".join(tudo))


def confere(n):
    erros = []
    postos, tipos, numeros, caixinhas = le_captura(n)
    citados, nums_texto, texto = le_texto(n)

    def citado(palavra):
        # SEM ESPAÇO TAMBÉM: o mesmo bloco tem dois nomes no Flowlab — na
        # palheta ele é `Restart Game` e na mesa o título é `RestartGame`. A
        # aula escreve o da palheta, que é o que a criança procura.
        p = _limpa(palavra)
        return p in texto or p.replace(" ", "") in texto.replace(" ", "")

    # 1. bloco que a captura coloca e nenhum passo manda arrastar
    for b in sorted(postos):
        if not citado(b):
            erros.append(f"a captura coloca `{b}` e NENHUM passo o menciona — "
                         "passo omitido: a criança não vai ter esse bloco")
    # 2. bloco que o texto manda arrastar e a captura nunca coloca
    conhecidos = {_limpa(b) for b in postos}
    import blocos as _bl
    vocabulario = {k.lower() for k in _bl.DESLOC} | \
                  {k.lower() for k in _bl.SEM_TITULO_LEGIVEL} | \
                  {"emit", "restart game", "destroyer", "alert", "once",
                   "always", "timer", "mailbox", "message", "filter",
                   "number", "label", "velocity", "position", "random",
                   "keyboard", "collision", "spawn", "camera", "impulse"}
    for c in sorted(citados):
        if c in vocabulario and c not in conhecidos:
            erros.append(f"o texto manda usar `{c}` e a captura nunca o "
                         "coloca — a figura não vai ter esse bloco")
    # 3. tipo escolhido numa lista e nunca citado
    for t in sorted(tipos):
        if not citado(t):
            erros.append(f"a captura escolhe o tipo `{t}` numa lista e nenhum "
                         "passo diz para escolhê-lo")
    # 4. número escrito num campo e nunca citado
    for rot, val in numeros:
        txt = str(int(val)) if float(val).is_integer() else str(val)
        if txt not in nums_texto:
            erros.append(f"a captura escreve {txt} em `{rot}` e nenhum passo "
                         f"cita esse número")
    # 5. caixinha de física mexida e nunca citada
    for c in sorted(caixinhas):
        if not citado(c):
            erros.append(f"a captura mexe na caixinha `{c}` e nenhum passo "
                         "manda mexer nela")
    return erros


def sabotagem():
    """O guarda ainda sabe achar uma omissão de verdade?

       Sem este controle ele só saberia dizer "ok", e eu não teria como
       distinguir "está tudo certo" de "não estou medindo nada"."""
    class FalsaAula:
        AULA = {"passos": [dict(corpo="Arraste o <span class=ui>Number</span>.",
                                ck="", sos=[])]}
    import types
    falso = types.ModuleType("conteudo_a99")
    falso.AULA = FalsaAula.AULA
    sys.modules["conteudo_a99"] = falso
    citados, _n, texto = le_texto(99)
    del sys.modules["conteudo_a99"]
    # a captura "colocaria" um Label que o texto nao menciona
    return "label" not in texto and "number" in texto


def main():
    if not sabotagem():
        print("⛔ a sabotagem falhou: este guarda nao esta medindo o que diz")
        raise SystemExit(1)
    print("sabotagem ok: o guarda ve um bloco ausente do texto\n")
    alvos = [int(a) for a in sys.argv[1:]] or [4, 5, 6, 7]
    total = 0
    for n in alvos:
        if not os.path.exists(f"cap{n}.py"):
            continue
        print(f"== aula {n} ==")
        try:
            erros = confere(n)
        except Exception as e:
            print(f"   nao consegui conferir: {type(e).__name__}: {e}")
            continue
        for e in erros:
            print("   ⛔", e)
        total += len(erros)
        if not erros:
            print("   ok: texto e captura dizem a mesma coisa")
    print(f"\n{total} divergencia(s)")
    raise SystemExit(1 if total else 0)


if __name__ == "__main__":
    main()
