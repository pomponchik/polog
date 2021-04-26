def not_none_to_dict(args_dict, key, value):
    """
    Если значение не None, кладем его в словарь.
    """
    if not (value is None):
        args_dict[key] = value
