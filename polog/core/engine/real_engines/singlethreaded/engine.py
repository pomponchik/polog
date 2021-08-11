from polog.core.engine.real_engines.abstract import AbstractRealEngine
from polog.core.utils.exception_escaping import exception_escaping


class SingleThreadedRealEngine(AbstractRealEngine):
    """
    Однопоточная синхронная реализация движка.
    """
    def write(self, function_input_data, **fields):
        """
        Передаем данные о событии в обработчики.
        """
        for handler in self.settings.handlers.values():
            self.call_handler(handler, function_input_data, fields)

    @exception_escaping
    def call_handler(self, handler, function_input_data, fields):
        """
        Вызов одного обработчика.
        """
        handler(function_input_data, **fields, service_name=self.settings['service_name'])
