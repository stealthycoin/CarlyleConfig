import logging

from dataclasses import dataclass, field
from typing import List, Any, Protocol, Optional


LOG = logging.getLogger(__name__)


class Provider(Protocol):
    def provide(self) -> Any:
        """Method to provide a value."""


@dataclass
class ConfigKey:
    """A class used as a placeholder in a Configuration object.

    Once the configuration object is instantiated all ConfigKey
    members will call their resolve method to fetch the actual
    value."""

    name: str = ""
    """What is this"""
    sensitive: bool = False
    providers: List[Provider] = field(default_factory=lambda: [])
    _cached: Optional[Any] = None
    _resolved: bool = False

    def resolve(self, only_providers: Optional[List[str]] = None) -> Any:
        """Resolves a ConfigKey to a value.

        A ConfigKey value is resolved by looping through all the
        providers and returning the first non-None value provided.

        One a key has been resolved once, that value is cached and
        the lookup is avoided the next time."""
        if self._resolved is True and only_providers is None:
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
