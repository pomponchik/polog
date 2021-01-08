from polog.handlers.file.rotation.rules.rules.tokenization.tokenizator import Tokenizator


class AbstractRule:
    def __init__(self, handler, source):
        self.source = source
        self.tokens = self.get_tokens(source)
        self.extract_data_from_string(source)

    def __repr__(self):
        type_name = type(self).__name__
        source = self.source
        result = f'{type_name}("{source}")'
        return result

    def get_tokens(self, source):
        self.tokens = Tokenizator(source).tokens

    def extract_data_from_string(self, source):
        """
        Эта функция не должна ничего возвращать, она сохраняет извлеченные из исходной строки данные в объект класса сама.
        """
        raise NotImplementedError

    @classmethod
    def prove_source(cls, source):
        """
        Здесь мы проверяем, что исходная строка в нужном нам формате, то есть описывает тот тип правил, который обрабатывается конкретным наследником данного класса.
        """
        raise NotImplementedError

    def check(self):
        """
        Эта функция будет вызываться при каждой записи лога.
        Ее задача - определить, должно ли данное правило сработать сейчас.
        """
        raise NotImplementedError
