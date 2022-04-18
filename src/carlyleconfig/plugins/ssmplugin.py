import logging
from dataclasses import dataclass, field
from typing import Any, ClassVar, Dict, List, Optional, Protocol, Callable
from types import MethodType

from carlyleconfig.plugins.base import BasePlugin
from carlyleconfig.key import ConfigKey

LOG = logging.getLogger(__name__)


class ParameterFetcher(Protocol):
    def get_parameters(self, Names: List[str], WithDecryption: bool) -> Dict[str, Any]:
        ...


@dataclass
class SSMProvider:
    name: str
    plugin: "SSMPlugin"
    cast: Optional[Callable[[str], Any]] = None

    def __post_init__(self):
        self.plugin.add_name(self.name)

    @property
    def description(self):
        return f"AWS SSM Parameter {self.plugin.prefix}{self.name}"

    def provide(self) -> Optional[str]:
        value = self.plugin.value_for_name(self.name)
        if value is not None and self.cast is not None:
            LOG.debug("Casting with %s", self.cast)
            value = self.cast(value)
        LOG.debug("Providing: %s", value)
        return value


def wrapper(plugin: "SSMPlugin"):
    def with_ssm_parameter(
        self, name: str, cast: Optional[Callable[[str], Any]] = None
    ) -> ConfigKey:
        self.providers.append(SSMProvider(name, plugin, cast=cast))
        return self

    return with_ssm_parameter


@dataclass
class SSMPlugin(BasePlugin):
    _MAX_SSM_NAMES: ClassVar[int] = 10
    prefix: str = ""
    client: Optional[ParameterFetcher] = None
    factory_name: ClassVar[str] = "ssm_parameter"
    names: List[str] = field(default_factory=lambda: [])
    cache: Optional[Dict[str, str]] = None

    @property
    def provider_name(self) -> str:
        return "SSMProvider"

    def set_client(self, client: ParameterFetcher) -> None:
        self.client = client

    def add_name(self, name: str) -> None:
        self.names.append(name)

    def fullname(self, name: str) -> str:
        return f"{self.prefix}{name}"

    def value_for_name(self, name: str) -> Optional[str]:
        if self.cache is None:
            self.cache = self._fetch()
        return self.cache.get(self.fullname(name))

    def _fetch(self) -> Dict[str, str]:
        if self.client is None:
            # The package does not depend on boto3, any application that
            # uses the config package to load ssm parameters itself should
            # require boto3.
            import boto3  # type: ignore

            self.client = boto3.client("ssm")  # type: ParameterFetcher
        values = {}
        for names in self._name_chunk(self.names, self._MAX_SSM_NAMES):
            result = self.client.get_parameters(
                Names=[self.fullname(name) for name in names],
                WithDecryption=True,
            )
            LOG.debug("Fetched: %s", result)
            values.update(
                {param["Name"]: param["Value"] for param in result["Parameters"]}
            )
        return values

    def _name_chunk(self, names: List[str], n: int):
        for i in range(0, len(names), n):
            yield names[i : i + n]

    def inject_factory_method(self, key: ConfigKey) -> ConfigKey:
        name = f"from_{self.factory_name}"
        setattr(key, name, MethodType(wrapper(self), key))
        return key
