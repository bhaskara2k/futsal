# src/entities/player.py
import pygame
from src import config

class Player:
    def __init__(self, x, y, raio, cor, time="A"):
        self.x = float(x)
        self.y = float(y)
        self.raio = int(raio)
        self.cor = cor
        self.time = time

        self.velocidade_x = 0.0 # Velocidade atual do jogador
        self.velocidade_y = 0.0
        self.velocidade_max = 3.0 # Velocidade de movimento quando uma tecla é pressionada

        self.tem_bola = False

        # self.orientacao_chute_x = 1 # Para onde o jogador está "olhando" para chutar (1=direita, -1=esquerda)
        # self.orientacao_chute_y = 0 # (0=reto, pode ser mais complexo com ângulos)
        # Por simplicidade inicial, o chute será sempre para frente na direção do movimento ou fixo

    def set_velocidade(self, vx, vy):
        """Define a velocidade do jogador (usado pelo input ou IA)."""
        self.velocidade_x = vx
        self.velocidade_y = vy

        # Atualizar orientação para o chute (simples)
        # if abs(vx) > 0.1 or abs(vy) > 0.1: # Se estiver se movendo
        #     # Normalizar para obter direção (mais complexo, por agora vamos simplificar)
        #     if abs(vx) > abs(vy):
        #         self.orientacao_chute_x = 1 if vx > 0 else -1
        #         self.orientacao_chute_y = 0
        #     else:
        #         self.orientacao_chute_y = 1 if vy > 0 else -1
        #         self.orientacao_chute_x = 0

    def atualizar_posicao(self, quadra_rect):
        """
        Atualiza a posição do jogador com base na sua velocidade atual
        e o mantém dentro dos limites da quadra jogável.
        """
        novo_x = self.x + self.velocidade_x
        novo_y = self.y + self.velocidade_y

        # Verificar colisão com os limites da quadra ANTES de mover
        # Colisão com a linha de fundo ESQUERDA
        if novo_x - self.raio < quadra_rect.left:
            novo_x = quadra_rect.left + self.raio
        # Colisão com a linha de fundo DIREITA
        elif novo_x + self.raio > quadra_rect.right:
            novo_x = quadra_rect.right - self.raio
        # Colisão com a linha lateral SUPERIOR
        if novo_y - self.raio < quadra_rect.top:
            novo_y = quadra_rect.top + self.raio
        # Colisão com a linha lateral INFERIOR
        elif novo_y + self.raio > quadra_rect.bottom:
            novo_y = quadra_rect.bottom - self.raio
        
        self.x = novo_x
        self.y = novo_y

        # Resetar velocidades após o movimento para que ele pare se nenhuma tecla estiver pressionada
        # (Este comportamento pode mudar quando a IA controlar)
        # self.velocidade_x = 0 # Para input por tecla, pode ser melhor resetar no loop de eventos
        # self.velocidade_y = 0

    def verificar_pegar_bola(self, bola):
        """Verifica se o jogador colide com a bola e pega a posse."""
        if not self.tem_bola and bola.esta_em_jogo:
            dist_x = self.x - bola.x
            dist_y = self.y - bola.y
            distancia = (dist_x**2 + dist_y**2)**0.5 # Distância Euclidiana
            if distancia < self.raio + bola.raio:
                self.tem_bola = True
                bola.ser_controlada(self) # Informa à bola quem a está controlando
                print(f"Jogador {self.time} pegou a bola!") # DEBUG
                return True
        return False

    def chutar_bola(self, bola_ref, forca_chute=10.0):
        """Jogador chuta a bola."""
        if self.tem_bola:
            self.tem_bola = False
            bola_ref.deixar_ser_controlada() # Libera a bola

            # Direção do chute (simples: para frente do gol adversário)
            # Time A chuta para a direita, Time B para a esquerda
            direcao_chute_x = 1 if self.time == "A" else -1
            # Poderíamos adicionar uma pequena variação aleatória ou baseada na última mov. do jogador
            
            bola_ref.chutar(direcao_chute_x * forca_chute, 0) # Chute reto
            print(f"Jogador {self.time} chutou a bola!") # DEBUG

    def desenhar(self, tela):
        pygame.draw.circle(tela, self.cor, (int(self.x), int(self.y)), self.raio)
        if self.time == "B":
            pygame.draw.circle(tela, config.PRETO, (int(self.x), int(self.y)), self.raio // 2)