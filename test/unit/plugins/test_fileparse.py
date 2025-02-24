import os
import json
from dataclasses import dataclass, field
from typing import List, Tuple, Any

import pytest

from carlyleconfig.plugins import FilePlugin
from carlyleconfig.plugins.fileparse import FileProvider
from carlyleconfig.plugins.fileparse import identity
from carlyleconfig.key import ConfigKey


def test_plugin_name():
    plugin = FilePlugin()
    assert plugin.factory_name == "file"
    assert plugin.provider_name == FileProvider.__name__


def test_plugin_injection():
    key = ConfigKey
    plugin = FilePlugin()
    plugin.inject_factory_method(key)
    assert hasattr(key, "from_file")
    assert hasattr(key, "from_json_file")


@dataclass
class FakeOSUtils:
    canned_content: str

    def read_file(self, *args):
        return self.canned_content


@pytest.fixture
def osutils(request):
    return FakeOSUtils(request.param)


@pytest.mark.parametrize(
    "osutils,parser,expected",
    [
        ("foo", identity, "foo"),
        (None, identity, None),
        ("{}", json.loads, {}),
        ('{"foo": "bar"}', json.loads, {"foo": "bar"}),
        (None, json.loads, None),
        ('"foo"', json.loads, "foo"),
        ("foo", json.loads, json.JSONDecodeError),
        ("", json.loads, json.JSONDecodeError),
    ],
    indirect=["osutils"],
)
def test_plugin(osutils, parser, expected):
    plugin = FilePlugin(osutils=osutils)
    if type(expected) is type:
        with pytest.raises(expected):
            plugin.read_file("filename", parser)
    else:
        result = plugin.read_file("filename", parser)
        assert result == expected


@dataclass
class FakePlugin:
    canned_content: str
    record: List[Tuple[str, Any]] = field(default_factory=lambda: [])

    def read_file(self, path, parser):
        self.record.append((path, parser))
        return self.canned_content


@pytest.fixture
def plugin(request):
    return FakePlugin(request.param)


@pytest.mark.parametrize(
    "plugin,selector,expected",
    [
        ("foo", identity, "foo"),
        (None, identity, None),
        ({"foo": "bar"}, lambda x: x.get("foo"), "bar"),
        (None, lambda x: x.get("foo"), None),
        ({}, lambda x: x["foo"], KeyError),
        ("", lambda x: x["foo"], TypeError),
        (None, lambda x: x["foo"], None),
    ],
    indirect=["plugin"],
)
def test_provider(plugin, selector, expected):
    provider = FileProvider(plugin=plugin, filename="filename", selector=selector)
    if type(expected) is type:
        with pytest.raises(expected):
            provider.provide()
    else:
        value = provider.provide()
        assert value == expected
        assert plugin.record == [(os.path.abspath("filename"), provider.parser)]


@pytest.mark.parametrize(
    "osutils,jmespath,expected",
    [
        (json.dumps({"foo": "bar"}), "foo", "bar"),
        (json.dumps({"foo": "bar"}), "badkey", None),
        (json.dumps({"root": {"nested": "value"}}), "root.nested", "value"),
        (json.dumps({"list": ["foo", "bar", "baz"]}), "list[0]", "foo"),
        (json.dumps({"list": ["foo", "bar", "baz"]}), "list[1]", "bar"),
        (json.dumps({"list": ["foo", "bar", "baz"]}), "list[2]", "baz"),
    ],
    indirect=["osutils"],
)
def test_from_json_file(osutils, jmespath, expected):
    key = ConfigKey()
    plugin = FilePlugin(osutils=osutils)
    plugin.inject_factory_method(key)
    result = key.from_json_file("test", jmespath=jmespath)
    assert result.resolve() == expected
