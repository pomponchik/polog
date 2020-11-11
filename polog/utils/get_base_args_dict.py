from polog.utils.get_arg import get_arg


def get_base_args_dict(func, message):
    """
    При каждом вызове функции с логирующим декоратором создается словарь с аргументами, которые будут переданы в очередь для обработчиков.
    В этой функции данный словарь инициализируется и заполняется значениями, которые уже известны еще до запуска задекорированной функции.
    """
    args_dict = {}
    args_dict['auto'] = True
    if message is not None:
        args_dict['message'] = str(message)
    get_arg(func, args_dict, '__module__')
    get_arg(func, args_dict, '__name__', key_name='function')
    return args_dict
