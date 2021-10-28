from polog.handlers.file.rotation.rules.rules.tokenization.tokens.abstractions.abstract_token import AbstractToken


class SizeToken(AbstractToken):
    """
    Токен размера файла. Работает с базовыми обозначениями размеров: байты, мегабайты и т. д.
    """
    regexp_letter = 's'

    # Сокращения названий размерностей файлов.
    short_sizes = {
        'b': 1,
        'kb': 1024,
        'mb': 1024 * 1024,
        'gb': 1024 * 1024 * 1024,
        'tb': 1024 * 1024 * 1024 * 1024,
        'pb': 1024 * 1024 * 1024 * 1024 * 1024,
    }
    # Полные названия размерностей.
    full_sizes = {
        'byte': 1,
        'kilobyte': 1024,
        'megabyte': 1024 * 1024,
        'gigabyte': 1024 * 1024 * 1024,
        'terabyte': 1024 * 1024 * 1024 * 1024,
        'petabyte': 1024 * 1024 * 1024 * 1024 * 1024,
    }

    @classmethod
    def its_me(cls, chunk):
        """
        Если подстрока chunk находится в полном списке возможных названий размерностей - возвращаем True.
        """
        return chunk in cls.get_all_keys()

    def parse(self):
        """
        Берем строку self.source и достаем из словарей self.short_sizes и self.full_sizes соответствующее число байт.
        """
        if self.source in self.short_sizes:
            return self.short_sizes[self.source]
        elif self.source in self.full_sizes:
            return self.full_sizes[self.source]
        if self.source.endswith('s'):
            return self.full_sizes[self.source[:-1]]

    @classmethod
    def get_all_keys(cls):
        """
        Возвращаем список всех ключей из словарей cls.short_sizes и cls.full_sizes, а также ключей из cls.full_sizes с постфиксами 's'.
        """
        result = [x for x in cls.short_sizes.keys()]
        result.extend([x for x in cls.full_sizes.keys()])
        result.extend([f'{x}s' for x in cls.full_sizes.keys()])
        return result
