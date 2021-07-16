from queue import Queue
from threading import Thread, Lock
from polog.core.engine.real_engines.multithreaded.worker import Worker
from polog.core.engine.real_engines.abstract import AbstractRealEngine


class MultiThreadedRealEngine(AbstractRealEngine):
    """
    Класс, в котором создаются потоки с логгерами и передаются в них задания.
    """
    is_completed = {}

    def __init__(self, settings):
        super().__init__(settings)
        with Lock():
            if not hasattr(self, 'workers'):
                # Очередь общая для всех потоков.
                self.queue = Queue()
                self.workers = [Thread(target=Worker(self.queue, index + 1, settings).run) for index in range(self.settings['pool_size'])]
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
