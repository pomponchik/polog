from polog.data_structures.trees.named_tree.node import NamedTreeNode


class NamedTree:
    def __init__(self):
        self.root = NamedTreeNode(self, None, '/', is_root=True)
        self.len = 0

    def __getitem__(self, key):
        keys = get_converted_keys(key)

    def __setitem__(self, key, value):
        keys = get_converted_keys(key)

    def __len__(self):
        return self.len

    def __iter__(self):
        pass

    def __contains__(self, key):
        pass

    def __delitem__(self, key):
        pass

    def get_converted_keys(self, key):
        if not isinstance(key, str):
            raise KeyError()
        keys = key.split('.')
        if any(not x.isidentifier() for x in keys):
            raise KeyError()
        return keys
