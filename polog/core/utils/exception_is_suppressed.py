def exception_is_suppressed(exception, suppressed_exceptions, config):
    """
    Здесь происходит проверка того, является ли переданное первым аргументом исключение одним из списка подавляемых.
    """
    if config['suppress_exception_subclasses']:
        if any(isinstance(exception, suppressed_exception) for suppressed_exception in suppressed_exceptions):
            return True
    else:
        if any(type(exception) is suppressed_exception for suppressed_exception in suppressed_exceptions):
            return True
    return False
