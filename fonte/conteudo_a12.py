# -*- coding: utf-8 -*-
"""Aula 12 — Projeto livre e mostra."""

AULA = {
 "n": 12,
 "slug": "aula12",
 "titulo": "Projeto livre e mostra",
 "subtitulo": "O jogo agora é seu: clone um jogo do curso, deixe com a sua cara e mande o link para a família.",
 "tempo": "50 minutos",
 "etiqueta": "Aula 12 · projeto livre e mostra",
 "fim": "Acabou a Aula 12 — e acabou o curso. Em doze aulas você fez <b>jogos de verdade</b>: um boneco que pega moedas, pula, foge da lava, atira, voa, abre portas, empurra caixas, corre contra o relógio, é perseguido, tem menu e fases, e uma estrela que gira, brilha e faz barulho. Hoje você viu o que vem depois: <b>clonar</b> um jogo, <b>mexer nele</b> até ficar seu, e <b>mostrar</b> pelo link. Daqui para a frente, a regra é a mesma de todas as aulas: <i>quando isto acontecer, faça aquilo</i> — e agora a ideia de jogo é sua.",
 "avisos": [
   ("Aula diferente", "Hoje <b>não há bloco novo</b>. O projeto é seu: o roteiro mostra o <b>caminho</b> — clonar, mudar, jogar, mostrar — num jogo de exemplo. Na sua vez, mude o que quiser: outro céu, outro boneco, mais estrelas, um som diferente, uma fase a mais."),
   ("O clone é uma cópia", "<span class=ui>Clone</span> cria um jogo <b>novo</b>, igual ao primeiro. O que você mudar nele <b>não muda o original</b>: o jogo da Aula 11 continua do jeito que estava."),
   ("Cuidado com o Delete", "O menu do cartão tem um <span class=ui>Delete</span> em <b>vermelho</b>. Ele apaga o jogo de verdade. Não clique nele."),
   ("O link é para quem o professor e a família combinarem", "Quem tem o link joga o seu jogo. Mande só para as pessoas que o professor ou a sua família combinaram."),
   ("Travou?", "Todo passo tem um quadro laranja embaixo com o conserto dos erros mais comuns."),
 ],
 "passos": [

  dict(n=1, titulo="Abra o Flowlab e entre em MY GAMES", img="comum_fotos/c02_lista.jpg", clipe="abrir_my_games.gif",
    corpo="Abra o navegador em <b>flowlab.io</b> e entre com a sua conta.<br><br>No alto da página, clique em <span class=ui>My Games</span>. Aparecem os jogos que você já fez.",
    ck="Você está na lista <span class=ui>My Games</span> e vê os seus jogos.",
    sos=[("Não lembro a senha","Chame o professor. Não crie conta nova: os seus jogos estão na antiga."),
         ("A lista está vazia","Confira se entrou com a mesma conta das outras aulas.")]),

  dict(n=2, titulo="Escolha o jogo-BASE", img="aula12/p01_lista.jpg",
    corpo="Todos os cartões se chamam <span class=ui>New Game</span> e ainda não têm figura (<span class=ui>No Screenshot Yet</span>). O que ajuda: o <b>primeiro cartão</b>, no alto à esquerda, é o jogo que você <b>mexeu por último</b>.<br><br>Para partir do jogo da Aula 11 (a estrela que gira), o cartão certo é o primeiro. Se você mexeu em outro jogo depois dela, o cartão da Aula 11 desceu uma casa. Na dúvida, abra o cartão e jogue: o professor ajuda.<br><br>(Você também pode partir de <b>qualquer outro</b> jogo do curso.)",
    ck="Você sabe qual cartão é o jogo-base: o da <b>estrela que gira</b>.",
    sos=[("Não sei qual é o jogo da Aula 11","Clique em <span class=ui>Edit</span> num cartão: se aparecer a noite azul com a estrela, é ele. Volte para <span class=ui>My Games</span> e siga."),
         ("Quero partir de outro jogo","Pode. O caminho é o mesmo para qualquer cartão.")]),

  dict(n=3, titulo="Abra o menu do cartão", img="aula12/p02_menu.jpg", clipe="abrir_o_menu.gif",
    corpo="No cartão do jogo-base, clique nos <b>três pontinhos</b> (⋮), no canto de cima à direita do cartão.<br><br>Abre um menu pequeno com quatro opções: <span class=ui>Add Tag</span>, <span class=ui>Clone</span>, <span class=ui>Lock Version</span> e <span class=ui>Delete</span>.<br><br>⚠️ <b>Não</b> clique no <span class=ui>Delete</span> (em vermelho): ele apaga o jogo.",
    ck="Apareceu o menu com <span class=ui>Add Tag</span>, <span class=ui>Clone</span>, <span class=ui>Lock Version</span> e <span class=ui>Delete</span>.",
    sos=[("Não acho os três pontinhos","Eles ficam no canto de cima, à direita do <b>nome</b> do jogo, dentro do cartão."),
         ("O menu fechou","Clique nos pontinhos de novo.")]),

  dict(n=4, titulo="CLONE o jogo", img="aula12/p03_dialogo.jpg", clipe="clonar_o_jogo.gif",
    corpo="No menu, clique em <span class=ui>Clone</span>. Abre uma janela: <span class=ui>Clone New Game?</span> — <i>Cloning will create a copy of this game</i> (clonar vai criar uma cópia deste jogo).<br><br>Clique no botão azul <span class=ui>Clone Game</span>. Espere alguns segundos.",
    ck="A janela fechou e a lista de jogos tem <b>um cartão a mais</b>.",
    sos=[("Cliquei em Cancel","Faça de novo: pontinhos, <span class=ui>Clone</span>, e agora o botão azul <span class=ui>Clone Game</span>."),
         ("Clonei duas vezes","Sem problema: ficam duas cópias. Use a primeira e deixe a outra quieta.")]),

  dict(n=5, titulo="Abra o CLONE", img="aula12/p04_lista_clone.jpg", clipe="editar_o_clone.gif",
    corpo="A cópia aparece no <b>primeiro cartão</b>, com o nome <span class=ui>Copy of New Game</span> (cópia de New Game). O jogo antigo desceu uma casa.<br><br>Clique em <span class=ui>Edit</span>, embaixo da figura do cartão <span class=ui>Copy of New Game</span>.",
    ck="O editor abriu e o endereço do navegador tem um <b>número diferente</b> do jogo-base.",
    sos=[("Abriu o jogo antigo","Você clicou no cartão errado. Volte para <span class=ui>My Games</span> e abra o <b>primeiro</b>."),
         ("A lista não mudou","Espere uns segundos e aperte <b>F5</b> para recarregar a página.")]),

  dict(n=6, titulo="O clone é o MESMO jogo", img="aula12/p05_editor.jpg",
    corpo="Olhe o editor: a noite azul, o chão, o boneco e a estrela — tudo igual ao jogo da Aula 11. Os <b>blocos</b> também vieram junto com os objetos: você vai ver a estrela girar, brilhar e sumir quando o boneco encostar (e dá para ouvir o som de moeda).<br><br>É uma cópia <b>só sua</b>: a partir daqui, tudo o que você mudar acontece nela.",
    ck="O editor mostra o chão, o boneco e a estrela do jogo da Aula 11.",
    sos=[("O editor está vazio","Você abriu um jogo novo, e não o clone. Volte para <span class=ui>My Games</span> e clique em <span class=ui>Edit</span> no primeiro cartão.")]),

  dict(n=7, titulo="Abra o SETTINGS", img="aula12/p06_settings.jpg", clipe="abrir_settings.gif",
    corpo="Na barra de baixo, clique em <span class=ui>Settings</span> (o último botão, à direita).<br><br>Abre o painel <span class=ui>GAME SETTINGS</span>, com os campos <span class=ui>Name</span> (o nome do jogo), <span class=ui>Gravity</span>, <span class=ui>Drag</span>, <span class=ui>Width</span> e <span class=ui>Height</span>.<br><br>Hoje só o <span class=ui>Name</span> interessa.",
    ck="O painel <span class=ui>GAME SETTINGS</span> está aberto e o <span class=ui>Name</span> diz <span class=ui>Copy of New Game</span>.",
    sos=[("Não acho o Settings","É o último botão da barra de baixo, com o desenho de barrinhas e bolinhas.")]),

  dict(n=8, titulo="Dê um NOME ao seu jogo", img="aula12/p07_nome.jpg", clipe="escrever_o_nome.gif",
    corpo="Clique no campo <span class=ui>Name</span>. Aperte <b>Cmd+A</b> (no Windows, <b>Ctrl+A</b>) para selecionar o nome antigo e escreva o seu: <b>Estrelas da Noite</b> (ou o nome que você preferir).<br><br>Clique no botão azul <span class=ui>OK</span>.<br><br>É esse nome que aparece na página do jogo e na lista de jogos.",
    ck="O campo <span class=ui>Name</span> mostra o nome novo (e não mais <span class=ui>Copy of New Game</span>), antes de você apertar o <span class=ui>OK</span>.",
    sos=[("O nome ficou emendado no antigo","Faltou selecionar tudo antes de escrever. Aperte Cmd+A (ou Ctrl+A) no campo e escreva de novo."),
         ("Apertei Cancel","O nome volta a ser <span class=ui>Copy of New Game</span>. Abra o <span class=ui>Settings</span> de novo e escreva.")]),

  dict(n=9, titulo="Pinte um céu NOVO", img="aula12/p08_ceu.jpg",
    clipe=[("Abrir os níveis", "abrir_niveis.gif"), ("Pintar o céu", "pintar_o_ceu.gif")],
    corpo="Clique em <span class=ui>Game Levels</span>, na barra de baixo. No campo da cor (o que mostra <span class=ui>1B2A4A</span>), apague, escreva <b>2B1055</b> e aperte Enter.<br><br>Um <b>roxo</b> de noite. Escolha a cor que quiser: são seis letras e números (de 0 a F).",
    ck="A folha ficou <b>roxa</b>.",
    sos=[("Digitei e não mudou","Aperte Enter depois da cor."),
         ("Quero outra cor","Escreva outras seis letras e números no mesmo campo. Se o céu ficar branco, a estrela deixa de brilhar: o brilho é uma <b>soma</b> de cores (Aula 11).")]),

  dict(n=10, titulo="Troque o JOGADOR: o desenho", img="aula12/p09_grade.jpg",
    corpo="Clique no <b>boneco</b> e, no painel dele, no quadrado <span class=ui>edit sprite</span>, à esquerda.<br><br>Se não aparecer a grade de bonecos à direita, clique em <span class=ui>Browse</span>, depois em <span class=ui>Flowlab Sprites</span> e na faixa azul <span class=ui>Characters</span>.<br><br>A grade tem uma fileira de cada personagem: cada linha é um boneco diferente (as figuras da linha são variações do mesmo personagem).",
    ck="À direita aparece a grade de personagens, com os bonecos, os cachorros, os morcegos…",
    sos=[("Não acho o Browse","Ele fica embaixo da paleta de cores, na coluna da direita."),
         ("Apareceu o botão azul < Menu","Ele serve para <b>voltar</b> aos pacotes. Se você já está na grade de personagens, não precisa dele.")]),

  dict(n=11, titulo="Escolha OUTRO boneco", img="aula12/p10_jogador.jpg", clipe="escolher_sprite.gif",
    corpo="Na grade, clique no <b>segundo boneco de cima para baixo</b>, na primeira coluna (uma menina de roupa rosa e verde). Feche no <span class=ui>OK</span>, no canto de baixo à esquerda, e feche também o painel do boneco.<br><br>O boneco novo entra no lugar do antigo. <b>Nenhum bloco muda</b>: eles ficam no <b>objeto</b>, e só o desenho trocou.",
    ck="O boneco da folha roxa é <b>outro</b> (uma menina de roupa rosa e verde) e o quadrado <span class=ui>edit sprite</span> mostra o desenho novo.",
    sos=[("Troquei por um cachorro","Sem problema: ele corre igual. Se quiser o boneco, abra o <span class=ui>edit sprite</span> de novo e clique no segundo da primeira coluna."),
         ("O boneco ficou do tamanho errado","Todos os da grade têm o mesmo tamanho. Confira se você apertou o <span class=ui>OK</span>.")]),

  dict(n=12, titulo="Prepare MAIS ESTRELAS", img="aula12/p11_menu_da_estrela.jpg",
    corpo="Clique na <b>estrela</b>. Abre a roda do objeto, com <span class=ui>Clone</span>, <span class=ui>Edit</span>, <span class=ui>Delete</span> e <span class=ui>Cancel</span>. (Cuidado: <span class=ui>Delete</span> apaga o objeto.)<br><br>A estrela é um <b>tipo</b>, e os blocos dela (girar, brilhar, fazer barulho, sumir quando o boneco encosta) pertencem ao tipo. Cada estrela nova que você clonar <b>já nasce sabendo tudo isso</b>.",
    ck="Apareceu a roda do objeto com <span class=ui>Clone</span>, <span class=ui>Edit</span>, <span class=ui>Delete</span> e <span class=ui>Cancel</span>.",
    sos=[("Abriu o painel do objeto, e não a roda","Feche o painel e clique na estrela de novo, uma vez só."),
         ("Cliquei no chão","Clique <b>em cima</b> da estrela, na ponta direita da fileira.")]),

  dict(n=13, titulo="CLONE a estrela", img="aula12/p12_estrelas.jpg", clipe="clonar_a_estrela.gif",
    corpo="Clique em <span class=ui>Clone</span> e, depois, clique em <b>três casas vazias</b> da mesma fileira, à esquerda da estrela: a <b>sexta</b>, a <b>nona</b> e a <b>décima segunda</b> casa, contando da esquerda (a estrela está na 14ª). Termine em <span class=ui>done cloning</span>.<br><br>Fica com <b>quatro estrelas</b> em cima do chão.",
    ck="Quatro estrelas estão em cima do chão, espaçadas.",
    sos=[("Clonei em cima de outra casa","Aperte <span class=ui>Undo</span> ou clique na estrela repetida e use <span class=ui>Delete</span> (só nessa estrela)."),
         ("Esqueci o done cloning","Clique em <span class=ui>done cloning</span>, no alto, para sair do modo de clonar. Se não sair, as próximas cliques viram estrelas.")]),

  dict(n=14, titulo="JOGUE o seu jogo", img="aula12/p13_jogo.jpg", clipe="jogar.gif",
    corpo="Clique em <span class=ui>Play</span>.<br><br>Olhe: o <b>nome</b> do jogo aparece embaixo da tela, o céu é <b>roxo</b>, o boneco é o novo e as <b>quatro estrelas</b> giram e brilham.",
    ck="A página do jogo mostra <b>Estrelas da Noite</b> (ou o seu nome), a noite roxa, o boneco novo e quatro estrelas.",
    sos=[("O nome ainda é Copy of New Game","Volte ao editor (aperte <span class=ui>Esc</span>), abra o <span class=ui>Settings</span> e escreva o nome. Aperte o <span class=ui>OK</span> no fim."),
         ("O jogo abre sem as estrelas novas","Confira se você terminou o <span class=ui>done cloning</span>.")]),

  dict(n=15, titulo="Pegue as estrelas", img="aula12/p14_prova.jpg",
    corpo="Clique dentro da tela do jogo (para o teclado valer), <b>corra</b> com a seta para a direita e <b>pule</b> com a seta para cima.<br><br>Quando o boneco encosta numa estrela, ela <b>some</b> e faz o barulho de moeda. Pegar as quatro é o desafio: se pular na hora errada, o boneco passa por cima da estrela.",
    ck="Pelo menos <b>duas</b> estrelas sumiram quando o boneco encostou.",
    sos=[("O boneco não anda","Clique dentro da tela do jogo antes de apertar as setas."),
         ("O boneco passa direto pelas estrelas","Ele pulou alto demais. Corra <b>sem pular</b> perto de cada estrela."),
         ("O boneco saiu da fase","Ele passou do fim do chão. Aperte <span class=ui>Esc</span> para voltar ao editor e jogue de novo.")]),

  dict(n=16, titulo="Veja o jogo com o NOME na lista", img="aula12/p15_lista_nome.jpg",
    corpo="Volte para <span class=ui>My Games</span> (no alto da página). O primeiro cartão agora tem o <b>seu nome</b> no lugar de <span class=ui>Copy of New Game</span>.",
    ck="O primeiro cartão mostra <b>Estrelas da Noite</b> (ou o nome que você escolheu).",
    sos=[("O cartão ainda diz Copy of New Game","Aperte <b>F5</b> para recarregar a lista. Se continuar, o <span class=ui>OK</span> do <span class=ui>Settings</span> não foi apertado: volte ao editor e refaça o passo 8.")]),

  dict(n=17, titulo="Abra o COMPARTILHAR", img="aula12/p16_share.jpg",
    corpo="No primeiro cartão, clique no <b>botão redondo com a seta para cima</b>, embaixo à esquerda (o primeiro de dois botões redondos).<br><br>Abre a janela <span class=ui>Share</span>, com três partes: <span class=ui>Share Game Link</span> (o endereço do jogo), <span class=ui>Game Embed Code</span> (para colocar o jogo numa página da internet) e <span class=ui>Download Game HTML File</span>.<br><br>O que você usa hoje é o <b>link</b>.",
    ck="A janela <span class=ui>Share</span> está aberta e mostra um endereço que termina com o <b>número do seu jogo</b>.",
    sos=[("Abriu o gráfico em vez do compartilhar","Você clicou no segundo botão redondo (o gráfico). O compartilhar é o <b>primeiro</b>, o da seta para cima."),
         ("O número do link é do jogo antigo","Você abriu o compartilhar do cartão errado. Feche no <span class=ui>OK</span> e confira qual cartão tem o seu nome.")]),

  dict(n=18, titulo="COPIE o link", img="aula12/p17_copiado.jpg", clipe="copiar_o_link.gif",
    corpo="Clique em <span class=ui>Copy Link</span>, ao lado do endereço. O endereço fica <b>selecionado em azul</b> e o link é <b>copiado</b> — como se você tivesse apertado Cmd+C (ou Ctrl+C).<br><br>Agora é só <b>colar</b> (Cmd+V, ou Ctrl+V) numa mensagem: no WhatsApp do professor, no e-mail, onde o professor e a sua família combinarem.<br><br>Feche a janela no <span class=ui>OK</span>.",
    ck="O link foi copiado: ao colar (Cmd+V ou Ctrl+V) numa mensagem, aparece <b>https://flowlab.io/game/play/</b> e o número do seu jogo.",
    sos=[("Colei e apareceu outra coisa","Você copiou outra coisa depois. Volte e clique em <span class=ui>Copy Link</span> de novo."),
         ("Não achei o Copy Link","É o botão ao lado direito do endereço, na primeira parte da janela.")]),

  dict(n=19, titulo="ABRA o link e mostre", img="aula12/p18_link.jpg",
    corpo="Abra uma <b>aba nova</b> do navegador, cole o link na barra de cima e aperte Enter.<br><br>Abre a página do jogo, com o <b>nome</b> e o botão de jogar. É o que a sua família vai ver.<br><br>Mostre o seu jogo, e conte o que foi mais difícil e o que foi mais divertido de fazer.",
    ck="A aba nova mostra a página do jogo, com o nome <b>Estrelas da Noite</b> (ou o seu).",
    sos=[("Abriu a página do Flowlab, mas sem o jogo","Confira se você colou o endereço <b>inteiro</b>, até o último número."),
         ("O endereço não abre","Confira se ele começa com <b>https://flowlab.io/game/play/</b> e termina com o número do seu jogo.")]),
 ],
}
