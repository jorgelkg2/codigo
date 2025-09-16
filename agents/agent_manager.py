"""
AgentManager - Gestiona múltiples agentes con errores corregidos
==============================================================
"""

import logging
import threading
import time
from typing import Dict, List, Optional, Any, Callable
from queue import Queue

from .agent import Agent
from .exceptions import AgentError, ConfigurationError


class AgentManager:
    """
    Gestor de agentes que maneja múltiples agentes y su comunicación.
    
    ERROR CORREGIDO #1: Race conditions en acceso concurrente
    ERROR CORREGIDO #2: Memory leaks al no limpiar agentes detenidos
    ERROR CORREGIDO #3: Falta de validación en métodos críticos
    """
    
    def __init__(self, max_agents: int = 100):
        # ERROR CORREGIDO: Validar parámetros de entrada
        if max_agents <= 0:
            raise ValueError("max_agents debe ser un número positivo")
        
        self.max_agents = max_agents
        self._agents: Dict[str, Agent] = {}
        self._lock = threading.RLock()
        self._message_router = Queue()
        self._shutdown_event = threading.Event()
        self._router_thread = None
        self._is_running = False
        
        # Configurar logging
        self.logger = logging.getLogger("agent_manager")
        self.logger.setLevel(logging.INFO)
        
        # Estadísticas del manager
        self.stats = {
            'agents_created': 0,
            'agents_destroyed': 0,
            'messages_routed': 0,
            'errors': 0
        }
    
    def start(self) -> None:
        """Inicia el gestor de agentes"""
        with self._lock:
            if self._is_running:
                self.logger.warning("AgentManager ya está ejecutándose")
                return
            
            self.logger.info("Iniciando AgentManager")
            self._is_running = True
            self._shutdown_event.clear()
            
            # ERROR CORREGIDO: Usar daemon thread
            self._router_thread = threading.Thread(
                target=self._message_router_loop,
                name="MessageRouter",
                daemon=True
            )
            self._router_thread.start()
    
    def stop(self) -> None:
        """Detiene el gestor y todos los agentes"""
        with self._lock:
            if not self._is_running:
                return
            
            self.logger.info("Deteniendo AgentManager")
            self._is_running = False
            self._shutdown_event.set()
            
            # Detener todos los agentes
            agents_to_stop = list(self._agents.values())
            for agent in agents_to_stop:
                try:
                    agent.stop()
                except Exception as e:
                    self.logger.error(f"Error al detener agente {agent.name}: {e}")
            
            # ERROR CORREGIDO: Cleanup del thread del router
            if self._router_thread and self._router_thread.is_alive():
                self._router_thread.join(timeout=5.0)
            
            # ERROR CORREGIDO: Limpiar diccionario de agentes
            self._agents.clear()
    
    def add_agent(self, agent: Agent) -> bool:
        """Añade un agente al gestor"""
        if not isinstance(agent, Agent):
            raise TypeError("El objeto debe ser una instancia de Agent")
        
        with self._lock:
            # ERROR CORREGIDO: Verificar límite de agentes
            if len(self._agents) >= self.max_agents:
                self.logger.error(f"Límite máximo de agentes alcanzado ({self.max_agents})")
                return False
            
            # ERROR CORREGIDO: Verificar que el agente no esté ya registrado
            if agent.id in self._agents:
                self.logger.warning(f"Agente {agent.name} ya está registrado")
                return False
            
            try:
                self._agents[agent.id] = agent
                self.stats['agents_created'] += 1
                self.logger.info(f"Agente {agent.name} añadido al gestor")
                
                # Configurar callback para routing de mensajes
                agent.add_message_callback(self._route_message)
                
                return True
                
            except Exception as e:
                self.logger.error(f"Error al añadir agente: {e}")
                self.stats['errors'] += 1
                return False
    
    def remove_agent(self, agent_id: str) -> bool:
        """Remueve un agente del gestor"""
        if not agent_id:
            raise ValueError("agent_id no puede estar vacío")
        
        with self._lock:
            if agent_id not in self._agents:
                self.logger.warning(f"Agente con ID {agent_id} no encontrado")
                return False
            
            try:
                agent = self._agents[agent_id]
                
                # ERROR CORREGIDO: Detener agente antes de removerlo
                if agent.is_running:
                    agent.stop()
                
                del self._agents[agent_id]
                self.stats['agents_destroyed'] += 1
                self.logger.info(f"Agente {agent.name} removido del gestor")
                
                return True
                
            except Exception as e:
                self.logger.error(f"Error al remover agente: {e}")
                self.stats['errors'] += 1
                return False
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Obtiene un agente por su ID"""
        with self._lock:
            return self._agents.get(agent_id)
    
    def get_agent_by_name(self, name: str) -> Optional[Agent]:
        """Obtiene un agente por su nombre"""
        with self._lock:
            for agent in self._agents.values():
                if agent.name == name:
                    return agent
            return None
    
    def list_agents(self) -> List[Agent]:
        """Lista todos los agentes registrados"""
        with self._lock:
            return list(self._agents.values())
    
    def start_agent(self, agent_id: str) -> bool:
        """Inicia un agente específico"""
        agent = self.get_agent(agent_id)
        if not agent:
            self.logger.error(f"Agente con ID {agent_id} no encontrado")
            return False
        
        try:
            agent.start()
            return True
        except Exception as e:
            self.logger.error(f"Error al iniciar agente: {e}")
            self.stats['errors'] += 1
            return False
    
    def stop_agent(self, agent_id: str) -> bool:
        """Detiene un agente específico"""
        agent = self.get_agent(agent_id)
        if not agent:
            self.logger.error(f"Agente con ID {agent_id} no encontrado")
            return False
        
        try:
            agent.stop()
            return True
        except Exception as e:
            self.logger.error(f"Error al detener agente: {e}")
            self.stats['errors'] += 1
            return False
    
    def start_all_agents(self) -> None:
        """Inicia todos los agentes registrados"""
        with self._lock:
            for agent in self._agents.values():
                if not agent.is_running:
                    try:
                        agent.start()
                    except Exception as e:
                        self.logger.error(f"Error al iniciar agente {agent.name}: {e}")
                        self.stats['errors'] += 1
    
    def stop_all_agents(self) -> None:
        """Detiene todos los agentes registrados"""
        with self._lock:
            for agent in self._agents.values():
                if agent.is_running:
                    try:
                        agent.stop()
                    except Exception as e:
                        self.logger.error(f"Error al detener agente {agent.name}: {e}")
                        self.stats['errors'] += 1
    
    def broadcast_message(self, message: Dict[str, Any], sender_id: Optional[str] = None) -> None:
        """Envía un mensaje a todos los agentes"""
        if not isinstance(message, dict):
            raise ValueError("El mensaje debe ser un diccionario")
        
        with self._lock:
            for agent in self._agents.values():
                # No enviar el mensaje al remitente
                if sender_id and agent.id == sender_id:
                    continue
                
                try:
                    agent.receive_message(message)
                except Exception as e:
                    self.logger.error(f"Error al enviar broadcast a {agent.name}: {e}")
                    self.stats['errors'] += 1
    
    def send_message(self, from_agent_id: str, to_agent_id: str, message: Dict[str, Any]) -> bool:
        """Envía un mensaje entre agentes específicos"""
        if not all([from_agent_id, to_agent_id, message]):
            raise ValueError("Todos los parámetros son requeridos")
        
        from_agent = self.get_agent(from_agent_id)
        to_agent = self.get_agent(to_agent_id)
        
        if not from_agent:
            self.logger.error(f"Agente origen {from_agent_id} no encontrado")
            return False
        
        if not to_agent:
            self.logger.error(f"Agente destino {to_agent_id} no encontrado")
            return False
        
        try:
            from_agent.send_message(to_agent, message)
            return True
        except Exception as e:
            self.logger.error(f"Error al enviar mensaje: {e}")
            self.stats['errors'] += 1
            return False
    
    def _route_message(self, message: Dict[str, Any]) -> None:
        """Callback para routing de mensajes (para futuras extensiones)"""
        try:
            self._message_router.put(message)
        except Exception as e:
            self.logger.error(f"Error en routing de mensaje: {e}")
    
    def _message_router_loop(self) -> None:
        """Bucle del router de mensajes"""
        while self._is_running and not self._shutdown_event.is_set():
            try:
                # ERROR CORREGIDO: Timeout para evitar bloqueos
                message = self._message_router.get(timeout=1.0)
                
                # Procesar mensaje si es necesario
                self.stats['messages_routed'] += 1
                self._message_router.task_done()
                
            except:
                # Timeout o error, continuar
                continue
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del gestor"""
        with self._lock:
            stats = self.stats.copy()
            stats['active_agents'] = len(self._agents)
            stats['running_agents'] = sum(1 for agent in self._agents.values() if agent.is_running)
            return stats
    
    def cleanup_stopped_agents(self) -> int:
        """Limpia agentes que ya no están ejecutándose"""
        count = 0
        with self._lock:
            # ERROR CORREGIDO: Crear lista de IDs para evitar modificar dict durante iteración
            stopped_agents = [
                agent_id for agent_id, agent in self._agents.items() 
                if not agent.is_running
            ]
            
            for agent_id in stopped_agents:
                if self.remove_agent(agent_id):
                    count += 1
        
        if count > 0:
            self.logger.info(f"Se limpiaron {count} agentes detenidos")
        
        return count
    
    def __del__(self):
        """Destructor para asegurar limpieza"""
        try:
            if hasattr(self, '_is_running') and self._is_running:
                self.stop()
        except:
            pass