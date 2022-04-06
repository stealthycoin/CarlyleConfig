import os
import sys
import subprocess
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
def test_config_program(args, env, expected):
    path = os.path.join(os.path.dirname(__file__), "config.py")
    p = subprocess.run(
        [sys.executable, path] + args,
        env=env,
        encoding="utf-8",
        capture_output=True,
    )
    loaded = json.loads(p.stdout)
    assert loaded == expected
