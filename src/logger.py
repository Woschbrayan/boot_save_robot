"""
Sistema de Registro e Monitoramento de Atividades
=================================================

Este módulo implementa um sistema abrangente de logging para monitoramento
e auditoria de atividades de navegação autônoma.

Autor: Sistema de Navegação Inteligente v2.0
Data: 2024
"""

import csv
import os
from datetime import datetime
from typing import List, Tuple, Optional

class SistemaLog:
    def __init__(self, identificador_sessao: str):
        """
        Inicializa o sistema de logging.
        
        Args:
            identificador_sessao (str): Identificador único para a sessão de log
        """
        # Cria diretório de logs se não existir
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # Gera timestamp para a sessão
        self.timestamp_sessao = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Constrói nome do arquivo
        self.nome_arquivo = f"logs/{identificador_sessao}_{self.timestamp_sessao}.csv"
        
        # Inicializa o arquivo de log
        self._inicializar_arquivo_log()
        
        print(f"Sistema de log inicializado: {self.nome_arquivo}")

    def _inicializar_arquivo_log(self):
        """
        Inicializa o arquivo de log com cabeçalho apropriado.
        """
        with open(self.nome_arquivo, 'w', newline='', encoding='utf-8') as arquivo:
            escritor_csv = csv.writer(arquivo)
            # Cabeçalho do arquivo de log
            escritor_csv.writerow([
                'Comando', 
                'Sensor Esquerdo', 
                'Sensor Frente', 
                'Sensor Direito', 
                'Compartimento'
            ])

    def registrar_atividade(self, 
                          comando: str, 
                          posicao: Tuple[int, int], 
                          direcao: int, 
                          leituras_sensores: List[str], 
                          estado_compartimento: str):
        """
        Registra uma atividade no sistema de log.
        
        Args:
            comando (str): Comando executado ou tipo de evento
            posicao (Tuple[int, int]): Posição do agente (linha, coluna)
            direcao (int): Direção atual do agente
            leituras_sensores (List[str]): Leituras dos sensores de proximidade
            estado_compartimento (str): Estado do compartimento de carga
        """
        with open(self.nome_arquivo, 'a', newline='', encoding='utf-8') as arquivo:
            escritor_csv = csv.writer(arquivo)
            # Formato do registro: Comando, Sensor Esquerdo, Sensor Frente, Sensor Direito, Compartimento
            escritor_csv.writerow([comando] + leituras_sensores + [estado_compartimento])
    
    def obter_estatisticas_sessao(self) -> dict:
        """
        Obtém estatísticas da sessão de log atual.
        
        Returns:
            dict: Dicionário com estatísticas da sessão
        """
        try:
            with open(self.nome_arquivo, 'r', encoding='utf-8') as arquivo:
                leitor_csv = csv.reader(arquivo)
                linhas = list(leitor_csv)
            
            # Remove cabeçalho
            dados = linhas[1:] if len(linhas) > 1 else []
            
            # Calcula estatísticas
            total_registros = len(dados)
            comandos_executados = len([linha for linha in dados if linha[0] not in ['INFO', 'ERRO', 'ALARME']])
            erros_registrados = len([linha for linha in dados if linha[0] == 'ERRO'])
            alarmes_registrados = len([linha for linha in dados if linha[0] == 'ALARME'])
            
            return {
                'total_registros': total_registros,
                'comandos_executados': comandos_executados,
                'erros_registrados': erros_registrados,
                'alarmes_registrados': alarmes_registrados,
                'timestamp_sessao': self.timestamp_sessao,
                'arquivo_log': self.nome_arquivo
            }
            
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            return {}

# Alias para compatibilidade com código existente
Logger = SistemaLog