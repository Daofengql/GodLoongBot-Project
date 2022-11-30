import os
import json
from pathlib import Path


class bot(object):
    def __init__(self):
        with (Path().resolve() / "library" / "weijinci.txt").open(
            "r",
            encoding="utf-8",
            errors="ignore",
        ) as f:
            self.weijingci = json.loads(f.read())