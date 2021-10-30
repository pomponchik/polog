import pytest

from polog.handlers.file.rotation.rules.rules.tokenization.tokens.tokens_group import TokensGroup
from polog.handlers.file.rotation.rules.rules.tokenization.tokens import SizeToken, NumberToken, DotToken


def test_check_regexp_base_behavior():
    """
    Пробуем разные паттерны.
    """
    group = TokensGroup([NumberToken('20'), DotToken('milliwatt')])
    assert group.check_regexp('..')
    assert group.check_regexp('**')
    assert group.check_regexp('*.*')
    assert group.check_regexp('*n*')
    assert group.check_regexp('*d*')
    assert group.check_regexp('*nd*')
    assert group.check_regexp('*n*d*')
    assert group.check_regexp('*.*d*')
    assert group.check_regexp('*.*.*')
    assert group.check_regexp('*n*.*')
    assert group.check_regexp('n.')
    assert group.check_regexp('**..*')
    assert group.check_regexp('n*')
    assert group.check_regexp('.*')
    assert group.check_regexp('*.')
    assert group.check_regexp('.*.')
    assert group.check_regexp('.[20]*.')
    assert group.check_regexp('.[20]*.[milliwatt]')
    assert group.check_regexp('*')
    assert group.check_regexp('nd[milliwatt]')
    assert group.check_regexp('.d[milliwatt]')
    assert group.check_regexp('n[20]d')
    assert group.check_regexp('nd')
    assert group.check_regexp('.*')
    assert group.check_regexp('.d')
    assert group.check_regexp('*********')
    assert group.check_regexp('*d[milliwatt]')
    assert group.check_regexp('n[20]d[milliwatt]')
    assert not group.check_regexp('nd[milliwatts]')
    assert not group.check_regexp('nd[lol]')
    assert not group.check_regexp('nd[kek]')
    assert not group.check_regexp('n[21]d')
    assert not group.check_regexp('.[21]*.')
    assert not group.check_regexp('ns')
    assert not group.check_regexp('.')
    assert not group.check_regexp('...')
    assert not group.check_regexp('*d[milliwatts]')
    assert not group.check_regexp('n[21]d[milliwatt]')
    assert not group.check_regexp('n[20]d[milliwatts]')

    group = TokensGroup([NumberToken('20'), SizeToken('mb'), DotToken('kek'), NumberToken('1')])
    assert group.check_regexp('....')
    assert group.check_regexp('....*')
    assert group.check_regexp('...*')
    assert group.check_regexp('..*')
    assert group.check_regexp('.*')
    assert group.check_regexp('*')
    assert group.check_regexp('*....*')
    assert group.check_regexp('***....***')
    assert group.check_regexp('***.*.*.*.***')
    assert group.check_regexp('***.**.*.***')
    assert group.check_regexp('***.***.***')
    assert group.check_regexp('*****.****')
    assert group.check_regexp('*********')
    assert group.check_regexp('****.[mb]*****')
    assert group.check_regexp('****.[20]*****')
    assert group.check_regexp('****.[kek]*****')
    assert group.check_regexp('****.[1]*****')
    assert group.check_regexp('n[20]s[mb]d[kek]n[1]')
    assert group.check_regexp('n[20].[mb]d[kek]n[1]')
    assert group.check_regexp('n[20].[mb].[kek]n[1]')
    assert group.check_regexp('n[20].[mb].[kek].[1]')
    assert group.check_regexp('.[20].[mb].[kek].[1]')
    assert group.check_regexp('nsdn')
    assert not group.check_regexp('.[200].[mb].[kek].[1]')
    assert not group.check_regexp('.[20].[mbs].[kek].[1]')
    assert not group.check_regexp('.[20].[mb].[keks].[1]')
    assert not group.check_regexp('.[20].[mb].[kek].[11]')
    assert not group.check_regexp('.*.[11]')
    assert not group.check_regexp('.*....')
    assert not group.check_regexp('.....')
    assert not group.check_regexp('nsdn.')


def test_no_content_to_wildcard():
    """
    Проверяем, что для символа звездочки нельзя указать точное значение.
    """
    group = TokensGroup([NumberToken('20'), DotToken('milliwatt')])
    with pytest.raises(ValueError):
        group.check_regexp('**[milliwatt]')
