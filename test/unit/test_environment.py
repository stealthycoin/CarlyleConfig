from carlyleconfig.environment import ConfigEnvironment
from carlyleconfig.plugins import ArgParsePlugin


class FakeParser:
    def parse_args(*args):
        pass


def test_default_environment():
    env = ConfigEnvironment()
    field = env.field()
    assert hasattr(field, "from_constant")
    assert hasattr(field, "from_env_var")


def test_add_plugin():
    parser = FakeParser()
    env = ConfigEnvironment(
        plugins=[
            ArgParsePlugin(parser),
        ]
    )
    field = env.field()
    assert hasattr(field, "from_constant")
    assert hasattr(field, "from_env_var")
    assert hasattr(field, "from_argparse")
