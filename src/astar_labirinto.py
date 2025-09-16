"""
Algoritmo de Busca Heurística A* para Navegação em Ambientes Complexos
======================================================================

Este módulo implementa o algoritmo de busca A* (A-star) otimizado para
navegação em ambientes bidimensionais. O algoritmo utiliza uma função
heurística baseada na distância de Manhattan para encontrar o caminho
ótimo entre dois pontos em um labirinto.

Características do algoritmo:
- Busca informada com função heurística
- Garantia de encontrar o caminho ótimo (se existir)
- Eficiência computacional através de estrutura de dados otimizada
- Suporte a diferentes tipos de obstáculos e terreno

Autor: Sistema de Navegação Inteligente v2.0
Data: 2024
"""

import heapq
from typing import List, Tuple, Optional, Set, Dict

class NoNavegacao:
    """
    Representa um nó na estrutura de busca do algoritmo A*.
    
    Cada nó contém informações sobre uma posição no ambiente,
    incluindo custos de caminho, heurística e referência ao nó pai
    para reconstrução do caminho.
    
    Atributos:
        posicao (Tuple[int, int]): Coordenadas (linha, coluna) do nó
        custo_g (float): Custo real do caminho desde o início
        custo_h (float): Custo heurístico estimado até o objetivo
        custo_f (float): Custo total (g + h)
        no_pai (Optional[NoNavegacao]): Referência ao nó pai no caminho
    """
    
    def __init__(self, posicao: Tuple[int, int], custo_g: float = 0, custo_h: float = 0, no_pai=None):
        """
        Inicializa um nó de navegação.
        
        Args:
            posicao (Tuple[int, int]): Coordenadas do nó
            custo_g (float): Custo real do caminho
            custo_h (float): Custo heurístico
            no_pai (Optional[NoNavegacao]): Nó pai
        """
        self.posicao = posicao
        self.custo_g = custo_g
        self.custo_h = custo_h
        self.custo_f = custo_g + custo_h
        self.no_pai = no_pai
    
    def __lt__(self, outro):
        """
        Compara nós para ordenação na fila de prioridade.
        
        Args:
            outro (NoNavegacao): Outro nó para comparação
            
        Returns:
            bool: True se este nó tem menor custo f
        """
        return self.custo_f < outro.custo_f
    
    def __eq__(self, outro):
        """
        Verifica igualdade entre nós baseada na posição.
        
        Args:
            outro (NoNavegacao): Outro nó para comparação
            
        Returns:
            bool: True se as posições forem iguais
        """
        return isinstance(outro, NoNavegacao) and self.posicao == outro.posicao
    
    def __hash__(self):
        """
        Calcula hash do nó baseado na posição.
        
        Returns:
            int: Hash da posição
        """
        return hash(self.posicao)

def calcular_distancia_manhattan(posicao_atual: Tuple[int, int], posicao_objetivo: Tuple[int, int]) -> float:
    """
    Calcula a distância de Manhattan entre duas posições.
    
    A distância de Manhattan é a soma das diferenças absolutas das
    coordenadas, sendo uma heurística admissível para o algoritmo A*.
    
    Args:
        posicao_atual (Tuple[int, int]): Posição atual (linha, coluna)
        posicao_objetivo (Tuple[int, int]): Posição objetivo (linha, coluna)
        
    Returns:
        float: Distância de Manhattan entre as posições
    """
    linha_atual, coluna_atual = posicao_atual
    linha_objetivo, coluna_objetivo = posicao_objetivo
    
    return abs(linha_atual - linha_objetivo) + abs(coluna_atual - coluna_objetivo)

def obter_vizinhos_validos(posicao: Tuple[int, int], mapa: List[List[str]]) -> List[Tuple[int, int]]:
    """
    Obtém lista de posições vizinhas válidas para navegação.
    
    Considera válidas apenas as posições que estão dentro dos limites
    do mapa e não contêm obstáculos (paredes).
    
    Args:
        posicao (Tuple[int, int]): Posição atual (linha, coluna)
        mapa (List[List[str]]): Representação do mapa
        
    Returns:
        List[Tuple[int, int]]: Lista de posições vizinhas válidas
    """
    linha, coluna = posicao
    vizinhos = []
    
    # Direções possíveis: Norte, Sul, Leste, Oeste
    direcoes = [(-1, 0), (1, 0), (0, 1), (0, -1)]
    
    for delta_linha, delta_coluna in direcoes:
        nova_linha = linha + delta_linha
        nova_coluna = coluna + delta_coluna
        
        # Verifica se está dentro dos limites do mapa
        if (0 <= nova_linha < len(mapa) and 
            0 <= nova_coluna < len(mapa[0])):
            
            # Verifica se não é uma parede
            if mapa[nova_linha][nova_coluna] != '*':
                vizinhos.append((nova_linha, nova_coluna))
    
    return vizinhos

def reconstruir_caminho_otimo(no_objetivo: NoNavegacao) -> List[Tuple[int, int]]:
    """
    Reconstrói o caminho ótimo desde o nó objetivo até o início.
    
    Percorre a cadeia de nós pais para construir a sequência
    completa de posições do caminho encontrado.
    
    Args:
        no_objetivo (NoNavegacao): Nó que representa o objetivo alcançado
        
    Returns:
        List[Tuple[int, int]]: Lista de posições do caminho ótimo
    """
    caminho = []
    no_atual = no_objetivo
    
    # Percorre a cadeia de nós pais
    while no_atual is not None:
        caminho.append(no_atual.posicao)
        no_atual = no_atual.no_pai
    
    # Inverte para obter o caminho do início ao fim
    caminho.reverse()
    return caminho

def algoritmo_busca_astar(mapa: List[List[str]], 
                         posicao_inicial: Tuple[int, int], 
                         posicao_objetivo: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
    """
    Implementa o algoritmo de busca A* para encontrar o caminho ótimo.
    
    O algoritmo A* combina busca em largura com heurística para encontrar
    o caminho mais eficiente entre dois pontos em um ambiente com obstáculos.
    
    Args:
        mapa (List[List[str]]): Representação matricial do ambiente
        posicao_inicial (Tuple[int, int]): Posição de início (linha, coluna)
        posicao_objetivo (Tuple[int, int]): Posição objetivo (linha, coluna)
        
    Returns:
        Optional[List[Tuple[int, int]]]: Caminho ótimo ou None se não encontrado
        
    Raises:
        ValueError: Se as posições forem inválidas ou o mapa estiver vazio
    """
    # Validações de entrada
    if not mapa or not mapa[0]:
        raise ValueError("Mapa não pode estar vazio")
    
    if (posicao_inicial[0] < 0 or posicao_inicial[0] >= len(mapa) or
        posicao_inicial[1] < 0 or posicao_inicial[1] >= len(mapa[0])):
        raise ValueError(f"Posição inicial inválida: {posicao_inicial}")
    
    if (posicao_objetivo[0] < 0 or posicao_objetivo[0] >= len(mapa) or
        posicao_objetivo[1] < 0 or posicao_objetivo[1] >= len(mapa[0])):
        raise ValueError(f"Posição objetivo inválida: {posicao_objetivo}")
    
    # Verifica se as posições não são obstáculos
    if mapa[posicao_inicial[0]][posicao_inicial[1]] == '*':
        raise ValueError(f"Posição inicial é um obstáculo: {posicao_inicial}")
    
    if mapa[posicao_objetivo[0]][posicao_objetivo[1]] == '*':
        raise ValueError(f"Posição objetivo é um obstáculo: {posicao_objetivo}")
    
    # Se início e objetivo são iguais
    if posicao_inicial == posicao_objetivo:
        return [posicao_inicial]
    
    # Inicializa estruturas de dados
    fila_prioridade = []  # Heap para nós a serem explorados
    nos_visitados: Set[Tuple[int, int]] = set()  # Conjunto de posições visitadas
    nos_abertos: Dict[Tuple[int, int], NoNavegacao] = {}  # Nós em aberto
    
    # Cria nó inicial
    custo_h_inicial = calcular_distancia_manhattan(posicao_inicial, posicao_objetivo)
    no_inicial = NoNavegacao(posicao_inicial, 0, custo_h_inicial)
    
    # Adiciona à fila de prioridade
    heapq.heappush(fila_prioridade, no_inicial)
    nos_abertos[posicao_inicial] = no_inicial
    
    print(f"Iniciando busca A* de {posicao_inicial} para {posicao_objetivo}")
    
    # Loop principal do algoritmo
    while fila_prioridade:
        # Remove nó com menor custo f da fila
        no_atual = heapq.heappop(fila_prioridade)
        
        # Verifica se chegou ao objetivo
        if no_atual.posicao == posicao_objetivo:
            caminho_encontrado = reconstruir_caminho_otimo(no_atual)
            print(f"Caminho encontrado com {len(caminho_encontrado)} posições")
            return caminho_encontrado
        
        # Marca como visitado
        nos_visitados.add(no_atual.posicao)
        
        # Remove dos nós em aberto
        if no_atual.posicao in nos_abertos:
            del nos_abertos[no_atual.posicao]
        
        # Explora vizinhos
        vizinhos = obter_vizinhos_validos(no_atual.posicao, mapa)
        
        for posicao_vizinho in vizinhos:
            # Pula se já foi visitado
            if posicao_vizinho in nos_visitados:
                continue
            
            # Calcula custos
            custo_g_vizinho = no_atual.custo_g + 1  # Custo unitário por movimento
            custo_h_vizinho = calcular_distancia_manhattan(posicao_vizinho, posicao_objetivo)
            
            # Verifica se já existe um nó para esta posição
            if posicao_vizinho in nos_abertos:
                no_vizinho_existente = nos_abertos[posicao_vizinho]
                
                # Se encontrou um caminho melhor, atualiza
                if custo_g_vizinho < no_vizinho_existente.custo_g:
                    no_vizinho_existente.custo_g = custo_g_vizinho
                    no_vizinho_existente.custo_f = custo_g_vizinho + custo_h_vizinho
                    no_vizinho_existente.no_pai = no_atual
                    
                    # Reordena a fila de prioridade
                    heapq.heapify(fila_prioridade)
            else:
                # Cria novo nó
                no_vizinho = NoNavegacao(posicao_vizinho, custo_g_vizinho, custo_h_vizinho, no_atual)
                
                # Adiciona à fila e aos nós em aberto
                heapq.heappush(fila_prioridade, no_vizinho)
                nos_abertos[posicao_vizinho] = no_vizinho
    
    # Se chegou aqui, não encontrou caminho
    print("Nenhum caminho encontrado entre as posições especificadas")
    return None

# Alias para compatibilidade com código existente
busca_astar = algoritmo_busca_astar