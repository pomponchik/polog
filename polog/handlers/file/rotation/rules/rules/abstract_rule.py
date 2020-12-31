class AbstractRule:
    def __init__(self, source):
        self.source = source
        self.extract_data_from_string(source)

    def __repr__(self):
        type_name = type(self).__name__
        source = self.source
        result = f'{type_name}("{source}")'
        return result

    def extract_data_from_string(self, source):
        raise NotImplementedError

    @classmethod
    def prove_source(cls, source):
        raise NotImplementedError

    def check(self):
        raise NotImplementedError
