from polog.handlers.file.rotation.rules.rules.abstract_rule import AbstractRule
from polog.handlers.file.rotation.rules.rules.tokenization.tokens.size_token import SizeToken
#from polog.handlers.file.file_dependency_wrapper import


class FileSizeRule(AbstractRule):
    @classmethod
    def prove_source(cls, source):
        keys = SizeToken.get_all_keys()
        for key in keys:
            if key in keys:
                return True
        return False

    def check(self):
        file_wrapper = self.handler.file
        if file_wrapper.get_size >= self.size_limit:
            pass

    def extract_data_from_string(self):
        number = tokens[0].content
        dimension = tokens[1].content
        self.size_limit = number * dimension
