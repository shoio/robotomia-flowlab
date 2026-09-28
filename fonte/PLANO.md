# Curso de Flowlab da Robotomia — plano

Escrito em 27-09-2026, antes de construir. Formato herdado do curso de Roblox
(`github.com/shoio/robotomia-roblox`), que ja esta no ar com 10 aulas: mesma
pagina, mesmo PDF, mesmos guardas, mesmo processo.

---

## 1. O que muda do Roblox para o Flowlab

| | Roblox | Flowlab |
|---|---|---|
| Onde roda | Studio instalado | **navegador**, conta logada |
| Programacao | codigo Lua digitado | **blocos de comportamento** ligados por fios |
| Um jogo por | curso (o obby cresce) | **aula** — cada aula nasce e termina um jogo |
| Publicar | experiencia na Roblox | link do Flowlab, que a familia abre |

O aluno **nao digita codigo**. Isso muda o que cada aula ensina: no Roblox o
degrau era a sintaxe; aqui o degrau e **a ligacao entre gatilho e acao** —
*quando isto acontece, faca aquilo*. E a mesma ideia de programacao, sem a
barreira do teclado.

A conta e **INDIE com jogos ilimitados**, entao cada aula tem o seu jogo
proprio, do zero — como o PADRAO do Roblox exige (projeto novo a cada aula,
porque as aulas sao em semanas diferentes e ninguem depende do arquivo da
semana passada).

---

## 2. As doze aulas

Cada aula termina com **um jogo que da para jogar e mandar o link** no mesmo
dia. 19 ou 20 passos, 50 minutos.

| # | Aula | O jogo que sai pronto | O que e novo |
|---|---|---|---|
| 1 | **Seu primeiro jogo: pega-moedas** | boneco anda, encosta na moeda, ela some e o placar sobe | criar objeto, desenhar sprite, mover com as setas, `Collision`, `Destroyer`, `Number` + `Label` |
| 2 | **Pulo e plataformas** | plataforma lateral com gravidade, pulo e queda que reinicia | fisica, `Keyboard`, `Jump`, camera que segue |
| 3 | **A lava que persegue** | corrida contra um perigo que sobe, com reinicio | `Always`, `Timer`, `Motion`, fim de jogo |
| 4 | **Nave e tiro** | naves inimigas descendo, tiro que destroi, placar | `Spawn`, `Mailbox` (objetos conversando), limpar o que sai da tela |
| 5 | **Um botao so (estilo Flappy)** | passaro entre canos, ponto a cada passagem | aleatorio, padrao de spawn, dificuldade que cresce |
| 6 | **Chave e porta** | labirinto com chave, porta trancada e final | `Property` como memoria, mensagem entre objetos |
| 7 | **Empurra-blocos** | quebra-cabeca: empurrar caixas ate os alvos | movimento em grade, condicao de vitoria contando |
| 8 | **Contra o relogio** | percurso cronometrado, com recorde da partida | `Timer` mostrado na tela, formatar numero |
| 9 | **Inimigo que persegue** | inimigo com IA simples, vida e barra de vida | proximidade, `Health`, barra de GUI |
| 10 | **Menu, fases e fim de jogo** | jogo com tela de titulo, 3 fases e tela de vitoria | `Game Flow`, varios niveis, botao clicavel |
| 11 | **Som, animacao e brilho** | o mesmo jogo, mas com vida: animacao, som, particulas | editor de animacao, `SoundEffect`, `Emitter` |
| 12 | **Projeto livre e mostra** | o jogo do aluno, publicado, com link para a familia | escolher, montar com o kit das 11 aulas, publicar |

**Por que nesta ordem:** as duas primeiras dao o par mais motivante e mais
barato (andar e pular). Da 3 a 5 entram as tres ideias que sustentam quase
todo jogo (tempo, criar coisas, acaso). 6 e 7 sao logica de verdade — memoria
e condicao — disfarcadas de jogo. 8 e 9 sao numero e inimigo. 10 transforma um
jogo numa *obra* (menu, fases, fim). 11 e polimento, que e onde a crianca se
orgulha. 12 fecha como a Aula 9 do Roblox fecha: projeto proprio e mostra.

---

## 3. O formato de cada aula (herdado, nao reinventado)

Igual ao `PADRAO.md` do Roblox, com uma diferenca: **nao ha bloco de codigo
digitado**; no lugar dele ha o **quadro de ligacao** — a lista dos blocos que
entram e de quais fios ligam onde.

- 19-20 passos, cada um com **foto da tela de verdade**;
- passos de gesto novo ganham **clipe** (GIF curto com o cursor);
- **quadro verde** (`ck`): como o aluno sabe que deu certo, pelo que APARECE;
- **quadro laranja** (`sos`): sintoma na voz da crianca + conserto;
- fim: o link do jogo publicado.

**Sobre os videos do Flowlab:** a plataforma tem videos oficiais. Onde um
gesto for mais claro em movimento, eu capturo do **editor de verdade**, nao do
video deles — as fotos do curso sao todas da tela real, como no Roblox. Se em
algum ponto eu quiser usar quadro de video deles, eu pergunto antes: material
de curso vendido para escola com imagem de terceiro e decisao sua, nao minha.

---

## 4. A maquina (o que ja funciona)

`fonte/nav.py` dirige o **Chrome com a sua conta logada**:

- acha a janela do Flowlab **pelo titulo da aba** — as duas listas de janelas
  do Chrome discordam entre si, e eu ja ia navegando numa e fotografando outra;
- `espera_parar()` espera a tela **parar de mudar**, em vez de dormir um tempo
  fixo e fotografar pagina pela metade;
- `acha_cor()` acha botao **pela cor**: o OCR nao le texto branco sobre botao
  colorido (medido: quatro modos de segmentacao, lista vazia);
- captura teimosa: logo depois de levantar a janela o Chrome devolve quadro
  preto, e o guarda de quadro cego (herdado do Roblox) recusa — entao eu repito
  em vez de afrouxar o guarda.

⛔ **JavaScript por AppleScript esta bloqueado** no Chrome por seguranca (tentei
ligar pelo menu; ele ignora o clique programatico). Entao nada de DOM: tudo por
pixel, cor e OCR — que e exatamente o que o curso de Roblox ja faz.

---

## 5. Como cada aula e construida (o laco)

1. **Provar a mecanica no editor**, antes de escrever a aula. Foi assim que a
   Aula 10 do Roblox nasceu certa, e foi por nao fazer isso que oito aulas de
   la estao escritas e nunca provadas.
2. Escrever o roteiro dos 20 passos.
3. `capN.py`: o robo constroi o jogo no Flowlab, capturando a cada gesto.
4. Montar clipes, converter para JPEG, rodar os guardas.
5. **Jogar o jogo** e provar que ele faz o que a aula promete.
6. **Engenharia reversa**: reler a aula como aluno, um passo por vez, sem usar
   o que eu sei — e consertar o que faltar. E esta passada que acha o passo
   *certo e incompleto*, que nenhum guarda pega.
7. Build, publicar, conferir **no ar**.

---

## 6. O que pode dar errado, dito antes

- **Arrastar bloco e ligar fio** e o gesto mais fino do Flowlab (o editor de
  comportamento e um canvas: os pinos sao circulos de poucos pixels). Se a
  ligacao por robo nao ficar confiavel, o plano B e montar o comportamento e
  capturar o RESULTADO, com o clipe do gesto refeito passo a passo.
- **A arte**: o Flowlab tem editor de pixel proprio. Desenhar por robo e caro;
  as aulas usam formas simples e a biblioteca de sprites, que e o que uma
  crianca de 10 anos faz mesmo.
- **Tempo**: no Roblox, uma aula inteira custou ~25 min de captura depois da
  maquina pronta, e a maquina levou uma noite. Aqui a maquina esta meio pronta
  (nav.py de pe, gerador do site herdado).

---

## 7. Ordem de trabalho desta noite

1. Provar no editor: criar objeto, desenhar, arrastar bloco, ligar fio, jogar.
2. Aula 1 inteira, do zero ao ar.
3. Aula 2, 3, … publicando **uma a uma**, na ordem da tabela.

Cada aula publicada e uma aula que da para dar amanha, mesmo que a noite acabe
antes da doze.
