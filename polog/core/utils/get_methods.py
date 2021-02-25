import inspect


def get_methods(Class, *methods):
    """
    Фунция, которая берет на вход объект класса и кортеж с названиями методов, и возвращает список с названиями методов.

    Если кортеж на входе пустой - возвращается список с названиями всех методов класса, которые не начинаются и заканчиваются на '__'.
    Иначе - названия из кортежа просто перекладываются в список.

    Семантика тут такая: если пользователь не указал конкретно имена методов, которые нужно логировать - логиируем весь класс. Иначе - только выбранные методы.
    """
    if not len(methods) or (len(methods) == 1 and inspect.isclass(methods[0])):
        methods = [func for func in dir(Class) if callable(getattr(Class, func)) and (not func.startswith('__') and not func.endswith('__'))]
    else:
        methods = [x for x in methods]
    return methods

def make_originals(Class, *methods):
    if methods:
        all = get_methods(Class)
        print(all)
        methods = set(methods)
        print(methods)
        result = tuple([x for x in all if x not in methods])
        print(result)
        return result
    else:
        return ()
