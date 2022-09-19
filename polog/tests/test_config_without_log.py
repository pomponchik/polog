from polog import config, file_writer


def do_log(filename):
    """
    Здесь используется, но нигде не импортируется функция log().
    Проверяем, что так можно.
    """
    config.add_handlers(file_writer(filename))
    config.set(log_is_built_in=True)

    log('kek')
