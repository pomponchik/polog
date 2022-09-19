from polog.core.log_item import LogItem
from polog.core.stores.settings.actions.decorator import is_action


@is_action
def fields_intersection_action(old_value, new_value, store):
    """
    Коллбек, вызываемый при изменении настройки 'fields_intersection'.

    Внутри класса LogItem кэшируется значение данной настройки, поэтому нужно синхронизировать изменения внутри хранилища настроек и внутри класса.
    """
    LogItem._fields_intersection = new_value
