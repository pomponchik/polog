class Levels(object):
    """
    Класс для хранения соответствий между именами уровней логирования и их числовыми значениями.
    Изначально имена уровням логирования не заданы. Чтобы задать их в соответствии со схемой из стандартной библиотеки (см. https://docs.python.org/3.8/library/logging.html#logging-levels), используйте Config.standart_levels().
    """
    levels = {}

    @classmethod
    def set(cls, name, value):
        assert isinstance(value, int) and isinstance(key, str)
        cls.levels[name] = value

    @classmethod
    def get(cls, key):
        if isinstance(key, str):
            result = cls.levels.get(key)
            if result is None:
                raise KeyError(f'Logging level "{key}" is not exist.')
        else:
            if not (type(key) is int) or key < 0:
                raise ValueError('Expected types for level: int or str.')
            result = key
        return result
