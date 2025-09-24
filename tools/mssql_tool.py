import json
import os

import pyodbc
from dotenv import load_dotenv

load_dotenv()


def get_sqlserver_connection():
    """Establece una conexión a SQL Server via ODBC.

    Requiere las variables de entorno (ejemplos):
      - MSSQL_SERVER=localhost
      - MSSQL_DATABASE=MyDb
      - MSSQL_USER=sa
      - MSSQL_PASSWORD=Secret123!
      - MSSQL_DRIVER=ODBC Driver 18 for SQL Server   # recomendado
      - MSSQL_PORT=1433                               # opcional
    """
    try:
        driver = os.getenv("MSSQL_DRIVER", "ODBC Driver 18 for SQL Server")
        server = os.getenv("MSSQL_SERVER")
        database = os.getenv("MSSQL_DATABASE")
        user = os.getenv("MSSQL_USER")
        password = os.getenv("MSSQL_PASSWORD")
        port = os.getenv("MSSQL_PORT") or "1433"

        if not all([server, database, user, password]):
            return Exception(
                "Faltan variables de entorno requeridas: MSSQL_SERVER, MSSQL_DATABASE, MSSQL_USER, MSSQL_PASSWORD"
            )

        # Encrypt and TrustServerCertificate options depend on your environment.
        # For local/dev, TrustServerCertificate=yes is common. Adjust as needed.
        conn_str = (
            f"DRIVER={{{driver}}};"
            f"SERVER={server},{port};"
            f"DATABASE={database};"
            f"UID={user};"
            f"PWD={password};"
            "Encrypt=yes;TrustServerCertificate=yes;"
        )
        conn = pyodbc.connect(conn_str)
        return conn
    except pyodbc.Error as e:
        return e


async def async_execute_mssql_query(input_query: str) -> json:
    return execute_mssql_query(input_query)


def execute_mssql_query(input_query: str) -> json:
    """
    Ejecuta una consulta de solo lectura (SELECT) en SQL Server.

    Args:
        input_query (str): Consulta SQL de lectura (SELECT ...)

    Returns:
        str: JSON serializado con resultados o mensaje de error.
    """
    if not input_query or not input_query.strip().upper().startswith("SELECT"):
        return json.dumps(
            {
                "status": "error",
                "message": "Operación no permitida. Solo se permiten consultas de lectura (SELECT).",
            }
        )

    conn = None
    try:
        conn = get_sqlserver_connection()
        if isinstance(conn, Exception):
            return json.dumps(
                {"status": "error", "message": f"Error de conexión: {conn}"}
            )

        with conn.cursor() as cur:
            cur.execute(input_query)

            if not cur.description:
                return json.dumps(
                    {
                        "status": "success",
                        "results": [],
                        "row_count": 0,
                        "message": "Consulta ejecutada correctamente, sin filas devueltas.",
                    }
                )

            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            formatted_results = [dict(zip(columns, row)) for row in rows]

            return json.dumps(
                {
                    "status": "success",
                    "results": formatted_results,
                    "row_count": len(formatted_results),
                }
            )

    except pyodbc.Error as e:
        return json.dumps({"status": "error", "message": f"Error ejecutando la consulta: {e}"})
    except Exception as e:
        return json.dumps({"status": "error", "message": f"Error inesperado: {e}"})
    finally:
        if conn and not isinstance(conn, Exception):
            conn.close()


if __name__ == "__main__":
    def main():
        # Consulta de prueba: lista las tablas del esquema dbo
        result = execute_mssql_query(
            "SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE' ORDER BY TABLE_SCHEMA, TABLE_NAME;"
        )
        print(result)

    main()
