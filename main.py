"""
Sistema de Navegação Autônoma - Interface Principal
===================================================

Este é o ponto de entrada principal do Sistema de Navegação Autônoma,
um sistema avançado para navegação e resgate em ambientes complexos.
O sistema oferece uma interface interativa para seleção de mapas
e execução de missões de navegação autônoma.

Funcionalidades principais:
- Interface de usuário interativa
- Seleção de mapas de ambiente
- Execução de missões de navegação
- Visualização de resultados
- Sistema de logging integrado

Autor: Sistema de Navegação Inteligente v2.0
Data: 2024
"""

import os
import sys
from typing import List, Optional

# Adiciona o diretório src ao path para importações
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.simulador_labirinto import AmbienteNavegacao
from src.robo_resgate import AgenteNavegacaoInteligente
from src.logger import SistemaLog

def exibir_titulo_sistema():
    """
    Exibe o título e informações do sistema.
    """
    print("=" * 80)
    print("🚀 SISTEMA DE NAVEGAÇÃO AUTÔNOMA v2.0 🚀")
    print("=" * 80)
    print("Sistema Avançado de Navegação e Resgate em Ambientes Complexos")
    print("Desenvolvido com algoritmos de inteligência artificial")
    print("=" * 80)
    print()

def listar_mapas_disponiveis() -> List[str]:
    """
    Lista todos os mapas disponíveis no diretório de mapas.
    
    Returns:
        List[str]: Lista de nomes de arquivos de mapa
    """
    diretorio_mapas = "mapas"
    
    if not os.path.exists(diretorio_mapas):
        print(f"❌ Diretório de mapas não encontrado: {diretorio_mapas}")
        return []
    
    arquivos_mapas = []
    for arquivo in os.listdir(diretorio_mapas):
        if arquivo.endswith('.txt'):
            arquivos_mapas.append(arquivo)
    
    arquivos_mapas.sort()  # Ordena alfabeticamente
    
    if not arquivos_mapas:
        print(f"❌ Nenhum mapa encontrado no diretório: {diretorio_mapas}")
        return []
    
    return arquivos_mapas

def exibir_menu_principal():
    """
    Exibe o menu principal do sistema.
    """
    print("📋 MENU PRINCIPAL")
    print("-" * 40)
    print("1. Executar Missão de Navegação")
    print("2. Visualizar Mapas Disponíveis")
    print("3. Informações do Sistema")
    print("4. Sair")
    print("-" * 40)

def exibir_informacoes_sistema():
    """
    Exibe informações detalhadas sobre o sistema.
    """
    print("\n🔍 INFORMAÇÕES DO SISTEMA")
    print("=" * 50)
    print("Versão: 2.0")
    print("Autor: Sistema de Navegação Inteligente")
    print("Data: 2024")
    print()
    print("📊 CARACTERÍSTICAS:")
    print("• Algoritmo de busca A* para planejamento de caminho")
    print("• Exploração baseada em sensores de proximidade")
    print("• Sistema de validação e monitoramento de segurança")
    print("• Geração de animações GIF do processo")
    print("• Sistema de logging abrangente")
    print("• Interface interativa amigável")
    print()
    print("🎯 FUNCIONALIDADES:")
    print("• Navegação autônoma em ambientes complexos")
    print("• Localização e coleta de objetos")
    print("• Retorno seguro à saída")
    print("• Validações de integridade do sistema")
    print("• Relatórios detalhados de missão")
    print("=" * 50)

def selecionar_mapa_interativo() -> Optional[str]:
    """
    Permite ao usuário selecionar um mapa de forma interativa.
    
    Returns:
        Optional[str]: Caminho do mapa selecionado ou None se cancelado
    """
    mapas_disponiveis = listar_mapas_disponiveis()
    
    if not mapas_disponiveis:
        return None
    
    print("\n🗺️  MAPAS DISPONÍVEIS:")
    print("-" * 40)
    
    for i, mapa in enumerate(mapas_disponiveis, 1):
        print(f"{i}. {mapa}")
    
    print(f"{len(mapas_disponiveis) + 1}. Voltar ao menu principal")
    print("-" * 40)
    
    while True:
        try:
            escolha = input("Digite o número do mapa desejado: ").strip()
            
            if not escolha:
                print("❌ Por favor, digite um número válido.")
                continue
            
            numero_escolha = int(escolha)
            
            if 1 <= numero_escolha <= len(mapas_disponiveis):
                mapa_selecionado = mapas_disponiveis[numero_escolha - 1]
                caminho_mapa = os.path.join("mapas", mapa_selecionado)
                print(f"✅ Mapa selecionado: {mapa_selecionado}")
                return caminho_mapa
            
            elif numero_escolha == len(mapas_disponiveis) + 1:
                return None
            
            else:
                print(f"❌ Número inválido. Digite um número entre 1 e {len(mapas_disponiveis) + 1}.")
        
        except ValueError:
            print("❌ Por favor, digite um número válido.")
        except KeyboardInterrupt:
            print("\n\n👋 Operação cancelada pelo usuário.")
            return None

def executar_missao_navegacao(caminho_mapa: str):
    """
    Executa uma missão completa de navegação.
    
    Args:
        caminho_mapa (str): Caminho para o arquivo do mapa
    """
    try:
        print(f"\n🚀 INICIANDO MISSÃO DE NAVEGAÇÃO")
        print("=" * 50)
        print(f"Mapa: {os.path.basename(caminho_mapa)}")
        print("=" * 50)
        
        # Inicializa componentes do sistema
        print("🔧 Inicializando componentes do sistema...")
        
        # Cria ambiente de navegação
        ambiente = AmbienteNavegacao(caminho_mapa)
        print("✅ Ambiente de navegação inicializado")
        
        # Cria sistema de logging
        nome_mapa = os.path.basename(caminho_mapa).split('.')[0]
        sistema_log = SistemaLog(f"missao_{nome_mapa}")
        print("✅ Sistema de logging inicializado")
        
        # Cria agente de navegação
        agente = AgenteNavegacaoInteligente(ambiente, sistema_log)
        print("✅ Agente de navegação inicializado")
        
        print("\n🎯 Executando missão...")
        print("-" * 30)
        
        # Executa a missão
        agente.executar_missao_resgate()
        
        print("\n🎉 MISSÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 50)
        
        # Exibe estatísticas finais
        estatisticas = sistema_log.obter_estatisticas_sessao()
        if estatisticas:
            print("📊 ESTATÍSTICAS DA MISSÃO:")
            print(f"• Total de registros: {estatisticas.get('total_registros', 0)}")
            print(f"• Comandos executados: {estatisticas.get('comandos_executados', 0)}")
            print(f"• Erros registrados: {estatisticas.get('erros_registrados', 0)}")
            print(f"• Alarmes registrados: {estatisticas.get('alarmes_registrados', 0)}")
            print(f"• Arquivo de log: {estatisticas.get('arquivo_log', 'N/A')}")
        
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ ERRO DURANTE A EXECUÇÃO DA MISSÃO:")
        print(f"Erro: {str(e)}")
        print("\n🔍 Verifique o arquivo de log para mais detalhes.")
    
    finally:
        print("\n⏸️  Pressione Enter para continuar...")
        try:
            input()
        except (EOFError, KeyboardInterrupt):
            pass

def executar_modo_demonstracao():
    """
    Executa uma demonstração automática do sistema.
    """
    print("\n🎬 MODO DEMONSTRAÇÃO")
    print("=" * 40)
    print("Executando demonstração automática...")
    
    # Lista mapas disponíveis
    mapas = listar_mapas_disponiveis()
    
    if not mapas:
        print("❌ Nenhum mapa disponível para demonstração.")
        return
    
    # Seleciona o primeiro mapa disponível
    mapa_demo = mapas[0]
    caminho_mapa = os.path.join("mapas", mapa_demo)
    
    print(f"📋 Mapa selecionado para demonstração: {mapa_demo}")
    
    # Executa a missão
    executar_missao_navegacao(caminho_mapa)

def main():
    """
    Função principal do sistema.
    """
    try:
        # Exibe título do sistema
        exibir_titulo_sistema()
        
        # Loop principal do menu
        while True:
            exibir_menu_principal()
            
            try:
                escolha = input("Digite sua escolha (1-4): ").strip()
                
                if escolha == "1":
                    # Executar missão de navegação
                    mapa_selecionado = selecionar_mapa_interativo()
                    if mapa_selecionado:
                        executar_missao_navegacao(mapa_selecionado)
                
                elif escolha == "2":
                    # Visualizar mapas disponíveis
                    print("\n🗺️  MAPAS DISPONÍVEIS:")
                    print("-" * 40)
                    mapas = listar_mapas_disponiveis()
                    if mapas:
                        for i, mapa in enumerate(mapas, 1):
                            print(f"{i}. {mapa}")
                    else:
                        print("❌ Nenhum mapa encontrado.")
                    print("-" * 40)
                    input("Pressione Enter para continuar...")
                
                elif escolha == "3":
                    # Informações do sistema
                    exibir_informacoes_sistema()
                    input("Pressione Enter para continuar...")
                
                elif escolha == "4":
                    # Sair do sistema
                    print("\n👋 Obrigado por usar o Sistema de Navegação Autônoma!")
                    print("Sistema desenvolvido com tecnologia de ponta.")
                    break
                
                else:
                    print("❌ Opção inválida. Digite um número entre 1 e 4.")
            
            except KeyboardInterrupt:
                print("\n\n👋 Sistema interrompido pelo usuário.")
                break
            except EOFError:
                # Modo não-interativo (para testes automatizados)
                print("\n🤖 Modo não-interativo detectado.")
                executar_modo_demonstracao()
                break
    
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO NO SISTEMA:")
        print(f"Erro: {str(e)}")
        print("\n🔧 Verifique a configuração do sistema e tente novamente.")

if __name__ == "__main__":
    main()