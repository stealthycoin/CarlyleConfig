import argparse
import json

from carlyleconfig import deriveconfig, derive
from carlyleconfig.plugins import ArgParsePlugin


parser_plugin = ArgParsePlugin()
derive.plugins = [parser_plugin]


@deriveconfig
class Config:
    debug: bool = (
        derive.field()
        .from_argparse("--debug", action="store_true", default=None)
        .from_env_var("TEST_CONFIG_DEBUG", cast=bool)
        .from_constant(False)
    )


def main():
    parser = argparse.ArgumentParser()
    parser_plugin.bind_parser(parser)
    parser.parse_args()
    config = Config()
    print(json.dumps(vars(config)))


if __name__ == "__main__":
    main()
