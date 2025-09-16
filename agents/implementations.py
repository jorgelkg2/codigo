"""
Implementaciones específicas de agentes
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


class MonitorAgent(Agent):
    """
    Agente que monitorea el sistema y otros agentes.
    Demuestra uso de callbacks y estadísticas.
    """
    
    def initialize(self) -> None:
        """Inicialización del agente monitor"""
        self.monitored_agents: Dict[str, Dict[str, Any]] = {}
        self.alerts: List[Dict[str, Any]] = []
        self.check_interval = self.config.get('check_interval', 5.0)
        self.last_check = 0
        self.logger.info(f"MonitorAgent {self.name} inicializado")
    
    def update(self) -> None:
        """Ejecuta checks de monitoreo"""
        if not hasattr(self, 'last_check'):
            return
            
        current_time = time.time()
        
        if current_time - self.last_check >= self.check_interval:
            self._perform_health_check()
            self.last_check = current_time
    
    def handle_message(self, message: Dict[str, Any]) -> None:
        """Maneja mensajes de monitoreo"""
        try:
            content = message.get('content', {})
            
            if isinstance(content, dict):
                msg_type = content.get('type')
                
                if msg_type == 'register_agent':
                    self._register_agent_for_monitoring(content)
                elif msg_type == 'health_report':
                    self._process_health_report(content, message.get('sender_name'))
                elif msg_type == 'alert':
                    self._process_alert(content, message.get('sender_name'))
            
        except Exception as e:
            self.logger.error(f"Error al procesar mensaje de monitoreo: {e}")
            raise
    
    def _register_agent_for_monitoring(self, content: Dict[str, Any]) -> None:
        """Registra un agente para monitoreo"""
        agent_id = content.get('agent_id')
        agent_name = content.get('agent_name')
        
        if agent_id and agent_name:
            self.monitored_agents[agent_id] = {
                'name': agent_name,
                'registered_at': time.time(),
                'last_health_report': None,
                'status': 'unknown'
            }
            self.logger.info(f"Agente {agent_name} registrado para monitoreo")
    
    def _process_health_report(self, content: Dict[str, Any], sender_name: str) -> None:
        """Procesa reporte de salud de un agente"""
        agent_id = content.get('agent_id')
        health_data = content.get('health_data', {})
        
        if agent_id in self.monitored_agents:
            self.monitored_agents[agent_id].update({
                'last_health_report': time.time(),
                'health_data': health_data,
                'status': 'healthy'
            })
    
    def _process_alert(self, content: Dict[str, Any], sender_name: str) -> None:
        """Procesa una alerta"""
        alert = {
            'timestamp': time.time(),
            'sender': sender_name,
            'severity': content.get('severity', 'info'),
            'message': content.get('message', ''),
            'details': content.get('details', {})
        }
        
        self.alerts.append(alert)
        self.logger.warning(f"Alerta recibida de {sender_name}: {alert['message']}")
        
        # Mantener solo las últimas 100 alertas
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
    
    def _perform_health_check(self) -> None:
        """Ejecuta check de salud en agentes monitoreados"""
        current_time = time.time()
        
        for agent_id, info in self.monitored_agents.items():
            last_report = info.get('last_health_report')
            
            if last_report:
                time_since_report = current_time - last_report
                
                # Si no hay reporte en 30 segundos, marcar como no saludable
                if time_since_report > 30:
                    info['status'] = 'unhealthy'
                    self.logger.warning(f"Agente {info['name']} no ha reportado en {time_since_report:.1f}s")
    
    def get_monitoring_report(self) -> Dict[str, Any]:
        """Genera reporte de monitoreo"""
        return {
            'monitored_agents': len(self.monitored_agents),
            'healthy_agents': sum(1 for info in self.monitored_agents.values() if info['status'] == 'healthy'),
            'recent_alerts': len([a for a in self.alerts if time.time() - a['timestamp'] < 300]),  # últimos 5 min
            'agent_details': self.monitored_agents.copy(),
            'recent_alerts_list': self.alerts[-10:]  # últimas 10 alertas
        }
    
    def cleanup(self) -> None:
        """Limpieza del agente monitor"""
        self.logger.info(f"MonitorAgent {self.name} finalizando. Alertas procesadas: {len(self.alerts)}")
        self.monitored_agents.clear()
        self.alerts.clear()