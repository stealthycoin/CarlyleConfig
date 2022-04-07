import argparse
import logging
from typing import Any, ClassVar, Optional, List
from types import MethodType

from dataclasses import dataclass, field
from carlyleconfig.plugins.base import BasePlugin
from carlyleconfig.key import ConfigKey


LOG = logging.getLogger(__name__)


@dataclass
class ArgParseProvider:
    name: str
    plugin: "ArgParsePlugin"

    def provide(self) -> Any:
        return getattr(self.plugin.args, self.name)


class ArgParsePendingProvider:
    def __init__(self, plugin: "ArgParsePlugin", name: str, **kwargs):
        self.plugin = plugin
        self.name = name
        self.provider: Optional[ArgParseProvider] = None
        self.kwargs = kwargs

    def provide(self) -> Any:
        if self.provider is None:
            return None
        value = self.provider.provide()
        LOG.debug("Providing: %s", value)
        return value

    def upgrade(self, parser: argparse.ArgumentParser):
        dest = install_arg(parser, self.name, **self.kwargs)
        self.provider = ArgParseProvider(dest, self.plugin)


def install_arg(parser: argparse.ArgumentParser, *args, **kwargs):
    LOG.debug("Installing arguments in parser %s, kwargs: %s", args, kwargs)
    argument = parser.add_argument(*args, **kwargs)
    return argument.dest


def wrapper(plugin: "ArgParsePlugin"):
    def with_argparse(self, name, **kwargs) -> ConfigKey:
        provider = ArgParsePendingProvider(plugin, name, **kwargs)
        plugin.install_provider(provider)
        self.providers.append(provider)
        return self

    return with_argparse


@dataclass
class ArgParsePlugin(BasePlugin):
    factory_name: ClassVar[str] = "argparse"
    parser: Optional[argparse.ArgumentParser] = None
    args: Optional[argparse.Namespace] = None
    on_bind: List[ArgParsePendingProvider] = field(default_factory=lambda: [])

    def bind_parser(self, parser: argparse.ArgumentParser):
        LOG.debug("Binding parser %s", parser)
        self.parser = parser
        self._capture_parse_args()

        for provider in self.on_bind:
            provider.upgrade(self.parser)

    def _capture_parse_args(self):
        parse_args = self.parser.parse_args

        def new_parse_args(*args):
            self.args = parse_args(*args)
            LOG.debug("Capturing args %s", self.args)
            return self.args

        self.parser.parse_args = new_parse_args

    def install_provider(self, provider):
        if self.parser is None:
            self.on_bind.append(provider)
        else:
            provider.upgrade(self.parser)

    def __post_init__(self):
        if self.parser is not None:
            self._capture_parse_args()

    def inject_factory_method(self, key: ConfigKey):
        name = f"from_{self.factory_name}"
        setattr(key, name, MethodType(wrapper(self), key))
