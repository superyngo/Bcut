import sys, os
from pathlib import Path
from typing import LiteralString
from enum import StrEnum, auto

# Get the parent directory of the current
runtime_pth = Path(os.path.abspath(sys.argv[0])).parent
