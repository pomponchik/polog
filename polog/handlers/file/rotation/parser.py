from polog.handlers.file.rotation.rules.rules_elector import RulesElector


class Parser:
    def extract_rules(self, rules, elector=RulesElector):
        self.elector = elector()
        splitted_rules = self.split_source(rules)


    def split_source(self, source):
        result = [x.strip() for x in source.split(',')]
        return result
