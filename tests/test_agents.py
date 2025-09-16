"""
Tests para el sistema de agentes
===============================
"""

import sys
import os
import unittest
import time
import threading
from unittest.mock import Mock, patch

# Agregar el directorio padre al path para importar agents
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import Agent, AgentManager, AgentError, CommunicationError
from agents.implementations import ChatAgent, TaskAgent, MonitorAgent


class TestAgent(Agent):
    """Agente de prueba para testing"""
    
    def __init__(self, name: str, config=None):
        super().__init__(name, config)
        self.update_count = 0
        self.messages_handled = []
        self.initialized = False
        self.cleaned_up = False
    
    def initialize(self):
        self.initialized = True
    
    def update(self):
        self.update_count += 1
    
    def handle_message(self, message):
        self.messages_handled.append(message)
    
    def cleanup(self):
        self.cleaned_up = True


class TestAgentBase(unittest.TestCase):
    """Tests para la clase base Agent"""
    
    def setUp(self):
        self.agent = TestAgent("TestAgent1")
    
    def tearDown(self):
        if self.agent.is_running:
            self.agent.stop()
    
    def test_agent_creation(self):
        """Test creación básica de agente"""
        self.assertEqual(self.agent.name, "TestAgent1")
        self.assertIsNotNone(self.agent.id)
        self.assertFalse(self.agent.is_running)
        self.assertIsNotNone(self.agent.logger)
    
    def test_invalid_agent_name(self):
        """Test validación de nombre de agente"""
        with self.assertRaises(ValueError):
            TestAgent("")
        
        with self.assertRaises(ValueError):
            TestAgent(None)
    
    def test_agent_start_stop(self):
        """Test iniciar y detener agente"""
        # Iniciar agente
        self.agent.start()
        self.assertTrue(self.agent.is_running)
        self.assertTrue(self.agent.initialized)
        
        # Esperar un poco para que procese
        time.sleep(0.1)
        
        # Verificar que update se está llamando
        self.assertGreater(self.agent.update_count, 0)
        
        # Detener agente
        self.agent.stop()
        self.assertFalse(self.agent.is_running)
        self.assertTrue(self.agent.cleaned_up)
    
    def test_agent_messaging(self):
        """Test comunicación entre agentes"""
        agent1 = TestAgent("Agent1")
        agent2 = TestAgent("Agent2")
        
        try:
            # Iniciar agentes
            agent1.start()
            agent2.start()
            time.sleep(0.1)
            
            # Enviar mensaje
            test_message = {"type": "test", "data": "hello"}
            agent1.send_message(agent2, test_message)
            
            # Esperar procesamiento
            time.sleep(0.1)
            
            # Verificar que el mensaje fue recibido
            self.assertGreater(len(agent2.messages_handled), 0)
            
            # Verificar contenido del mensaje
            received_msg = agent2.messages_handled[0]
            self.assertEqual(received_msg['sender_name'], "Agent1")
            self.assertEqual(received_msg['content'], test_message)
            
        finally:
            agent1.stop()
            agent2.stop()
    
    def test_message_validation(self):
        """Test validación de mensajes"""
        agent1 = TestAgent("Agent1")
        agent2 = TestAgent("Agent2")
        
        try:
            # Test mensaje inválido
            with self.assertRaises(ValueError):
                agent1.send_message(agent2, "not a dict")
            
            # Test destinatario inválido
            with self.assertRaises(CommunicationError):
                agent1.send_message(None, {"test": "message"})
            
        finally:
            agent1.stop()
            agent2.stop()
    
    def test_agent_stats(self):
        """Test estadísticas del agente"""
        agent1 = TestAgent("Agent1")
        agent2 = TestAgent("Agent2")
        
        try:
            agent1.start()
            agent2.start()
            time.sleep(0.1)
            
            # Obtener estadísticas iniciales
            stats = agent1.get_stats()
            self.assertEqual(stats['messages_sent'], 0)
            self.assertEqual(stats['messages_received'], 0)
            
            # Enviar mensaje
            agent1.send_message(agent2, {"test": "data"})
            time.sleep(0.1)
            
            # Verificar estadísticas actualizadas
            stats1 = agent1.get_stats()
            stats2 = agent2.get_stats()
            
            self.assertEqual(stats1['messages_sent'], 1)
            self.assertEqual(stats2['messages_received'], 1)
            
        finally:
            agent1.stop()
            agent2.stop()


class TestAgentManager(unittest.TestCase):
    """Tests para AgentManager"""
    
    def setUp(self):
        self.manager = AgentManager(max_agents=5)
        self.manager.start()
    
    def tearDown(self):
        self.manager.stop()
    
    def test_manager_creation(self):
        """Test creación de manager"""
        self.assertEqual(self.manager.max_agents, 5)
        self.assertTrue(self.manager._is_running)
    
    def test_add_remove_agent(self):
        """Test añadir y remover agentes"""
        agent = TestAgent("TestAgent")
        
        # Añadir agente
        result = self.manager.add_agent(agent)
        self.assertTrue(result)
        self.assertEqual(len(self.manager.list_agents()), 1)
        
        # Verificar que se puede obtener el agente
        retrieved_agent = self.manager.get_agent(agent.id)
        self.assertEqual(retrieved_agent, agent)
        
        # Remover agente
        result = self.manager.remove_agent(agent.id)
        self.assertTrue(result)
        self.assertEqual(len(self.manager.list_agents()), 0)
    
    def test_agent_limit(self):
        """Test límite máximo de agentes"""
        agents = []
        
        # Añadir agentes hasta el límite
        for i in range(self.manager.max_agents):
            agent = TestAgent(f"Agent{i}")
            result = self.manager.add_agent(agent)
            self.assertTrue(result)
            agents.append(agent)
        
        # Intentar añadir uno más (debería fallar)
        extra_agent = TestAgent("ExtraAgent")
        result = self.manager.add_agent(extra_agent)
        self.assertFalse(result)
    
    def test_start_stop_agents(self):
        """Test iniciar y detener agentes"""
        agent = TestAgent("TestAgent")
        self.manager.add_agent(agent)
        
        # Iniciar agente
        result = self.manager.start_agent(agent.id)
        self.assertTrue(result)
        self.assertTrue(agent.is_running)
        
        # Detener agente
        result = self.manager.stop_agent(agent.id)
        self.assertTrue(result)
        self.assertFalse(agent.is_running)
    
    def test_broadcast_message(self):
        """Test broadcast de mensajes"""
        agents = []
        for i in range(3):
            agent = TestAgent(f"Agent{i}")
            self.manager.add_agent(agent)
            self.manager.start_agent(agent.id)
            agents.append(agent)
        
        time.sleep(0.1)
        
        # Enviar broadcast
        message = {"type": "broadcast", "data": "hello all"}
        self.manager.broadcast_message(message)
        
        time.sleep(0.1)
        
        # Verificar que todos recibieron el mensaje
        for agent in agents:
            self.assertGreater(len(agent.messages_handled), 0)
    
    def test_cleanup_stopped_agents(self):
        """Test limpieza de agentes detenidos"""
        agent = TestAgent("TestAgent")
        self.manager.add_agent(agent)
        self.manager.start_agent(agent.id)
        
        # Detener agente directamente
        agent.stop()
        
        # Limpiar agentes detenidos
        cleaned = self.manager.cleanup_stopped_agents()
        self.assertEqual(cleaned, 1)
        self.assertEqual(len(self.manager.list_agents()), 0)


class TestSpecificAgents(unittest.TestCase):
    """Tests para implementaciones específicas de agentes"""
    
    def test_chat_agent(self):
        """Test ChatAgent"""
        agent = ChatAgent("ChatBot")
        
        try:
            agent.start()
            time.sleep(0.1)
            
            # Enviar mensaje de saludo
            message = {
                'sender_name': 'TestUser',
                'content': {'type': 'greeting', 'text': 'Hello'}
            }
            agent.receive_message(message)
            time.sleep(0.1)
            
            # Verificar que el mensaje fue procesado
            self.assertIn('TestUser', agent.conversations)
            
        finally:
            agent.stop()
    
    def test_task_agent(self):
        """Test TaskAgent"""
        config = {'max_tasks': 3, 'task_timeout': 5.0}
        agent = TaskAgent("TaskBot", config)
        
        try:
            agent.start()
            time.sleep(0.1)
            
            # Enviar tarea de cálculo
            task_message = {
                'sender_name': 'TestUser',
                'content': {
                    'type': 'task',
                    'task_id': 'test_calc',
                    'action': 'calculate',
                    'params': {'a': 5, 'b': 3, 'operation': 'add'}
                }
            }
            agent.receive_message(task_message)
            
            # Esperar procesamiento
            time.sleep(0.5)
            
            # Verificar que la tarea fue procesada
            self.assertGreater(len(agent.completed_tasks), 0)
            
            completed_task = agent.completed_tasks[0]
            self.assertEqual(completed_task['status'], 'completed')
            self.assertEqual(completed_task['result']['result'], 8)
            
        finally:
            agent.stop()
    
    def test_task_agent_error_handling(self):
        """Test manejo de errores en TaskAgent"""
        agent = TaskAgent("TaskBot")
        
        try:
            agent.start()
            time.sleep(0.1)
            
            # Enviar tarea con error (división por cero)
            error_task = {
                'sender_name': 'TestUser',
                'content': {
                    'type': 'task',
                    'task_id': 'error_task',
                    'action': 'calculate',
                    'params': {'a': 10, 'b': 0, 'operation': 'divide'}
                }
            }
            agent.receive_message(error_task)
            
            # Esperar procesamiento
            time.sleep(0.5)
            
            # Verificar que el error fue manejado correctamente
            self.assertGreater(len(agent.completed_tasks), 0)
            
            failed_task = agent.completed_tasks[0]
            self.assertEqual(failed_task['status'], 'failed')
            self.assertIn('error', failed_task)
            
        finally:
            agent.stop()
    
    def test_monitor_agent(self):
        """Test MonitorAgent"""
        config = {'check_interval': 1.0}
        agent = MonitorAgent("Monitor", config)
        
        try:
            agent.start()
            time.sleep(0.1)
            
            # Registrar agente para monitoreo
            register_message = {
                'sender_name': 'TestSystem',
                'content': {
                    'type': 'register_agent',
                    'agent_id': 'test_agent_123',
                    'agent_name': 'TestAgent'
                }
            }
            agent.receive_message(register_message)
            time.sleep(0.1)
            
            # Verificar registro
            self.assertIn('test_agent_123', agent.monitored_agents)
            
            # Obtener reporte
            report = agent.get_monitoring_report()
            self.assertEqual(report['monitored_agents'], 1)
            
        finally:
            agent.stop()


def run_tests():
    """Ejecuta todos los tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Añadir todas las clases de test
    test_classes = [
        TestAgentBase,
        TestAgentManager,
        TestSpecificAgents
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    if success:
        print("\n✓ Todos los tests pasaron correctamente!")
    else:
        print("\n✗ Algunos tests fallaron")
        exit(1)