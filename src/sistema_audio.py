"""
Sistema de Efeitos Sonoros para Robô de Salvamento

Este módulo implementa um sistema completo de efeitos sonoros para simular
os sons de um robô real durante suas operações de navegação e resgate.

Funcionalidades:
- Efeitos sonoros sintéticos para diferentes ações do robô
- Sistema de volume e controle de áudio
- Sons para movimento, rotação, coleta e ejeção
- Indicadores visuais de áudio

Autor: Sistema de Navegação Inteligente v2.0
Data: 2024
"""

import numpy as np
import time
import threading
from typing import Optional

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("⚠️  pygame não disponível. Efeitos sonoros desabilitados.")

class SistemaEfeitosSonoros:
    """
    Sistema de efeitos sonoros para simulação de robô.
    
    Gera sons sintéticos para diferentes ações do robô:
    - Movimento: Som de motor e passos
    - Rotação: Som de servo motor
    - Coleta: Som de mecanismo de captura
    - Ejeção: Som de liberação
    - Descoberta: Som de alerta/sucesso
    """
    
    def __init__(self, volume: float = 0.3, habilitado: bool = True):
        """
        Inicializa o sistema de efeitos sonoros.
        
        Args:
            volume (float): Volume dos efeitos (0.0 a 1.0)
            habilitado (bool): Se os efeitos sonoros estão habilitados
        """
        self.volume = max(0.0, min(1.0, volume))
        self.habilitado = habilitado and PYGAME_AVAILABLE
        
        if self.habilitado:
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
                print("🔊 Sistema de efeitos sonoros inicializado")
            except pygame.error:
                print("❌ Erro ao inicializar pygame mixer")
                self.habilitado = False
        else:
            print("🔇 Efeitos sonoros desabilitados")
    
    def _gerar_onda_simples(self, frequencia: float, duracao: float, 
                           tipo_onda: str = 'seno') -> np.ndarray:
        """
        Gera uma onda sonora simples.
        
        Args:
            frequencia (float): Frequência em Hz
            duracao (float): Duração em segundos
            tipo_onda (str): Tipo de onda ('seno', 'quadrada', 'dente_serra')
            
        Returns:
            np.ndarray: Array de áudio
        """
        if not self.habilitado:
            return np.array([])
        
        sample_rate = 22050
        frames = int(duracao * sample_rate)
        arr = np.zeros(frames)
        
        for i in range(frames):
            t = i / sample_rate
            
            if tipo_onda == 'seno':
                arr[i] = np.sin(2 * np.pi * frequencia * t)
            elif tipo_onda == 'quadrada':
                arr[i] = 1 if np.sin(2 * np.pi * frequencia * t) > 0 else -1
            elif tipo_onda == 'dente_serra':
                arr[i] = 2 * (t * frequencia - np.floor(t * frequencia + 0.5))
        
        # Aplica envelope para evitar clicks
        envelope = np.exp(-t * 2)
        arr = arr * envelope * self.volume
        
        return arr
    
    def _gerar_ruido_branco(self, duracao: float, intensidade: float = 0.1) -> np.ndarray:
        """
        Gera ruído branco para efeitos de motor.
        
        Args:
            duracao (float): Duração em segundos
            intensidade (float): Intensidade do ruído (0.0 a 1.0)
            
        Returns:
            np.ndarray: Array de áudio
        """
        if not self.habilitado:
            return np.array([])
        
        sample_rate = 22050
        frames = int(duracao * sample_rate)
        arr = np.random.normal(0, intensidade, frames)
        
        # Aplica envelope
        t = np.linspace(0, duracao, frames)
        envelope = np.exp(-t * 3)
        arr = arr * envelope * self.volume
        
        return arr
    
    def _tocar_som(self, arr: np.ndarray):
        """
        Toca um array de áudio usando pygame.
        
        Args:
            arr (np.ndarray): Array de áudio para tocar
        """
        if not self.habilitado or len(arr) == 0:
            return
        
        try:
            # Converte para formato pygame
            arr_int16 = (arr * 32767).astype(np.int16)
            sound = pygame.sndarray.make_sound(arr_int16)
            sound.play()
        except Exception as e:
            print(f"⚠️  Erro ao tocar som: {e}")
    
    def som_movimento(self):
        """
        Toca som de movimento do robô (motor + passos).
        """
        if not self.habilitado:
            print("🔊 [SOM] Movimento do robô")
            return
        
        # Gera som de motor (ruído de baixa frequência)
        motor = self._gerar_ruido_branco(0.3, 0.15)
        
        # Gera som de passo (onda quadrada de alta frequência)
        passo = self._gerar_onda_simples(800, 0.1, 'quadrada')
        
        # Combina os sons
        som_completo = np.concatenate([motor, passo])
        self._tocar_som(som_completo)
        print("🔊 [SOM] Movimento do robô")
    
    def som_rotacao(self):
        """
        Toca som de rotação do robô (servo motor).
        """
        if not self.habilitado:
            print("🔊 [SOM] Rotação do robô")
            return
        
        # Som de servo motor (onda senoidal com frequência variável)
        t = np.linspace(0, 0.4, int(0.4 * 22050))
        frequencia = 200 + 100 * np.sin(2 * np.pi * 5 * t)  # Varia entre 100-300 Hz
        som = np.sin(2 * np.pi * frequencia * t) * np.exp(-t * 2)
        
        # Adiciona ruído característico de servo
        ruido = self._gerar_ruido_branco(0.4, 0.05)
        som_completo = (som + ruido) * self.volume
        
        self._tocar_som(som_completo)
        print("🔊 [SOM] Rotação do robô")
    
    def som_coleta(self):
        """
        Toca som de coleta do humano (mecanismo de captura).
        """
        if not self.habilitado:
            print("🔊 [SOM] Coleta do humano")
            return
        
        # Som de mecanismo (sequência de cliques)
        som_total = np.array([])
        
        for i in range(3):
            # Som de clique (onda quadrada curta)
            clique = self._gerar_onda_simples(1200 + i * 200, 0.05, 'quadrada')
            som_total = np.concatenate([som_total, clique, np.zeros(int(0.05 * 22050))])
        
        # Som final de confirmação
        confirmacao = self._gerar_onda_simples(800, 0.2, 'seno')
        som_total = np.concatenate([som_total, confirmacao])
        
        self._tocar_som(som_total)
        print("🔊 [SOM] Coleta do humano")
    
    def som_ejecao(self):
        """
        Toca som de ejeção do humano (mecanismo de liberação).
        """
        if not self.habilitado:
            print("🔊 [SOM] Ejeção do humano")
            return
        
        # Som de ejeção (som descendente)
        t = np.linspace(0, 0.5, int(0.5 * 22050))
        frequencia = 600 * np.exp(-t * 3)  # Frequência decresce
        som = np.sin(2 * np.pi * frequencia * t)
        
        # Adiciona som de "whoosh"
        whoosh = self._gerar_ruido_branco(0.5, 0.2) * np.exp(-t * 2)
        som_completo = (som + whoosh) * self.volume
        
        self._tocar_som(som_completo)
        print("🔊 [SOM] Ejeção do humano")
    
    def som_descoberta(self):
        """
        Toca som de descoberta do humano (alerta de sucesso).
        """
        if not self.habilitado:
            print("🔊 [SOM] Descoberta do humano!")
            return
        
        # Sequência de tons ascendentes (alerta de sucesso)
        som_total = np.array([])
        
        for freq in [440, 554, 659, 880]:  # Lá, Dó#, Mi, Lá (acorde maior)
            tom = self._gerar_onda_simples(freq, 0.2, 'seno')
            som_total = np.concatenate([som_total, tom])
        
        # Acorde final
        acorde = (self._gerar_onda_simples(440, 0.5, 'seno') + 
                 self._gerar_onda_simples(554, 0.5, 'seno') + 
                 self._gerar_onda_simples(659, 0.5, 'seno')) / 3
        
        som_total = np.concatenate([som_total, acorde])
        self._tocar_som(som_total)
        print("🔊 [SOM] Descoberta do humano!")
    
    def som_erro(self):
        """
        Toca som de erro (alerta de problema).
        """
        if not self.habilitado:
            print("🔊 [SOM] Erro detectado!")
            return
        
        # Som de erro (tom baixo e repetitivo)
        som_total = np.array([])
        
        for _ in range(3):
            erro = self._gerar_onda_simples(200, 0.1, 'quadrada')
            silencio = np.zeros(int(0.1 * 22050))
            som_total = np.concatenate([som_total, erro, silencio])
        
        self._tocar_som(som_total)
        print("🔊 [SOM] Erro detectado!")
    
    def som_inicializacao(self):
        """
        Toca som de inicialização do sistema.
        """
        if not self.habilitado:
            print("🔊 [SOM] Sistema inicializado")
            return
        
        # Sequência de inicialização
        som_total = np.array([])
        
        for i in range(5):
            tom = self._gerar_onda_simples(300 + i * 100, 0.1, 'seno')
            som_total = np.concatenate([som_total, tom])
        
        self._tocar_som(som_total)
        print("🔊 [SOM] Sistema inicializado")
    
    def som_missao_concluida(self):
        """
        Toca som de missão concluída com sucesso.
        """
        if not self.habilitado:
            print("🔊 [SOM] Missão concluída!")
            return
        
        # Fanfarra de sucesso
        som_total = np.array([])
        
        # Melodia simples de vitória
        melodia = [523, 659, 784, 1047]  # Dó, Mi, Sol, Dó (oitava)
        
        for nota in melodia:
            som = self._gerar_onda_simples(nota, 0.3, 'seno')
            som_total = np.concatenate([som_total, som])
        
        # Acorde final
        acorde = (self._gerar_onda_simples(523, 1.0, 'seno') + 
                 self._gerar_onda_simples(659, 1.0, 'seno') + 
                 self._gerar_onda_simples(784, 1.0, 'seno')) / 3
        
        som_total = np.concatenate([som_total, acorde])
        self._tocar_som(som_total)
        print("🔊 [SOM] Missão concluída!")
    
    def ajustar_volume(self, novo_volume: float):
        """
        Ajusta o volume do sistema de áudio.
        
        Args:
            novo_volume (float): Novo volume (0.0 a 1.0)
        """
        self.volume = max(0.0, min(1.0, novo_volume))
        print(f"🔊 Volume ajustado para: {self.volume:.1f}")
    
    def habilitar_desabilitar(self, habilitado: bool):
        """
        Habilita ou desabilita os efeitos sonoros.
        
        Args:
            habilitado (bool): Se os efeitos devem estar habilitados
        """
        self.habilitado = habilitado and PYGAME_AVAILABLE
        status = "habilitados" if self.habilitado else "desabilitados"
        print(f"🔊 Efeitos sonoros {status}")
    
    def __del__(self):
        """
        Limpa recursos do pygame ao destruir o objeto.
        """
        if self.habilitado:
            try:
                pygame.mixer.quit()
            except:
                pass
