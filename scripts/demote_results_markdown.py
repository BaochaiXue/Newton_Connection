#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results"


def _tracked_paths() -> set[str]:
    try:
        out = subprocess.run(
            ["git", "ls-files", "results"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
    except Exception:
        return set()
    return {line.strip() for line in out if line.strip()}


def _preserve_markdown(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if rel == Path("results/README.md"):
        return True
    parts = rel.parts
    return len(parts) == 3 and parts[0] == "results" and parts[2] == "README.md"


def _demotion_pairs() -> list[tuple[Path, Path]]:
    pairs: list[tuple[Path, Path]] = []
    for path in sorted(RESULTS_DIR.rglob("*.md")):
        if _preserve_markdown(path):
            continue
        target = path.with_suffix(".txt")
        pairs.append((path, target))
    return pairs


def main() -> int:
    parser = argparse.ArgumentParser(description="Demote deep local Markdown under results/ to .txt.")
    parser.add_argument("--dry-run", action="store_true", help="Show planned renames without mutating files.")
    args = parser.parse_args()

    tracked = _tracked_paths()
    pairs = _demotion_pairs()
    if not pairs:
        print("No deep results Markdown files need demotion.")
        return 0

    renamed = 0
    for src, dst in pairs:
        if dst.exists():
            raise SystemExit(f"Refusing to overwrite existing file: {dst}")

        src_rel = src.relative_to(ROOT).as_posix()
        dst_rel = dst.relative_to(ROOT).as_posix()
        print(f"{src_rel} -> {dst_rel}")
        if args.dry_run:
            continue

        if src_rel in tracked:
            subprocess.run(["git", "mv", src_rel, dst_rel], cwd=ROOT, check=True)
        else:
            src.rename(dst)
        renamed += 1

    if args.dry_run:
        print(f"Planned {len(pairs)} demotions.")
    else:
        print(f"Demoted {renamed} deep results Markdown files to .txt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
