class Levels:
    """
    Класс для хранения соответствий между именами уровней логирования и их числовыми значениями.
    Изначально имена уровням логирования не заданы. Чтобы задать их в соответствии со схемой из стандартной библиотеки (см. https://docs.python.org/3.8/library/logging.html#logging-levels), используйте Config.standart_levels().
    """
    # Названия уровней - ключи, числа - значения.
    levels = {}
    # Наоборот, числа - ключи, названия уровней - значения.
    # Размер словаря не обязан совпадать с размером levels, т. к. пользователь может дать одному уровню 2 разных имени, и здесь из них будет фигурировать только последнее.
    levels_reverse = {}

    @classmethod
    def set(cls, name, value):
        assert isinstance(value, int) and isinstance(name, str)
        cls.levels[name] = value
        cls.levels_reverse[value] = name

    @classmethod
    def get(cls, key):
        """
        Получаем номер уровня по названию.
        """
        if isinstance(key, str):
            result = cls.levels.get(key)
            if result is None:
                raise KeyError(f'Logging level "{key}" is not exist.')
        else:
            if not (type(key) is int) or key < 0:
                raise ValueError('Expected types for level: int or str.')
            result = key
        return result

    @classmethod
    def get_level_name(cls, level_number):
        """
        Получаем название уровня по числовому значению.
        В случае, если один уровень фигурировал под двумя разными названиями, вернется последнее название.
        Если название уровня не зарегистрировано, вернется преобразованное в строку числовое значение уровня.
        """
        result = cls.levels_reverse.get(level_number, None)
        if result is None:
            result = str(level_number)
        return result

    @classmethod
    def get_all_names(cls):
        result = list(cls.levels.keys())
        return result
