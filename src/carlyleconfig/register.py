import logging

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
                value = field.resolve()
            setattr(self, name, value)
            LOG.debug("Done initializing %s", name)
        LOG.debug("Done initializing carlyleconfig class %s", self.__class__.__name__)

    return init


def register(Cls):
    fields = {k: v for k, v in vars(Cls).items() if not k.startswith("__")}
    _attach_names(fields)
    _attach_init(Cls, fields)


def _attach_names(fields):
    for name, field in fields.items():
        field.name = name


def _attach_init(Cls, fields):
    setattr(Cls, "__init__", init_factory(fields))
