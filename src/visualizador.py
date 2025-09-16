"""
Sistema de Visualização e Animação de Navegação
===============================================

Este módulo implementa um sistema avançado de visualização para gerar
animações e representações visuais do processo de navegação autônoma.
O sistema cria frames sequenciais que são compilados em animações GIF
para análise e demonstração do comportamento do agente.

Funcionalidades principais:
- Geração de frames visuais do estado do ambiente
- Representação gráfica do agente e sua orientação
- Compilação de frames em animações GIF
- Suporte a diferentes tipos de terreno e obstáculos
- Sistema de cores e símbolos para identificação visual

Autor: Sistema de Navegação Inteligente v2.0
Data: 2024
"""

import numpy as np
import matplotlib.pyplot as plt
import imageio
from typing import List, Tuple, Optional

class GeradorVisualizacao:
    """
    Sistema de geração de visualizações e animações de navegação.
    
    Esta classe gerencia a criação de representações visuais do processo
    de navegação, incluindo frames individuais e animações completas.
    Utiliza matplotlib para renderização e imageio para compilação de GIFs.
    
    Atributos:
        labirinto (List[str]): Representação do mapa do ambiente
        frames_animacao (List[np.ndarray]): Lista de frames para animação
        mapeamento_cores (dict): Mapeamento de elementos para cores
        simbolos_orientacao (dict): Símbolos para diferentes orientações
    """
    
    def __init__(self, mapa_ambiente: List[str]):
        """
        Inicializa o gerador de visualizações.
        
        Args:
            mapa_ambiente (List[str]): Representação do mapa do ambiente
        """
        self.labirinto = mapa_ambiente
        self.frames_animacao = []
        
        # Mapeamento de cores para diferentes elementos
        self.mapeamento_cores = {
            'parede': '#2C3E50',      # Azul escuro para paredes
            'espaco_livre': '#ECF0F1', # Cinza claro para espaços livres
            'entrada': '#27AE60',      # Verde para entrada
            'objeto': '#E74C3C',       # Vermelho para objeto
            'agente': '#F39C12',       # Laranja para agente
            'agente_com_carga': '#8E44AD'  # Roxo para agente com carga
        }
        
        # Símbolos para diferentes orientações
        self.simbolos_orientacao = {
            0: '▲',  # Norte
            1: '►',  # Leste
            2: '▼',  # Sul
            3: '◄'   # Oeste
        }
        
        print("Gerador de visualizações inicializado")
    
    def criar_frame(self, 
                   posicao_agente: Tuple[int, int], 
                   orientacao_agente: int, 
                   objeto_coletado: bool):
        """
        Cria um frame visual do estado atual do ambiente.
        
        Args:
            posicao_agente (Tuple[int, int]): Posição atual do agente
            orientacao_agente (int): Orientação atual do agente
            objeto_coletado (bool): Se o objeto foi coletado
        """
        try:
            # Calcula dimensões do mapa
            numero_linhas = len(self.labirinto)
            numero_colunas = max(len(linha) for linha in self.labirinto)
            
            # Cria matriz de visualização
            matriz_visualizacao = np.zeros((numero_linhas, numero_colunas), dtype=int)
            
            # Preenche a matriz com base no mapa
            for i in range(numero_linhas):
                for j in range(numero_colunas):
                    if j < len(self.labirinto[i]):
                        caractere = self.labirinto[i][j]
                        if caractere in ['*', 'X']:
                            matriz_visualizacao[i, j] = 1  # Parede
                        elif caractere == 'E':
                            matriz_visualizacao[i, j] = 2  # Entrada
                        elif caractere in ['H', '@']:
                            matriz_visualizacao[i, j] = 3  # Objeto
                        else:
                            matriz_visualizacao[i, j] = 0  # Espaço livre
                    else:
                        matriz_visualizacao[i, j] = 1  # Parede (preenchimento)
            
            # Marca posição do agente
            linha_agente, coluna_agente = posicao_agente
            if (0 <= linha_agente < numero_linhas and 
                0 <= coluna_agente < numero_colunas):
                if objeto_coletado:
                    matriz_visualizacao[linha_agente, coluna_agente] = 5  # Agente com carga
                else:
                    matriz_visualizacao[linha_agente, coluna_agente] = 4  # Agente sem carga
            
            # Cria figura para visualização
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Define cores para cada tipo de elemento
            cores_elementos = [
                self.mapeamento_cores['espaco_livre'],  # 0 - Espaço livre
                self.mapeamento_cores['parede'],        # 1 - Parede
                self.mapeamento_cores['entrada'],       # 2 - Entrada
                self.mapeamento_cores['objeto'],        # 3 - Objeto
                self.mapeamento_cores['agente'],        # 4 - Agente
                self.mapeamento_cores['agente_com_carga']  # 5 - Agente com carga
            ]
            
            # Cria mapa de cores
            from matplotlib.colors import ListedColormap
            mapa_cores = ListedColormap(cores_elementos)
            
            # Exibe o mapa
            im = ax.imshow(matriz_visualizacao, cmap=mapa_cores, vmin=0, vmax=5)
            
            # Adiciona símbolo de orientação se o agente estiver visível
            if (0 <= linha_agente < numero_linhas and 
                0 <= coluna_agente < numero_colunas):
                simbolo = self.simbolos_orientacao.get(orientacao_agente, '?')
                ax.text(coluna_agente, linha_agente, simbolo, 
                       ha='center', va='center', fontsize=16, 
                       color='white', weight='bold')
            
            # Configurações da visualização
            ax.set_title('Estado do Ambiente de Navegação', fontsize=14, weight='bold')
            ax.set_xlabel('Coluna', fontsize=12)
            ax.set_ylabel('Linha', fontsize=12)
            
            # Adiciona grade para melhor visualização
            ax.set_xticks(range(numero_colunas))
            ax.set_yticks(range(numero_linhas))
            ax.grid(True, alpha=0.3)
            
            # Adiciona legenda
            elementos_legenda = [
                'Espaço Livre', 'Parede', 'Entrada', 'Objeto', 
                'Agente', 'Agente com Carga'
            ]
            cores_legenda = cores_elementos
            
            handles = [plt.Rectangle((0,0),1,1, color=cor) for cor in cores_legenda]
            ax.legend(handles, elementos_legenda, loc='upper right', bbox_to_anchor=(1.3, 1))
            
            # Ajusta layout
            plt.tight_layout()
            
            # Converte para imagem
        fig.canvas.draw()
            buf = fig.canvas.buffer_rgba()
            imagem_frame = np.asarray(buf)
            # Converte RGBA para RGB
            imagem_frame = imagem_frame[:, :, :3]
            self.frames_animacao.append(imagem_frame)
            
            plt.close(fig)  # Libera memória
            
        except Exception as e:
            print(f"Erro ao criar frame de visualização: {e}")
    
    def compilar_animacao_gif(self, nome_arquivo: str = 'animacao_navegacao.gif', 
                             duracao_frame: int = 500):
        """
        Compila os frames em uma animação GIF.
        
        Args:
            nome_arquivo (str): Nome do arquivo GIF a ser gerado
            duracao_frame (int): Duração de cada frame em milissegundos
            
        Returns:
            bool: True se a animação foi gerada com sucesso
        """
        try:
            if not self.frames_animacao:
                print("Nenhum frame disponível para compilar animação")
                return False
            
            # Compila frames em GIF
            imageio.mimsave(nome_arquivo, self.frames_animacao, duration=duracao_frame)
            print(f"Animação GIF salva: {nome_arquivo}")
            print(f"Total de frames: {len(self.frames_animacao)}")
            return True
            
        except Exception as e:
            print(f"Erro ao compilar animação GIF: {e}")
            return False
    
    def salvar_gif(self, nome_arquivo: str = 'animacao_navegacao.gif', 
                   duracao_frame: int = 500):
        """
        Alias para compilar_animacao_gif para compatibilidade.
        
        Args:
            nome_arquivo (str): Nome do arquivo GIF a ser gerado
            duracao_frame (int): Duração de cada frame em milissegundos
            
        Returns:
            bool: True se a animação foi gerada com sucesso
        """
        return self.compilar_animacao_gif(nome_arquivo, duracao_frame)
    
    def obter_estatisticas_visualizacao(self) -> dict:
        """
        Obtém estatísticas da visualização atual.
        
        Returns:
            dict: Dicionário com estatísticas da visualização
        """
        return {
            'total_frames': len(self.frames_animacao),
            'dimensoes_mapa': (len(self.labirinto), max(len(linha) for linha in self.labirinto)),
            'elementos_mapeados': len(self.mapeamento_cores),
            'orientacoes_suportadas': len(self.simbolos_orientacao)
        }
    
    def limpar_frames(self):
        """
        Limpa todos os frames armazenados para liberar memória.
        """
        self.frames_animacao.clear()
        print("Frames de visualização limpos")

# Alias para compatibilidade com código existente
Visualizador = GeradorVisualizacao