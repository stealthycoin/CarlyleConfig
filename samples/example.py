import argparse

from carlyleconfig import deriveconfig, derive
from carlyleconfig.plugins import ArgParsePlugin


PARSER_PLUGIN = ArgParsePlugin()
derive.plugins = [PARSER_PLUGIN]


@deriveconfig
class Config:
    name: str = (
        derive.field()
        .from_argparse("--name", help="Name parm.")
        .from_env_var("TEST_ENV")
        .from_constant("default")
    )
    debug: bool = (
        derive.field()
        .from_argparse("--debug", action="store_true", default=None)
        .from_env_var("EXAMPLE_DEBUG", cast=bool)
        .from_constant(False)
    )


def main():
    parser = argparse.ArgumentParser()
    PARSER_PLUGIN.bind_parser(parser)

    parser.add_argument("--after-arg")
    parser.parse_args()
    config = Config()
    print(config.debug, config.name)


if __name__ == "__main__":
    main()
