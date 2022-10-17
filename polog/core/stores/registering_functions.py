import weakref

from polog.data_structures.wrappers.weak_linked.dictionary import LockedWeakKeyValueDictionary


class RegisteringFunctions:
    """
    Класс для регистрации задекорированных функций. Используется, к примеру, для работы декоратора, запрещающего логирование другими декораторами. Для своей работы он должен сначала убедиться, что функция, логирование которой он запрещает, не была задекорирована логгером ранее.
    """
    # Соответствия между декораторами и оригиналами.
    all_decorated_functions = LockedWeakKeyValueDictionary()
    # Соответствия между задекорированными @unlog'ом функциями и оригиналами.
    unlogged_functions = LockedWeakKeyValueDictionary()
    # Оригиналы функций, которые запрещено декорировать.
    forbidden_to_decorate = weakref.WeakSet()
    # Оригиналы функций, задекорированных через декоратор класса.
    decorated_methods = weakref.WeakSet()

    def add(self, decorated_function, original_function, is_method=False):
        """
        Добавляем функцию в реестр задекорированных.
        """
        self.all_decorated_functions[decorated_function] = original_function
        if is_method:
            self.decorated_methods.add(original_function)

    def add_unlogged(self, unlogged_function, original_function):
        """
        Любую функцию можно обернуть декоратором @unlog.
        Если это сделать, перед каждым ее вызовом будет проставляться специальная контекстная переменная, а после вызова она будет удаляться.
        Здесь мы добавляем задекорированную unlog'ом функцию в реестр, который позволяет достать оригинал.
        """
        self.unlogged_functions[unlogged_function] = original_function

    def remove(self, func):
        """
        Удаляем функцию из реестра задекорированных.
        """
        if self.is_decorator(func):
            original_function = self.get_original(func)
            self.all_decorated_functions.pop(func, None)
            if original_function in self.decorated_methods:
                self.decorated_methods.discard(original_function)

    def forbid(self, func):
        """
        Внести функцию в множество тех, что запрещено логировать.
        """
        original_function = self.get_original(func)
        if self.is_forbidden(original_function):
            return
        self.forbidden_to_decorate.add(original_function)

    def get_function_or_wrapper(self, func, before_change_func, wrapper, is_method, unlog_decorator=None):
        """
        Здесь принимается решение, декорировать функцию или оставить оригинал.

        Если декорирование функции ранее было запрещено, вернется оригинал.
        Если функция ранее уже была задекорирована, тут надо смотреть на приоритеты. У декоратора класса приоритет ниже, чем у декоратора функций. Если функция ранее была задекорирована через декоратор класса, она передекорируется в любом случае. Если через декоратор функций - то только в том случае, если сейчас ее декорируют не через декоратор класса.
        """
        if self.is_forbidden(func):
            if unlog_decorator is None:
                from polog.unlog import unlog
                unlog_decorator = unlog
            return unlog_decorator(func)
        if self.is_decorator(before_change_func):
            if self.is_method(before_change_func):
                self.remove(before_change_func)
                self.add(wrapper, func, is_method=is_method)
                return wrapper
            else:
                if not is_method:
                    self.remove(before_change_func)
                    self.add(wrapper, func, is_method=is_method)
                    return wrapper
                else:
                    return before_change_func
        self.remove(func)
        self.add(wrapper, func, is_method=is_method)
        return wrapper

    def is_forbidden(self, func):
        """
        Проверка, запрещено ли логировать функцию.
        """
        func = self.get_original(func)
        result = func in self.forbidden_to_decorate
        return result

    def is_decorator(self, func):
        """
        Проверка, является ли функция задекорированной ранее.

        Важно: если функция была задекорирована, данный метод вернет True, только если ему скормить задекорированную версию. На оригинал он вернет False.
        """
        original_func = self.get_original(func)
        result = func is not original_func
        return result

    def is_method(self, func):
        """
        Проверка, что функция была задекорирована через декоратор класса.
        """
        func = self.get_original(func)
        result = func in self.decorated_methods
        return result

    def get_original(self, func):
        """
        Получить оригинальный объект функции, до его подмены через декоратор.
        Если функция ранее не логировалась, возвращается она же.
        """
        if func in self.all_decorated_functions:
            maybe_function = self.all_decorated_functions.get(func)
            if maybe_function is not None:
                return maybe_function
        if func in self.unlogged_functions:
            maybe_function = self.unlogged_functions.get(func)
            if maybe_function is not None:
                return maybe_function
        return func
