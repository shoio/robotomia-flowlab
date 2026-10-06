# Como se faz uma aula de Flowlab da Robotomia

Leia isto **antes** de começar a próxima aula. Ele existe porque a Aula 3
custou uma tarde inteira redescobrindo coisas que já estavam escritas em algum
lugar — aqui, no `PADRAO.md` do curso de Roblox, ou na memória.

---

## 0. O que vem de graça do curso de Roblox

O formato da aula é o mesmo e **não se reinventa**: leia
`~/Coding/robotomia-roblox/fonte/PADRAO.md` §1, §2 e §7. O que vale igual:

- 19–20 passos, 50 minutos, projeto novo a cada aula, termina jogável;
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
2. Escrever o roteiro dos 20 passos, um por linha.
3. `capN.py` constrói o jogo capturando a cada gesto.
4. Clipes, JPEG, guardas.
5. **Jogar** e provar as promessas, uma a uma.
6. **Engenharia reversa**: reler como aluno, um passo por vez.
7. Build, publicar, conferir **no ar**.

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
