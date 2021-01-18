from polog.handlers.file.rotation.rules.rules.file_size_rule import FileSizeRule


class RulesElector:
    def __init__(self, handler, rules=[FileSizeRule]):
        self.handler = handler
        self.rules = rules

    def choose(self, source):
        for rule in self.rules:
            try:
                rule = rule(source, self.handler)
                if rule.prove_source():
                    return rule
            except Exception as e:
                raise e
        raise ValueError(f'The rule "{source}" is formatted incorrectly. Read the documentstion.')
