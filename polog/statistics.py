class Statistics:
    def __init__(self, logs):
        if logs is None:
            raise ValueError('None is not logs object!')
        self.logs = logs
