from queue import Queue
from threading import Thread
from polog.worker import Worker
from polog.base_settings import BaseSettings


class Writer(object):
    """
    Класс, в котором создаются потоки с логгерами и передаются в них задания.
    """
    def __init__(self):
        settings = BaseSettings()
        if not hasattr(settings, 'pool_size'):
            raise AttributeError('Atribute "pool_size" is not determinated. Use Config.settings(pool_size=<INTEGER>).')
        pool_size = settings.pool_size
        assert pool_size > 0
        assert type(pool_size) is int

        if not hasattr(self, 'workers'):
            #очередь общая для всех потоков
            self.queue = Queue()
            self.workers = [Thread(target=Worker(self.queue, index + 1).run) for index in range(pool_size)]
            for worker in self.workers:
                worker.daemon = True
                worker.start()

    def __new__(cls, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Writer, cls).__new__(cls)
        return cls.instance

    def write(self, **kwargs):
        """
        Кладем словарь с аргументами в очередь на запись.
        """
        self.queue.put_nowait(kwargs)

    def queue_size(self):
        """
        ПРИМЕРНЫЙ размер очереди, см. документацию:
        https://docs.python.org/3/library/queue.html#queue.Queue.qsize
        """
        size = self.queue.qsize()
        return size
