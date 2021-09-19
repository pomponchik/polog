class NamedTreeNode:
    def __init__(self, tree, parent, name, line_index, value=None, is_root=False):
        self.tree = tree
        self.parent = parent
        self.name = name
        self.line_index = line_index
        self.value = value
        self.is_root = is_root
        self.childs = {}

    def get(self):
        return self.value

    def set(self, value):
        self.value = value
