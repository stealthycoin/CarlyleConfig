import argparse

import pytest

from carlyleconfig.plugins import ArgParsePlugin
from carlyleconfig.plugins.argparse import ArgParsePendingProvider
from carlyleconfig.plugins.ssmplugin import SSMPlugin
from carlyleconfig.plugins.argparse import wrapper
from carlyleconfig.key import ConfigKey
from carlyleconfig import deriveconfig
from carlyleconfig.environment import ConfigEnvironment


class FakeParser:
    def __init__(self):
        self.arguments = []

    def parse_args(self):
        return argparse.Namespace(foo="bar")

    def add_argument(self, *args, **kwargs):
        self.arguments.append((args, kwargs))


def test_plugin():
    parser = FakeParser()
    plugin = ArgParsePlugin(parser)
    assert plugin.factory_name == "argparse"
    assert plugin.provider_name == ArgParsePendingProvider.__name__
    assert plugin.args is None


def test_plugin_injection():
    key = ConfigKey()
    parser = FakeParser()
    plugin = ArgParsePlugin(parser)
    plugin.inject_factory_method(key)
    assert hasattr(key, "from_argparse")


def test_plugin_arg_parse_interception():
    parser = FakeParser()
    plugin = ArgParsePlugin(parser)
    args = parser.parse_args()
    assert plugin.args == argparse.Namespace(foo="bar")
    assert args == argparse.Namespace(foo="bar")
    assert args == plugin.args


@pytest.fixture
def plugin():
    parser = FakeParser()
    plugin = ArgParsePlugin(parser)
    return plugin


@pytest.fixture
def provider(plugin):
    provider = wrapper(plugin)("--key")
    return provider


@pytest.mark.parametrize(
    "param,extra,args,expected",
    [
        ("--key", {}, ["--key", "value"], "value"),
        ("--debug", {"action": "store_true"}, ["--debug"], True),
        ("--debug", {"action": "store_true"}, [], False),
    ],
)
def test_provider(param, extra, args, expected):
    key = ConfigKey()
    parser = argparse.ArgumentParser()
    plugin = ArgParsePlugin(parser)
    plugin.inject_factory_method(key)
    key.from_argparse(param, **extra)
    parser.parse_args(args)
    provider = key.providers[0]
    assert provider.provide() == expected


def test_argparse_auto_help():
    parser = argparse.ArgumentParser()
    environment = ConfigEnvironment()
    ArgParsePlugin(update_help=True)
    environment.add_plugin(SSMPlugin("/prefix/"))

    @deriveconfig
    class Config:
        value = (
            environment.field()
            .from_argparse("--value", help="Falls back to: ")
            .from_env_var("VALUE")
            .from_ssm_parameter("value")
            .from_file("path.txt")
            .from_constant("default value")
        )

    environment.get_plugin(ArgParsePlugin).bind_parser(parser)
    assert parser._actions[1].help == (
        "Falls back to: "
        "environment variable VALUE, "
        "AWS SSM Parameter /prefix/value, "
        "file path.txt, "
        "defaults to default value"
    )
