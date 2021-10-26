import fcntl
from threading import Lock
from functools import partial


class FileLock:
    """
    Менеджер контекста сразу для двух типов блокировок:
    1. Блокировки потока (см. https://en.wikipedia.org/wiki/Lock_(computer_science)).
    2. Файловой блокировки (см. https://en.wikipedia.org/wiki/File_locking).

    Блокировка необходима в момент какой-то чувствительной работы над файлом, когда важно, чтобы в нее не вмешивались другие процессы / потоки.
    Опирается на соответствующий API операционной системы, поэтому может работать не везде.
    """
    def __init__(self, filename, lock_type, lock_file_extension='lock'):
        if not lock_type:
            self.set_empty_actions()
        else:
            self.set_actions(filename, lock_file_extension, lock_type)

    def set_empty_actions(self):
        self.enter_actions = []
        self.exit_actions = []

    def set_actions(self, filename, lock_file_extension, lock_type):
        if not isinstance(lock_type, str):
            raise ValueError()

        action_getters = {
            'thread': self.get_thread_lock,
            'file': partial(self.get_file_lock, filename, lock_file_extension),
        }

        self.enter_actions = []
        self.exit_actions = []

        lock_types = set(lock_type.split('+'))

        for lock_type in lock_types:
            if lock_type not in action_getters:
                raise ValueError()
            getter = action_getters[lock_type]
            enter_action, exit_action = getter()
            if enter_action is not None:
                self.enter_actions.append(enter_action)
            if exit_action is not None:
                self.exit_actions.append(exit_action)

    def get_thread_lock(self):
        lock = Lock()
        def enter():
            lock.acquire()
        def exit():
            lock.release()
        return enter, exit

    def get_file_lock(self, filename, lock_file_extension):
        if not filename:
            return None, None
        self.filename = f'{filename}.{lock_file_extension}'
        self.file = open(self.filename, 'w')

        def enter():
            fcntl.flock(self.file.fileno(), fcntl.LOCK_EX)
        def exit():
            fcntl.flock(self.file.fileno(), fcntl.LOCK_UN)

        return enter, exit

    def __enter__(self):
        for action in self.enter_actions:
            action()

    def __exit__(self, exception_type, exception_value, traceback):
        for action in self.exit_actions:
            action()
