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

                # Novos atributos para o "cooldown" de posse
        self.frames_desde_nova_posse = 0
        self.FRAMES_INVULNERABILIDADE_POSSE = 15 # Ex: 15 frames (0.25s a 60FPS) de posse "segura"

    def ser_controlada(self, jogador):
        self.controlada_por_jogador = jogador
        self.esta_em_jogo = True
        self.velocidade_x = 0
        self.velocidade_y = 0
        self.frames_desde_nova_posse = 0 # Reseta o contador quando um novo jogador pega
        print(f"BOLA: Controlada por {jogador.time}. Frames posse resetado.") # DEBUG

    def deixar_ser_controlada(self):
        self.controlada_por_jogador = None
        # print("BOLA: Deixou de ser controlada.") # DEBUG

    def mover(self, quadra_rect, gol_y_sup, gol_y_inf):
        if self.controlada_por_jogador:
            self.frames_desde_nova_posse += 1 # Incrementa o tempo que o jogador atual tem a posse

            offset_bola_x = self.controlada_por_jogador.raio + self.raio - 2
            direcao_x_posse = 1 if self.controlada_por_jogador.time == "A" else -1
            self.x = self.controlada_por_jogador.x + (direcao_x_posse * offset_bola_x)
            self.y = self.controlada_por_jogador.y
            self.velocidade_x = 0
            self.velocidade_y = 0
            self.esta_em_jogo = True
            return None

        # Se não está controlada, segue a lógica de bola livre:
        if not self.esta_em_jogo:
            self.velocidade_x = 0
            self.velocidade_y = 0
            return None

        # Movimento da bola livre (como você já tinha)
        self.x += self.velocidade_x
        self.y += self.velocidade_y

        self.velocidade_x *= self.atrito
        self.velocidade_y *= self.atrito

        if abs(self.velocidade_x) < 0.1: self.velocidade_x = 0
        if abs(self.velocidade_y) < 0.1: self.velocidade_y = 0

        saiu_por = None

        # Bola cruzou a linha de fundo ESQUERDA
        if self.x - self.raio <= quadra_rect.left:
            self.esta_em_jogo = False
            self.velocidade_x = 0; self.velocidade_y = 0
            if self.y > gol_y_sup and self.y < gol_y_inf: # GOL
                saiu_por = "GOL_ESQUERDA"
                self.x = quadra_rect.left - self.raio # Bola um pouco dentro do gol
            else: # Fundo
                saiu_por = "fundo_esquerda"
                self.x = quadra_rect.left + self.raio
        
        # Bola cruzou a linha de fundo DIREITA
        elif self.x + self.raio >= quadra_rect.right:
            self.esta_em_jogo = False
            self.velocidade_x = 0; self.velocidade_y = 0
            if self.y > gol_y_sup and self.y < gol_y_inf: # GOL
                saiu_por = "GOL_DIREITA"
                self.x = quadra_rect.right + self.raio
            else: # Fundo
                saiu_por = "fundo_direita"
                self.x = quadra_rect.right - self.raio

        # Colisão com linha lateral
        if self.esta_em_jogo: 
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
            if "GOL" in saiu_por:
                print(f"GOOOOLLL!!! {saiu_por}")
            else:
                print(f"Bola saiu por: {saiu_por}")
            return saiu_por
        return None

    def chutar(self, forca_x, forca_y):
        # self.esta_em_jogo = True # Bola chutada volta a estar "em jogo" (se não estava)
        # Não precisa mais disso aqui, pois deixar_ser_controlada já a torna "em jogo" indiretamente
        # e o resetar_para_jogo também.
        self.velocidade_x = forca_x
        self.velocidade_y = forca_y

    def resetar_para_jogo(self, x, y):
        self.x = float(x); self.y = float(y)
        self.velocidade_x = 0.0; self.velocidade_y = 0.0
        self.esta_em_jogo = True
        self.controlada_por_jogador = None
        self.frames_desde_nova_posse = 0 # Reseta aqui também
        print(f"Bola resetada para ({self.x}, {self.y}) e em jogo.")

    def desenhar(self, tela):
        pygame.draw.circle(tela, self.cor, (int(self.x), int(self.y)), self.raio)