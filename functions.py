from datetime import datetime


def get_current_datetime():
    return str(datetime.now())


def get_current_weather(city: str):
    return "24 grados celcius"


async def async_get_current_datetime():
    return str(datetime.now())


async def async_get_current_weather(city: str):
    return "24 grados celcius"


if __name__ == "__main__":
    print(get_current_datetime())