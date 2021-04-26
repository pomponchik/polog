from polog.handlers.file.rotation.rules.rules.tokenization.tokens.abstractions.abstract_token import AbstractToken


class DotToken(AbstractToken):
    """
    Токен "по умолчанию". Любая строка может представляет токен данного типа, если только она не представляет токен какого-то другого типа.
    """
    regexp_letter = '.'

    @classmethod
    def its_me(cls, chunk):
        """
        Любой строке говорим "да" - она представляет DotToken.
        Поэтому на принадлежность к DotToken'у нужно проверять в последнюю очередь.
        """
        return True

    def parse(self):
        """
        По сути этот метод не имеет никакого смысла. Переопределен просто чтобы было.
        """
        return '.'
