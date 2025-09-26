tools = [
    {
        "type": "function",
        "function": {
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
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_datetime",
            "description": "Obtiene fecha y hora actual",
            "parameters": {},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "execute_query",
            "description": "Ejecuta una consulta SQL de tipo SELECT la base de datos disponible",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_query": {
                        "type": "string",
                        "description": "Consulta SQL que se va a ejecutar en la base de datos",
                    },
                },
                "required": ["input_query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "execute_sql_server_query",
            "description": "Ejecuta una consulta de solo lectura (SELECT) en una base de datos SQL Server disponible",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_query": {
                        "type": "string",
                        "description": "Consulta SQL (SELECT ...) que se ejecutará en SQL Server",
                    },
                },
                "required": ["input_query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "manipulate_xlsx",
            "description": "Lee, escribe o modifica archivos Excel (.xlsx) en el directorio raíz",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["read", "write", "append", "list_files"],
                        "description": "Operación a realizar: 'read' para leer, 'write' para escribir nuevo archivo, 'append' para añadir datos, 'list_files' para listar archivos .xlsx",
                    },
                    "filename": {
                        "type": "string",
                        "description": "Nombre del archivo .xlsx (no requerido para list_files)",
                    },
                    "sheet_name": {
                        "type": "string",
                        "description": "Nombre de la hoja en el archivo Excel",
                        "default": "Sheet1",
                    },
                    "data": {
                        "type": "array",
                        "items": {"type": "array", "items": {"type": "string"}},
                        "description": "Datos a escribir o añadir (solo para operaciones write/append)",
                    },
                    "header": {
                        "type": "boolean",
                        "description": "Indica si los datos incluyen encabezados",
                        "default": False,
                    },
                },
                "required": ["operation"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Envía un correo electrónico desde una cuenta de Gmail con opción de adjuntar archivos",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Dirección de correo electrónico del destinatario",
                    },
                    "subject": {
                        "type": "string",
                        "description": "Asunto del correo electrónico",
                    },
                    "body": {
                        "type": "string",
                        "description": "Cuerpo del mensaje",
                    },
                    "is_html": {
                        "type": "boolean",
                        "description": "Indica si el cuerpo es HTML (opcional, por defecto es falso)",
                    },
                    "attachments": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "filename": {
                                    "type": "string",
                                    "description": "Nombre del archivo adjunto",
                                },
                            },
                            "required": ["filename"],
                        },
                        "description": "Lista de archivos adjuntos (opcional)",
                    },
                },
                "required": ["to", "subject", "body"],
            },
        },
    },
]

print("AVANGENIO tools loaded")
