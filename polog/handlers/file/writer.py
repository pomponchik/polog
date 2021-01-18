from polog.handlers.abstract.base import BaseHandler
from polog.handlers.file.file_dependency_wrapper import FileDependencyWrapper
from polog.handlers.file.base_formatter import BaseFormatter
from polog.handlers.file.rotation.rotator import Rotator


class file_writer(BaseHandler):
    """
    Класс-обработчик для логов.
    Объект класса является вызываемым благодаря наличию метода .__call__().
    При вызове экземпляра класса, происходит запись лога в файл.
    Поддерживаются ротация логов, фильтрация и форматирование.
    """
    def __init__(self, file, formatter=None, rotation=None, forced_flush=True, separator='\n', only_errors=False, filter=None, alt=None, file_wrapper=FileDependencyWrapper, base_formatter=BaseFormatter, rotator=Rotator):
        self.file = file_wrapper(file)
        self.forced_flush = forced_flush
        self.filter = filter
        self.only_errors = only_errors
        self.alt = alt
        self.base_formatter = base_formatter(separator)
        self.formatter = self.get_formatter(formatter)
        self.rotator = self.get_rotator(rotator, rotation)

    def do(self, content):
        """
        Данная функция вызывается непосредственно для записи лога.
        Помимо записи, опционально тут вызывается ротация (в зависимости от установленных настроек ротации) и сброс буфера.
        """
        # Проверка, нужна ли сейчас ротация логов. Если нужна - ротируем, после чего уже переходим к записи нового лога.
        self.maybe_rotation()
        # Запись лога в файл.
        self.file.write(content)
        # Сброс буфера вывода. Осуществляется по умолчанию, это можно настроить при инициализации обработчика.
        self.maybe_flush()

    def get_content(self, args, **kwargs):
        """
        Стандартный метод для создания строки лога из исходных данных. Использует стандартный форматтер.
        """
        return self.formatter(args, **kwargs)

    def maybe_flush(self):
        """
        Проверяем, нужен ли в данном случае сброс буфера файлового вывода.
        Если да - сбрасываем, то есть записываем в файл весь буфер.
        """
        if self.forced_flush:
            self.file.flush()

    def maybe_rotation(self):
        """
        Проверяем, нужна ли ротация логов при данном вызове.
        Если да - ротируем.
        """
        if self.rotator.maybe_rotation():
            self.rotate()

    def rotate(self):
        self.file.move_file('logs/lolg.pi')
        self.file.reopen()

    def get_formatter(self, maybe_formatter):
        if callable(maybe_formatter):
            return maybe_formatter
        return self.base_formatter_wrapper

    def get_rotator(self, rotator, rotation):
        if isinstance(rotation, Rotator):
            return rotation
        return rotator(rotation, self)

    def base_formatter_wrapper(self, args, **kwargs):
        result = self.base_formatter(args, **kwargs)
        return result
