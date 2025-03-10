import os
import json
import logging
from typing import Any, ClassVar, Union, Dict, Callable, Tuple, TypeVar

from dataclasses import dataclass, field
from types import MethodType

import jmespath as jp  # type: ignore

from carlyleconfig.plugins.base import BasePlugin
from carlyleconfig.key import ConfigKey
from carlyleconfig.utils import OSUtils

LOG = logging.getLogger(__name__)

T = TypeVar("T")
U = TypeVar("U")

ParserType = Callable[[str | bytes], T]
SelectorType = Callable[[T], U]


def identity(x: Any) -> Any:
    return x


@dataclass
class FileProvider:
    plugin: "FilePlugin"
    filename: Union[str, ConfigKey]
    parser: ParserType[str] = identity
    selector: SelectorType[str, Any] = identity

    @property
    def description(self) -> str:
        return f"file {self.filename}"

    def provide(self) -> Any:
        path = self.filename
        if isinstance(self.filename, ConfigKey):
            path = self.filename.resolve()
        path = os.path.abspath(os.path.expanduser(str(path)))
        LOG.debug("Fetching file %s", path)
        content = self.plugin.read_file(path, self.parser)
        LOG.debug("Parsed type: %s content:\n%s", type(content), content)
        if content is None:
            return None
        selected = self.selector(content)
        LOG.debug("Providing: %s", selected)
        return selected


def wrapper(
    plugin: "FilePlugin",
) -> Callable[[ConfigKey, str, ParserType[str], SelectorType[str, Any]], ConfigKey]:
    def with_file(
        self: ConfigKey,
        filename: str,
        parser: ParserType[str] = identity,
        selector: SelectorType[str, Any] = identity,
    ) -> ConfigKey:
        self.providers.append(FileProvider(plugin, filename, parser, selector))
        return self

    return with_file


def json_wrapper(plugin: "FilePlugin") -> Callable[[ConfigKey, str, str], ConfigKey]:
    def with_json_file(self: ConfigKey, filename: str, jmespath: str) -> ConfigKey:
        parser = json.loads
        selector = jp.compile(jmespath).search
        self.providers.append(FileProvider(plugin, filename, parser, selector))
        return self

    return with_json_file


@dataclass
class FilePlugin(BasePlugin):
    factory_name: ClassVar[str] = "file"
    _cache: Dict[Tuple[str, ParserType[str]], Any] = field(default_factory=lambda: {})
    osutils: OSUtils = field(default_factory=lambda: OSUtils())

    @property
    def provider_name(self) -> str:
        return "FileProvider"

    def read_file(self, path: str, parser: ParserType[str]) -> Any:
        if (path, parser) not in self._cache:
            LOG.debug("%s not in cache, trying to load", (path, parser))
            try:
                content = self.osutils.read_file(path)
            except FileNotFoundError:
                LOG.debug("%s does not exist", path)
                content = None
            if content is not None:
                LOG.debug("%s found, loading content:\n%s", path, content)
                LOG.debug("Parsing with %s", parser)
                content = parser(content)
            self._cache[(path, parser)] = content
        return self._cache[(path, parser)]

    def inject_factory_method(self, key: ConfigKey) -> None:
        name = f"from_{self.factory_name}"
        setattr(key, name, MethodType(wrapper(self), key))
        setattr(key, "from_json_file", MethodType(json_wrapper(self), key))
