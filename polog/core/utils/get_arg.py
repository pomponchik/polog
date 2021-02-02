def get_arg(obj, args, arg_name, key_name=None):
    if key_name is None:
        key_name = arg_name.replace('_', '')
    arg = getattr(obj, arg_name, None)
    if arg:
        args[key_name] = arg
