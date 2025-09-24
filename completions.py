import asyncio
import json
import time
from concurrent.futures import ThreadPoolExecutor

from dotenv import get_key, load_dotenv
from openai import AsyncOpenAI, OpenAI

from enumerations import EffortType, MessageType, ModelType, VerbosityType
from functions import (
    async_get_current_datetime,
    async_get_current_weather,
    get_current_datetime,
    get_current_weather,
)
from tools.pg_tool import execute_query, async_execute_query
from json_tools import tools, table_names
from tools.email_tool import send_email, async_send_email
from tools.excel_tool import manipulate_xlsx, async_manipulate_xlsx

load_dotenv(".env")


class Completions:
    def __init__(
        self,
        api_key,
        name="Completions",
        model=ModelType.GPT_5.value,
        base_url = None,
        prompt="",
        json_tools=[],
        functions={},
        tool_choice="auto",
        error_response="Ha ocurrido un error",
    ):
        if base_url:
            self.__client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.__client = OpenAI(api_key=api_key)
            
        self.name: str = name
        self.__model: str = model
        self.__json_tools: list = json_tools
        self.__functions: dict = functions
        self.__tool_choice: str = tool_choice
        self.__error_response: str = error_response
        self.__response = None
        if prompt:
            self.__messages = [
                {
                    "role": MessageType.DEVELOPER.value,
                    "content": prompt,
                }
            ]
            # Save initial prompt message for future resets
            self.__initial_prompt_msg = self.__messages[0].copy()
        else:
            self.__messages = []
            self.__initial_prompt_msg = None
        # Track tool messages temporarily to purge them after final assistant answer
        self.__temp_tool_messages: list = []
    
    # Shared helpers to reduce duplication across sync/async implementations
    def _web_search_enabled(self) -> bool:
        # Detect flag regardless of subclass name mangling
        for attr in ("_Completions__web_search", "_AsyncCompletions__web_search", "__web_search"):
            if getattr(self, attr, False):
                return True
        return False

    def _prepare_web_search_tools(self) -> None:
        if self._web_search_enabled():
            try:
                if isinstance(self.__json_tools, list):
                    if not any(isinstance(t, dict) and t.get("type") == "web_search_preview" for t in self.__json_tools):
                        self.__json_tools.append({"type": "web_search_preview"})
            except AttributeError:
                pass

    def _build_response_params(self) -> dict:
        params = {
            "model": self.__model,
            "input": self.__messages,
            "tools": self.__json_tools,
            "tool_choice": self.__tool_choice,  # type: ignore
        }

        if self.__model == ModelType.GPT_5.value:
            params.update({"text": {"verbosity": VerbosityType.LOW.value}})
            # Reasoning effort cannot be used with web_search tools
            if not self._web_search_enabled():
                params.update({"reasoning": {"effort": EffortType.MINIMAL.value}})
                
        return params
            

    def set_messages(self, messages: list[dict]):
        if messages:
            for id, msg in enumerate(messages):
                if not MessageType.has_value(msg["role"]):
                    print(
                        f"Invalid role {msg['role']} in the {id + 1} message, must be one of: {MessageType.list_values()}"
                    )
                    return False

            self.__messages = messages
            return True

        print("messages is empty")
        return False

    def get_messages(self):
        return self.__messages

    def reset_history(self):
        """Clear conversation history leaving only the initial prompt (if any)."""
        if getattr(self, "_Completions__initial_prompt_msg", None):
            self.__messages = [self.__initial_prompt_msg.copy()]
        else:
            self.__messages = []
        return True

    def add_msg(self, message: str, role: str):
        if MessageType.has_value(role):
            self.__messages.append(
                {
                    "role": role,
                    "content": message,
                }
            )
            return True

        print(f"Invalid role {role}, must be one of: {MessageType.list_values()}")
        return False

    def send_message(self, message: str, web_search: bool = False) -> str | None:
        self.__last_time = time.time()
        self.__web_search = web_search
        print(f"Running {self.__model} with {len(self.__functions)} tools")
        self.add_msg(message, MessageType.USER.value)

        while True:
            self._generate_response()

            functions_called = [
                item
                for item in self.__response.z
                if item.type == MessageType.FUNCTION_CALL.value
            ]

            custom_tools_called = [
                item
                for item in self.__response.output
                if item.type == MessageType.CUSTOM_TOOL_CALL.value
            ]

            if not functions_called and not custom_tools_called:
                break

            if functions_called:
                self._run_functions(functions_called)

            if custom_tools_called:
                self._run_custom_tools(custom_tools_called)

        return self._get_response()

    def _generate_response(self):
        self._prepare_web_search_tools()
        params = self._build_response_params()
        self.__response = self.__client.responses.create(**params)
        # Append outputs and mark tool-call items as temporary
        for item in self.__response.output:
            self.__messages.append(item)
            if getattr(item, "type", "") in (
                MessageType.FUNCTION_CALL.value,
                MessageType.CUSTOM_TOOL_CALL.value,
            ):
                self.__temp_tool_messages.append(item)

    def _get_response(self):
        # print(self._Completions__response.model_dump_json(indent=2))

        for item in self.__response.output:
            if item.type == "message":
                ans = item.content[0].text
                print(f"{self.__model}: {ans}")

                self.add_msg(ans, MessageType.ASSISTANT.value)

                # Purge temporary tool messages from history after finalizing answer
                self._purge_temp_tool_messages()

                print(
                    f"Performance de {self.__model}: {time.time() - self.__last_time}"
                )
                return ans

        return "No Answer"

    def _purge_temp_tool_messages(self):
        # Remove any tool-related temporary messages from the conversation history
        if getattr(self, "_Completions__temp_tool_messages", None):
            self.__messages = [
                m for m in self.__messages if m not in self.__temp_tool_messages
            ]
            self.__temp_tool_messages.clear()

    def _run_functions(
        self,
        functions_called,
    ) -> None:
        print(f"{len(functions_called)} functions need to be called!")

        with ThreadPoolExecutor() as executor:
            futures = []
            for tool in functions_called:
                function_name = tool.name
                print(f"function_name: {function_name}")

                # Handle built-in tool: reset_history
                if function_name == "reset_history":
                    def run_reset():
                        self.reset_history()
                        return "Historial borrado."
                    futures.append(executor.submit(run_reset))
                    continue

                function_to_call = self.__functions[function_name]

                function_args = json.loads(tool.arguments)
                print(f"function_args: {function_args}")

                futures.append(executor.submit(function_to_call, **function_args))

            self._set_tool_answers(futures, functions_called)

    def _run_custom_tools(
        self,
        custom_tools_called,
    ) -> None:
        print(f"{len(custom_tools_called)} custom tools need to be called!")

        with ThreadPoolExecutor() as executor:
            futures = []
            for tool in custom_tools_called:
                print(f"Custom tool name: {tool.name}")
                function_to_call = self.__functions[tool.name]
                print(f"Custom tool input: {tool.input}")

                futures.append(executor.submit(function_to_call, tool.input))

            self._set_tool_answers(futures, custom_tools_called)

    def _set_tool_answers(self, futures, tools):
        for future, tool in zip(futures, tools):
            try:
                function_response = future.result()
                print(f"{tool.name}: {function_response[:100]}")  # type: ignore
            except Exception as exc:
                print(f"{tool.name}: {exc}")
                function_response = self.__error_response

            msg = {
                "type": "function_call_output",
                "call_id": tool.call_id,
                "output": str(function_response),
            }
            self.__messages.append(msg)
            self.__temp_tool_messages.append(msg)


class Completions_v2(Completions):
    def _run_functions(
        self,
        functions_called,
    ) -> None:
        print(f"{len(functions_called)} functions need to be called!")

        for tool in functions_called:
            function_name = tool.name
            print(f"function_name: {function_name}")
            function_to_call = self._Completions__functions[function_name]

            function_args = json.loads(tool.arguments)
            print(f"function_args: {function_args}")

            try:
                function_response = function_to_call(**function_args)
                print(f"{tool._Completions__model}: {function_response[:100]}")  # type: ignore

            except Exception as exc:
                print(f"{tool.name}: {exc}")
                function_response = self._Completions__error_response

            self._set_tool_answer(tool, function_response)

    def _run_custom_tools(
        self,
        custom_tools_called,
    ) -> None:
        print(f"{len(custom_tools_called)} custom tools need to be called!")

        for tool in custom_tools_called:
            print(f"function_name: {tool.name}")
            function_to_call = self._Completions__functions[tool.name]
            print(f"Input tool: {tool.input}")

            try:
                function_response = function_to_call(tool.input)
                print(f"{tool.name}: {function_response[:100]}")  # type: ignore

            except Exception as exc:
                print(f"{tool.name}: {exc}")
                function_response = self._Completions__error_response

            self._set_tool_answer(tool, function_response)

    def _set_tool_answer(self, tool, function_response):
        msg = {
            "type": "function_call_output",
            "call_id": tool.call_id,
            "output": str(function_response),
        }
        self._Completions__messages.append(msg)
        self._Completions__temp_tool_messages.append(msg)


class AsyncCompletions(Completions):
    def __init__(
        self,
        api_key,
        name="Completions (async)",
        model=ModelType.GPT_5.value,
        base_url = None,
        prompt="",
        json_tools=[],
        functions={},
        tool_choice="auto",
        error_response="Ha ocurrido un error",
    ):
        if base_url:
            self.__async_client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        else:
            self.__async_client = AsyncOpenAI(api_key=api_key)

        super().__init__(
            api_key,
            name,
            model,
            base_url,
            prompt,
            json_tools,
            functions,
            tool_choice,
            error_response,
        )

    async def send_message(self, message: str, web_search: bool = False) -> str | None:
        self._Completions__last_time = time.time()
        self.__web_search = web_search
        print(
            f"Running {self._Completions__model} with {len(self._Completions__functions)} tools"
        )
        self.add_msg(message, MessageType.USER.value)

        while True:
            await self._generate_response()

            functions_called = [
                item
                for item in self._Completions__response.output
                if item.type == MessageType.FUNCTION_CALL.value
            ]

            custom_tools_called = [
                item
                for item in self._Completions__response.output
                if item.type == MessageType.CUSTOM_TOOL_CALL.value
            ]

            if not functions_called and not custom_tools_called:
                break

            if functions_called:
                await self._run_functions(functions_called)

            if custom_tools_called:
                await self._run_custom_tools(custom_tools_called)

        return self._get_response()

    async def _generate_response(self):
        # Common preparation (reuse base helpers)
        self._prepare_web_search_tools()

        # Build common params and make async call
        params = self._build_response_params()
        self._Completions__response = await self.__async_client.responses.create(**params)

        # Append outputs to messages and mark tool-call items as temporary
        for item in self._Completions__response.output:
            self._Completions__messages.append(item)
            if getattr(item, "type", "") in (
                MessageType.FUNCTION_CALL.value,
                MessageType.CUSTOM_TOOL_CALL.value,
            ):
                self._Completions__temp_tool_messages.append(item)

    async def _run_functions(
        self,
        functions_called,
    ) -> None:
        print(f"{len(functions_called)} tools need to be called!")

        tasks = []
        for tool in functions_called:
            function_name = tool.name
            print(f"function_name: {function_name}")
            # Handle built-in tool: reset_history
            if function_name == "reset_history":
                tasks.append(self._async_reset_history())
                continue

            function_to_call = self._Completions__functions[function_name]

            function_args = json.loads(tool.arguments)
            print(f"function_args: {function_args}")

            tasks.append(function_to_call(**function_args))

        results: list[str] = await asyncio.gather(*tasks, return_exceptions=True)

        self._set_tool_answers(functions_called, results)

    async def _async_reset_history(self):
        self.reset_history()
        return "Historial borrado."

    async def _run_custom_tools(
        self,
        custom_tools_called,
    ) -> None:
        print(f"{len(custom_tools_called)} custom tools need to be called!")

        tasks = []
        for tool in custom_tools_called:
            print(f"function_name: {tool.name}")
            function_to_call = self._Completions__functions[tool.name]

            print(f"Input tool: {tool.input}")

            tasks.append(function_to_call(tool.input))

        results: list[str] = await asyncio.gather(*tasks, return_exceptions=True)

        self._set_tool_answers(custom_tools_called, results)

    def _set_tool_answers(self, tools, results):
        for tool, function_response in zip(tools, results):
            if isinstance(function_response, Exception):
                print(f"{tool.name}: {function_response}")
                function_response = self._Completions__error_response
            else:
                print(f"{tool.name}: {function_response[:100]}")  # type: ignore

            msg = {
                "type": "function_call_output",
                "call_id": tool.call_id,
                "output": str(function_response),
            }
            self._Completions__messages.append(msg)
            self._Completions__temp_tool_messages.append(msg)


if __name__ == "__main__":
    async_functions = {
        "get_current_datetime": async_get_current_datetime,
        "get_current_weather": async_get_current_weather,
        "execute_query": async_execute_query,
        "send_email": async_send_email,
        "manipulate_xlsx": async_manipulate_xlsx,
    }

    functions = {
        "get_current_datetime": get_current_datetime,
        "get_current_weather": get_current_weather,
        "execute_query": execute_query,
        "send_email": send_email,
        "manipulate_xlsx": manipulate_xlsx,
    }

    prompt = f"""
        Solo ejecuta consultas SQL de lectura. La base de datos a la que tienes acceso es de Odoo 17. Estas son las tablas disponibles: {table_names}
    """

    async_bot = AsyncCompletions(
        api_key=get_key(".env", "OPENAI_API_KEY"),
        prompt=prompt,
        functions=async_functions,
        json_tools=tools,
    )

    bot = Completions(
        api_key=get_key(".env", "OPENAI_API_KEY"),
        prompt=prompt,
        functions=functions,
        json_tools=tools,
    )

    async def chat_loop():
        web_search = True
        print("\nComenzando chat. Comandos disponibles:")
        print("  /exit                -> salir")
        print("  /web on              -> activar web search")
        print("  /web off             -> desactivar web search")
        print("")

        while True:
            user_input = await asyncio.to_thread(input, "Tú> ")
            if user_input is None:
                continue
            text = user_input.strip()
            if not text:
                continue

            if text.lower() in ("/exit", "/quit", ":q"):
                print("Saliendo…")
                break

            if text.lower() in ("/web on", "/web_on", "/webon"):
                web_search = True
                print("Web search ACTIVADO")
                continue

            if text.lower() in ("/web off", "/web_off", "/weboff"):
                web_search = False
                print("Web search DESACTIVADO")
                continue

            # Send message to async bot
            try:
                await async_bot.send_message(text, web_search=web_search)
            except Exception as e:
                print(f"Error: {e}")

    asyncio.run(chat_loop())
