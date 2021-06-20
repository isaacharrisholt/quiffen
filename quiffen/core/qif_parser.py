from quiffen.core import transactions


class QifParser:
    def __init__(self, path, day_first=True):
        self._path = path
        self.day_first = day_first
        with open(path, 'r') as f:
            self.data = f.read()
            self.data_by_line = f.readlines()

