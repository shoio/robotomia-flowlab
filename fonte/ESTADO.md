# Estado do curso de Flowlab — 11-10-2026 (noite)

**Sete aulas no ar**, em https://shoio.github.io/robotomia-flowlab/ — conferido
em produção, não só commitado.

O que custou a madrugada está no `PADRAO.md`, §2n a §2t. O maior é o §2n: o
remendo da bancada sumia por ordem de import e **todo arrasto ia para a tela de
verdade**, em silêncio, com o defeito latente também em `cap1`, `cap2` e `cap3`.

## O que está pronto

| aula | jogo | o que a aula entrega | provado em jogo |
|---|---|---|---|
| 1 | pega-moedas | boneco anda, moeda some | sim |
| 2 | pulo e plataformas | 28 colunas, **câmera que segue**, céu azul, lava que reinicia | pulo 198 px · reinício · câmera (chão desliza 192 px, boneco varia 164) |
| 3 | a lava que sobe | céu de noite, lava que sobe sozinha, estrela no alto | lava sobe 170 px · reinício · estrela pega |
| 4 | nave e tiro | céu de espaço, nave que anda para os dois lados, tiro no espaço, canhão que solta inimigos, tiro que destrói | esquerda move 86 px e direita traz 123 de volta · espaço faz nascer tiro · inimigo desce 687 px sozinho |
| 5 | um botão só | passarinho com gravidade, chão, bolas de fogo em alturas sorteadas, fim de jogo e **placar na tela** | espaço levanta 331 px e a gravidade traz de volta · fogo separado por 653 px num mesmo quadro · placar sobe sozinho |
| 6 | chave e porta | plataforma, porta de três pedaços fechando o caminho, chave que **manda recado** e estrela do outro lado | seta leva o jogador 398 px · pulo de 154 px · a metade de cima vai de 8128 a 0 px de não-céu quando a chave fala · estrela de 704 a 0 |
| 7 | empurra-blocos | três caixas empurráveis, um alvo que **conta**, e um `Filter` que abre a porta quando o número passa de 2 | placar sobe até 3 e a porta cai sozinha (13004 → 1170 px de não-céu) |

Aulas 8 a 12: planejadas em `PLANO.md`, não construídas.

## Pendente para o Julio

- ~~Push~~ **feito em 11-10**: as aulas 4 e 5 estão no ar e conferidas em
  produção (a home diz "5 de 12 aulas no ar").
- ~~Placar~~ **decidido em 11-10: o placar vai para a Aula 5**, que já promete
  "ponto a cada passagem" — lá ele é a ideia NOVA da aula (`Number` + `Label` e
  a camada de GUI), e não a quarta ideia espremida numa aula cheia. A Aula 4
  fica sem pontuação, de propósito. A Aula 8 (`recorde da partida`) passa a
  construir em cima dele, não do zero.
  ⚠️ `Label` não aparece em aula nenhuma até aqui — conferido, não lembrado.
- **Jogos de rascunho.** As corridas desta noite deixaram vários jogos novos na
  conta. Só `fonte/aula4/jogo.txt` é o da aula; o `apaga_jogo.py` recusa apagar
  qualquer id que esteja num `aulaN/jogo.txt`. Não apaguei nenhum sem pedir.

## ⚠️ O defeito da noite: o céu azul desmarcava `movable`

`AZUL_OK` é `(126,168,224)`; o céu da Aula 2 é `87CEEB` = `(135,206,235)`.
Distância `(9,38,11)`, **dentro da tolerância 40**. `fecha_painel_objeto`
achava um pedaço de céu em vez do botão, e o clique caía dentro do painel de
física **em cima da caixinha `movable`**.

Em jogo: o boneco **anda e não pula** — `Velocity` move objeto parado,
`Impulse` (o pulo) não. A Aula 3 escapou porque o céu dela é de noite.

Três coisas que valem para sempre:

1. **Teto de tamanho não resolve.** Eu já tinha consertado a função irmã
   (`abre_fisica`) com um limite de pixels; aqui ele passa — o céu se parte
   em pedaços de 97 mil e o botão tem 24 mil.
2. **O que separa os dois é a PALAVRA no botão.** `comum._ponto_do_ok` lê o
   rótulo e só cai na cor como reserva.
3. **Isso só ficou possível porque a escada de OCR ganhou os degraus de
   limiar 200.** Ela parava em 170, e com isso **todo** rótulo branco sobre
   botão azul do Flowlab era invisível — inclusive o nome do pacote de sprites
   *quando ele está selecionado* (foi o que parou a captura com «não achei
   `Flowlab Sprites`», com o nome aceso na tela).

Trancado por `prova_ok_nao_e_o_ceu.py`. E `jogador()` das duas aulas agora
**reabre a física depois de fechar** e exige `movable` marcado.

## Os outros consertos desta noite

- **`rs.procura_forte` achava o alvo por um PEDAÇO dele.** «New Game», o
  título da *página do jogo*, casava com `Game Levels`, que só existe no
  editor — e `editor.no_jogo()` decidia com isso. Agora junta a LINHA antes de
  comparar e aceita um **prefixo de 60%** do alvo (o OCR corta o fim de rótulo
  comprido: «affected by gravi»). `prova_casamento_ocr.py` guarda os dois
  lados, inclusive o conserto intermediário que eu quase publiquei sozinho.
- **A bancada tem duas metades.** `BANCADA=1` posta sem os remendos já era
  barrada; agora **motor de pé + `BANCADA` ausente** também para. Três sondas
  minhas fotografaram o Chrome do Julio e levaram a aba dele para a página do
  jogo. Quem precisa da tela de verdade diz `TELA_DE_VERDADE=1`.
- **Duas fotos iguais byte a byte** na mesma aula agora reprovam. Pegou a foto
  do limite da câmera (mostrava a figura do passo anterior, sem o número) e
  três fotos do cenário PRONTO em passos que prometem o cenário pela metade.
- **Foto publicada mais velha que a captura** também reprova. Pegou as três
  aulas de uma vez: a página mostrava os JPEG de antes do céu.
- **Aula 3 ganhou o passo 4, «Pinte o céu de NOITE».** O jogo já nascia
  pintado na captura e a aula nunca mandava a criança pintar.
- **O passo do céu virou dois clipes com abas.** Com um só, a seta apontava
  para o campo da cor, que no quadro de antes nem está na tela —
  `confere_alvos` acusa isso sozinho.

## ⚠️ Retomar uma etapa do meio FOTOGRAFA O FIM

Cada etapa é tolerante de propósito, para a captura poder ser retomada depois
de um erro. **Essa mesma tolerância faz a foto mentir**: rodar `plataformas`
num jogo já completo não dá erro e salva o cenário pronto com o nome do passo
«faça o chão». Etapa do meio refeita num jogo pronto exige **recapturar a aula
inteira**, do `novo`.

## Como se roda

```
node fonte/bancada/motor.mjs &          # a bancada, fora da tela dele
BANCADA=1 python3 fonte/cap2.py         # a aula inteira, do zero
BANCADA=1 python3 fonte/cap2.py prova   # de uma etapa em diante
BANCADA=1 python3 fonte/refaz_clipes.py ceu2    # só os clipes do céu
python3 fonte/gera_gifs.py aula2 && python3 fonte/para_jpeg.py aula2
python3 fonte/build_curso.py            # roda os dois guardas antes de montar
for f in fonte/prova_*.py; do python3 $f; done
```

`BANCADA=1` é obrigatório: sem ela, com o motor de pé, tudo para (de
propósito).

## O que ficou em aberto

- **Fundo decorado com parallax.** O `Camera` tem `Parallax` (% da velocidade
  do cenário) e `Background Repeats`, e a camada `Background` não tem física
  nem comportamentos. Dá profundidade de verdade, mas são 2 a 3 passos novos —
  não cabe na Aula 2, que já está em 20. Decisão do Julio: aula própria ou
  passo extra.
- **Aula 4 (nave e tiro).** As três peças novas já estão **medidas na
  bancada**, antes de a aula ser desenhada (§2k do `PADRAO.md`): o `Keyboard`
  solto dispara, o `Timer` dispara sozinho e o `Spawn` cria objeto. Só o
  `MouseClick` continua sem medida. Falta escrever os 20 passos e o `cap4.py`.
- **Os jogos de rascunho na conta: sobram 46.** Dois foram apagados em 07-10
  (`3151717`, o boneco que não pulava, e `3152352`, a captura que falhou na
  estrela). O Flowlab guarda os apagados **uma semana** na lixeira.

  ⚠️ **O endereço que vale é SEMPRE o de `aulaN/jogo.txt`, lido na hora.** Eu
  escrevi aqui que `3152363` «seria descartável se a recaptura não fosse a
  última», e depois repeti isso como fato — e ele é a Aula 2 que está no ar.
  Na conta todos se chamam `New Game` e nenhum tem miniatura: não há como
  reconhecer pelo nome, só pelo id. O script de apagar recusa qualquer id que
  esteja num `jogo.txt`.

  Os outros 43 são rascunhos das medições e de capturas antigas. Apagar em
  lote depende dele pedir.

- **`3152613` é o PROTÓTIPO da Aula 4** — não é rascunho. Nele estão provados
  o `Keyboard[Espaço] → Emitter`, a direção do tiro e a física que ele precisa
  (§2l do `PADRAO.md`). Ele vira o jogo da aula ou é apagado quando o `cap4.py`
  criar o seu.
