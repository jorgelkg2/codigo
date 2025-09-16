"""
Ejemplo de uso del sistema de agentes con errores corregidos
==========================================================
"""

import time
import logging
from typing import Dict, Any

from agents.implementations import ChatAgent, TaskAgent
from agents.exceptions import AgentError


def setup_logging():
    """Configura el logging para el ejemplo"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def create_sample_agents() -> Dict[str, Any]:
    """Crea agentes de ejemplo"""
    agents = {}
    
    # Crear ChatAgent
    chat_agent = ChatAgent("ChatBot1")
    agents['chat'] = chat_agent
    print(f"✓ ChatAgent creado: {chat_agent.id}")
    
    # Crear TaskAgent con configuración
    task_config = {
        'max_tasks': 5,
        'task_timeout': 10.0
    }
    task_agent = TaskAgent("TaskProcessor1", task_config)
    agents['task'] = task_agent
    print(f"✓ TaskAgent creado: {task_agent.id}")
    
    return agents


def demonstrate_corrected_errors(agents: Dict[str, Any]):
    """Demuestra los errores que fueron corregidos"""
    
    print("\n=== DEMOSTRACIÓN DE ERRORES CORREGIDOS ===")
    
    # ERROR CORREGIDO #1: Validación de entrada
    print("\n1. Validación de entrada corregida:")
    try:
        # Esto funcionará correctamente
        valid_agent = ChatAgent("ValidAgent")
        print("✓ Agente con nombre válido creado correctamente")
        
        # Esto lanzará excepción por validación
        invalid_agent = ChatAgent("")  # Nombre vacío
        print("✗ No debería llegar aquí")
    except ValueError as e:
        print(f"✓ Validación funcionando: {e}")
    
    # ERROR CORREGIDO #2: Thread safety y comunicación
    print("\n2. Comunicación thread-safe entre agentes:")
    chat_agent = agents['chat']
    task_agent = agents['task']
    
    # Enviar mensaje de chat
    chat_message = {
        'type': 'greeting',
        'text': 'Hola TaskAgent!'
    }
    
    try:
        chat_agent.send_message(task_agent, chat_message)
        print("✓ Mensaje enviado sin race conditions")
    except Exception as e:
        print(f"✗ Error en comunicación: {e}")
    
    # ERROR CORREGIDO #3: Manejo de tareas con error recovery
    print("\n3. Manejo robusto de errores en tareas:")
    
    # Tarea válida
    valid_task = {
        'type': 'task',
        'task_id': 'calc_001',
        'action': 'calculate',
        'params': {'a': 10, 'b': 5, 'operation': 'add'}
    }
    
    # Tarea con error (división por cero)
    error_task = {
        'type': 'task',
        'task_id': 'calc_002',
        'action': 'calculate',
        'params': {'a': 10, 'b': 0, 'operation': 'divide'}
    }
    
    # Enviar ambas tareas
    chat_agent.send_message(task_agent, {'content': valid_task})
    chat_agent.send_message(task_agent, {'content': error_task})
    
    print("✓ Tareas enviadas (una válida, una con error)")


def demonstrate_system_resilience(agents: Dict[str, Any]):
    """Demuestra la resistencia del sistema a fallos"""
    
    print("\n=== DEMOSTRACIÓN DE RESISTENCIA DEL SISTEMA ===")
    
    # Iniciar todos los agentes
    print("\n1. Iniciando todos los agentes...")
    for agent in agents.values():
        agent.start()
    time.sleep(1)  # Dar tiempo para inicialización
    
    # Simular actividad del sistema
    print("\n2. Simulando actividad del sistema...")
    chat_agent = agents['chat']
    task_agent = agents['task']
    
    # Enviar múltiples tareas
    for i in range(3):
        task_msg = {
            'type': 'task',
            'task_id': f'test_task_{i}',
            'action': 'process_data',
            'params': {'data': list(range(i * 10, (i + 1) * 10))}
        }
        chat_agent.send_message(task_agent, {'content': task_msg})
    
    print("✓ Múltiples tareas enviadas")
    
    # Dar tiempo para procesamiento
    time.sleep(2)
    
    # Mostrar estadísticas de agentes
    print("\n3. Estadísticas de agentes:")
    for name, agent in agents.items():
        stats = agent.get_stats()
        print(f"  {name.upper()}:")
        print(f"    - Mensajes recibidos: {stats['messages_received']}")
        print(f"    - Mensajes enviados: {stats['messages_sent']}")
        print(f"    - Tareas completadas: {stats['tasks_completed']}")
        print(f"    - Errores: {stats['errors']}")
        if stats.get('uptime'):
            print(f"    - Tiempo activo: {stats['uptime']:.2f}s")


def main():
    """Función principal del ejemplo"""
    setup_logging()
    
    print("=== SISTEMA DE AGENTES CON ERRORES CORREGIDOS ===")
    print("Este ejemplo demuestra un sistema robusto de agentes")
    print("con los principales errores identificados y corregidos.\n")
    
    try:
        # Crear agentes de ejemplo
        agents = create_sample_agents()
        
        if len(agents) == 2:
            print(f"✓ {len(agents)} agentes creados exitosamente")
            
            # Demostrar errores corregidos
            demonstrate_corrected_errors(agents)
            
            # Demostrar resistencia del sistema
            demonstrate_system_resilience(agents)
            
        else:
            print(f"✗ Error: Solo se crearon {len(agents)} agentes de 2 esperados")
        
        # Pausa antes de cleanup
        print("\n=== FINALIZANDO SISTEMA ===")
        time.sleep(1)
        
    except Exception as e:
        print(f"✗ Error en el ejemplo: {e}")
    
    finally:
        # Cleanup del sistema
        try:
            for agent in agents.values():
                agent.stop()
            print("✓ Sistema detenido correctamente")
        except Exception as e:
            print(f"✗ Error al detener sistema: {e}")


if __name__ == "__main__":
    main()