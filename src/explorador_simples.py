"""
Sistema de Exploração Inteligente por Sensores
==============================================

Este módulo implementa um sistema de exploração autônoma que utiliza
apenas informações de sensores de proximidade para navegar em ambientes
desconhecidos. O sistema simula o comportamento de um agente real que
não possui conhecimento prévio do mapa e deve explorar para localizar
objetos de interesse.

Funcionalidades principais:
- Exploração baseada em sensores de proximidade
- Mapeamento progressivo do ambiente conhecido
- Estratégia de navegação em profundidade (DFS)
- Detecção e localização de objetos de interesse
- Sistema de backtracking para navegação

Autor: Sistema de Navegação Inteligente v2.0
Data: 2024
"""

from typing import List, Tuple, Optional, Set, Dict
import time
import random
from .sistema_audio import SistemaEfeitosSonoros

class ExploradorInteligente:
    """
    Sistema de exploração autônoma baseado em sensores de proximidade.
    
    Esta classe implementa um explorador que navega em ambientes desconhecidos
    utilizando apenas informações dos sensores de proximidade. O sistema
    constrói um mapa mental do ambiente conforme explora e utiliza estratégias
    de navegação para localizar objetos de interesse.
    
    Atributos:
        ambiente: Simulador do ambiente de navegação
        sistema_log: Sistema de registro de atividades
        mapa_conhecido (Dict): Mapa das posições conhecidas
        posicoes_visitadas (Set): Conjunto de posições já visitadas
        pilha_navegacao (List): Pilha para navegação em profundidade
        posicao_objeto (Optional[Tuple[int, int]]): Posição do objeto encontrado
        max_iteracoes (int): Número máximo de iterações de exploração
    """
    
    def __init__(self, ambiente, sistema_log=None, max_iteracoes: int = 500):
        """
        Inicializa o explorador inteligente.
        
        Args:
            ambiente: Simulador do ambiente de navegação
            sistema_log: Sistema de registro de atividades
            max_iteracoes (int): Número máximo de iterações de exploração
        """
        self.ambiente = ambiente
        self.sistema_log = sistema_log
        self.mapa_conhecido = {}  # (row, col) -> ' ', '*', 'H', 'E'
        self.posicoes_visitadas = set()
        self.pilha_navegacao = []
        self.posicao_objeto = None
        self.max_iteracoes = max_iteracoes
        
        # Sistema de efeitos sonoros
        self.sistema_audio = SistemaEfeitosSonoros(volume=0.3, habilitado=True)
        
        print("Explorador inteligente inicializado")
    
    def explorar_ate_encontrar_objeto(self) -> bool:
        """
        Explora o ambiente até encontrar o objeto de interesse.
        
        Returns:
            bool: True se o objeto foi encontrado, False caso contrário
        """
        print("Iniciando exploração inteligente...")
        
        # Adiciona posição inicial ao mapa conhecido
        posicao_inicial = self.ambiente.posicao_agente
        self.posicoes_visitadas.add(posicao_inicial)
        self.mapa_conhecido[posicao_inicial] = 'E'  # Assume entrada como 'E'
        self.pilha_navegacao.append(posicao_inicial)
        
        iteracao = 0
        
        while iteracao < self.max_iteracoes:
            iteracao += 1
            
            posicao_atual = self.pilha_navegacao[-1]  # Peek top of stack
            
            # Atualiza o mapa conhecido com as leituras da posição atual
            self._atualizar_mapa_com_sensores(posicao_atual)
            
            # Verifica se o objeto está adjacente
            leituras = self.ambiente.obter_leituras_sensores_proximidade()
            print(f"🔍 Sensores: Esquerda={leituras[0]}, Frente={leituras[1]}, Direita={leituras[2]}")
            
            if leituras[1] == "HUMANO":  # Sensor da frente
                self.posicao_objeto = self._get_posicao_a_frente(posicao_atual, self.ambiente.direcao_agente)
                self.mapa_conhecido[self.posicao_objeto] = '@'  # Marca no mapa conhecido
                print(f"🎯 HUMANO ENCONTRADO em {self.posicao_objeto}!")
                time.sleep(2)  # Pausa para mostrar descoberta
                return True
            
            # Tenta mover para uma nova posição
            proxima_posicao = self._encontrar_proxima_posicao_para_explorar(posicao_atual)
            
            if proxima_posicao:
                print(f"🤖 Explorando nova posição: {proxima_posicao}")
                self._mover_para(proxima_posicao)
                self.posicoes_visitadas.add(self.ambiente.posicao_agente)
                self.pilha_navegacao.append(self.ambiente.posicao_agente)
                print(f"📍 Robô agora em: {self.ambiente.posicao_agente}")
                time.sleep(1.5)  # Pausa para visualizar movimento
            else:
                print("🔄 Não há caminho à frente, fazendo backtracking...")
                # Se não há para onde ir, faz backtracking
                self.pilha_navegacao.pop()
                if self.pilha_navegacao:
                    self._mover_para(self.pilha_navegacao[-1])
                    time.sleep(1)  # Pausa para backtracking
                else:
                    # Se a pilha está vazia, não há mais para onde ir
                    break
            
            # Registra progresso
            if iteracao % 50 == 0:
                print(f"Iteração {iteracao}: Posição {self.ambiente.posicao_agente}, "
                      f"Mapa conhecido: {len(self.mapa_conhecido)} posições")
        
        print(f"Exploração finalizada após {iteracao} iterações")
        return False
    
    def _atualizar_mapa_com_sensores(self, posicao_atual):
        """
        Atualiza o mapa conhecido com informações dos sensores atuais.
        """
        i, j = posicao_atual
        direcao_robo = self.ambiente.direcao_agente
        
        # Mapeia direções relativas (esquerdo, frente, direito) para coordenadas absolutas
        # 0=Norte, 1=Leste, 2=Sul, 3=Oeste
        mapa_direcoes_sensores = {
            0: [(-1, -1), (-1, 0), (-1, 1)],  # Norte: esq, frente, dir
            1: [(-1, 1), (0, 1), (1, 1)],     # Leste: esq, frente, dir  
            2: [(1, 1), (1, 0), (1, -1)],     # Sul: esq, frente, dir
            3: [(1, -1), (0, -1), (-1, -1)]   # Oeste: esq, frente, dir
        }
        
        leituras = self.ambiente.obter_leituras_sensores_proximidade()
        direcoes_relativas = mapa_direcoes_sensores[direcao_robo]
        
        for idx, (di, dj) in enumerate(direcoes_relativas):
            ni, nj = i + di, j + dj
            celula_lida = leituras[idx]
            
            if celula_lida == "PAREDE":
                self.mapa_conhecido[(ni, nj)] = 'X'
            elif celula_lida == "HUMANO":
                self.mapa_conhecido[(ni, nj)] = '@'
                self.posicao_objeto = (ni, nj)
            elif celula_lida == "VAZIO":
                if (ni, nj) not in self.mapa_conhecido:  # Não sobrescreve 'E' ou '@'
                    self.mapa_conhecido[(ni, nj)] = '.'
    
    def _encontrar_proxima_posicao_para_explorar(self, posicao_atual):
        """
        Encontra a próxima posição para explorar.
        
        Args:
            posicao_atual (Tuple[int, int]): Posição atual
            
        Returns:
            Optional[Tuple[int, int]]: Próxima posição para explorar ou None
        """
        i, j = posicao_atual
        direcao_robo = self.ambiente.direcao_agente
        
        # Prioriza frente, depois direita, depois esquerda
        ordem_exploracao = [
            (0, 1),   # Frente
            (1, 0),   # Direita (após um G)
            (-1, 0)   # Esquerda (após três G's)
        ]
        
        # Mapeia direções relativas para absolutas
        # 0=Norte, 1=Leste, 2=Sul, 3=Oeste
        direcoes_absolutas = {
            0: [(-1, 0), (0, 1), (0, -1)],  # Norte: frente, direita, esquerda
            1: [(0, 1), (1, 0), (-1, 0)],   # Leste: frente, direita, esquerda
            2: [(1, 0), (0, -1), (0, 1)],   # Sul: frente, direita, esquerda
            3: [(0, -1), (-1, 0), (1, 0)]   # Oeste: frente, direita, esquerda
        }
        
        for di, dj in direcoes_absolutas[direcao_robo]:
            nova_posicao = (i + di, j + dj)
            if (nova_posicao not in self.posicoes_visitadas and 
                self.mapa_conhecido.get(nova_posicao) != 'X'):  # Não é parede
                return nova_posicao
        return None
    
    def _mover_para(self, posicao_alvo):
        """
        Move o agente para uma posição específica.
        
        Args:
            posicao_alvo (Tuple[int, int]): Posição de destino
        """
        atual = self.ambiente.posicao_agente
        dx = posicao_alvo[0] - atual[0]
        dy = posicao_alvo[1] - atual[1]
        
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
        
        self._ajustar_direcao(direcao_alvo)
        print(f"🚶 Robô andando para {posicao_alvo}")
        
        # Toca som de movimento
        self.sistema_audio.som_movimento()
        
        self.ambiente.executar_comando_navegacao('A')
        self.ambiente.exibir_estado_ambiente()
        if self.sistema_log:
            leituras = self.ambiente.obter_leituras_sensores_proximidade()
            compartimento = 'COM HUMANO' if self.ambiente.objeto_coletado else 'SEM CARGA'
            self.sistema_log.registrar_atividade('A', self.ambiente.posicao_agente, self.ambiente.direcao_agente, leituras, compartimento)
    
    def _ajustar_direcao(self, direcao_alvo):
        """
        Ajusta a direção do agente para a direção especificada.
        
        Args:
            direcao_alvo (int): Direção alvo (0=Norte, 1=Leste, 2=Sul, 3=Oeste)
        """
        while self.ambiente.direcao_agente != direcao_alvo:
            print(f"🔄 Robô girando... Direção atual: {self.ambiente.direcao_agente}, Alvo: {direcao_alvo}")
            
            # Toca som de rotação
            self.sistema_audio.som_rotacao()
            
            self.ambiente.executar_comando_navegacao('G')
            time.sleep(0.5)  # Pausa para girar
            if self.sistema_log:
                leituras = self.ambiente.obter_leituras_sensores_proximidade()
                compartimento = 'COM HUMANO' if self.ambiente.objeto_coletado else 'SEM CARGA'
                self.sistema_log.registrar_atividade('G', self.ambiente.posicao_agente, self.ambiente.direcao_agente, leituras, compartimento)
    
    def _get_posicao_a_frente(self, posicao_atual, direcao_robo):
        """
        Obtém a posição à frente do agente.
        
        Args:
            posicao_atual (Tuple[int, int]): Posição atual
            direcao_robo (int): Direção atual do agente
            
        Returns:
            Tuple[int, int]: Posição à frente
        """
        i, j = posicao_atual
        if direcao_robo == 0:
            return (i-1, j)  # Norte
        if direcao_robo == 1:
            return (i, j+1)  # Leste
        if direcao_robo == 2:
            return (i+1, j)  # Sul
        if direcao_robo == 3:
            return (i, j-1)  # Oeste
        return None
    
    def obter_estatisticas_exploracao(self) -> dict:
        """
        Obtém estatísticas da exploração realizada.
        
        Returns:
            dict: Dicionário com estatísticas da exploração
        """
        return {
            'posicoes_exploradas': len(self.mapa_conhecido),
            'profundidade_pilha': len(self.pilha_navegacao),
            'objeto_encontrado': self.posicao_objeto is not None,
            'posicao_objeto': self.posicao_objeto,
            'posicao_atual': self.ambiente.posicao_agente
        }

# Alias para compatibilidade com código existente
ExploradorSimples = ExploradorInteligente