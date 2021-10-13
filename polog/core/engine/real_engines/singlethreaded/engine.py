from polog.core.engine.real_engines.abstract import AbstractRealEngine
from polog.core.utils.exception_escaping import exception_escaping


class SingleThreadedRealEngine(AbstractRealEngine):
    """
    Однопоточная синхронная реализация движка.
    """
    def write(self, log):
        """
        Передаем данные о событии в обработчики.
        """
        for handler in log.get_handlers():
            self.call_handler(handler, log)

    @exception_escaping
    def call_handler(self, handler, log):
        """
        Вызов одного обработчика.
        """
        handler(log)
