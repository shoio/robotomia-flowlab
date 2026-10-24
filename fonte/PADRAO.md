# Como se faz uma aula de Flowlab da Robotomia

Leia isto **antes** de começar a próxima aula. Ele existe porque a Aula 3
custou uma tarde inteira redescobrindo coisas que já estavam escritas em algum
lugar — aqui, no `PADRAO.md` do curso de Roblox, ou na memória.

---

## 0. O que vem de graça do curso de Roblox

O formato da aula é o mesmo e **não se reinventa**: leia
`~/Coding/robotomia-roblox/fonte/PADRAO.md` §1, §2 e §7. O que vale igual:

- 19–21 passos, 50 minutos, projeto novo a cada aula, termina jogável
  (o teto subiu de 20 para 21 quando o passo do céu entrou nas Aulas 2 e 3);
- **nenhum passo supõe que o aluno já sabe fazer aquilo** — repita o
  procedimento inteiro, mesmo repetindo o vizinho;
- quadro verde (`ck`) descreve o que **aparece na tela**;
- quadro laranja (`sos`) é sintoma na voz da criança + conserto;
- copiar o `conteudo_aN.py` mais parecido em vez de começar do zero.

A única diferença de formato: aqui não há bloco de código digitado. No lugar
dele vai a **lista dos blocos e dos fios**.

---

## 1. O laço de uma aula

1. **Provar a mecânica** no editor de verdade, antes de escrever uma linha.
2. Escrever o roteiro dos 19 a 21 passos, um por linha.
3. `capN.py` constrói o jogo capturando a cada gesto.
4. Clipes, JPEG, guardas.
5. **Jogar** e provar as promessas, uma a uma.
6. **Engenharia reversa**: reler como aluno, um passo por vez.
7. **Olhar a folha de contato** (`folha_de_contato.py aulaN`): todas as figuras
   lado a lado, numa imagem só. Dois defeitos desta madrugada só apareceram
   assim — um clipe do nível BRANCO no meio de dezesseis de céu escuro, e três
   passos mostrando o cenário PRONTO onde o texto promete o cenário pela
   metade. Os arquivos existiam, abriam e passavam em todos os guardas.
8. Build, publicar, conferir **no ar**.

O passo 1 é onde mora quase todo o tempo. Os §2 e §3 abaixo são para encurtá-lo.

---

## 2. O que a mesa de blocos já ensinou (não redescubra)

| fato medido | consequência |
|---|---|
| O painel de ajustes de um bloco abre com **clique LENTO** (`rs.clique_lento`) | clique comum e duplo só selecionam; o arrasto move |
| O campo `Current value` **engole o hífen** quando ele é o primeiro caractere | negativo só pelo botão `−`, que tira 1 por clique |
| `rs.digita_teclas` cai no mapa **americano** | sem `ê`, sem `ç`: texto que vai PARA DENTRO do jogo é escolhido sem acento |
| ⛔ `rs.digita` (Unicode) **não se usa no Chrome** | ele pendura o caractere no código de tecla 0 e o Chrome lê como atalho — abriu DevTools, modo dispositivo e painel lateral de uma vez |
| O painel do objeto nasce **do lado da casa clicada** | procurar só na metade direita da tela perde o painel da lava |
| A caixinha do painel se acha **pela cor**, não por deslocamento | o rótulo é achado pelo centro do texto, e o centro anda com o tamanho da palavra |
| O OCR **não lê** um recorte pequeno de tela escura | confira bloco solto na mesa INTEIRA (`acha_bloco`), não na vizinhança do ponto onde soltou |
| O OCR **não lê** os botões do diálogo do Chrome | responda pelo teclado: Enter = botão azul, Esc = cinza |
| Soltar bloco **perto da beirada direita** faz a mesa rolar | solte com x ≤ 1700 |
| O `Number` tem três entradas | `get` é o gatilho; ligar no `set` não faz sair nada |
| `Velocity y` **positivo é para BAIXO** | subir é número negativo |
| A barra de baixo diz **em que tela estou** | `Library/Game Levels/Layer/Settings` = editor |
| Arrastar da palheta precisa de **pressão longa** antes de mover | com 0,45 s a mesa fica IGUAL, sem erro nenhum; com 1,2 s o mesmo gesto solta o bloco. `solta` escala 0,6 → 1,2 → 2,0 |
| O bloco **não nasce onde eu soltei** | o endereço é `acha_bloco(titulo)`, lido na tela; a coordenada do arrasto é só a mira |
| Arrastar um bloco que JÁ existe funciona com o gesto curto | foi assim que separei «o arrasto está quebrado» de «a palheta não registrou» |

E a tabela de velocidade, já medida: `-1` sobe 55 px/s (a tela em 14 s),
`-0.5` sobe 27 px/s (28 s).

---

## 2a. ⚠️ LEIA A DOCUMENTAÇÃO ANTES DE MEDIR

O Flowlab **tem documentação**, e eu passei uma noite inteira descobrindo por
tentativa coisas que estão escritas. Está tudo em `fonte/docs/`, baixado pela
bancada (o site devolve 403 para requisição direta; `docs/le_docs.py` passa
pelo navegador logado e usa `document.body.innerText`):

| arquivo | o que é |
|---|---|
| `handbook.txt` | **Behavior Handbook** — toda propriedade, entrada e saída de cada bloco |
| `guia_essencial.txt` | o guia oficial em PDF, convertido |
| `behaviors.txt` | programação com behaviors |
| `features.txt`, `resources.txt`, `video.txt` | recursos e lista de vídeos |

**A regra:** antes de medir o comportamento de um bloco na tela, procure-o no
handbook. `grep -i "camera" fonte/docs/handbook.txt` responde em um segundo o
que me custou horas.

---

## 2b. Tela, nível e câmera — o que eu entendi errado

Isto é o erro mais caro que cometi no curso, e vale a seção inteira.

**`Width`/`Height` em Settings é o tamanho da TELA, não do nível.** O guia diz
«change the *screen* width and height». O nível é tão grande quanto você
construir: **dá para pôr peça fora da folha branca** — provado, a folha ficou
uma tira estreita e o chão continuou inteiro, fora dela.

Eu vi a folha mudar de tamanho junto com o número e concluí «nível = tela,
logo a câmera não tem o que rolar». A observação era verdadeira; a conclusão eu
nunca testei, e foi ela que me fez descartar a câmera e alargar a Aula 2 pelo
lado errado — eu alarguei a JANELA, e por isso as peças ficaram menores.

### O jeito certo de fazer fase comprida

1. **Tela fica em 16×12.** É o tamanho em que o sprite de 32 px aparece bem.
2. **Construa além da folha branca.** O nível cresce com as peças.
3. **Um bloco `Camera` no jogador.** `Autoscroll X/Y` já vem marcado: a vista
   segue o objeto, centralizando-o.
4. **A `Viewable Area`** (left/top/right/bottom, em casas da grade) limita até
   onde a câmera vai — ajuste para cobrir o nível inteiro.

### O que o handbook diz, e eu não sabia

| fato | consequência |
|---|---|
| O `Camera` é **`GAME LAYER ONLY`** | não funciona em objeto do fundo nem da interface |
| **Só UM objeto por nível deve ter `Camera`** | «com mais de uma câmera ativa o resultado é indefinido» |
| `zoom` é **porcentagem**, padrão **100**, **maior aproxima**, faixa 1 a 10000 | eu mandei 3 e 0,33 — isto é, 3% e 0,33% — e li o afastamento extremo como «o pino não serve» |
| `set x`/`set y` **não têm efeito** com Autoscroll ligado | o autoscroll reposiciona no quadro seguinte |
| `move x`/`move y` **substituem** o deslocamento anterior, não somam | mandar 0 remove; é o jeito de fazer tremor de tela |
| `Parallax` é a % da velocidade do fundo | 100 = junto com o jogo, 0 = parado; menor = mais longe |
| `Background Repeats` ladrilha o fundo | o fundo não acaba quando a câmera passa da beirada |
| A camada **`Background`** não tem física **nem comportamentos** | céu e montanhas são decoração pura; nada de blocos neles |
| A camada **`User Interface`** não rola com a câmera | é onde ficam placar, vidas e botões |

---

## 2c. A biblioteca de desenhos (o que custou a Aula 2 inteira)

Objeto de aula **não é quadrado pintado**: o Flowlab tem sete bibliotecas
prontas (`edit sprite` → `Browse`), e a da casa é `Flowlab Sprites`
(ENDESGA), com `Blocks`, `Characters`, `Objects`, `Terrain` e `Town`.

| fato medido | consequência |
|---|---|
| O passo entre fileiras da grade é **~89 px**, não 85 | erro de 4 px por fileira ACUMULA: na nona o clique cai no **vão** e não aplica nada — e o editor não acusa |
| Clique no vão é **mudo** | o objeto fica com o losango bege PADRÃO do Flowlab, e só a prova em jogo descobre |
| A grade **rola** | contar fileira no olho erra; `comum.linhas_da_grade()` MEDE os centros a cada corrida |
| O sprite no jogo sai **pequeno e partido** | rastrear por `maior_mancha` diz «sumiu»; use `comum.centro_por_cor` |
| A cor de rastreio é a mais **ABUNDANTE** que ainda distingue | pegar a mais distante escolheu um ciano de uma dúzia de pixels, e o pulo mediu 50 px em vez de 428 |
| Uma cor de tom médio **casa com CINZA** | a pele do herói é (234,179,146) e um cinza (190,190,190) cai dentro de 46 nos três canais: `mascara_cor` exige o pixel tão colorido quanto o alvo |
| Um toque de tecla de **duração zero não existe** para o jogo | o motor lê o estado das teclas uma vez por quadro; `keyboard.press` aperta e solta no mesmo instante e some entre dois quadros. Segurar 0,18 s resolveu: 0 px → 128 px |
| Com o jogo apagado **as teclas não chegam nele** | o mesmo corre-e-pula levava 373 px e dois degraus aceso, e 163 px e nenhum degrau apagado: clique dentro do jogo ANTES de cada gesto |
| O escurecimento é **sistemático**, não esporádico | no registro ele aparece a cada gesto e some a cada clique |
| O Flowlab **escurece o jogo inteiro** quando a página perde o foco | nada some, só apaga — e aí a página virava «boneco» com 667.424 pixels |
| O herói tem **vermelho** na roupa | faixa de tom escrita à mão («vermelho é a lava») lê o herói como lava; a cor sai MEDIDA do sprite (`cores_do_sprite`) |
| O `OK` do editor de desenho **não é o azul** do painel do objeto | `volta_ao_nivel` tem de fechar os três: desenho, objeto e física |

E o guarda: `comum.clica_sprite` **exige** que o desenho mude. Aceitar calado
o «já era esse» é exatamente o que escondeu a estrela sem desenho. Quando nada
muda, ele põe o vizinho, volta ao alvo e cobra a mudança.

---

## 2d. ⚠️ O arrasto da palheta: o defeito está na ORIGEM, não no destino

`blocos.item_palheta(nome)` devolve, **de forma intermitente**, um ponto que
não está sobre o item: medido, a mesma chamada deu `(115, 474)` — em cima do
texto «Restart Game» — e `(42, 1116)`, que é o **ícone na beirada**.

**Arrastar do ponto errado não dá erro.** Ele arrasta a PALHETA, o bloco não
nasce, e a falha sai como *«soltei X em (…) e a mesa não mudou ali»* — uma
mensagem que aponta para o **destino** quando o defeito está na **origem**.

Isso me custou a maior parte de uma sessão, e gerou quatro modelos errados que
eu cheguei a escrever aqui como se fossem fato: fio diagonal engana o detector,
o fundo azul estragou o OCR, a mesa cansa, e **«o Flowlab só aceita um arrasto
da palheta por carregamento de página»**. Esse último chegou a virar código —
recarregar antes de cada bloco, 12 s cada. Nenhum era a causa.

**A guarda:** o texto dos itens fica entre x≈62 e x≈330 (antes vem o ícone).
Ponto fora dessa faixa é recusado e relido. `blocos.PALHETA_X`.

**A lição geral:** quando a mensagem de erro descreve o DESTINO de um gesto,
conferir a ORIGEM antes. E quando um sintoma é intermitente, desconfiar de um
endereço que é RELIDO a cada vez, não de um estado que se acumula.

---

## 2e. ⚠️ O modal `Recover unsaved work`

Captura que falha no meio deixa edições de comportamento **não salvas**. Ao
navegar para fora, o `beforeunload` do Chrome dispara e a navegação pode
abortar. Na abertura seguinte do objeto aparece o **`Recover unsaved work`** —
e ele é MODAL: com ele na tela, arrasto não arrasta e clique não clica.

`editor.recupera()` existia e era chamado em quatro lugares **sem nunca
disparar**, porque achava o botão com a leitura que para na primeira com
conteúdo. Hoje percorre a escada e **descarta** por padrão.

E o `OK` azul da mesa é o que **commita** os blocos: recarregar sem fechar a
mesa descarta tudo o que foi solto desde que ela abriu.

**Antes de investigar por que um gesto não funciona: fotografe a TELA INTEIRA e
olhe.** Eu recortava a mesa e analisava o recorte, com o diálogo logo acima.

---

## 2f. ⚠️ O OCR achava o alvo por um PEDAÇO dele

`rs.procura_forte` casava quando o lido era substring do ALVO e tinha 3 letras
ou mais. O ramo existe por um motivo bom — o OCR corta o fim de rótulo
comprido, e «Behavior» precisa valer por «Behaviors». Só que, com piso de 3
letras, **qualquer palavra do alvo servia**: «New Game», o título em letra
grande da *página do jogo*, casava com `Game Levels`, que só existe no
**editor**.

Quem decidia com esse casamento era `editor.no_jogo()`. Ele dizia «estou no
editor» com o jogo desenhado na tela, e a prova da Aula 3 parou sem haver nada
errado com a fase. Guarda que erra para o lado de recusar não acusa dano, o que
o torna mais difícil de ver que o contrário.

Hoje o piso é **60 % do comprimento do alvo**. `prova_casamento_ocr.py` tranca
os dois lados com duas fotos de verdade: a página do jogo **não** pode casar
com `game levels`, e o editor **tem** de casar.

---

## 2g. ⚠️ A bancada tem DUAS metades, e eu errei a segunda

`BANCADA=1` posta sem os remendos instalados já era barrada. O caso que de
fato se repetiu é o avesso: **não pôr a variável**. Com o motor de pé, três
sondas minhas de diagnóstico fotografaram o Chrome do Julio, clicaram nele e
levaram a aba dele para a página do jogo — e eu passei meia hora lendo uma tela
que não era a que a captura estava construindo.

Agora motor de pé + `BANCADA` ausente também **para**. Quem precisa mesmo da
tela de verdade diz `TELA_DE_VERDADE=1`, em voz alta.

---

## 2h. ⚠️ O céu azul desmarcava `movable` — e o jogo foi publicado assim

`AZUL_OK` é `(126,168,224)`. O céu da Aula 2 é `87CEEB` = `(135,206,235)`.
Distância `(9, 38, 11)` — **dentro da tolerância 40**. Com o nível pintado,
`fecha_painel_objeto` achava um pedaço de CÉU em vez do botão, e o clique caía
dentro do painel de física, **em cima da caixinha `movable`**.

Em jogo, isso dá um boneco que **anda e não pula**: `Velocity` move objeto
parado, `Impulse` (o pulo) não. A Aula 3 escapou só porque o céu dela é de
noite.

Três coisas a guardar:

1. **O teto de tamanho não resolve.** Eu já tinha consertado a função irmã
   (`abre_fisica`) com um limite de pixels; trazido para cá, ele passa — o céu
   se parte em pedaços de 97 mil pixels e o botão tem 24 mil.
2. **O que separa os dois é a PALAVRA escrita no botão.** `_ponto_do_ok` lê o
   rótulo e só cai na cor como reserva. Isso só foi possível depois de a escada
   de OCR ganhar os degraus de limiar **200** — branco sobre azul não aparecia
   em nenhum degrau anterior, e com isso **todo** rótulo de botão azul do
   Flowlab era invisível (`Browse`, `Blocks`, `Characters`, e o nome do pacote
   de sprites **quando ele está selecionado**).
3. **Conferir depois de fechar.** `jogador()` reabre a física e exige `movable`
   marcado. Quem grava é o OK; se o OK for outra coisa, nada acusa.

`prova_ok_nao_e_o_ceu.py` tranca os três.

---

## 2i. ⚠️ Retomar uma etapa do meio FOTOGRAFA O FIM

Cada etapa é tolerante de propósito (`objeto_ou_abre` edita o que já existe,
`bloco_ou_solta` acha o bloco que já está na mesa) para que a captura possa ser
retomada depois de um erro. **Essa mesma tolerância faz a foto mentir**: rodar
`plataformas` num jogo já completo não dá erro nenhum e salva o cenário PRONTO
com o nome do passo «faça o chão».

Três passos da Aula 2 saíram assim, e o que os pegou foi uma regra boba do
`confere_aulas`: *duas fotos da mesma aula não podem ser iguais byte a byte*.
Fotos do fim que fossem apenas **parecidas** teriam passado.

**Regra:** etapa do meio refeita num jogo pronto exige **recapturar a aula
inteira**, do `novo`. Não há meio-termo barato.

---

## 2j. ✅ O bloco `Keyboard` DISPARA pela bancada (medido 07-10)

A nota antiga dizia que `Keyboard`, `MouseClick` e `Timer` não disparavam nem
pela bancada. **Para o `Keyboard` isso é falso hoje.** Medido num jogo de
descarte, com `Keyboard[A].down → Destroyer.in` no boneco, e com o controle
nos MESMOS segundos: a seta direita o levou de x=1309 a 1472, e logo depois a
tecla `a` o **destruiu** — tela acesa, boneco sumido. O que não disparava era o
`keyboard.press` de duração ZERO do motor, consertado depois.

Isso libera a Aula 4 (nave e tiro) para ser provada por máquina. `MouseClick` e
`Timer` continuam **sem medida** — meça antes de desenhar em cima deles.

⚠️ **Três armadilhas no caminho, e as três davam o mesmo resultado falso:**

1. **Bloco `Keyboard` novo não tem tecla.** «Current key:» vem **vazio**. O
   primeiro teste não media nada, e «não disparou» era indistinguível do real.
2. **`Activate on any key` troca o tipo da saída para TEXTO** — e isso
   **derruba o fio** que já existia para uma entrada não-texto. Pior: o
   Flowlab passa a RECUSAR a ligação, e `liga_fixo` falha com «nenhum fio
   apareceu». Segundo teste vazio, por outro motivo.
3. Só a **foto do fio** desmentiu os dois.

⭐ **E o `Change Key` aceita tecla da bancada:** clicar nele e mandar a tecla
deixa «Current key: A». A configuração do bloco é automatizável.

**Regra:** teste de «não aconteceu» prova, na mesma rodada, que o caminho
inteiro existia — o bloco configurado, o fio no lugar, e um CONTROLE que
mostre que o gesto chega.

---

## 2k. As três peças da Aula 4, medidas antes de desenhar a aula

| bloco | medido | o que ficou sabido |
|---|---|---|
| `Keyboard` | ✅ dispara | bloco novo vem **sem tecla**; `Change Key` aceita tecla da bancada; `Activate on any key` troca a saída para TEXTO e **derruba o fio** |
| `Timer` | ✅ dispara sozinho | nasce com `auto start` (nada ligado ao `start`), atraso em **décimos** de segundo (10 = 1 s), `Repeat: 1` |
| `Spawn` | ✅ cria objeto | `Spawn X/Y` são **coordenadas do NÍVEL em pixels**, não relativas a quem cria: com 0/0 o objeto nasceu no canto de cima à esquerda do nível |
| `MouseClick` | ⬜ **sem medida** | medir antes de desenhar em cima dele |

## 2l. O TIRO da Aula 4 é `Emitter`, não `Spawn` — medido no protótipo

`Spawn` precisaria de `Extractor(X)` + `Extractor(Y)` + fios para o tiro nascer
na nave, porque **`Spawn X/Y` são coordenadas do NÍVEL**. O `Emit` resolve tudo
isso: nasce **no próprio objeto**, já sai andando numa direção e **expira
sozinho** — some a tarefa de «limpar o que sai da tela» que o plano previa.

A aula inteira do tiro é **um bloco e um fio**:
`Keyboard[Espaço].down → Emitter.emit`.

Medido no protótipo (jogo `3152613`):

| o que | valor | como se mediu |
|---|---|---|
| nome na palheta | `Emit` | — |
| **título na mesa** | **`Emitter`** | ⚠️ e o pino de entrada também se chama `emit`: `acha_bloco("Emit")` casa com o RÓTULO DO PINO, 86 px abaixo do título |
| `Emit Angle` | 0 = direita, **90 = BAIXO**, **270 = cima** | com 90 o tiro nasceu ABAIXO da nave; com 270, acima |
| `Expire After` | em **trinta avos de segundo** | o padrão `10` dá **um terço de segundo** — some antes de a criança ver |
| `Emit Force` | 25 é rápido demais para a minha câmera | com o tiro parado (`movable` desmarcado) ele fica visível; solto, atravessa a tela entre dois quadros meus |
| física do tiro | **`movable` marcado, gravidade desmarcada** | de fábrica o tiro nasce `movable: False` e **não anda** — a terceira vez que o `movable` morde este curso |

⭐ **`movable` já mordeu três vezes:** o boneco que não pulava (Aula 2), a lava
que não subia (Aula 3) e agora o tiro que não anda. Na Aula 4 isso deixa de ser
armadilha e vira **conteúdo**: a criança marca a caixinha e vê o tiro sair.

---

⛔ **Duas armadilhas de desenho de teste que me custaram meia hora cada:**

1. **Entrada só aceita UM fio.** Ligar um segundo bloco à mesma entrada é
   recusado pelo Flowlab — e o `liga_fixo` dizia que tinha ligado, porque
   contava o fio que já estava lá (§ `prova_fio_entre_pinos.py`).
2. **`Spawn` do PRÓPRIO tipo que contém o spawner é uma bomba.** Mandei o
   boneco criar bonecos, cada um com o mesmo `Timer`: o canvas ficou preto em
   segundos. Para medir `Spawn`, crie um tipo que **não** tenha o spawner.

---

## 2m. ⚙️ Como se roda uma aula sem queimar tempo e token

Quatro regras, cada uma de um custo medido:

**1. Toda etapa que ESCREVE lê de volta, na hora.** As duas recapturas
inteiras da Aula 2 tiveram a mesma forma: uma escrita silenciosa que só
apareceu no fim, ou depois de publicada. Uma leitura de volta custa seis
segundos. Já estão com ela: `cor_do_ceu` (mede a cor da folha), `marca_caixa`
(lê a cor da caixinha), `arrasta_slider`, o `density`, `nomeia_tipo`,
`campo_do_painel`, `liga_fixo`, `solta`.

⚠️ **E o guarda tem de ser testado nos DOIS sentidos.** A primeira versão da
leitura do `campo_do_painel` reprovou um `right` que estava escrito **27** na
tela, certinho — guarda que reprova o caso certo aborta uma captura boa, e é
pior que guarda nenhum.

**2. A captura é assíncrona e muda.**

```
python3 fonte/roda_aula.py 4           # a aula inteira
python3 fonte/roda_aula.py 4 prova     # de uma etapa em diante
```

Ele roda a captura, os clipes, os JPEG, os dois guardas e a folha de contato, e
imprime **um veredito** com as medidas que a prova tirou em jogo. Não se
acompanha pelo caminho: numa noite de trabalho eu gastei uma fatia enorme do
orçamento olhando um processo de vinte minutos avançar, e nenhuma dessas
leituras mudou nada do que eu fiz depois.

**3. Quando algo falha, a diagnose vem em TEXTO.** `comum.onde_estou()`
responde de uma vez: em que tela estou, tem diálogo por cima, tem roda aberta,
que cor tem a folha, qual é o endereço. Está ligado no `main` das capturas, e
sai junto com o erro. Imagem é a coisa mais cara que eu leio — a maioria das
diagnoses não precisa de nenhuma.

**4. Aula nova importa `aula_comum.py`.** `cria_objeto`, `da_fisica`,
`confere_fisica`, `abre_mesa`/`fecha_mesa` — todos já com leitura de volta. As
Aulas 1 a 3 **não** foram migradas de propósito: estão capturadas, provadas e
publicadas, e refatorar forma aprovada exigiria provar neutralidade, que aqui
custa uma recaptura inteira. Quem mexer numa delas na próxima vez, migra.

---

## 2n. ⛔ O REMENDO DA BANCADA SUMIA, e todo arrasto ia para a tela de verdade

Custou uma noite da Aula 4. Sintoma: `solta` não largava bloco nenhum na mesa —
`mudou 0 px`, sem erro, sem nada na tela.

`bancada.instala()` troca `blocos.arrasta_devagar` por uma lambda que fala com o
motor. Mas `bancada.liga_se_pedido()` mora dentro do `comum.py`, e na ordem de
import das capturas (`import rs, nav, editor, blocos, comum`) quem carrega
primeiro é o `blocos`: ele importa `comum` no meio do próprio carregamento, o
`instala()` recebe um módulo **pela metade**, põe a lambda — e logo depois o
`def arrasta_devagar` do próprio arquivo a **sobrescreve**.

O estrago é assimétrico e por isso mudo: `rs._evento_mouse` continuava remendado
(só o MOVER sobrevive; apertar e soltar são engolidos), `nav.janela` devolvia a
área da bancada e as fotos saíam certas — mas os eventos de arrasto iam **crus
para a tela de verdade, na origem**, fora do navegador.

Prova de dois segundos:

```
BANCADA=1 python3 -c "import rs, nav, editor, blocos, comum; print(blocos.arrasta_devagar)"
# -> <function arrasta_devagar ...>            (remendo PERDIDO)
BANCADA=1 python3 -c "import comum; import blocos;            print(blocos.arrasta_devagar)"
# -> <function instala.<locals>.<lambda> ...>  (remendo de pé)
```

⭐ Conserto: a escolha mora **dentro** da função, em tempo de chamada, não num
remendo de import. Quem for trocar peça de `rs`/`nav`/`blocos` por causa da
bancada daqui para a frente: faça igual, não por atribuição no `instala()`.

### E a sonda que escondia isso

Três sondas minhas deram VERDE e me fizeram descartar as hipóteses certas. Elas
chamavam `solta(..., tentativas=1)` — e dentro do laço está
`if k == tentativas - 1: _recarrega_e_reabre()`. Com `tentativas=1` isso vale
**já na primeira volta**: a sonda recarregava a página antes de cada arrasto, que
é justamente o caminho de recuperação. Ela consertava o defeito antes de medi-lo.
Para sondar `solta`, use `tentativas=2` ou mais.

## 2o. ⚠️ O `−` do painel de um bloco fica a +186 do rótulo, não a +220

`prepara_menos` devolvia o ponto `(rótulo + 220, +70)`. Medido na foto: com o
ponto no CENTRO de `Current value:`, o `−` está em **+186** e o `+` em **+249**,
a 63 px um do outro. O +220 caía no vão, puxado para o `+`: três cliques num
`Number` zerado davam `3` em vez de `-3`, e a nave andava para o lado errado.
Na Aula 3 o mesmo +220 pegou o `−` por pouco — por isso o defeito atravessou uma
aula inteira sem aparecer.

## 2p. ⚠️ Reprocurar bloco SÓ PELO NOME devolve o primeiro da mesa

`le_valor` e `escolhe_tipo_da_colisao` faziam `acha_bloco(bloco.nome)` sem
recorte. A Aula 4 tem **dois** `Number` na mesa da nave (um por sentido): o de
baixo mostrava `3` na tela, certinho, e a leitura trazia o `-3` do de cima — a
guarda reprovava um valor correto e parava a captura.

Os dois agora procuram na **faixa do próprio bloco** (`bloco.y ± `). Reprocurar
continua valendo (zoom e rolagem movem tudo), mas perto de onde o bloco estava.
Mesma regra para `bloco_ou_solta`/`solta`, que ganharam `regiao=`: sem ela, o
segundo `Keyboard` de uma mesa devolve a coordenada do primeiro e os fios vão
todos para o bloco errado, sem erro nenhum.

## 2q. ⛔ `Ship Controls` NÃO é movimento de quatro setas

Medido abrindo o pacote e fotografando o miolo:

```
Keyboard[Left].down  -> Number(-4) -> Rotation.add      (GIRA)
Keyboard[Right].down -> Number(4)  -> Rotation.add      (GIRA)
Keyboard[Up].down    -> Number(6)  -> Motor.forward     (acelera pelo nariz)
```

É girar-e-acelerar, estilo Asteroids. Em jogo a nave sai voando e não volta. E,
pior para uma aula de tiro: com a nave girando, o `emit angle` 270 deixa de
significar "para cima".

A palheta de `Behavior Bundles` tem só `Run & Jump`, `Dangerous` e
`Ship Controls`. `More Bundles` é **busca de pacotes da comunidade**, não lista
local — conteúdo de terceiros, que muda sem aviso; não serve de base para aula.

⭐ O movimento da Aula 4 é o trio da Aula 3 (`Number` → `Velocity`) com o
`Always` trocado por `Keyboard` e o `y` por `x`. `-3` vai para a esquerda, `3`
para a direita. **Sem gravidade e sem atrito do ar — o painel de física do
Flowlab não tem amortecimento — a nave NÃO PARA ao soltar a tecla.** Isso não é
defeito: é o espaço, e a aula ensina a frear com a seta oposta.

## 2r. ⚠️ Média não mede FLUXO CONSTANTE

A prova da Aula 4 media a altura MÉDIA do vermelho para provar que os inimigos
descem. Com o canhão soltando sem parar e os inimigos expirando sozinhos, a
média entra em **regime** e fica parada: li `[622, 588, 615, 586, 600, 594, 598,
612]` num jogo em que eles desciam a tela inteira. A prova reprovava o certo.

⭐ A régua passou a ser a própria tela: o vermelho mais BAIXO tem de passar da
metade do caminho entre onde o inimigo nasce e o pé da fase — e os dois extremos
são lidos na hora (o pé da fase sai do retângulo da cor do céu, que é cor que a
aula pinta).

## 2s. As peças da Aula 5, medidas antes de desenhar a aula

Protótipo: `3155537`. Tudo abaixo foi visto na tela, não deduzido.

**A palheta inteira, por categoria** (o que existe de verdade):

- `Logic & Math`: `Number`, `Expression`, `Global Variable`, `Object Variable`,
  `Ease`, **`Random`**, `Repeater`, `Filter`, `Switch`, `Toggle Switch`,
  `Router`, `Logic Gate`, `Custom Behavior`
- `Properties`: `Position`, `Rotation`, `Alpha`, `Size`, `Enabled`, `Animation`,
  `Velocity`, `Spin`, `Material`, `Flip`, `Extractor`, `Display Order`,
  `Shader`, `Blending`
- `Components`: `Sound`, `Emit`, `Spawn`, `Attacher`, `Physics Joint`,
  `Proximity`, `Push`, `Motor`, `Spin Motor`, `Impulse`, `PointAt`,
  `Destroyer`, `Camera`, `Message`, `RayCast`
- **`GUI`: `Alert`, `Bar`, `Label`, `Cursor`** ← o placar mora aqui
- `Game Flow`: `Pause Game`, `Load Level`, `Restart Game`, `Fetch URL`,
  `Save Value`, `Leaderboard`, `Achievement`, `Level Physics`, `User Info`,
  `Clipboard`, `Full Screen`, `Cloud Game Save`

**✅ O PLACAR, provado em jogo.** `Keyboard.down → Number.+` e
`Number.out → Label.text`. Com o `Number` em 1, três toques no espaço deixaram o
`Label` mostrando **4**: cada pulso no pino `+` **soma 1** (não soma o próprio
valor — seria 8). E o `out` do `Number` atualiza o `Label` sozinho, sem precisar
disparar o `get`. Para um placar, o `Number` começa em **0**.

**O `Label`:** entradas `text`, `alpha`, `x`, `y` (e as mesmas quatro na saída).
O painel tem caixa de texto, cor do texto e do contorno, fonte, alinhamento e
réguas de `size`, `weight`, `alpha`, `outline`, `spacing`, mais `max width` e
`attach to object`. **`size` nasce em 10, que é pequeno** — placar pede aumentar.

⚠️ **O `Label` ESCREVE O PRÓPRIO TEXTO DENTRO DA FASE**, em letra grande. Um
`Label` recém-solto desenha a palavra "Label" no nível, e `acha_bloco("Label")`
casa com ELA, não com o título do bloco — medido: devolveu `x=959` com o bloco
em `x=1460`. Procure sempre com `regiao=` fora do retângulo do nível.

**O `Random`:** entradas `min`, `max`, `new`; saída `out`. Nasce com faixa
`0-10`. Quem pede número novo é o pulso em `new`.

**⛔ O `Impulse` NÃO MOVEU NADA, e o `Velocity` moveu.** Mesmo objeto, mesma
mesa, mesmo fio no pino `y`, com `movable` marcado e gravidade ligada (o boneco
caía e parava no chão, então era móvel). Com `Keyboard → Number(-25) → Impulse.y`
a leitura foi `906, 906, 906, 906` — parado. Trocando só o bloco final por
`Velocity.y`: `906 → 692 → 597 → 576` (subiu **330 px**) e **voltou a 906** em
1,5 s, puxado pela gravidade. É exatamente a sensação de Flappy, e de quebra o
pulo da Aula 5 fica sendo **o mesmo trio da Aula 3** — zero peça nova.

**✅ A ALTURA SORTEADA, provada com número.** No `Fogo` (o obstáculo):
`Once.out → Random.new` e `Random.out → Position.+y`. O `+y` é DESLOCAMENTO, e
por isso não exige saber coordenada nenhuma da fase — cada cópia emitida nasce
no soltador e desce um tanto sorteado. Medido com o jogo rodando: o topo do mais
alto ficou entre 224 e 295, o pé do mais baixo entre 671 e 911, **687 px de
espalhamento**, variando a cada amostra.

⚠️ **O `Random` nasce em `0-10`**, que desloca dez pixels e não dá para ver. O
`Max value` fica na linha ABAIXO do rótulo (o `campo_ao_lado` escrevia no vazio
e lia `['|']`): use `campo_abaixo("max value", 600)`. A conferência mais barata é
o próprio bloco, que passa a mostrar **`0-600`** embaixo do dado.

⛔ **E a armadilha que eu quase registrei como verdade:** na primeira foto os
fogos apareciam em alturas diferentes e eu dei o sorteio por provado. Olhando de
novo, os mais à esquerda (os mais ANTIGOS) estavam mais baixos e os recém-soltos
no alto — uma parábola de queda, não sorteio. Fui conferir a física do `Fogo` e
`affected by gravity` estava **desmarcado**, então nem a parábola explicava. O
`Random` estava em 0-10 o tempo todo: a figura concordava com a minha hipótese
pelo motivo errado. Só o número (687 px, variando) provou alguma coisa.

**⚠️ Pássaro com gravidade e SEM CHÃO sai da fase antes de a criança reagir.**
Medido: cinco segundos depois do Play a tela já estava vazia, e o rastreio
devolvia `None` em dez amostras seguidas. A Aula 5 precisa de chão — e ele ainda
serve de fim de jogo.

## 2t. ⚠️ Sonda com `pasta("aulaN")` ESCREVE dentro da aula N

Minhas sondas da Aula 5 começavam com `comum.pasta("aula4")` — copiei o
cabeçalho da aula anterior e não troquei. Elas mediram no protótipo, mas
gravaram as cores de `Passaro`, `Chao`, `Fogo` e `Soltador` dentro do
`fonte/aula4/cores.json`, de uma aula **já publicada**.

Nada na tela acusa: a página da Aula 4 não muda, os guardas passam, e o
`git status` só diz "modificado". O estrago apareceria mais tarde, numa
recaptura da Aula 4: `rastreio("Nave", …)` teria de separar a nave de um
pássaro que não existe naquele jogo, e poderia recusar uma cor boa.

⭐ Sonda mede em PROTÓTIPO e não deve escrever em pasta de aula. Antes de
commitar depois de uma noite de sondas, `git status` nas pastas `aulaN/` —
arquivo de aula antiga modificado sem eu ter capturado aquela aula é sintoma.

## 2u. As peças da Aula 6 (chave e porta), medidas

Protótipo: `3155573`.

**`Message`** (em `Components`): pinos `send` (entrada) e `done` (saída). O
painel tem dois seletores — **`Message`**, que nasce em `Hello`, e **`Send To`**,
que nasce em **`Myself`**.

**`Mailbox`** (em `Triggers`): só a saída `out`. O painel tem um seletor só, o
`Message`, que também nasce em `Hello`. ⭐ Como os dois já nascem combinados em
`Hello`, a aula não precisa criar nome de recado nenhum.

**`Send To` não tem opção de "todo mundo".** A lista inteira é `Choose objects`,
`Myself`, `Last contacted object`, `Last raycast target`, `Last spawned object`,
`All spawned objects`, `All attached objects`, `Last attached object`. Para a
chave falar com a porta o caminho é `Choose objects`, que abre mais dois
seletores: **`Select Type`** (escolhe-se `Porta`) e `Any Object`. Isso cobra o
`Type` que o curso ensina desde a Aula 1 — bom para a aula.

⚠️ **Geometria do painel:** o seletor do `Send To` fica na linha **de baixo** do
rótulo, não ao lado. `escolhe_na_lista` ganhou `dy=` por isso; com `dy=0` o
clique cai no rótulo, lista nenhuma abre, e o erro que sobra ("não achei na
lista") manda procurar o defeito na lista.

**✅ PROVADO:** `Once → Message(Hello, Choose objects → Select Type: Porta)` na
chave, e `Mailbox(Hello) → Destroyer` na porta. No editor havia dois objetos; no
jogo, depois do recado, só um — **a porta some**. O recado atravessa de um
objeto para outro.

⛔ E a medida errou de novo pelo mesmo motivo de sempre: eu rastreava a porta
pela cor da grama, e o desenho não tinha sido aplicado (ficou o losango padrão).
O rastreio deu `0` no editor E no jogo — **zero nos dois lados é sintoma de
instrumento cego, não de prova**. Quem decidiu foi o olho.

## 2v. ⛔ O `Alert` ESCURECE a tela e não desenha a caixa

Medido na Aula 3 e quase repetido na Aula 6: na página do jogo, o `Alert`
escurece tudo e **não desenha a caixa dentro do canvas**. A criança encosta na
estrela e vê a tela apagar, sem uma palavra.

⭐ Fim de jogo que FUNCIONA é a estrela que **some** — `Collision` +
`Destroyer`, a dupla da moeda da Aula 1, já provada, e que diz "peguei" sem
ambiguidade.

Este fato estava escrito só num comentário dentro do `cap3.py`, e por isso eu
cheguei a escrever a Aula 6 inteira com `Alert` antes de topar com ele. Fato que
vale para o curso todo mora aqui, não dentro de uma captura.

## 2w. ⛔ `is solid` DESLIGADO é colisão DESLIGADA

Eu queria um alvo que a caixa pudesse **atravessar** e ainda assim ser sentida,
e desmarquei `is solid`. No Flowlab isso não é "passa por dentro mas sente": é
**colisão desligada**. Um `Collision` naquele objeto não dispara nunca.

⭐ **E quem me disse foi o próprio editor**, num aviso amarelo desenhado na mesa
de blocos, ao lado do `Collision`:

> *"This object has disabled collisions, so Collision will not trigger"*

Eu só o vi porque fui olhar a foto do fio que não nascia. **O Flowlab escreve
avisos na mesa** — quando um bloco não funciona e não há erro, olhe a mesa
inteira antes de medir qualquer coisa.

⭐ O conserto melhorou a Aula 7: o alvo fica sólido, e quem sente a batida é a
CAIXA (que tem colisão ligada). Ela manda um recado para o alvo — a mesma dupla
`Message`/`Mailbox` da Aula 6, agora aparecendo duas vezes na mesma aula.

## 2x. ⚠️ A lista de tipos do `Collision` ROLA

Com quatro ou cinco tipos no jogo a lista ganha barra e mostra só parte dela. O
erro que sobrava — "o tipo não aparece na lista" — manda conferir o campo `Type`
do objeto, e eu fui olhar: o painel do Alvo dizia `Type: Alvo`, certinho.
`escolhe_tipo_da_colisao` agora rola a lista antes de desistir.

## 2y. ⚠️ A palavra `type` aparece DUAS VEZES no painel do objeto

No rótulo e dentro do próprio conteúdo do campo (`New Type 3`). Clicar 54 px
abaixo do CONTEÚDO cai na linha do `Parent`, o texto vai para o vazio e o Tab
leva o foco para o `Reset`. Resultado: um objeto com `Name: Caixa` e
`Type: New Type 3`, e o erro saindo como *"li 'mo' de volta"* — lixo de OCR de
um campo que nem era o certo. Funcionou nos dois objetos anteriores da mesma
captura por sorte da ordem em que o OCR devolveu as palavras.

⭐ `nomeia_tipo` não tem mais ponto único: tem uma LISTA de candidatos, do mais
alto para o mais baixo, e tenta cada um até a leitura de volta bater.

## 2z. ⛔ RETOMAR UMA ETAPA trabalhava no jogo que estivesse ABERTO

Pedi `roda_aula.py 5 prova_fogo` e a medida saiu do jogo da **Aula 7**: a foto
mostrava caixas, alvo e porta. A etapa retomada não navegava para lugar nenhum —
ela usava o que estivesse no navegador, que é o jogo da última captura que
rodou.

Essa, por sorte, só MEDIA. As etapas seguintes da Aula 5 mexem na mesa de
blocos: elas teriam escrito blocos dentro do jogo **publicado** de outra aula,
sem nada na tela dizendo que o jogo era o errado.

⭐ `aula_comum.main` agora abre o `jogo.txt` da própria aula antes de qualquer
etapa retomada, **e confere o endereço depois de abrir**.

## 2aa. ⛔ Leitura de volta sem recorte aprova o que NÃO aconteceu

Dois casos na mesma aula, e os dois ficaram verdes:

1. `escolhe_na_lista` procurava o item e conferia o resultado na **tela
   inteira**. Numa mesa de blocos a palavra `Alvo` mora também no RÓTULO do
   `Collision` ao lado: o clique foi para o rótulo, o `Select Type` ficou no
   texto de fábrica, e a conferência achou a mesma palavra no lugar errado. O
   jogo saiu com a caixa mandando recado **para ninguém**;
2. o casador aceitava `input > 2` casando com a palavra **`input`**, que está
   igual no bloco que mostra `input > 0`. A condição do `Filter` NUNCA foi
   ajustada — a porta abria na primeira caixa — e a aula perdia inteira o seu
   ponto.

⭐ Toda leitura de volta tem de ser **ancorada no painel** que ela confere, e o
ramo palavra-por-palavra do casador só vale para alvo de UMA palavra. Os dois
casos estão trancados em `prova_casamento_ocr`, com sabotagem.

## 2ab. ⚠️ Ponto estimado de rótulo: `acha_texto` devolve o CENTRO

Estimei o botão `+` do `Filter` em (+152, +82) a partir do rótulo — e
`acha_texto` devolve o **centro da frase**, não a ponta. Os cliques caíam fora
do botão. Quando o alvo é pequeno (um `+`, um `−`), ache-o por LEITURA, como o
`cap7` faz agora, em vez de somar deslocamento a um ponto cuja origem você não
conferiu. Ver também §2o, o `−` que ficava no vão.

## 2ac. As peças da Aula 8, medidas antes de a aula existir

| peça | medido | o que ficou sabido |
|---|---|---|
| `Global Variable` | ✅ | entradas `set`, `get`, `+`; saída `out`. O painel é **uma lista**: clicar no campo abre, `+ Add New Name` abre um diálogo com `Name`, `Type: Number` e **`Default Value`** |
| o título do bloco | ⚠️ | depois de escolhida a variável, o bloco **passa a se chamar pelo nome dela** (`Recorde`), e `DESLOC`/`PORTAS` são por TIPO — daí o campo `tipo` do `Bloco` |
| sobreviver ao recomeço | ✅ | com 99 de fábrica, foi a 7, o `Restart Game` rodou e ela **continuou 7** — nunca voltou a 99. É o que faz o «recorde da partida» existir |
| `Default Value` | ✅ | vale no começo da partida (lido 99 na tela por 8 s antes do primeiro `set`) — dispensa semear o recorde com `Once` + `Number` |
| `Filter`: as comparações | ✅ | seis: `greater than`, `less than`, `equal to`, `not equal to`, `less than or equal to`, `greater than or equal to` |
| ⭐ fio no `set` do `Filter` | ✅ | **o fio manda no número do painel.** Provado com 50 no fio contra `input > 0` no painel: com o fio, o objeto viveu os 26 s contando até 25; sem ele, morria no primeiro segundo |
| ⚠️ ordem do primeiro pulso | ⛔ | o fio só manda **depois de ter entregue alguma coisa**. Se o primeiro `in` chega antes do primeiro `set`, quem decide é o painel — e foi assim que a minha primeira medição disse «o painel manda» |
| `Timer` | ✅ | o atraso de fábrica é **10 décimos = 1 segundo**: a aula não precisa mexer nele |
| `Label` | ⚠️ | nasce **salmão** e desenha no canto de cima do nível. Dois `Label` nascem **um em cima do outro** — o segundo desce pelo pino `y`. E em céu ESCURO ninguém lê o salmão: duas medições minhas voltaram vazias por isso, e eu quase fui procurar o defeito no jogo |

⭐ **A regra que sai daí:** num `Filter` que compara com fio, **alimente o `set`
antes** — na Aula 8 quem faz isso é o `Timer` da bandeira, de segundo em
segundo, desde o começo da partida.

## 2ad. ⛔ A mesa ANDA entre um arrasto e outro

Cada arrasto da palheta recarrega a página (§2 do `solta`), e o editor
**recentra os blocos**. Com isso:

- coordenada de bloco guardada **antes** de um arrasto está velha — por isso
  `liga_fixo` tem de re-achar os dois blocos na hora de ligar;
- fileira em fração da tela (`_na_fila`) deixa de valer depois de alguns
  arrastos. Quem precisa escolher entre dois blocos de mesmo nome usa
  **`blocos.acha_todos`**, que devolve todos em ORDEM na tela.

E duas armadilhas de leitura que vieram junto, as duas trancadas em
`prova_titulo_composto`:

1. **Título de DUAS palavras** (`Global Variable`) não era achado: o ramo
   `exato` comparava item por item do OCR, e o tesseract entrega uma palavra
   por item.
2. **Dois blocos na mesma altura entram na MESMA linha do OCR** — o título
   chegava como `timer global variable`. O bloco estava na tela, aceso, e
   `solta` desfazia o arrasto três vezes antes de desistir. O diagnóstico que
   saía («não consegui LER o título») é o mesmo de bloco que não nasceu.

## 2ae. ⚠️ Campo de painel com o mesmo nome de um PINO

O `Delay` do `Timer` tem um gêmeo: o pino `delay` do próprio bloco.
`acha_texto('delay')` ora devolvia um, ora outro — e escrever no pino não
acusa nada. Daí `blocos.caixa_do_painel()`, que acha a caixa do painel aberto
pelo par `Help`/`Note` (que só existe dentro dele), e `campo_abaixo` procura
ali primeiro.

E o rótulo comprido **quebra em duas linhas** em painel estreito, o que muda a
distância até o campo: por isso o atraso do `Timer` se escreve com
`campo_acima('repeat forever', ...)`, ancorado no rótulo que não quebra.

⚠️ **Campo sem foco deste editor não é lido pelo OCR** (cinza claro sobre cinza
escuro). A leitura de volta tem de ser feita com o cursor ainda dentro do
campo — e em DUAS escalas: o mesmo `50` saiu como `'50 - +'` numa e `'a +'` na
outra.

## 2af. ⛔ Os pinos `x`/`y` do `Label` NÃO movem o texto

Dois `Label` de objetos diferentes nascem **no mesmo canto do nível**, um em
cima do outro, e os dois números ficam ilegíveis. Eu liguei `Number(80)` no
pino `y` — pelo `Once` e depois pelo `Timer`, para descartar «disparou cedo
demais» — e nas duas vezes o texto **não se moveu um pixel**. O fio estava no
pino certo (conferido na foto da mesa).

**Quem move é a caixinha `attach to object` do painel**: marcada, o texto passa
a ser desenhado em cima do OBJETO dono do bloco. Medido na Aula 8: com ela
marcada na bandeira, o recorde saiu do canto e foi desenhado na bandeira.

⭐ E isso resolveu a aula com MENOS peça, não mais: o tempo gruda no corredor
(e corre com ele), o recorde fica no canto, e nenhum bloco entra na mesa.

## 2ag. ⛔ Buraco sem fundo não custa tempo, custa o JOGO

A Aula 8 nasceu com dois buracos no chão. O corredor caiu no primeiro, saiu
pelo pé do nível e **sumiu** — e a foto do passo que promete «você corre e pula
os buracos» saiu com o percurso vazio, sem boneco nenhum. Nenhum guarda de
forma pega isso: o arquivo existe, abre, e tem o tamanho certo.

Duas consequências:

1. **Buraco de percurso leva uma casa de chão uma fileira abaixo.** Cair passa
   a custar segundos, que é o que um jogo contra o relógio quer.
2. **A foto de uma etapa que mostra o jogador tem de PROVAR que ele está lá.**
   `cap8` mede a posição dele por cor antes e depois da corrida, e reprova se
   ele sumiu ou não andou.

E uma terceira, medida no mesmo lugar: **passar da bandeira também tira o
boneco do nível** — ele pula por cima e cai fora pela direita. A corrida da
captura para ANTES da bandeira; quem chega na bandeira é a etapa da prova,
onde a batida já recomeça o jogo.

## 2ah. As peças da Aula 9, medidas antes de a aula existir

| peça | medido | o que ficou sabido |
|---|---|---|
| `Proximity` | ✅ | entradas `dist` (valor) e `check` (gatilho); saídas `x`, `y`, `miss`. Só olha quando recebe o `check` — daí o `Timer`. **`Distance` nasce em 32 px**: só acha quem está encostado; 3000 enxerga a fase inteira |
| `PointAt` | ✅ | entradas `x` e `y`, saída `rot`; a caixinha `Rotate sprite` nasce marcada. Liga-se `Proximity.x → x` e `Proximity.y → y` |
| `Velocity.forward` | ✅ | «frente» é para onde o `PointAt` virou o objeto. **Número 2 leva ~8,5 s para cruzar a fase** (≈100 px de imagem por segundo) |
| `Object Variable` | ⚠️ | mesmas três entradas (`set`, `get`, `+`) e saída `out` da global, mas o diálogo de criar **só tem `Name` e `Type`** — sem `Default Value`. Nasce valendo 0. O valor de partida entra por `Once → Number → set` |
| a lista de nomes | ⚠️ | na global a entrada se chama `+ Add New Name`; na variável do objeto, `+ Add New Variable`. `usa_global` procura o pedaço comum, `add new` |
| `+` com valor negativo | ✅ | a documentação diz que o `+` **soma o valor que chega**, e funciona: `Number(-1)` ligado nele subtrai um, e a variável avisa a barra pela saída `out` |
| `Bar` | ✅ | entrada `value`, saída `out`; painel `Current value` (nasce 5), `Max value` (nasce 10), cor da moldura e cor da barra — **as duas cores nascem ALEATÓRIAS**. Desenha no canto de cima, à esquerda, da fase |
| `Expression` | ✅ | existe (`A`, `B`, `eval` → `out`), mas **ficou de fora**: o `+` negativo faz a mesma conta com um bloco a menos |
| `Collision` | ⛔ | **dispara UMA vez por batida.** Com um morcego atravessável em cima do jogador por 40 s, a barra desceu uma vez (5096 → 3404 px) e parou. O dano contínuo é `Timer → Proximity` do lado do jogador |

⛔ **O morcego sólido empurra o jogador para fora da fase.** Parado no chão, o
jogador foi arrastado até a beirada, caiu fora do nível e **sumiu** — com o
morcego pregado na borda. O conserto é o da lava da Aula 3: `is solid`
desmarcado (atravessa) e `enable collisions` marcado (devolve o toque sem o
empurrão).

## 2ai. ⛔ Prova que mede um objeto em movimento começa NO CLIQUE

A prova da perseguição saiu «verde» três vezes com a distância já em 3 px na
primeira leitura. Três atrasos somados, todos ANTES da primeira medida:

1. `A.gesto('jogar')` espera a tela **parar** (até 15 s) — e numa fase em que
   o morcego voa ela nunca para. O clipe `jogar` agora vem da aula anterior;
2. `editor.exige_jogo()` lê a tela várias vezes: **~30 s**;
3. o clique de foco no jogo.

O morcego cruza a fase em 8,5 s. A regra: **clicar em Play e ler NA HORA**; o
`exige_jogo` e o clique de foco vêm depois (retrospectivos). E a prova passou a
exigir que a **primeira** leitura seja longe (≥ 250 px), senão ela reprova por
«não vi a viagem».

⭐ E a segunda fase da prova, que é a que prova «olhar»: depois de o morcego
chegar, o jogador corre para o outro lado e o morcego **tem de mudar de rumo**
(x 1082 → 1594). Um morcego que só voasse em linha reta até onde o jogador
ESTAVA passaria na primeira fase.

## 2aj. A leitura do campo precisa de recorte do tamanho do campo

- `campo_abaixo` lia uma faixa de ±75 px; num painel de campos empilhados (a
  `Bar`) ela apanhava o rótulo do campo de cima — `Current value: ...` em vez
  de `3`. Agora `meia=` é parâmetro (38 na `Bar`).
- O `+` do painel do `Filter` **não é uma palavra**: o OCR não o lê, e a Aula 7
  só o achava por sorte. O número agora se **escreve** no campo (positivo não
  sofre do problema do hífen).
- A cara do bloco chega do OCR como `input` e `<1` — duas palavras.
  `tem_texto('input < 1')` reprovava uma condição CERTA; compare sem espaços.
- O clique no campo do número cai em `centro da frase − 25 px`. Com −60 ele
  caía na borda esquerda do campo, fora dele.

## 2ak. As peças da Aula 10, medidas antes de a aula existir

| peça | medido | o que ficou sabido |
|---|---|---|
| painel `Game Levels` | ✅ | uma **linha por fase**: nome, cor (hex + amostra), `Load` (ou `Current`, na fase aberta), ordem `- +`, lixeira. Botões `New Level`, `OK`, `Loading Screen` |
| `New Level` | ✅ | cria uma fase **vazia**, chamada `New Level`, de céu branco. O painel **cresce para cima**: as linhas se contam a partir do `Loading Screen` (última linha: −91 px; cada anterior, +74) |
| ⚠️ o nome da 2ª fase | ⛔ | **também nasce `New Level`** — e o OCR achava a linha em vez do botão. Ancore no `Loading Screen` |
| `Current` | ⚠️ | o botão da fase aberta é branco sobre azul: **o OCR não o lê**. Se a linha pedida não tem `Load`, ela já é a atual |
| ⛔ o `Play` | ⛔ | **começa na fase que está ABERTA NO EDITOR, não na primeira.** Medido: com a Fase 1 carregada, o jogo abriu nela, sem botão. Quem quer testar a corrente inteira carrega o `Titulo` antes |
| `MouseClick` | ✅ | saídas `down`, `up`, `over`, `out`; painel `leftClick`/`rightClick` e `capture clicks anywhere`. Sem a caixinha, só dispara **em cima do objeto**. O clique da bancada o dispara |
| `Load Level` | ✅ | o título na mesa é `LoadLevel` (sem espaço, como `RestartGame`). Entradas `go`, `get`; saídas `out`, `out`. Nasce em `Next Level` — **não precisa mexer no painel** |
| a Biblioteca | ✅ | lista os **tipos**; clicar no cartão não faz nada, **arrastar** solta uma instância na casa. O painel cobre a faixa de baixo (x 930–1590): solte longe dele |
| os blocos | ✅ | pertencem ao **TIPO**: a estrela arrastada para a Fase 2 já sabia carregar a próxima fase |
| `Label` | ⚠️ | nasce com cor **aleatória** (7872A7, AF6A69…); em título azul-escuro o roxo some. A caixa de texto é multilinha e o OCR a lê mal — o texto aparece **também** em letra grande no canto da fase, e é ali que se confere |
| `Label` + `attach to object` | ✅ | o texto passa a ser desenhado **no objeto**: é o rótulo do botão |

⛔ **`solta` recarrega a página na última tentativa, e a página reabre no
PRIMEIRO nível.** Um `Label` solto fora do recorte de leitura (y alto demais)
não foi achado, `solta` recarregou, e a mesa seguinte era a do **Título**, com
o objeto errado. O erro que sobrou («não achei o bloco») mandava procurar o
defeito no bloco, não no nível. Regra: em aula com vários níveis, o recorte de
`bloco_ou_solta` tem de CONTER o ponto de soltura.

## 2al. A conferência de linha de painel é POR LINHA

Ler o painel `Game Levels` inteiro devolvia as linhas de cima e perdia a de
baixo (`Vitoria` estava escrita e visível, e a conferência dizia que não).
`editor.confere_nome_do_nivel` lê **só aquela linha**, em duas segmentações. A
cor do hex nunca se confere por OCR: confere-se **carregando a fase** e lendo o
céu (`cor_da_folha`), que é o que a criança vê.

## 3. As três armadilhas de FÍSICA que não aparecem no editor

Todas custaram horas na Aula 3, e nenhuma dá erro em lugar nenhum:

1. **`Collision` em `Any Type` conta com qualquer coisa.** Uma lava que sobe
   bate primeiro no CHÃO: o jogo reinicia sozinho a cada poucos segundos.
   → aponte para o TIPO (e por isso o objeto leva o mesmo nome no campo `Type`).
2. **Objeto sólido que se move TRAVA no cenário.** As peças clonadas param em
   alturas diferentes e a parede se parte.
   → desmarque `is solid`.
3. **…mas desmarcar `is solid` desliga a BATIDA junto.** No lugar dele nasce
   `enable collisions` — ela devolve o toque sem devolver o empurrão.

E uma de desenho de fase: **`Any Type` também deixa um objeto comer o outro**
— a lava destruía a estrela antes da criança chegar lá.

---

## 4. A lista de pré-voo (o que já me custou tempo antes)

Antes de dar uma aula por pronta, passe por estas. Cada uma é um erro que já
aconteceu, neste curso ou nos anteriores:

- [ ] **A promessa da página tem execução que a contradiga?** Prosa de aula não
      roda. Toda frase do tipo «ele faz X» vira uma medida na `prova`.
- [ ] **O guarda confere o INVARIANTE ou um proxy?** «Alguma coisa mudou no
      caminho» não é «há fio entre estes dois pinos» — e o proxy reprova quando
      o fio já estava lá.
- [ ] **«Existe caminho» não é «resolvível pelo programa que a aula ensina».**
      Prove que dá para VENCER a fase, não só que ela carrega.
- [ ] **As duas medidas saem do MESMO quadro?** Cada chamada tirava a sua
      própria foto, meio segundo depois da outra. Com o jogo piscando entre
      aceso e apagado, eu lia «a estrela não está» no quadro escuro e «o boneco
      está» no quadro aceso — dois instantes — e chamava de vitória. Uma foto,
      todas as medidas; e **a foto que a aula publica é o quadro que provou**,
      não outra tirada depois.
- [ ] **A sonda está medindo o ator certo?** Uma série constante em 447 era a
      ESTRELA sendo lida como lava.
- [ ] **A peça certa já existe e o chamador não foi trocado?** Cinco vezes numa
      sessão: `_acha_no_painel` olhava os dois lados e só a Aula 1 a usava;
      `prepara_menos`/`clica_menos` existiam e a captura chamava a versão
      antiga; `procura_forte` percorre a escada atrás de UMA palavra e
      `na_tela` pegava a primeira leitura qualquer. **`grep` dos chamadores
      antes de dar por consertado** — a glosa no código não troca ninguém.
- [ ] **A régua depende de uma propriedade ACIDENTAL do que ela mede?** Cinco
      vezes numa sessão: passo da grade de sprites «é 85» (era 89), casa do
      nível «é 64» (varia com o zoom), mínimo da barrinha «é 16» (é 4), zoom
      normal «é 1» (é 100), e a folha «é branca» — até a aula passar a pintar
      o céu, e a régua dizer que não havia folha. **Régua que depende da cor do
      que mede quebra no dia em que a cor vira conteúdo.**
- [ ] **O meu lixo na conta quebra a minha ferramenta?** Jogo sem miniatura
      mostra um cartão de cor SORTEADA, e um deles saiu verde — dentro da faixa
      onde eu procuro o verde do botão `+ New Game`. Rascunho se chama
      `rascunho`, e some quando o dono mandar.
- [ ] **Isto está no handbook?** `grep -i "<bloco>" fonte/docs/handbook.txt`
      antes de medir na tela. Medir o que está escrito é o jeito mais caro de
      aprender — e o mais sujeito a eu concluir errado com dados certos.
- [ ] **O defeito pode estar no INSTRUMENTO, e não na aula?** Quatro medidas
      consistentes diziam «o boneco não pula correndo», e a leitura natural
      era que a fase não tinha saída. Estavam todas certas sobre o que mediam
      e erradas sobre o que isso significava. O conserto «óbvio» — alargar as
      plataformas — teria piorado a aula por um motivo que não existia. Quando
      a medida condena o DESENHO da aula, peça a mão do Julio antes de mexer
      nele: a mão dele é o único instrumento que enxerga um defeito do meu.
- [ ] **A sonda sabe distinguir «sumiu» de «apagou»?** O Flowlab **escurece o
      jogo inteiro** quando a página perde o foco — nada some, só apaga, e as
      cores medidas no sprite deixam de bater. Ausência de amarelo é a mesma
      leitura em dois casos opostos («a criança pegou» e «o jogo está
      pausado»). Toda prova que conclui por AUSÊNCIA tem de exigir, na MESMA
      leitura, que outra coisa viva esteja na tela — e, quando as duas somem,
      clicar dentro do jogo antes de desistir.
- [ ] **O verde é novo? Sabote e repita.** Guarda que não reprova quando eu
      quebro de propósito não está guardando nada.
- [ ] **O texto ainda fala de pintar?** Trocar o quadrado pelo sprite deixa
      «pinte de verde», «a latinha» e «o seu quadrado azul» vivos em `ck` e
      `sos` de três aulas. `grep -n "pinte\|latinha\|balde\|quadrado"`.
- [ ] **A foto bate com o texto?** Figura só se confere com o olho; o `ck` que
      descreve o que a foto não mostra é uma mentira silenciosa.
- [ ] **A função que ESCREVE confere o que escreveu?** `cor_do_ceu` abria o
      painel, digitava a cor, apertava Enter, imprimia «céu em #87CEEB» e
      devolvia — sem olhar nada. Uma aula inteira foi capturada de um jogo
      BRANCO com o passo 3 jurando que o céu estava pintado. O invariante é o
      que a criança vê (a cor da folha), não o texto do campo.
- [ ] **Estou lendo um arquivo que outro processo está escrevendo?** Três vezes
      numa madrugada eu medi fotos da pasta da aula no meio da captura e tirei
      conclusão da versão anterior — uma delas me fez acusar um defeito que não
      existia. E o irmão silencioso: duas coisas minhas rodando OCR ao mesmo
      tempo liam a imagem UMA DA OUTRA, porque o temporário tinha nome fixo.
      Arquivo de ferramenta leva o PID; arquivo de captura só se lê depois que
      o processo saiu.
- [ ] **O passo que manda clicar diz ONDE?**
- [ ] **Cabe em 50 minutos?** Um passo com três blocos, dois fios e um número é
      dois passos.
- [ ] **O artefato é mais novo que a fonte?** `find fonte -newer <saída>`.
- [ ] **Está no AR, não só commitado.**

---

## 5. O atalho que ainda não foi testado

A comunidade do Flowlab descreve **copiar e colar blocos como JSON pelo
clipboard**: ferramenta de seleção na mesa → `copy`; na outra mesa, clicar no
vazio → `Import` → Cmd+V.

Se o formato for texto, dá para montar a árvore de blocos em Python, jogar no
clipboard com `pbcopy` e colar — e aí o **passo 1 do laço** (provar a mecânica)
fica barato. O `PLANO.md` §6 já previa isso como plano B e eu demorei a usar.

⚠️ Isso serve para **descobrir e provar**, não para capturar: as fotos e os
clipes da aula têm de mostrar o caminho da criança.

Teste de um minuto: abrir uma mesa com blocos, selecionar, `copy`, e olhar o
`pbpaste`.
