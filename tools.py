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