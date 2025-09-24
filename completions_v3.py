import asyncio
import json
import sys
import pathlib
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Optional

# Add project root to sys.path for direct execution
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI
from proxy_config import ProxyConfig

from enumerations import (
    EffortType,
    MessageType,
    ModelType,
    VerbosityType,
)
from prompt import SYSTEM_PROMPT


load_dotenv(".env")


class SetMessagesError(Exception):
    pass


class GetMessagesError(Exception):
    pass


class FunctionDoesNotExist(Exception):
    pass


class ChatMemory:
    def __init__(self, prompt=SYSTEM_PROMPT):
        self.__ai_output: dict[int, Any] = {}
        self.__messages: dict[int, list[dict]] = {}
        self.__pos_tool_msgs: dict[int, list[int]] = {}
        self.init_msg = {
            "role": MessageType.SYSTEM.value,
            "content": prompt,
        }
        self.__last_time: float

    def _get_ai_output(self, user_id: int):
        if user_id not in self.__ai_output:
            raise GetMessagesError(f"{user_id} not found in memory")

        return self.__ai_output[user_id]

    def _get_pos_tool_msgs(self, user_id: int):
        if user_id not in self.__pos_tool_msgs:
            return []
        return self.__pos_tool_msgs[user_id]

    def get_messages(self, user_id: int, with_prompt: bool = True):
        if user_id not in self.__messages:
            print(f"{user_id} not found in memory")
            self.init_chat(user_id)

        if with_prompt:
            return self.__messages[user_id]
        else:
            return self.__messages[user_id][1:]

    def reduce_context(self, user_id: int):
        if len(self.__messages[user_id]) < 20:
            return

        new_messages = [self.__messages[user_id][0]]
        last_idx = len(self.__messages) - 1

        for idx, msg in enumerate(self.__messages[user_id][10:], start=10):
            if msg["role"] == MessageType.USER.value:
                new_messages += self.__messages[user_id][idx:last_idx]

        self.__messages[user_id] = new_messages

    def get_last_time(self):
        return self.__last_time

    def _set_ai_output(self, ai_output, user_id: int):
        self.__ai_output[user_id] = ai_output

    def _set_tool_calls(self, user_id: int):
        if user_id not in self.__messages:
            print(f"{user_id} not found in memory")
            return False

        ai_output = self._get_ai_output(user_id)
        message = ai_output.choices[0].message

        # Convert the message to a proper dictionary format
        tool_call_msg = {
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    },
                }
                for tool_call in message.tool_calls
            ],
        }

        self.__messages[user_id].append(tool_call_msg)
        if user_id not in self.__pos_tool_msgs:
            self.__pos_tool_msgs[user_id] = [len(self.__messages[user_id]) - 1]
        else:
            self.__pos_tool_msgs[user_id].append(len(self.__messages[user_id]) - 1)

    def _clean_tool_msgs(self, user_id: int):
        if user_id not in self.__pos_tool_msgs:
            print(f"{user_id} not have tool messages")

        self.__pos_tool_msgs[user_id] = []

    def has_chat(self, user_id: int) -> bool:
        return user_id in self.__messages and len(self.__messages[user_id]) > 0

    def delete_chat(self, user_id: int) -> None:
        if user_id in self.__messages:
            del self.__messages[user_id]
        if user_id in self.__pos_tool_msgs:
            del self.__pos_tool_msgs[user_id]
        if user_id in self.__ai_output:
            del self.__ai_output[user_id]

    def init_chat(self, user_id: int):
        self.set_messages([self.init_msg], user_id)
        print(f"New chat for {user_id}")

    def add_msg(self, message: str, role: str, user_id: int):
        if user_id not in self.__messages:
            self.init_chat(user_id)

        if MessageType.has_value(role):
            self.__messages[user_id].append(
                {
                    "role": role,
                    "content": message,
                }
            )
            print(f"New message from {role} added to chat of {user_id}")
            return True

        print(f"Invalid role {role}, must be one of: {MessageType.list_values()}")
        return False

    def set_messages(self, messages: list[dict[str, str]], user_id: int):
        if not isinstance(messages, list):
            raise SetMessagesError(f"messages must be a list, not {type(messages)}")

        for id, msg in enumerate(messages):
            if not MessageType.has_value(msg["role"]):
                raise SetMessagesError(
                    f"Invalid role {msg['role']} in the {id + 1} message, must be one of: {MessageType.list_values()}"
                )

        self.__messages[user_id] = messages

    def _get_ai_msg(self, user_id: int):
        ai_output = self._get_ai_output(user_id)
        return ai_output.choices[0].message.content.strip()

    def _purge_tool_msgs(self, user_id: int):
        pos_tool_msgs = self._get_pos_tool_msgs(user_id)
        messages = self.get_messages(user_id)

        if pos_tool_msgs:
            clean_messages = [
                m for idx, m in enumerate(messages) if idx not in pos_tool_msgs
            ]
            try:
                self.set_messages(clean_messages, user_id)
                print(f"{len(messages) - len(clean_messages)} tool messages purged")
            except SetMessagesError as exc:
                print(f"Error purging tool messages: {exc}")
            finally:
                self._clean_tool_msgs(user_id)

    def _set_tool_output(self, call_id, function_out, user_id: int, function_name: str):
        # Store as ephemeral tool output; do not persist in history
        if user_id not in self.__messages:
            print(f"{user_id} not found in memory")
            return False

        # Serialize function output to string if it's not already a string
        if isinstance(function_out, (dict, list)):
            content = json.dumps(function_out, ensure_ascii=False)
        else:
            content = str(function_out)

        msg = {
            "tool_call_id": call_id,
            "role": "tool",
            "name": function_name,
            "content": content,
        }

        self.__messages[user_id].append(msg)
        if user_id not in self.__pos_tool_msgs:
            self.__pos_tool_msgs[user_id] = [len(self.__messages[user_id]) - 1]
        else:
            self.__pos_tool_msgs[user_id].append(len(self.__messages[user_id]) - 1)


class AIClient:
    def __init__(self, api_key: str, base_url: str = None, proxy_url: Optional[str] = None):
        """
        Initialize AI Client with optional proxy support.
        
        Args:
            api_key: OpenAI API key
            base_url: Custom base URL for API
            proxy_url: HTTP proxy URL in format: http://username:password@host:port
        """
        # Configure proxy using ProxyConfig class
        self.proxy_config = ProxyConfig(proxy_url)
        
        # Create HTTP clients with proxy configuration
        http_client = None
        async_http_client = None
        
        if self.proxy_config.proxy_url and self.proxy_config.is_valid:
            http_client = self.proxy_config.create_sync_client()
            async_http_client = self.proxy_config.create_async_client()
            print(f"Proxy configured: {self.proxy_config.get_proxy_info()}")
        else:
            print("No proxy configured or invalid proxy URL")
        
        if base_url:
            self.__client = OpenAI(
                api_key=api_key, 
                base_url=base_url,
                http_client=http_client
            )
            self.__async_client = AsyncOpenAI(
                api_key=api_key, 
                base_url=base_url,
                http_client=async_http_client
            )
        else:
            self.__client = OpenAI(
                api_key=api_key,
                http_client=http_client
            )
            self.__async_client = AsyncOpenAI(
                api_key=api_key,
                http_client=async_http_client
            )

    async def _async_gen_ai_output(self, params: dict):
        ai_output = await self.__async_client.client.chat.completions.create(**params)
        return ai_output

    def _gen_ai_output(self, params: dict):
        return self.__client.chat.completions.create(**params)


class ToolRunner:
    def __init__(
        self,
        error_msg="Ha ocurrido un error inesperado",
    ):
        self.ERROR_MSG = error_msg

    def _run_functions(
        self, functions_called, user_id: int, chat_memory: ChatMemory, rag_functions
    ) -> None:
        print(f"{len(functions_called)} functions need to be called!")

        with ThreadPoolExecutor() as executor:
            futures = []
            for tool in functions_called:
                function_name = tool.function.name
                function_args = tool.function.arguments
                print(f"function_name: {function_name}")
                print(
                    f"function_args: {function_args[:100]}{'...' if len(function_args) > 100 else ''}"
                )

                if function_name not in rag_functions:
                    raise FunctionDoesNotExist(
                        f"{function_name} not available in {rag_functions.keys()}"
                    )

                function_to_call = rag_functions[function_name]
                if function_args:
                    function_args = json.loads(function_args)
                    futures.append(executor.submit(function_to_call, **function_args))
                else:
                    futures.append(executor.submit(function_to_call))

            self.run_futures(futures, functions_called, user_id, chat_memory)

    def run_futures(self, futures, tools_called, user_id: int, chat_memory: ChatMemory):
        for future, tool in zip(futures, tools_called):
            try:
                function_out = future.result()
                print(f"{tool.function.name}: {function_out}")  # type: ignore
            except Exception as exc:
                print(f"{tool.function.name}: {exc}")
                function_out = self.ERROR_MSG

            chat_memory._set_tool_output(
                tool.id, function_out, user_id, tool.function.name
            )

    async def _async_run_functions(
        self, functions_called, user_id: int, chat_memory: ChatMemory, rag_functions
    ) -> None:
        print(f"{len(functions_called)} function need to be called!")
        tasks = []
        for tool in functions_called:
            function_name = tool.function.name
            function_args = tool.function.arguments
            print(f"function_name: {function_name}")
            print(
                f"function_args: {function_args[:100]}{'...' if len(function_args) > 100 else ''}"
            )

            if function_name not in rag_functions:
                raise FunctionDoesNotExist(
                    f"{function_name} not available in {rag_functions.keys()}"
                )

            function_to_call = rag_functions[function_name]  # type: ignore
            if function_args:
                function_args = json.loads(function_args)
                tasks.append(function_to_call(**function_args))
            else:
                tasks.append(function_to_call())

        await self.run_coroutines(functions_called, tasks, user_id, chat_memory)

    async def run_coroutines(
        self, tools_called, tasks, user_id: int, chat_memory: ChatMemory
    ):
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for tool, function_out in zip(tools_called, results):
            if isinstance(function_out, Exception):
                print(f"{tool.function.name}: {function_out}")
                function_out = self.ERROR_MSG  # type: ignore
            else:
                print(f"{tool.function.name}: {function_out}")  # type: ignore

            chat_memory._set_tool_output(
                tool.id, function_out, user_id, tool.function.name
            )


class Agent:
    def __init__(
        self,
        name="Odoo Agent",
        model=ModelType.AGENT_XS.value,
        prompt=SYSTEM_PROMPT,
        proxy_url: Optional[str] = None,
    ):
        self.name = name
        self.model = model
        self.chat_memory = ChatMemory(prompt=prompt)
        
        # Use proxy from parameter or environment variable
        proxy = proxy_url or os.getenv("HTTP_PROXY")
        
        self._ai_client = AIClient(
            api_key=os.getenv("AVANGENIO_API_KEY"),
            base_url="https://apigateway.avangenio.net",
            proxy_url=proxy,
        )  # type: ignore
        self._tool_runner = ToolRunner()

    def process_msg(
        self,
        message: str,
        user_id: int,
        rag_functions: dict = {},
        rag_prompt: list[dict] = [],
        tool_execution_callback=None,
    ) -> str | None:
        print(f"Running {self.model} with {len(rag_prompt)} tools")
        self.chat_memory.add_msg(message, MessageType.USER.value, user_id)
        counter = 1

        while True:
            print(f"{counter}° iteration")

            params = {
                "model": self.model,  # type: ignore
                "messages": self.chat_memory.get_messages(user_id),  # type: ignore
                "tools": rag_prompt,  # type: ignore
            }
            if self.model == ModelType.GPT_5.value:  # type: ignore
                params["text"] = {"verbosity": VerbosityType.LOW.value}
                params["reasoning"] = {"effort": EffortType.LOW.value}

            # print(self.chat_memory.get_messages(user_id, with_prompt=False))
            ai_output = self._ai_client._gen_ai_output(params)
            self.chat_memory._set_ai_output(ai_output, user_id)

            if not ai_output.choices[0].message.tool_calls:
                break

            # Call the callback with the assistant's message before tool execution
            if tool_execution_callback and ai_output.choices[0].message.content:
                tool_execution_callback(ai_output.choices[0].message.content)

            self.chat_memory._set_tool_calls(user_id)

            self._tool_runner._run_functions(
                ai_output.choices[0].message.tool_calls,
                user_id,
                self.chat_memory,
                rag_functions,
            )

            counter += 1

        self.chat_memory._purge_tool_msgs(user_id)
        ai_msg = self.chat_memory._get_ai_msg(user_id)
        # print(f"{self.name}: {ai_msg}")

        self.chat_memory.add_msg(ai_msg, MessageType.ASSISTANT.value, user_id)
        self.chat_memory.reduce_context(user_id)
        return ai_msg

    def verify_context_size(self, chat_id):
        if len(self.chat_memory.get_messages(chat_id)) > 20:
            self.chat_memory.delete_chat(chat_id)
            print("Chat memory exceeded limit, resetting chat.")
            return False

    async def async_process_msg(
        self,
        message: str,
        user_id: int,
        rag_functions: dict = {},
        rag_prompt: list[dict] = [],
        tool_execution_callback=None,
    ) -> str | None:
        print(f"Running {self.name} with {len(rag_prompt)} tools")
        self.chat_memory.add_msg(message, MessageType.USER.value, user_id)

        counter = 1
        while True:
            print(f"{counter}° iteration")

            params = {
                "model": self.model,  # type: ignore
                "messages": self.chat_memory.get_messages(user_id),  # type: ignore
                "tools": rag_prompt,  # type: ignore
            }
            if self.model == ModelType.GPT_5.value:  # type: ignore
                params["text"] = {"verbosity": VerbosityType.LOW.value}
                params["reasoning"] = {"effort": EffortType.MINIMAL.value}

            ai_output = await self._ai_client._async_gen_ai_output(params)
            self.chat_memory._set_ai_output(ai_output, user_id)

            if not ai_output.choices[0].message.tool_calls:
                break

            # Call the callback with the assistant's message before tool execution
            if tool_execution_callback and ai_output.choices[0].message.content:
                tool_execution_callback(ai_output.choices[0].message.content)

            self.chat_memory._set_tool_calls(user_id)

            await self._tool_runner._async_run_functions(
                ai_output.choices[0].message.tool_calls,
                user_id,
                self.chat_memory,
                rag_functions,
            )

            counter += 1

        self.chat_memory._purge_tool_msgs(user_id)
        ai_msg = self.chat_memory._get_ai_msg(user_id)
        # print(f"{self.name}: {ai_msg}")

        self.chat_memory.add_msg(ai_msg, MessageType.ASSISTANT.value, user_id)
        self.chat_memory.reduce_context(user_id)
        return ai_msg


# agent = Agent()  # Commented out to avoid initialization errors during import
