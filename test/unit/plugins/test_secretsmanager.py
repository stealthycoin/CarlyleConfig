import pytest

from carlyleconfig.plugins import SecretsManagerPlugin
from carlyleconfig.plugins.awssecretsmanager import SecretsManagerProvider
from carlyleconfig.key import ConfigKey


class FakeClient:
    def __init__(self, result):
        self.recorded = []
        self.result = result

    def get_secret_value(self, SecretId: str):
        self.recorded.append(SecretId)
        return self.result


def test_plugin():
    client = FakeClient({"SecretString": "secret"})
    plugin = SecretsManagerPlugin(client=client)

    assert plugin.factory_name == "secrets_manager"
    assert plugin.provider_name == SecretsManagerProvider.__name__

    assert plugin.get_secret("anything") == "secret"

    assert client.recorded == ["anything"]


def test_plugin_injection():
    key = ConfigKey()
    plugin = SecretsManagerPlugin()
    plugin.inject_factory_method(key)
    assert hasattr(key, "from_secrets_manager")


@pytest.mark.parametrize(
    "name,key,params,cast,expected",
    [
        ("name", None, {"SecretString": "foo"}, None, "foo"),
        ("name", None, {"SecretString": "42"}, None, "42"),
        ("name", None, {"SecretString": "42"}, str, "42"),
        ("name", None, {"SecretString": "42"}, int, 42),
        ("name", None, {"SecretString": ""}, bool, False),
        ("name", None, {"SecretString": "1"}, bool, True),
        ("name", None, {"SecretString": "true"}, bool, True),
        ("name", None, {}, None, None),
        ("name", None, {}, bool, None),
        ("name", None, {"SecretString": '{"foo": "bar"}'}, None, '{"foo": "bar"}'),
        ("name", "foo", {"SecretString": '{"foo": "bar"}'}, None, "bar"),
        ("name", "foo", {"SecretString": '{"foo": "1"}'}, int, 1),
        ("name", "foo", {"SecretString": '{"foo": "1"}'}, bool, True),
        ("name", "foo", {"SecretString": '{"foo": ""}'}, bool, False),
        ("name", "foo", {"SecretString": "{}"}, None, None),
        ("name", "foo", {"SecretString": "{}"}, bool, None),
    ],
)
def test_provider(name, key, params, cast, expected):
    client = FakeClient(params)
    config_key = ConfigKey()
    plugin = SecretsManagerPlugin(client=client)
    plugin.inject_factory_method(config_key)
    args = {}
    if cast is not None:
        args["cast"] = cast
    if key is not None:
        args["key"] = key
    config_key.from_secrets_manager(name, **args)
    provider = config_key.providers[0]
    assert provider.provide() == expected
