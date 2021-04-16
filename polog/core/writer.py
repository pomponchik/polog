from queue import Queue
from threading import Thread, Lock
from polog.core.worker import Worker
from polog.core.settings_store import SettingsStore
from polog.core.utils.read_only_singleton import ReadOnlySingleton


class Writer(ReadOnlySingleton):
    """
    Класс, в котором создаются потоки с логгерами и передаются в них задания.
    """
    is_completed = {}

    def __init__(self):
        settings = SettingsStore()
        self.pool_size = settings.pool_size
        assert self.pool_size > 0
        assert type(self.pool_size) is int

        with Lock():
            if not hasattr(self, 'workers'):
                # Очередь общая для всех потоков.
                self.queue = Queue()
                self.workers = [Thread(target=Worker(self.queue, index + 1).run) for index in range(self.pool_size)]
                for worker in self.workers:
                    worker.daemon = True
                    worker.start()

    def write(self, original_args, **kwargs):
        """
        Кладем аргументы оригинальной функции и извлеченные логгером данные в очередь на запись.
        """
        self.queue.put_nowait((original_args, kwargs))

    def queue_size(self):
        """
        ПРИМЕРНЫЙ размер очереди, см. документацию:
        https://docs.python.org/3/library/queue.html#queue.Queue.qsize
        """
        size = self.queue.qsize()
        return size
