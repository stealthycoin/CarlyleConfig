import os
from dataclasses import dataclass, field
from typing import Any, ClassVar, Dict, Callable, Optional
from types import MethodType

from carlyleconfig.plugins.base import BasePlugin
from carlyleconfig.key import ConfigKey


@dataclass
class EnvVarProvider:
    value: Any
    cast: Optional[Callable[[str], Any]] = None
    environ: Dict[str, str] = field(default_factory=lambda: os.environ.copy())

    def provide(self) -> Any:
        value = self.environ.get(self.value)
        if value is not None and self.cast is not None:
            value = self.cast(value)
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

    def inject_factory_method(self, key: ConfigKey) -> ConfigKey:
        name = f"from_{self.factory_name}"
        setattr(key, name, MethodType(with_env_var, key))
        return key
