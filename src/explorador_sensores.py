"""
Algoritmo de exploração usando apenas os sensores do robô.
O robô não conhece o mapa e deve explorar o ambiente para encontrar o humano.
"""

class ExploradorSensores:
    def __init__(self, simulador, logger=None):
        self.simulador = simulador
        self.logger = logger
        self.mapa_conhecido = {}  # {(x, y): 'PAREDE'|'VAZIO'|'HUMANO'}
        self.posicoes_visitadas = set()
        self.pilha_exploracao = []
        self.humano_encontrado = False
        self.posicao_humano = None
        
    def explorar_ambiente(self):
        """
        Explora o ambiente usando apenas os sensores até encontrar o humano.
        """
        print("Iniciando exploração do ambiente...")
        
        # Começa na posição inicial
        posicao_atual = self.simulador.posicao_robo
        self.pilha_exploracao.append(posicao_atual)
        
        while not self.humano_encontrado and self.pilha_exploracao:
            posicao_atual = self.pilha_exploracao[-1]
            
            # Move o robô para a posição atual se necessário
            if self.simulador.posicao_robo != posicao_atual:
                self._mover_para_posicao(posicao_atual)
            
            # Verifica se encontrou o humano
            if self._verificar_humano():
                self.humano_encontrado = True
                self.posicao_humano = posicao_atual
                print(f"Humano encontrado em {posicao_atual}!")
                break
            
            # Explora a posição atual
            self._explorar_posicao(posicao_atual)
            
            # Encontra próxima posição para explorar
            proxima_posicao = self._encontrar_proxima_posicao()
            if proxima_posicao:
                self.pilha_exploracao.append(proxima_posicao)
            else:
                # Volta para posição anterior
                if len(self.pilha_exploracao) > 1:
                    self.pilha_exploracao.pop()
                else:
                    break
        
        return self.humano_encontrado
    
    def _verificar_humano(self):
        """
        Verifica se o humano está à frente do robô usando os sensores.
        """
        leituras = self.simulador.obter_leituras_sensores()
        return len(leituras) >= 2 and leituras[1] == "HUMANO"
    
    def _explorar_posicao(self, posicao):
        """
        Explora a posição atual e mapeia o ambiente ao redor.
        """
        if posicao in self.posicoes_visitadas:
            return
        
        self.posicoes_visitadas.add(posicao)
        print(f"Explorando posição {posicao}")
        
        # Mapeia as 4 direções ao redor da posição atual
        direcoes = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # Norte, Leste, Sul, Oeste
        nomes_direcoes = ['Norte', 'Leste', 'Sul', 'Oeste']
        
        for i, (dx, dy) in enumerate(direcoes):
            nova_posicao = (posicao[0] + dx, posicao[1] + dy)
            
            # Gira o robô para a direção desejada
            direcao_atual = self.simulador.direcao_robo
            while direcao_atual != i:
                self.simulador.mover_robo('G')
                direcao_atual = (direcao_atual + 1) % 4
            
            # Lê os sensores
            leituras = self.simulador.obter_leituras_sensores()
            sensor_frente = leituras[1] if len(leituras) >= 2 else "PAREDE"
            
            # Mapeia a posição
            self.mapa_conhecido[nova_posicao] = sensor_frente
            
            print(f"  {nomes_direcoes[i]}: {sensor_frente}")
    
    def _encontrar_proxima_posicao(self):
        """
        Encontra a próxima posição não visitada para explorar.
        """
        # Procura por posições vazias não visitadas que sejam adjacentes a posições visitadas
        posicao_atual = self.simulador.posicao_robo
        
        # Verifica posições adjacentes à posição atual
        for dx, dy in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
            nova_posicao = (posicao_atual[0] + dx, posicao_atual[1] + dy)
            
            if (nova_posicao in self.mapa_conhecido and 
                self.mapa_conhecido[nova_posicao] == "VAZIO" and 
                nova_posicao not in self.posicoes_visitadas):
                return nova_posicao
        
        return None
    
    def _mover_para_posicao(self, posicao_alvo):
        """
        Move o robô para uma posição específica.
        """
        atual = self.simulador.posicao_robo
        dx = posicao_alvo[0] - atual[0]
        dy = posicao_alvo[1] - atual[1]
        
        # Determina a direção alvo
        if dx == 1:
            direcao_alvo = 2  # Sul
        elif dx == -1:
            direcao_alvo = 0  # Norte
        elif dy == 1:
            direcao_alvo = 1  # Leste
        elif dy == -1:
            direcao_alvo = 3  # Oeste
        else:
            return
        
        # Ajusta a direção
        while self.simulador.direcao_robo != direcao_alvo:
            self.simulador.mover_robo('G')
        
        # Move para frente
        self.simulador.mover_robo('A')
    
    def encontrar_caminho_para_humano(self):
        """
        Encontra um caminho para o humano usando o mapa conhecido.
        """
        if not self.humano_encontrado:
            return None
        
        # Implementa busca em largura para encontrar o caminho mais curto
        from collections import deque
        
        inicio = self.simulador.posicao_robo
        fim = self.posicao_humano
        
        fila = deque([(inicio, [inicio])])
        visitados = {inicio}
        
        while fila:
            posicao_atual, caminho = fila.popleft()
            
            if posicao_atual == fim:
                return caminho
            
            # Explora vizinhos
            for dx, dy in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
                nova_posicao = (posicao_atual[0] + dx, posicao_atual[1] + dy)
                
                if (nova_posicao not in visitados and 
                    nova_posicao in self.mapa_conhecido and 
                    self.mapa_conhecido[nova_posicao] == "VAZIO"):
                    
                    visitados.add(nova_posicao)
                    fila.append((nova_posicao, caminho + [nova_posicao]))
        
        return None
