import pytest

from polog.handlers.file.locks.abstract_single_lock import AbstractSingleLock


class LittleLessAbstractLock(AbstractSingleLock):
    def __init__(self, on):
        if not on:
            self.off()

def test_off_lock_is_working():
    """
    Проверяем, что метод .off() - работает.
    Его задача - переопределять методы взятия и освобождения блокировки "болванками".
    """
    # Ничего не происходит, блокировка отключена за счет перегрузки метода.
    LittleLessAbstractLock(False).acquire()
    LittleLessAbstractLock(False).release()

    with pytest.raises(NotImplementedError):
        # Блокировка НЕ отключена, срабатывает метод, который должен быть переопределен в "нормальных" наследниках, поднимающий исключение.
        LittleLessAbstractLock(True).acquire()

    with pytest.raises(NotImplementedError):
        # Блокировка НЕ отключена, срабатывает метод, который должен быть переопределен в "нормальных" наследниках, поднимающий исключение.
        LittleLessAbstractLock(True).release()

def test_active_flag_is_working_for_abstract():
    """
    Проверяем, что атрибут .active проставляется правильно.
    """
    assert LittleLessAbstractLock(True).active == True
    assert LittleLessAbstractLock(False).active == False
