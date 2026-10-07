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

⛔ **Duas armadilhas de desenho de teste que me custaram meia hora cada:**

1. **Entrada só aceita UM fio.** Ligar um segundo bloco à mesma entrada é
   recusado pelo Flowlab — e o `liga_fixo` dizia que tinha ligado, porque
   contava o fio que já estava lá (§ `prova_fio_entre_pinos.py`).
2. **`Spawn` do PRÓPRIO tipo que contém o spawner é uma bomba.** Mandei o
   boneco criar bonecos, cada um com o mesmo `Timer`: o canvas ficou preto em
   segundos. Para medir `Spawn`, crie um tipo que **não** tenha o spawner.

---

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
