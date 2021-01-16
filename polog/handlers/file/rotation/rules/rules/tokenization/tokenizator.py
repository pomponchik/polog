from polog.handlers.file.rotation.rules.rules.tokenization.tokens import SizeToken, NumberToken, DotToken
from polog.handlers.file.rotation.rules.rules.tokenization.tokens.tokens_group import TokensGroup


class Tokenizator:
    def __init__(self, source, tokens_classes=[SizeToken, NumberToken, DotToken]):
        self.source = source
        self.tokens_classes = tokens_classes
        self.tokens = self.generate_tokens()

    def generate_tokens(self):
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
        return source.split()
