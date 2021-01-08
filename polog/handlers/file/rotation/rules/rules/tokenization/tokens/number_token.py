from polog.handlers.file.rotation.rules.rules.tokenization.tokens.abstractions.abstract_token import AbstractToken


class NumberToken(AbstractToken):
    regexp_letter = 'n'

    @classmethod
    def its_me(cls, chunk):
        return chunk.isdecimal()

    def parse(self):
        return int(self.source)
