import argparse

from carlyleconfig import deriveconfig, derive
from carlyleconfig.plugins import ArgParsePlugin


@deriveconfig
class Config:
    # Derive the debug field from the following sources in order:
    # 1) an argparse argument named --debug.
    #    Defaults to None if not provided so we can fall through to
    #    the next case if not provided. Uses argparse's store_true
    #    action if it is provided so we get a bool value.
    # 2) the EXAMPLE_DEBUG environment variable. The string env var
    #    is cast to a bool. If not present None will be returned,
    #    falling through to the next case.
    # 3) a constant value of False, this will always provide a value
    #    and should be treated as the last fallback case.
    debug: bool = (
        derive.field()
        .from_argparse("--debug", action="store_true", default=None)
        .from_env_var("EXAMPLE_DEBUG", cast=bool)
        .from_constant(False)
    )


def main():
    parser = argparse.ArgumentParser()
    # Binding the parser to the ArgParsePlugin allows it to fill out
    # extra arguments, and intercept the parse_args() call.
    derive.get_plugin(ArgParsePlugin).bind_parser(parser)

    # Since we don't have any other arguments we don't need to save
    # the args. the ArgParsePlugin intercepts the call and gets a
    # copy of the parsed args to use when populating the Config
    # object.
    parser.parse_args()

    # Instantiating a Config object resolves the derive chains into
    # concrete values. Explicit overrides can be provided as well,
    # such as Config(debug=True).
    config = Config()
    print(f"DEBUG: {config.debug}")


if __name__ == "__main__":
    main()
