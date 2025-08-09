import asyncio
import json
import time
from concurrent.futures import ThreadPoolExecutor

from dotenv import get_key, load_dotenv
from openai import AsyncOpenAI, OpenAI

from functions import query_exec, async_query_exec, get_current_datetime, async_get_current_datetime, get_current_weather, async_get_current_weather
from tools import tools

load_dotenv(".env")


class Completions:
    def __init__(
        self,
        api_key,
        name="Completions",
        model="gpt-5",
        messages=[],
        json_tools=[],
        functions={},
        tool_choice="auto",
        error_response="Ha ocurrido un error",
    ):
        self.__client = OpenAI(api_key=api_key)
        self.name: str = name
        self.__model: str = model
        self.__json_tools: list = json_tools
        self.__functions: dict = functions
        self.__tool_choice: str = tool_choice
        self.__error_response: str = error_response
        self.__response = None
        self.__messages = messages
        self.__roles = ["user", "assistant", "system", "tool"]

    def set_messages(self, messages: list[dict]):
        if messages:
            for id, msg in enumerate(messages):
                if msg["role"] not in self.__roles:
                    print(
                        f"Invalid role {msg['role']} in the {id + 1} message, must be one of: {self.__roles}"
                    )
                    return False

            self.__messages = messages
            return True

    def get_messages(self):
        return self.__messages

    def add_msg(self, message: str, role: str):
        if role in self.__roles:
            self.__messages.append(
                {
                    "role": role,
                    "content": message,
                }
            )
            return True

        print(f"Invalid role {role}, must be one of: {self.__roles}")
        return False

    def send_message(self, message: str) -> str | None:
        self.__last_time = time.time()
        print(f"Running {self.__model} with {len(self.__functions)} tools")
        self.add_msg(message, "user")

        while True:
            self._generate_response()

            functions_called = [
                item for item in self.__response.output if item.type == "function_call"
            ]

            custom_tools_called = [
                item
                for item in self.__response.output
                if item.type == "custom_tool_call"
            ]

            if not functions_called and not custom_tools_called:
                break

            if functions_called:
                self._run_functions(functions_called)

            if custom_tools_called:
                self._run_custom_tools(custom_tools_called)

        return self._get_response()

    def _generate_response(self):
        if self.__model == "gpt-5":
            self.__response = self.__client.responses.create(
                model=self.__model,
                input=self.__messages,
                tools=self.__json_tools,
                tool_choice=self.__tool_choice,  # type: ignore
                text={"verbosity": "low"},
                reasoning={"effort": "minimal"},
            )
        else:
            self.__response = self.__client.responses.create(
                model=self.__model,
                input=self.__messages,
                tools=self.__json_tools,
                tool_choice=self.__tool_choice,  # type: ignore
            )

        self.__messages += self.__response.output

    def _get_response(self):
        # print(self._Completions__response.model_dump_json(indent=2))

        for item in self.__response.output:
            if item.type == "message":
                ans = item.content[0].text
                print(f"{self.__model}: {ans}")
                print(f"Performance de {self.__model}: {time.time() - self.__last_time}")
                return ans

        return "No Answer"

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

            self.__messages.append(
                {
                    "type": "function_call_output",
                    "call_id": tool.call_id,
                    "output": str(function_response),
                }
            )


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
        self._Completions__messages.append(
            {
                "type": "function_call_output",
                "call_id": tool.call_id,
                "output": str(function_response),
            }
        )


class Completions_v3(Completions):
    def __init__(
        self,
        api_key,
        name="Completions (async)",
        model="gpt-5",
        messages=[],
        json_tools=[],
        functions={},
        tool_choice="auto",
        error_response="Ha ocurrido un error",
    ):
        self.__async_client = AsyncOpenAI(api_key=api_key)
        super().__init__(
            api_key,
            name,
            model,
            messages,
            json_tools,
            functions,
            tool_choice,
            error_response,
        )

    async def send_message(self, message: str) -> str | None:
        self._Completions__last_time = time.time()
        print(
            f"Running {self._Completions__model} with {len(self._Completions__functions)} tools"
        )
        self.add_msg(message, "user")

        while True:
            self._generate_response()

            functions_called = [
                item
                for item in self._Completions__response.output
                if item.type == "function_call"
            ]

            custom_tools_called = [
                item
                for item in self._Completions__response.output
                if item.type == "custom_tool_call"
            ]

            if functions_called:
                await self._run_functions(functions_called)
                continue

            if custom_tools_called:
                await self._run_custom_tools(custom_tools_called)
                continue

            break

        return self._get_response()

    async def _run_functions(
        self,
        functions_called,
    ) -> None:
        print(f"{len(functions_called)} tools need to be called!")

        tasks = []
        for tool in functions_called:
            function_name = tool.name
            print(f"function_name: {function_name}")
            function_to_call = self._Completions__functions[function_name]

            function_args = json.loads(tool.arguments)
            print(f"function_args: {function_args}")

            tasks.append(function_to_call(**function_args))

        results: list[str] = await asyncio.gather(*tasks, return_exceptions=True)

        self._set_tool_answers(functions_called, results)

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

            self._Completions__messages.append(
                {
                    "type": "function_call_output",
                    "call_id": tool.call_id,
                    "output": str(function_response),
                }
            )


if __name__ == "__main__":
    async_functions = {
        "get_current_datetime": async_get_current_datetime,
        "get_current_weather": async_get_current_weather,
        "query_exec": async_query_exec,
    }

    functions = {
        "get_current_datetime": get_current_datetime,
        "get_current_weather": get_current_weather,
        "query_exec": query_exec,
    }

    bot = Completions_v3(
        api_key=get_key(".env", "OPENAI_API_KEY"),
        functions=async_functions,
        json_tools=tools,
        model="gpt-5",
    )

    msg = """
        cuantos usuarios hay en la base de datos
        """

    #bot.send_message(msg)
    asyncio.run(bot.send_message(msg))
