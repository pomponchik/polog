from polog.handlers.file.rotation.rules.rules.file_size_rule import AbstractRule


class PeriodRule(AbstractRule):
    def extract_data_from_string(self, source):
        raise NotImplementedError

    @classmethod
    def prove_source(cls, source):
        raise NotImplementedError

    def check(self):
        raise NotImplementedError
