import pytest

from polog.core.stores.settings.actions.decorator import is_action, ItIsNotAnActionError


def test_not_an_action():
    """
    Пробуем скормить декоратору функции, не подходящие по сигнатуре, чтобы быть коллбеками для настроек.
    Должно подниматься ItIsNotAnActionError.
    """
    with pytest.raises(ItIsNotAnActionError):
        @is_action
        def not_action():
            pass

    with pytest.raises(ItIsNotAnActionError):
        @is_action
        def not_action(lol):
            pass

    with pytest.raises(ItIsNotAnActionError):
        @is_action
        def not_action(lol, kek):
            pass

    with pytest.raises(ItIsNotAnActionError):
        @is_action
        def not_action(lol, kek, cheburek, perekek):
            pass

def test_args_in_action_are_equal():
    """
    Коллбек должен срабатывать только в том случае, когда первый и второй аргументы отличаются.
    Проверяем, что это так.
    """
    @is_action
    def action(old_value, new_value, store):
        return 5

    assert action(1, 1, 2) is None
    assert action(1, 2, 3) == 5
