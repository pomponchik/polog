from polog.handlers.file.rotation.parser import Parser


class Rotator:
    def __init__(self, rules, handler):
        self.parser = Parser(handler)
        self.rules = self.generate_rules(rules)

    def generate_rules(self, source_rules):
        if source_rules is None:
            return []
        rules = self.parser.extract_rules(source_rules)
        return rules

    def maybe_rotation(self):
        for rule in self.rules:
            if rule.check():
                return True
        return False
