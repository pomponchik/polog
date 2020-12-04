from polog.base_settings import BaseSettings


def extract_extra_fields(args, args_dict):
    settings = BaseSettings()
    extra_fields = settings.extra_fields
    for name, field in extra_fields.items():
        try:
            value = field.extract(args, **args_dict)
            args_dict[name] = value
        except:
            pass
