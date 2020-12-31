from polog.handlers.file.rotation.parser import Parser


class Rotator:
    def __init__(self, rules):
        self.rules = self.generate_rules(rules)
        self.parser = Parser()

    def generate_rules(self, source_rules):
        if source_rules is None:
            return []
        rules = self.parser.extract_rules(source_rules)
        return rules
