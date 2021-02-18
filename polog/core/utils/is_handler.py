from inspect import Signature


def is_handler(function):
    """
    Проверка сигнатуры функции на предмет того, может она быть обработчиком Polog или нет.

    Обработчик - это вызываемый объект со следующей сигнатурой (названия аргументов не обязаны совпадать):

    handler(function_input, **fields)
    """
    if not callable(function):
        return False
    signature = Signature.from_callable(function)
    parameters = list(signature.parameters.values())
    if len(parameters) != 2:
        return False
    result = True
    result *= (parameters[0].kind == parameters[0].POSITIONAL_ONLY) or (parameters[0].kind == parameters[0].POSITIONAL_OR_KEYWORD)
    result *= (parameters[1].kind == parameters[1].VAR_KEYWORD)
    return result
