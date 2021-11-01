import pytest

from polog.handlers.file.rotation.rules.rules_elector import RulesElector
from polog.handlers.file.rotation.rules.rules.file_size_rule import FileSizeRule
from polog.handlers.file.file_dependency_wrapper import FileDependencyWrapper


def test_rules_elector_base_behavior_with_file_size_rule(filename_for_test):
    file = FileDependencyWrapper([filename_for_test], lock_type='thread+file')
    elector = RulesElector(file)

    assert isinstance(elector.choose('20 mb'), FileSizeRule)

def test_rules_elector_base_behavior_with_no_rules(filename_for_test):
    file = FileDependencyWrapper([filename_for_test], lock_type='thread+file')
    elector = RulesElector(file)

    with pytest.raises(ValueError):
        elector.choose('20 milliwatt')

    with pytest.raises(ValueError):
        elector.choose('twenty mb')

    with pytest.raises(ValueError):
        elector.choose('jnsdvkjnsdfkjncvs')
