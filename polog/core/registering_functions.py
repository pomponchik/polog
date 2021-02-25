import weakref


class RegisteringFunctions:
    """
    Класс для регистрации задекорированных функций и хранения их id. Используется, к примеру, для работы декоратора, запрещающего логирование другими декораторами. Для своей работы он должен сначала убедиться, что функция, логирование которой он запрещает, не была задекорирована логгером ранее.
    Проверка задекорированности функции производится по ее id.
    """
    # Соответствия между id декораторов и слабыми ссылками на оригиналы.
    all_decorated_functions = {}
    # Множество id's функций, которые запрещено декорировать.
    forbidden_to_decorate = set()
    # id's функций, задекорированных через декоратор класса. Имеются ввиду id's именно оригиналов.
    decorated_methods = set()

    def add(self, decorated_function, original_function, is_method=False):
        """
        Добавляем функцию в реестр задекорированных.
        """
        decorated_id = id(decorated_function)
        original_id = id(original_function)
        self.all_decorated_functions[decorated_id] = weakref.ref(original_function)
        if is_method:
            self.decorated_methods.add(original_id)
        self.create_finalizer(decorated_id, original_id, original_function)

    def create_finalizer(self, decorated_id, original_id, function):
        """
        Регистрация финализатора для функции.

        Финализатор нужен, чтобы стереть из Polog упоминания функции, когда заканчивается ее жизненный цикл. Актуально для функций с ограниченным жизненным циклом, например для тех, которые порождаются в других функциях.
        Если этого не сделать, память из-под функции будет освобождена и ее может занять другой объект, например другая функция. При этом с точки зрения Polog это все еще прежняя функция, со всеми указанными для нее настройками (например, с запретом на логирование, если таковой был).
        """
        def finalize():
            self.all_decorated_functions.pop(decorated_id, None)
            self.forbidden_to_decorate.discard(original_id)
            self.decorated_methods.discard(original_id)
        weakref.finalize(function, finalize)

    def remove(self, func):
        """
        Удаляем функцию из реестра задекорированных.
        """
        if self.is_decorator(func):
            original_function = self.get_original(func)
            func_id = id(func)
            self.all_decorated_functions.pop(func_id, None)
            original_id = id(original_function)
            if original_id in self.decorated_methods:
                self.decorated_methods.discard(original_id)

    def forbid(self, func):
        """
        Внести функцию в множество тех, что запрещено логировать.
        """
        original_function = self.get_original(func)
        if self.is_forbidden(original_function):
            return
        func_id = id(original_function)
        self.forbidden_to_decorate.add(func_id)

    def get_function_or_wrapper(self, func, before_change_func, wrapper, is_method):
        """
        Здесь принимается решение, декорировать функцию или оставить оригинал.
        Если декорирование функции ранее было запрещено, вернется оригинал.
        Если функция ранее уже была задекорирована, тут надо смотреть на приоритеты. У декоратора класса приоритет ниже, чем у декоратора функций. Если функция ранее была задекорирована через декоратор класса, она передекорируется в любом случае. Если через декоратор функций - то только в том случае, если сейчас ее декорируют не через декоратор класса.
        """
        if self.is_forbidden(func):
            return func
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
        func_id = id(func)
        result = func_id in self.forbidden_to_decorate
        return result

    def is_decorator(self, func):
        """
        Проверка, является ли функция задекорированной ранее.

        Важно: если функция была задекорирована, данный метод вернет True, только если ему скормить задекорированную версию. На оригинал он вернет False.
        """
        func_id = id(func)
        original_func = self.get_original(func)
        original_id = id(original_func)
        result = func_id != original_id
        return result

    def is_method(self, func):
        """
        Проверка, что функция была задекорирована через декоратор класса.
        """
        func = self.get_original(func)
        func_id = id(func)
        result = func_id in self.decorated_methods
        return result

    def get_original(self, func):
        """
        Получить оригинальный объект функции, до его подмены через декоратор.
        Если функция ранее не логировалась, возвращается она же.
        """
        func_id = id(func)
        if func_id in self.all_decorated_functions:
            maybe_function = self.all_decorated_functions.get(func_id)
            maybe_function = maybe_function()
            if maybe_function is not None:
                return maybe_function
        return func
