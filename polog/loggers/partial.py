from polog.loggers.finalizer import LoggerRouteFinalizer


class RouterPartial:
    """
    Объект, возвращаемый при извлечении у роутера атрибута по неизвестному имени.

    Его можно использовать в качестве контекстного менеджера (проксируемого на сам роутер). То есть за счет него будет срабатывать вот такой трюк:

    >>> from polog import log, config
    >>>
    >>> config.levels(kek=5)
    >>>
    >>> with log.kek:
    >>> ... pass

    Также можно вызывать от объектов данного класса метод .suppress(). Непосредственно от роутера:

    >>> with log.suppress():
    >>> ... raise ValueError # Будет подавлено.

    После указания уровня через точку:

    >>> with log.kek.suppress():
    >>> ... raise ValueError # Будет подавлено.
    """
    def __init__(self, item, **kwargs):
        """
        Сохранение аргументов для последующего отложенного вызова функции.

        item - объект роутера.
        kwargs - именованные аргументы, которые будут переданы в роутер при вызове объекта RouterPartial.
        """
        self.item = item
        self.kwargs = kwargs
        self.to_calling_before_enter = None

    def __call__(self, *args, **kwargs):
        """
        Отложенный вызов функции, аналог functools.partial.
        """
        kwargs.update(self.kwargs)
        return self.item(*args, **kwargs)

    def __enter__(self):
        """
        Вход в контекстный менеджер. По факту проксирует вход в контекстный менеджер от роутера.
        """
        result = self.item.__enter__()
        result(**self.kwargs)
        if self.to_calling_before_enter is not None:
            method_name, args, kwargs = self.to_calling_before_enter
            attribute = getattr(result, method_name)
            attribute(*args, **kwargs)
        return result

    def __exit__(self, exception_type, exception_value, traceback_instance):
        """
        Выход из контекста.
        """
        return self.item.__exit__(exception_type, exception_value, traceback_instance)

    def aware_calling_method(self, method_name, *args, **kwargs):
        """
        Данный метод будет вызван у роутера при входе в контекстный менеджер.

        method_name - имя метода.
        args, kwargs - аргументы, которые будут туда переданы.
        """
        self.to_calling_before_enter = (method_name, args, kwargs)

    def suppress(self, *exceptions):
        """
        Подавление исключений для контекстных менеджеров.
        """
        result = LoggerRouteFinalizer(**self.kwargs)
        result.suppress(*exceptions)
        return result
