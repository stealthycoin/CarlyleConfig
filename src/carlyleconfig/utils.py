from typing import cast


class OSUtils:
    def read_file(self, path: str, binary: bool = False) -> str | bytes:
        mode = "r" if not binary else "rb"
        with open(path, mode=mode) as f:
            return cast(str | bytes, f.read())
