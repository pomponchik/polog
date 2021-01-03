class MetaToken(type):
    def __new__(cls, name, bases, dct):
        x = super().__new__(cls, name, bases, dct)
        # Данные символы зарезервированы движком регулярных выражений.
        forbidden_regexp_letters = (
            # Пропуск любого количества токенов до тех пор, пока не начнется нужная последовательность.
            '*',
            # Пропуск одного любого токена.
            '.',
            # Квадратные скобки используются в движке регулярных выражений для обозначения подстроки, с которой нужно сравнивать токен.
            '[',
            ']',
        )
        if type(x.regexp_letter) is not str or len(x.regexp_letter) != 1 or x.regexp_letter in forbidden_regexp_letters:
            raise AttributeError(f'The attribute "regexp_letter" of the class {x.__name__} must be a string of the lenth == 1, not "*" and not ".". When inheriting from an abstract class, you should correctly override this parameter. These conditions are automatically checked in the metaclass.')
        if 
        return x
