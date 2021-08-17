import time
from polog.core.engine.real_engines.multithreaded.worker import Worker
from queue import Queue


class ThreadPool:
    def __init__(self, settings):
        self.settings = settings
        self.queue = Queue(maxsize=self.settings.force_get('max_queue_size'))
        self.workers = self.create_workers()

    def put(self, function_input_data, **fields):
        self.queue.put(function_input_data, **fields)

    def stop(self):
        """
        Остановка воркеров.

        Подразумевается, что объект, останавливающий группу потоков, проконтролирует, что в процессе остановки очередь пополняться не будет.

        Этапы остановки:
        1. Дождаться опустошения очереди.
        2. Проставить флаги остановки воркерам. Воркер нельзя просто "убить". Он должен завершить работу с текущим таском, после чего проверит флаг остановки, и, если он установлен - выйти из цикла.
        3. Заджойнить потоки воркеров.
        """
        self.wait_empty_queue()
        for worker in self.workers:
            worker.set_stop_flag()
        for worker in self.workers:
            worker.stop()

    def wait_empty_queue(self):
        delay = self.settings['time_quant'] * self.settings['delay_on_exit_loop_iteration_in_quants']
        while True:
            if self.queue.empty():
                break
            time.sleep(delay)

    def create_workers(self):
        workers = []
        for index in range(self.settings.force_get('pool_size')):
            worker = Worker(self.queue, index, self.settings)
            workers.append(worker)
        return workers
