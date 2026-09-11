#!/usr/bin/env python3
"""Build examples/sample.html — a showcase deck exercising every layout.

This renders the layout showcase (assets/demo_content.py) with edit mode on, so
the committed sample doubles as (a) a visual reference of all 17 layouts and the
H1/H2/H3 Horizon themes, and (b) a live demo of Edit mode (press E).

    python3 examples/build_sample.py    # writes examples/sample.html

New decks: don't copy this — write your own content list and call build()
(see ../SKILL.md).
"""
import os, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"
sys.path.insert(0, str(ASSETS))

from build_deck import build          # noqa: E402
from demo_content import SLIDES       # noqa: E402

if __name__ == "__main__":
    build(SLIDES,
          title="ProFinda Deck Engine — Layout Showcase",
          out=str(HERE / "sample.html"),
          edit=True)
