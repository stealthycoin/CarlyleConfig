import os
import logging
from dataclasses import dataclass, field
from typing import Any, ClassVar, Dict, Callable, Optional
from types import MethodType

from carlyleconfig.plugins.base import BasePlugin
from carlyleconfig.key import ConfigKey


LOG = logging.getLogger(__name__)


@dataclass
class EnvVarProvider:
    value: Any
    cast: Optional[Callable[[str], Any]] = None
    environ: Dict[str, str] = field(default_factory=lambda: os.environ.copy())

    @property
    def description(self):
        return f"environment variable {self.value}"

    def provide(self) -> Any:
        LOG.debug("Fetching env var %s", self.value)
        value = self.environ.get(self.value)
        LOG.debug("Got value: %s", value)
        if value is not None and self.cast is not None:
            LOG.debug("Casting with %s", self.cast)
            value = self.cast(value)
        LOG.debug("Providing: %s", value)
        return value


def with_env_var(
    self, name: str, cast: Optional[Callable[[str], Any]] = None
) -> ConfigKey:
    provider = EnvVarProvider(name, cast=cast)
    self.providers.append(provider)
    return self


@dataclass
class EnvVarPlugin(BasePlugin):
    factory_name: ClassVar[str] = "env_var"

    @property
    def provider_name(self) -> str:
        return "EnvVarProvider"

    def inject_factory_method(self, key: ConfigKey) -> ConfigKey:
        name = f"from_{self.factory_name}"
        setattr(key, name, MethodType(with_env_var, key))
        return key
