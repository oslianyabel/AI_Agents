#!/usr/bin/env python3
"""
Test script for proxy configuration with OpenAI SDK
"""

import os
from dotenv import load_dotenv
from agent_v2 import Agent
from proxy_config import ProxyConfig

# Load environment variables
load_dotenv(".env")

def test_proxy_configuration():
    """Test proxy configuration and connection."""
    print("=== Prueba de Configuración de Proxy ===\n")
    
    # Test 1: Check proxy configuration
    print("1. Verificando configuración de proxy...")
    proxy_url = "http://osliani.figueiras:Dteam801*@proxy.desoft.cu:3128"
    proxy_config = ProxyConfig(proxy_url)
    
    print(f"Información del proxy: {proxy_config.get_proxy_info()}")
    print(f"Proxy válido: {proxy_config.is_valid}")
    print()
    
    # Test 2: Create agent with proxy
    print("2. Creando agente con configuración de proxy...")
    try:
        agent = Agent(
            name="Test Agent",
            proxy_url=proxy_url
        )
        print("✓ Agente creado exitosamente con proxy")
    except Exception as e:
        print(f"✗ Error creando agente: {e}")
        return False
    
    # Test 3: Test simple message (this will actually try to connect)
    print("\n3. Probando conexión con mensaje simple...")
    try:
        response = agent.process_msg(
            message="Hola, ¿puedes responder brevemente?",
            user_id=999,  # Test user ID
            rag_functions={},
            rag_prompt=[]
        )
        
        if response:
            print("✓ Conexión exitosa a través del proxy")
            print(f"Respuesta: {response[:100]}...")
        else:
            print("✗ No se recibió respuesta")
            
    except Exception as e:
        print(f"✗ Error en la conexión: {e}")
        print("Esto puede indicar un problema con el proxy o las credenciales")
    
    print("\n=== Fin de la prueba ===")

def test_environment_proxy():
    """Test proxy configuration from environment variables."""
    print("\n=== Prueba de Proxy desde Variables de Entorno ===\n")
    
    # Set environment variable for testing
    os.environ["HTTP_PROXY"] = "http://osliani.figueiras:Dteam801*@proxy.desoft.cu:3128"
    
    print("1. Configurando HTTP_PROXY en variables de entorno...")
    proxy_config = ProxyConfig()  # Should pick up from environment
    
    print(f"Proxy detectado: {proxy_config.get_proxy_info()}")
    
    # Create agent without explicit proxy (should use environment)
    print("\n2. Creando agente sin proxy explícito (usando variables de entorno)...")
    try:
        env_agent = Agent(name="Environment Test Agent")
        print("✓ Agente creado exitosamente usando variables de entorno")
        print(f"Proxy info del agente: {env_agent._ai_client.proxy_config.get_proxy_info()}")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    # Check if API key is configured
    if not os.getenv("AVANGENIO_API_KEY"):
        print("⚠️  Advertencia: AVANGENIO_API_KEY no está configurada")
        print("La prueba de conexión puede fallar por falta de API key")
        print()
    
    test_proxy_configuration()
    test_environment_proxy()
    
    print("\n📋 Instrucciones para uso:")
    print("1. Configura HTTP_PROXY en tu archivo .env")
    print("2. O pasa proxy_url directamente al crear el Agent")
    print("3. El formato del proxy debe ser: http://usuario:contraseña@host:puerto")
    print("4. Asegúrate de que AVANGENIO_API_KEY esté configurada")
