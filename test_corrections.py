"""
Tests básicos para validar las correcciones implementadas
========================================================
"""

import sys
import os
import time
import threading
from unittest.mock import Mock

# Agregar el directorio al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.implementations import ChatAgent, TaskAgent
from agents.exceptions import AgentError


def test_input_validation():
    """Test ERROR CORREGIDO #1: Validación de entrada"""
    print("Testing input validation...")
    
    # Test válido
    try:
        agent = ChatAgent("ValidAgent")
        print("✓ Valid agent creation works")
    except Exception as e:
        print(f"✗ Valid agent creation failed: {e}")
        return False
    
    # Test inválido
    try:
        agent = ChatAgent("")  # Nombre vacío
        print("✗ Invalid agent creation should have failed")
        return False
    except ValueError:
        print("✓ Invalid agent creation properly rejected")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False
    
    return True


def test_thread_safety():
    """Test ERROR CORREGIDO #2: Thread safety"""
    print("\nTesting thread safety...")
    
    agent1 = ChatAgent("Agent1")
    agent2 = ChatAgent("Agent2")
    
    try:
        # Iniciar agentes
        agent1.start()
        agent2.start()
        time.sleep(0.2)
        
        # Test comunicación concurrente
        def send_messages():
            for i in range(10):
                message = {"type": "test", "data": f"message_{i}"}
                agent1.send_message(agent2, message)
                time.sleep(0.01)
        
        # Ejecutar en múltiples threads
        threads = []
        for _ in range(3):
            t = threading.Thread(target=send_messages)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        time.sleep(0.5)
        
        # Verificar que no hubo errores
        stats1 = agent1.get_stats()
        stats2 = agent2.get_stats()
        
        if stats1['errors'] == 0 and stats2['errors'] == 0:
            print("✓ Thread safety test passed")
            return True
        else:
            print(f"✗ Thread safety test failed: {stats1['errors']} + {stats2['errors']} errors")
            return False
            
    except Exception as e:
        print(f"✗ Thread safety test failed: {e}")
        return False
    
    finally:
        agent1.stop()
        agent2.stop()


def test_error_recovery():
    """Test ERROR CORREGIDO #4: Manejo de errores"""
    print("\nTesting error recovery...")
    
    agent = TaskAgent("TestTaskAgent")
    
    try:
        agent.start()
        time.sleep(0.2)
        
        # Enviar tarea con error (división por cero)
        error_task = {
            'type': 'task',
            'task_id': 'error_test',
            'action': 'calculate',
            'params': {'a': 10, 'b': 0, 'operation': 'divide'}
        }
        
        agent.receive_message({
            'sender_name': 'Test',
            'content': error_task
        })
        
        time.sleep(0.5)
        
        # Verificar que el agente siguió funcionando
        if agent.is_running:
            print("✓ Agent continues running after error")
            
            # Verificar que el error fue registrado
            stats = agent.get_stats()
            if stats['errors'] > 0:
                print("✓ Error was properly counted")
                return True
            else:
                print("✗ Error was not counted")
                return False
        else:
            print("✗ Agent stopped after error")
            return False
            
    except Exception as e:
        print(f"✗ Error recovery test failed: {e}")
        return False
    
    finally:
        agent.stop()


def test_memory_cleanup():
    """Test ERROR CORREGIDO #3: Memory cleanup"""
    print("\nTesting memory cleanup...")
    
    try:
        # Crear y destruir múltiples agentes
        agents = []
        for i in range(5):
            agent = ChatAgent(f"TestAgent_{i}")
            agent.start()
            agents.append(agent)
        
        time.sleep(0.2)
        
        # Detener todos los agentes
        for agent in agents:
            agent.stop()
        
        # Verificar que todos se detuvieron correctamente
        all_stopped = all(not agent.is_running for agent in agents)
        
        if all_stopped:
            print("✓ All agents stopped correctly")
            return True
        else:
            print("✗ Some agents failed to stop")
            return False
            
    except Exception as e:
        print(f"✗ Memory cleanup test failed: {e}")
        return False


def run_all_tests():
    """Ejecuta todos los tests de corrección"""
    print("=== TESTING CORRECTED ERRORS ===\n")
    
    tests = [
        test_input_validation,
        test_thread_safety,
        test_error_recovery,
        test_memory_cleanup
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
    
    print(f"\n=== RESULTS ===")
    print(f"Passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 All error corrections validated successfully!")
        return True
    else:
        print("❌ Some corrections need review")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)