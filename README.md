# AI Agents Library

Una biblioteca completa para crear agentes de IA conversacionales con soporte para múltiples proveedores (OpenAI y Avangenio) y herramientas integradas.

## 🚀 Características

- **Múltiples Proveedores de IA**: Soporte para OpenAI (GPT-4, GPT-5) y Avangenio (agent-xs, agent-md, etc.)
- **Configuración Automática**: Detección automática del proveedor y modelo basado en variables de entorno
- **Herramientas Integradas**: Email, Excel, bases de datos (PostgreSQL, SQL Server), clima(pruebas), fecha/hora
- **Soporte de Proxy**: Configuración automática de proxy HTTP para entornos corporativos
- **Interfaz de Consola**: Chat interactivo por consola con comandos especiales
- **Reasoning Display**: Visualización del proceso de razonamiento del modelo
- **Gestión de Memoria**: Sistema de memoria de chat persistente por usuario

## 📋 Requisitos

### Dependencias Básicas
```bash
pip install -r requirements.txt
```

## ⚙️ Configuración

### Variables de Entorno

Crea un archivo `.env` en el directorio raíz con las siguientes variables:

#### Configuración del Agente
```bash
# Tipo de agente: OPENAI o AVANGENIO
AGENT_VERSION=OPENAI

# Modelos disponibles
OPENAI_MODEL=gpt-5
AVANGENIO_MODEL=agent-md

# API Keys
OPENAI_API_KEY=tu-clave-openai
AVANGENIO_API_KEY=tu-clave-avangenio
```

#### Configuración de Proxy (Opcional)
```bash
HTTP_PROXY=http://usuario:password@proxy.host:puerto
```

#### Configuración de Base de Datos (Opcional)
```bash
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=mi_base_datos
POSTGRES_USER=usuario
POSTGRES_PASSWORD=password

# SQL Server
MSSQL_SERVER=localhost
MSSQL_DATABASE=mi_base_datos
MSSQL_USER=usuario
MSSQL_PASSWORD=password
MSSQL_DRIVER=ODBC Driver 18 for SQL Server
MSSQL_PORT=1433
```

#### Configuración de Email (Opcional)
```bash
GMAIL_USER=tu-email@gmail.com
GMAIL_PASSWORD=tu-app-password
```

## 🎯 Uso Rápido

### Ejecutar Chat de Consola
```bash
python console_chat.py
```

El sistema detectará automáticamente tu configuración basándose en las variables de entorno.

### Uso Programático

#### Agente OpenAI
```python
from agent import Agent
from enumerations import ModelType

# tools/mi_herramienta.py
def mi_funcion_personalizada(parametro: str) -> str:
    return f"Procesado: {parametro}"

rag_functions = {"mi_funcion_personalizada": mi_funcion_personalizada}

# json_tools_v2.py
rag_prompt = [
    {
        "type": "function",
        "function": {
            "name": "mi_funcion_personalizada",
            "description": "Descripción de mi función",
            "parameters": {
                "type": "object",
                "properties": {
                    "parametro": {
                        "type": "string",
                        "description": "Descripción del parámetro"
                    }
                },
                "required": ["parametro"]
            }
        }
    }
]

agent = Agent(name="Mi Agente", model=ModelType.GPT_5.value)

response = agent.process_msg(
    message="¿Cuál es el clima en Madrid?",
    user_id=1,  # importante para persistir los mensajes por usuario
    rag_functions=rag_functions,
    rag_prompt=rag_prompt
)
print(response)
```

## 🛠️ Herramientas Disponibles

### Herramientas Básicas
- **get_current_datetime**: Obtiene fecha y hora actual
- **get_current_weather**: Obtiene información del clima de una ciudad(pruebas)

### Herramientas de Comunicación
- **send_email**: Envía emails con adjuntos via Gmail

### Herramientas de Datos
- **manipulate_xlsx**: Lee, escribe y modifica archivos Excel
- **execute_query**: Ejecuta consultas SELECT en PostgreSQL
- **execute_sql_server_query**: Ejecuta consultas SELECT en SQL Server

### Herramientas Web
- **web_search**: Búsqueda web (solo OpenAI)

## 🔧 Configuración Avanzada

### Modelos Disponibles

#### OpenAI
- `gpt-4.1`, `gpt-4.1-mini`, `gpt-4.1-nano`
- `gpt-5`, `gpt-5-mini`, `gpt-5-nano`

#### Avangenio
- `agent-xs`, `agent-sm`, `agent-md`, `agent-lg`, `agent-xl`
