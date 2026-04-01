#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

from md_truth_inventory import ROOT, active_task_slugs, build_inventory_paths


TASK_PAGE_DIR = ROOT / "docs/bridge/tasks"
SPEC_DIR = ROOT / "tasks/spec"
PLAN_DIR = ROOT / "plans/active"
IMPLEMENT_DIR = ROOT / "tasks/implement"
STATUS_DIR = ROOT / "tasks/status"
DEPRECATIONS_DOC = ROOT / "docs/generated/harness_deprecations.md"
HARNESS_AUDIT_DOC = ROOT / "docs/generated/harness_audit.md"
CURRENT_STATUS = ROOT / "docs/bridge/current_status.md"
MD_INVENTORY_JSON = ROOT / "docs/generated/md_inventory.json"
INVENTORY_MD = ROOT / "docs/generated/md_inventory.md"
MD_CLEANUP_REPORT = ROOT / "docs/generated/md_cleanup_report.md"
MD_ORPHANS = ROOT / "docs/generated/md_orphans.md"
MD_DEPRECATION_MATRIX = ROOT / "docs/generated/md_deprecation_matrix.md"
REGISTRY_TASKS_DIR = ROOT / "results_meta/tasks"

ROOT_SINGLETONS = ("Plan.md", "Prompt.md", "Status.md", "DecisionLog.md")
LOCAL_POINTER_RE = re.compile(r"(BEST_RUN\.md|LATEST_SUCCESS\.txt|LATEST_ATTEMPT\.txt)", re.IGNORECASE)
CANONICAL_CLAIM_RE = re.compile(r"\b(canonical|authoritative|source of truth|committed|best run|fallback)\b", re.IGNORECASE)
RUN_ID_RE = re.compile(r"\b(?:\d{8}_\d{6}[A-Za-z0-9_]*|[A-Za-z][A-Za-z0-9_]*_\d{8}(?:_\d{6})[A-Za-z0-9_]*)\b")
ALLOW_NONCANONICAL_MARKERS = ("historical", "local-only", "scratch", "comparison", "superseded", "rejected", "secondary")
LOCAL_ONLY_RESULTS_MD = (
    ROOT / "results/README.md",
    ROOT / "results/bunny_force_visualization/README.md",
    ROOT / "results/bunny_force_visualization/INDEX.md",
    ROOT / "results/robot_deformable_demo/README.md",
    ROOT / "results/robot_deformable_demo/BEST_RUN.md",
    ROOT / "results/native_robot_rope_drop_release/README.md",
    ROOT / "results/native_robot_rope_drop_release/BEST_RUN.md",
    ROOT / "results/rope_perf_apples_to_apples/README.md",
    ROOT / "results/rope_perf_apples_to_apples/BEST_EVIDENCE.md",
)
LOCAL_ONLY_RESULTS_TXT = (
    ROOT / "results/bunny_force_visualization/LATEST_ATTEMPT.txt",
    ROOT / "results/bunny_force_visualization/LATEST_SUCCESS.txt",
    ROOT / "results/native_robot_rope_drop_release/LATEST_ATTEMPT.txt",
    ROOT / "results/native_robot_rope_drop_release/LATEST_SUCCESS.txt",
)


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_inventory() -> list[dict[str, Any]]:
    if not MD_INVENTORY_JSON.exists():
        return []
    raw = json.loads(MD_INVENTORY_JSON.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        raw = raw.get("entries", [])
    return list(raw)


def _registry_entries() -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    if not REGISTRY_TASKS_DIR.exists():
        return out
    for path in sorted(REGISTRY_TASKS_DIR.glob("*.json")):
        obj = json.loads(path.read_text(encoding="utf-8"))
        out[obj["task_slug"]] = obj
    return out


def _issues_from_active_chain(active_slugs: list[str]) -> list[str]:
    issues: list[str] = []
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
    for path in sorted(PLAN_DIR.glob("*.md")):
        if path.name in {"README.md", "_plan_template.md"}:
            continue
        if path.stem not in active_slugs:
            issues.append(f"non-active plan still lives in plans/active/: {_relative(path)}")
    return issues


def _issues_from_root_singletons(inventory_by_path: dict[str, dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    for rel in ROOT_SINGLETONS:
        path = ROOT / rel
        if not path.exists():
            continue
        entry = inventory_by_path.get(rel)
        if entry is None:
            issues.append(f"retired root singleton is not in inventory: {rel}")
            continue
        if entry.get("classification") != "deprecated-pointer":
            issues.append(f"retired root singleton must be absent or an explicit deprecated stub: {rel}")
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        nonblank = [line for line in text.splitlines() if line.strip()]
        if len(nonblank) > 25:
            issues.append(f"retired root singleton stub is too substantive: {rel}")
        lowered = text.lower()
        if "do not use as source of truth" not in lowered:
            issues.append(f"retired root singleton stub lacks 'do not use as source of truth': {rel}")
    return issues


def _issues_from_inventory(entries: list[dict[str, Any]], registry_entries: dict[str, dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    if not entries:
        issues.append("missing generated markdown inventory: docs/generated/md_inventory.json")
        return issues

    scanned_paths = {_relative(path) for path in build_inventory_paths()}
    inventory_paths = {entry["path"] for entry in entries}
    missing = sorted(scanned_paths - inventory_paths)
    extra = sorted(inventory_paths - scanned_paths)
    if missing:
        issues.append(f"inventory is missing control-plane markdown paths: {', '.join(missing)}")
    if extra:
        issues.append(f"inventory contains stale paths that no longer exist: {', '.join(extra)}")

    delete_candidates = [entry["path"] for entry in entries if entry["classification"] == "delete-candidate"]
    if delete_candidates:
        issues.append(
            "control-plane markdown still has delete-candidates: "
            + ", ".join(sorted(delete_candidates))
        )

    for entry in entries:
        if entry["classification"] in {"deprecated-pointer", "historical"}:
            text = (ROOT / entry["path"]).read_text(encoding="utf-8", errors="ignore")
            lowered = text.lower()
            if "status:" not in lowered:
                issues.append(f"{entry['classification']} file lacks metadata status field: {entry['path']}")
            if "owner_surface:" not in lowered:
                issues.append(f"{entry['classification']} file lacks owner_surface field: {entry['path']}")
            if "last_reviewed:" not in lowered:
                issues.append(f"{entry['classification']} file lacks last_reviewed field: {entry['path']}")
            if "notes:" not in lowered:
                issues.append(f"{entry['classification']} file lacks notes field: {entry['path']}")
            if entry["classification"] == "deprecated-pointer" and not entry.get("canonical_replacement"):
                issues.append(f"deprecated-pointer file lacks canonical_replacement field: {entry['path']}")

    generated_expected = {
        "docs/generated/md_inventory.md",
        "docs/generated/md_inventory.json",
        "docs/generated/md_cleanup_report.md",
        "docs/generated/md_orphans.md",
        "docs/generated/md_deprecation_matrix.md",
    }
    for rel in sorted(generated_expected):
        if not (ROOT / rel).exists():
            issues.append(f"missing generated markdown artifact: {rel}")

    for entry in entries:
        if entry["classification"] == "canonical" and entry.get("contains_machine_local_paths"):
            issues.append(f"machine-local absolute path in canonical markdown surface: {entry['path']}")

        if entry["classification"] == "canonical":
            path = ROOT / entry["path"]
            if not path.exists():
                continue
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
            for idx, raw in enumerate(lines):
                if not LOCAL_POINTER_RE.search(raw):
                    continue
                context = "\n".join(lines[max(0, idx - 2) : idx + 1]).lower()
                if CANONICAL_CLAIM_RE.search(raw) and "local-only" not in context and "secondary" not in context:
                    issues.append(
                        f"canonical markdown treats local pointer as committed truth: {entry['path']}"
                    )
                    break

    for slug, entry in registry_entries.items():
        run = entry.get("authoritative_run") or {}
        run_id = str(run.get("run_id") or "")
        if not run_id:
            issues.append(f"registry entry `{slug}` missing authoritative run id")
            continue
        chain = entry.get("task_chain") or {}
        status_rel = chain.get("status")
        if not status_rel:
            issues.append(f"registry entry `{slug}` missing task-chain status path")
            continue
        status_path = ROOT / status_rel
        if not status_path.exists():
            issues.append(f"registry entry `{slug}` points to missing status page: {status_rel}")
            continue
        status_text = status_path.read_text(encoding="utf-8", errors="ignore")
        registry_rel = f"results_meta/tasks/{slug}.json"
        if registry_rel not in status_text:
            issues.append(f"status page `{status_rel}` does not mention its committed registry entry `{registry_rel}`")
        if run_id not in status_text:
            issues.append(f"status page `{status_rel}` does not mention registry run id `{run_id}`")
        for raw in status_text.splitlines():
            run_ids = RUN_ID_RE.findall(raw)
            if not run_ids:
                continue
            lowered = raw.lower()
            if any(marker in lowered for marker in ALLOW_NONCANONICAL_MARKERS):
                continue
            if CANONICAL_CLAIM_RE.search(raw) and run_id not in raw:
                issues.append(
                    f"status page `{status_rel}` contains authoritative-sounding non-registry run line: {raw.strip()}"
                )
                break

    if CURRENT_STATUS.exists():
        current_text = CURRENT_STATUS.read_text(encoding="utf-8", errors="ignore")
        for slug, entry in registry_entries.items():
            run_id = str((entry.get("authoritative_run") or {}).get("run_id") or "")
            if not run_id:
                continue
            if run_id in current_text:
                continue
            # Accept bundle-root-only summaries for rope perf, but require registry link or task name.
            bundle_root = str(entry.get("bundle_root") or "")
            if bundle_root and bundle_root in current_text:
                continue
            issues.append(
                f"current_status.md does not mention registry run id or bundle root for `{slug}`"
            )
    return issues


def _issues_from_registry_and_pointers(registry_entries: dict[str, dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    if not DEPRECATIONS_DOC.exists():
        issues.append("missing deprecation ledger: docs/generated/harness_deprecations.md")
    if not HARNESS_AUDIT_DOC.exists():
        issues.append("missing harness audit: docs/generated/harness_audit.md")
    for path in (INVENTORY_MD, MD_CLEANUP_REPORT, MD_ORPHANS, MD_DEPRECATION_MATRIX):
        if not path.exists():
            issues.append(f"missing generated markdown artifact: {_relative(path)}")

    if HARNESS_AUDIT_DOC.exists():
        audit = HARNESS_AUDIT_DOC.read_text(encoding="utf-8", errors="ignore")
        if "Root-Level Shadow Docs Competed With Task-Scoped Truth" in audit and "Current status: `resolved`" in audit:
            for rel in ROOT_SINGLETONS:
                if (ROOT / rel).exists():
                    issues.append("harness_audit.md claims root singleton issue is resolved, but a root singleton still exists")
                    break
        if "Video Acceptance Was Optimistic And Generator-Coupled" in audit and "Current status: `resolved`" in audit:
            required = [
                ROOT / "docs/evals/video_acceptance_rubric.md",
                ROOT / "docs/evals/video_evaluator_prompt.md",
                ROOT / "scripts/prepare_video_review_bundle.py",
                ROOT / "scripts/run_skeptical_video_audit.py",
            ]
            missing = [_relative(path) for path in required if not path.exists()]
            if missing:
                issues.append(
                    "harness_audit.md claims skeptical video layer resolved, but files are missing: "
                    + ", ".join(missing)
                )

    for slug, entry in registry_entries.items():
        chain = entry.get("task_chain") or {}
        for key in ("task_page", "spec", "plan", "implement", "status"):
            rel = chain.get(key)
            if not rel:
                issues.append(f"registry entry `{slug}` missing task_chain field `{key}`")
                continue
            if not (ROOT / rel).exists():
                issues.append(f"registry entry `{slug}` points to missing `{key}` path: {rel}")
        for rel in entry.get("local_only_surfaces", []):
            text = ""
            path = ROOT / rel
            if path.exists() and path.suffix == ".md":
                text = path.read_text(encoding="utf-8", errors="ignore")
                if CANONICAL_CLAIM_RE.search(text) and "local-only" not in text.lower() and "secondary" not in text.lower():
                    issues.append(f"local-only pointer surface still sounds canonical: {rel}")
    for path in LOCAL_ONLY_RESULTS_MD:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        lowered = text.lower()
        if "local-only" not in lowered and "local bundle" not in lowered and "local pointer" not in lowered:
            issues.append(f"tracked local-only results markdown lacks a local-only banner: {_relative(path)}")
        if "/home/" in text:
            issues.append(f"tracked local-only results markdown still contains machine-local paths: {_relative(path)}")
    expected_success = {
        _relative(ROOT / "results/bunny_force_visualization/LATEST_SUCCESS.txt"): str((registry_entries.get("bunny_penetration_force_diagnostic", {}).get("authoritative_run") or {}).get("run_id") or ""),
        _relative(ROOT / "results/native_robot_rope_drop_release/LATEST_SUCCESS.txt"): str((registry_entries.get("native_robot_rope_drop_release", {}).get("authoritative_run") or {}).get("run_id") or ""),
    }
    for path in LOCAL_ONLY_RESULTS_TXT:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").strip()
        if text.startswith("/home/"):
            issues.append(f"tracked local-only pointer text uses machine-local absolute path: {_relative(path)}")
        expected = expected_success.get(_relative(path))
        if expected and expected not in text:
            issues.append(f"latest-success pointer does not match results_meta: {_relative(path)}")
    if CURRENT_STATUS.exists():
        current_text = CURRENT_STATUS.read_text(encoding="utf-8", errors="ignore")
        contradictions = {
            "Committed results metadata mirrors for every major authoritative run family": "current_status.md still claims major results_meta mirrors are missing",
            "A hard skeptical video evaluator layer separate from optimistic automatic QC": "current_status.md still claims skeptical video evaluator is missing",
            "One standard harness-consistency lint pass in normal task closeout": "current_status.md still claims harness lint closeout is missing",
        }
        for needle, message in contradictions.items():
            if needle in current_text:
                issues.append(message)
    return issues


def _collect_issues() -> list[str]:
    issues: list[str] = []
    active_slugs = active_task_slugs()
    registry_entries = _registry_entries()
    inventory_entries = _load_inventory()
    inventory_by_path = {entry["path"]: entry for entry in inventory_entries}

    issues.extend(_issues_from_active_chain(active_slugs))
    issues.extend(_issues_from_root_singletons(inventory_by_path))
    issues.extend(_issues_from_inventory(inventory_entries, registry_entries))
    issues.extend(_issues_from_registry_and_pointers(registry_entries))
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
