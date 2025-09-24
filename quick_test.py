#!/usr/bin/env python3
"""
Quick test to verify proxy configuration is working
"""

def main():
    print("=== Verificación Rápida de Configuración de Proxy ===\n")
    
    # Test 1: Import proxy config
    try:
        from proxy_config import ProxyConfig
        print("✓ ProxyConfig importado correctamente")
        
        proxy_url = "http://osliani.figueiras:Dteam801*@proxy.desoft.cu:3128"
        config = ProxyConfig(proxy_url)
        
        print(f"✓ Proxy configurado: {config.is_valid}")
        print(f"  Info: {config.get_proxy_info()}")
        
    except Exception as e:
        print(f"✗ Error con ProxyConfig: {e}")
        return
    
    # Test 2: Import Agent
    try:
        from completions_v3 import Agent
        print("✓ Agent importado correctamente")
        
    except Exception as e:
        print(f"✗ Error importando Agent: {e}")
        return
    
    # Test 3: Create Agent with proxy
    try:
        agent = Agent(
            name="Test Agent",
            proxy_url=proxy_url
        )
        print("✓ Agent creado exitosamente con proxy")
        
    except Exception as e:
        print(f"✗ Error creando Agent: {e}")
        return
    
    print("\n=== ¡Configuración Exitosa! ===")
    print("\nTu Agente de IA está configurado para usar el proxy:")
    print("http://osliani.figueiras:Dteam801*@proxy.desoft.cu:3128")
    print("\nPara usar el chat de consola:")
    print("1. Configura AVANGENIO_API_KEY en tu archivo .env")
    print("2. Ejecuta: python console_chat.py")
    print("\nO configura HTTP_PROXY como variable de entorno.")

if __name__ == "__main__":
    main()
