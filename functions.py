from datetime import datetime


def get_current_datetime():
    return str(datetime.now())


def get_current_weather(city: str):
    return "24 grados celcius"


def query_exec(model_input):
    print(model_input)
    return "15"


async def async_query_exec(model_input):
    print(model_input)
    return "15"


async def async_get_current_datetime():
    return str(datetime.now())


async def async_get_current_weather(city: str):
    return "24 grados celcius"


if __name__ == "__main__":
    print(get_current_datetime())