from polog.handlers.file.rotation.rules.rules.abstract_rule import AbstractRule
from polog.handlers.file.rotation.rules.rules.tokenization.tokens.size_token import SizeToken
#from polog.handlers.file.file_dependency_wrapper import



class FileSizeRule(AbstractRule):
    def prove_source(self):
        print(self)
        result = self.tokens.check_regexp('sm')
        print('result = ', result)
        return result

    def check(self):
        file_wrapper = self.handler.file
        if file_wrapper.get_size >= self.size_limit:
            pass

    def extract_data_from_string(self):
        number = self.tokens[0].content
        dimension = self.tokens[1].content
        self.size_limit = number * dimension
        print(self.size_limit)
        print(number, dimension)
