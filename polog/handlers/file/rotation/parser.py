from polog.handlers.file.rotation.rules.rules_elector import RulesElector


class Parser:
    def __init__(self, file, elector=RulesElector):
        self.file = file
        self.elector = elector(file)

    def extract_rules(self, rules):
        result = []
        splitted_rules = self.split_source(rules)
        for source in splitted_rules:
            try:
                rule = self.elector.choose(source)
                result.append(rule)
            except Exception as e:
                raise e
        return result

    def split_source(self, source):
        result = [x.strip() for x in source.split(',')]
        return result
