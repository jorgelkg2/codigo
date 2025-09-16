"""
Excepciones personalizadas para el sistema de agentes
====================================================
"""


class AgentError(Exception):
    """Excepción base para errores relacionados con agentes"""
    pass


class CommunicationError(AgentError):
    """Error en la comunicación entre agentes"""
    pass


class TaskError(AgentError):
    """Error en la ejecución de tareas del agente"""
    pass


class ConfigurationError(AgentError):
    """Error en la configuración del agente"""
    pass