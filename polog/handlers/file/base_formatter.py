from polog.levels import Levels
from polog.handlers.file.base_formatter_fields_extractors import BaseFormatterFieldsExtractors


class BaseFormatter:
    FORBIDDEN_EXTRA_FIELDS = {
        'module',
        'service_name',
    }

    def __init__(self, separator):
        self.separator = separator

    def __init_on_run__(self):
        self.FIELD_HANDLERS = self.get_base_field_handlers()
        self.ALIGN_NORMS = self.get_align_norms()

    def __call__(self, args, **kwargs):
        self.__init_on_run__()
        result = self.__second_call__(args, **kwargs)
        self.__call__ = self.__second_call__
        return result

    def __second_call__(self, args, **kwargs):
        data = self.get_dict(args, **kwargs)
        self.width_and_align(data)
        result = self.format(data)
        return result

    def get_base_field_handlers(self):
        result = {
            'time': BaseFormatterFieldsExtractors.time,
            'level': BaseFormatterFieldsExtractors.level,
            'success': BaseFormatterFieldsExtractors.success,
            'auto': BaseFormatterFieldsExtractors.auto,
            'message': BaseFormatterFieldsExtractors.message,
            'function': BaseFormatterFieldsExtractors.function,
            'result': BaseFormatterFieldsExtractors.result,
            'time_of_work': BaseFormatterFieldsExtractors.time_of_work,
            'input_variables': BaseFormatterFieldsExtractors.input_variables,
            'local_variables': BaseFormatterFieldsExtractors.local_variables,
        }
        return result

    def get_align_norms(self):
        result = {
            'level': (max([len(x) for x in Levels.get_all_names()]), '^'),
            'success': (7, '^'),
            'auto': (6, '^'),
        }
        return result

    def get_dict(self, args, **kwargs):
        result = {}
        self.add_base_fields(result, args, **kwargs)
        self.add_extra_fields(result, args, **kwargs)
        return result

    def add_base_fields(self, base, args, **kwargs):
        for field_name, extractor in self.FIELD_HANDLERS.items():
            value = extractor(**kwargs)
            if value is not None:
                base[field_name] = str(value)

    def add_extra_fields(self, base, args, **kwargs):
        for field_name, value in kwargs.items():
            if field_name not in base:
                if field_name not in self.FORBIDDEN_EXTRA_FIELDS:
                    if value is not None:
                        base[field_name] = f'{field_name}: "{value}"'

    def format(self, data):
        values = data.values()
        return ' | '.join(values) + '\n'

    def width_and_align(self, data):
        for field_name in self.ALIGN_NORMS:
            item = data.get(field_name, None)
            if item is not None:
                width, align = self.ALIGN_NORMS[field_name]
                value = f'{item:{align}{width}}'
                data[field_name] = value
