from pony.orm import select
from pony.orm import db_session
from polog.model import Log


@db_session
def select_items(generator):
    items = select(generator)
    if items is None:
        return items
    items = items.order_by(Log.time)
    return items
