#!/usr/bin/env python3
"""Backward-compatible runner for readablepdf."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from readablepdf.pipeline import main


if __name__ == "__main__":
    raise SystemExit(main())
