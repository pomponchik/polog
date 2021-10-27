from threading import Lock


class ThreadLock:
    """
    Обертка вокруг обычного тред-лока (см. https://en.wikipedia.org/wiki/Lock_(computer_science)).

    Предназначена, чтобы сделать лок отключаемым.
    """
    def __init__(self, on=True):
        if not on:
            self.acquire = self.empty_acquire
            self.release = self.empty_release
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

    def empty_acquire(self):
        """
        Сделать вид, что взял лок.
        """
        pass

    def empty_release(self):
        """
        Сделать вид, что отпустил лок.
        """
        pass
