from polog.handlers.file.rotation.rules.rules.tokenization.tokens import SizeToken, NumberToken, DotToken
class Tokenizator:
    def __init__(self, source, tokens_classes=[SizeToken, NumberToken, DotToken]):
        self.source = source
        self.tokens_classes = tokens_classes
        self.tokens = self.generate_tokens()

    def generate_tokens(self):
        pre_tokens = self.split_text(self.source)
        tokens = []
        for source_token in pre_tokens:
            is_defined = False
            for cls in self.tokens_classes:
                try:
                    token = cls(source_token)
                    is_defined = True
                except:
                    pass
            if not is_defined:
                raise ValueError(f'The "{source_token}" token is not recognized.')
            tokens.append(token)
        return tokens

    def split_text(self, source):
        return source.split()
