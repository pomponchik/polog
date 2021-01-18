import collections


class TokensGroup:
    regexp_unit = collections.namedtuple('regexp_unit', 'letter value')

    def __init__(self, tokens_list):
        self.tokens = tokens_list

    def __getitem__(self, key):
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
        if not isinstance(regexp, str):
            raise ValueError('The regexp variable must be str instance.')
        if regexp == '':
            return True
        regexp = self.parse_regexp(regexp)
        try:
            return self.regexp_loop(regexp, self.tokens, 0, 0)
        except RecursionError:
            return False

    def regexp_loop(self, regexp, tokens, tokens_index, regexp_index):
        if regexp_index >= len(regexp):
            return
        while tokens_index < len(tokens):
            unit = regexp[regexp_index]
            token = tokens[tokens_index]
            if unit.letter == token.regexp_letter:
                tokens_index += 1
                regexp_index += 1
            else:
                if unit.letter == '*':
                    tokens_index += 1
                    return self.regexp_loop(regexp, tokens, tokens_index, regexp_index)
                else:
                    return False
            tokens_index += 1
        return True

    def parse_regexp(self, regexp):
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
        if letter == '[':
            if bracket_flag:
                raise ValueError('Extra token "[" in the regexp.')
            else:
                if base_letter is None:
                    raise ValueError("The value of the regular expression token must be specified in square brackets. You didn't specify a token for this.")
                if base_letter == '.' or base_letter == '*':
                    raise ValueError("""Values can only be specified for "specific" regular expression elements. You cannot specify values in square brackets for elements '*' or '.'.""")
                bracket_flag = True
                into_brackets = []
                result = None
                return result, bracket_flag, into_brackets, base_letter
        elif letter == ']':
            if not bracket_flag:
                raise ValueError("You close square brackets that you didn't open.")
            value = ''.join(into_brackets)
            result = regexp_unit(letter=base_letter, value=value)
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
