"""
Sistema de Simulação de Ambiente para Navegação Autônoma
========================================================

Este módulo implementa um simulador de ambiente que permite a navegação
de um agente autônomo em um labirinto bidimensional. O sistema simula
sensores de proximidade, movimento e interação com objetos no ambiente.

Funcionalidades principais:
- Carregamento e validação de mapas de labirinto
- Simulação de sensores de proximidade (esquerdo, frente, direito)
- Controle de movimento e rotação do agente
- Detecção e coleta de objetos de interesse
- Validação de estados do ambiente

Autor: Sistema de Navegação Autônoma v2.0
Data: 2024
"""

import os
from typing import List, Tuple, Optional

class AmbienteNavegacao:
    """
    Classe principal para simulação de ambiente de navegação.
    
    Esta classe gerencia todo o estado do ambiente de navegação, incluindo:
    - Mapa do labirinto
    - Posição e orientação do agente
    - Estado dos objetos coletáveis
    - Validações de integridade do ambiente
    
    Atributos:
        nome_mapa (str): Nome identificador do mapa carregado
        labirinto (List[str]): Representação matricial do labirinto
        posicao_agente (Tuple[int, int]): Coordenadas (linha, coluna) do agente
        direcao_agente (int): Orientação atual do agente (0=Norte, 1=Leste, 2=Sul, 3=Oeste)
        objeto_coletado (bool): Flag indicando se o objeto foi coletado
    """
    
    def __init__(self, mapa_ou_arquivo):
        """
        Inicializa o simulador de ambiente.
        
        Args:
            mapa_ou_arquivo: Pode ser uma lista (mapa em memória) ou string (caminho do arquivo)
        
        Raises:
            ValueError: Se o mapa não for válido ou não puder ser carregado
        """
        # Verifica se o input é uma lista (mapa) ou um arquivo
        if isinstance(mapa_ou_arquivo, list):
            self.nome_mapa = "mapa_teste"
            self.labirinto = mapa_ou_arquivo
        else:
            # Extrai o nome do arquivo sem a extensão
            self.nome_mapa = os.path.basename(mapa_ou_arquivo).split('.')[0]
            self.labirinto = self._carregar_mapa_arquivo(mapa_ou_arquivo)
        
        # Inicializa a posição e direção do agente
        self.posicao_agente = self._localizar_ponto_entrada()
        self.direcao_agente = self._calcular_orientacao_inicial()
        self.objeto_coletado = False
        
        # Verifica se o labirinto é válido
        self._validar_integridade_mapa()
    
    def _carregar_mapa_arquivo(self, caminho_arquivo: str) -> List[str]:
        """
        Carrega um mapa de labirinto a partir de um arquivo de texto.
        
        Args:
            caminho_arquivo (str): Caminho para o arquivo do mapa
            
        Returns:
            List[str]: Lista de strings representando as linhas do mapa
            
        Raises:
            FileNotFoundError: Se o arquivo não for encontrado
            ValueError: Se o arquivo estiver vazio ou mal formatado
        """
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
                linhas = arquivo.readlines()
            
            # Remove quebras de linha e espaços em branco
            mapa_limpo = [linha.strip() for linha in linhas if linha.strip()]
            
            if not mapa_limpo:
                raise ValueError(f"Arquivo {caminho_arquivo} está vazio ou contém apenas espaços em branco")
            
            print(f"Mapa carregado: {caminho_arquivo}")
            return mapa_limpo
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo de mapa não encontrado: {caminho_arquivo}")
    
    def _localizar_ponto_entrada(self) -> Tuple[int, int]:
        """
        Localiza a posição da entrada no mapa.
        
        Returns:
            Tuple[int, int]: Coordenadas (linha, coluna) da entrada
            
        Raises:
            ValueError: Se não houver entrada ou houver múltiplas entradas
        """
        entradas_encontradas = []
        
        for i, linha in enumerate(self.labirinto):
            for j, caractere in enumerate(linha):
                if caractere == 'E':
                    entradas_encontradas.append((i, j))
        
        if len(entradas_encontradas) == 0:
            raise ValueError("Nenhuma entrada encontrada no mapa (procurando por 'E')")
        elif len(entradas_encontradas) > 1:
            raise ValueError(f"Múltiplas entradas encontradas: {entradas_encontradas}")
        
        entrada = entradas_encontradas[0]
        print(f"Entrada localizada em: {entrada}")
        return entrada
    
    def _calcular_orientacao_inicial(self) -> int:
        """
        Determina a orientação inicial do agente baseada na posição da entrada.
        
        Returns:
            int: Direção inicial (0=Norte, 1=Leste, 2=Sul, 3=Oeste)
        """
        linha, coluna = self.posicao_agente
        
        # Verifica se a entrada está nas bordas do mapa
        if linha == 0:
            return 2  # Sul (agente entra pelo norte)
        elif linha == len(self.labirinto) - 1:
            return 0  # Norte (agente entra pelo sul)
        elif coluna == 0:
            return 1  # Leste (agente entra pelo oeste)
        else:
            return 3  # Oeste (agente entra pelo leste)
    
    def _validar_integridade_mapa(self):
        """
        Valida a integridade e consistência do mapa carregado.
        
        Verifica:
        - Presença de exatamente uma entrada
        - Presença de exatamente um objeto coletável
        - Formato consistente do mapa
        
        Raises:
            ValueError: Se o mapa não atender aos critérios de validação
        """
        # Conta entradas e objetos coletáveis
        contador_entradas = sum(linha.count('E') for linha in self.labirinto)
        contador_objetos = sum(linha.count('H') + linha.count('@') for linha in self.labirinto)
        
        if contador_entradas != 1:
            raise ValueError(f"Mapa deve ter exatamente 1 entrada. Encontradas: {contador_entradas}")
        
        if contador_objetos != 1:
            raise ValueError(f"Mapa deve ter exatamente 1 objeto coletável. Encontrados: {contador_objetos}")
        
        print(f"Validação do mapa concluída: {contador_entradas} entrada(s), {contador_objetos} objeto(s)")
    
    def obter_leituras_sensores_proximidade(self) -> List[str]:
        """
        Obtém as leituras dos sensores de proximidade do agente.
        
        Os sensores detectam o conteúdo das células adjacentes nas direções:
        - Esquerda: Célula à esquerda da direção atual
        - Frente: Célula à frente da direção atual  
        - Direita: Célula à direita da direção atual
        
        Returns:
            List[str]: Lista com 3 elementos: [esquerda, frente, direita]
                      Valores possíveis: "PAREDE", "VAZIO", "HUMANO"
        """
        linha_atual, coluna_atual = self.posicao_agente
        
        # Mapeia direções relativas baseado na orientação do agente
        # 0=Norte, 1=Leste, 2=Sul, 3=Oeste
        direcoes_relativas = {
            0: [(-1, -1), (-1, 0), (-1, 1)],  # Norte: esq, frente, dir
            1: [(-1, 1), (0, 1), (1, 1)],     # Leste: esq, frente, dir  
            2: [(1, 1), (1, 0), (1, -1)],     # Sul: esq, frente, dir
            3: [(1, -1), (0, -1), (-1, -1)]   # Oeste: esq, frente, dir
        }
        
        leituras_sensores = []
        direcoes = direcoes_relativas[self.direcao_agente]
        
        for delta_linha, delta_coluna in direcoes:
            nova_linha = linha_atual + delta_linha
            nova_coluna = coluna_atual + delta_coluna
            
            # Verifica se a posição está dentro dos limites do mapa
            if (0 <= nova_linha < len(self.labirinto) and 
                0 <= nova_coluna < len(self.labirinto[0])):
                
                conteudo_celula = self.labirinto[nova_linha][nova_coluna]
                
                # Identifica o tipo de conteúdo
                if conteudo_celula in ['*', 'X']:  # Suporte aos dois formatos
                    leituras_sensores.append("PAREDE")
                elif conteudo_celula in ['H', '@']:  # Suporte aos dois formatos
                    leituras_sensores.append("HUMANO")
                else:
                    leituras_sensores.append("VAZIO")
            else:
                # Fora dos limites do mapa é considerado parede
                leituras_sensores.append("PAREDE")
        
        return leituras_sensores
    
    def executar_comando_navegacao(self, comando: str):
        """
        Executa um comando de navegação no ambiente.
        
        Comandos suportados:
        - 'A': Avança o agente na direção atual
        - 'G': Gira o agente 90 graus no sentido horário
        - 'P': Coleta objeto se estiver à frente
        - 'E': Ejeta objeto se estiver na saída
        
        Args:
            comando (str): Comando a ser executado
            
        Raises:
            ValueError: Se o comando for inválido ou não puder ser executado
        """
        if comando == 'A':
            print("🚶 Comando: AVANÇAR")
            self._avancar_agente()
        elif comando == 'G':
            print("🔄 Comando: GIRAR")
            self._girar_agente()
        elif comando == 'P':
            print("🤲 Comando: COLETAR")
            self._coletar_objeto()
        elif comando == 'E':
            print("📤 Comando: EJETAR")
            self._ejetar_objeto()
        else:
            raise ValueError(f"Comando inválido: {comando}")
    
    def _avancar_agente(self):
        """
        Move o agente uma célula na direção atual.
        
        Raises:
            ValueError: Se houver colisão com parede
        """
        # Calcula a nova posição baseada na direção atual
        direcoes_movimento = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # Norte, Leste, Sul, Oeste
        delta_linha, delta_coluna = direcoes_movimento[self.direcao_agente]
        
        nova_linha = self.posicao_agente[0] + delta_linha
        nova_coluna = self.posicao_agente[1] + delta_coluna
        
        # Verifica se o movimento é válido
        if (0 <= nova_linha < len(self.labirinto) and 
            0 <= nova_coluna < len(self.labirinto[0]) and 
            self.labirinto[nova_linha][nova_coluna] not in ['*', 'X']):
            
            self.posicao_agente = (nova_linha, nova_coluna)
        else:
            raise ValueError(f"Colisão com parede! Tentativa de mover de {self.posicao_agente} para ({nova_linha}, {nova_coluna})")
    
    def _girar_agente(self):
        """
        Gira o agente 90 graus no sentido horário.
        """
        self.direcao_agente = (self.direcao_agente + 1) % 4
    
    def _coletar_objeto(self):
        """
        Coleta o objeto se estiver à frente do agente.
        
        Raises:
            ValueError: Se não houver objeto à frente ou se já estiver coletado
        """
        leituras = self.obter_leituras_sensores_proximidade()
        
        if len(leituras) >= 2 and leituras[1] == "HUMANO":  # Sensor da frente
            # Mapeia direção da frente baseado na orientação do agente
            direcoes_frente = {
                0: (-1, 0),  # Norte
                1: (0, 1),   # Leste
                2: (1, 0),   # Sul
                3: (0, -1)   # Oeste
            }
            
            delta_linha, delta_coluna = direcoes_frente[self.direcao_agente]
            linha_objeto = self.posicao_agente[0] + delta_linha
            coluna_objeto = self.posicao_agente[1] + delta_coluna
            
            if self.labirinto[linha_objeto][coluna_objeto] in ['H', '@']:
                self.objeto_coletado = True
                # Remove o objeto do mapa
                linha_atual = self.labirinto[linha_objeto]
                self.labirinto[linha_objeto] = linha_atual[:coluna_objeto] + ' ' + linha_atual[coluna_objeto + 1:]
                print("Objeto coletado com sucesso!")
            else:
                raise ValueError("Erro ao coletar o objeto")
        else:
            raise ValueError("Tentativa de coleta sem objeto à frente")
    
    def _ejetar_objeto(self):
        """
        Ejeta o objeto se o agente estiver na saída.
        
        Raises:
            ValueError: Se não houver objeto coletado ou não estiver na saída
        """
        if not self.objeto_coletado:
            raise ValueError("Tentativa de ejecção sem objeto coletado!")
        
        if not self._verificar_posicao_saida():
            raise ValueError("Tentativa de ejecção fora da saída!")
        
        self.objeto_coletado = False
        print("Objeto ejetado com sucesso!")
    
    def _verificar_posicao_saida(self) -> bool:
        """
        Verifica se o agente está na posição de saída.
        
        Returns:
            bool: True se estiver na saída, False caso contrário
        """
        linha, coluna = self.posicao_agente
        
        # Verifica se está nas bordas do mapa
        if (linha == 0 or linha == len(self.labirinto) - 1 or 
            coluna == 0 or coluna == len(self.labirinto[0]) - 1):
            return True
        
        return False
    
    def exibir_estado_ambiente(self):
        """
        Exibe o estado atual do ambiente de forma visual.
        
        Mostra o mapa com a posição e orientação do agente representados
        por símbolos visuais.
        """
        print("\nEstado atual do ambiente:")
        print("=" * 50)
        
        # Cria uma cópia do mapa para exibição
        mapa_exibicao = [list(linha) for linha in self.labirinto]
        
        # Marca a posição do agente
        linha_agente, coluna_agente = self.posicao_agente
        simbolos_direcao = ['▲', '►', '▼', '◄']  # Norte, Leste, Sul, Oeste
        mapa_exibicao[linha_agente][coluna_agente] = simbolos_direcao[self.direcao_agente]
        
        # Exibe o mapa
        for linha in mapa_exibicao:
            print(''.join(linha))
        
        # Exibe informações do agente
        print(f"\nPosição do agente: {self.posicao_agente}")
        print(f"Direção do agente: {self.direcao_agente} ({simbolos_direcao[self.direcao_agente]})")
        print(f"Objeto coletado: {'Sim' if self.objeto_coletado else 'Não'}")
        print("=" * 50)