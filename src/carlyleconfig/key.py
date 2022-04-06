from dataclasses import dataclass, field
from typing import List, Any, Protocol


class Provider(Protocol):
    def provide(self) -> Any:
        """Method to provide a value."""


@dataclass
class ConfigKey:
    name: str = field(init=False)
    providers: List[Provider] = field(default_factory=lambda: [])

    def resolve(self) -> Any:
        for provider in self.providers:
            value = provider.provide()
            if value is not None:
                return value
        return None
