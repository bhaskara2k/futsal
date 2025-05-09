# src/entities/ball.py
import pygame
from src import config

class Bola:
    def __init__(self, x, y, raio, cor):
        self.x = float(x)
        self.y = float(y)
        self.raio = int(raio)
        self.cor = cor
        self.velocidade_x = 0.0
        self.velocidade_y = 0.0
        self.atrito = 0.99
        # self.elasticidade_quique = 0.6 # Não vamos mais usar para quique simples nas bordas
        self.esta_em_jogo = True # Novo atributo para controlar se a bola está jogável
        self.controlada_por_jogador = None # Novo: referência ao jogador que a controla

    def ser_controlada(self, jogador):
        """Define que a bola está sendo controlada por um jogador."""
        self.controlada_por_jogador = jogador
        self.esta_em_jogo = True # Garante que está em jogo ao ser controlada
        self.velocidade_x = 0
        self.velocidade_y = 0

    def deixar_ser_controlada(self):
        """Libera a bola do controle do jogador."""
        if self.controlada_por_jogador:
             # Posiciona a bola ligeiramente à frente do jogador ao ser solta/chutada
             # (Simples: na direção do gol adversário)
             offset_chute = self.controlada_por_jogador.raio + self.raio + 2 # Pequeno espaço
             direcao_x = 1 if self.controlada_por_jogador.time == "A" else -1
             self.x = self.controlada_por_jogador.x + (direcao_x * offset_chute)
             self.y = self.controlada_por_jogador.y # Mantém o Y do jogador
        self.controlada_por_jogador = None

    def mover(self, quadra_rect):

        if self.controlada_por_jogador:
            # Bola acompanha o jogador (ex: na frente dele)
            # Simples: um pouco à frente na direção do gol adversário
            offset_bola_x = self.controlada_por_jogador.raio + self.raio -2 # Quase colada
            direcao_x = 1 if self.controlada_por_jogador.time == "A" else -1
            
            self.x = self.controlada_por_jogador.x + (direcao_x * offset_bola_x)
            self.y = self.controlada_por_jogador.y # Bola acompanha o Y do jogador
            return None # Não verifica saída de campo enquanto controlada

        if not self.esta_em_jogo:
            self.velocidade_x = 0 # Garante que a bola parada não ganhe velocidade por atrito residual
            self.velocidade_y = 0
            return None # Não faz nada se a bola já está fora de jogo

        self.x += self.velocidade_x
        self.y += self.velocidade_y

        self.velocidade_x *= self.atrito
        self.velocidade_y *= self.atrito

        if abs(self.velocidade_x) < 0.1: self.velocidade_x = 0
        if abs(self.velocidade_y) < 0.1: self.velocidade_y = 0

        # Verificar qual limite foi atingido
        saiu_por = None

        saiu_por = None
        if self.x - self.raio <= quadra_rect.left:
            self.x = quadra_rect.left + self.raio
            self.velocidade_x = 0; self.velocidade_y = 0
            self.esta_em_jogo = False; saiu_por = "fundo_esquerda"
        elif self.x + self.raio >= quadra_rect.right:
            self.x = quadra_rect.right - self.raio
            self.velocidade_x = 0; self.velocidade_y = 0
            self.esta_em_jogo = False; saiu_por = "fundo_direita"

        # Usar 'if' em vez de 'elif' para permitir saídas de canto
        if self.y - self.raio <= quadra_rect.top:
            self.y = quadra_rect.top + self.raio
            self.velocidade_x = 0; self.velocidade_y = 0
            self.esta_em_jogo = False
            saiu_por = "lateral_superior" if saiu_por is None else f"{saiu_por}_e_lateral_superior"
        elif self.y + self.raio >= quadra_rect.bottom:
            self.y = quadra_rect.bottom - self.raio
            self.velocidade_x = 0; self.velocidade_y = 0
            self.esta_em_jogo = False
            saiu_por = "lateral_inferior" if saiu_por is None else f"{saiu_por}_e_lateral_inferior"

        if saiu_por:
            print(f"Bola saiu por: {saiu_por}") # DEBUG
            return saiu_por
        return None

    def chutar(self, forca_x, forca_y):
        # self.esta_em_jogo = True # Bola chutada volta a estar "em jogo" (se não estava)
        # Não precisa mais disso aqui, pois deixar_ser_controlada já a torna "em jogo" indiretamente
        # e o resetar_para_jogo também.
        self.velocidade_x = forca_x
        self.velocidade_y = forca_y

    def resetar_para_jogo(self, x, y):
        """ Recoloca a bola em jogo em uma nova posição. """
        self.x = float(x)
        self.y = float(y)
        self.velocidade_x = 0.0
        self.velocidade_y = 0.0
        self.esta_em_jogo = True
        print(f"Bola resetada para ({self.x}, {self.y}) e em jogo.") # DEBUG

    def desenhar(self, tela):
        pygame.draw.circle(tela, self.cor, (int(self.x), int(self.y)), self.raio)