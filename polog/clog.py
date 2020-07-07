from polog.flog import flog
from polog.utils.get_methods import get_methods


def clog(*methods, message=None, level=1, errors_level=None):
    def decorator(Class):
        all_methods = get_methods(Class, *methods)
        for method_name in all_methods:
            method = getattr(Class, method_name)
            wrapper = flog(message=message, level=level, errors_level=errors_level)
            new_method = wrapper(method)
            setattr(Class, method_name, new_method)
        return Class
    return decorator
