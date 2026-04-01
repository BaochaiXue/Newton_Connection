#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_TASKS_README = ROOT / "docs/bridge/tasks/README.md"
TASK_PAGE_DIR = ROOT / "docs/bridge/tasks"
SPEC_DIR = ROOT / "tasks/spec"
PLAN_DIR = ROOT / "plans/active"
IMPLEMENT_DIR = ROOT / "tasks/implement"
STATUS_DIR = ROOT / "tasks/status"
RESULTS_META_DIR = ROOT / "results_meta"
REGISTRY_TASKS_DIR = RESULTS_META_DIR / "tasks"
DEPRECATIONS_DOC = ROOT / "docs/generated/harness_deprecations.md"

ABSOLUTE_PATH_RE = re.compile(r"(^|[^A-Za-z])(/home/[^\\s`'\"<>()]+)")
TASK_LINK_RE = re.compile(r"\[([^\]]+\.md)\]\(\./([^)]+\.md)\)")


def _active_task_slugs() -> list[str]:
    text = ACTIVE_TASKS_README.read_text(encoding="utf-8").splitlines()
    active: list[str] = []
    in_active = False
    for raw in text:
        line = raw.strip()
        if line == "## Active Task Set":
            in_active = True
            continue
        if in_active and line.startswith("Task template"):
            break
        if not in_active:
            continue
        match = TASK_LINK_RE.search(line)
        if not match:
            continue
        slug = Path(match.group(2)).stem
        if slug.startswith("_"):
            continue
        active.append(slug)
    return active


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_registry_entries() -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    if not REGISTRY_TASKS_DIR.exists():
        return out
    for path in sorted(REGISTRY_TASKS_DIR.glob("*.json")):
        obj = json.loads(path.read_text(encoding="utf-8"))
        out[obj["task_slug"]] = obj
    return out


def _collect_issues() -> list[str]:
    issues: list[str] = []

    active_slugs = _active_task_slugs()
    for slug in active_slugs:
        expected = [
            TASK_PAGE_DIR / f"{slug}.md",
            SPEC_DIR / f"{slug}.md",
            PLAN_DIR / f"{slug}.md",
            IMPLEMENT_DIR / f"{slug}.md",
            STATUS_DIR / f"{slug}.md",
        ]
        missing = [_relative(path) for path in expected if not path.exists()]
        if missing:
            issues.append(f"active task `{slug}` is missing chain files: {', '.join(missing)}")

    deprecated_candidates = [
        SPEC_DIR / "self_collision_transfer_decision.md",
        PLAN_DIR / "self_collision_transfer_decision.md",
        STATUS_DIR / "self_collision_transfer_decision.md",
        SPEC_DIR / "final_self_collision_campaign.md",
        PLAN_DIR / "final_self_collision_campaign.md",
        IMPLEMENT_DIR / "final_self_collision_campaign.md",
        STATUS_DIR / "final_self_collision_campaign.md",
    ]
    for path in deprecated_candidates:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if "Deprecated" not in text and "Historical" not in text:
            issues.append(f"deprecated surface lacks deprecation marker: {_relative(path)}")

    if not DEPRECATIONS_DOC.exists():
        issues.append("missing deprecation ledger: docs/generated/harness_deprecations.md")

    registry_entries = _load_registry_entries()
    expected_registry = {
        "robot_deformable_demo",
        "native_robot_rope_drop_release",
        "bunny_penetration_force_diagnostic",
        "rope_perf_apples_to_apples",
        "self_collision_transfer",
    }
    for slug in sorted(expected_registry):
        if slug not in registry_entries:
            issues.append(f"missing results registry entry for `{slug}`")
    for slug, entry in registry_entries.items():
        chain = entry.get("task_chain") or {}
        for key in ("task_page", "spec", "plan", "implement", "status"):
            rel = chain.get(key)
            if not rel:
                issues.append(f"registry entry `{slug}` missing task_chain field `{key}`")
                continue
            if not (ROOT / rel).exists():
                issues.append(f"registry entry `{slug}` points to missing `{key}` path: {rel}")

    if not (RESULTS_META_DIR / "INDEX.md").exists():
        issues.append("missing generated results registry index: results_meta/INDEX.md")
    if not (RESULTS_META_DIR / "LATEST.md").exists():
        issues.append("missing generated results registry latest view: results_meta/LATEST.md")

    all_durable_docs = list((ROOT / "docs").rglob("*.md")) + list((ROOT / "tasks").rglob("*.md")) + list((ROOT / "plans").rglob("*.md")) + [ROOT / "AGENTS.md"]
    for path in sorted(all_durable_docs):
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if ABSOLUTE_PATH_RE.search(text):
            issues.append(f"machine-local absolute path in durable doc: {_relative(path)}")

    slug_buckets: dict[str, list[str]] = defaultdict(list)
    for directory in (SPEC_DIR, PLAN_DIR, IMPLEMENT_DIR, STATUS_DIR):
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.md")):
            slug = path.stem
            normalized = slug.replace("_decision", "")
            slug_buckets[normalized].append(_relative(path))
    for normalized, paths in sorted(slug_buckets.items()):
        if len(paths) <= 4:
            continue
        if any("self_collision_transfer_decision" in p for p in paths):
            deprecated_ok = True
            for p in paths:
                full = ROOT / p
                text = full.read_text(encoding="utf-8")
                if "self_collision_transfer_decision" in p and "Deprecated" not in text:
                    deprecated_ok = False
            if not deprecated_ok:
                issues.append(f"ambiguous slug family `{normalized}` is not fully deprecated: {', '.join(paths)}")

    for slug, entry in registry_entries.items():
        run = entry.get("authoritative_run") or {}
        bundle_root = ROOT / entry.get("bundle_root", "")
        run_id = str(run.get("run_id") or "")
        if not run_id:
            issues.append(f"registry entry `{slug}` missing authoritative run id")
            continue
        if bundle_root.exists():
            for pointer_name in ("BEST_RUN.md", "INDEX.md", "LATEST_SUCCESS.txt"):
                pointer = bundle_root / pointer_name
                if not pointer.exists():
                    continue
                text = pointer.read_text(encoding="utf-8", errors="ignore")
                if run_id not in text and pointer_name != "LATEST_SUCCESS.txt":
                    issues.append(
                        f"local pointer surface does not mention registry run id `{run_id}`: {_relative(pointer)}"
                    )
                if pointer_name == "LATEST_SUCCESS.txt":
                    normalized = text.strip().replace(str(ROOT) + "/", "")
                    if run_id not in normalized:
                        issues.append(
                            f"local pointer surface does not resolve to registry run id `{run_id}`: {_relative(pointer)}"
                        )

    return issues


def main() -> int:
    issues = _collect_issues()
    if issues:
        print("Harness consistency check: FAIL")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("Harness consistency check: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
