# -*- coding: utf-8 -*-
"""Aula 2 — Pulo e plataformas."""

AULA = {
 "n": 2,
 "slug": "aula2",
 "titulo": "Pulo e plataformas",
 "subtitulo": "Um jogo de subir: três plataformas, uma estrela no alto e lava embaixo. Caiu, recomeça.",
 "tempo": "50 minutos",
 "etiqueta": "Aula 2 · pulo",
 "fim": "Acabou a Aula 2. O seu jogo agora tem altura: dá para pular, dá para errar e dá para recomeçar. Mande o link para a sua família tentar chegar na estrela.",
 "avisos": [
   ("Jogo novo", "Esta aula começa num jogo novo, do zero. O da Aula 1 fica guardado na sua lista."),
   ("O que é novo hoje", "O <b>pulo</b> — e o peso que faz ele funcionar — e o <b>recomeçar</b> quando o jogador cai."),
   ("Os clipes", "Os passos com animação mostram o gesto inteiro: o mouse andando, o <b>botão certo acendendo</b> e o que muda na tela."),
   ("Travou?", "Todo passo tem um quadro laranja embaixo com o conserto dos erros mais comuns."),
 ],
 "passos": [

  dict(n=1, titulo="Abra o Flowlab", img="comum_fotos/c01_site.jpg", clipe=None,
    corpo="No navegador, vá para <span class=ui>flowlab.io</span>.<br><br>Se aparecer <span class=ui>Log in</span> no canto de cima à direita, clique nele e entre com a sua conta antes de seguir.",
    ck="Você está em flowlab.io e <b>não</b> aparece <span class=ui>Log in</span> no canto de cima.",
    sos=[("Aparece Log in","Clique nele e entre com o e-mail e a senha da sua conta. Sem entrar, o jogo não fica salvo.")]),

  dict(n=2, titulo="Entre em MY GAMES", img="comum_fotos/c02_lista.jpg", clipe="abrir_my_games.gif",
    corpo="No alto à direita, clique em <span class=ui>My Games</span>.<br><br>O jogo da Aula 1 está aí na lista — ele fica guardado. Hoje a gente faz outro, do zero.",
    ck="O título da página é <span class=ui>My Games</span> e o seu Pega-moedas aparece na lista.",
    sos=[("Minha lista está vazia","Você pode estar em outra conta. Clique na bolinha do canto de cima e confira.")]),

  dict(n=3, titulo="Crie um jogo novo", img="comum_fotos/c03_escolher.jpg", clipe="novo_jogo.gif",
    corpo="Clique no botão verde <span class=ui>+ New Game</span>, no canto direito.",
    ck="Apareceram duas figuras: <span class=ui>Empty Project</span> e <span class=ui>Flowlab Tutorial</span>.",
    sos=[("Não aconteceu nada","Clique de novo, uma vez só, bem no meio do botão verde. Às vezes ele demora alguns segundos para abrir a janelinha.")]),

  dict(n=4, titulo="Escolha o PROJETO VAZIO", img="aula2/p01_vazio.jpg", clipe="empty_project.gif",
    corpo="Clique na <b>figura</b> da esquerda, a do <b>+</b> grande.<br><br>Clique na figura, não no nome embaixo dela — o nome não responde.",
    ck="Sobrou a folha branca vazia, com a fileira <span class=ui>Play · Library · Game Levels · Layer · Settings</span> embaixo.",
    sos=[("Abriu o Flowlab Tutorial","Volte para <span class=ui>My Games</span>, apague esse jogo nos três pontinhos e comece de novo.")]),

  dict(n=5, titulo="Crie o jogador", img="aula2/g01_b.jpg", clipe="criar_objeto.gif",
    corpo="Clique uma vez dentro da folha branca, na <b>parte de baixo e à esquerda</b> — o boneco vai começar ali.<br><br>Abre a roda com <span class=ui>Create</span> e <span class=ui>Cancel</span>.",
    ck="Apareceu a roda escura com <span class=ui>Create</span> e <span class=ui>Cancel</span>.",
    sos=[("Apareceu Clone, Edit, Delete","Aquela casa já tem um objeto. Clique em <span class=ui>Cancel</span> e escolha uma casa vazia.")]),

  dict(n=6, titulo="Escolha CREATE", img="aula2/g02_b.jpg", clipe="escolher_create.gif",
    corpo="Clique na metade <span class=ui>Create</span> da roda.<br><br>Abre o painel do objeto, igual ao da Aula 1: <span class=ui>edit sprite</span>, <span class=ui>Behaviors</span>, <span class=ui>Name</span> e, no canto de baixo, <span class=ui>Physics ></span>.",
    ck="O painel do objeto está aberto.",
    sos=[("Cliquei em Cancel","Clique na mesma casa de novo e escolha <span class=ui>Create</span>.")]),

  dict(n=7, titulo="Dê o nome JOGADOR", img="aula2/p02_nome.jpg", clipe=None,
    corpo="No campo <span class=ui>Name</span>, apague o que está escrito, escreva <b>Jogador</b> e aperte <span class=ui>Tab</span>.<br><br>Não aperte Enter: o Enter fecha o painel antes da hora.",
    ck="O campo <span class=ui>Name</span> mostra <b>Jogador</b> e o painel continua aberto.",
    sos=[("O painel fechou","Foi o Enter. Clique na casa do boneco, escolha <span class=ui>Edit</span> e escreva de novo, terminando com Tab.")]),

  dict(n=8, titulo="Pinte o jogador de azul", img="aula2/p03_azul.jpg", clipe=None,
    corpo="Clique em <span class=ui>edit sprite</span>. No editor de desenho:<br><br><b>1.</b> Clique na ferramenta <b>balde</b>.<br><b>2.</b> Clique num <b>azul</b> da paleta da direita.<br><b>3.</b> Clique nas <b>três partes</b> do desenho.<br><br>Depois clique em <span class=ui>OK</span>, no canto de baixo à esquerda.",
    ck="O boneco ficou um quadrado azul inteiro.",
    sos=[("Sobrou pedaço de outra cor","O balde pinta uma região por vez: clique nas outras partes também.")]),

  dict(n=9, titulo="Abra as regras de física", img="aula2/g03_b.jpg", clipe="abrir_physics.gif",
    corpo="No painel do objeto, clique em <span class=ui>Physics ></span>, no canto de baixo à direita.",
    ck="Apareceram <span class=ui>movable</span>, <span class=ui>is solid</span>, <span class=ui>Density</span>, <span class=ui>Bounce</span> e <span class=ui>Friction</span>.",
    sos=[("Não acho o Physics","É o texto azul do canto de baixo à direita do painel, ao lado do <span class=ui>OK</span>.")]),

  dict(n=10, titulo="Marque MOVABLE", img="aula2/g04_b.jpg", clipe="marcar_movable.gif",
    corpo="Clique na caixinha <span class=ui>movable</span>.<br><br>Ela libera as outras: sem ela, o boneco não anda, não cai e não pula.",
    ck="A caixinha ficou <b>azul</b> e apareceu <span class=ui>affected by gravity</span> ao lado, também marcada.",
    sos=[("A caixinha não fica azul","Clique no quadradinho, não na palavra."),
         ("Density continua cinza","É porque <span class=ui>movable</span> ainda está desmarcado.")]),

  dict(n=11, titulo="O peso certo — é ele que deixa pular", img="aula2/p04_fisica.jpg", clipe="peso_do_pulo.gif",
    corpo="Agora o passo mais importante da aula.<br><br><b>1.</b> Em <span class=ui>Density</span> (peso), clique na barrinha <b>um pouco antes da metade</b>, até o número ao lado ficar perto de <b>30</b>. A barrinha marca o valor <b>onde você clica</b>: se passar de 30, clique um pouco mais para a <b>esquerda</b>; se ficar abaixo, um pouco mais para a <b>direita</b>.<br><b>2.</b> Em <span class=ui>Friction</span> (atrito), clique na <b>ponta direita</b> da barrinha, para ficar <b>100</b>.<br><br>Por que isso importa: o pulo do Flowlab tem uma força <b>fixa</b>. Se o boneco for muito pesado, essa força não levanta ele do chão — ele simplesmente não pula. Se for leve demais, ele sai voando para fora da tela. Perto de <b>30</b> ele pula a altura de umas quatro casas, que é o que esta fase precisa.",
    ck="<span class=ui>Density</span> mostra um número perto de <b>30</b> e <span class=ui>Friction</span> mostra <b>100.0</b>.",
    sos=[("Meu boneco não pula de jeito nenhum","O peso está alto. Clique mais para a esquerda na barrinha do <span class=ui>Density</span>, até perto de 30."),
         ("Ele pula e some da tela","O peso está baixo demais. Clique um pouco mais para a direita."),
         ("O número foi para 100 e eu queria 30","Você clicou perto da ponta direita. Clique de novo um pouco antes da metade da barrinha.")]),

  dict(n=12, titulo="Dê movimento e pulo ao jogador", img="aula2/p05_run_and_jump.jpg", clipe=None,
    corpo="Feche a física no <span class=ui>OK</span> e clique em <span class=ui>Behaviors</span>.<br><br>Na coluna da esquerda, lá embaixo, clique em <span class=ui>Behavior Bundles</span> e <b>arraste</b> o <span class=ui>Run &amp; Jump</span> para o meio da mesa.<br><br>Esse pacote dá as setas para andar <b>e a seta de cima para pular</b>. Espere uns segundos antes de fechar — o Flowlab precisa de um tempinho para guardar.",
    ck="Um bloco <span class=ui>Run &amp; Jump</span> está na mesa de blocos.",
    sos=[("Arrastei e não ficou nada","Puxe de novo, mais devagar, e solte no meio da área escura."),
         ("Fechei e o bloco sumiu","Abra de novo e confira. Se sumiu mesmo, arraste outra vez e espere alguns segundos antes de fechar.")]),

  dict(n=13, titulo="Faça o primeiro chão", img="aula2/p06_chao.jpg", clipe=None,
    corpo="Feche as duas telas (<span class=ui>OK</span> da mesa de blocos e <span class=ui>OK</span> azul do painel).<br><br>Clique numa casa <b>logo abaixo</b> do boneco, escolha <span class=ui>Create</span>, chame de <b>Chao</b> e pinte de <b>verde</b>.<br><br>Depois clique nele, escolha <span class=ui>Clone</span> e clique nas casas ao lado para fazer uma plataforma de <b>quatro casas</b>, sem buraco. Clique em <span class=ui>Done Cloning</span> para parar.",
    depois="O chão <b>não</b> leva física: não marque <span class=ui>movable</span> nele. Só o jogador se mexe; chão e plataformas ficam parados.",
    ck="O boneco está em cima de uma faixa verde de quatro casas, sem buraco.",
    sos=[("Ficou buraco entre as peças","Clique exatamente nas casas vizinhas; buraco faz o boneco cair."),
         ("Meu chão caiu junto com o boneco","Você marcou <span class=ui>movable</span> no chão. Clique nele, vá em <span class=ui>Physics ></span> e desmarque."),
         ("Não paro de clonar","Clique em <span class=ui>Done Cloning</span>, no lugar onde antes estava escrito Library.")]),

  dict(n=14, titulo="Faça a segunda plataforma, mais alta", img="aula2/p07_plataforma.jpg", clipe=None,
    corpo="Agora uma plataforma <b>mais alta e mais à direita</b> — duas casas acima do chão e umas duas casas de distância.<br><br>Clique numa casa vazia ali, escolha <span class=ui>Create</span>, chame de <b>Plataforma</b>, pinte de <b>verde</b> e use o <span class=ui>Clone</span> para deixá-la com <b>três casas</b>.",
    ck="Há duas faixas verdes: a de baixo com o boneco e outra mais alta, à direita — e nenhuma delas com <span class=ui>movable</span> marcado.",
    sos=[("Minha plataforma ficou alta demais","Duas casas acima do chão é o certo. Mais que isso, o pulo não alcança: clique nela, escolha <span class=ui>Delete</span> e refaça mais baixo.")]),

  dict(n=15, titulo="Faça a terceira plataforma", img="aula2/p08_tres_plataformas.jpg", clipe=None,
    corpo="Repita: mais duas casas para cima e mais para a direita, uma terceira plataforma de <b>três casas</b>, chamada <b>Alta</b> e pintada de <b>verde</b>.<br><br>Olhe a fase inteira: tem de parecer uma <b>escada</b> de três degraus.",
    ck="Três faixas verdes em degraus, cada uma mais alta e mais à direita que a anterior.",
    sos=[("A escada ficou longe demais","Se o degrau estiver a mais de duas casas de altura, o pulo não chega. Apague e refaça mais perto.")]),

  dict(n=16, titulo="Ponha a lava embaixo de tudo", img="aula2/p09_lava.jpg", clipe=None,
    corpo="Lá embaixo, na última linha da folha branca, faça um objeto novo chamado <b>Lava</b> e pinte de <b>vermelho</b>.<br><br>Depois use o <span class=ui>Clone</span> para esticar a lava de <b>uma ponta à outra</b> da folha. Ela precisa cobrir todo o fundo — é onde o jogador cai quando erra o pulo.",
    ck="Uma faixa vermelha atravessa o fundo da tela inteira, sem buraco.",
    sos=[("Minha lava tem buracos","O jogador pode cair exatamente no buraco e não acontecer nada. Clone nas casas que faltam."),
         ("A lava ficou colada na plataforma","Deixe pelo menos duas casas de distância, senão o jogador encosta nela sem querer.")]),

  dict(n=17, titulo="Ensine a lava a recomeçar o jogo", img="aula2/p12_fio_lava.jpg", clipe=None,
    corpo="Clique na lava, escolha <span class=ui>Edit</span> e depois <span class=ui>Behaviors</span>. Monte dois blocos:<br><br><b>1.</b> Em <span class=ui>Triggers</span>, arraste <span class=ui>Collision</span> — o <b>quando</b>: <i>quando alguém encostar em mim</i>.<br><b>2.</b> Em <span class=ui>Game Flow</span>, arraste <span class=ui>Restart Game</span> — o <b>o quê</b>: <i>recomece o jogo</i>.<br><b>3.</b> Ligue o fio da bolinha <span class=ui>hit</span> até a bolinha <span class=ui>go</span>.<br><br>Lido em voz alta: <b>quando alguém encostar na lava, o jogo recomeça</b>.",
    depois="Feche as duas telas: <span class=ui>OK</span> da mesa de blocos e <span class=ui>OK</span> azul do painel.",
    ck="Um fio branco liga o <span class=ui>Collision</span> ao <span class=ui>Restart Game</span>.",
    sos=[("O fio não fica","Comece o arrasto em cima da bolinha e solte em cima da outra bolinha, devagar."),
         ("Arrastei e o bloco inteiro andou","Você pegou o bloco, não a bolinha. Use o <span class=ui>Undo</span> do canto de baixo à direita e tente de novo, mirando na bolinha."),
         ("Não acho o Restart Game","Ele está na categoria <span class=ui>Game Flow</span>, na coluna da esquerda.")]),

  dict(n=18, titulo="Ponha a estrela no alto", img="aula2/p14_fio_estrela.jpg", clipe=None,
    corpo="Em cima da terceira plataforma, crie um objeto chamado <b>Estrela</b> e pinte de <b>amarelo</b>.<br><br>Depois dê a ela o mesmo comportamento da moeda da Aula 1: em <span class=ui>Behaviors</span>, um <span class=ui>Collision</span> ligado a um <span class=ui>Destroyer</span> — <i>quando alguém encostar em mim, eu sumo</i>.",
    depois="Feche as duas telas no <span class=ui>OK</span>, como sempre.",
    ck="A estrela amarela está em cima da plataforma mais alta, e tem um fio ligando <span class=ui>Collision</span> a <span class=ui>Destroyer</span>.",
    sos=[("A estrela caiu quando eu joguei","Ela não precisa de física: deixe <span class=ui>movable</span> desmarcado nela."),
         ("A estrela some sozinha no começo","Ela está encostando na plataforma. Suba a estrela uma casa.")]),

  dict(n=19, titulo="Jogue e pule os degraus", img="aula2/p17_pulo.jpg", clipe="jogar.gif",
    corpo="Clique em <span class=ui>Play</span>. <b>Clique uma vez dentro do jogo</b> e use:<br><br><b>→</b> para andar<br><b>↑</b> para pular<br><br>Suba os três degraus e pegue a estrela. Dá para andar no ar enquanto pula — segure a seta de lado enquanto sobe.",
    ck="O boneco sai do chão quando você aperta a seta de cima, e consegue subir para a segunda plataforma.",
    sos=[("Ele anda mas não pula","Volte ao passo 11: o peso está alto demais. <span class=ui>Density</span> perto de 30."),
         ("Ele pula e some","O peso está baixo demais; aumente um pouco."),
         ("Ele pula mas não alcança a plataforma","O degrau está alto. Duas casas de altura é o limite confortável."),
         ("Nada acontece quando aperto as setas","Clique uma vez dentro do jogo antes: o teclado precisa estar 'dentro' dele.")]),

  dict(n=20, titulo="Caia de propósito — e veja recomeçar", img="aula2/p18_recomecou.jpg", clipe=None,
    corpo="Agora erre de propósito: ande para a esquerda até cair do chão.<br><br>Quando o boneco encostar na lava, o jogo <b>recomeça</b> e ele volta para o lugar onde começou. É o seu primeiro jogo com <b>chance de errar</b> — e é isso que faz um jogo ser jogo.<br><br>O endereço desta página é o link do seu jogo: mande para a sua família tentar chegar na estrela.",
    ck="Ao encostar na lava, o boneco voltou sozinho para a posição inicial.",
    sos=[("Caí e não aconteceu nada","A lava não cobre aquele pedaço, ou o fio do passo 17 não ficou ligado. Confira os dois."),
         ("O jogo recomeça sozinho sem eu cair","O boneco está nascendo encostado na lava. Suba o chão ou desça a lava.")]),
 ],
}
