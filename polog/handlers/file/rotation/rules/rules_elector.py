from polog.handlers.file.rotation.rules.rules.file_size_rule import FileSizeRule


class RulesElector:
    """
    Класс для распознавания правил, представленных в виде строк, и преобразования их в функциональные объекты.
    """
    def __init__(self, file, rules=[FileSizeRule]):
        self.file = file
        self.rules = rules

    def choose(self, source):
        """
        Берем строку source и скармливаем ее в конструкторы классов, перечисленных в self.rules.
        Если конкретное правило не узнает себя в переданной строке, метод .prove_source() у него вернет False и мы переходим к следующему правилу.
        Если ни одно из правил себя не узнало, поднимется исключение. Это значит, что форматирование исходной строки некорректно.
        """
        for rule in self.rules:
            try:
                rule = rule(source, self.file)
                if rule.prove_source():
                    return rule
            except Exception as e:
                raise e
        raise ValueError(f'The rule "{source}" is formatted incorrectly. Read the documentstion.')
