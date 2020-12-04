class field:
    def __init__(self, extractor, converter=None):
        self.extractor = self.get_extractor(extractor)
        self.converter = self.get_converter(converter)

    def extract(self, args, **kwargs):
        return self.extractor(args, **kwargs)

    def convert(self, value):
        return self.converter(value)

    def get_extractor(self, extractor):
        if not callable(extractor):
            raise ValueError('Extractor must be called.')
        return extractor

    def get_converter(self, maybe_converter):
        if maybe_converter is None:
            return self.standart_converter
        if callable(maybe_converter):
            return maybe_converter
        raise ValueError('Converter must be called.')

    def standart_converter(self, value):
        result = str(value)
        return result
