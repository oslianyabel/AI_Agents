from datetime import datetime
import json


def get_current_datetime():
    return str(datetime.now())


def get_current_weather(city: str):
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


async def async_get_current_datetime():
    return str(datetime.now())


async def async_get_current_weather(city: str):
    print(f"async_get_current_weather: {city}")

    return {
        "city": city,
        "temperature": 24,
        "unit": "celsius",
        "description": "Soleado",
        "humidity": 65,
        "wind_speed": 10,
    }


if __name__ == "__main__":
    print(get_current_datetime())
