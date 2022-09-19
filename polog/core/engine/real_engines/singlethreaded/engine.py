from polog.core.engine.real_engines.abstract import AbstractRealEngine
from polog.core.utils.exception_escaping import exception_escaping


class SingleThreadedRealEngine(AbstractRealEngine):
    """
    Однопоточная синхронная реализация движка.
    """
    def write(self, log_item):
        """
        "Выполняем" лог, то есть запускаем все привязанные к нему действия - извлечения полей, передачу лога в обработчики и т. д.
        """
        log_item()
