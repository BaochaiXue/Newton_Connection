#!/usr/bin/env python3
"""Reorder PhysTwin calibrate.pkl camera extrinsics for selected cases."""

from __future__ import annotations

import argparse
import pickle
from pathlib import Path

import numpy as np


DEFAULT_BASE_PATH = Path("PhysTwin/data/different_types")
DEFAULT_ORDER = "0,2,1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Rewrite calibrate.pkl for selected PhysTwin cases by applying a camera-order permutation."
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
        help="Case name to update. Repeat for multiple cases.",
    )
    parser.add_argument(
        "--order",
        default=DEFAULT_ORDER,
        help=f"Comma-separated new order over camera indices (default: {DEFAULT_ORDER}).",
    )
    return parser.parse_args()


def parse_order(order_text: str) -> tuple[int, ...]:
    order = tuple(int(part.strip()) for part in order_text.split(","))
    if sorted(order) != list(range(len(order))):
        raise ValueError(f"Order must be a permutation starting at 0: {order_text}")
    return order


def main() -> int:
    args = parse_args()
    base_path = args.base_path.resolve()
    order = parse_order(args.order)

    for case_name in args.case:
        case_dir = base_path / case_name
        calibrate_path = case_dir / "calibrate.pkl"
        if not calibrate_path.is_file():
            raise FileNotFoundError(f"Missing calibrate.pkl: {calibrate_path}")

        with calibrate_path.open("rb") as f:
            calibrate = pickle.load(f)

        calibrate_arr = np.asarray(calibrate)
        if calibrate_arr.ndim != 3 or calibrate_arr.shape[1:] != (4, 4):
            raise ValueError(
                f"Unexpected calibrate.pkl shape for {case_name}: {calibrate_arr.shape}"
            )
        if len(order) != calibrate_arr.shape[0]:
            raise ValueError(
                f"Permutation length {len(order)} does not match number of cameras "
                f"{calibrate_arr.shape[0]} for {case_name}"
            )

        reordered = [calibrate[idx] for idx in order]
        with calibrate_path.open("wb") as f:
            pickle.dump(reordered, f)

        print(f"[fixed] {case_name}: order {order}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
