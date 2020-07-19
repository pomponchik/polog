import time
import atexit
from pony.orm import db_session, commit
from polog.connector import Connector
from polog.model import Log


class Worker(object):
    """
    Экземпляр класса соответствует одному потоку. Здесь происходит непосредственно запись в БД.
    """
    def __init__(self, queue, index):
        self.index = index
        self.queue = queue
        # Инициализация соединения.
        self.connector = Connector()
        # Метка full нужна, чтобы не завершить поток раньше времени, когда он уже взял таску из очереди, но еще не успел записать ее в БД.
        # По умолчанию метка в фиктивном положительном положении, чтобы исключить ситуацию с преждевременным прекращением потока при очень быстром завершении программы. Если метка по умолчанию будет отрицательной, функция ожидания завершения не будет дожидаться окончания записи и прервет поток на самом интересном месте.
        self.full = True
        self.await_empty_queue()

    def run(self):
        """
        Принимаем из очереди словари с данными для записи в БД и собственно записываем их.
        """
        while True:
            try:
                item = self.queue.get()
                self.full = True
                self.write_log(**item)
                self.full = False
            except Exception as e:
                # Если не удалось записать лог в бд, запись уничтожается.
                self.full = False

    @db_session
    def write_log(self, **kwargs):
        log = Log(**kwargs)
        commit()

    def await_empty_queue(self):
        """
        Прежде, чем завершить программу, дожидаемся, пока все потоки запишут в базу последние сообщения.
        Лимит на ожидание - 1 секунда. Он необходим для разрешения ситуации, когда поток еще ни разу не писал в лог сообщений, и соответственно статус заполненности у него фиктивный, в результате чего из него невозможно выйти.
        """
        @atexit.register
        def full_checker():
            start_awaiting_time = time.time()
            while True:
                maybe_finish = time.time()
                time_delta = maybe_finish - start_awaiting_time
                if time_delta > 1.0:
                    break
                if (not self.full) and self.queue.empty():
                    break
