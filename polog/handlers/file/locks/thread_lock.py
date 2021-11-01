from threading import Lock

from polog.handlers.file.locks.abstract_single_lock import AbstractSingleLock


class ThreadLock(AbstractSingleLock):
    """
    Обертка вокруг обычного тред-лока (см. https://en.wikipedia.org/wiki/Lock_(computer_science)).

    Предназначена, чтобы сделать лок отключаемым.
    """
    def __init__(self, on=True):
        if not on:
            self.off()
        else:
            self.lock = Lock()

    def acquire(self):
        """
        Взять лок.
        """
        self.lock.acquire()

    def release(self):
        """
        Отпустить лок.
        """
        self.lock.release()
