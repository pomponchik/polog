import inspect
from polog.loggers.auto.function_logger import flog
from polog.core.registering_functions import RegisteringFunctions
from polog.errors import IncorrectUseOfTheDecoratorError


class ClassLogger:
    """
    Экземпляры данного класса - готовые декораторы для других классов.
    """

    def __call__(self, *args, methods=(), message=None, level=1, errors_level=None):
        """
        Фабрика декораторов классов. Можно вызывать как со скобками, так и без.
        В задекорированном классе @flog() применяется ко всем методам, кроме тех, чье название начинается с '__'.
        Приоритет декорирования через класс ниже, чем при прямом декорировании метода с помощью @flog() самим пользователем. Если пользователь навесил на метод задекорированного класса еще @flog(), то применяться будет только декоратор из flog().
        """
        def decorator(Class):
            # Получаем имена методов класса.
            all_methods = self.get_logging_methods(Class, *methods)
            for method_name in all_methods:
                method = getattr(Class, method_name)
                # Конфигурируем декоратор для метода.
                wrapper = flog(message=message, level=level, errors_level=errors_level, is_method=True)
                # Применяем его.
                new_method = wrapper(method)
                setattr(Class, method_name, new_method)
            # Получаем кортеж с именами методов, которые логировать НЕ надо.
            # Если они уже залогированы - нужно вернуть оригиналы.
            originals = self.make_originals(Class, *methods)
            register = RegisteringFunctions()
            for method_name in originals:
                method = getattr(Class, method_name)
                original = register.get_original(method)
                setattr(Class, method_name, original)
            return Class
        if not len(args):
            return decorator
        elif len(args) == 1 and inspect.isclass(args[0]):
            return decorator(args[0])
        raise IncorrectUseOfTheDecoratorError('The @clog decorator could be used only for classes.')

    def make_originals(self, Class, *methods):
        """
        Возвращаем кортеж с названиями всех методов класса, за исключением возвращенных через self.get_logging_methods().
        То есть, фактически, все методы, которые НЕ надо логировать.
        Используется для того, чтобы в дочерних классах подменить данные методы на оригиналы.
        """
        if methods:
            all = self.get_logging_methods(Class)
            methods = set(methods)
            result = tuple([x for x in all if x not in methods])
            return result
        else:
            return ()

    @staticmethod
    def get_logging_methods(Class, *methods):
        """
        Метод, который берет на вход объект класса и кортеж с названиями методов, и возвращает список с названиями методов.

        Если кортеж на входе пустой - возвращается список с названиями всех методов класса, которые не начинаются и заканчиваются на '__'.
        Иначе - названия из кортежа просто перекладываются в список.

        Семантика тут такая: если пользователь не указал конкретно имена методов, которые нужно логировать - логиируем весь класс. Иначе - только выбранные методы.
        """
        if not len(methods) or (len(methods) == 1 and inspect.isclass(methods[0])):
            methods = [func for func in dir(Class) if callable(getattr(Class, func)) and (not func.startswith('__') and not func.endswith('__'))]
        else:
            methods = [x for x in methods]
        return methods


clog = ClassLogger()
