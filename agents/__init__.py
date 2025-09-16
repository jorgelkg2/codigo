"""
Sistema de Agentes - Paquete principal
=============================================

Este paquete implementa un sistema básico de agentes con capacidades de
comunicación, gestión de tareas y manejo de errores.
"""

from .agent import Agent
from .agent_manager import AgentManager
from .exceptions import AgentError, CommunicationError, TaskError

__version__ = "1.0.0"
__all__ = ["Agent", "AgentManager", "AgentError", "CommunicationError", "TaskError"]