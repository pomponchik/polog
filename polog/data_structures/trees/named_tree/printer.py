class TreePrinter:
    """
    Класс, инкапсулирующий логику, связанную со строковым представлением дерева.
    """
    def __init__(self, tree, filler='\t'):
        self.tree = tree
        self.filler = filler

    def get_indented_representation(self):
        """
        Метод возвращает строковое представление дерева.

        Ноды дерева получаются путем обхода в глубину, соответствующим образом формируется и их порядок.

        Поскольку обход в глубину реализован через рекурсию, при превышении максимально допустимой глубины возвращается "болванка".
        То же самое происходит в случае, если все ноды дерева - пустые.

        Глубина расположения той или иной ноды дерева показана ее отступом от левого края.
        """
        data = []
        if not len(self.tree):
            return f'<{type(self.tree).__name__} empty object>'
        try:
            for node in self.tree.walker.dfs():
                full_name = node.get_full_name()
                indent = full_name.count(self.tree.keys_separator) + 1 if full_name != self.tree.keys_separator else 0
                filler = self.filler * indent
                name = node.name if node.name is not None else self.tree.keys_separator
                full_string = f'{filler}|\033[4m{name}\033[0m'
                data.append(full_string)
        except RecursionError:
            return f'<{type(self.tree).__name__} very big object>'
        indented_representation = '\n'.join(data)
        full_representation = f'<{type(self.tree).__name__}:\n{indented_representation}>'
        return full_representation
