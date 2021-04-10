from polog.core.registering_functions import RegisteringFunctions


def logging_is_forbidden(func):
    """
    Декоратор, запрещающий логирование функции. Запрет достигается через внесение id функции в реестр функций, который запрещено декорировать, через класс RegisteringFunctions.
    Если функция уже была задекорирована логгером, возвращается ее оригинал, до декорирования. Класс RegisteringFunctions хранит ссылку на оригинальную версию каждой задекорированной функции и возвращает ее по запросу.
    """
    if not RegisteringFunctions().is_decorator(func):
        RegisteringFunctions().forbid(func)
        return func
    original_function = RegisteringFunctions().get_original(func)
    RegisteringFunctions().remove(func)
    RegisteringFunctions().forbid(original_function)
    return original_function
