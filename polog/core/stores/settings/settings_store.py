import json
import inspect
from threading import Lock

from polog.core.utils.read_only_singleton import ReadOnlySingleton
from polog.core.utils.reload_engine import reload_engine
from polog.core.stores.settings.setting_point import SettingPoint
from polog.core.stores.levels import Levels
from polog.core.engine.real_engines.fabric import real_engine_fabric


class SettingsStore(ReadOnlySingleton):
    """
    Здесь хранятся все базовые настройки Polog.

    Данный класс не предназначен для доступа "снаружи". Его должны использовать только другие части Polog.
    Потокобезопасный синглтон, с экземпляром можно обращаться как со словарем (только в плане считывания и записи значений по ключам).
    """

    # Перечисление пунктов настроек. Каждый пункт - экземпляр класса SettingPoint, внутри которого проводятся все необходимые проверки и блокировки.
    # По сути весь класс SettingsStore проксирует доступ к этому словарю.
    points = {
        'pool_size': SettingPoint(
            2,
            proves={
                'the value must be an integer': lambda x: isinstance(x, int),
                'the value must be greater than or equal to zero': lambda x: x >= 0,
            },
            conflicts={
                'max_queue_size': lambda new_value, old_value, other_field_value: new_value == 0 and other_field_value != 0,
            },
            action=lambda old_value, new_value, store: reload_engine() if old_value != new_value else None,
            read_lock=True,
            shared_lock_with=(
                'max_queue_size',
                'started',
            ),
        ),
        'max_queue_size': SettingPoint(
            0,
            proves={
                'the value must be an integer': lambda x: isinstance(x, int),
                'the value must be greater than or equal to zero': lambda x: x >= 0,
            },
            conflicts={
                'pool_size': lambda new_value, old_value, other_field_value: new_value != 0 and other_field_value == 0,
            },
            action=lambda old_value, new_value, store: reload_engine() if old_value != new_value else None,
            read_lock=True,
            shared_lock_with=(
                'pool_size',
                'started',
            ),
        ),
        'started': SettingPoint(
            False,
            proves={
                'the value must be boolean': lambda x: isinstance(x, bool),
                'the value can only be positive (True)': lambda x: x == True,
            },
            no_check_first_time=True,
            change_once=True,
            shared_lock_with=(
                'pool_size',
                'max_queue_size',
            ),
        ),
        'original_exceptions': SettingPoint(
            False,
            proves={
                'the value must be boolean': lambda x: isinstance(x, bool),
            },
        ),
        'level': SettingPoint(
            1,
            proves={
                'the value can be a string or an integer greater than or equal to zero': lambda x: (isinstance(x, int) and x >= 0) or isinstance(x, str),
            },
            converter=Levels.get,
        ),
        'errors_level': SettingPoint(
            2,
            proves={
                'the value can be a string or an integer greater than or equal to zero': lambda x: (isinstance(x, int) and x >= 0) or isinstance(x, str),
            },
            converter=Levels.get,
        ),
        'service_name': SettingPoint(
            'base',
            proves={
                'the value can only be a string': lambda x: isinstance(x, str),
                'the value must follow the rules for formatting identifiers in Python': lambda x: x.isidentifier(),
            },
        ),
        'silent_internal_exceptions': SettingPoint(
            False,
            proves={
                'the value must be boolean': lambda x: isinstance(x, bool),
            },
        ),
        'max_delay_before_exit': SettingPoint(
            1.0,
            proves={
                'the value must be a number (int or float)': lambda x: isinstance(x, int) or isinstance(x, float),
                'the value must be greater than zero': lambda x: x > 0,
            },
        ),
        'delay_on_exit_loop_iteration_in_quants': SettingPoint(
            10,
            proves={
                'the value must be an integer': lambda x: isinstance(x, int),
                'the value must be greater than zero': lambda x: x > 0,
            },
        ),
        'time_quant': SettingPoint(
            0.01,
            proves={
                'the value must be a number (int or float)': lambda x: isinstance(x, int) or isinstance(x, float),
                'the value must be greater than zero': lambda x: x > 0,
            },
        ),
        'engine': SettingPoint(
            real_engine_fabric,
            proves={
                'the value can be a class or a callable object': lambda x: inspect.isclass(x) or callable(x),
            },
            no_check_first_time=True,
        ),
        'json_module': SettingPoint(
            json,
            proves={
                'the value must be a module': lambda x: inspect.ismodule(x),
                'the value must have the "loads" attribute': lambda x: hasattr(x, 'loads'),
                'the value must have the "dumps" attribute': lambda x: hasattr(x, 'dumps'),
                'the "loads" attribute of the value must be called': lambda x: callable(getattr(x, 'loads')),
                'the "dumps" attribute of the value must be called': lambda x: callable(getattr(x, 'dumps')),
            },
        ),
    }
    points_are_informed = False
    extra_fields = {}
    lock = Lock()

    def __init__(self, **kwargs):
        """
        Здесь происходит оповещение пунктов настроек об экземпляре класса настроек, а также о прочих важных аспектах, чтобы те могли обращаться друг к другу при необходимости.

        К примеру, некоторые пункты настроек нельзя изменять без проверки на то, был ли уже записан первый лог. В свою очередь, событие записи первого лога изменяет пункт настроек 'started' на значение True. Прочие пункты настроек могут обращаться к данному и поднимать исключение, если их нельзя изменять после записи первого лога.
        Т. к. это синглтон, операция оповещения проделывается ровно один раз - за это отвечает флаг self.points_are_informed.
        """
        with self.lock:
            if not self.points_are_informed:
                for name, point in self.points.items():
                    point.set_store_object(self)
                    point.set_name(name)
                for name, point in self.points.items():
                    point.share_lock_object()
                self.points_are_informed = True

    def __getitem__(self, key):
        """
        Получение текущего значения пункта настроек по его названию.

        Список допустимых названий пунктов настроек см. в SettingsStore.points.
        В случае запроса по любому другому ключу - поднимется KeyError.
        Считывание настроек является неблокирующей операцией (за исключением случаев, когда при инициализации пункта настроек был установлен режим read_lock == True).
        """
        point = self.get_point(key)
        return point.get()

    def __setitem__(self, key, value):
        """
        Устанавливаем новое значение пункта настроек по его названию.

        По умолчанию у каждого пункта настроек есть дефолтное значение.
        Каждое новое значение проверяется на соответствие некоему формату. Скажем, если конкретный пункт предполагает число, а пользователь передает строку - будет поднято исключение с сообщением о неправильном формате. Также производится проверка на конфликты с другими полями настроек.
        Список допустимых названий пунктов настроек см. в SettingsStore.points. В случае использования любого другого ключа - поднимется KeyError.
        При установке нового значения пункта настроек, блокируется только данный пункт. Прочие пункты настроек в этот момент можно изменять из других потоков. Старая настройка доступна для считывания, пока устанавливается новое значение, то есть блокировка распространяется только на операции записи. Однако для отдельных пунктов настроек чтение может быть заблокировано на время, пока другой поток производит запись - см. пункты с аргументом read_lock == True.
        """
        point = self.get_point(key)
        point.set(value)

    def __contains__(self, key):
        """
        Проверка того, что переданное название пункта настроек существует.
        """
        return key in self.points

    def force_get(self, key):
        """
        Получение текущего значения пункта настроек по его названию, с игнорированием возможного режима блокировки на чтение.
        Даже если на чтение стоит блокировка, значение будет считано в обход.

        Использовать данный метод следует с большой осторожностью. Основной ожидаемый кейс использования - когда функции внутри функции, обозначенной для пункта настроек как action, используется считывание значения данного пункта. При обычном способе получения значения, если там установлен режим защищенного чтения, возникнет взаимоблокировка (deadlock), а данный метод позволяет ее избежать.
        """
        point = self.get_point(key)
        return point.unlocked_get()

    def get_point(self, key):
        """
        Получаем объект поля по его названию.

        Важно отличать объекты полей от их содержимого. Объект поля всегда относится к классу SettingPoint, а содержимое поле - те данные, которые помещены в объект и собственно используются в качестве текущего значения настройки.
        """
        if key not in self.points:
            raise KeyError(f'{key} - there is no settings point with this name.')
        return self.points[key]
