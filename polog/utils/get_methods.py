import inspect


def get_methods(Class, *methods):
    if not len(methods) or (len(methods) == 1 and inspect.isclass(methods[0])):
        methods = [func for func in dir(Class) if callable(getattr(Class, func)) and not func.startswith('__')]
    else:
        methods = [x for x in methods]
    return methods
