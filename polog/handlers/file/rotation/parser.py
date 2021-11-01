from polog.handlers.file.rotation.rules.rules_elector import RulesElector


class Parser:
    """
    Здесь исходная строка с правилами ротации превращается в список объектов правил.
    """
    def __init__(self, file, elector=RulesElector):
        self.file = file
        self.elector = elector(file)

    def extract_rules(self, rules):
        """
        Делим строку по разделителю и скармливаем получившиеся подстроки распознавателю правил.
        """
        result = []
        splitted_rules = self.split_source(rules)
        for source in splitted_rules:
            rule = self.elector.choose(source)
            result.append(rule)
        return result

    def split_source(self, source):
        """
        Делим строку по разделителю.
        """
        result = [x.strip() for x in source.replace(';', ',').split(',') if x.strip()]
        return result
