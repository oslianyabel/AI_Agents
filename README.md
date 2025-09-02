# IA Completions Library

Esta librería proporciona una interfaz flexible para interactuar con modelos de lenguaje de OpenAI, permitiendo la integración de herramientas y funciones personalizadas (sincrónicas y asíncronas) en flujos conversacionales.

## Características

- Soporte para modelos OpenAI (incluyendo GPT-4, GPT-5, etc.)
- Soporte para modelos Avangenio (agent-xs, agent-md, …) vía API Gateway
- Ejecución de funciones y herramientas personalizadas (sync y async)
- Integración sencilla de nuevas herramientas
- Manejo de mensajes y contexto conversacional
- Ejecución de código y consultas a APIs externas

## Instalación

```bash
pip install openai python-dotenv
```

## Uso Básico (OpenAI)

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

## Soporte Avangenio (v2 y v3)

Esta librería incluye integración con el gateway de Avangenio en `completions_v2.py` (chat con tools estilo Chat Completions) y `completions_v3.py` (ejemplo mínimo).

Variables de entorno necesarias:

- `AVANGENIO_API_KEY`: clave del gateway.
- Base URL utilizada: `https://apigateway.avangenio.net` (ya configurada en código).

Ejemplo (v2: manejo de historial interno y tools):

```bash
python completions_v2.py
```

`completions_v2.py` inicializa el bot con un prompt del sistema y habilita tools como:

- `get_current_datetime`, `get_current_weather`
- `send_email`
- `manipulate_xlsx`
- `execute_query` (solo SELECT sobre PostgreSQL)

Características de v2:

- Manejo interno del historial: `submit_message("hola")` agrega el mensaje y la respuesta.
- Mensajes de herramientas se agregan temporalmente y se purgan tras la respuesta final.
- `reset_history` limpia el historial dejando solo el prompt inicial.
- Si `reset_history` se llama junto con otras tools, no se ejecuta y devuelve: "no es posible limpiar el chat durante le ejecucion de otras herramientas".
- Reintentos con backoff exponencial ante errores 429 (rate limit).

Ejemplo (v3: snippet mínimo de Chat Completions):

```python
from openai import OpenAI

client = OpenAI(
    api_key="<AVANGENIO_API_KEY>",
    base_url="https://apigateway.avangenio.net",
)

completion = client.chat.completions.create(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "How many days are in a year?"},
    ],
    model="agent-xs",
)

print(completion.choices[0].message.content)
```

Nota: No expongas tu API key en código fuente; usa variables de entorno.

## Estructura

- `completions.py`: Clases principales para gestionar la conversación y la integración de herramientas (OpenAI Responses API con tools).
- `completions_v2.py`: Integración con Avangenio (Chat Completions + tools, historial interno y backoff).
- `completions_v3.py`: Ejemplo mínimo usando Avangenio Chat Completions.
- `functions.py`: Funciones personalizadas (sync y async) que puedes conectar como herramientas.
- `tools.py` / `json_tools_v2.py`: Definición de herramientas para el modelo.

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
