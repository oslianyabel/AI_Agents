#!/usr/bin/env python3
"""
Simplified startup script for the AI Agent with proxy support
"""

import os
import sys
from typing import Optional

def check_environment():
    """Check if environment is properly configured."""
    print("Verificando configuración del entorno...")
    
    # Check API key
    api_key = os.getenv("AVANGENIO_API_KEY")
    if not api_key:
        print("⚠️  AVANGENIO_API_KEY no está configurada")
        print("   Configura tu API key en el archivo .env")
        return False
    else:
        print("✓ AVANGENIO_API_KEY configurada")
    
    # Check proxy
    proxy = os.getenv("HTTP_PROXY")
    if proxy:
        print(f"✓ HTTP_PROXY configurado: {proxy[:50]}...")
    else:
        print("ℹ️  HTTP_PROXY no configurado (se usará proxy por defecto)")
    
    return True

def start_simple_chat():
    """Start a simple chat interface."""
    try:
        from completions_v3 import Agent
        
        # Use default proxy or environment variable
        proxy_url = "http://osliani.figueiras:Dteam801*@proxy.desoft.cu:3128"
        
        print(f"\nCreando agente con proxy: {proxy_url[:50]}...")
        agent = Agent(
            name="Asistente IA",
            proxy_url=proxy_url
        )
        
        print("✓ Agente creado exitosamente")
        print("\n" + "="*60)
        print("  Chat Simple con Agente de IA")
        print("="*60)
        print("Escribe 'salir' para terminar")
        print("="*60)
        
        user_id = 1
        while True:
            try:
                user_input = input("\nTú: ").strip()
                
                if user_input.lower() in ['salir', 'exit', 'quit']:
                    print("¡Hasta luego!")
                    break
                
                if not user_input:
                    continue
                
                print("Agente está pensando...")
                response = agent.process_msg(
                    user_input,
                    user_id,
                    rag_functions={},
                    rag_prompt=[]
                )
                
                if response:
                    print(f"\nAgente: {response}")
                else:
                    print("\nAgente: Lo siento, no pude procesar tu mensaje.")
                    
            except KeyboardInterrupt:
                print("\n\n¡Hasta luego! (Ctrl+C detectado)")
                break
            except Exception as e:
                print(f"\nError: {e}")
                print("Intenta de nuevo...")
                
    except Exception as e:
        print(f"Error iniciando el agente: {e}")
        print("\nPosibles soluciones:")
        print("1. Verifica que AVANGENIO_API_KEY esté configurada")
        print("2. Verifica la conexión a internet")
        print("3. Verifica la configuración del proxy")

def main():
    """Main function."""
    print("=== Iniciador Simple del Agente de IA ===\n")
    
    if not check_environment():
        print("\nConfigura tu entorno antes de continuar.")
        return
    
    start_simple_chat()

if __name__ == "__main__":
    main()
