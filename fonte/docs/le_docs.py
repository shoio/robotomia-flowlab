"""Le a documentacao do Flowlab pelo navegador da bancada.

   O site devolve 403 para requisicao direta, mas a bancada e um Chrome de
   verdade e ja esta logada. A rota `aval` do motor executa JS na pagina, entao
   `document.body.innerText` traz o texto limpo — muito melhor que OCR de
   print."""
import os, sys, time, json
sys.path.insert(0, "/Users/shoio/Coding/robotomia-flowlab/fonte")
os.chdir("/Users/shoio/Coding/robotomia-flowlab/fonte")
import comum, nav, bancada

PAGINAS = [
    ("resources", "https://flowlab.io/resources"),
    ("handbook", "https://flowlab.io/behavior_handbook/"),
    ("behaviors", "https://flowlab.io/resources_behaviors"),
    ("video", "https://flowlab.io/video_tutorials"),
    ("features", "https://flowlab.io/features"),
]
saida = "/private/tmp/claude-501/-Users-shoio/79d5c84f-451d-49d3-bb28-bcb73195eca6/scratchpad/docs"
os.makedirs(saida, exist_ok=True)
for nome, url in PAGINAS:
    try:
        nav.vai(url); time.sleep(5)
        r = bancada._chama("aval", js="document.body.innerText")
        txt = r.get("valor") or ""
        with open(f"{saida}/{nome}.txt", "w") as f:
            f.write(txt)
        print(f"{nome:12} {len(txt):7} caracteres  <- {url}", flush=True)
    except Exception as e:
        print(f"{nome:12} ERRO {e}", flush=True)
