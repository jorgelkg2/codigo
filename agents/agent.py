"""
Clase base Agent con errores comunes identificados y corregidos
=============================================================
"""

import logging
import threading
import time
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
from queue import Queue, Empty

from .exceptions import AgentError, CommunicationError, TaskError


class Agent(ABC):
    """
    Clase base para todos los agentes del sistema.
    
    ERROR CORREGIDO #1: Falta de manejo adecuado de threading
    ERROR CORREGIDO #2: No hay validación de entrada en métodos críticos
    ERROR CORREGIDO #3: Falta de cleanup en el destructor
    """
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        # ERROR CORREGIDO: Validación de entrada faltante
        if not name or not isinstance(name, str):
            raise ValueError("El nombre del agente debe ser una cadena no vacía")
        
        self.id = str(uuid.uuid4())
        self.name = name
        self.config = config or {}
        self.is_running = False
        self.message_queue = Queue()
        self.logger = self._setup_logger()
        
        # ERROR CORREGIDO: Thread safety con locks
        self._lock = threading.RLock()
        self._worker_thread = None
        self._shutdown_event = threading.Event()
        
        # Lista de callbacks para mensajes
        self._message_callbacks: List[Callable] = []
        
        # Estadísticas del agente
        self.stats = {
            'messages_received': 0,
            'messages_sent': 0,
            'tasks_completed': 0,
            'errors': 0,
            'start_time': None
        }
    
    def _setup_logger(self) -> logging.Logger:
        """Configura el logger para el agente"""
        logger = logging.getLogger(f"agent.{self.name}")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def start(self) -> None:
        """Inicia el agente"""
        with self._lock:
            if self.is_running:
                self.logger.warning(f"Agente {self.name} ya está ejecutándose")
                return
            
            try:
                self.logger.info(f"Iniciando agente {self.name}")
                self.is_running = True
                self.stats['start_time'] = time.time()
                self._shutdown_event.clear()
                
                # ERROR CORREGIDO: Usar daemon thread para evitar bloqueos al salir
                self._worker_thread = threading.Thread(
                    target=self._run_loop,
                    name=f"Agent-{self.name}",
                    daemon=True
                )
                self._worker_thread.start()
                
                # Llamar a la inicialización personalizada del agente
                self.initialize()
                
            except Exception as e:
                self.logger.error(f"Error al iniciar agente {self.name}: {e}")
                self.is_running = False
                raise AgentError(f"No se pudo iniciar el agente: {e}")
    
    def stop(self) -> None:
        """Detiene el agente de forma segura"""
        with self._lock:
            if not self.is_running:
                return
            
            self.logger.info(f"Deteniendo agente {self.name}")
            self.is_running = False
            self._shutdown_event.set()
            
            # ERROR CORREGIDO: Cleanup adecuado del thread
            if self._worker_thread and self._worker_thread.is_alive():
                self._worker_thread.join(timeout=5.0)
                if self._worker_thread.is_alive():
                    self.logger.warning(f"Thread del agente {self.name} no se detuvo correctamente")
            
            # Llamar a cleanup personalizado
            self.cleanup()
    
    def _run_loop(self) -> None:
        """Bucle principal del agente"""
        try:
            while self.is_running and not self._shutdown_event.is_set():
                try:
                    # Procesar mensajes de la cola
                    self._process_messages()
                    
                    # Ejecutar lógica personalizada del agente
                    self.update()
                    
                    # ERROR CORREGIDO: Pequeña pausa para evitar usar 100% CPU
                    time.sleep(0.01)
                    
                except Exception as e:
                    self.stats['errors'] += 1
                    self.logger.error(f"Error en bucle del agente {self.name}: {e}")
                    # ERROR CORREGIDO: No terminar por un error, continuar ejecutando
                    
        except Exception as e:
            self.logger.critical(f"Error crítico en agente {self.name}: {e}")
        finally:
            self.logger.info(f"Agente {self.name} ha terminado su ejecución")
    
    def _process_messages(self) -> None:
        """Procesa mensajes de la cola"""
        try:
            # ERROR CORREGIDO: Usar timeout para evitar bloqueos
            message = self.message_queue.get(timeout=0.1)
            
            try:
                self.stats['messages_received'] += 1
                self.handle_message(message)
                
                # Notificar a callbacks registrados
                for callback in self._message_callbacks:
                    try:
                        callback(message)
                    except Exception as e:
                        self.logger.error(f"Error en callback de mensaje: {e}")
                        
            except Exception as e:
                self.logger.error(f"Error al procesar mensaje: {e}")
            finally:
                self.message_queue.task_done()
                
        except Empty:
            # No hay mensajes, continuar
            pass
    
    def send_message(self, recipient: 'Agent', message: Dict[str, Any]) -> None:
        """Envía un mensaje a otro agente"""
        if not isinstance(message, dict):
            raise ValueError("El mensaje debe ser un diccionario")
        
        if not recipient or not hasattr(recipient, 'receive_message'):
            raise CommunicationError("Destinatario inválido")
        
        try:
            # ERROR CORREGIDO: Agregar metadata al mensaje
            enriched_message = {
                'sender_id': self.id,
                'sender_name': self.name,
                'timestamp': time.time(),
                'message_id': str(uuid.uuid4()),
                'content': message
            }
            
            recipient.receive_message(enriched_message)
            self.stats['messages_sent'] += 1
            self.logger.debug(f"Mensaje enviado de {self.name} a {recipient.name}")
            
        except Exception as e:
            self.logger.error(f"Error al enviar mensaje: {e}")
            raise CommunicationError(f"No se pudo enviar el mensaje: {e}")
    
    def receive_message(self, message: Dict[str, Any]) -> None:
        """Recibe un mensaje de otro agente"""
        try:
            # ERROR CORREGIDO: Validar mensaje antes de agregarlo a la cola
            if not isinstance(message, dict):
                raise ValueError("Mensaje inválido recibido")
            
            self.message_queue.put(message)
            
        except Exception as e:
            self.logger.error(f"Error al recibir mensaje: {e}")
            raise CommunicationError(f"No se pudo recibir el mensaje: {e}")
    
    def add_message_callback(self, callback: Callable) -> None:
        """Registra un callback para cuando se reciben mensajes"""
        if callable(callback):
            self._message_callbacks.append(callback)
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del agente"""
        stats = self.stats.copy()
        if stats['start_time']:
            stats['uptime'] = time.time() - stats['start_time']
        return stats
    
    @abstractmethod
    def initialize(self) -> None:
        """Inicialización personalizada del agente (implementar en subclases)"""
        pass
    
    @abstractmethod
    def update(self) -> None:
        """Lógica de actualización del agente (implementar en subclases)"""
        pass
    
    @abstractmethod
    def handle_message(self, message: Dict[str, Any]) -> None:
        """Maneja mensajes recibidos (implementar en subclases)"""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Limpieza al detener el agente (implementar en subclases)"""
        pass
    
    def __del__(self):
        """Destructor para asegurar limpieza"""
        # ERROR CORREGIDO: Cleanup en destructor
        try:
            if hasattr(self, 'is_running') and self.is_running:
                self.stop()
        except:
            # Evitar errores en destructor
            pass
    
    def __repr__(self) -> str:
        return f"Agent(id={self.id}, name={self.name}, running={self.is_running})"