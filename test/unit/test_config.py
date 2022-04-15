from carlyleconfig import deriveconfig
from carlyleconfig.environment import ConfigEnvironment


def test_repr():
    derive = ConfigEnvironment()

    @deriveconfig
    class Config:
        foo: str = derive.field().from_constant("foo")
        bar: str = derive.field().from_constant("bar")

    config = Config()
    value = str(config)
    assert value == "{'bar': 'bar', 'foo': 'foo'}"


def test_sensitive_field():
    derive = ConfigEnvironment()

    @deriveconfig
    class Config:
        secret: str = derive.field(sensitive=True).from_constant("secret")

    config = Config()
    value = str(config)
    assert value == "{'secret': '*****'}"
