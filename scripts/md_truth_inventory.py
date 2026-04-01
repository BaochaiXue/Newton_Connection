#!/usr/bin/env python3
from __future__ import annotations

"""Compatibility shim for markdown truth inventory helpers.

The generator and the lint must share one inventory scope. Keep this module as a
thin re-export layer so older imports do not fork the control-plane scan logic.
"""

from md_truth_inventory_lib import ROOT, active_task_slugs, build_inventory_paths

__all__ = ["ROOT", "active_task_slugs", "build_inventory_paths"]
