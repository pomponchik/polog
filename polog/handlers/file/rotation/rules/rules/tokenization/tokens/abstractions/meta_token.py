class MetaToken(type):
    """
    Здесь попрождаются классы токенов.
    При создании класса проверяем корректность набора его атрибутов.
    """

    # Данные символы зарезервированы движком регулярных выражений.
    forbidden_regexp_letters = (
        '*', # Пропуск любого количества токенов до тех пор, пока не начнется нужная последовательность.
        '[', # Квадратные скобки используются в движке регулярных выражений для обозначения подстроки, с которой нужно сравнивать токен.
        ']',
    )

    # У каждого порожденного класса должен быть атрибут regexp_letter.
    # regexp_letter не должен быть одинаковым у двух разных классов.
    # Для обеспечения такой проверки в данном словаре хранятся regexp_letter'ы ранее порожденных классов (ключи) и их названия (значения).
    all_regexp_letters = {}

    def __new__(cls, name, bases, dct):
        """
        Перед созданием класса у него проверяется корретность содержимого атрибута regexp_letter.

        Атрибут regexp_letter должен:
        1. Быть.
        2. Быть строкой.
        3. Иметь длину в 1 символ.
        4. Не быть одним из зарезервированных для синтаксиса токенизатора символов.
        5. Не повторяться у двух разных классов.
        6. Не быть определенным у абстрактного класса.

        При несоблюдении любого из этих правил, поднимется исключение.
        """
        x = super().__new__(cls, name, bases, dct)
        if x.__name__ == 'AbstractToken':
            if hasattr(x, 'regexp_letter') and getattr(x, 'regexp_letter') is not None:
                raise AttributeError('The "regexp_letter" attribute should not be defined for the abstract token class.')
            return x
        if not hasattr(x, 'regexp_letter') or type(x.regexp_letter) is not str or len(x.regexp_letter) != 1 or x.regexp_letter in cls.forbidden_regexp_letters:
            raise AttributeError(f'The attribute "regexp_letter" of the class {x.__name__} must be a string of the lenth == 1, not "*" and not ".". When inheriting from an abstract class, you should correctly override this parameter. These conditions are automatically checked in the metaclass.')
        if x.regexp_letter in cls.all_regexp_letters:
            raise AttributeError(f'The {cls.all_regexp_letters[x.regexp_letter]} and {name} classes have the same value "{x.regexp_letter}" for the attribute "regexp_letter".')
        else:
            cls.all_regexp_letters[x.regexp_letter] = name
        return x
