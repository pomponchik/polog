from threading import Lock
from polog.core.utils.read_only_singleton import ReadOnlySingleton
from polog.core.stores.settings.setting_point import SettingPoint
from polog.core.stores.levels import Levels


class SettingsStore(ReadOnlySingleton):
    """
    Здесь хранятся все базовые настройки Polog.
    Данный класс не предназначен для доступа "снаружи". Его должны использовать только другие части Polog.
    Потокобезопасный синглтон, с экземпляром можно обращаться как со словарем (только в плане считывания и записи значений по ключам).
    """

    # Перечисление пунктов настроек. Каждый пункт - экземпляр класса SettingPoint, внутри которого проводятся все необходимые проверки и блокировки.
    # По сути весь класс SettingsStore проксирует доступ к этому словарю.
    points = {
        'pool_size': SettingPoint(2, prove=lambda x: isinstance(x, int) and x > 0),
        'original_exceptions': SettingPoint(False, prove=lambda x: isinstance(x, bool)),
        'level': SettingPoint(1, prove=lambda x: (isinstance(x, int) and x > 0) or isinstance(x, str), converter=Levels.get),
        'errors_level': SettingPoint(2, prove=lambda x: (isinstance(x, int) and x > 0) or isinstance(x, str), converter=Levels.get),
        'service_name': SettingPoint('base', prove=lambda x: isinstance(x, str) and x.isidentifier()),
        'delay_before_exit': SettingPoint(1.0, prove=lambda x: (isinstance(x, int) or isinstance(x, float)) and x >= 0),
        'silent_internal_exceptions': SettingPoint(False, prove=lambda x: isinstance(x, bool)),
        'started': SettingPoint(False, prove=lambda x: isinstance(x, bool) and x == True, no_check_first_time=True),
    }
    points_are_informed = False
    handlers = {}
    extra_fields = {}

    def __init__(self, **kwargs):
        """
        Здесь происходит оповещение пунктов настроек об экземпляре класса настроек, чтобы те могли обращаться друг к другу при необходимости.

        К примеру, некоторые пункты настроек нельзя изменять без проверки на то, был ли уже записан первый лог. В свою очередь, событие записи первого лога изменяет пункт настроек 'started' на значение True. Прочие пункты настроек могут обращаться к данному и поднимать исключение, если их нельзя изменять после записи первого лога.
        Т. к. это синглтон, операция оповещения проделывается ровно один раз - за это отвечает флаг self.points_are_informed.
        """
        with Lock():
            if not self.points_are_informed:
                for name, point in self.points.items():
                    point.set_store_object(self)
                self.points_are_informed = True

    def __getitem__(self, key):
        """
        Получение текущего значения пункта настроек по его названию.

        Список допустимых названий пунктов настроек см. в SettingsStore.points.
        В случае запроса по любому другому ключу - поднимется KeyError.
        Считывание настроек является неблокирующей операцией.
        """
        if key not in self.points:
            raise KeyError()
        point = self.points[key]
        value = point.get()
        return value

    def __setitem__(self, key, value):
        """
        Устанавливаем новое значение пункта настроек по его названию.

        По умолчанию у каждого пункта настроек есть дефолтное значение.
        Каждое новое значение проверяется на соответствие некоему формату. Скажем, если конкретный пункт предполагает число, а пользователь передает строку - будет поднято исключение с сообщением о неправильном формате.
        Список допустимых названий пунктов настроек см. в SettingsStore.points. В случае использования любого другого ключа - поднимется KeyError.
        При установке нового значения пункта настроек, блокируется только данный пункт. Прочие пункты настроек в этот момент можно изменять из других потоков. Старая настройка доступна для считывания, пока устанавливается новое значение, то есть блокировка распространяется только на операции записи.
        """
        if key not in self.points:
            raise KeyError()
        point = self.points[key]
        point.set(value)
