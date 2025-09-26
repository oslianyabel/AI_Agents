"""
Tools package for AI Agents Library.

Este paquete contiene todas las herramientas disponibles para los agentes de IA.
"""

# Importaciones básicas
from .datetime_tool import get_current_datetime, async_get_current_datetime
from .weather_tool import get_current_weather, async_get_current_weather

# Importaciones opcionales con manejo de errores
try:
    from .email_tool import send_email
except ImportError:
    send_email = None

try:
    from .excel_tool import manipulate_xlsx
except ImportError:
    manipulate_xlsx = None

try:
    from .pg_tool import execute_query
except ImportError:
    execute_query = None

try:
    from .sql_server_tool import execute_sql_server_query
except ImportError:
    execute_sql_server_query = None

# Lista de todas las herramientas disponibles
__all__ = [
    'get_current_datetime',
    'async_get_current_datetime',
    'get_current_weather', 
    'async_get_current_weather',
    'send_email',
    'manipulate_xlsx',
    'execute_query',
    'execute_sql_server_query'
]

# Diccionario de funciones disponibles
AVAILABLE_FUNCTIONS = {
    'get_current_datetime': get_current_datetime,
    'get_current_weather': get_current_weather,
}

# Agregar funciones opcionales si están disponibles
if send_email:
    AVAILABLE_FUNCTIONS['send_email'] = send_email

if manipulate_xlsx:
    AVAILABLE_FUNCTIONS['manipulate_xlsx'] = manipulate_xlsx

if execute_query:
    AVAILABLE_FUNCTIONS['execute_query'] = execute_query

if execute_sql_server_query:
    AVAILABLE_FUNCTIONS['execute_sql_server_query'] = execute_sql_server_query
