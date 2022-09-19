import json


def is_json(value):
    """
    Функция, проверяющая, является ли переданное ей значение валидной строкой формата json.
    """
    try:
        json.loads(value)
    except Exception:
        return False
    return True
