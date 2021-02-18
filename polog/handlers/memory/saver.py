from threading import Lock, BoundedSemaphore
from polog.handlers.abstract.base import BaseHandler
from polog.handlers.memory.log_item import LogItem
from polog.core.utils.read_only_singleton import ReadOnlySingleton


class memory_saver(ReadOnlySingleton, BaseHandler):
    """
    Класс-заглушка обработчика для тестов.
    Подключается как обычный обработчик, но никуда не записывает и не отправляет логи, а только сохраняет их в оперативной памяти.
    Сохраненные данным классом логи - экземпляры LogItem.
    Последний лог всегда в атрибуте 'last'. Все логи - в атрибуте 'all'.
    """
    last = None
    all_semaphore = BoundedSemaphore(value=1)

    def __init__(self):
        with Lock():
            if not hasattr(self, 'inited'):
                super().__init__()
                self.all = []
                self.inited = True

    def __call__(self, args, **kwargs):
        """
        При вызове экземпляра класса, обновляем информацию о последнем логе, и добавляем новый лог в список со всеми логами.
        """
        with Lock():
            log = LogItem(args, **kwargs)
            with self.all_semaphore:
                self.all.append(log)
                self.last = log

    def clean(self):
        """
        Очистка старых записей.
        Семафор используется, чтобы случайно не очистить список старых логов в тот момент, когда в него идет запись из другого потока.
        """
        with self.all_semaphore:
            self.all = []
            self.last = None
