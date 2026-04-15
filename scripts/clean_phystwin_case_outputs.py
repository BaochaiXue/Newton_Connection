#!/usr/bin/env python3
"""Remove generated PhysTwin process_data outputs for selected raw-capture cases."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


DEFAULT_BASE_PATH = Path("PhysTwin/data/different_types")
GENERATED_PATHS = (
    "mask",
    "cotracker",
    "pcd",
    "pcd_debug",
    "tmp_data",
    "temp_mask",
    "final_data.pkl",
    "final_data.mp4",
    "final_pcd.mp4",
    "split.json",
    "track_process_data.pkl",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Delete generated PhysTwin outputs under case folders while preserving raw inputs."
        )
    )
    parser.add_argument(
        "--base-path",
        type=Path,
        default=DEFAULT_BASE_PATH,
        help=f"Case root directory (default: {DEFAULT_BASE_PATH}).",
    )
    parser.add_argument(
        "--case",
        action="append",
        required=True,
        help="Case name to clean. Repeat for multiple cases.",
    )
    return parser.parse_args()


def remove_path(path: Path) -> None:
    if not path.exists():
        return
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


def main() -> int:
    args = parse_args()
    base_path = args.base_path.resolve()

    for case_name in args.case:
        case_dir = base_path / case_name
        if not case_dir.is_dir():
            raise FileNotFoundError(f"Missing case directory: {case_dir}")
        print(f"[clean] {case_name}")
        for relative in GENERATED_PATHS:
            target = case_dir / relative
            if target.exists():
                print(f"  remove {target}")
                remove_path(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
