import pytest

from carlyleconfig.plugins import SSMPlugin
from carlyleconfig.key import ConfigKey


class FakeClient:
    def __init__(self, result):
        self.recorded = []
        self.result = result

    def get_parameters(self, Names):
        self.recorded.extend(Names)
        return self.result


def test_plugin():
    client = FakeClient(
        {
            "Parameters": [
                {"Name": "/prefix/foo", "Value": "foovalue"},
                {"Name": "/prefix/bar", "Value": "barvalue"},
            ]
        }
    )
    plugin = SSMPlugin("/prefix/", client=client)

    assert plugin.factory_name == "ssm_parameter"

    plugin.add_name("foo")
    plugin.add_name("bar")

    assert plugin.value_for_name("foo") == "foovalue"
    assert plugin.value_for_name("bar") == "barvalue"

    assert client.recorded == ["/prefix/foo", "/prefix/bar"]


def test_plugin_injection():
    key = ConfigKey()
    plugin = SSMPlugin()
    plugin.inject_factory_method(key)
    assert hasattr(key, "from_ssm_parameter")


@pytest.mark.parametrize(
    "prefix,name,params,cast,expected",
    [
        ("/prefix/", "foo", {"/prefix/foo": "foovalue"}, None, "foovalue"),
        ("", "/prefix/foo", {"/prefix/foo": "foovalue"}, None, "foovalue"),
        ("/prefix/", "bar", {"/prefix/foo": "foovalue"}, None, None),
        ("", "foo", {"/prefix/foo": "foovalue"}, None, None),
        ("/prefix/", "foo", {"/prefix/foo": ""}, bool, False),
        ("/prefix/", "foo", {"/prefix/foo": "1"}, bool, True),
        ("/prefix/", "foo", {"/prefix/foo": "true"}, bool, True),
        ("/prefix/", "foo", {}, bool, None),
    ],
)
def test_provider(prefix, name, params, cast, expected):
    client = FakeClient(
        {"Parameters": [{"Name": k, "Value": v} for k, v in params.items()]}
    )
    key = ConfigKey()
    plugin = SSMPlugin(prefix, client=client)
    plugin.inject_factory_method(key)
    key.from_ssm_parameter(name, cast=cast)
    provider = key.providers[0]
    assert provider.provide() == expected
