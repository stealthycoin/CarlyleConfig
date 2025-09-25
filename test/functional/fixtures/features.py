import json

from carlyleconfig import deriveconfig, derive


@deriveconfig
class Config:
    constant: int = derive.field().from_constant(3)
    default_fn: list = derive.field().from_default_factory(list)


def main():
    config = Config()
    print(json.dumps(vars(config)))


if __name__ == "__main__":
    main()
