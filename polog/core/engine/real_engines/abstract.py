class AbstractRealEngine:
    def __init__(self, settings):
        self.settings = settings

    def write(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError
