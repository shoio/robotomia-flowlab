import sys, time, json, glob, urllib.request
sys.path.insert(0, "/Users/shoio/Coding/robotomia-flowlab/fonte")
import comum, nav, editor, rs

def aval(js):
    d = json.dumps({"js": js}).encode()
    r = urllib.request.urlopen(urllib.request.Request(
        "http://127.0.0.1:8765/aval", data=d,
        headers={"content-type": "application/json"}), timeout=20)
    return json.loads(r.read()).get("valor")

EM_USO = {open(f).read().strip().rsplit("/", 1)[-1]
          for f in glob.glob("/Users/shoio/Coding/robotomia-flowlab/fonte/aula*/jogo.txt")}

jid = sys.argv[1]
if jid in EM_USO:
    raise SystemExit(f"RECUSADO: {jid} e o jogo de uma aula ({sorted(EM_USO)})")
print("em uso pelas aulas:", sorted(EM_USO), "| apagando:", jid, flush=True)

nav.vai("https://flowlab.io/games/mine", espera=6); time.sleep(6); nav.espera_parar(limite=30)
antes = int(aval('document.querySelectorAll(\'a[href*="/game/edit/"]\').length'))
print("jogos antes:", antes, flush=True)
r = aval(f'''(()=>{{
  const a=document.querySelector('a[href$="/game/edit/{jid}"]');
  if(!a) return "ausente";
  const card=a.closest('div.card'); card.scrollIntoView({{block:'center'}});
  card.querySelector('button[data-toggle=dropdown]').click();
  const del=[...card.querySelectorAll('a.dropdown-item')].find(e=>e.textContent.trim()==='Delete');
  del.click();
  return "abriu";
}})()''')
print("menu/delete:", r, flush=True)
if r != "abriu":
    raise SystemExit(f"{jid} nao esta na lista")
time.sleep(2.5)
a, _ = nav.captura(f"/tmp/_cf_{jid}.png")
if not rs.tem_texto("deleted games can be restored", arquivo=a):
    raise SystemExit("o modal de confirmacao nao apareceu — nao vou clicar as cegas")
p = nav.acha_cor((237, 110, 85), tol=40, regiao=(0.3, 0.3, 0.9, 0.8),
                 minimo=2000, arquivo=a)
if not p:
    raise SystemExit("nao achei o botao de confirmar")
print("confirmando em", p[:2], flush=True)
rs.clique_img(p[0], p[1], escala=2.0, janela=nav.janela()); time.sleep(3)
nav.espera_parar(limite=20)
depois = int(aval('document.querySelectorAll(\'a[href*="/game/edit/"]\').length'))
ainda = int(aval(f'document.querySelectorAll(\'a[href$="/game/edit/{jid}"]\').length'))
print(f"jogos depois: {depois}  (antes {antes})  |  {jid} ainda na lista: {ainda}", flush=True)
for u in sorted(EM_USO):
    n = int(aval(f'document.querySelectorAll(\'a[href$="/game/edit/{u}"]\').length'))
    print(f"   aula com jogo {u}: {'OK' if n else 'SUMIU!!'}", flush=True)
