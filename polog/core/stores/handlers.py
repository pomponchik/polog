from polog.data_structures.trees.named_tree.tree import NamedTree
from polog.core.utils.signature_matcher import SignatureMatcher


global_handlers = NamedTree(
    value_checker=SignatureMatcher.is_handler,
)
