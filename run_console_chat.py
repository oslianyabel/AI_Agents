#!/usr/bin/env python3
"""
Example script to run the console chat with the Agent.
"""

from console_chat import ConsoleChat
from enumerations import ModelType
import os


def main():
    """Run the console chat example."""

    # Check if API key is configured
    if not os.getenv("AVANGENIO_API_KEY"):
        print(
            "⚠️  ADVERTENCIA: La variable de entorno AVANGENIO_API_KEY no está configurada."
        )
        print(
            "   Para usar el chat completo, configura tu clave API en el archivo .env"
        )
        print(
            "   Por ahora, el chat se ejecutará pero puede fallar al procesar mensajes.\n"
        )

    # Create console chat instance
    chat = ConsoleChat(agent_name="Console Agent", model=ModelType.AGENT_MD.value)

    # Run the chat
    chat.run()


if __name__ == "__main__":
    main()
