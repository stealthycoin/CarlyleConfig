def init_factory(fields):
    def init(self, **kwargs):
        for name, field in fields.items():
            if name in kwargs:
                value = kwargs[name]
            else:
                value = field.resolve()
            setattr(self, name, value)

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
