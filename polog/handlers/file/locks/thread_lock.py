from threading import Lock


class ThreadLock:
    def __init__(self, on=True):
        if not on:
            self.acquire = self.empty_acquire
            self.release = self.empty_release
        else:
            self.lock = Lock()

    def acquire(self):
        self.lock.acquire()

    def release(self):
        self.lock.release()

    def empty_acquire(self):
        pass

    def empty_release(self):
        pass
