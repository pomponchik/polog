from polog.handlers.file.rotation.rules.rules.abstract_rule import AbstractRule
from polog.handlers.file.rotation.rules.rules.tokenization.tokens.size_token import SizeToken


class FileSizeRule(AbstractRule):
    """
    Правило для ротации логов в зависимости от размера файла, куда они пишутся.
    """
    def prove_source(self):
        if not self.tokens.check_regexp('ns'):
            return False
        if self.tokens['n'][0].content <= 0:
            return False
        return True

    def check(self):
        file_wrapper = self.file
        return file_wrapper.get_size() >= self.size_limit

    def extract_data_from_string(self):
        """
        Заполняем self.size_limit.

        self.size_limit - это количество байт размера файла, которое нельзя превышать.
        Образуется путем перемножения 2-х переменных: количества и размерности.
        Скажем, в строке '5 megabytes' количество - это 5, а размерность - количество байт в мегабайте.
        """
        number = self.tokens['n'][0].content
        dimension = self.tokens['s'][0].content
        self.size_limit = number * dimension
