import fcntl

from polog.handlers.file.locks.abstract_single_lock import AbstractSingleLock


class FileLock(AbstractSingleLock):
    """
    Реализация файловой блокировки (см. https://en.wikipedia.org/wiki/File_locking).

    Опирается на соответствующий API операционной системы, который присутствует только в *NIX'ах. Соответственно, в других ОС использовать нельзя.

    Файловая блокировка защищает прежде всего от аффектов перекрестных действий со стороны разных процессов над одним файлом.
    То есть у нас один процесс может, к примеру, решить, что файл с логами нужно ротировать, в то время как второй продолжает в него писать.
    Для файловой блокировки создается отдельный специальный файл с расширением .lock. Это необходимо, поскольку сам файл с логами ненадежен - его отдельные процессы могут перемещать или удалять.
    """
    def __init__(self, original_file_name, lock_file_extension='lock'):
        """
        Инициализация блокировки.
        
        original_file_name - имя файла, куда идет запись логов, и который мы хотим защитить локом. Если передать вместо него None, блокировка включена не будет.
        lock_file_extension - расширение файла блокировки. Для реализации блокировки будет создан еще один файл, имя которого образовано из имени оригинального файла + нового расширения.
        """
        if not original_file_name:
            self.off()
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
