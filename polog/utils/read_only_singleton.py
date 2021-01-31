from threading import Lock


class ReadOnlySingleton:
    """
    Базовый класс синглтона, в котором лочится только момент первого создания экземпляра, для защиты от состояния гонки.
    Подразумевается, что прочие аспекты существования класса пользователь защищает от состояния гонки самостоятельно.
    """
    def __new__(cls, **kwargs):
        """
        Данный метод отрабатывает только один раз.
        После чего подменяется объявленным внутри него же методом __new_new__(), который всегда возвращает экземпляр без дополнительных проверок.
        """
        with Lock():
            def __new_new__(cls, **kwargs):
                return cls.instance
            if not hasattr(cls, 'instance'):
                cls.instance = super().__new__(cls)
            cls.__new__ = __new_new__
            cls.__new__.__name__ = '__name__'
            return cls.instance
