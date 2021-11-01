import collections


class TokensGroup:
    regexp_unit = collections.namedtuple('regexp_unit', 'letter value')

    def __init__(self, tokens_list):
        self.tokens = tokens_list

    def __getitem__(self, key):
        """
        Получение токена или токенов из группы по ключу.

        Ключей может быть 2 вида:
        1. Строки. В качестве такого ключа подается символ, и возвращается всегда объект TokensGroup, содержащий только те токены исходной группы, атрибут .regexp_letter у которых совпадает с переданным ключом.
        2. Целые числа. Число указывает на порядковый номер токена в группе.

        Соответственно, к примеру, если мы хотим получить первый токен типа 'd' из группы, мы обращаемся к группе через 2 индекса: сначала по символу, потом по числу, вот так:
        >>> token = tokens_group['d'][0]
        """
        _class = self.__class__
        if isinstance(key, int):
            return self.tokens[key]
        elif isinstance(key, str):
            if key == '.':
                for token in self.tokens:
                    if token.regexp_letter != '.':
                        return _class([token])
                return _class([])
            elif key == '*':
                return _class([x for x in self.tokens])
            elif len(key) == 1:
                return _class([x for x in self.tokens if x.regexp_letter == key])
        raise KeyError('The key can be a string of lenth equal 1 or a number.')

    def __len__(self):
        return len(self.tokens)

    def check_regexp(self, regexp):
        """
        Проверяем, что исходная строка (токены из которой находятся в self.tokens) соответствует строке паттерна, переданной сюда как regexp.
        """
        if not isinstance(regexp, str):
            raise ValueError('The regexp variable must be str instance.')
        if regexp == '':
            return True
        regexp = self.reduce_regexp(self.parse_regexp(regexp))
        try:
            return self.regexp_loop(regexp, self.tokens, 0, 0)
        except RecursionError:
            return False

    def reduce_regexp(self, regexp):
        """
        Убираем из списка юнитов паттерна дублирующиеся звездочки. Любая пара звездочек, идущих друг за другом, преобразуется в одну звездочку.
        """
        result = []
        for index, unit in enumerate(regexp):
            if unit.letter == '*':
                if index == len(regexp) - 1:
                    result.append(unit)
                else:
                    next_unit = regexp[index + 1]
                    if next_unit.letter == '*':
                        continue
                    else:
                        result.append(unit)
            else:
                result.append(unit)
        return result

    def regexp_loop(self, regexp, tokens, tokens_index, regexp_index):
        """
        Рекурсивная функция сверки списка токенов из строки и паттерна, выраженного в виде списка юнитов.

        Возвращает bool, означающий, что паттерн совпал с токенами (True) или нет (False).
        """
        if (tokens_index == len(tokens) - 1) and (regexp_index == len(regexp) - 1):
            return self.compare_token_and_unit(regexp, tokens, tokens_index, regexp_index)
        elif regexp_index == len(regexp) - 1:
            if regexp[regexp_index].letter == '*':
                return True
            return False
        elif tokens_index == len(tokens) - 1:
            if regexp[regexp_index].letter == '*':
                return self.regexp_loop(regexp, tokens, tokens_index, regexp_index + 1)
            elif self.compare_token_and_unit(regexp, tokens, tokens_index, regexp_index):
                if len(regexp) - 1 == regexp_index + 1:
                    if regexp[regexp_index + 1].letter == '*':
                        return True
            return False
        else:
            if regexp[regexp_index].letter == '*':
                new_tokens_index = tokens_index
                while new_tokens_index < len(tokens):
                    if self.regexp_loop(regexp, tokens, new_tokens_index, regexp_index + 1):
                        return True
                    new_tokens_index += 1
                return False
            else:
                if not self.compare_token_and_unit(regexp, tokens, tokens_index, regexp_index):
                    return False
                else:
                    return self.regexp_loop(regexp, tokens, tokens_index + 1, regexp_index + 1)

    @staticmethod
    def compare_token_and_unit(regexp, tokens, tokens_index, regexp_index):
        """
        Здесь происходит сравнение одного элемента паттерна с одним токеном.
        """
        unit = regexp[regexp_index]
        token = tokens[tokens_index]

        if unit.letter == '*':
            return True
        elif unit.letter == '.':
            if unit.value is not None:
                try:
                    if unit.value == token.source:
                        return True
                    return False
                except:
                    return False
            return True
        elif unit.letter != token.regexp_letter:
            return False

        if unit.value is not None:
            try:
                if unit.value == token.source:
                    return True
                return False
            except:
                return False
        return True

    def parse_regexp(self, regexp):
        """
        Парсинг строки с паттерном.
        Здесь исходная строка-паттерн преобразуется в список юнитов.

        Юнит - это объект, обозначающий какой-то элемент паттерна.
        """
        result = []
        bracket_flag = False
        base_letter = None
        next_letter = None
        into_brackets = None
        for index, letter in enumerate(regexp):
            next_letter = regexp[index + 1] if index != len(regexp) - 1 else ''
            regexp_unit, bracket_flag, into_brackets, base_letter = self.get_regexp_unit(letter, base_letter, next_letter, bracket_flag, into_brackets)
            if regexp_unit is not None:
                result.append(regexp_unit)
        return result

    def get_regexp_unit(self, letter, base_letter, next_letter, bracket_flag, into_brackets):
        """
        В процессе парсинга строки с паттерном здесь порождается объект элемента паттерна (см. атрибут regexp_unit у класса).
        """
        if letter == '[':
            if bracket_flag:
                raise ValueError('Extra token "[" in the regexp.')
            else:
                if base_letter is None:
                    raise ValueError("The value of the regular expression token must be specified in square brackets. You didn't specify a token for this.")
                if base_letter == '*':
                    raise ValueError("""Values can only be specified for "specific" regular expression elements. You cannot specify values in square brackets for element '*'.""")
                bracket_flag = True
                into_brackets = []
                result = None
                return result, bracket_flag, into_brackets, base_letter
        elif letter == ']':
            if not bracket_flag:
                raise ValueError("You close square brackets that you didn't open.")
            value = ''.join(into_brackets)
            result = self.regexp_unit(letter=base_letter, value=value)
            bracket_flag = False
            into_brackets = None
            return result, bracket_flag, into_brackets, base_letter
        else:
            if bracket_flag:
                into_brackets.append(letter)
                result = None
            else:
                base_letter = letter
                if next_letter != '[':
                    result = self.regexp_unit(letter=letter, value=None)
                else:
                    result = None
            return result, bracket_flag, into_brackets, base_letter
