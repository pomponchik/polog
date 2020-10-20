import time
import atexit
from polog.base_settings import BaseSettings


class Worker(object):
    """
    Экземпляр класса соответствует одному потоку. Здесь происходит непосредственно запись в БД.
    """
    def __init__(self, queue, index):
        self.index = index
        self.queue = queue
        # Метка full нужна, чтобы не завершить поток раньше времени, когда он уже взял таску из очереди, но еще не успел записать ее в БД.
        # По умолчанию метка в фиктивном положительном положении, чтобы исключить ситуацию с преждевременным прекращением потока при очень быстром завершении программы. Если метка по умолчанию будет отрицательной, функция ожидания завершения не будет дожидаться окончания записи и прервет поток на самом интересном месте.
        self.full = True
        self.await_empty_queue()

    def run(self):
        """
        Принимаем из очереди словари с данными для записи в БД и собственно записываем их.
        """
        while True:
            try:
                items = self.queue.get()
                self.full = True
                self.do_anything(items[0], **(items[1]))
                self.full = False
            except Exception as e:
                # Если не удалось записать лог в бд, запись уничтожается.
                self.full = False

    def do_anything(self, **kwargs):
        """
        Выполняем кастомные обработчики для записи логов.
        """
        for handler in BaseSettings().handlers:
            try:
                handler(**kwargs)
            except Exception as e:
                print(e)

    def await_empty_queue(self):
        """
        Прежде, чем завершить программу, дожидаемся, пока все потоки запишут в базу последние сообщения.
        Лимит на ожидание берется из настроек. Он необходим для разрешения ситуации, когда поток еще ни разу не писал в лог сообщений, и соответственно статус заполненности у него фиктивный, в результате чего из него невозможно выйти.
        """
        @atexit.register
        def full_checker():
            start_awaiting_time = time.time()
            while True:
                maybe_finish = time.time()
                time_delta = maybe_finish - start_awaiting_time
                if time_delta > BaseSettings().delay_before_exit:
                    break
                if (not self.full) and self.queue.empty():
                    break
