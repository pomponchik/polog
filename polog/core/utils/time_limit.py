from threading import Timer
from functools import wraps
try:
    import thread
except ImportError:
    import _thread as thread

from polog.core.utils.signature_matcher import SignatureMatcher


class time_limit:
    """
    Класс, предназначенный для использования в качестве декоратора для функций.
    Устанавливает лимит времени для их выполнения.

    По истечении таймаута, поднимается исключение TimeoutError.

    В связи с особенностями реализации, есть несколько ограничений на использование такого рода таймаутов:
    1. Исключение выбрасывается всегда в основном потоке. То есть, при использовании данного декоратора не в основном потоке, там исполнение кода остановлено не будет.
    2. Таймаут может не сработать в случае использования time.sleep() или бинарных расширений для Python (см. https://stackoverflow.com/a/31667005/14522393).
    3. При попытке остановить программу через ctrl+c в момент, пока исполняется функция под данным декоратором, это будет интерпретировано декоратором как окончание таймаута и перехвачено.
    """
    def __init__(self, delay):
        """
        Установка параметра для декоратора.

        delay - это либо число (int или float) больше нуля, либо функция без аргументов, которая возвращает такое число. Если передана функция, она будет вызвана непосредственно перед выполнением задекорированной функции, что позволяет устанавливать таймаут отложенно или даже изменять его в процессе выполнения.
        Если в качестве delay была передана функция, и эта функция возвращает не число больше нуля, таймаут установлен не будет и задекорированная функция будет выполняться столько, сколько захочет.
        """
        self.delay = self.get_delay_function(delay)

    def __call__(self, func):
        """
        Непосредственно функция-декоратор.

        Отсчет времени реализован через threading.Timer, где регистрируется обработчик, вызывающий thread.interrupt_main() (функцию, поднимающую KeyboardInterrupt в основном потоке). KeyboardInterrupt перехватывается и преобразуется в TimeoutError.
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                delay = self.delay()
                if (not isinstance(delay, int) and not isinstance(delay, float)) or (delay <= 0):
                    raise ValueError
            except Exception as e:
                return func(*args, **kwargs)
            def raise_error():
                thread.interrupt_main()
            timer = Timer(delay, raise_error)
            try:
                timer.start()
                return func(*args, **kwargs)
            except KeyboardInterrupt:
                raise TimeoutError(f'The operation time of the function "{func.__name__}" exceeded the timeout of {delay} seconds.')
            finally:
                timer.cancel()
        return wrapper

    def get_delay_function(self, delay):
        """
        Проверка пользовательского ввода и его преобразование к единому формату.

        Если в качестве аргумента delay было передано число, оно запаковывается в функцию, которая вернет это число.
        Если передана функция, возвращается эта же функция.

        В случае, если передно число больше нуля, функция с неправильной сигнатурой (должна быть без аргументов) или что-то еще - будет поднято ValueError.
        """
        base_error_message = f"You can pass as an argument to {type(self).__name__} a function that takes a single positional argument, which will return a number, or directly a number."
        if callable(delay):
            matcher = SignatureMatcher()
            if matcher.match(delay):
                return delay
            raise ValueError(f'{base_error_message}. You passed a function whose signature does not match the expected one.')
        if isinstance(delay, int) or isinstance(delay, float):
            if delay > 0:
                return lambda: delay
            raise ValueError(f'{base_error_message}. You have passed a number that is less than zero. A meaningful designation of the delay is only numbers greater than zero.')
        raise ValueError(base_error_message)
