import pytest

from carlyleconfig.plugins import EnvVarPlugin
from carlyleconfig.plugins.envvar import EnvVarProvider
from carlyleconfig.key import ConfigKey


def test_plugin():
    plugin = EnvVarPlugin()
    assert plugin.factory_name == "env_var"
    assert plugin.provider_name == EnvVarProvider.__name__


def test_plugin_injection():
    key = ConfigKey
    plugin = EnvVarPlugin()
    plugin.inject_factory_method(key)
    assert hasattr(key, "from_env_var")


@pytest.mark.parametrize(
    "key,cast,expected",
    [
        ("foo", None, "bar"),
        ("empty", None, ""),
        ("missing", None, None),
        ("foo", bool, True),
        ("empty", bool, False),
        ("missing", bool, None),
    ],
)
def test_provider(key, cast, expected):
    provider = EnvVarProvider(
        key,
        cast=cast,
        environ={
            "empty": "",
            "foo": "bar",
        },
    )
    value = provider.provide()
    assert value == expected
