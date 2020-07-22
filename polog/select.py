from polog.model import Log
from polog.utils.select_items import select_items
from pony.orm import db_session, count


logs = Log
select = select_items
