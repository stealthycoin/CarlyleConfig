import os
import sys
import subprocess
import pytest


@pytest.fixture
def run_fixture():
    def run(filename, args, env):
        path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
        p = subprocess.run(
            [sys.executable, path] + args,
            env=env,
            encoding="utf-8",
            capture_output=True,
        )
        return p

    return run
