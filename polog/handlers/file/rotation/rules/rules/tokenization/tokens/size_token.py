from polog.handlers.file.rotation.rules.rules.tokenization.tokens.abstractions.abstract_token import AbstractToken


class SizeToken(AbstractToken):
    regexp_letter = 's'

    short_sizes = {
        'b': 1,
        'kb': 1024,
        'mb': 1024 * 1024,
        'gb': 1024 * 1024 * 1024,
        'tb': 1024 * 1024 * 1024 * 1024,
        'pd': 1024 * 1024 * 1024 * 1024 * 1024,
    }
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
        result = chunk in cls.short_sizes
        result += chunk in cls.full_sizes
        result += chunk + 's' in cls.full_sizes
        return result

    def parse(self):
        if chunk in cls.short_sizes:
            return cls.short_sizes[self.source]
        elif chunk in cls.full_sizes:
            return cls.full_sizes[self.source]
        return cls.full_sizes[f'{self.source}s']
