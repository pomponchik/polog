from threading import Lock
from polog.data_structures.trees.named_tree.node import NamedTreeNode


class NamedTree:
    """
    Экземпляры данного класса представляют из себя деревья.

    Каждая нода дерева имеет имя. 
    """
    def __init__(self, keys_separator='.', key_checker=lambda key: x.isidentifier()):
        self.keys_separator = keys_separator
        self.key_checker = key_checker
        self.root = NamedTreeNode(self, None, '/', -1, is_root=True)
        self.len = 0
        self.lock = Lock()
        self.lst = []

    def __getitem__(self, key):
        with self.lock:
            keys = get_converted_keys(key)


    def __setitem__(self, key, value):
        with self.lock:
            keys = get_converted_keys(key)
            self.len += 1

    def __len__(self):
        with self.lock:
            return self.len

    def __iter__(self):
        pass

    def __contains__(self, key):
        with self.lock:
            pass

    def __delitem__(self, key):
        with self.lock:
            keys = get_converted_keys(key)
            self.len -= 1

    def get_converted_keys(self, key):
        if not isinstance(key, str):
            raise KeyError()
        keys = key.split(self.keys_separator)
        if any(not self.key_checker(x) for x in keys):
            raise KeyError()
        return keys
