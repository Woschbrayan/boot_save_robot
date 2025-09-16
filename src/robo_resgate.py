"""
Sistema de Navegação Inteligente para Resgate Autônomo
======================================================

Este módulo implementa um sistema de navegação inteligente que utiliza
algoritmos de busca e exploração para localizar e resgatar objetos em
ambientes complexos. O sistema combina múltiplas estratégias de navegação
incluindo busca heurística e exploração baseada em sensores.

Funcionalidades principais:
- Navegação autônoma com múltiplas estratégias
- Algoritmo de busca A* para planejamento de caminho
- Exploração baseada em sensores de proximidade
- Sistema de validação e monitoramento de segurança
- Integração com sistema de logging e visualização

Autor: Sistema de Navegação Inteligente v2.0
Data: 2024
"""

from .astar_labirinto import busca_astar
# from .visualizador import Visualizador  # Removido para não gerar GIFs
from .explorador_simples import ExploradorSimples
from .sistema_audio import SistemaEfeitosSonoros
import time
from typing import List, Tuple, Optional, Set

class AgenteNavegacaoInteligente:
    """
    Classe principal para navegação inteligente e resgate autônomo.
    
    Esta classe implementa um agente autônomo capaz de navegar em ambientes
    complexos, localizar objetos de interesse e executar operações de resgate.
    O agente utiliza múltiplas estratégias de navegação adaptadas ao contexto.
    
    Atributos:
        ambiente (AmbienteNavegacao): Simulador do ambiente de navegação
        sistema_log (SistemaLog): Sistema de registro de atividades
        caminho_planejado (List[Tuple[int, int]]): Caminho calculado para navegação
        mapa_explorado (Set[Tuple[int, int]]): Conjunto de posições já exploradas
        pilha_navegacao (List[Tuple[int, int]]): Pilha para navegação em profundidade
        posicao_objeto (Optional[Tuple[int, int]]): Posição do objeto a ser resgatado
        representacao_mapa (List[List[str]]): Representação do mapa para algoritmos
        # gerador_visualizacao (Visualizador): Gerador de visualizações do processo  # Removido para não gerar GIFs
        explorador_ambiente (ExploradorSimples): Sistema de exploração por sensores
    """
    
    def __init__(self, ambiente, sistema_log=None):
        """
        Inicializa o agente de navegação inteligente.
        
        Args:
            ambiente: Objeto simulador do ambiente de navegação
            sistema_log: Sistema de registro de atividades (opcional)
        """
        self.ambiente = ambiente
        self.sistema_log = sistema_log
        self.caminho_planejado = []
        self.mapa_explorado = set()
        self.pilha_navegacao = []
        self.posicao_objeto = None
        self.representacao_mapa = self._construir_representacao_mapa()
        # self.gerador_visualizacao = Visualizador(ambiente.labirinto)  # Removido para não gerar GIFs
        self.explorador_ambiente = ExploradorSimples(ambiente, sistema_log)
        
        # Sistema de efeitos sonoros
        self.sistema_audio = SistemaEfeitosSonoros(volume=0.5, habilitado=True)
        
        # Toca som de inicialização
        self.sistema_audio.som_inicializacao()
    
    def _construir_representacao_mapa(self) -> List[List[str]]:
        """
        Constrói uma representação do mapa adequada para algoritmos de busca.
        
        Esta representação normaliza o mapa para garantir que todas as linhas
        tenham o mesmo comprimento, preenchendo com paredes quando necessário.
        
        Returns:
            List[List[str]]: Matriz representando o mapa normalizado
        """
        # Calcula dimensões do mapa
        numero_linhas = len(self.ambiente.labirinto)
        numero_colunas = max(len(linha) for linha in self.ambiente.labirinto)
        
        # Constrói matriz normalizada
        mapa_normalizado = []
        for i in range(numero_linhas):
            linha_mapa = []
            for j in range(numero_colunas):
                if j < len(self.ambiente.labirinto[i]):
                    if self.ambiente.labirinto[i][j] in ['*', 'X']:
                        linha_mapa.append('*')
                    else:
                        linha_mapa.append(' ')
                else:
                    linha_mapa.append('*')  # Preenche com parede se necessário
            mapa_normalizado.append(linha_mapa)
        
        print("Representação do mapa construída:")
        for linha in mapa_normalizado:
            print(''.join(linha))
        
        return mapa_normalizado
    
    def executar_missao_resgate(self):
        """
        Executa a missão completa de resgate de objeto.
        
        Esta função coordena todo o processo de resgate, incluindo:
        1. Exploração do ambiente para localizar o objeto
        2. Coleta do objeto quando encontrado
        3. Retorno à saída com o objeto
        4. Ejecção do objeto na saída
        
        Raises:
            ValueError: Se a missão não puder ser completada
        """
        try:
            print("Iniciando missão de resgate...")
            print(f"Posição inicial do agente: {self.ambiente.posicao_agente}")
            print(f"Direção inicial do agente: {self.ambiente.direcao_agente}")
            print("Representação do mapa para algoritmos:")
            for linha in self.ambiente.labirinto:
                print(linha)

            # Registra início da missão
            if self.sistema_log:
                leituras_iniciais = self.ambiente.obter_leituras_sensores_proximidade()
                self.sistema_log.registrar_atividade('LIGAR', self.ambiente.posicao_agente, self.ambiente.direcao_agente, 
                                        leituras_iniciais, 'SEM CARGA')
            
            self.ambiente.exibir_estado_ambiente()
            # self.gerador_visualizacao.criar_frame(self.ambiente.posicao_agente, self.ambiente.direcao_agente, self.ambiente.objeto_coletado)  # Removido para não gerar GIFs
            
            # Busca o objeto usando exploração por sensores
            caminho_encontrado = self._buscar_objeto_por_exploracao()
            if caminho_encontrado is None:
                raise ValueError("Não foi possível encontrar um caminho para o objeto")
            
            # Coleta o objeto
            self._coletar_objeto_detectado()
            self.ambiente.exibir_estado_ambiente()
            # self.gerador_visualizacao.criar_frame(self.ambiente.posicao_agente, self.ambiente.direcao_agente, self.ambiente.objeto_coletado)  # Removido para não gerar GIFs
            
            # Validações após coleta do objeto
            self._validar_estado_pos_coleta()
            
            # Se o objeto foi coletado, retorna à saída
            if self.ambiente.objeto_coletado:
                if self.sistema_log:
                    self.sistema_log.registrar_atividade('INFO', self.ambiente.posicao_agente, self.ambiente.direcao_agente, 
                                            ['Objeto coletado, retornando à saída'], 'COM CARGA')
                
                # Retorna à saída (já inclui ejecção do objeto)
                caminho_retorno = self._retornar_a_saida()
                if caminho_retorno:
                    if self.sistema_log:
                        self.sistema_log.registrar_atividade('INFO', self.ambiente.posicao_agente, self.ambiente.direcao_agente, 
                                                [f"Caminho de retorno executado: {len(caminho_retorno)} posições"], 'SEM CARGA')
                self.ambiente.exibir_estado_ambiente()
                # self.gerador_visualizacao.criar_frame(self.ambiente.posicao_agente, self.ambiente.direcao_agente, self.ambiente.objeto_coletado)  # Removido para não gerar GIFs
            
            print("Missão de resgate concluída com sucesso!")
            
            # Toca som de missão concluída
            self.sistema_audio.som_missao_concluida()

        except Exception as e:
            if self.sistema_log:
                self.sistema_log.registrar_atividade('ERRO', self.ambiente.posicao_agente, self.ambiente.direcao_agente, 
                                        [str(e)], 'SEM CARGA' if not self.ambiente.objeto_coletado else 'COM CARGA')
            raise
        finally:
            # self.gerador_visualizacao.salvar_gif(f'animacao_agente_{self.ambiente.nome_mapa}.gif')  # Removido para não gerar GIFs
            pass
    
    def _buscar_objeto_por_exploracao(self) -> Optional[List[Tuple[int, int]]]:
        """
        Busca o objeto no ambiente usando apenas sensores de proximidade.
        
        Esta estratégia não requer conhecimento prévio do mapa e simula
        a navegação real de um agente com sensores limitados.
        
        Returns:
            Optional[List[Tuple[int, int]]]: Caminho até o objeto ou None se não encontrado
        """
        print("Iniciando busca por exploração de sensores...")
        
        # Explora o ambiente até encontrar o objeto
        if not self.explorador_ambiente.explorar_ate_encontrar_objeto():
            if self.sistema_log:
                self.sistema_log.registrar_atividade('ERRO', self.ambiente.posicao_agente, self.ambiente.direcao_agente, 
                                        ['Objeto não encontrado durante exploração'], 'SEM CARGA')
            return None

        print("Objeto encontrado por exploração!")
        
        # Toca som de descoberta
        self.sistema_audio.som_descoberta()
        
        self.posicao_objeto = self.explorador_ambiente.posicao_objeto
        
        # Retorna um caminho simples (apenas a posição atual)
        return [self.ambiente.posicao_agente]
    
    def _buscar_objeto_por_astar(self) -> Optional[List[Tuple[int, int]]]:
        """
        Busca o objeto usando algoritmo A* (método alternativo).
        
        Esta estratégia utiliza conhecimento completo do mapa para
        calcular o caminho ótimo até o objeto.
        
        Returns:
            Optional[List[Tuple[int, int]]]: Caminho ótimo até o objeto ou None se não encontrado
        """
        posicao_inicial = self.ambiente.posicao_agente
        posicao_objeto = self._localizar_objeto_no_mapa()
        
        if posicao_objeto is None:
            if self.sistema_log:
                self.sistema_log.registrar_atividade('ERRO', self.ambiente.posicao_agente, self.ambiente.direcao_agente, 
                                        ['Objeto não encontrado no mapa'], 'SEM CARGA')
            return None

        self.caminho_planejado = busca_astar(self.representacao_mapa, posicao_inicial, posicao_objeto)
        print(f"Caminho encontrado pelo A*: {self.caminho_planejado}")
        
        if self.caminho_planejado is None:
            if self.sistema_log:
                self.sistema_log.registrar_atividade('ERRO', self.ambiente.posicao_agente, self.ambiente.direcao_agente, 
                                        ['Caminho para o objeto não encontrado'], 'SEM CARGA')
            return None

        # Executa o caminho até encontrar o objeto
        for i in range(1, len(self.caminho_planejado)):
            if self._verificar_objeto_adjacente():
                self.posicao_objeto = posicao_objeto
                return self.caminho_planejado[:i+1]
            self._navegar_para_posicao(self.caminho_planejado[i])
        
        self.posicao_objeto = posicao_objeto
        return self.caminho_planejado
    
    def _navegar_para_posicao(self, posicao_destino: Tuple[int, int]):
        """
        Navega o agente para uma posição específica.
        
        Args:
            posicao_destino (Tuple[int, int]): Coordenadas de destino
        """
        posicao_atual = self.ambiente.posicao_agente
        delta_linha = posicao_destino[0] - posicao_atual[0]
        delta_coluna = posicao_destino[1] - posicao_atual[1]
        
        # Determina a direção necessária
        if delta_linha == 1:
            direcao_destino = 2  # Sul
        elif delta_linha == -1:
            direcao_destino = 0  # Norte
        elif delta_coluna == 1:
            direcao_destino = 1  # Leste
        elif delta_coluna == -1:
            direcao_destino = 3  # Oeste
        else:
            return  # Já está na posição
        
        self._ajustar_orientacao_agente(direcao_destino)
        print(f"🤖 Robô avançando de {posicao_atual} para {posicao_destino}")
        
        # Toca som de movimento
        self.sistema_audio.som_movimento()
        
        time.sleep(1)  # Pausa de 1 segundo para visualização
        self.ambiente.executar_comando_navegacao('A')
        self.ambiente.exibir_estado_ambiente()
        time.sleep(1)  # Pausa após movimento
    
    def _ajustar_orientacao_agente(self, direcao_desejada: int):
        """
        Ajusta a orientação do agente para a direção especificada.
        
        Args:
            direcao_desejada (int): Direção alvo (0=Norte, 1=Leste, 2=Sul, 3=Oeste)
        """
        while self.ambiente.direcao_agente != direcao_desejada:
            # Toca som de rotação
            self.sistema_audio.som_rotacao()
            
            self.ambiente.executar_comando_navegacao('G')
        print(f"Orientação ajustada para {self.ambiente.direcao_agente}")
    
    def _verificar_objeto_adjacente(self) -> bool:
        """
        Verifica se o objeto está à frente do agente.
        
        Returns:
            bool: True se o objeto estiver à frente, False caso contrário
        """
        leituras = self.ambiente.obter_leituras_sensores_proximidade()
        return len(leituras) >= 2 and leituras[1] == "HUMANO"  # Sensor da frente
    
    def _localizar_objeto_no_mapa(self) -> Optional[Tuple[int, int]]:
        """
        Localiza a posição do objeto no mapa.
        
        Returns:
            Optional[Tuple[int, int]]: Coordenadas do objeto ou None se não encontrado
        """
        for i, linha in enumerate(self.ambiente.labirinto):
            for j, caractere in enumerate(linha):
                if caractere in ['H', '@']:
                    return (i, j)
        
        if self.sistema_log:
            self.sistema_log.registrar_atividade('ERRO', self.ambiente.posicao_agente, self.ambiente.direcao_agente, 
                                      ['Objeto não encontrado no mapa'], 'SEM CARGA')
        return None
    
    def _coletar_objeto_detectado(self):
        """
        Coleta o objeto se estiver à frente do agente.
        """
        if self._verificar_objeto_adjacente():
            # O objeto já está à frente, pode coletar diretamente
            
            # Toca som de coleta
            self.sistema_audio.som_coleta()
            
            self.ambiente.executar_comando_navegacao('P')
            if self.sistema_log:
                self.sistema_log.registrar_atividade('INFO', self.ambiente.posicao_agente, self.ambiente.direcao_agente, 
                                          ['Objeto coletado'], 'COM CARGA')
        else:
            if self.sistema_log:
                self.sistema_log.registrar_atividade('ERRO', self.ambiente.posicao_agente, self.ambiente.direcao_agente, 
                                          ['Tentativa de coletar objeto sem estar à frente'], 'SEM CARGA')
    
    def _retornar_a_saida(self) -> Optional[List[Tuple[int, int]]]:
        """
        Retorna à saída do ambiente após coletar o objeto.
        
        Returns:
            Optional[List[Tuple[int, int]]]: Caminho até a saída ou None se não encontrado
        """
        posicao_inicial = self.ambiente.posicao_agente
        posicao_saida = self._localizar_saida()
        
        if posicao_inicial == posicao_saida:
            # O agente já está na saída
            self.ambiente.executar_comando_navegacao('E')
            return [posicao_inicial]
        
        # Calcula caminho de retorno usando A*
        caminho_retorno = busca_astar(self.representacao_mapa, posicao_inicial, posicao_saida)
        
        if caminho_retorno is None:
            if self.sistema_log:
                self.sistema_log.registrar_atividade('ERRO', self.ambiente.posicao_agente, self.ambiente.direcao_agente, 
                                          ['Caminho de retorno não encontrado'], 'COM CARGA')
            return None

        # Executa navegação de retorno com tratamento de erro
        try:
            self._executar_sequencia_navegacao(caminho_retorno)
            # Verifica se chegou à saída antes de ejectar
            if self.ambiente.posicao_agente == posicao_saida:
                self.ambiente.executar_comando_navegacao('E')
            else:
                print(f"⚠️ Não chegou à saída esperada. Posição atual: {self.ambiente.posicao_agente}, Saída: {posicao_saida}")
        except Exception as e:
            print(f"⚠️ Erro durante navegação de retorno: {e}")
            # Tenta ejectar mesmo assim se estiver próximo da saída
            try:
                self.ambiente.executar_comando_navegacao('E')
            except:
                pass
        
        return caminho_retorno
    
    def _localizar_saida(self) -> Optional[Tuple[int, int]]:
        """
        Localiza a posição da saída no ambiente.
        
        Returns:
            Optional[Tuple[int, int]]: Coordenadas da saída ou None se não encontrada
        """
        # Encontra o tamanho máximo das colunas
        max_colunas = max(len(linha) for linha in self.ambiente.labirinto)
        
        # Verifica bordas esquerda e direita
        for i in range(len(self.ambiente.labirinto)):
            linha = self.ambiente.labirinto[i]
            if len(linha) > 0 and linha[0] == 'E':
                return (i, 0)
            if len(linha) > 0 and linha[-1] == 'E':
                return (i, len(linha) - 1)
        
        # Verifica bordas superior e inferior
        for j in range(max_colunas):
            if len(self.ambiente.labirinto[0]) > j and self.ambiente.labirinto[0][j] == 'E':
                return (0, j)
            ultima_linha = self.ambiente.labirinto[-1]
            if len(ultima_linha) > j and ultima_linha[j] == 'E':
                return (len(self.ambiente.labirinto) - 1, j)
        
        return None

    def _validar_estado_pos_coleta(self):
        """
        Valida o estado do agente após coletar o objeto.
        
        Verifica se não está em beco sem saída e se os sensores funcionam corretamente.
        """
        if not self.ambiente.objeto_coletado:
            return
        
        leituras = self.ambiente.obter_leituras_sensores_proximidade()
        
        # Validação 1: Verifica se os 3 sensores não veem paredes simultaneamente
        if len(leituras) >= 3 and all(leitura == "PAREDE" for leitura in leituras):
            mensagem = "ALARME: Todos os 3 sensores veem paredes simultaneamente após coleta!"
            print(f"⚠️ {mensagem}")
            if self.sistema_log:
                self.sistema_log.registrar_atividade('ALARME', self.ambiente.posicao_agente, self.ambiente.direcao_agente, 
                                        leituras, 'COM CARGA')
            raise ValueError(mensagem)
        
        # Validação 2: Verifica se o agente não está em beco sem saída
        espacos_livres = sum(1 for leitura in leituras if leitura == "VAZIO")
        if espacos_livres == 0:
            mensagem = "ALARME: Agente em beco sem saída após coletar objeto!"
            print(f"⚠️ {mensagem}")
            if self.sistema_log:
                self.sistema_log.registrar_atividade('ALARME', self.ambiente.posicao_agente, self.ambiente.direcao_agente, 
                                        leituras, 'COM CARGA')
            raise ValueError(mensagem)
        
        # Validação 3: Verifica se pelo menos um sensor está funcionando
        if len(leituras) != 3:
            mensagem = "ALARME: Número incorreto de leituras dos sensores!"
            print(f"⚠️ {mensagem}")
            if self.sistema_log:
                self.sistema_log.registrar_atividade('ALARME', self.ambiente.posicao_agente, self.ambiente.direcao_agente, 
                                        leituras, 'COM CARGA')
            raise ValueError(mensagem)
        
        print(f"✅ Validações passaram: {espacos_livres} espaços livres detectados")
    
    def _executar_sequencia_navegacao(self, sequencia_posicoes: List[Tuple[int, int]]):
        """
        Executa uma sequência de navegação através de posições específicas.
        
        Args:
            sequencia_posicoes (List[Tuple[int, int]]): Lista de posições para navegar
        """
        if not sequencia_posicoes:
            return
            
        # Pula a primeira posição (posição atual)
        for i in range(1, len(sequencia_posicoes)):
            try:
                self._navegar_para_posicao(sequencia_posicoes[i])
            except Exception as e:
                print(f"Erro ao navegar para posição {sequencia_posicoes[i]}: {e}")
                # Se há erro, tenta a próxima posição
                continue
    
    def _ejetar_objeto_na_saida(self):
        """
        Ejeta o objeto na saída do ambiente.
        """
        try:
            # Toca som de ejeção
            self.sistema_audio.som_ejecao()
            
            self.ambiente.executar_comando_navegacao('E')
            if self.sistema_log:
                self.sistema_log.registrar_atividade('INFO', self.ambiente.posicao_agente, self.ambiente.direcao_agente, 
                                          ['Objeto ejetado na saída'], 'SEM CARGA')
        except ValueError as e:
            # Objeto já foi ejetado
            print(f"Objeto já foi ejetado: {e}")
    
    def executar_comando_individual(self, comando: str):
        """
        Executa um comando individual e registra o resultado.
        
        Args:
            comando (str): Comando a ser executado
        """
        posicao_antes = self.ambiente.posicao_agente
        direcao_antes = self.ambiente.direcao_agente
        
        try:
            self.ambiente.executar_comando_navegacao(comando)
            
            if self.sistema_log:
                leituras = self.ambiente.obter_leituras_sensores_proximidade()
                estado_carga = 'COM CARGA' if self.ambiente.objeto_coletado else 'SEM CARGA'
                self.sistema_log.registrar_atividade(comando, posicao_antes, direcao_antes, leituras, estado_carga)
            
            print(f"Comando executado: {comando}")
            print(f"Posição antes: {posicao_antes}, Direção antes: {direcao_antes}")
            print(f"Posição depois: {self.ambiente.posicao_agente}, Direção depois: {self.ambiente.direcao_agente}")
            
        except Exception as e:
            if self.sistema_log:
                leituras = self.ambiente.obter_leituras_sensores_proximidade()
                estado_carga = 'COM CARGA' if self.ambiente.objeto_coletado else 'SEM CARGA'
                self.sistema_log.registrar_atividade('ERRO', posicao_antes, direcao_antes, [str(e)], estado_carga)
            raise