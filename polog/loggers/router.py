import inspect
import functools
from polog.core.levels import Levels
from polog.loggers.handle.handle_log import handle_log
from polog.loggers.handle.message import message
from polog.loggers.auto.class_logger import clog
from polog.loggers.auto.function_logger import flog
from polog.errors import IncorrectUseOfTheDecoratorError


class Router:
    """
    Данный класс перенаправляет запросы к различным функциям / декораторам Polog.
    Он представляет единый интерфейс для всех логгеров.
    """
    def __call__(self, *args, **kwargs):
        """
        При вызове объекта класса, мы смотрим на аргументы и перенаправляем вызов к соответствующему объекту.

        Существует 8 способов вызвать объект роутера:

        1. Как обычный ручной логгер. При этом строка с сообщением должна идти первым неименованным аргументом.
        2. Как обычный ручной логгер, но не напрямую, а через имя уровня логирования. Скажем, если мы хотим вручную создать запись уровня "kek" (при условии, что данный уровень логирования ранее был зарегистрирован), мы вызовем объект вот так: log.kek('hello').
        3. В качестве декоратора для функции без скобок.
        4. В качестве декоратора для функции с передачей произвольных аргументов через скобки.
        5. В качестве декоратора для функций любым из двух перечисленных выше способов, но с указанием имени уровня логирования через точку. Например: @log.kek(message='hello').
        6. В качестве декоратора классов без скобок.
        7. В качестве декоратора классов с аргументами в скобках.
        8. В качестве декоратора классов с указанием уровня логирования через точку, по аналогии с декорированием функций.

        Неправильный вызов объекта может привести к поднятию исключения, которое нельзя отключить, управляя настройкой "silent_internal_exceptions".
        Это связано с тем, что иногда невозможно определить, был вызов осуществлен как функции или как декоратора, в то время как настройка "silent_internal_exceptions" не должна гасить исключения, возникающие при инициализации декораторов.
        """
        if len(args) == 1:
            item = args[0]
            if isinstance(item, str):
                return handle_log(*args, **kwargs)
            elif callable(item):
                return self._wrap(flog, item, *([*args][1:]), **kwargs)
            elif inspect.isclass(item):
                return self._wrap(clog, item, *([*args][1:]), **kwargs)
            else:
                raise IncorrectUseOfTheDecoratorError(f'The first argument of class {str(type(item))} is not recognized.')
        elif len(args) == 0:
            return self._route_wrapper(*args, **kwargs)
        else:
            raise IncorrectUseOfTheDecoratorError('Passing more than one positional argument to the logger.')

    def _route_wrapper(self, *args, **kwargs):
        """
        Декорируем декоратор.
        Когда пользователь использует синтаксис декоратора (@) со скобками, возвращается функция, которая в свою очередь вернет уже обернутую оригинальную функцию или класс.
        Так вот, в данном случае мы не просто возвращаем ее, мы возвращаем обертку, которая смотрит на то, передан в нее класс или функция, и в зависимости от этого возвращает разную обертку.
        Если вы это прочитали, соболезную.
        """
        def wrapper(item):
            if inspect.isclass(item):
                wrapped_wrapper = clog(*args, **kwargs)
            elif callable(item):
                wrapped_wrapper = flog(*args, **kwargs)
            return wrapped_wrapper(item)
        return wrapper

    def _wrap(self, wrapper, item, *args, **kwargs):
        """
        Обычно данный метод будет срабатывать, когда объект используется в качестве декоратора без скобок.
        В этом случае мы просто передаем в обертку wrapper переданный нам объект item (класс или функция) и возвращаем результат.
        Предварительно проверяем на наличие аргов и кваргов, т. к. возможна переадресация из self.__getattribute__() с обогащением доп. аргументами.
        """
        if args or kwargs:
            wrapper = wrapper(*args, **kwargs)
        return wrapper(item)

    def message(self, *args, **kwargs):
        """
        Чтобы не импортировать каждый раз лишний логгер, пользователь может вызывать объект message непосредственно от объекта класса Router.
        """
        message(*args, **kwargs)

    def __getattribute__(self, name):
        """
        Объект данного класса можно вызывать как непосредственно, так и через "виртуальные" методы, имена которых соответствуют именам зарегистрированных пользователем уровней логирования.
        Во втором случае вызов будет автоматически преобразован в обычный, но с добавлением аргумента "level", соответствующего имени уровня логирования, которое было использовано при вызове.
        Если пользователь при вызове с именем уровня логирования через точку еще отдельно передаст именованный аргумент level, приоритет будет у переданного аргумента.
        """
        if name in Levels.levels:
            return functools.partial(self, level=name)
        return object.__getattribute__(self, name)


log = Router()
