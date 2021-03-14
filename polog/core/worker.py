import time
import atexit
from polog.core.settings_store import SettingsStore


class Worker:
    """
    Экземпляр класса соответствует одному потоку. Здесь происходит непосредственно выполнение функций-обработчиков.
    """
    def __init__(self, queue, index, settings=SettingsStore()):
        self.index = index
        self.queue = queue
        # Метка full нужна, чтобы не завершить поток раньше времени, когда он уже взял таску из очереди, но еще не успел ее обработать.
        # По умолчанию метка в фиктивном положительном положении, чтобы исключить ситуацию с преждевременным прекращением потока при очень быстром завершении программы. Если метка по умолчанию будет отрицательной, функция ожидания завершения не будет дожидаться окончания записи и прервет поток на самом интересном месте.
        self.full = True
        self.settings = settings
        self.await_empty_queue()

    def run(self):
        """
        Принимаем из очереди данные и что-то с ними делаем.
        """
        while True:
            try:
                items = self.queue.get()
                self.full = True
                # items - это всегда кортеж из 2-х элементов.
                self.do_anything(items[0], **(items[1]))
                self.queue.task_done()
                self.full = False
            except Exception as e:
                self.queue.task_done()
                # Если не удалось записать лог, запись уничтожается.
                self.full = False

    def do_anything(self, args, **kwargs):
        """
        Выполняем кастомные обработчики для записи логов. Если один из них поднимет исключение, гасим его и продолжаем выполнять оставшиеся обработчики.
        """
        for handler in self.settings.handlers.values():
            try:
                handler(args, **kwargs, service_name=self.settings.service_name)
            except Exception as e:
                pass

    def await_empty_queue(self):
        """
        Прежде, чем завершить программу, дожидаемся, пока все потоки обработают последние сообщения.
        Лимит на ожидание берется из настроек. Он необходим для разрешения ситуации, когда поток еще ни разу не писал в лог сообщений, и соответственно статус заполненности у него фиктивный, в результате чего из него невозможно выйти.
        """
        @atexit.register
        def full_checker():
            start_awaiting_time = time.time()
            while True:
                maybe_finish = time.time()
                time_delta = maybe_finish - start_awaiting_time
                if time_delta > self.settings.delay_before_exit:
                    break
                if (not self.full) and self.queue.empty():
                    break
