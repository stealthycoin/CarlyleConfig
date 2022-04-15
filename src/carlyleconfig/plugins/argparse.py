import argparse
import logging
from typing import Any, ClassVar, Optional, List
from types import MethodType

from dataclasses import dataclass, field
from carlyleconfig.plugins.base import BasePlugin
from carlyleconfig.key import ConfigKey, Provider


LOG = logging.getLogger(__name__)


@dataclass
class ArgParseProvider(Provider):
    name: str
    plugin: "ArgParsePlugin"

    def provide(self) -> Any:
        return getattr(self.plugin.args, self.name)


class ArgParsePendingProvider(Provider):
    _RESERVED_KWARGS = ("update_help",)

    def __init__(self, plugin: "ArgParsePlugin", name: str, key: ConfigKey, **kwargs):
        self.plugin = plugin
        self.name = name
        self.key = key
        self.provider: Optional[ArgParseProvider] = None
        self.kwargs = kwargs

    @property
    def description(self):
        return f"argparse argument {self.name}"

    def provide(self) -> Any:
        if self.provider is None:
            return None
        value = self.provider.provide()
        LOG.debug("Providing: %s", value)
        return value

    def upgrade(self, parser: argparse.ArgumentParser):
        args = {k: v for k, v in self.kwargs.items() if k not in self._RESERVED_KWARGS}
        if self._should_update_help():
            self._append_help(args)
        dest = install_arg(parser, self.name, **args)
        self.provider = ArgParseProvider(dest, self.plugin)

    def _should_update_help(self):
        if self.kwargs.get("update_help") is not None:
            return self.kwargs.get("update_help")
        return self.plugin.update_help

    def _append_help(self, args):
        extra_help = self._generate_extra_help()
        if "help" not in args:
            args["help"] = ""
        args["help"] += f"{extra_help}"

    def _generate_extra_help(self):
        if self not in self.key.providers:
            # This is the case where this provider is not in it's
            # owning key's provider list. This should only be possible
            # in test scenarios.
            return ""
        providers = self.key.providers[self.key.providers.index(self) + 1 :]
        value = ", ".join(p.description for p in providers)
        return value


def install_arg(parser: argparse.ArgumentParser, *args, **kwargs):
    LOG.debug("Installing arguments in parser %s, kwargs: %s", args, kwargs)
    argument = parser.add_argument(*args, **kwargs)
    return argument.dest


def wrapper(plugin: "ArgParsePlugin"):
    def with_argparse(self, name, **kwargs) -> ConfigKey:
        provider = ArgParsePendingProvider(plugin, name, self, **kwargs)
        plugin.install_provider(provider)
        self.providers.append(provider)
        return self

    return with_argparse


@dataclass
class ArgParsePlugin(BasePlugin):
    factory_name: ClassVar[str] = "argparse"
    parser: Optional[argparse.ArgumentParser] = None
    update_help: bool = False
    args: Optional[argparse.Namespace] = None
    on_bind: List[ArgParsePendingProvider] = field(default_factory=lambda: [])

    @property
    def provider_name(self) -> str:
        return "ArgParsePendingProvider"

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
