import pytest

from polog.handlers.file.rotation.rules.rules.file_size_rule import FileSizeRule
from polog.handlers.file.file_dependency_wrapper import FileDependencyWrapper


class FileDependencyWrapperMock:
    def __init__(self, size):
        self.size = size
    def get_size(self):
        return self.size


def test_less_or_equal_than_zero_multiplier_in_file_size(filename_for_test):
    """
    Проверяем, что нельзя указать отрицательный или нулевой размер файла.
    """
    assert FileSizeRule('-12 mb', None).prove_source() == False
    assert FileSizeRule('0 mb', None).prove_source() == False

def test_check_file_size():
    """
    Проверяем, что проверка размера файла проходит корректно.
    """
    assert FileSizeRule('12 mb', FileDependencyWrapperMock(12 * 1024 * 1024)).check() == True
    assert FileSizeRule('12 mb', FileDependencyWrapperMock(12 * 1024 * 1024 - 1)).check() == False
