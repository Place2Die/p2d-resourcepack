#!/usr/bin/env python3
"""Entry point of the pack tooling: ./pack.py validate | build (see README)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "tools"))

from p2dpack.cli import main  # noqa: E402

sys.exit(main())
