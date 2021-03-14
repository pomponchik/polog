import functools
from polog.core.levels import Levels
from polog.core.settings_store import SettingsStore


class AbstractHandleLogger:
    _allowed_types = {
        'function': lambda x: type(x) is str or callable(x), # Функция, событие в которой логируется. Ожидается либо сам объект функции, либо строка с ее названием.
        'module': lambda x: type(x) is str, # Модуль, событие в котором логируется. Ожидается только название.
        'message': lambda x: type(x) is str, # Сообщение лога, любая строка.
        'exception': lambda x: type(x) is str or isinstance(x, Exception), # Экземпляр перехваченного пользователем исключения или его название. Если передается экземпляр, поля с названием исключения и его сообщением будут заполнены автоматически.
        'vars': lambda x: type(x) is str, # Ожидается любая строка, но для совместимости формата с автоматическими логами рекомендуется передавать аргументы в функцию polog.utils.json_vars(), а уже то, что она вернет, передавать сюда в качестве аргумента.
        'success': lambda x: type(x) is bool, # Успех / провал операции, которая логируется.
        'level': lambda x: type(x) is str or type(x) is int, # Уровень важности лога.
        'local_variables': lambda x: type(x) is str, # json с локальными переменными, либо строка от пользователя в свободном формате.
    }
    _convert_values = {
        'function': lambda x: x if isinstance(x, str) else x.__name__,
        'exception': lambda x: x if isinstance(x, str) else type(x).__name__,
        'level': Levels.get,
    }
    _convert_keys = {
        'vars': 'local_variables',
    }

    def __getattribute__(self, name):
        """
        Экземпляр класса-наследника можно вызывать как непосредственно, так и через "методы", названия которых соответствуют зарегистрированным пользователем уровням логирования.
        Если использован второй вариант, уровень логирования подставится автоматически.
        """
        if name in Levels.levels:
            return functools.partial(self, level=name)
        return object.__getattribute__(self, name)

    @staticmethod
    def maybe_raise(exception, message):
        """
        При реальном использовании логгер не должен аффектить работу основной программы.
        Даже в случае, когда он был использован неправильно, он должен подавить возникшее исключение и по возможности залогировать хоть что-то.
        На этапе отладки наоборот, рекомендуется отключить подавление исключений, чтобы ошибки использования логгера были явными.

        Управлять режимом подавления исключений можно через config, манипулируя настройкой silent_internal_exceptions.
        """
        if not SettingsStore().silent_internal_exceptions:
            raise exception(message)
