from openai import OpenAI
from dotenv import load_dotenv
import time
import os
import json
import urllib.parse
import httpx
from functions import get_current_datetime, get_current_weather
from tools.email_tool import send_email
from tools.excel_tool import manipulate_xlsx
from tools.pg_tool import execute_query
from tools.mssql_tool import execute_mssql_query
from json_tools_v2 import tools, table_names
from enumerations import MessageType

load_dotenv()


class Completions:
    def __init__(
        self,
        name="Avangenio Agent",
        model="agent-md",
        json_tools=[],
        functions={},
        tool_choice="auto",
        max_retries: int = 5,
        backoff_base: float = 1.0,
        backoff_max: float = 30.0,
        prompt: str | None = None,
    ):
        # http_client = self._build_http_client_with_proxy()
        self.client = OpenAI(
            api_key=os.getenv("AVANGENIO_API_KEY"),
            base_url="https://apigateway.avangenio.net",
            # http_client=http_client,
        )
        self.name = name
        self.model = model
        self.json_tools = json_tools
        self.functions = functions
        self.tool_choice = tool_choice
        self.error_response = """Ha ocurrido un error ejecutando la herramienta {tool_name} con los argumentos: {tool_args}"""
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.backoff_max = backoff_max
        # Internal conversation history (Chat Completions format)
        self.messages: list[dict] = []
        if prompt:
            initial = {"role": MessageType.SYSTEM.value, "content": prompt.strip()}
            self.messages.append(initial)
            # Keep a copy to allow resets
            self._initial_system_msg = initial.copy()
        else:
            self._initial_system_msg = None
        # Track tool messages to later purge
        self._temp_tool_messages: list[dict] = []

    def submit_message(self, user_message: str) -> str:
        last_time = time.time()
        print(f"Running {self.name} with {len(self.functions)} tools")
        # Add user message to internal history
        self.messages.append({"role": "user", "content": user_message})

        while True:
            # Retry with exponential backoff on 429
            attempt = 0
            while True:
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=self.messages, # type: ignore
                        tools=self.json_tools,
                        functions=self.functions,
                        tool_choice=self.tool_choice, # type: ignore
                    )
                    break
                except Exception as e:
                    emsg = str(e)
                    is_429 = (
                        "429" in emsg or "Rate limit" in emsg or "rate limit" in emsg
                    )
                    if is_429 and attempt < self.max_retries:
                        wait = min(self.backoff_max, self.backoff_base * (2**attempt))
                        # small jitter
                        wait += min(1.0, 0.1 * attempt)
                        print(
                            f"Rate limited (attempt {attempt + 1}/{self.max_retries}). Reintentando en {wait:.1f}s…"
                        )
                        time.sleep(wait)
                        attempt += 1
                        continue
                    raise
            if response.choices[0].message.tool_calls:
                self.run_tools(response)
                continue

            break

        ans = response.choices[0].message.content.strip() # type: ignore
        print(f"{self.name}: {ans}")
        # Add assistant answer to history
        self.messages.append({"role": "assistant", "content": ans})
        # Purge temporary tool messages now that we finalized the answer
        if self._temp_tool_messages:
            self.messages = [
                m for m in self.messages if m not in self._temp_tool_messages
            ]
            self._temp_tool_messages.clear()
        print(f"Performance de {self.name}: {time.time() - last_time}")
        return ans

    def run_tools(self, response) -> None:
        tools = response.choices[0].message.tool_calls
        print(f"{len(tools)} tools need to be called!")
        # Append the tool-call message temporarily
        self.messages.append(response.choices[0].message)
        self._temp_tool_messages.append(response.choices[0].message)

        # Ensure reset_history (if present) runs last
        ordered_tools = []
        reset_tools = []
        for t in tools:
            if t.function.name == "reset_history":
                reset_tools.append(t)
            else:
                ordered_tools.append(t)
        ordered_tools.extend(reset_tools)

        has_others_tools = len(ordered_tools) - len(reset_tools) > 0

        for tool in ordered_tools:
            function_name = tool.function.name
            function_args = json.loads(tool.function.arguments)
            print(f"function_name: {function_name}")
            print(f"function_args: {function_args}")
            # Special-case: reset history
            if function_name == "reset_history":
                # If reset_history is called alongside other tools, do not reset
                if has_others_tools:
                    function_response = "no es posible limpiar el chat durante le ejecucion de otras herramientas"
                    print(f"{tool.function.name}: {function_response}")
                else:
                    try:
                        function_response = self.reset_history()
                        print(f"{tool.function.name}: {function_response[:100]}")
                    except Exception as exc:
                        print(f"{tool.function.name}: {exc}")
                        function_response = self.error_response.format(
                            tool_name=function_name, tool_args=function_args
                        )
            else:
                function_to_call = self.functions[function_name]
                try:
                    function_response = function_to_call(
                        **function_args,
                    )
                    print(f"{tool.function.name}: {function_response[:100]}")
                except Exception as exc:
                    print(f"{tool.function.name}: {exc}")
                    function_response = self.error_response.format(
                        tool_name=function_name, tool_args=function_args
                    )
                finally:
                    tool_msg = {
                        "tool_call_id": tool.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                    self.messages.append(tool_msg)
                    self._temp_tool_messages.append(tool_msg)

    def reset_history(self) -> str:
        """Borra el historial dejando solo el prompt inicial (si existe)."""
        if getattr(self, "_initial_system_msg", None):
            self.messages = [
                self._initial_system_msg.copy(), # type: ignore
                {
                    "role": "system",
                    "content": "historial eliminado. Preséntate ante el usuario y explícale que la conversación ha sido reiniciada.",
                },
            ]
        else:
            self.messages = []

        return "Historial borrado."

    def _build_http_client_with_proxy(self):
        """
        Construye un httpx.Client con proxy si las variables de entorno existen.
        Variables soportadas:
          - PROXY_URL (p.ej. http://user:pass@host:port)
          - o bien PROXY_SCHEME (http/https), PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS
        Si no hay configuración, devuelve None (sin proxy).
        """
        proxy_url = os.getenv("PROXY_URL")

        if not proxy_url:
            host = os.getenv("PROXY_HOST")
            port = os.getenv("PROXY_PORT")
            user = os.getenv("PROXY_USER")
            password = os.getenv("PROXY_PASS")
            scheme = os.getenv("PROXY_SCHEME", "http")

            if host and port:
                if user and password:
                    user_enc = urllib.parse.quote(user, safe="")
                    pass_enc = urllib.parse.quote(password, safe="")
                    proxy_url = f"{scheme}://{user_enc}:{pass_enc}@{host}:{port}"
                else:
                    proxy_url = f"{scheme}://{host}:{port}"

        if proxy_url:
            # En esta versión de httpx usamos el parámetro 'proxy'
            return httpx.Client(proxy=proxy_url)

        return None


if __name__ == "__main__":
    # 1) Mapeo de funciones disponibles para tools
    functions = {
        "get_current_datetime": get_current_datetime,
        "get_current_weather": get_current_weather,
        "send_email": send_email,
        "manipulate_xlsx": manipulate_xlsx,
        "execute_query": execute_query,
        "execute_mssql_query": execute_mssql_query,
    }

    # 2) Prompt del sistema (contexto)
    prompt = f"""
Eres un asistente que puede utilizar herramientas. 
- Tienes acceso a bases de datos (PostgreSQL y SQL Server); si necesitas consultarlas solo tienes permitido realizar consultas SELECT.
- Puedes usar: clima, fecha/hora, envío de correo, manipulación de archivos .xlsx y consultas SQL de solo lectura.
- Sé conciso y responde en español.
Tablas conocidas de la BD: {table_names}
"""

    # 3) Instanciar el chatbot
    bot = Completions(
        name="Avangenio Agent",
        model="agent-xs",
        json_tools=tools,
        functions=functions,
        prompt=prompt,
    )

    # 4) Bucle interactivo
    print("\nComenzando chat. Comandos:")
    print("  /exit  -> salir")
    print("")

    while True:
        try:
            user_input = input("Tú> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSaliendo…")
            break

        if not user_input:
            continue

        if user_input.lower() in ("/exit", "/quit", ":q"):
            print("Saliendo…")
            break

        # Enviar mensaje al modelo (la clase maneja el historial internamente)
        try:
            ans = bot.submit_message(user_input)
        except Exception as e:
            print(f"Error: {e}")
            continue
