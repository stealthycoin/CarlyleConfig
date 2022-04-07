from typing import AnyStr


class OSUtils:
    def read_file(self, path: str, binary=False) -> AnyStr:
        mode = "r"
        if binary:
            mode += "b"
        with open(path, mode=mode) as f:
            return f.read()
