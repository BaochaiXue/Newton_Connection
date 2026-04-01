#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_TASKS_README = ROOT / "docs/bridge/tasks/README.md"
REGISTRY_TASKS_DIR = ROOT / "results_meta/tasks"

ROOT_CONTROL_FILES = [
    ROOT / "AGENTS.md",
    ROOT / "TODO.md",
]

CONTROL_DIRS = [
    ROOT / "docs",
    ROOT / "tasks",
    ROOT / "plans",
    ROOT / "results_meta",
]

EXTRA_CONTROL_SURFACES = [
    ROOT / "results/README.md",
    ROOT / "Newton/phystwin_bridge/STATUS.md",
    ROOT / "Newton/phystwin_bridge/AGENTS.md",
    ROOT / "Newton/phystwin_bridge/demos/AGENTS.md",
    ROOT / "results/bunny_force_visualization/README.md",
    ROOT / "results/bunny_force_visualization/INDEX.md",
    ROOT / "results/bunny_force_visualization/QA_WORKFLOW.md",
    ROOT / "results/bunny_force_visualization/VERDICT_TEMPLATE.md",
    ROOT / "results/bunny_force_visualization/archive/README.md",
    ROOT / "results/native_robot_rope_drop_release/README.md",
    ROOT / "results/native_robot_rope_drop_release/BEST_RUN.md",
    ROOT / "results/native_robot_rope_drop_release/SLIDE_READY.md",
    ROOT / "results/robot_deformable_demo/README.md",
    ROOT / "results/robot_deformable_demo/BEST_RUN.md",
    ROOT / "results/robot_deformable_demo/LEGACY_CANDIDATES.md",
    ROOT / "results/robot_deformable_demo/SLIDE_READY.md",
    ROOT / "results/rope_perf_apples_to_apples/README.md",
    ROOT / "results/rope_perf_apples_to_apples/BEST_EVIDENCE.md",
    ROOT / "Newton/phystwin_bridge/results/robot_rope_franka/README.md",
    ROOT / "Newton/phystwin_bridge/results/robot_rope_franka/BEST_RUN/README.md",
]

GENERATED_TARGETS = [
    ROOT / "docs/generated/md_inventory.md",
    ROOT / "docs/generated/md_cleanup_report.md",
    ROOT / "docs/generated/md_orphans.md",
    ROOT / "docs/generated/md_deprecation_matrix.md",
]

GENERATED_MARKDOWN = {
    "docs/generated/harness_audit.md",
    "docs/generated/harness_deprecations.md",
    "docs/generated/md_inventory.md",
    "docs/generated/md_cleanup_report.md",
    "docs/generated/md_orphans.md",
    "docs/generated/md_deprecation_matrix.md",
    "results_meta/INDEX.md",
    "results_meta/LATEST.md",
}

LOCAL_POINTER_REPLACEMENTS = {
    "Newton/phystwin_bridge/STATUS.md": "docs/bridge/current_status.md",
    "results/bunny_force_visualization/INDEX.md": "results_meta/tasks/bunny_penetration_force_diagnostic.json",
    "results/native_robot_rope_drop_release/BEST_RUN.md": "results_meta/tasks/native_robot_rope_drop_release.json",
    "results/robot_deformable_demo/BEST_RUN.md": "results_meta/tasks/robot_deformable_demo.json",
    "results/rope_perf_apples_to_apples/BEST_EVIDENCE.md": "results_meta/tasks/rope_perf_apples_to_apples.json",
}

LOCAL_POINTER_REASONS = {
    "Newton/phystwin_bridge/STATUS.md": "Legacy subtree status surface kept only as a pointer into the canonical bridge control plane.",
    "results/bunny_force_visualization/INDEX.md": "Bundle-local pointer surface remains useful for local navigation, but committed run authority now lives in results_meta.",
    "results/native_robot_rope_drop_release/BEST_RUN.md": "Bundle-local convenience pointer only; committed run authority now lives in results_meta.",
    "results/robot_deformable_demo/BEST_RUN.md": "Bundle-local convenience pointer only; committed run authority now lives in results_meta.",
    "results/rope_perf_apples_to_apples/BEST_EVIDENCE.md": "Bundle-local summary pointer only; committed run authority now lives in results_meta.",
}

CANONICAL_ROOT_SURFACES = {
    "AGENTS.md": "workspace_harness",
    "TODO.md": "task_index",
    "docs/README.md": "docs_system",
    "docs/PROJECT_MAP.md": "docs_system",
    "docs/STYLE_GUIDE.md": "docs_system",
    "docs/bridge/README.md": "bridge_docs",
    "docs/bridge/current_status.md": "bridge_control_plane",
    "docs/bridge/experiment_index.md": "bridge_control_plane",
    "docs/bridge/open_questions.md": "bridge_control_plane",
    "docs/bridge/tasks/README.md": "task_index",
    "docs/bridge/tasks/AGENTS.md": "task_index",
    "docs/runbooks/README.md": "runbooks",
    "docs/evals/README.md": "evals",
    "docs/generated/README.md": "generated_docs",
    "results_meta/README.md": "results_registry",
    "results_meta/DEPRECATED.md": "results_registry",
    "results_meta/schema.md": "results_registry",
    "results_meta/AGENTS.md": "results_registry",
    "tasks/README.md": "task_execution",
    "tasks/AGENTS.md": "task_execution",
    "plans/README.md": "plans_system",
    "plans/completed/README.md": "plans_system",
    "tasks/contracts/README.md": "task_execution",
    "tasks/handoffs/README.md": "task_execution",
    "docs/archive/README.md": "docs_archive",
    "docs/runbooks/doc_gardening.md": "doc_gardening",
}

ABSOLUTE_PATH_RE = re.compile(r"(^|[^A-Za-z])(/home/[^\\s`'\"<>()]+)")
AUTHORITATIVE_WORD_RE = re.compile(r"\b(authoritative|current|latest|promoted|best run|best|final)\b", re.IGNORECASE)
RUN_ID_RE = re.compile(r"\b(?:20\d{6}(?:_\d{6})?(?:_[A-Za-z0-9]+)+|final_self_collision_campaign_\d{8}_\d{6}_[A-Za-z0-9]+)\b")
TASK_LINK_RE = re.compile(r"\[([^\]]+\.md)\]\(\./([^)]+\.md)\)")
MD_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)#]+\.md)(?:#[^)]+)?\)")


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _active_task_slugs() -> list[str]:
    text = ACTIVE_TASKS_README.read_text(encoding="utf-8").splitlines()
    active: list[str] = []
    in_active = False
    for raw in text:
        line = raw.strip()
        if line == "## Active Task Set":
            in_active = True
            continue
        if in_active and line.startswith("## "):
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


def active_task_slugs() -> list[str]:
    return _active_task_slugs()


def _registry_entries() -> dict[str, dict]:
    out: dict[str, dict] = {}
    if not REGISTRY_TASKS_DIR.exists():
        return out
    for path in sorted(REGISTRY_TASKS_DIR.glob("*.json")):
        obj = json.loads(path.read_text(encoding="utf-8"))
        out[obj["task_slug"]] = obj
    return out


def _parse_metadata_block(text: str) -> dict[str, str]:
    meta: dict[str, str] = {}
    for raw in text.splitlines()[:8]:
        line = raw.strip()
        if not line.startswith("> "):
            continue
        body = line[2:]
        if ":" not in body:
            continue
        key, value = body.split(":", 1)
        meta[key.strip()] = value.strip().strip("`")
    return meta


def _owner_surface(rel: str, *, meta: dict[str, str], active_slugs: list[str]) -> str:
    if meta.get("owner_surface"):
        return meta["owner_surface"]
    if rel in CANONICAL_ROOT_SURFACES:
        return CANONICAL_ROOT_SURFACES[rel]
    for prefix in ("docs/bridge/tasks/", "tasks/spec/", "tasks/implement/", "tasks/status/", "plans/active/", "plans/completed/"):
        if rel.startswith(prefix) and rel.endswith(".md"):
            slug = Path(rel).stem
            return slug if slug in active_slugs or not slug.startswith("_") else prefix.rstrip("/")
    if rel.startswith("results_meta/"):
        return "results_registry"
    if rel.startswith("results/bunny_force_visualization/"):
        return "bunny_penetration_force_diagnostic"
    if rel.startswith("results/native_robot_rope_drop_release/"):
        return "native_robot_rope_drop_release"
    if rel.startswith("results/robot_deformable_demo/"):
        return "robot_deformable_demo"
    if rel.startswith("results/rope_perf_apples_to_apples/"):
        return "rope_perf_apples_to_apples"
    if rel.startswith("Newton/phystwin_bridge/results/robot_rope_franka/"):
        return "robot_rope_franka_tabletop_push_hero"
    return "misc"


def _classify(rel: str, *, meta: dict[str, str]) -> tuple[str, str | None, str, str]:
    status = meta.get("status", "").lower()
    replacement = meta.get("canonical_replacement")
    notes = meta.get("notes", "")
    if rel in GENERATED_MARKDOWN:
        return ("generated", replacement, "GENERATED", notes or "Machine-generated control-plane surface.")
    if status == "deprecated":
        return ("deprecated-pointer", replacement, "STUB", notes or "Deprecated pointer surface.")
    if status == "historical":
        return ("historical", replacement, "ARCHIVE", notes or "Historical archive surface.")
    if rel in LOCAL_POINTER_REPLACEMENTS:
        return (
            "deprecated-pointer",
            LOCAL_POINTER_REPLACEMENTS[rel],
            "STUB",
            LOCAL_POINTER_REASONS[rel],
        )
    return ("canonical", replacement, "KEEP", notes or "Canonical live surface for its concept.")


def iter_control_plane_markdown() -> list[Path]:
    seen: set[str] = set()
    paths: list[Path] = []
    for path in ROOT_CONTROL_FILES:
        if path.exists():
            rel = _relative(path)
            seen.add(rel)
            paths.append(path)
    for directory in CONTROL_DIRS:
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*.md")):
            rel = _relative(path)
            if rel in seen:
                continue
            seen.add(rel)
            paths.append(path)
    for path in EXTRA_CONTROL_SURFACES:
        if not path.exists():
            continue
        rel = _relative(path)
        if rel in seen:
            continue
        seen.add(rel)
        paths.append(path)
    for path in GENERATED_TARGETS:
        rel = _relative(path)
        if rel in seen:
            continue
        seen.add(rel)
        paths.append(path)
    return sorted(paths, key=lambda p: _relative(p))


def build_inventory_paths() -> list[Path]:
    return iter_control_plane_markdown()


def build_inventory() -> list[dict]:
    active_slugs = _active_task_slugs()
    inventory: list[dict] = []
    for path in iter_control_plane_markdown():
        rel = _relative(path)
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        meta = _parse_metadata_block(text)
        classification, replacement, action, reason = _classify(rel, meta=meta)
        owner = _owner_surface(rel, meta=meta, active_slugs=active_slugs)
        inventory.append(
            {
                "path": rel,
                "classification": classification,
                "owner_surface": owner,
                "canonical_replacement": replacement or "",
                "action": action,
                "reason": reason,
                "contains_authoritative_language": bool(AUTHORITATIVE_WORD_RE.search(text)),
                "contains_run_ids": bool(RUN_ID_RE.search(text)),
                "contains_machine_local_paths": bool(ABSOLUTE_PATH_RE.search(text)),
            }
        )
    return inventory


def _resolve_link(path: Path, raw_target: str) -> str | None:
    if raw_target.startswith(("http://", "https://", "mailto:", "#")):
        return None
    target = (path.parent / raw_target).resolve()
    try:
        return _relative(target)
    except ValueError:
        return None


def find_orphans(inventory: list[dict]) -> list[dict]:
    path_map = {row["path"]: row for row in inventory}
    entrypoints = {
        "AGENTS.md",
        "TODO.md",
        "docs/README.md",
        "docs/bridge/tasks/README.md",
        "tasks/README.md",
        "plans/README.md",
        "results_meta/README.md",
        "docs/generated/README.md",
    }
    referenced: set[str] = set()
    for rel in entrypoints:
        if rel in path_map:
            referenced.add(rel)
    for row in inventory:
        path = ROOT / row["path"]
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for match in MD_LINK_RE.finditer(text):
            resolved = _resolve_link(path, match.group(1))
            if resolved and resolved in path_map:
                referenced.add(resolved)
        replacement = row["canonical_replacement"]
        if replacement and replacement in path_map:
            referenced.add(replacement)
    active_slugs = _active_task_slugs()
    for slug in active_slugs:
        for rel in (
            f"docs/bridge/tasks/{slug}.md",
            f"tasks/spec/{slug}.md",
            f"tasks/implement/{slug}.md",
            f"tasks/status/{slug}.md",
            f"plans/active/{slug}.md",
        ):
            if rel in path_map:
                referenced.add(rel)

    allowlist = {
        rel
        for rel in path_map
        if rel.endswith("README.md")
        or rel.endswith("AGENTS.md")
        or "/_" in rel
        or rel.startswith("docs/generated/")
        or rel.startswith("results_meta/")
    }
    orphans: list[dict] = []
    for row in inventory:
        if row["classification"] != "canonical":
            continue
        rel = row["path"]
        if rel in referenced or rel in allowlist:
            continue
        orphans.append(row)
    return orphans


def deprecation_rows(inventory: list[dict]) -> list[dict]:
    return [
        row
        for row in inventory
        if row["classification"] in {"deprecated-pointer", "historical"}
    ]


def summary_counts(inventory: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in inventory:
        key = row["classification"]
        counts[key] = counts.get(key, 0) + 1
    return counts
