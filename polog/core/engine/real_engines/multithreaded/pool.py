import time
from queue import Queue

from polog.core.engine.real_engines.multithreaded.worker import Worker


class ThreadPool:
    """
    Группа потоков-воркеров, обрабатывающая запись логов. Каждый воркер смотрит в общую очередь и забирает оттуда данные.

    Группа поддерживает команды, относящиеся ко всей группе сразу:
    .put(<данные лога>) - записать лог.
    .stop() - дождаться записи всех логов в очереди, после чего завершить потоки-воркеры и присоединить их.
    """
    def __init__(self, settings):
        self.settings = settings
        self.queue = Queue(maxsize=self.settings.force_get('max_queue_size'))
        self.workers = self.create_workers()

    def put(self, log_item):
        """
        Помещение лога в очередь.
        """
        self.queue.put(log_item)

    def stop(self):
        """
        Остановка воркеров.

        Подразумевается, что объект, останавливающий группу потоков, проконтролирует, что в процессе остановки очередь пополняться не будет.

        Этапы остановки:
        1. Дождаться опустошения очереди.
        2. Проставить флаги остановки воркерам. Воркер нельзя просто "убить". Он должен завершить работу с текущим таском, после чего проверить флаг остановки, и, если он установлен - выйти из цикла.
        3. Заджойнить потоки воркеров.
        """
        self.wait_empty_queue()
        for worker in self.workers:
            worker.set_stop_flag()
        for worker in self.workers:
            worker.stop()

    def wait_empty_queue(self):
        """
        Опрашиваем очередь с некоторой периодичностью, пока она не опустеет. Когда очередь опустела, выходим.

        Периодичность опроса определяется двумя пунктами настроек - 'time_quant' и 'delay_on_exit_loop_iteration_in_quants'.
        'time_quant' - временной квант, константа, определяющая минимальное время выполнения любой операции (в секундах).
        'delay_on_exit_loop_iteration_in_quants' - количество квантов (целое число), на которое мы засыпаем в каждой итерации цикла опроса.
        """
        delay = self.settings['time_quant'] * self.settings['delay_on_exit_loop_iteration_in_quants']
        while True:
            if self.queue.empty():
                break
            time.sleep(delay)

    def create_workers(self):
        """
        Создание и запуск воркеров.
        """
        workers = []
        for index in range(self.settings.force_get('pool_size')):
            worker = Worker(self.queue, index, self.settings)
            workers.append(worker)
        return workers
