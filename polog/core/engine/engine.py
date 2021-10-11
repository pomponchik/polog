import atexit
from threading import Lock

from polog.core.stores.settings.settings_store import SettingsStore
from polog.core.utils.read_only_singleton import ReadOnlySingleton
from polog.core.utils.exception_escaping import exception_escaping
from polog.core.utils.time_limit import time_limit


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
                self.serial_number = 0
                self.active = False

    def __second_init__(self):
        """
        Вторая стадия инициализации движка.
        Осуществляется при первой записи лога.

        Подгрузка движка является "ленивой" операцией и осуществляется только на этом этапе. Поэтому запись первого лога займет чуть больше времени.
        """
        self.settings['started'] = True
        self.load()
        self.atexit_register()

    def write(self, log):
        """
        Запись лога.

        При первом вызове данного метода будет выполнена вторичная инициализация, после чего метод будет подменен на тот, что непосредственно записывает лог.
        """
        with self.lock:
            if not self.settings['started']:
                self.__second_init__()
                self.write = self._new_write
        self._new_write(log)

    def _new_write(self, log):
        """
        Данный метод фактически вызывается каждый раз при вызове метода self.write().
        """
        self.real_engine.write(log)

    def _blocked_write(self, log):
        with self.lock:
            self._new_write(log)

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

    @exception_escaping
    def load(self):
        """
        Загрузка, то есть создание нового экземпляра, движка.
        """
        self.real_engine = self.settings['engine'](self.settings)
        self.increment_serial_number()
        self.active = True

    @exception_escaping
    def stop(self):
        """
        Остановка движка.
        """
        self.real_engine.stop()
        self.active = False

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
        self.write = self._new_write
        self.lock.release()

    def increment_serial_number(self):
        """
        Увеличение порядкового номера движка. Производится при каждой загрузке.
        """
        self.serial_number += 1

    def atexit_register(self):
        """
        Регистрация обработчика прекращения работы.

        Задача обработчика - добиться, чтобы все логи были записаны. Настройка 'max_delay_before_exit' указывает максимальное число секунд, в течение которых логи будут записываться после поступления сигнала о прекращении работы. То есть в теории потеря логов при прекращении работы возможна, но при достаточно большом (или бесконечно большом) значении 'max_delay_before_exit' этого произойти не должно.
        Следует учитывать, что находящиеся в обработке логи могут быть утеряны в случае физического прекращения работы программы, например при отключении электропитания сервера.
        """
        @atexit.register
        @exception_escaping
        @time_limit(lambda: self.settings['max_delay_before_exit'])
        # Учет данной функции при расчете покрытия тестами отключен, поскольку для его проверки используется отдельный процесс, который, к сожалению, не учитывается сборщиком статистики.
        def checker(): # pragma: no cover
            self.block()
            self.stop()
