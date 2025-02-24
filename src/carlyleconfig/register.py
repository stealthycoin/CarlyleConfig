import logging
import pprint
from typing import Dict, Any, Type, List, Optional, Callable

LOG = logging.getLogger(__name__)


def init_factory(fields: Dict[str, Any]) -> Callable[[Any], None]:
    def init(self: Any, **kwargs: Any) -> None:
        LOG.debug("Initializing carlyleconfig class %s", self.__class__.__name__)
        for name, field in fields.items():
            LOG.debug("Initializing field: %s", name)
            if name in kwargs:
                LOG.debug("Explicit value provided: %s", kwargs[name])
                value = kwargs[name]
            else:
                value = field.resolve(kwargs.get("__only_providers", []))
            setattr(self, name, value)
            LOG.debug("Done initializing %s", name)
        LOG.debug("Done initializing carlyleconfig class %s", self.__class__.__name__)

    return init


def register(Cls: Type[Any]) -> None:
    fields = {k: v for k, v in vars(Cls).items() if not k.startswith("__")}
    _attach_names(fields)
    _attach_init(Cls, fields)
    _attach_constructors(Cls)
    _attach_key_filter(Cls, fields)
    _attach_repr(Cls, fields)


def _attach_names(fields: Dict[str, Any]) -> None:
    for name, field in fields.items():
        field.name = name


def _attach_init(Cls: Type[Any], fields: Dict[str, Any]) -> None:
    setattr(Cls, "__init__", init_factory(fields))


def constructor_factory() -> Callable[[Type[Any], Optional[List[str]]], Any]:
    def load(cls: Type[Any], only_providers: Optional[List[str]] = None) -> Any:
        return cls(__only_providers=only_providers)

    return load


def _attach_constructors(Cls: Type[Any]) -> None:
    setattr(Cls, "load", classmethod(constructor_factory()))


def _attach_key_filter(Cls: Type[Any], fields: Dict[str, Any]) -> None:
    def filterfn(cls: Type[Any], has_provider: Optional[List[str]] = None) -> List[str]:
        if has_provider is None:
            has_provider = []
        keys = []
        for name, field in fields.items():
            for provider in field.providers:
                if provider.__class__.__name__ in has_provider:
                    keys.append(name)
        return keys

    setattr(Cls, "keys", classmethod(filterfn))


def _repr_factory(fields: Dict[str, Any]) -> Callable[[Any], str]:
    def __repr__(self: Any) -> str:
        return pprint.pformat(
            {
                name: getattr(self, name) if not field.sensitive else "*****"
                for name, field in fields.items()
            },
            indent=4,
        )

    return __repr__


def _attach_repr(Cls: Type[Any], fields: Dict[str, Any]) -> None:
    setattr(Cls, "__repr__", _repr_factory(fields))
