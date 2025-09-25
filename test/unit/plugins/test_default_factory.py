from carlyleconfig.plugins import DefaultFactoryPlugin
from carlyleconfig.key import ConfigKey
from carlyleconfig.plugins.default_factory import DefaultFactoryProvider


def test_plugin():
    plugin = DefaultFactoryPlugin()
    assert plugin.factory_name == "default_factory"
    assert plugin.provider_name == DefaultFactoryProvider.__name__


def test_plugin_injection():
    key = ConfigKey()
    plugin = DefaultFactoryPlugin()
    plugin.inject_factory_method(key)
    assert hasattr(key, "from_default_factory")


def test_provider():
    provider = DefaultFactoryProvider(list)
    assert provider.provide() == []
