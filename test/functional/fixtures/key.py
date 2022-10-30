import argparse

from carlyleconfig import deriveconfig, derive
from carlyleconfig.plugins import ArgParsePlugin


@deriveconfig
class Config:
    foo: bool = (
        derive.field()
        .from_argparse("--foo", action="store_true", default=None)
        .from_env_var("FOO", cast=bool)
    )
    bar: bool = derive.field().from_env_var("BAR", cast=bool).from_constant(False)
    baz: bool = (
        derive.field()
        .from_argparse("--baz", action="store_true", default=None)
        .from_constant(False)
    )


def main():
    parser = argparse.ArgumentParser()
    derive.get_plugin(ArgParsePlugin).bind_parser(parser)

    print(Config.keys(has_provider=["ArgParsePendingProvider"]))
    print(Config.keys(has_provider=["EnvVarProvider"]))
    print(Config.keys(has_provider=["ConstantProvider"]))


if __name__ == "__main__":
    main()
