import logging

from dataclasses import dataclass, field
from typing import List, Any, Protocol, Optional


LOG = logging.getLogger(__name__)


class Provider(Protocol):
    def provide(self) -> Any:
        """Method to provide a value."""


@dataclass
class ConfigKey:
    name: str = ""
    sensitive: bool = False
    providers: List[Provider] = field(default_factory=lambda: [])
    _cached: Optional[Any] = None
    _resolved: bool = False

    def resolve(self, only_providers: List[str] = None) -> Any:
        if self._resolved is True and not only_providers:
            return self._cached
        LOG.debug("Resolving ConfigKey value for %s", self.name)
        for provider in self.providers:
            if only_providers:
                if provider.__class__.__name__ not in only_providers:
                    LOG.debug(
                        "Skipping %s not in %s",
                        provider.__class__.__name__,
                        only_providers,
                    )
                    continue
            LOG.debug("Trying provider %s", provider.__class__.__name__)
            value = provider.provide()
            if value is not None:
                LOG.debug("%s resolved to %s", self.name, value)
                if only_providers:
                    return value
                self._cached = value
                break
        self._resolved = True
        return self._cached
