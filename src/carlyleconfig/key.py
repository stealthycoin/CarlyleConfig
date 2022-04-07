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
    providers: List[Provider] = field(default_factory=lambda: [])
    _cached: Optional[Any] = None
    _resolved: bool = False

    def resolve(self) -> Any:
        if self._resolved is True:
            return self._cached
        LOG.debug("Resolving ConfigKey value for %s", self.name)
        for provider in self.providers:
            LOG.debug("Trying provider %s", provider.__class__.__name__)
            value = provider.provide()
            if value is not None:
                LOG.debug("%s resolved to %s", self.name, value)
                self._cached = value
                break
        self._resolved = True
        return self._cached
