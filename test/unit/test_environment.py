from carlyleconfig.environment import ConfigEnvironment
from carlyleconfig.plugins import ArgParsePlugin


class FakeParser:
    def parse_args(*args):
        pass


def test_default_environment():
    env = ConfigEnvironment()
    field = env.field()
    from_methods = {f for f in dir(field) if "from_" in f}
    assert from_methods == {
        "from_constant",
        "from_env_var",
        "from_argparse",
        "from_file",
        "from_json_file",
        "from_default_factory",
    }


def test_add_plugin():
    FakeParser()
    env = ConfigEnvironment(plugins={})
    env.add_plugin(ArgParsePlugin())
    field = env.field()
    print(dir(field))
    assert hasattr(field, "from_argparse")
    assert not hasattr(field, "from_constant")
