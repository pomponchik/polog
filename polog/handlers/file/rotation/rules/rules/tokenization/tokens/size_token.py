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
        raise NotImplementedError()

    def parse(self):
        raise NotImplementedError()