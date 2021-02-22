from polog.core.base_settings import BaseSettings


def extract_extra_fields(args, args_dict, settings=BaseSettings()):
    """
    Функция, извлекающая данные всех дополнительных полей из исходных данных.
    Если поле уже заполнено ранее, здесь оно не изменяется.
    """
    extra_fields = settings.extra_fields
    for name, field in extra_fields.items():
        if name not in args_dict:
            try:
                value = field.get_data(args, **args_dict)
                args_dict[name] = value
            except:
                pass
