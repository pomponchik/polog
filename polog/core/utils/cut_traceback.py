try:
    from sys import exc_info
    from _testcapi import set_exc_info


    def cut_traceback(store):
        """
        Обрезаем 1 уровень трейсбека. Полезно для использования в декораторах, чтобы они не "мусорили" в трейсбек.
        """
        if store['traceback_cutting']:
            tp, exc, tb = exc_info()
            set_exc_info(tp, exc, tb.tb_next)

except ImportError: # pragma: no cover
    def cut_traceback(store):
        """
        Модуль _testcapi может быть не доступен в некоторых интерпретаторах. В этих случаях обрезание трейсбека происходить не будет.

        См.:
        1. https://stackoverflow.com/a/68908998/14522393
        2. https://stackoverflow.com/a/73418463/14522393
        """
        pass
