from polog.core.levels import Levels
from polog.handlers.file.base_formatter_fields_extractors import BaseFormatterFieldsExtractors
import types

class BaseFormatter:
    """
    Здесь происходит преобразование исходных данных в строку, которая будет записана в файл.
    """

    # Названия полей исходного словаря с данными, которые игнорируются.
    # Их содержимое никак не видоизменяется.
    FORBIDDEN_EXTRA_FIELDS = {
        'module',
        'service_name',
        'exception_type',
        'exception_message',
    }

    def __init__(self, separator):
        """
        Первый этап инициализации объекта - при его создании.

        Инициализация объекта разделена на 2 этапа.
        Первый этап - при создании объекта, второй - при записи первого лога.
        В данном случае мы опираемся на то, что пользователь обязан завершить настройку логгера до его первого вызова. То есть до первого вызова мы не знаем в точности все настройки. Поэтому окончательно все настройки фиксируются только при первом вызове.

        separator - разделитель между строками логов, обычно "\n".
        """
        self.separator = separator

    def __init_on_run__(self):
        """
        Второй этап инициализации объекта - при первом вызове метода .get_formatted_string().
        Данный метод будет вызван только один раз, после чего он больше не будет нужен.
        """
        self.FIELD_HANDLERS = self.get_base_field_handlers()
        self.ALIGN_NORMS = self.get_align_norms()

    def get_formatted_string(self, args, **kwargs):
        """
        При первом вызове данного метода он будет переопределен методом _get_formatted_string().
        Здесь происходит вызов вторичной инициализации объекта, после чего происходит запись лога и метод становится не нужным.
        """
        self.__init_on_run__()
        result = self._get_formatted_string(args, **kwargs)
        self.get_formatted_string = self._get_formatted_string
        return result

    def _get_formatted_string(self, args, **kwargs):
        """
        Начиная со второго вызова метода get_formatted_string(), будет сразу вызван данный метод, т. к. он заменит собою get_formatted_string().

        Форматирование лога происходит в 3 этапа:

        1. Формирование словаря с подстроками.
        2. Форматирование подстрок по ширине.
        3. Создание одной большой строки из нескольких "кусочков".
        """
        data = self.get_dict(args, **kwargs)
        self.width_and_align(data)
        result = self.format(data)
        return result

    def get_base_field_handlers(self):
        """
        Данный метод срабатывает на 2 этапе инициализации.

        Возвращает словарь, где ключи - названия исходных полей лога (не обязательно исходных полей, поле может быть создано с таким названием), а значения - некие функции, которые берут исходные данные и делают из них некую подстроку, т. е. кусочек будущего лога. Эти кусочки позднее будут склеены, в другом методе.
        """
        result = {
            'time': BaseFormatterFieldsExtractors.time,
            'level': BaseFormatterFieldsExtractors.level,
            'success': BaseFormatterFieldsExtractors.success,
            'auto': BaseFormatterFieldsExtractors.auto,
            'message': BaseFormatterFieldsExtractors.message,
            'function': BaseFormatterFieldsExtractors.function,
            'time_of_work': BaseFormatterFieldsExtractors.time_of_work,
            'input_variables': BaseFormatterFieldsExtractors.input_variables,
            'local_variables': BaseFormatterFieldsExtractors.local_variables,
            'result': BaseFormatterFieldsExtractors.result,
            'exception': BaseFormatterFieldsExtractors.exception,
            'traceback': BaseFormatterFieldsExtractors.traceback,
        }
        return result

    def get_align_norms(self):
        """
        Часть второго этапа инициализации. Возвращаем словарь с правилами выравнивания для отдельных полей.

        Значения в словаре - кортежи из 2-х элементов.
        Первый элемент каждого кортежа - ширина поля. Если исходный контент меньше, он будет дополнен пробелами.
        Второй элемент - индикатор выравнивания (см. https://www.python.org/dev/peps/pep-3101/#standard-format-specifiers).
        """
        result = {
            'level': (max(max([len(x) for x in Levels.get_all_names()], default=2), len('UNKNOWN')), '^'), # Длина самого длинного названия уровня логирования.
            'success': (7, '^'),
            'auto': (6, '^'),
        }
        return result

    def get_dict(self, args, **kwargs):
        """
        Из исходных данных формируем словарь, заполненный только нужными полями, в уже отформатированном виде.
        Потом останется этот словарь только "склеить" в одну строку.
        """
        result = {}
        self.add_base_fields(result, args, **kwargs)
        self.add_extra_fields(result, args, **kwargs)
        return result

    def add_base_fields(self, base, args, **kwargs):
        """
        Базовые поля - это те, для которых прописаны специальные обработчики в self.FIELD_HANDLERS.
        Здесь мы вызываем все эти обработчики.
        """
        for field_name, extractor in self.FIELD_HANDLERS.items():
            try:
                value = extractor(**kwargs)
            except:
                try:
                    value = str(kwargs[field_name])
                except:
                    value = None
            if value is not None:
                base[field_name] = value

    def add_extra_fields(self, base, args, **kwargs):
        """
        Добавляем в словарь с данными поля, отсутствующие в self.FIELD_HANDLERS.
        """
        for field_name, value in kwargs.items():
            if field_name not in base:
                if field_name not in self.FORBIDDEN_EXTRA_FIELDS:
                    if value is not None:
                        base[field_name] = f'{field_name}: "{value}"'

    def format(self, data):
        """
        Берем словарь с уже отформатированными данными и делаем из него строку.
        """
        values = data.values()
        return ' | '.join(values) + self.separator

    def width_and_align(self, data):
        """
        Для некоторых полей заданы нормы форматирования (self.ALIGN_NORMS). Здесь происходит применение этих норм.

        data - словарь с полями лога.
        """
        for field_name in self.ALIGN_NORMS:
            item = data.get(field_name, None)
            if item is not None:
                width, align = self.ALIGN_NORMS[field_name]
                value = f'{item:{align}{width}}'
                data[field_name] = value
