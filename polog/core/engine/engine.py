from threading import Lock
from polog.core.stores.settings.settings_store import SettingsStore
from polog.core.utils.read_only_singleton import ReadOnlySingleton


class Engine(ReadOnlySingleton):
    """
    Обертка для "движка" Polog.

    Снаружи по отношению к ней доступны только 2 действия:
    1. Запись лога (write).
    2. Перезагрузка движка (reload). Перезагрузка включает в себя ожидание, пока ранее переданные на запись логи не запишутся, деактивация текущего движка и загрузка нового.

    При загрузке нового движка учитываются актуальные настройки, например про нужное количество воркеров. Таким образом становится возможным менять количество воркеров непосредственно в процессе работы программы.
    Кроме того, на время перезагрузки движка возможность записи лога временно блокируется, без необходимости как-то этим управлять со стороны вызывающего кода.

    Для взаимодействия с движком снаружи предназначен только этот класс.

    Базовых движков несколько, их выбор осуществляется в зависимости от настроек пользователя на момент подгрузки движка.
    Вне зависимости от того, какой движок сейчас подгружен, общение с ним происходит через объект класса Engine.
    """

    lock = Lock()

    def __init__(self):
        """
        Первая стадия инициализации движка.
        Осуществляется при запуске программы.
        """
        with self.lock:
            if not hasattr(self, 'inited'):
                self.settings = SettingsStore()
                self.blocked = False
                self.inited = True

    def __second_init__(self):
        """
        Вторая стадия инициализации движка.
        Осуществляется при первой записи лога.

        Подгрузка движка является "ленивой" операцией и осуществляется только на этом этапе. Поэтому запись первого лога займет чуть больше времени.
        """
        self.settings['started'] = True
        self.load()

    def write(self, function_input_data, **fields):
        """
        Запись лога.

        При первом вызове данного метода будет выполнена вторичная инициализация, после чего метод будет подменен на тот, что непосредственно записывает лог.
        """
        with self.lock:
            if not self.settings['started']:
                self.__second_init__()
                self.write = self._new_write
        self._new_write(function_input_data, **fields)

    def _new_write(self, function_input_data, **fields):
        """
        Данный метод фактически вызывается каждый раз при вызове метода self.write().
        """
        self.real_engine.write(function_input_data, **fields)

    def _blocked_write(self, function_input_data, **fields):
        with self.lock:
            self._new_write(function_input_data, **fields)

    def reload(self):
        """
        Перезагрузка движка.

        При перезагрузке учитываются все актуальные на момент ее проведения настройки, таким образом их становится возможным менять в процессе работы программы.
        На момент перезагрузки движка, операции записи блокируются для всех потоков.
        """
        if self.settings['started']:
            self.block()
            self.stop()
            self.load()
            self.unlock()

    def load(self):
        """
        Загрузка, то есть создание нового экземпляра, движка.
        """
        try:
            self.real_engine = self.settings['engine'](self.settings)
        except RuntimeError:
            self.real_engine = self.settings['engine'](self.settings)

    def stop(self):
        """
        Остановка движка.
        """
        self.real_engine.stop()

    def block(self):
        """
        Блокировка обертки движка, чтобы, пока происходит перезагрузка, нельзя было записывать логи.
        """
        if self.settings['started']:
            self.lock.acquire()
            self.write = self._blocked_write

    def unlock(self):
        """
        Разблокировка обертки движка.
        """
        self.write = _new_write
        self.lock.release()
