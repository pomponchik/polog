from polog.handlers.file.rotation.rules.rules.tokenization.tokens.abstractions.abstract_token import AbstractToken


class DotToken(AbstractToken):
    regexp_letter = '.'

    @classmethod
    def its_me(cls, chunk):
        return True

    def parse(self):
        return '.'
