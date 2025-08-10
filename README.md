# IA Completions Library

Esta librería proporciona una interfaz flexible para interactuar con modelos de lenguaje de OpenAI, permitiendo la integración de herramientas y funciones personalizadas (sincrónicas y asíncronas) en flujos conversacionales.

## Características

- Soporte para modelos OpenAI (incluyendo GPT-4, GPT-5, etc.)
- Ejecución de funciones y herramientas personalizadas (sync y async)
- Integración sencilla de nuevas herramientas
- Manejo de mensajes y contexto conversacional
- Ejecución de código y consultas a APIs externas

## Instalación

```bash
pip install openai python-dotenv
```

## Uso Básico

```python
from completions import Completions
from tools import tools

def get_current_datetime():
    return str(datetime.now())

bot = Completions(
    api_key="TU_API_KEY",
    functions={"get_current_datetime": get_current_datetime},
    json_tools=tools,
    model="gpt-5",
)
respuesta = bot.send_message("¿Qué hora es?")
print(respuesta)

```

## Estructura

- `completions.py`: Clases principales para gestionar la conversación y la integración de herramientas.
- `functions.py`: Funciones personalizadas (sync y async) que puedes conectar como herramientas.
- `tools.py`: Definición de herramientas para el modelo.

## Definición de herramientas en formato json

tools = [
    {
        "type": "function",
        "name": "get_current_weather",
        "description": "Obtiene la temperatura actual de una ciudad",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Nombre de la ciudad",
                },
            },
            "required": ["city"],
        },
    },
    {
        "type": "function",
        "name": "get_current_datetime",
        "description": "Obtiene fecha y hora actual",
    },
    {
        "type": "custom",
        "name": "query_exec",
        "description": "Ejecuta una consulta SQL en PostgreSQL",
    },
]

## Licencia

MIT
