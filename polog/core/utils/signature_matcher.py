from inspect import Signature


class SignatureMatcher:
    def __init__(self, *args):
        self.is_args = '*' in args
        self.is_kwargs = '**' in args
        self.number_of_position_args = len([x for x in args if x == '.'])
        self.number_of_named_args = len([x for x in args if x.isidentifier()])
        self.names_of_named_args = [x for x in args if x.isidentifier()]

    def match(self, function):
        if not callable(function):
            raise ValueError('It is impossible to determine the signature of an object that is not being callable.')
        signature = Signature.from_callable(function)
        parameters = list(signature.parameters.values())
        result = True
        result *= self.prove_is_args(parameters)
        result *= self.prove_is_kwargs(parameters)
        result *= self.prove_number_of_position_args(parameters)
        result *= self.prove_number_of_named_args(parameters)
        result *= self.prove_names_of_named_args(parameters)
        return result

    def prove_is_args(self, parameters):
        pass

    def prove_is_kwargs(self, parameters):
        pass

    def prove_number_of_position_args(self, parameters):
        """
        Проверка, что количество позиционных аргументов совпадает с ожидаемым.
        """
        return self.number_of_position_args == len([parameter for parameter in parameters if parameter.kind == parameter.POSITIONAL_ONLY])

    def prove_number_of_named_args(self, parameters):
        pass

    def prove_names_of_named_args(self, parameters):
        pass
