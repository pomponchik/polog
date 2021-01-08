from polog.handlers.file.rotation.rules.rules.file_size_rule import FileSizeRule


class RulesElector:
    def __init__(self, rules=[FileSizeRule]):
        self.rules = rules

    def choose(self, source):
        for rule in self.rules:
            if rule.prove_source(source):
                return rule(source)
        raise ValueError(f'The rule "{source}" is formatted incorrectly. Read the documentstion.')
