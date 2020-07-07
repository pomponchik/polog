from polog.utils.get_arg import get_arg


def get_base_args_dict(func, message):
    args_dict = {}
    args_dict['auto'] = True
    if not (message is None):
        args_dict['message'] = str(message)
    get_arg(func, args_dict, '__module__')
    get_arg(func, args_dict, '__name__', key_name='function')
    return args_dict
