# CarlyleConfig
Small Hierarchical Configuration loader

[![PyPI version](https://badge.fury.io/py/carlyleconfig.svg)](https://badge.fury.io/py/carlyleconfig)

# Example Usage

```python
import argparse

from carlyleconfig import deriveconfig, derive
from carlyleconfig.plugins import ArgParsePlugin


# Load the ArgParsePlugin and attach it to the default derive object.
# this gives us access to the derive.field().with_argparse(...) method.
# The with_constant and with_env_var methods are plugins that are loaded
# by default since they are so simple.
PARSER_PLUGIN = ArgParsePlugin()
derive.plugins = [PARSER_PLUGIN]



@deriveconfig
class Config:
    # Derive the debug field from the following sources in order:
    # 1) an argparse argument named --debug. 
    #    Defaults to None if not provided so we can fall through to the next case
    #    if not provided. Uses argparse's store_true action if it is provided so we get a bool value.
    # 2) the EXAMPLE_DEBUG environment variable. The string env var is cast to a bool.
    #    If not present None will be returned, falling through to the next case.
    # 3) a constant value of False, this will always provide a value and should be treated
    #    as the last fallback case. 
    debug: bool = (
        derive.field()
        .from_argparse("--debug", action="store_true", default=None)
        .from_env_var("EXAMPLE_DEBUG", cast=bool)
        .from_constant(False)
    )


def main():
    parser = argparse.ArgumentParser()
    # Binding the parser to the ArgParsePlugin allows it to fill out extra
    # arguments, and intercept the parse_args() call. 
    PARSER_PLUGIN.bind_parser(parser)

    # Since we don't have any other arguments we don't need to save the args.
    # the ArgParsePlugin intercepts the call and gets a copy of the parsed args
    # to use when populating the Config object.
    parser.parse_args()
    
    # Instantiating a Config object resolves the derive chains into concrete values.
    # Explicit overrides can be provided as well, such as Config(debug=True).
    config = Config()
    print(f'DEBUG: {config.debug}')


if __name__ == "__main__":
    main()

```

```bash
$ python example.py
DEBUG: False
$ EXAMPLE_DEBUG=1 python samples/example.py
DEBUG: True
$ python samples/example.py --debug
DEBUG: True
```
