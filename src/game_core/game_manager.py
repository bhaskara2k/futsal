# src/game_core/game_manager.py
import pygame
from src import config # Para os estados e outras configs

class GameManager:
    def __init__(self, bola, lista_jogadores, posicoes_iniciais_jogadores):
        self.bola = bola
        self.lista_jogadores = lista_jogadores
        self.posicoes_iniciais_jogadores = posicoes_iniciais_jogadores # Dicionário: {jogador_obj: (x,y)}

        self.placar_time_A = 0
        self.placar_time_B = 0
        
        self.estado_jogo = config.ESTADO_PREPARANDO_SAQUE
        self.quem_saca = "A" # Time A começa sacando, por exemplo

        self.timer_estado_gol = 0
        self.DURACAO_ESTADO_GOL = 180 # Frames (ex: 3 segundos a 60FPS)

        print("GameManager iniciado. Preparando primeiro saque.")
        self.preparar_saque_centro() # Prepara o primeiro saque

    def atualizar_estado(self):
        """Gerencia as transições de estado e lógicas de cada estado."""
        if self.estado_jogo == config.ESTADO_GOL_MARCADO:
            self.timer_estado_gol += 1
            if self.timer_estado_gol > self.DURACAO_ESTADO_GOL:
                self.preparar_saque_centro() # Prepara para o próximo saque
        
        # (No futuro, ESTADO_PREPARANDO_SAQUE pode ter uma pequena pausa antes de ir para JOGANDO)

    def registrar_gol(self, time_que_marcou):
        if self.estado_jogo == config.ESTADO_JOGANDO: # Só registra gol se estiver jogando
            if time_que_marcou == "A":
                self.placar_time_A += 1
                self.quem_saca = "B" # O outro time saca
            elif time_que_marcou == "B":
                self.placar_time_B += 1
                self.quem_saca = "A" # O outro time saca
            
            print(f"GOL DO TIME {time_que_marcou}! Placar: A {self.placar_time_A} x {self.placar_time_B} B")
            self.estado_jogo = config.ESTADO_GOL_MARCADO
            self.timer_estado_gol = 0 # Reseta o timer para a comemoração/pausa do gol
            
            # Parar todos os jogadores e a bola
            self.bola.velocidade_x = 0
            self.bola.velocidade_y = 0
            self.bola.controlada_por_jogador = None # Garante que a bola está livre
            for jogador in self.lista_jogadores:
                jogador.set_velocidade(0, 0)
                jogador.tem_bola = False


    def preparar_saque_centro(self):
        print(f"Preparando saque. Time {self.quem_saca} vai sacar.")
        self.estado_jogo = config.ESTADO_PREPARANDO_SAQUE # Ou diretamente JOGANDO após um pequeno delay

        # Reposicionar bola no centro
        self.bola.resetar_para_jogo(config.LARGURA_TELA / 2, config.ALTURA_TELA / 2)

        # Reposicionar jogadores
        for jogador in self.lista_jogadores:
            pos_inicial = self.posicoes_iniciais_jogadores.get(jogador)
            if pos_inicial:
                jogador.x = pos_inicial[0]
                jogador.y = pos_inicial[1]
            jogador.set_velocidade(0, 0) # Garantir que comecem parados
            jogador.tem_bola = False

            # Simples lógica de posse para o saque:
            # O jogador "mais próximo" do centro do time que saca pega a bola
            # (Pode ser mais sofisticado, mas para 1v1 é o único do time)
            if jogador.time == self.quem_saca:
                 # Para 1v1, este jogador sempre pegará a bola para o saque
                 if not jogador.tem_bola and self.bola.controlada_por_jogador is None: # Garante que só pega se a bola estiver livre
                     jogador.tem_bola = True
                     self.bola.ser_controlada(jogador)
                     print(f"Jogador {jogador.time} com a posse para o saque.")


        # Após um pequeno tempo ou uma ação (ex: primeiro toque), mudaria para ESTADO_JOGANDO
        # Por enquanto, vamos mudar direto para JOGANDO para simplificar
        # Idealmente, PREPARANDO_SAQUE teria um pequeno delay ou esperaria um input para o "primeiro toque"
        self.estado_jogo = config.ESTADO_JOGANDO 
        print("Saque preparado. Estado: JOGANDO")


    def obter_estado_jogo(self):
        return self.estado_jogo

    def obter_placar_formatado(self):
        return f"Time A: {self.placar_time_A}  Time B: {self.placar_time_B}"