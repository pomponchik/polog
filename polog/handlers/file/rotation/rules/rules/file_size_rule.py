from polog.handlers.file.rotation.rules.rules.abstract_rule import AbstractRule
from polog.handlers.file.rotation.rules.rules.tokenization.tokens.size_token import SizeToken


class FileSizeRule(AbstractRule):
    def prove_source(self):
        result = self.tokens.check_regexp('ns')
        return result

    def check(self):
        file_wrapper = self.handler.file
        return file_wrapper.get_size() >= self.size_limit

    def extract_data_from_string(self):
        number = self.tokens['n'][0].content
        dimension = self.tokens['s'][0].content
        self.size_limit = number * dimension
