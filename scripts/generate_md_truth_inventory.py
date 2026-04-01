#!/usr/bin/env python3
from __future__ import annotations

"""Compatibility alias for the markdown inventory generator.

Use `python scripts/generate_md_inventory.py` as the public entrypoint.
Keep this file only so older notes or scripts do not fork the inventory story.
"""

from generate_md_inventory import main


if __name__ == "__main__":
    raise SystemExit(main())
