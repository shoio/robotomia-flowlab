# Estado do curso de Flowlab — 03-10-2026, 19h

**A animacao com o mouse esta pronta** e a maquina monta o jogo inteiro. **A
Aula 1 ainda nao fecha**: o jogo nao faz o que a aula promete — a moeda nao
some. Tudo o que foi medido hoje esta abaixo, para a proxima sessao nao
repetir nenhuma descoberta.

## Pronto hoje

- **`gif.mouse(...)`**: desenha um mouse ao lado do cursor com o botao
  ESQUERDO ou DIREITO aceso em vermelho, nos quadros do clique. E o que o
  dono pediu: a crianca ve qual botao apertar.
- **`cap1.confere_fase()`**: olha o nivel e reprova se o chao tiver vao, se o
  jogador ou a moeda nao estiverem sobre ele, ou se estiverem em linhas
  diferentes. Pegou tres fases tortas seguidas.
- **Persistencia provada**: o pacote de comportamento SO fica salvo com pausa
  antes de fechar (2,5 s). Sem isso ele some em silencio — o jogador nao anda
  e nada no editor acusa. A captura agora reabre o objeto e CONFERE.
- **28 fotos e 6 animacoes** registradas de gestos reais em `fonte/aula1/`.

## Medidas da tela (pagina em 100%)

| medida | valor |
|---|---|
| canto da area do nivel | (958, 415) |
| celula da grade | 64 px |
| nivel | 16 x 12 celulas |
| OK do painel do objeto | branco sobre azul `(126,168,224)`, **altura varia** |
| passo do jogador, toque de 0,15 s | **344 px** (5 celulas) |
| passo do jogador, toque de ate 0,08 s | **0 px** |

## Dialogos que aparecem e travam tudo (todos tratados em `nav.DIALOGOS`)

1. "Sair do site?" → **Sair**
2. "Atualizar o site?" → **Cancelar** (recarregar perde o que nao foi salvo)
3. "Recover unsaved work" → **Recover** (o titulo tambem diz 'Recover': o
   botao e a ocorrencia de BAIXO)
4. "Deseja ativar o Ditado?" (macOS, disparado pelas minhas teclas repetidas)
   → **Agora Nao**

## O que trava a Aula 1, com o que ja sei

A moeda **nao some** quando o jogador passa por ela. O que esta medido:

- a logica da moeda **existe e fica salva**: `Collision (Any) -> Destroyer.in`,
  conferida depois de reabrir;
- a moeda e **solida e estatica** (`is solid` marcado, `movable` desmarcado);
- o jogador e **solido e movel**, com o pacote `Run & Jump` salvo;
- num toque de 0,15 s o jogador vai de x=1373 a x=1717 — e a moeda estava em
  x=1470, no caminho.

Isso e contraditorio: com os dois solidos, o jogador devia ser BARRADO pela
moeda, nao atravessa-la. Tres hipoteses, em ordem de custo:

1. o que eu medi como "jogador em 1717" nao era o jogador (outro azul da
   tela) — **medir dentro do recorte do nivel**, como `confere_fase` ja faz;
2. o pacote `Run & Jump` faz o boneco PULAR por cima da moeda (o impulso de
   344 px num toque e alto demais para um passo);
3. a colisao nao vale porque os dois estao em grupos de colisao diferentes.

A primeira se resolve em cinco minutos e e a mais provavel.

---

## 1. O que esta pronto

| peca | estado |
|---|---|
| `PLANO.md` | 12 aulas, um jogo por aula, formato herdado do curso de Roblox |
| `nav.py` | **funciona**: navega, espera a tela assentar, captura, acha por cor e por texto, fecha dialogo do Chrome |
| `rs.py` | herdado do Roblox + `ocr_forte` / `procura_forte` (escada de escalas) |
| `blocos.py` | **parcial**: soltar e achar bloco funcionam; achar as bolinhas dos pinos funciona com a pagina em 150% e falha em 100% |
| gerador do site | herdado inteiro do Roblox (`gera_curso.py`, `build_curso.py`, `faz_pdfs.py`, `para_jpeg.py`) — ainda sem nenhuma aula para gerar |
| repositorio | local, em `~/Coding/robotomia-flowlab`. **Nao publicado**: criar repositorio publico foi recusado pela politica de permissao. Falta um comando seu |

---

## 2. O caminho do editor, ja percorrido e medido

Cada linha abaixo eu fiz de verdade nesta madrugada, na conta dele:

1. `flowlab.io` → **My Games** (topo direito) → lista em `flowlab.io/games/mine`.
   A conta e **INDIE, jogos ilimitados** — da para um jogo por aula.
2. **+ New Game** (botao verde `(99,173,97)`): o OCR **nao le** texto branco
   sobre botao colorido; achar pela cor funciona.
3. Abre um escolhedor com duas miniaturas: **Empty Project** e **Flowlab
   Tutorial**. O rotulo NAO e clicavel — quem responde e a miniatura.
4. Editor: canvas branco do nivel e barra de baixo com
   **Play · Library · Game Levels · Layer · Settings**, e "Saved" automatico.
5. **Library** com o projeto vazio diz: *"No objects yet! Click the grid to
   create some."*
6. **Clicar na grade** abre um menu radial **Create / Cancel**.
7. **Create** abre o painel do objeto: `edit sprite`, **Behaviors**, `Type`,
   `Name`, `Parent`, `Reset`, `Display Order`, `Multiplayer`, `OK`, `Physics >`.
8. **Behaviors** abre o editor de comportamento: palheta a esquerda
   (Triggers, Logic & Math, Components, Properties, Text & Lists, GUI,
   Game Flow, Mobile Device, Multiplayer, **Behavior Bundles**), area de
   trabalho, e no rodape as ferramentas e o **OK**.
9. **Arrastar** um bloco da palheta para a area **funciona**.
10. **Ligar fio** de bolinha a bolinha **funciona** (feito a mao e conferido).
11. O Flowlab avisa sozinho quando a montagem nao faz sentido — apareceu
    *"This object is not movable, so Impulse will have no effect"*. Isso e
    material de aula de graca.
12. Em **Behavior Bundles** ha prontos: **Run & Jump**, **Dangerous**,
    **Ship Controls**, e "More Bundles". Um bundle da movimento sem nenhum fio
    — e o caminho certo para a Aula 1 e a 2.

---

## 3. As armadilhas que custaram a noite (todas medidas)

1. **O dialogo invisivel.** O Chrome desenha *"Sair do site? As alteracoes
   podem nao ser salvas"* numa camada que a captura **por janela** nao
   enxerga. Eu vi a tela "congelada" por quase uma hora com a navegacao
   travada por um dialogo que nao aparecia nas minhas fotos.
   **Conserto:** `nav.cap_tela` captura o RETANGULO DA TELA, nao a janela, e
   `nav.fecha_dialogo` reconhece e responde.
2. **Duas listas de janelas que discordam.** Para o sistema a janela do
   Flowlab era a primeira; para o AppleScript a da frente era um PDF. Eu
   navegava numa e fotografava a outra. **Conserto:** casar pelo titulo, e
   quando o titulo vem vazio (o `/games/mine` vem), levantar a janela e usar a
   ordem do sistema com o Chrome na frente.
3. **Ampliar nem sempre ajuda.** Com a pagina em 150%, o titulo de um bloco
   **nao e lido** em escala 2 e **e lido** em escala 1. O contrario vale para
   o rotulo de pino. **Conserto:** `ocr_forte` percorre uma escada de
   (escala, limiar) — e `procura_forte` para quando acha **o que eu procuro**,
   nao quando a leitura tem qualquer coisa.
4. **Texto branco sobre botao colorido nao e lido** em nenhum modo de
   segmentacao. **Conserto:** `acha_cor`.
5. **Repetir sem desfazer empilha lixo.** Tres blocos `Destroyer` empilhados
   porque a conferencia falhou e o retry soltou outro. **Conserto:** `Cmd+Z`
   antes de repetir.
6. **A palheta e sanfona** e, com zoom, ela passa do tamanho da tela.
7. **O bloco nasce centrado** no ponto onde se solta, nao pelo canto.

8. **Sair do editor sem salvar perde os blocos.** Ao voltar, o Flowlab
   oferece *"Recover unsaved work — This object has unsaved behavior edits
   from your last session. [Recover] [Discard]"*. Bom para a aula (a crianca
   vai ver isso), e um passo obrigatorio no roteiro de captura.
9. **Crescer a regiao para medir o bloco VAZA** para o vizinho: a erosao 3x3
   nao mata o fio, e dois blocos ligados viram uma caixa so (medi 1263x639
   para um bloco de ~230x45). E aqui que a proxima sessao tem de comecar.

---

## 4. O que falta para a primeira aula sair

1. **Fechar `blocos.bolinhas`** para o zoom de 100%. Duas tentativas ja
   falharam e estao no arquivo, com o motivo: varredura por linha (para cedo
   no miolo) e crescimento de regiao (vaza pelo fio). A terceira ideia, nao
   tentada: procurar as bolinhas em volta do TITULO do bloco, limitando a
   busca a uma faixa de altura fixa por TIPO de bloco (o Timer tem 3 entradas,
   o Destroyer 1) — a contagem conhecida vira a conferencia.
2. Com isso, escrever `cap1.py` no molde do `cap10.py` do Roblox: etapas
   nomeadas, captura a cada gesto, e **prova no fim** (jogar e ver a moeda
   sumir).
3. Escrever `conteudo_a1.py` a partir do que a captura registrou, nunca de
   cabeca.
4. `build_curso.py` já monta o site; falta so a aula existir.

**Estimativa honesta:** o primeiro item e o unico incerto. Feito ele, uma aula
por sessao e realista — foi o ritmo do curso de Roblox depois que a maquina
ficou de pe.

---

## 5. Coisas da conta dele que eu mexi

- Criei **um jogo extra** na conta (aparece como "New Game", editado em
  27-09) — era o meu campo de testes. Da para apagar sem perda.
- **Deixei o zoom da pagina do Flowlab em 100%** (mexi nele durante a noite).
- Nao mudei nenhuma configuracao do Chrome. Tentei ligar *"Permitir o
  JavaScript do Eventos da Apple"* pelo menu; o Chrome **ignora** o clique
  programatico, entao continua desligado, como estava.
