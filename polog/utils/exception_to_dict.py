def exception_to_dict(args_dict, exc):
    """
    Заполняем словарь с аргументами информацией об исключении.
    """
    args_dict['exception_message'] = str(exc)
    args_dict['exception_type'] = type(exc).__name__
