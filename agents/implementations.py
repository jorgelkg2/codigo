"""
Implementaciones específicas de agentes corregidos
=====================================
"""

import time
import random
from typing import Dict, Any, List
from .agent import Agent


class ChatAgent(Agent):
    """
    Agente de chat que maneja conversaciones.
    Demuestra el uso correcto del sistema base.
    """
    
    def initialize(self) -> None:
        """Inicialización del agente de chat"""
        self.conversations: Dict[str, List[str]] = {}
        self.response_templates = [
            "Hola {sender}, ¿cómo estás?",
            "Interesante mensaje de {sender}: {content}",
            "Gracias por el mensaje, {sender}",
            "¿Podrías elaborar más sobre eso, {sender}?"
        ]
        self.logger.info(f"ChatAgent {self.name} inicializado")
    
    def update(self) -> None:
        """Lógica de actualización del chat agent"""
        # Simular actividad periódica del agente
        if random.random() < 0.01:  # 1% probabilidad por ciclo
            self.stats['tasks_completed'] += 1
    
    def handle_message(self, message: Dict[str, Any]) -> None:
        """Maneja mensajes de chat"""
        try:
            sender_name = message.get('sender_name', 'Unknown')
            content = message.get('content', {})
            
            # Almacenar en historial de conversación
            if sender_name not in self.conversations:
                self.conversations[sender_name] = []
            
            self.conversations[sender_name].append(str(content))
            
            # Simular procesamiento del mensaje
            if isinstance(content, dict) and content.get('type') == 'greeting':
                self.logger.info(f"Recibido saludo de {sender_name}")
            
        except Exception as e:
            self.logger.error(f"Error al procesar mensaje de chat: {e}")
            raise
    
    def cleanup(self) -> None:
        """Limpieza del agente de chat"""
        self.conversations.clear()
        self.logger.info(f"ChatAgent {self.name} finalizado")


class TaskAgent(Agent):
    """
    Agente que ejecuta tareas específicas.
    Demuestra manejo de errores y recuperación.
    """
    
    def initialize(self) -> None:
        """Inicialización del agente de tareas"""
        self.task_queue: List[Dict[str, Any]] = []
        self.completed_tasks: List[Dict[str, Any]] = []
        self.max_tasks = self.config.get('max_tasks', 10)
        self.task_timeout = self.config.get('task_timeout', 30.0)
        self.logger.info(f"TaskAgent {self.name} inicializado con max_tasks={self.max_tasks}")
    
    def update(self) -> None:
        """Procesa tareas en cola"""
        if hasattr(self, 'task_queue') and self.task_queue:
            task = self.task_queue.pop(0)
            self._execute_task(task)
    
    def handle_message(self, message: Dict[str, Any]) -> None:
        """Maneja mensajes con nuevas tareas"""
        try:
            content = message.get('content', {})
            
            if isinstance(content, dict) and content.get('type') == 'task':
                if len(self.task_queue) < self.max_tasks:
                    task = {
                        'id': content.get('task_id'),
                        'action': content.get('action'),
                        'params': content.get('params', {}),
                        'received_at': time.time(),
                        'sender': message.get('sender_name')
                    }
                    self.task_queue.append(task)
                    self.logger.info(f"Tarea {task['id']} añadida a la cola")
                else:
                    self.logger.warning("Cola de tareas llena, rechazando nueva tarea")
            
        except Exception as e:
            self.logger.error(f"Error al procesar mensaje de tarea: {e}")
            raise
    
    def _execute_task(self, task: Dict[str, Any]) -> None:
        """Ejecuta una tarea específica"""
        try:
            task_id = task.get('id', 'unknown')
            action = task.get('action')
            
            start_time = time.time()
            
            # Simular ejecución de tarea
            if action == 'calculate':
                result = self._calculate_task(task.get('params', {}))
            elif action == 'process_data':
                result = self._process_data_task(task.get('params', {}))
            else:
                raise ValueError(f"Acción desconocida: {action}")
            
            execution_time = time.time() - start_time
            
            # Verificar timeout
            if execution_time > self.task_timeout:
                raise TimeoutError(f"Tarea {task_id} excedió el timeout")
            
            # Marcar como completada
            completed_task = task.copy()
            completed_task.update({
                'result': result,
                'completed_at': time.time(),
                'execution_time': execution_time,
                'status': 'completed'
            })
            
            self.completed_tasks.append(completed_task)
            self.stats['tasks_completed'] += 1
            
            self.logger.info(f"Tarea {task_id} completada en {execution_time:.2f}s")
            
        except Exception as e:
            # ERROR CORREGIDO: Manejo adecuado de errores en tareas
            self.logger.error(f"Error ejecutando tarea {task.get('id')}: {e}")
            
            failed_task = task.copy()
            failed_task.update({
                'completed_at': time.time(),
                'status': 'failed',
                'error': str(e)
            })
            
            self.completed_tasks.append(failed_task)
            self.stats['errors'] += 1
    
    def _calculate_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simula una tarea de cálculo"""
        # Simular trabajo computacional
        time.sleep(0.1)
        
        a = params.get('a', 0)
        b = params.get('b', 0)
        operation = params.get('operation', 'add')
        
        if operation == 'add':
            result = a + b
        elif operation == 'multiply':
            result = a * b
        elif operation == 'divide':
            if b == 0:
                raise ValueError("División por cero")
            result = a / b
        else:
            raise ValueError(f"Operación no soportada: {operation}")
        
        return {'result': result, 'operation': operation}
    
    def _process_data_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simula procesamiento de datos"""
        # Simular procesamiento
        time.sleep(0.05)
        
        data = params.get('data', [])
        if not isinstance(data, list):
            raise ValueError("Los datos deben ser una lista")
        
        # Simular análisis básico
        result = {
            'count': len(data),
            'sum': sum(x for x in data if isinstance(x, (int, float))),
            'processed_at': time.time()
        }
        
        return result
    
    def cleanup(self) -> None:
        """Limpieza del agente de tareas"""
        self.logger.info(f"TaskAgent {self.name} finalizando. Tareas completadas: {len(self.completed_tasks)}")
        self.task_queue.clear()
        self.completed_tasks.clear()