import json

import pytest


@pytest.mark.parametrize(
    "args,env,expected",
    [
        ([], {}, {"debug": False}),
        (["--debug"], {}, {"debug": True}),
        ([], {"TEST_CONFIG_DEBUG": "foo"}, {"debug": True}),
        ([], {"TEST_CONFIG_DEBUG": ""}, {"debug": False}),
        ([], {"TEST_CONFIG_DEBUG": "1"}, {"debug": True}),
        (["--debug"], {"TEST_CONFIG_DEBUG": "1"}, {"debug": True}),
        (["--debug"], {"TEST_CONFIG_DEBUG": ""}, {"debug": True}),
    ],
)
def test_config_program(run_fixture, args, env, expected):
    p = run_fixture("config.py", args, env)
    loaded = json.loads(p.stdout)
    assert loaded == expected


def test_key_program(run_fixture):
    p = run_fixture("key.py", [], {})
    loaded = p.stdout.strip().split("\n")
    assert loaded == [
        "['foo', 'baz']",
        "['foo', 'bar']",
        "['bar', 'baz']",
    ]


def test_features_program(run_fixture):
    p = run_fixture("features.py", [], {})
    loaded = json.loads(p.stdout)
    assert loaded == {
        "constant": 3,
        "default_fn": [],
    }
