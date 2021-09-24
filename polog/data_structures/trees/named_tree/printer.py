class TreePrinter:
    def __init__(self, tree, filler='\t'):
        self.tree = tree
        self.filler = filler

    def get_indented_representation(self):
        data = []
        if not len(self.tree):
            return f'<{type(self.tree).__name__} object>'
        for node in self.tree.walker.dfs():
            full_name = node.get_full_name()
            indent = full_name.count(self.tree.keys_separator) + 1 if full_name != self.tree.keys_separator else 0
            filler = self.filler * indent
            name = node.name if node.name is not None else self.tree.keys_separator
            full_string = f'{filler}|\033[4m{name}\033[0m'
            data.append(full_string)
        indented_representation = '\n'.join(data)
        full_representation = f'<{type(self.tree).__name__}:\n{indented_representation}>'
        return full_representation
