class AbstractSingleLock:
    """
    Все единичные классы блокировок, унаследованные от данного класса:
    1. Должны переопределить методы .acquire() и .release().
    2. Являются отключаемыми. То есть, после вызова метода .off() у их экземпляров они просто не работают.
    """
    active = True

    def off(self):
        """
        Отключение блокировки.

        После вызова данного метода методы .acquire() и .release() перестают работать. Откатить это нельзя, операция одноразовая, поэтому рекомендуется применять при инициализации экземпляра отнаследованного класса.
        """
        self.acquire = self.empty_acquire
        self.release = self.empty_release
        self.active = False

    def acquire(self):
        """
        Взять лок.

        Должно быть переопределено наследником.
        """
        raise NotImplementedError('The basic action for the blocking class is not spelled out.')

    def release(self):
        """
        Отпустить лок.

        Должно быть переопределено наследником.
        """
        raise NotImplementedError('The basic action for the blocking class is not spelled out.')

    def empty_acquire(self):
        """
        Сделать вид, что взял лок.
        """
        pass

    def empty_release(self):
        """
        Сделать вид, что отпустил лок.
        """
        pass
