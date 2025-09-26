import sys
import os
from typing import Optional
from agent_v2 import Agent as AvangenioAgent
from agent import Agent as OpenAIAgent
from tools import AVAILABLE_FUNCTIONS as rag_functions


try:
    if os.getenv("AGENT_VERSION") == "OPENAI":
        from json_tools import tools as rag_prompt
    else:
        from json_tools_v2 import tools as rag_prompt
except ImportError:
    print("Warning: RAG prompt tools not available")
    rag_prompt = []


class ConsoleChat:
    """Interactive console chat interface for the Agent."""

    def __init__(
        self,
        agent_name: str = "Assistant",
    ):
        agent_version = os.getenv("AGENT_VERSION").upper()

        if agent_version == "OPENAI":
            openai_model = os.getenv("OPENAI_MODEL")
            self.agent = OpenAIAgent(name=agent_name, model=openai_model)
            print(f"Using OpenAI Agent with model: {openai_model}")
        else:
            avangenio_model = os.getenv("AVANGENIO_MODEL")

            proxy_url = os.getenv("HTTP_PROXY")
            if proxy_url:
                print(f"Proxy detectado: {proxy_url[:50]}...")
                self.agent = AvangenioAgent(
                    name=agent_name, model=avangenio_model, proxy_url=proxy_url
                )
            else:
                self.agent = AvangenioAgent(name=agent_name, model=avangenio_model)

            print(f"Using Avangenio Agent with model: {avangenio_model}")

        self.user_id = 1  # Using a fixed channel ID for console chat
        self.running = True

        # Console colors for better UX
        self.COLORS = {
            "user": "\033[94m",  # Blue
            "agent": "\033[92m",  # Green
            "system": "\033[93m",  # Yellow
            "error": "\033[91m",  # Red
            "reset": "\033[0m",  # Reset
        }

    def print_colored(self, text: str, color: str = "reset", end: str = "\n") -> None:
        """Print text with color."""
        print(f"{self.COLORS.get(color, '')}{text}{self.COLORS['reset']}", end=end)

    def print_welcome(self) -> None:
        """Print welcome message and instructions."""
        self.print_colored("=" * 60, "system")
        self.print_colored(
            f"  Bienvenido al Chat de Consola con {self.agent.name}", "system"
        )
        self.print_colored("=" * 60, "system")
        self.print_colored("\nComandos disponibles:", "system")
        self.print_colored("  /help    - Mostrar esta ayuda", "system")
        self.print_colored("  /clear   - Limpiar historial de conversación", "system")
        self.print_colored("  /exit    - Salir del chat", "system")
        self.print_colored("  /quit    - Salir del chat", "system")
        self.print_colored(
            "\nEscribe tu mensaje y presiona Enter para enviar.", "system"
        )
        self.print_colored("=" * 60, "system")

    def handle_command(self, command: str) -> bool:
        """
        Handle special commands.

        Args:
            command: The command to handle

        Returns:
            True if the command was handled, False if it's a regular message
        """
        command = command.strip().lower()

        if command in ["/exit", "/quit"]:
            self.print_colored("\n¡Hasta luego! Cerrando el chat...", "system")
            self.running = False
            return True

        elif command == "/clear":
            self.agent.chat_memory.delete_chat(self.user_id)
            self.print_colored("\n✓ Historial de conversación limpiado.", "system")
            return True

        elif command == "/help":
            self.print_colored("\nComandos disponibles:", "system")
            self.print_colored("  /help    - Mostrar esta ayuda", "system")
            self.print_colored(
                "  /clear   - Limpiar historial de conversación", "system"
            )
            self.print_colored("  /exit    - Salir del chat", "system")
            self.print_colored("  /quit    - Salir del chat", "system")
            return True

        return False

    def get_user_input(self) -> Optional[str]:
        """
        Get user input with proper handling.

        Returns:
            User input string or None if interrupted
        """
        try:
            self.print_colored("\nTú: ", "user", end="")
            user_input = input().strip()
            return user_input
        except KeyboardInterrupt:
            self.print_colored("\n\n¡Hasta luego! (Ctrl+C detectado)", "system")
            return None
        except EOFError:
            self.print_colored("\n\n¡Hasta luego! (EOF detectado)", "system")
            return None

    def tool_execution_callback(self, message: str) -> None:
        content = f"🔧 {self.agent.name}: {message}"
        width = max(50, len(content) + 4)  # Minimum 50 chars, or content + padding

        print("\n" + "=" * width)
        print(f"= {content:<{width - 4}} =")
        print("=" * width)

    def process_message(self, message: str) -> None:
        """
        Process a user message and get agent response.

        Args:
            message: The user message to process
        """
        try:
            # Show thinking indicator
            self.print_colored(f"\n{self.agent.name} está pensando...", "system")

            response = self.agent.process_msg(
                message,
                self.user_id,
                rag_functions=rag_functions,
                rag_prompt=rag_prompt,
                tool_execution_callback=self.tool_execution_callback,
            )

            if response:
                self.print_colored(f"\n{self.agent.name}: ", "agent", end="")
                self.print_colored(response, "agent")
            else:
                self.print_colored(
                    f"\n{self.agent.name}: Lo siento, no pude procesar tu mensaje.",
                    "error",
                )

        except Exception as e:
            self.print_colored(f"\nError al procesar el mensaje: {str(e)}", "error")
            self.print_colored("Por favor, intenta de nuevo.", "error")

    def run(self) -> None:
        """Run the main conversation loop."""
        self.print_welcome()

        while self.running:
            user_input = self.get_user_input()

            if user_input is None:
                break

            if not user_input:
                continue

            if user_input.startswith("/"):
                self.handle_command(user_input)
                continue

            self.process_message(user_input)

        self.print_colored("\n¡Gracias por usar el chat de consola!", "system")


def main():
    try:
        chat = ConsoleChat(agent_name="Console Agent")
        chat.run()
    except Exception as exc:
        print(f"Error al inicializar el chat: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
