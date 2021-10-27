import fcntl


class FileLock:
    def __init__(self, original_file_name, lock_file_extension='lock'):
        if not original_file_name:
            self.acquire = self.empty_acquire
            self.release = self.empty_release
        else:
            self.filename = f'{original_file_name}.{lock_file_extension}'
            self.file = open(self.filename, 'w')

    def acquire(self):
        fcntl.flock(self.file.fileno(), fcntl.LOCK_EX)

    def release(self):
        fcntl.flock(self.file.fileno(), fcntl.LOCK_UN)

    def empty_acquire(self):
        pass

    def empty_release(self):
        pass
