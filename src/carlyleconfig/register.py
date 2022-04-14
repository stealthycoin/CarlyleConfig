import logging
import pprint

LOG = logging.getLogger(__name__)


def init_factory(fields):
    def init(self, **kwargs):
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


def register(Cls):
    fields = {k: v for k, v in vars(Cls).items() if not k.startswith("__")}
    _attach_names(fields)
    _attach_init(Cls, fields)
    _attach_constructors(Cls)
    _attach_key_filter(Cls, fields)
    _attach_repr(Cls, fields)


def _attach_names(fields):
    for name, field in fields.items():
        field.name = name


def _attach_init(Cls, fields):
    setattr(Cls, "__init__", init_factory(fields))


def constructor_factory():
    @classmethod
    def load(cls, only_providers=None):
        return cls(__only_providers=only_providers)

    return load


def _attach_constructors(Cls):
    setattr(Cls, "load", constructor_factory())


def filter_factory(fields):
    @classmethod
    def filterfn(cls, has_provider=None):
        if has_provider is None:
            has_provider = []
        keys = []
        for name, field in fields.items():
            for provider in field.providers:
                if provider.__class__.__name__ in has_provider:
                    keys.append(name)
        return keys

    return filterfn


def _attach_key_filter(Cls, fields):
    setattr(Cls, "keys", filter_factory(fields))


def _repr_factory(fields):
    def __repr__(self):
        return pprint.pformat(
            {
                name: getattr(self, name) if not field.sensitive else "*****"
                for name, field in fields.items()
            },
            indent=4,
        )

    return __repr__


def _attach_repr(Cls, fields):
    setattr(Cls, "__repr__", _repr_factory(fields))
