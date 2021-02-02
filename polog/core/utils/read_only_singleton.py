from threading import Lock


class ReadOnlySingleton:
    """
    Базовый класс синглтона, в котором лочится только момент первого создания экземпляра, для защиты от состояния гонки.
    Подразумевается, что прочие аспекты существования класса пользователь защищает от состояния гонки самостоятельно.
    """
    def __new__(cls, **kwargs):
        """
        Данный метод отрабатывает только один раз.
        После чего подменяется объявленной внутри него же функцией __new__(), которая всегда возвращает экземпляр без дополнительных проверок.
        """
        with Lock():
            def __new__(cls, **kwargs):
                return cls.instance
            if not hasattr(cls, 'instance'):
                cls.instance = super().__new__(cls)
            cls.__new__ = __new__
            return cls.instance
