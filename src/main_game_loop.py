# src/main_game_loop.py

import pygame
from src import config  # Importando nossas configurações
import math  # Para cálculos matemáticos, como ângulos e distância
from src.entities.ball import Bola # << IMPORTAR A NOSSA BOLA
import random # Já estávamos usando para o chute aleatório da bola
from src.entities.player import Player # << IMPORTAR O JOGADOR
from src.game_core.game_manager import GameManager # << IMPORTAR

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


def rodar_jogo():
    pygame.init()
    pygame.font.init() # Inicializa o módulo de fontes

    tela = pygame.display.set_mode((config.LARGURA_TELA, config.ALTURA_TELA))
    pygame.display.set_caption(config.TITULO_JANELA)
    relogio = pygame.time.Clock()

    # Definição da área jogável interna da quadra
    quadra_rect_jogavel = pygame.Rect(
        config.MARGEM_QUADRA + config.ESPESSURA_LINHA,
        config.MARGEM_QUADRA + config.ESPESSURA_LINHA,
        config.LARGURA_TELA - 2 * (config.MARGEM_QUADRA + config.ESPESSURA_LINHA),
        config.ALTURA_TELA - 2 * (config.MARGEM_QUADRA + config.ESPESSURA_LINHA)
    )

    # Coordenadas Y da "boca do gol" para detecção de gol
    # (Usando a altura interna da quadra para calcular a altura da boca do gol)
    altura_interna_quadra_para_gol = config.ALTURA_TELA - 2 * config.MARGEM_QUADRA
    altura_boca_gol_logica = altura_interna_quadra_para_gol * 0.20
    
    gol_post_superior_y = (config.ALTURA_TELA / 2) - (altura_boca_gol_logica / 2)
    gol_post_inferior_y = gol_post_superior_y + altura_boca_gol_logica

    # Criação da Bola
    raio_bola_cfg = 10 # Pode vir de config.py
    cor_bola_cfg = config.BRANCO # Pode vir de config.py
    bola = Bola(config.LARGURA_TELA / 2, config.ALTURA_TELA / 2, raio_bola_cfg, cor_bola_cfg)
    
    # Criação dos Jogadores e suas posições iniciais
    raio_jogador_cfg = 15 # Pode vir de config.py
    cor_jogador_time_a_cfg = (0, 0, 255) # Time A - Azul
    cor_jogador_time_b_cfg = (255, 0, 0) # Time B - Vermelho

    pos_inicial_j1 = (config.LARGURA_TELA * 0.35, config.ALTURA_TELA / 2) # Um pouco mais perto do centro
    pos_inicial_j2 = (config.LARGURA_TELA * 0.65, config.ALTURA_TELA / 2) # Um pouco mais perto do centro

    jogador1 = Player(pos_inicial_j1[0], pos_inicial_j1[1], raio_jogador_cfg, cor_jogador_time_a_cfg, "A", controlado_por_ia=True)
    jogador2 = Player(pos_inicial_j2[0], pos_inicial_j2[1], raio_jogador_cfg, cor_jogador_time_b_cfg, "B", controlado_por_ia=True)
    lista_jogadores = [jogador1, jogador2]

    posicoes_iniciais_para_gm = {
        jogador1: pos_inicial_j1,
        jogador2: pos_inicial_j2
    }

    # Instanciar o GameManager
    game_manager = GameManager(bola, lista_jogadores, posicoes_iniciais_para_gm)

    # Fonte para o placar
    try:
        fonte_placar = pygame.font.SysFont("arial", 28, bold=True)
    except pygame.error: # Fallback se a fonte não existir
        fonte_placar = pygame.font.Font(None, 36) # Fonte padrão do Pygame

    rodando = True
    while rodando:
        # --- Tratamento de Eventos ---
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            # (Aqui poderiam entrar eventos para pausar o jogo, etc., controlados pelo GameManager)

        # --- Atualizar Estado do GameManager ---
        game_manager.atualizar_estado() # Controla timers e transições de estado (ex: GOL_MARCADO -> PREPARANDO_SAQUE)

        # --- Lógica do Jogo (Só executa se o estado for "JOGANDO") ---
        if game_manager.obter_estado_jogo() == config.ESTADO_JOGANDO:
            # Atualizar IA e Posição dos Jogadores
            for jogador_atualizar in lista_jogadores:
                if jogador_atualizar.controlado_por_ia:
                    jogador_atualizar.atualizar_cerebro_ia(bola, quadra_rect_jogavel)
                jogador_atualizar.atualizar_posicao(quadra_rect_jogavel)

            # Interação Jogador-Bola (tentativa de pegar/roubar)
            if not bola.controlada_por_jogador: # Se a bola está livre
                for jogador_interagir in lista_jogadores:
                    if jogador_interagir.verificar_pegar_bola(bola):
                        break # Só um jogador pega a bola por vez
            
            # Movimentação da Bola
            status_bola = None # Para armazenar se saiu ou foi gol
            if bola.esta_em_jogo: # Se a bola está marcada como "em jogo"
                # O método mover da bola agora lida internamente se está controlada ou livre
                status_bola = bola.mover(quadra_rect_jogavel, gol_post_superior_y, gol_post_inferior_y)
            
            # Verificar Resultado do Movimento da Bola
            if status_bola: # Se 'mover' retornou algo (saiu ou foi gol)
                if "GOL_ESQUERDA" in status_bola: # Time B marcou
                    game_manager.registrar_gol("B")
                elif "GOL_DIREITA" in status_bola: # Time A marcou
                    game_manager.registrar_gol("A")
                elif "fundo" in status_bola or "lateral" in status_bola:
                    # Bola saiu por lateral/fundo (não foi gol)
                    # O GameManager precisaria de lógica para quem repõe e como.
                    # Por agora, o jogo vai "parar" pois o estado do GM não muda para JOGANDO
                    # até que algo (como um gol) chame preparar_saque_centro().
                    # Ou, para continuar o teste de IA, podemos forçar um reinício:
                    print(f"Bola saiu ({status_bola}). Próximo saque será preparado pelo GameManager em breve (após um gol).")
                    # Se quiser que o jogo continue para teste de IA mesmo com laterais/fundo:
                    # game_manager.quem_saca = "A" if "direita" in status_bola or "superior" in status_bola else "B" # Exemplo simples
                    # game_manager.preparar_saque_centro()


        # --- Desenho na Tela ---
        tela.fill(config.AZUL_QUADRA)
        desenhar_quadra(tela)

        for jogador_desenhar in lista_jogadores:
            jogador_desenhar.desenhar(tela)
        
        # Só desenha a bola se ela não estiver "invisível" (ex: após sair e antes de resetar)
        # A lógica atual de bola.esta_em_jogo e bola.controlada_por_jogador deve cuidar disso
        # Se GameManager.estado_jogo != GOL_MARCADO (para a bola sumir durante a "comemoração")
        if game_manager.obter_estado_jogo() != config.ESTADO_GOL_MARCADO or (game_manager.timer_estado_gol % 30 < 15) : # Pisca a bola no estado GOL
            bola.desenhar(tela)

        # Desenhar Placar
        placar_surface = fonte_placar.render(game_manager.obter_placar_formatado(), True, config.BRANCO)
        pos_placar_x = config.LARGURA_TELA / 2 - placar_surface.get_width() / 2
        tela.blit(placar_surface, (pos_placar_x, 10))

        # Desenhar Estado do Jogo (para debug)
        estado_surface = fonte_placar.render(f"Estado: {game_manager.obter_estado_jogo()}", True, config.BRANCO)
        pos_estado_x = config.LARGURA_TELA / 2 - estado_surface.get_width() / 2
        tela.blit(estado_surface, (pos_estado_x, 40))


        pygame.display.flip()
        relogio.tick(config.FPS)

    pygame.quit()



if __name__ == '__main__':
    rodar_jogo()