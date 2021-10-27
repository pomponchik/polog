import fcntl


class FileLock:
    """
    Реализация файловой блокировки (см. https://en.wikipedia.org/wiki/File_locking).

    Опирается на соответствующий API операционной системы, который присутствует только в *NIX'ах. Соответственно, в других ОС использовать нельзя.

    Файловая блокировка защищает прежде всего от аффектов перекрестных действий со стороны разных процессов над одним файлом.
    То есть у нас один процесс может, к примеру, решить, что файл с логами нужно ротировать, в то время как второй продолжает в него писать.
    Для файловой блокировки создается отдельный специальный файл с расширением .lock. Это необходимо, поскольку сам файл с логами ненадежен - его отдельные процессы могут перемещать или удалять.
    """
    def __init__(self, original_file_name, lock_file_extension='lock'):
        if not original_file_name:
            self.acquire = self.empty_acquire
            self.release = self.empty_release
        else:
            self.filename = f'{original_file_name}.{lock_file_extension}'
            self.file = open(self.filename, 'w')

    def acquire(self):
        """
        Взять лок.
        """
        fcntl.flock(self.file.fileno(), fcntl.LOCK_EX)

    def release(self):
        """
        Отпустить лок.
        """
        fcntl.flock(self.file.fileno(), fcntl.LOCK_UN)

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
