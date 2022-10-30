import json
import logging
from dataclasses import dataclass, field
from typing import Any, ClassVar, Dict, List, Optional, Protocol, Callable
from types import MethodType

from carlyleconfig.plugins.base import BasePlugin
from carlyleconfig.key import ConfigKey

LOG = logging.getLogger(__name__)


class SecretFetcher(Protocol):
    exceptions: Any

    def get_secret_value(self, SecretId: str) -> Dict[str, Any]:
        ...


@dataclass
class SecretsManagerProvider:
    name: str
    key: Optional[str]
    plugin: "SecretsManagerPlugin"
    cast: Optional[Callable[[str], Any]] = None
    require_key: bool = False

    @property
    def description(self):
        return f"AWS Secrets Manager"

    def provide(self) -> Optional[str]:
        value = self.plugin.get_secret(self.name)
        value = self._extract_from_json(value)
        value = self._cast(value)
        LOG.debug("Providing: %s", value)
        return value

    def _extract_from_json(self, value: Optional[str]) -> Optional[str]:
        if value is not None and self.key is not None:
            json_value = json.loads(value)
            if self.key not in json_value:
                LOG.debug("Secret %s did not have key %s", self.name, self.key)
                if self.require_key:
                    raise RuntimeError(
                        f"Key '{self.key}' was missing from secret '{self.name}'."
                    )
                return None

            value = json_value[self.key]
        return value

    def _cast(self, value: Any) -> Any:
        if value is not None and self.cast is not None:
            LOG.debug("Casting with %s", self.cast)
            value = self.cast(value)
        return value


def wrapper(plugin: "SecretsManagerPlugin"):
    def with_secrets_manager(
        self,
        name: str,
        key: Optional[str] = None,
        cast: Optional[Callable[[str], Any]] = None,
        require_key: bool = False,
    ) -> ConfigKey:
        self.providers.append(
            SecretsManagerProvider(
                name, key, plugin, cast=cast, require_key=require_key
            )
        )
        return self

    return with_secrets_manager


@dataclass
class SecretsManagerPlugin(BasePlugin):

    client: Optional[SecretFetcher] = None
    factory_name: ClassVar[str] = "secrets_manager"

    @property
    def provider_name(self) -> str:
        return "SecretsManagerProvider"

    def get_secret(self, name: str) -> Optional[str]:
        return self._fetch(name)

    def _fetch(self, name: str) -> Optional[str]:
        if self.client is None:
            # The package does not depend on boto3, any application that
            # uses the config package to load secrets itself should
            # require boto3.
            import boto3  # type: ignore

            self.client = boto3.client("secretsmanager")  # type: SecretFetcher
        try:
            result = self.client.get_secret_value(
                SecretId=name,
            )
            if "SecretString" in result:
                secret = result["SecretString"]
                return secret
            return None
        except self.client.exceptions.ResourceNotFoundException:
            LOG.debug("Could not find secret %s", name)
            return None

    def inject_factory_method(self, key: ConfigKey) -> ConfigKey:
        name = f"from_{self.factory_name}"
        setattr(key, name, MethodType(wrapper(self), key))
        return key
