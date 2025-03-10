import argparse

from carlyleconfig import deriveconfig, derive
from carlyleconfig.plugins import ArgParsePlugin


# Load the ArgParsePlugin and attach it to the default derive object.
# this gives us access to the derive.field().with_argparse(...) method.
# The with_constant, with_file, and with_env_var methods are plugins
# that are loaded by default since they require no extra steps.


@deriveconfig
class Config:
    # Derive the filepath field from the first non-None source below:
    # 1) The command line argument --config-path. If not provided it
    # will be None falling through to the next case.
    # 2) The environment variable EXAMPLE_CONFIG_PATH if present.
    # 3) Constant value of ~/.default-config.json
    filepath: str = (
        derive.field()
        .from_argparse("--config-path", default=None)
        .from_env_var("EXAMPLE_CONFIG_PATH")
        .from_constant("~/.default-config.json")
    )

    # Derive the debug field from the following sources in order:
    # 1) an argparse argument named --debug.
    #    Defaults to None if not provided so we can fall through to
    #    the next case if not provided. Uses argparse's store_true
    #    action if it is provided so we get a bool value.
    # 2) the EXAMPLE_DEBUG environment variable. The string env var
    #    is cast to a bool. If not present None will be returned,
    #    falling through to the next case.
    # 3) A file named filepath. filepath is a reference to the prior
    #    config key in this class. Since it is loaded first we can
    #    uses a reference to it here as if it were a concrete value.
    #    Once the file is loaded it will use the json.loads function
    #    to parse the file. And the selector function
    #    lambda x: x.get("DEBUG") to select out the value from the
    #    file.
    # 4) a constant value of False, this will always provide a value
    #    and should be treated as the last fallback case.
    debug: bool = (
        derive.field()
        .from_argparse("--debug", action="store_true", default=None)
        .from_env_var("EXAMPLE_DEBUG", cast=bool)
        .from_json_file(filepath, jmespath="DEBUG")
        .from_constant(False)
    )

    # Grab the full contents of the config file without any parsing
    # by using the from_file method without any parser/selector.
    # Provide a default of empty string in case the file doesn't exist.
    raw_config_file: str = derive.field().from_file(filepath).from_constant("")


def main():
    parser = argparse.ArgumentParser()
    # Binding the parser to the ArgParsePlugin allows it to fill out
    # extra arguments, and intercept the parse_args() call.
    derive.get_plugin(ArgParsePlugin).bind_parser(parser)

    # Since we don't have any other arguments we don't need to save
    # the args. the ArgParsePlugin intercepts the call and gets a
    # copy of the parsed args to use when populating the Config object.
    parser.parse_args()

    # Instantiating a Config object resolves the derive chains into
    # concrete values. Explicit overrides can be provided as well,
    # such as Config(debug=True).
    config = Config()
    print(f"DEBUG: {config.debug}")
    print(f'config file contents: "{config.raw_config_file}"')


if __name__ == "__main__":
    main()
