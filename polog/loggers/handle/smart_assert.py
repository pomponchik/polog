from polog.loggers.handle.abstract import AbstractHandleLogger
from polog.core.stores.settings.settings_store import SettingsStore
from polog import log


class SmartAssert(AbstractHandleLogger):
    """
    Класс обертки вокруг инструкции assert.

    Если переменная __debug__ равна True, все работает в точности как assert.
    Если __debug__ == False и переданное выражение эквивалентно False, записывается лог.

    О переменной __debug__ см. https://docs.python.org/3/using/cmdline.html#cmdoption-O и https://docs.python.org/3/reference/simple_stmts.html#assert.
    """
    def __init__(self):
        self.settings = SettingsStore()

    def __call__(self, expression_result, *maybe_message):
        """
        Если первый аргумент эквивалентен False - мы либо поднимаем исключение, либо пишем лог.
        Выбранный вариант зависит от текущей настройки debug_mode. Если debug_mode == False - поднимется исключение, иначе - пишется лог.
        """
        message = self.get_message(expression_result, *maybe_message)
        try:
            if self.settings['smart_assert_politic'](self.settings['debug_mode'], expression_result):
                log(message, exception=AssertionError(message))
            if self.settings['debug_mode'] and not expression_result:
                raise AssertionError(message)
        except Exception:
            if self.settings['debug_mode']:
                log(message, exception=AssertionError(message))
                raise AssertionError(message)

    def get_message(self, expression_result, *maybe_message):
        """
        Извлекаем сообщение из того, что было передано.

        Если передано сообщение как строка - используем его. Если нет - сериализуем результат выражения.
        Если при сериализации возникает проблема, возвращаем сообщение об ошибке.
        """
        if len(maybe_message) > 1:
            self._maybe_raise(TypeError, 'The assert wrapper function accepts no more than 2 arguments: an expression and a message.')

        message = None
        default_message = 'It is impossible to extract data for the log.'

        try:
            if len(maybe_message) >= 1:
                message = maybe_message[0]
                if not isinstance(message, str):
                    try:
                        message = str(message)
                    except Exception:
                        message = expression_result
                        if not isinstance(message, str):
                            message = str(message)
            else:
                message = expression_result
            if not isinstance(message, str):
                message = str(message)
        except Exception:
            if not isinstance(message, str):
                message = default_message
            pass
        return message


smart_assert = SmartAssert()
