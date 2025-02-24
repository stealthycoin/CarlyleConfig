from carlyleconfig.plugins import ConstantPlugin
from carlyleconfig.key import ConfigKey
from carlyleconfig.plugins.constant import ConstantProvider


def test_plugin():
    plugin = ConstantPlugin()
    assert plugin.factory_name == "constant"
    assert plugin.provider_name == ConstantProvider.__name__


def test_plugin_injection():
    key = ConfigKey()
    plugin = ConstantPlugin()
    plugin.inject_factory_method(key)
    assert hasattr(key, "from_constant")


def test_provider():
    provider = ConstantProvider("foo")
    assert provider.provide() == "foo"
