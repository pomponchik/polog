import sys

import pytest

from polog.core.utils.cut_traceback import cut_traceback


def test_compare_counters_traceback_cutting_on_and_off():
    """
    Проверяем, что обрезание трейсбека действительно работает, то есть трейсбек становится меньше, чем если обрезание не делать.
    Также проверяем, что при настройке 'traceback_cutting' в положении False длина трейсбека аналогична тому, что обрезание не запускалось бы вовсе.
    """
    try:
        raise ValueError
    except:
        cut_traceback({'traceback_cutting': True})
        _, _, tb = sys.exc_info()
        counter_1 = 0
        while tb:
            counter_1 += 1
            tb = tb.tb_next

    try:
        raise ValueError
    except:
        cut_traceback({'traceback_cutting': False})
        _, _, tb = sys.exc_info()
        counter_2 = 0
        while tb:
            counter_2 += 1
            tb = tb.tb_next

    try:
        raise ValueError
    except:
        _, _, tb = sys.exc_info()
        counter_3 = 0
        while tb:
            counter_3 += 1
            tb = tb.tb_next

    assert counter_1 < counter_2
    assert counter_1 < counter_3
    assert counter_2 == counter_3
