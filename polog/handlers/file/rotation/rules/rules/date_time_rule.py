from polog.handlers.file.rotation.rules.rules.file_size_rule import AbstractRule


class DateTimeRule(AbstractRule):
    @classmethod
    def prove_source(cls, source):
        raise NotImplementedError

    def check(self):
        raise NotImplementedError
