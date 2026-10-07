# Estado do curso de Flowlab — 07-10-2026, madrugada

**Três aulas no ar, e nesta noite a Aula 2 estava publicada com um defeito que
nenhum guarda via: o boneco corria e não pulava.** A causa e o conserto estão
abaixo, junto com tudo o mais que mudou — para a próxima sessão não redescobrir
nada.

## O que está pronto

| aula | jogo | o que a aula entrega | provado em jogo |
|---|---|---|---|
| 1 | pega-moedas | boneco anda, moeda some | sim |
| 2 | pulo e plataformas | 28 colunas, **câmera que segue**, céu azul, lava que reinicia | pulo 198 px · reinício · câmera (chão desliza 192 px, boneco varia 164) |
| 3 | a lava que sobe | céu de noite, lava que sobe sozinha, estrela no alto | lava sobe 170 px · reinício · estrela pega |

Aulas 4 a 12: planejadas em `PLANO.md`, não construídas.

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
- **Aula 4 (nave e tiro).** Antes de desenhar, **medir se o bloco `Keyboard`
  solto dispara pela bancada**. O que já se sabe: as setas do pacote
  `Run & Jump` disparam (e o miolo dele são blocos `Keyboard`), e um `Keyboard`
  solto nunca foi medido. Se não disparar, **parar e avisar** — a mão dele é o
  instrumento.
- **Os jogos de rascunho na conta.** Sobraram vários `New Game` sem uso,
  inclusive o `3151717` (a Aula 2 velha, com o boneco que não pula). Apagar
  depende dele pedir.
