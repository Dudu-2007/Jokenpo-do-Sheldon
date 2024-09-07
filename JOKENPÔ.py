import pygame
import sys
import random
import os
import time

# Inicialização do Pygame e do módulo de mixer (para sons)
pygame.init()
pygame.mixer.init()

# Configurações da tela
LARGURA_TELA, ALTURA_TELA = 800, 600
tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption("JOKENPÔ DO SHELDON")

# Definição de cores em formato RGB
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
VERDE = (34, 139, 34)
VERMELHO = (178, 34, 34)
AZUL = (0, 102, 204)
CINZA = (169, 169, 169)
FUNDO = (240, 248, 255)  # Alice Blue

# Criação de objetos de fonte para diferentes tamanhos de texto
fonte_grande = pygame.font.Font(None, 64)
fonte_media = pygame.font.Font(None, 48)
fonte_pequena = pygame.font.Font(None, 32)

# Lista de itens do jogo com seus respectivos pesos
itens = {
    "Papel": 1,
    "Tesoura": 2,
    "Pedra": 3,
    "Lagarto": 4,
    "Spock": 5
}

# Carregamento e redimensionamento das imagens dos itens
caminho_imagens = "imagens"
imagens = {}
for item in itens:
    imagens[item] = pygame.image.load(os.path.join(caminho_imagens, f"{item.lower()}.png"))
    imagens[item] = pygame.transform.scale(imagens[item], (120, 120))

# Carregamento das imagens de vitória e derrota
imagem_vitoria = pygame.image.load(os.path.join(caminho_imagens, "sheldon_feliz.png"))
imagem_derrota = pygame.image.load(os.path.join(caminho_imagens, "sheldon_decepcionado.png"))
imagem_vitoria = pygame.transform.scale(imagem_vitoria, (200, 200))
imagem_derrota = pygame.transform.scale(imagem_derrota, (200, 200))

# Carregamento dos efeitos sonoros
som_vitoria = pygame.mixer.Sound("sons/vitoria.wav")
som_derrota = pygame.mixer.Sound("sons/derrota.wav")
som_empate = pygame.mixer.Sound("sons/empate.wav")
som_clique = pygame.mixer.Sound("sons/clique.wav")

# Ajuste do volume dos efeitos sonoros
som_vitoria.set_volume(0.8)
som_derrota.set_volume(2)
som_empate.set_volume(0.5)
som_clique.set_volume(1.23)

# Carregamento e configuração da música de fundo
pygame.mixer.music.load("sons/musica_fundo.mp3")
pygame.mixer.music.set_volume(0.19)

# Criação de um canal de som único para evitar sobreposição de efeitos sonoros
canal_som = pygame.mixer.Channel(0)

# Variáveis globais para controle da pontuação
pontos_usuario = 0
pontos_computador = 0

def tocar_som(som):
    """Função para tocar um efeito sonoro"""
    canal_som.stop()
    canal_som.play(som)

def exibir_texto(texto, fonte, cor, x, y, alinhamento='centro'):
    """Função para exibir texto na tela com alinhamento especificado"""
    texto_renderizado = fonte.render(texto, True, cor)
    if alinhamento == 'esquerda':
        texto_rect = texto_renderizado.get_rect(midleft=(x, y))
    elif alinhamento == 'direita':
        texto_rect = texto_renderizado.get_rect(midright=(x, y))
    else:
        texto_rect = texto_renderizado.get_rect(center=(x, y))
    tela.blit(texto_renderizado, texto_rect)

def desenhar_botao(texto, x, y, largura, altura, cor_inativa, cor_ativa):
    """Função para desenhar e gerenciar botões interativos"""
    mouse = pygame.mouse.get_pos()
    clique = pygame.mouse.get_pressed()[0]
    
    if x < mouse[0] < x + largura and y < mouse[1] < y + altura:
        pygame.draw.rect(tela, cor_ativa, (x, y, largura, altura), border_radius=15)
        if clique:
            som_clique.play()
            return True
    else:
        pygame.draw.rect(tela, cor_inativa, (x, y, largura, altura), border_radius=15)
    
    exibir_texto(texto, fonte_pequena, BRANCO, x + largura/2, y + altura/2)
    return False

def atualizar_pontuacao(escolha_jogador, escolha_computador, resultado):
    """Função para atualizar a pontuação com base no resultado da jogada e nos pesos"""
    global pontos_usuario, pontos_computador
    if resultado == "Você venceu!":
        pontos_usuario += itens[escolha_jogador]
        pontos_computador -= itens[escolha_computador]
    elif resultado == "Computador venceu!":
        pontos_computador += itens[escolha_computador]
        pontos_usuario -= itens[escolha_jogador]
    
    pontos_usuario = max(0, pontos_usuario)  # Evita pontuação negativa
    pontos_computador = max(0, pontos_computador)  # Evita pontuação negativa

def escolher_jogada(escolha_jogador):
    """Função para determinar o resultado da jogada"""
    escolha_computador = random.choice(list(itens.keys()))
    
    if escolha_jogador == escolha_computador:
        return escolha_computador, "Empate!"
    elif (
        (escolha_jogador == "Pedra" and escolha_computador in ["Tesoura", "Lagarto"]) or
        (escolha_jogador == "Papel" and escolha_computador in ["Pedra", "Spock"]) or
        (escolha_jogador == "Tesoura" and escolha_computador in ["Papel", "Lagarto"]) or
        (escolha_jogador == "Lagarto" and escolha_computador in ["Papel", "Spock"]) or
        (escolha_jogador == "Spock" and escolha_computador in ["Pedra", "Tesoura"])
    ):
        return escolha_computador, "Você venceu!"
    else:
        return escolha_computador, "Computador venceu!"


def jogar():
    """Função principal do jogo"""
    global pontos_usuario, pontos_computador
    escolha_jogador = None
    escolha_computador = None
    resultado = None
    mostrando_resultado = False
    tempo_espera = 0
    pontuacao_atualizada = False
    jogada_numero = 1  # Contador para as jogadas

    # Abre o arquivo para registrar as jogadas em modo de escrita (limpa o conteúdo anterior)
    with open("jogadas.txt", "w") as arquivo:
        while True:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            tela.fill(FUNDO)
            
            exibir_texto("JOKENPÔ DO SHELDON", fonte_grande, AZUL, LARGURA_TELA/2, 50)
            exibir_texto(f"Você: {pontos_usuario}", fonte_media, VERDE, 150, 120, 'esquerda')
            exibir_texto(f"Computador: {pontos_computador}", fonte_media, VERMELHO, LARGURA_TELA - 150, 120, 'direita')
            
            if escolha_jogador:
                exibir_texto("Sua escolha:", fonte_pequena, PRETO, LARGURA_TELA/4, 200)
                tela.blit(imagens[escolha_jogador], (LARGURA_TELA/4 - 60, 230))
                
                if escolha_computador and time.time() - tempo_espera > 1:
                    exibir_texto("Escolha do computador:", fonte_pequena, PRETO, 3*LARGURA_TELA/4, 200)
                    tela.blit(imagens[escolha_computador], (3*LARGURA_TELA/4 - 60, 230))
                
                if resultado and time.time() - tempo_espera > 2:
                    exibir_texto(resultado, fonte_media, VERMELHO if "Computador" in resultado else VERDE, LARGURA_TELA/2, 420)
                    if not mostrando_resultado:
                        mostrando_resultado = True
                        if resultado == "Voce venceu!":
                            tocar_som(som_vitoria)
                        elif resultado == "Computador venceu!":
                            tocar_som(som_derrota)
                        else:
                            tocar_som(som_empate)
                    if not pontuacao_atualizada and time.time() - tempo_espera > 3:
                        atualizar_pontuacao(escolha_jogador, escolha_computador, resultado)
                        pontuacao_atualizada = True
                        # Salva a jogada no arquivo com a pontuação em tempo real
                        arquivo.write(f"Jogada {jogada_numero}: {escolha_jogador} vs {escolha_computador} - {resultado} | Pontos: Voce {pontos_usuario}, Computador {pontos_computador}\n")
                        jogada_numero += 1  # Incrementa o número da jogada
            
            for i, item in enumerate(itens):
                if desenhar_botao(item, 50 + i*150, 500, 140, 50, VERDE, AZUL) and not escolha_jogador:
                    escolha_jogador = item
                    escolha_computador, resultado = escolher_jogada(escolha_jogador)
                    tempo_espera = time.time()
                    mostrando_resultado = False
                    pontuacao_atualizada = False
            
            if desenhar_botao("Menu", 20, 20, 80, 30, AZUL, (100, 150, 255)):
                return
            
            if mostrando_resultado and time.time() - tempo_espera > 4:
                if pontos_usuario >= 10 or pontos_computador >= 10:
                    mostrar_resultado_final()
                    zerar_pontos()  # Zera o placar após o resultado final
                    return
                escolha_jogador = None
                escolha_computador = None
                resultado = None
                mostrando_resultado = False
            
            pygame.display.flip()
            pygame.time.delay(50)  # Adiciona um pequeno atraso para controlar a taxa de atualização

def mostrar_resultado_final():
    """Função para mostrar o resultado final do jogo"""
    tela.fill(FUNDO)
    if pontos_usuario >= 10:
        tela.blit(imagem_vitoria, (LARGURA_TELA/2 - 100, 100))
        exibir_texto("Parabéns, você ganhou!", fonte_grande, VERDE, LARGURA_TELA/2, 350)
    else:
        tela.blit(imagem_derrota, (LARGURA_TELA/2 - 100, 100))
        exibir_texto("Decepcionante... Você perdeu!", fonte_grande, VERMELHO, LARGURA_TELA/2, 350)
    
    pygame.display.flip()
    time.sleep(5)  # Mostra a tela de resultado por 5 segundos

def regras():
    """Função para exibir as regras do jogo"""
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        tela.fill(FUNDO)
        exibir_texto("REGRAS", fonte_grande, AZUL, LARGURA_TELA/2, 50)
        
        regras_texto = [
            "Pedra vence Tesoura e Lagarto",
            "Papel vence Pedra e Spock",
            "Tesoura vence Papel e Lagarto",
            "Lagarto vence Papel e Spock",
            "Spock vence Pedra e Tesoura",
            "",
            "Pesos dos itens:",
            "Papel: 1, Tesoura: 2, Pedra: 3, Lagarto: 4, Spock: 5",
            "",
            "Ao vencer, você ganha pontos iguais ao peso do seu item",
            "e o oponente perde pontos iguais ao peso do item dele.",
            "",
            "O jogo termina quando um jogador atinge 10 pontos.",
        ]
        
        for i, regra in enumerate(regras_texto):
            exibir_texto(regra, fonte_pequena, PRETO, LARGURA_TELA/2, 120 + i*30)
        
        if desenhar_botao("Menu", 20, 20, 80, 30, AZUL, (100, 150, 255)):
            return
        
        pygame.display.flip()

def referencias():
    """Função para exibir as referências do jogo"""
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        tela.fill(FUNDO)
        exibir_texto("REFERÊNCIAS", fonte_grande, AZUL, LARGURA_TELA/2, 50)
        
        referencias_texto = [
            "Este jogo é baseado na versão de Pedra, Papel,",
            "Tesoura, Lagarto, Spock criada por Sam Kass e",
            "Karen Bryla, popularizada por Sheldon Cooper",
            "na série de TV 'The Big Bang Theory'.",
            "",
            "Desenvolvido por: Eduardo Vinícius e Lucas Fernando",
        ]
        
        for i, referencia in enumerate(referencias_texto):
            exibir_texto(referencia, fonte_pequena, PRETO, LARGURA_TELA/2, 150 + i*35)
        
        if desenhar_botao("Menu", 20, 20, 80, 30, AZUL, (100, 150, 255)):
            return
        
        pygame.display.flip()

def zerar_pontos():
    """Função para zerar a pontuação"""
    global pontos_usuario, pontos_computador
    pontos_usuario = 0
    pontos_computador = 0
    print("Placar zerado!")


def menu_principal():
    """Função do menu principal"""
    pygame.mixer.music.play(-1)  # Inicia a música de fundo em loop
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        tela.fill(FUNDO)
        exibir_texto("JOKENPÔ DO SHELDON", fonte_grande, AZUL, LARGURA_TELA/2, 100)
        
        largura_botao = 300
        altura_botao = 70
        
        if desenhar_botao("Jogar", LARGURA_TELA/2 - largura_botao/2, 200, largura_botao, altura_botao, VERDE, (0, 180, 0)):
            jogar()
        if desenhar_botao("Regras", LARGURA_TELA/2 - largura_botao/2, 300, largura_botao, altura_botao, AZUL, (0, 150, 255)):
            regras()
        if desenhar_botao("Referências", LARGURA_TELA/2 - largura_botao/2, 400, largura_botao, altura_botao, AZUL, (0, 150, 255)):
            referencias()
        if desenhar_botao("Zerar Placar", LARGURA_TELA/2 - largura_botao/2, 500, largura_botao, altura_botao, VERMELHO, (255, 50, 50)):
            zerar_pontos()
        if desenhar_botao("Sair", LARGURA_TELA/2 - largura_botao/2, 600, largura_botao, altura_botao, CINZA, (100, 100, 100)):
            pygame.quit()
            sys.exit()
        
        exibir_texto(f"Você: {pontos_usuario}", fonte_media, VERDE, 150, 30, 'esquerda')
        exibir_texto(f"Computador: {pontos_computador}", fonte_media, VERMELHO, LARGURA_TELA - 150, 30, 'direita')
        

        pygame.display.flip()
        
        

# Ponto de entrada do programa
if __name__ == "__main__":
    menu_principal()  # Inicia o jogo chamando o menu principal