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
        self.connector = Connector()
        #метка full нужна, чтобы не завершить поток раньше времени, когда он уже взял таску из очереди, но еще не успел записать ее в БД.
        self.full = False
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
        """
        @atexit.register
        def full_checker():
            while True:
                if (not self.full) and self.queue.empty():
                    break
