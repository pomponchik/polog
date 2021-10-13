from queue import Empty
from threading import Thread


class Worker:
    """
    Экземпляр класса соответствует одному потоку. Здесь происходит непосредственно выполнение функций-обработчиков.
    """
    def __init__(self, queue, index, settings):
        self.index = index
        self.queue = queue
        self.stopped = False
        self.settings = settings
        self.thread = self.start_thread()

    def run(self):
        """
        В бесконечном цикле принимаем из очереди данные и что-то с ними делаем.

        На каждом обороте цикла, а также в случае слишком долгого ожидания блокировки очереди, необходимо проверять наличие стоп-сигнала. В случае получения стоп-сигнала, необходимо выйти из цикла, чтобы поток мог быть присоединен к основному.
        """
        stopped_from_flag = False
        while True:
            try:
                while True:
                    try:
                        log = self.queue.get(timeout=self.settings['time_quant'])
                        break
                    except Empty:
                        if self.stopped:
                            stopped_from_flag = True
                            break
                if stopped_from_flag:
                    break
                self.do_anything(log)
                self.queue.task_done()
            except Exception as e:
                self.queue.task_done()

    def start_thread(self):
        """
        Запуск отдельного потока, который будет принимать события из очереди.
        """
        thread = Thread(target=self.run)
        thread.daemon = True
        thread.start()
        return thread

    def set_stop_flag(self):
        """
        Устанавливаем флаг остановки.

        Флаг остановки проверяется внутри цикла обработки поступающих из очереди логов. Пока он не установлен, логи обрабатываются в штатном режиме. Когда флаг установлен, а очередь пуста - происходит выход из цикла.

        Установка флага - первый этап остановки воркера.
        """
        self.stopped = True

    def stop(self):
        """
        Останавливаем воркер.

        Это второй этап остановки воркера (см. также self.set_stop_flag()). Ожидается, что к моменту вызова данного метода флаг остановки уже установлен и цикл обработки логов прерван, что позволяет беспрепятственно присоединить поток воркера.
        """
        self.thread.join()

    def do_anything(self, log):
        """
        Выполняем кастомные обработчики для записи логов.

        Если один из них поднимет исключение, гасим его и продолжаем выполнять оставшиеся обработчики.
        """
        for handler in log.get_handlers():
            try:
                handler(log)
            except Exception as e:
                pass
