from pony.orm import select
from pony.orm import db_session
from polog.model import Log
from polog.connector import Connector


def select_items(generator):
    """
    Замена оригинальной функции select() из Pony ORM, во всем идентичная оригиналу, кроме того, что тут результат всегда отсортирован по полю time.
    """
    connect = Connector()
    items = select(generator)
    if items is None:
        return items
    items = items.order_by(Log.time)
    return items
