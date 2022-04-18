import string

import pytest

from carlyleconfig.plugins import SSMPlugin
from carlyleconfig.plugins.ssmplugin import SSMProvider
from carlyleconfig.key import ConfigKey


class FakeClient:
    def __init__(self, result):
        self.recorded = []
        self.result = result

    def get_parameters(self, Names, WithDecryption):
        assert WithDecryption is True
        self.recorded.append(Names)
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
    assert plugin.provider_name == SSMProvider.__name__

    plugin.add_name("foo")
    plugin.add_name("bar")

    assert plugin.value_for_name("foo") == "foovalue"
    assert plugin.value_for_name("bar") == "barvalue"

    assert client.recorded == [["/prefix/foo", "/prefix/bar"]]


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
    args = {}
    if cast is not None:
        args["cast"] = cast
    key.from_ssm_parameter(name, **args)
    provider = key.providers[0]
    assert provider.provide() == expected


def test_ssm_api_limit():
    sequence = string.ascii_lowercase[0:11]
    ssm_params = {f"/prefix/{v}": v for v in sequence}
    client = FakeClient(
        {"Parameters": [{"Name": k, "Value": v} for k, v in ssm_params.items()]}
    )
    plugin = SSMPlugin("/prefix/", client=client)
    for v in sequence:
        plugin.add_name(v)

    for v in sequence:
        assert plugin.value_for_name(v) == v

    # Limit to names sent to the SSM Get Parameter API is 10.
    # So if we try to fetch 11 it should be broken up into 2 requests.
    # One with the first 10 elements, and one with a single leftover
    # element.
    assert len(client.recorded) == 2
    assert len(client.recorded[0]) == 10
    assert len(client.recorded[1]) == 1
