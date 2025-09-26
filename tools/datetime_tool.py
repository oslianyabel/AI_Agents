from datetime import datetime


def get_current_datetime():
    """
    Obtiene la fecha y hora actual.
    
    Returns:
        str: Fecha y hora actual en formato string
    """
    return str(datetime.now())


async def async_get_current_datetime():
    """
    Versión asíncrona para obtener la fecha y hora actual.
    
    Returns:
        str: Fecha y hora actual en formato string
    """
    return str(datetime.now())


if __name__ == "__main__":
    # Prueba de la función
    print("Fecha y hora actual:", get_current_datetime())
