from pony.orm import db_session, count
from polog.model import Log
from polog.handlers.pony.select_items import select_items


logs = Log
select = select_items
