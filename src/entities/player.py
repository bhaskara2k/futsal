# src/entities/player.py
import pygame
import math
from src import config

class Player:
    def __init__(self, x, y, raio, cor, time="A", controlado_por_ia=False): # Novo parâmetro
        self.x = float(x)
        self.y = float(y)
        self.raio = int(raio)
        self.cor = cor
        self.time = time
        self.controlado_por_ia = controlado_por_ia # Indica se a IA controla este jogador

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
        """Verifica se o jogador colide com a bola e pode pegá-la."""
        if not self.tem_bola and bola.esta_em_jogo: # Se eu não tenho a bola e ela está em jogo
            dist_x = self.x - bola.x
            dist_y = self.y - bola.y
            distancia = (dist_x**2 + dist_y**2)**0.5

            if distancia < self.raio + bola.raio: # Houve contato físico
                pode_pegar_ou_roubar = False
                if bola.controlada_por_jogador is None: # Bola está livre
                    pode_pegar_ou_roubar = True
                    print(f"DEBUG JOGADOR {self.time}: Bola estava livre, pegando.") #DEBUG
                elif bola.controlada_por_jogador != self and \
                     bola.frames_desde_nova_posse > bola.FRAMES_INVULNERABILIDADE_POSSE:
                    # Bola está com oponente, mas o "cooldown" de posse dele já passou
                    print(f"DEBUG JOGADOR {self.time}: Tentando roubar de {bola.controlada_por_jogador.time}. Frames posse oponente: {bola.frames_desde_nova_posse}") #DEBUG
                    if bola.controlada_por_jogador: # Garante que o oponente perca a bola
                        bola.controlada_por_jogador.tem_bola = False
                    pode_pegar_ou_roubar = True
                # else: Se a bola está com oponente e cooldown não passou, não faz nada
                    # print(f"DEBUG JOGADOR {self.time}: Oponente {bola.controlada_por_jogador.time} ainda protegido. Frames posse: {bola.frames_desde_nova_posse}")


                if pode_pegar_ou_roubar:
                    self.tem_bola = True
                    bola.ser_controlada(self) # Isso reseta bola.frames_desde_nova_posse para 0
                    # O print de quem pegou a bola já está em bola.ser_controlada indiretamente ou no original
                    print(f"Jogador {self.time} ({'IA' if self.controlado_por_ia else 'Humano'}) AGORA TEM A BOLA!") # DEBUG
                    return True
        return False

    def chutar_bola(self, bola_ref, forca_chute=10.0):
        """Jogador chuta a bola."""
        if self.tem_bola:
            self.tem_bola = False
            
            # Jogador não controla mais a bola
            bola_ref.controlada_por_jogador = None # Libera a bola do controle

            # Posicionar a bola para o chute: ligeiramente à frente do jogador
            direcao_chute_x_normalizada = 1 if self.time == "A" else -1
            
            # Distância à frente do jogador para posicionar a bola
            offset_pos_bola = self.raio + bola_ref.raio + 1 # Bola um pixel à frente do contato

            nova_bola_x = self.x + (direcao_chute_x_normalizada * offset_pos_bola)
            nova_bola_y = self.y # Mantém o Y do jogador para um chute reto inicial

            # AINDA NÃO ESTAMOS CLAMPANDO A POSIÇÃO DA BOLA NA QUADRA AQUI,
            # A FÍSICA DA BOLA (bola.mover) DEVE CUIDAR DISSO QUANDO ELA ESTIVER LIVRE.
            # MAS, SE O JOGADOR ESTIVER MUITO COLADO NA LINHA, ISSO PODE SER UM PROBLEMA.
            # VAMOS VER COM OS DEBUG PRINTS PRIMEIRO.
            
            bola_ref.x = nova_bola_x
            bola_ref.y = nova_bola_y
            
            # Aplicar a força do chute
            # Time A chuta para a direita, Time B para a esquerda
            vx_chute = direcao_chute_x_normalizada * forca_chute
            vy_chute = 0 # Chute reto por enquanto
            
            bola_ref.chutar(vx_chute, vy_chute)
            print(f"Jogador {self.time} ({'IA' if self.controlado_por_ia else 'Humano'}) chutou a bola de ({nova_bola_x:.1f},{nova_bola_y:.1f}) com vel ({vx_chute}, {vy_chute})")

    def atualizar_cerebro_ia(self, bola_obj, quadra_rect):
        """ Lógica de decisão da IA para este jogador. """
        if not self.controlado_por_ia:
            return

        if self.tem_bola:
            gol_adversario_x = 0
            if self.time == "A":
                gol_adversario_x = quadra_rect.right
            else: # Time B
                gol_adversario_x = quadra_rect.left
            
            meio_gol_adversario_y = config.ALTURA_TELA / 2
            dist_x_para_gol = abs(self.x - gol_adversario_x)
            LIMITE_DISTANCIA_CHUTE = quadra_rect.width * 0.3

            print(f"DEBUG IA {self.time}: Com bola. MinhaPos X: {self.x:.1f}, GolAdv X: {gol_adversario_x:.1f}, DistXParaGol: {dist_x_para_gol:.1f}, LimiteChute: {LIMITE_DISTANCIA_CHUTE:.1f}") # DEBUG

            if dist_x_para_gol < LIMITE_DISTANCIA_CHUTE:
                print(f"DEBUG IA {self.time}: CONDIÇÃO DE CHUTE ATINGIDA!") # DEBUG
                self.chutar_bola(bola_obj)
                self.set_velocidade(0,0) # IMPORTANTE: Parar o jogador no frame que ele chuta
            else:
                # Ainda não está perto o suficiente, conduzir a bola (driblar)
                print(f"DEBUG IA Jogador {self.time}: Conduzindo bola para o gol. Dist: {dist_x_para_gol:.1f}")
                dir_x_gol = gol_adversario_x - self.x
                dir_y_gol = meio_gol_adversario_y - self.y # Mirar no centro do gol verticalmente
                print(f"DEBUG IA {self.time}: Driblando...") # DEBUG

                distancia_para_meio_gol = (dir_x_gol**2 + dir_y_gol**2)**0.5

                if distancia_para_meio_gol > 0:
                    norm_x_gol = dir_x_gol / distancia_para_meio_gol
                    norm_y_gol = dir_y_gol / distancia_para_meio_gol
                else:
                    norm_x_gol = 0
                    norm_y_gol = 0
                
                # Driblar com uma velocidade um pouco menor que a máxima talvez?
                velocidade_drible = self.velocidade_max * 0.8 
                self.set_velocidade(norm_x_gol * velocidade_drible, norm_y_gol * velocidade_drible)
            return

        # IA NÃO TEM A BOLA: Lógica de seguir a bola (como antes)
        # ... (o restante da lógica de seguir a bola permanece igual)
        dir_x = bola_obj.x - self.x
        dir_y = bola_obj.y - self.y
        distancia_para_bola = (dir_x**2 + dir_y**2)**0.5

        if distancia_para_bola > 0:
            norm_x = dir_x / distancia_para_bola
            norm_y = dir_y / distancia_para_bola
        else:
            norm_x = 0
            norm_y = 0
        
        # ---- INÍCIO DA NOVA LÓGICA DE VELOCIDADE DE APROXIMAÇÃO ----
        velocidade_aproximacao = self.velocidade_max
        
        # Se estiver muito perto da bola, reduz a velocidade para um "toque" mais suave
        # Usamos o raio do jogador como referência para "perto"
        if distancia_para_bola < self.raio * 1.5: # Ex: se a distância é menor que 1.5x o raio do jogador
            velocidade_aproximacao = self.velocidade_max * 0.3 # Bem devagar para o "domínio"
            print(f"DEBUG IA {self.time}: Perto da bola ({distancia_para_bola:.1f}), reduzindo vel para pegar.") #DEBUG
        elif distancia_para_bola < self.raio * 3: # Ex: se a distância é menor que 3x o raio do jogador
            velocidade_aproximacao = self.velocidade_max * 0.6 # Moderadamente devagar
        # Senão, mantém velocidade_max
        # ---- FIM DA NOVA LÓGICA DE VELOCIDADE DE APROXIMAÇÃO ----
        
        self.set_velocidade(norm_x * velocidade_aproximacao, norm_y * velocidade_aproximacao)


    def desenhar(self, tela):
        pygame.draw.circle(tela, self.cor, (int(self.x), int(self.y)), self.raio)
        if self.time == "B":
            pygame.draw.circle(tela, config.PRETO, (int(self.x), int(self.y)), self.raio // 2)

        # Visualizar se tem a bola
        if self.tem_bola:
            pygame.draw.rect(tela, config.BRANCO, (self.x - 5, self.y - self.raio - 10, 10, 5))
        