from queue import Queue
from threading import Thread, Lock
from polog.worker import Worker
from polog.base_settings import BaseSettings


class Writer:
    """
    Класс, в котором создаются потоки с логгерами и передаются в них задания.
    """
    is_completed = {}

    def __init__(self):
        settings = BaseSettings()
        if not hasattr(settings, 'pool_size'):
            raise AttributeError('Atribute "pool_size" is not determinated. Use Config.settings(pool_size=<INTEGER>).')
        self.pool_size = settings.pool_size
        assert self.pool_size > 0
        assert type(self.pool_size) is int

        if not hasattr(self, 'workers'):
            #очередь общая для всех потоков
            self.queue = Queue()
            self.workers = [Thread(target=Worker(self.queue, index + 1).run) for index in range(self.pool_size)]
            for worker in self.workers:
                worker.daemon = True
                worker.start()

    def __new__(cls, **kwargs):
        with Lock():
            if not hasattr(cls, 'instance'):
                cls.instance = super(Writer, cls).__new__(cls)
            return cls.instance

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
