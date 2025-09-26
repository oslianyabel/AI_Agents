import json


def get_current_weather(city: str):
    """
    Obtiene información del clima de una ciudad (datos simulados para pruebas).
    
    Args:
        city (str): Nombre de la ciudad
        
    Returns:
        str: JSON con información del clima
    """
    print(f"get_current_weather: {city}")

    return json.dumps(
        {
            "city": city,
            "temperature": 24,
            "unit": "celsius",
            "description": "Soleado",
            "humidity": 65,
            "wind_speed": 10,
        }
    )


async def async_get_current_weather(city: str):
    """
    Versión asíncrona para obtener información del clima.
    
    Args:
        city (str): Nombre de la ciudad
        
    Returns:
        str: JSON con información del clima
    """
    print(f"async_get_current_weather: {city}")
    
    return json.dumps(
        {
            "city": city,
            "temperature": 24,
            "unit": "celsius",
            "description": "Soleado",
            "humidity": 65,
            "wind_speed": 10,
        }
    )


if __name__ == "__main__":
    # Prueba de la función
    result = get_current_weather("Madrid")
    print("Clima en Madrid:", result)
