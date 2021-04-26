from polog.handlers.file.rotation.rules.rules.tokenization.tokens import SizeToken, NumberToken, DotToken
from polog.handlers.file.rotation.rules.rules.tokenization.tokens.tokens_group import TokensGroup


class Tokenizator:
    """
    Разбиваем исходную строку с правилом на токены.
    """
    def __init__(self, source, tokens_classes=[SizeToken, NumberToken, DotToken]):
        """
        source - исходная строка с правилом.
        tokens_classes - все доступные классы токенов.

        Особое внимание на класс DotToken. Любой нераспознанный токен будет отнесен к данному классу.
        Именно поэтому он ОБЯЗАТЕЛЬНО должен быть последним в списке.
        """
        self.source = source
        self.tokens_classes = tokens_classes
        self.tokens = self.generate_tokens()

    def generate_tokens(self):
        """
        Делим исходную строку на подстроки (скажем, на слова). Эти подстроки скармливаем в конструкторы всех классов токенов.
        Если токен не узнает себя в подстроке, он поднимает исключение. То есть, если исключения нет - значит подстрока представляет именно данный токен.
        """
        pre_tokens = self.split_text(self.source)
        tokens = []
        for source_token in pre_tokens:
            full = False
            for cls in self.tokens_classes:
                try:
                    token = cls(source_token)
                    tokens.append(token)
                    full = True
                except Exception as e:
                    pass
                if full:
                    break
        return TokensGroup(tokens)

    def split_text(self, source):
        """
        Берем исходную строку с правилом и делим на подстроки.
        Каждая подстрока представляет отдельный токен.
        """
        return source.split()
