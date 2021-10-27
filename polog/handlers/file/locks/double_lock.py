from polog.handlers.file.locks.file_lock import FileLock
from polog.handlers.file.locks.thread_lock import ThreadLock


class DoubleLock:
    """
    Менеджер контекста сразу для двух типов блокировок:
    1. Блокировки потока.
    2. Файловой блокировки.

    Блокировка необходима в момент какой-то чувствительной работы над файлом, когда важно, чтобы в нее не вмешивались другие процессы / потоки.
    """
    def __init__(self, filename, lock_type, lock_file_extension='lock'):
        self.types = self.get_lock_types(lock_type)
        self.thread_lock = self.get_thread_lock()
        self.file_lock = self.get_file_lock(filename, lock_file_extension)

    def __enter__(self):
        """
        Взять оба лока.
        """
        self.thread_lock.acquire()
        self.file_lock.acquire()

    def __exit__(self, exception_type, exception_value, traceback):
        """
        Отпустить оба лока.
        """
        self.thread_lock.release()
        self.file_lock.release()

    def get_lock_types(self, lock_type):
        """
        Получить коллекцию строк - видов локов, которые нужно включить.
        """
        if not lock_type:
            return ()
        if not isinstance(lock_type, str):
            raise ValueError('A set of lock types can only be specified as a string, using the "+" sign as a connector. Example: "thread+file".')

        allowed_types = set(('file', 'thread'))
        maybe_types = {x for x in lock_type.split('+') if x}
        for maybe_type in maybe_types:
            if maybe_type not in allowed_types:
                raise ValueError(f'{len(allowed_types)} types of blocking are allowed: {", ".join([x for x in allowed_types])}. You passed "{maybe_type}".')
        return allowed_types

    def get_thread_lock(self):
        """
        Получить объект обертки над тред-локом.
        """
        on = 'thread' in self.types
        return ThreadLock(on=on)

    def get_file_lock(self, filename, lock_file_extension):
        """
        Получить объект обертки над файл-локом.
        """
        if 'file' not in self.types:
            filename = None
        return FileLock(filename, lock_file_extension)
