from polog.base_settings import BaseSettings


def extract_extra_fields(args_dict, args, **kwargs):
    settings = BaseSettings()
    extra_fields = settings.extra_fields
    for name, field in extra_fields.items():
        value = field.extract(args, **kwargs)
        args_dict[name] = value
