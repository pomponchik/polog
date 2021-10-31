from polog.handlers.abstract.base import BaseHandler
from polog.core.utils.signature_matcher import SignatureMatcher
from polog.handlers.file.file_dependency_wrapper import FileDependencyWrapper
from polog.handlers.file.base_formatter import BaseFormatter
from polog.handlers.file.rotation.rotator import Rotator
from polog.core.utils.exception_escaping import exception_escaping


class file_writer(BaseHandler):
    """
    Класс-обработчик для логов.
    Объект класса является вызываемым благодаря наличию метода .__call__().
    При вызове экземпляра класса, происходит запись лога в файл.
    Поддерживаются ротация логов, фильтрация и форматирование.
    """

    input_proves = {
        'forced_flush': lambda x: isinstance(x, bool),
        'separator': lambda x: isinstance(x, str),
        'formatter': lambda x: x is None or SignatureMatcher.is_handler(x),
        'rotation': lambda x: x is None or isinstance(x, str),
    }

    def __init__(self, *file, formatter=None, rotation=None, forced_flush=True, separator='\n', only_errors=False, filter=None, alt=None, file_wrapper=FileDependencyWrapper, base_formatter=BaseFormatter, rotator=Rotator, lock_type='thread'):
        super().__init__(only_errors=only_errors, filter=filter, alt=alt)
        self.do_input_proves(forced_flush=forced_flush, separator=separator, formatter=formatter, rotation=rotation)
        self.file = file_wrapper([x for x in file], lock_type)
        self.forced_flush = forced_flush
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

    def get_content(self, log):
        """
        Стандартный метод для создания строки лога из исходных данных. Использует стандартный форматтер.
        """
        return self.formatter(log)

    def maybe_flush(self):
        """
        Проверяем, нужен ли в данном случае сброс буфера файлового вывода.
        Если да - сбрасываем, то есть записываем в файл весь буфер.
        """
        if self.forced_flush:
            self.file.flush()

    @exception_escaping
    def maybe_rotation(self):
        """
        Проверяем, нужна ли ротация логов при данном вызове.
        Если да - ротируем.
        """
        self.rotator.maybe_do()

    def get_formatter(self, maybe_formatter):
        """
        Возвращаем форматтер - некую функцию или класс.
        Его задача - преобразовывать "сырые" данные лога в строку для записи в файл.
        Пользователь может передать сюда свой форматтер. Если он этого не сделал, берем стандартный метод форматирования.
        """
        if callable(maybe_formatter):
            return maybe_formatter
        return self.base_formatter_wrapper

    def get_rotator(self, rotator, rotation_rules):
        """
        Возвращаем ротатор - объект класса, ответственного за ротацию.
        У ротатора обязан присутствовать метод .maybe_do().
        """
        return rotator(rotation_rules, self.file)

    def base_formatter_wrapper(self, log):
        """
        Метод, где вызывается базовый форматтер.
        """
        return self.base_formatter.get_formatted_string(log)
