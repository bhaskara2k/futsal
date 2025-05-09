# src/main_game_loop.py

import pygame
from src import config  # Importando nossas configurações
import math  # Para cálculos matemáticos, como ângulos e distância
from src.entities.ball import Bola # << IMPORTAR A NOSSA BOLA
import random # Já estávamos usando para o chute aleatório da bola
from src.entities.player import Player # << IMPORTAR O JOGADOR

def desenhar_quadra(tela):
    """
    Função placeholder para desenhar a quadra.
    Vamos implementá-la em breve.
    """
    # Por enquanto, apenas um fundo para sabermos que está funcionando
    # A cor da quadra será definida dentro desta função quando a implementarmos.
    pass

def rodar_jogo():

    pygame.init()
    tela = pygame.display.set_mode((config.LARGURA_TELA, config.ALTURA_TELA))
    pygame.display.set_caption(config.TITULO_JANELA)
    relogio = pygame.time.Clock()

    quadra_rect_jogavel = pygame.Rect(
        config.MARGEM_QUADRA + config.ESPESSURA_LINHA,
        config.MARGEM_QUADRA + config.ESPESSURA_LINHA,
        config.LARGURA_TELA - 2 * (config.MARGEM_QUADRA + config.ESPESSURA_LINHA),
        config.ALTURA_TELA - 2 * (config.MARGEM_QUADRA + config.ESPESSURA_LINHA)
    )

    raio_bola_cfg = 10
    cor_bola_cfg = config.BRANCO # Ou uma cor específica para a bola
    bola = Bola(
        x = config.LARGURA_TELA / 2,
        y = config.ALTURA_TELA / 2,
        raio = raio_bola_cfg,
        cor = cor_bola_cfg
    )
    
    # Criar um jogador de teste
    raio_jogador_cfg = 15
    cor_jogador_time_a_cfg = (0, 0, 255) # Azul para time A
    cor_jogador_time_b_cfg = (255, 0, 0) # Vermelho para time B

    jogador1 = Player(
        x = config.LARGURA_TELA * 0.25, # Posição inicial no campo de ataque esquerdo
        y = config.ALTURA_TELA / 2,
        raio = raio_jogador_cfg,
        cor = cor_jogador_time_a_cfg,
        time = "A"
    )

    jogador2 = Player( # Um segundo jogador para teste, do outro time
        x = config.LARGURA_TELA * 0.75, # Posição inicial no campo de ataque direito
        y = config.ALTURA_TELA / 2,
        raio = raio_jogador_cfg,
        cor = cor_jogador_time_b_cfg,
        time = "B"
    )

    lista_jogadores = [jogador1, jogador2] # Uma lista para facilitar o gerenciamento

    # Para teste inicial, vamos dar um chute na bola
    bola.chutar(5, 3) # Chuta com velocidade (5, 3) pixels/frame
    tempo_bola_parada = 0
    TEMPO_MAX_PARADA_DEBUG = 120 # 2 segundos a 60 FPS

    rodando = True
    while rodando:
        jogador1_vx, jogador1_vy = 0, 0
        acao_chute_jogador1 = False

        # --- Tratamento de Eventos ---
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            if evento.type == pygame.KEYDOWN: # Evento de tecla pressionada UMA VEZ
                if evento.key == pygame.K_SPACE: # Tecla de Espaço para chutar
                    acao_chute_jogador1 = True
            
        # --- Input do Teclado (para controlar jogador1) ---
        teclas = pygame.key.get_pressed() # Pega o estado de todas as teclas
        if teclas[pygame.K_LEFT]:
            jogador1_vx = -jogador1.velocidade_max
        if teclas[pygame.K_RIGHT]:
            jogador1_vx = jogador1.velocidade_max
        if teclas[pygame.K_UP]:
            jogador1_vy = -jogador1.velocidade_max
        if teclas[pygame.K_DOWN]:
            jogador1_vy = jogador1.velocidade_max
        
        # Definir a velocidade do jogador1 com base no input
        jogador1.set_velocidade(jogador1_vx, jogador1_vy)

        # --- Lógica do Jogo ---
        for jogador_atualizar in lista_jogadores:
            jogador_atualizar.atualizar_posicao(quadra_rect_jogavel)

        # Interação Jogador-Bola
        if not bola.controlada_por_jogador: # Se a bola está livre
            for jogador_interagir in lista_jogadores:
                if jogador_interagir.verificar_pegar_bola(bola):
                    break # Só um jogador pega a bola por vez
        
        # Ação de Chute do Jogador 1 (controlado manualmente)
        if acao_chute_jogador1 and jogador1.tem_bola:
            jogador1.chutar_bola(bola) # Passamos a referência da bola para o jogador chutar

        # Lógica da bola (mover se não controlada, ou se controlada, sua posição é atualizada em ser_controlada/mover)
        status_bola = None
        if not bola.controlada_por_jogador and bola.esta_em_jogo:
            status_bola = bola.mover(quadra_rect_jogavel)
        elif bola.controlada_por_jogador: # Se controlada, atualiza sua posição para seguir o jogador
            bola.mover(quadra_rect_jogavel) # O mover da bola agora sabe lidar com isso

        if status_bola: # Se a bola saiu (e não estava controlada)
            tempo_bola_parada = 0
        elif not bola.esta_em_jogo and not bola.controlada_por_jogador: # Bola saiu e não foi resetada ainda
            tempo_bola_parada += 1
            if tempo_bola_parada > TEMPO_MAX_PARADA_DEBUG:
                bola.resetar_para_jogo(config.LARGURA_TELA / 2, config.ALTURA_TELA / 2)
                # bola.chutar(random.choice([-5, 5]), random.choice([-3, 3])) # Não chuta mais automaticamente ao resetar
                tempo_bola_parada = 0

        # --- Desenho na Tela ---
        tela.fill(config.AZUL_QUADRA)  # Preenche a tela com a cor da quadra
        desenhar_quadra(tela) # Chamaremos nossa função para desenhar as linhas aqui

        for jogador in lista_jogadores: # Desenhar cada jogador
            jogador.desenhar(tela)

        bola.desenhar(tela) 

        pygame.display.flip()  # Atualiza o conteúdo da tela inteira

        # --- Controle de FPS ---
        relogio.tick(config.FPS)

    pygame.quit()
    # sys.exit() # Descomente se precisar garantir que o programa feche em todas as plataformas

def desenhar_quadra(tela):
    """
    Desenha todas as linhas e marcações da quadra de futsal.
    """
    # Cores e espessura das linhas vêm do config
    cor_linha = config.COR_LINHA
    espessura_linha = config.ESPESSURA_LINHA
    cor_gol = config.COR_GOL

    # Dimensões da área de jogo (considerando as margens)
    # A quadra será desenhada DENTRO dessas margens
    quadra_x = config.MARGEM_QUADRA
    quadra_y = config.MARGEM_QUADRA
    quadra_largura = config.LARGURA_TELA - (2 * config.MARGEM_QUADRA)
    quadra_altura = config.ALTURA_TELA - (2 * config.MARGEM_QUADRA)

    # 1. Linhas Limítrofes (Retângulo externo da quadra)
    pygame.draw.rect(tela, cor_linha, (quadra_x, quadra_y, quadra_largura, quadra_altura), espessura_linha)

    # 2. Linha de Meio da Quadra
    meio_x = config.LARGURA_TELA / 2
    pygame.draw.line(tela, cor_linha, (meio_x, quadra_y), (meio_x, quadra_y + quadra_altura), espessura_linha)

    # 3. Círculo Central
    raio_circulo_central = quadra_altura * 0.15 # Exemplo: 15% da altura da quadra
    if raio_circulo_central < 1 : raio_circulo_central = 1 # Garantir que o raio seja pelo menos 1 se a quadra for muito pequena
    pygame.draw.circle(tela, cor_linha, (int(meio_x), int(quadra_y + quadra_altura / 2)), int(raio_circulo_central), espessura_linha)

    # --- Gols e Áreas Penais (para cada lado) ---
    largura_gol = quadra_altura * 0.20 # Exemplo: 20% da altura da quadra para a largura do gol
    altura_gol = largura_gol / 2.5     # Proporção típica de gol de futsal (ex: 3m x 2m, mas aqui é visual)
    raio_area_penal = quadra_altura * 0.25 # Raio para os arcos da área penal (6 metros na realidade)

    # Lado Esquerdo
    gol_esq_x = quadra_x
    gol_esq_y = (config.ALTURA_TELA / 2) - (largura_gol / 2)
    pygame.draw.rect(tela, cor_gol, (gol_esq_x - altura_gol, gol_esq_y, altura_gol, largura_gol)) # Gol para fora da linha
    # Arcos da área penal esquerda (desenhando dois arcos para formar o semicírculo)
    # Ponto central para os arcos da área é o meio do gol, na linha de fundo
    centro_area_esq_x = quadra_x
    centro_area_esq_y = config.ALTURA_TELA / 2
    # Retângulo que define o limite dos arcos
    rect_area_esq = pygame.Rect(centro_area_esq_x - raio_area_penal,
                                centro_area_esq_y - raio_area_penal,
                                2 * raio_area_penal,
                                2 * raio_area_penal)
    pygame.draw.arc(tela, cor_linha, rect_area_esq, -math.pi/2, math.pi/2, espessura_linha) # Arco de -90 a 90 graus

    # Lado Direito
    gol_dir_x = quadra_x + quadra_largura
    gol_dir_y = (config.ALTURA_TELA / 2) - (largura_gol / 2)
    pygame.draw.rect(tela, cor_gol, (gol_dir_x, gol_dir_y, altura_gol, largura_gol)) # Gol para fora da linha
    # Arcos da área penal direita
    centro_area_dir_x = quadra_x + quadra_largura
    centro_area_dir_y = config.ALTURA_TELA / 2
    rect_area_dir = pygame.Rect(centro_area_dir_x - raio_area_penal,
                                centro_area_dir_y - raio_area_penal,
                                2 * raio_area_penal,
                                2 * raio_area_penal)
    pygame.draw.arc(tela, cor_linha, rect_area_dir, math.pi/2, 3*math.pi/2, espessura_linha) # Arco de 90 a 270 graus

    # 5. Marcas de Pênalti (simplificado como um pequeno círculo ou X)
    # Distância de 6m (proporcional aqui)
    dist_penalti = raio_area_penal * (6.0 / (raio_area_penal / (quadra_altura * 0.25))) # Tentativa de manter proporção, pode simplificar
    if dist_penalti > quadra_largura / 2: dist_penalti = quadra_largura * 0.1 # Evitar que passe do meio
    pygame.draw.circle(tela, cor_linha, (int(quadra_x + dist_penalti), int(config.ALTURA_TELA / 2)), espessura_linha + 1, espessura_linha)
    pygame.draw.circle(tela, cor_linha, (int(quadra_x + quadra_largura - dist_penalti), int(config.ALTURA_TELA / 2)), espessura_linha + 1, espessura_linha)

    # Poderíamos adicionar mais detalhes como segunda marca de pênalti e arcos de canto
    # mas isso já nos dá uma quadra bem reconhecível.

# Para garantir que o jogo rode quando este arquivo é executado diretamente
# (será chamado pelo run_game.py, mas é bom para testes diretos)
if __name__ == '__main__':
    rodar_jogo()