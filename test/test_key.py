import pytest
from typing import Any, List

from carlyleconfig.key import ConfigKey


class Provider:
    def __init__(self, value: Any):
        self.value = value

    def provide(self) -> Any:
        return self.value


@pytest.fixture
def providers():
    def build_providers(values: List[Any]):
        return [Provider(value) for value in values]

    return build_providers


@pytest.mark.parametrize(
    "seq,expected",
    [
        ([1, 2, 3], 1),
        ([None, None, 3], 3),
        ([None, 0, 3], 0),
        ([0, None, 3], 0),
        ([True, False, None], True),
        ([False, True, None], False),
        ([None, True, False], True),
        ([None, False, True], False),
        (["foo", "bar", "baz"], "foo"),
        (["", "bar", "baz"], ""),
        ([None, "bar", "baz"], "bar"),
    ],
)
def test_resolve(providers, seq, expected):
    actual = ConfigKey(providers=providers(seq)).resolve()
    assert actual == expected
