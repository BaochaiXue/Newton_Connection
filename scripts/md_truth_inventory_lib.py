#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from datetime import date
from fnmatch import fnmatch
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_TASKS_README = ROOT / "docs/bridge/tasks/README.md"
REGISTRY_TASKS_DIR = ROOT / "results_meta/tasks"
PUBLIC_GENERATOR_CMD = "python scripts/generate_md_inventory.py"
PRIVATE_GENERATOR_CMD = "python scripts/generate_md_truth_inventory.py"
TODAY = date.today()

ROOT_CONTROL_FILES = [
    ROOT / "AGENTS.md",
    ROOT / "TODO.md",
]

CONTROL_DIRS = [
    ROOT / "tasks",
    ROOT / "plans",
    ROOT / "results_meta",
]

DOC_CONTROL_FILES = [
    ROOT / "docs" / "AGENTS.md",
    ROOT / "docs" / "README.md",
    ROOT / "docs" / "PROJECT_MAP.md",
    ROOT / "docs" / "STYLE_GUIDE.md",
    ROOT / "docs" / "archive" / "README.md",
    ROOT / "docs" / "bridge" / "README.md",
    ROOT / "docs" / "bridge" / "current_status.md",
    ROOT / "docs" / "bridge" / "open_questions.md",
    ROOT / "docs" / "bridge" / "experiment_index.md",
]

DOC_CONTROL_DIRS = [
    ROOT / "docs" / "bridge" / "tasks",
    ROOT / "docs" / "archive" / "tasks",
    ROOT / "docs" / "generated",
    ROOT / "docs" / "runbooks",
    ROOT / "docs" / "evals",
    ROOT / "docs" / "decisions",
]

EXTRA_CONTROL_SURFACES = [
    ROOT / "results/README.md",
    ROOT / "results/bunny_force_visualization/README.md",
    ROOT / "results/interactive_playground_profiling/README.md",
    ROOT / "results/native_robot_rope_drop_release/README.md",
    ROOT / "results/robot_deformable_demo/README.md",
    ROOT / "results/rope_perf_apples_to_apples/README.md",
    ROOT / "results/rope_perf_apples_to_apples_refresh/README.md",
    ROOT / "results/rope_perf_apples_to_apples_smoke/README.md",
    ROOT / "Newton/phystwin_bridge/STATUS.md",
    ROOT / "Newton/phystwin_bridge/AGENTS.md",
    ROOT / "Newton/phystwin_bridge/demos/AGENTS.md",
    ROOT / "Newton/phystwin_bridge/results/robot_rope_franka/README.md",
    ROOT / "Newton/phystwin_bridge/results/robot_rope_franka/BEST_RUN/README.md",
]

EXTRA_CONTROL_GLOBS = []

APPROVED_BUNDLE_ENTRY_SURFACES = {
    "results/README.md",
    "results/bunny_force_visualization/README.md",
    "results/interactive_playground_profiling/README.md",
    "results/native_robot_rope_drop_release/README.md",
    "results/robot_deformable_demo/README.md",
    "results/rope_perf_apples_to_apples/README.md",
    "results/rope_perf_apples_to_apples_refresh/README.md",
    "results/rope_perf_apples_to_apples_smoke/README.md",
    "Newton/phystwin_bridge/results/robot_rope_franka/README.md",
    "Newton/phystwin_bridge/results/robot_rope_franka/BEST_RUN/README.md",
}

APPROVED_BUNDLE_ENTRY_GLOBS = tuple(EXTRA_CONTROL_GLOBS)

ROOT_ALLOWED_TRACKED_COMPONENTS = {
    ".agents",
    ".codex",
    ".gitignore",
    ".gitmodules",
    "AGENTS.md",
    "Newton",
    "PhysTwin",
    "TODO.md",
    "diagnostics",
    "docs",
    "formal_slide",
    "plans",
    "results_meta",
    "scripts",
    "tasks",
}

GENERATED_TARGETS = [
    ROOT / "docs/generated/md_inventory.md",
    ROOT / "docs/generated/md_cleanup_report.md",
    ROOT / "docs/generated/md_orphans.md",
    ROOT / "docs/generated/md_deprecation_matrix.md",
    ROOT / "docs/generated/md_staleness_report.md",
    ROOT / "docs/generated/task_surface_matrix.md",
]

GENERATED_MARKDOWN = {
    "docs/generated/md_inventory.md",
    "docs/generated/md_cleanup_report.md",
    "docs/generated/md_orphans.md",
    "docs/generated/md_deprecation_matrix.md",
    "docs/generated/md_staleness_report.md",
    "docs/generated/task_surface_matrix.md",
    "results_meta/INDEX.md",
    "results_meta/LATEST.md",
}

CANONICAL_SURFACES = {
    "TODO.md",
    "docs/README.md",
    "docs/PROJECT_MAP.md",
    "docs/STYLE_GUIDE.md",
    "docs/bridge/current_status.md",
    "docs/bridge/experiment_index.md",
    "docs/bridge/open_questions.md",
    "docs/bridge/tasks/README.md",
    "docs/archive/tasks/README.md",
    "docs/generated/README.md",
    "docs/runbooks/doc_gardening.md",
    "results_meta/README.md",
    "results_meta/schema.md",
    "results_meta/DEPRECATED.md",
    "tasks/README.md",
    "tasks/AGENTS.md",
    "tasks/contracts/README.md",
    "tasks/handoffs/README.md",
    "tasks/history/README.md",
    "plans/README.md",
    "plans/completed/README.md",
    "AGENTS.md",
}

REVIEW_ENFORCED_SURFACES = {
    "TODO.md",
    "docs/bridge/current_status.md",
    "docs/bridge/open_questions.md",
    "docs/bridge/experiment_index.md",
    "docs/bridge/tasks/README.md",
    "docs/archive/README.md",
    "docs/archive/tasks/README.md",
    "docs/generated/README.md",
    "docs/runbooks/doc_gardening.md",
    "results_meta/README.md",
    "results_meta/DEPRECATED.md",
    "results_meta/schema.md",
    "tasks/README.md",
    "tasks/contracts/README.md",
    "tasks/handoffs/README.md",
}

ACTIVE_SUPPORTING_PATHS = {
    "docs/AGENTS.md",
    "docs/bridge/README.md",
    "docs/bridge/architecture.md",
    "docs/bridge/demos_and_diagnostics.md",
    "docs/bridge/ir_and_import.md",
    "docs/bridge/tasks/AGENTS.md",
    "docs/decisions/README.md",
    "docs/evals/README.md",
    "docs/evals/evaluator_rubric.md",
    "docs/evals/video_acceptance_rubric.md",
    "docs/evals/video_evaluator_prompt.md",
    "docs/generated/AGENTS.md",
    "docs/newton/README.md",
    "docs/newton/architecture.md",
    "docs/newton/runtime_and_contacts.md",
    "docs/phystwin/README.md",
    "docs/phystwin/architecture.md",
    "docs/phystwin/artifacts.md",
    "docs/runbooks/README.md",
    "docs/runbooks/local_dev.md",
    "docs/runbooks/pipeline_run.md",
    "docs/runbooks/release_send_pdf.md",
    "docs/archive/README.md",
    "Newton/phystwin_bridge/AGENTS.md",
    "Newton/phystwin_bridge/demos/AGENTS.md",
}

LOCAL_ONLY_SURFACES = {
    "results/README.md",
    "results/bunny_force_visualization/README.md",
    "results/interactive_playground_profiling/README.md",
    "results/native_robot_rope_drop_release/README.md",
    "results/robot_deformable_demo/README.md",
    "results/rope_perf_apples_to_apples/README.md",
    "results/rope_perf_apples_to_apples_refresh/README.md",
    "results/rope_perf_apples_to_apples_smoke/README.md",
    "Newton/phystwin_bridge/results/robot_rope_franka/README.md",
    "Newton/phystwin_bridge/results/robot_rope_franka/BEST_RUN/README.md",
}

LOCAL_ONLY_REPLACEMENTS = {
    "results/README.md": "results_meta/README.md",
    "results/bunny_force_visualization/README.md": "results_meta/tasks/bunny_penetration_force_diagnostic.json",
    "results/native_robot_rope_drop_release/README.md": "results_meta/tasks/native_robot_rope_drop_release.json",
    "results/robot_deformable_demo/README.md": "results_meta/tasks/robot_deformable_demo.json",
    "results/rope_perf_apples_to_apples/README.md": "results_meta/tasks/rope_perf_apples_to_apples.json",
    "results/rope_perf_apples_to_apples_refresh/README.md": "results_meta/tasks/rope_perf_apples_to_apples.json",
    "results/rope_perf_apples_to_apples_smoke/README.md": "results_meta/tasks/rope_perf_apples_to_apples.json",
    "Newton/phystwin_bridge/results/robot_rope_franka/README.md": "results_meta/tasks/robot_rope_franka_tabletop_push_hero.json",
    "Newton/phystwin_bridge/results/robot_rope_franka/BEST_RUN/README.md": "results_meta/tasks/robot_rope_franka_tabletop_push_hero.json",
}

OWNER_OVERRIDES = {
    "docs/bridge/current_status.md": "bridge_control_plane",
    "docs/bridge/experiment_index.md": "bridge_control_plane",
    "docs/bridge/open_questions.md": "bridge_control_plane",
    "docs/bridge/tasks/README.md": "task_index",
    "docs/runbooks/doc_gardening.md": "doc_gardening",
    "results/README.md": "results_registry",
    "results_meta/README.md": "results_registry",
    "results_meta/schema.md": "results_registry",
    "results_meta/DEPRECATED.md": "results_registry",
    "results_meta/INDEX.md": "results_registry",
    "results_meta/LATEST.md": "results_registry",
    "Newton/phystwin_bridge/STATUS.md": "bridge_control_plane",
    "tasks/README.md": "task_execution",
    "tasks/AGENTS.md": "task_execution",
    "tasks/contracts/README.md": "task_execution",
    "tasks/handoffs/README.md": "task_execution",
    "tasks/history/README.md": "task_history",
}

ENTRYPOINTS = {
    "AGENTS.md",
    "TODO.md",
    "docs/README.md",
    "docs/bridge/tasks/README.md",
    "tasks/README.md",
    "plans/README.md",
    "results_meta/README.md",
    "docs/generated/README.md",
}

WORKFLOW_CLASS = {
    "markdown_harness_maintenance_upgrade": "high_risk_multi_session_maintenance",
    "slide_deck_overhaul": "meeting_facing_release",
    "bridge_code_structure_cleanup": "multi_session_structural_refactor",
    "bunny_penetration_force_diagnostic": "result_bearing_visual_evidence",
    "rope_perf_apples_to_apples": "result_bearing_benchmark",
    "self_collision_transfer": "blocked_result_bearing",
}

CONTRACT_REQUIRED_TASKS = set(WORKFLOW_CLASS)
HANDOFF_REQUIRED_TASKS = set(WORKFLOW_CLASS)

ABSOLUTE_PATH_RE = re.compile(r"(^|[^A-Za-z])(/home/[^\s`'\"<>()]+)")
AUTHORITATIVE_WORD_RE = re.compile(
    r"\b(authoritative|current|latest|best run|best|promoted|final|canonical|source of truth)\b",
    re.IGNORECASE,
)
RUN_ID_RE = re.compile(
    r"\b(?:20\d{6}(?:_\d{6})?(?:_[A-Za-z0-9]+)+|final_self_collision_campaign_\d{8}_\d{6}_[A-Za-z0-9]+)\b"
)
TASK_LINK_RE = re.compile(r"\[([^\]]+\.md)\]\(\./([^)]+\.md)\)")
MD_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)#]+\.md)(?:#[^)]+)?\)")


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _parse_metadata_block(text: str) -> dict[str, str]:
    meta: dict[str, str] = {}
    for raw in text.splitlines()[:10]:
        line = raw.strip()
        if not line.startswith("> "):
            continue
        body = line[2:]
        if ":" not in body:
            continue
        key, value = body.split(":", 1)
        meta[key.strip()] = value.strip().strip("`")
    return meta


def _active_task_readme_rows() -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    section = ""
    for raw in ACTIVE_TASKS_README.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("## "):
            section = line[3:].strip()
            continue
        match = TASK_LINK_RE.search(line)
        if not match:
            continue
        rows.append((section, Path(match.group(2)).stem))
    return rows


def active_task_slugs() -> list[str]:
    return [slug for section, slug in _active_task_readme_rows() if section == "Active Task Set"]


def historical_task_slugs() -> list[str]:
    return [slug for section, slug in _active_task_readme_rows() if "Historical" in section or "One-Off" in section]


def _registry_entries() -> dict[str, dict]:
    out: dict[str, dict] = {}
    if not REGISTRY_TASKS_DIR.exists():
        return out
    for path in sorted(REGISTRY_TASKS_DIR.glob("*.json")):
        obj = json.loads(path.read_text(encoding="utf-8"))
        out[obj["task_slug"]] = obj
    return out


def _iter_extra_glob_paths() -> list[Path]:
    seen: set[str] = set()
    out: list[Path] = []
    for pattern in EXTRA_CONTROL_GLOBS:
        for path in sorted(ROOT.glob(pattern)):
            rel = _relative(path)
            if rel in seen:
                continue
            seen.add(rel)
            out.append(path)
    return out


def is_approved_bundle_entry(rel: str) -> bool:
    if rel in APPROVED_BUNDLE_ENTRY_SURFACES:
        return True
    return any(fnmatch(rel, pattern) for pattern in APPROVED_BUNDLE_ENTRY_GLOBS)


def tracked_root_components() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return []
    components = {
        line.split("/", 1)[0]
        for line in result.stdout.splitlines()
        if line.strip() and (ROOT / line).exists()
    }
    return sorted(components)


def root_allowlist_violations() -> list[str]:
    return [component for component in tracked_root_components() if component not in ROOT_ALLOWED_TRACKED_COMPONENTS]


def iter_control_plane_markdown() -> list[Path]:
    seen: set[str] = set()
    paths: list[Path] = []
    for path in ROOT_CONTROL_FILES:
        if path.exists():
            rel = _relative(path)
            seen.add(rel)
            paths.append(path)
    for path in DOC_CONTROL_FILES:
        if path.exists():
            rel = _relative(path)
            if rel in seen:
                continue
            seen.add(rel)
            paths.append(path)
    for directory in DOC_CONTROL_DIRS:
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*.md")):
            rel = _relative(path)
            if rel in seen:
                continue
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
    for path in EXTRA_CONTROL_SURFACES + _iter_extra_glob_paths():
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


def _is_template_or_helper(rel: str) -> bool:
    name = Path(rel).name
    return name.startswith("_") or name in {"AGENTS.md", "README.md"} and rel not in CANONICAL_SURFACES


def _owner_surface(rel: str, meta: dict[str, str], active_slugs: list[str]) -> str:
    if meta.get("owner_surface"):
        return meta["owner_surface"]
    if rel in OWNER_OVERRIDES:
        return OWNER_OVERRIDES[rel]
    if rel.startswith("docs/bridge/tasks/") and rel.endswith(".md") and not Path(rel).name.startswith("_"):
        return Path(rel).stem
    for prefix in ("tasks/spec/", "tasks/implement/", "tasks/status/", "plans/active/"):
        if rel.startswith(prefix) and rel.endswith(".md"):
            return Path(rel).stem
    if rel.startswith("tasks/history/"):
        parts = Path(rel).parts
        if len(parts) >= 4:
            return Path(parts[-1]).stem
        return "task_history"
    if rel.startswith("plans/completed/"):
        return Path(rel).stem
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
    if rel.startswith("Newton/phystwin_bridge/results/final_self_collision_campaign_"):
        return "self_collision_transfer"
    if Path(rel).stem in active_slugs:
        return Path(rel).stem
    return "misc"


def _base_classification(rel: str, meta: dict[str, str]) -> tuple[str, str, str]:
    status = meta.get("status", "").lower()
    replacement = meta.get("canonical_replacement", "")
    notes = meta.get("notes", "")
    if rel in GENERATED_MARKDOWN:
        return ("GENERATED_CANONICAL", replacement, notes or "Generated control-plane surface.")
    if status == "deprecated":
        return ("DEPRECATED_POINTER", replacement, notes or "Deprecated pointer surface.")
    if status == "historical":
        return ("HISTORICAL_ARCHIVE", replacement, notes or "Historical archive surface.")
    if rel.startswith("docs/archive/") and rel not in {"docs/archive/README.md", "docs/archive/tasks/README.md"}:
        return ("HISTORICAL_ARCHIVE", replacement or "none", notes or "Historical archived documentation surface.")
    if rel.startswith("tasks/history/") and rel != "tasks/history/README.md":
        return ("HISTORICAL_ARCHIVE", replacement or "none", notes or "Execution-layer historical archive.")
    if rel.startswith("plans/completed/") and rel != "plans/completed/README.md":
        return ("HISTORICAL_ARCHIVE", replacement or "none", notes or "Completed or historical plan surface.")
    if rel in LOCAL_ONLY_SURFACES:
        return (
            "LOCAL_ONLY_SECONDARY",
            LOCAL_ONLY_REPLACEMENTS.get(rel, replacement),
            notes or "Tracked local-only result/navigation surface; committed authority lives elsewhere.",
        )
    if rel == "Newton/phystwin_bridge/STATUS.md":
        return (
            "DEPRECATED_POINTER",
            "docs/bridge/current_status.md",
            notes or "Legacy subtree status surface kept only as a pointer into the canonical bridge dashboard.",
        )
    if rel in CANONICAL_SURFACES or rel.startswith("results_meta/tasks/"):
        return ("CANONICAL", replacement, notes or "Canonical live surface for its concept.")
    if rel.startswith("docs/bridge/tasks/") and Path(rel).stem in active_task_slugs():
        return ("CANONICAL", replacement, notes or "Active canonical task page.")
    if rel.startswith(("tasks/spec/", "tasks/implement/", "tasks/status/", "plans/active/")) and not _is_template_or_helper(rel):
        return ("ACTIVE_SUPPORTING", replacement, notes or "Active execution-chain support surface.")
    if _is_template_or_helper(rel) or rel in ACTIVE_SUPPORTING_PATHS:
        return ("ACTIVE_SUPPORTING", replacement, notes or "Supporting control-plane surface.")
    return ("CANONICAL", replacement, notes or "Canonical live surface for its concept.")


def _resolve_link(path: Path, raw_target: str) -> str | None:
    if raw_target.startswith(("http://", "https://", "mailto:", "#")):
        return None
    target = (path.parent / raw_target).resolve()
    try:
        return _relative(target)
    except ValueError:
        return None


def _indexed_paths(path_rows: dict[str, dict]) -> set[str]:
    referenced: set[str] = {rel for rel in ENTRYPOINTS if rel in path_rows}
    for row in path_rows.values():
        path = ROOT / row["path"]
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for match in MD_LINK_RE.finditer(text):
            resolved = _resolve_link(path, match.group(1))
            if resolved and resolved in path_rows:
                referenced.add(resolved)
        replacement = row["canonical_replacement"]
        if replacement and replacement != "none" and replacement in path_rows:
            referenced.add(replacement)
    for slug in active_task_slugs():
        for rel in (
            f"docs/bridge/tasks/{slug}.md",
            f"tasks/spec/{slug}.md",
            f"plans/active/{slug}.md",
            f"tasks/implement/{slug}.md",
            f"tasks/status/{slug}.md",
        ):
            if rel in path_rows:
                referenced.add(rel)
    return referenced


def _allow_unindexed(rel: str, classification: str) -> bool:
    if classification in {"GENERATED_CANONICAL", "DEPRECATED_POINTER", "HISTORICAL_ARCHIVE", "LOCAL_ONLY_SECONDARY"}:
        return True
    if rel.endswith(("README.md", "AGENTS.md")):
        return True
    if Path(rel).name.startswith("_"):
        return True
    if rel.startswith(("results_meta/", "docs/generated/")):
        return True
    return False


def _line_metrics(text: str) -> tuple[int, int, float]:
    lines = text.splitlines()
    nonblank = [line for line in lines if line.strip()]
    max_len = max((len(line) for line in lines), default=0)
    avg_len = sum(len(line) for line in nonblank) / len(nonblank) if nonblank else 0.0
    return len(lines), max_len, avg_len


def _overgrown_for_role(rel: str, line_count: int) -> bool:
    if rel == "docs/bridge/current_status.md":
        return line_count > 140
    if rel == "docs/bridge/tasks/README.md":
        return line_count > 120
    if rel == "TODO.md":
        return line_count > 140
    if rel.startswith("docs/bridge/tasks/"):
        return line_count > 220
    if rel.startswith(("tasks/status/", "tasks/spec/", "tasks/implement/", "plans/active/")):
        return line_count > 220
    if rel.startswith("docs/runbooks/"):
        return line_count > 220
    if rel.startswith("docs/generated/"):
        return line_count > 280
    return line_count > 320


def _line_compressed(max_len: int, avg_len: float) -> bool:
    return max_len > 260 or avg_len > 170.0


def _parse_review_interval_days(value: str) -> int | None:
    raw = value.strip().lower()
    if not raw:
        return None
    if raw.endswith("d") and raw[:-1].isdigit():
        return int(raw[:-1])
    if raw.isdigit():
        return int(raw)
    return None


def _default_review_interval(rel: str, classification: str) -> int | None:
    if classification == "GENERATED_CANONICAL":
        return None
    if rel == "docs/bridge/current_status.md":
        return 7
    if rel in {
        "TODO.md",
        "docs/bridge/tasks/README.md",
        "tasks/README.md",
        "results_meta/README.md",
        "docs/generated/README.md",
        "docs/runbooks/doc_gardening.md",
    }:
        return 30
    if rel.startswith("docs/bridge/tasks/") and not Path(rel).name.startswith("_"):
        return 21
    if rel.startswith(("tasks/status/", "tasks/spec/", "tasks/implement/", "plans/active/")) and not Path(rel).name.startswith("_"):
        return 21
    if classification in {"CANONICAL", "ACTIVE_SUPPORTING"}:
        return 90
    return None


def _review_enforced(rel: str, classification: str) -> bool:
    if classification == "GENERATED_CANONICAL":
        return False
    if rel in REVIEW_ENFORCED_SURFACES:
        return True
    if rel.startswith("docs/bridge/tasks/") and Path(rel).stem in active_task_slugs():
        return True
    return False


def _in_review_scope(rel: str, classification: str) -> bool:
    if classification == "GENERATED_CANONICAL":
        return False
    if rel in {
        "TODO.md",
        "docs/bridge/current_status.md",
        "docs/bridge/open_questions.md",
        "docs/bridge/tasks/README.md",
        "docs/generated/README.md",
        "docs/runbooks/doc_gardening.md",
        "results_meta/README.md",
        "results_meta/schema.md",
        "tasks/README.md",
        "tasks/contracts/README.md",
        "tasks/handoffs/README.md",
        "docs/bridge/tasks/markdown_harness_maintenance_upgrade.md",
        "tasks/spec/markdown_harness_maintenance_upgrade.md",
        "plans/active/markdown_harness_maintenance_upgrade.md",
        "tasks/implement/markdown_harness_maintenance_upgrade.md",
        "tasks/status/markdown_harness_maintenance_upgrade.md",
    }:
        return True
    if rel.startswith("docs/bridge/tasks/") and Path(rel).stem in active_task_slugs():
        return True
    return False


def _review_info(meta: dict[str, str], rel: str, classification: str) -> tuple[int | None, int | None, str]:
    if classification == "GENERATED_CANONICAL":
        return (None, None, "generated")
    if not _in_review_scope(rel, classification):
        return (None, None, "out_of_scope")
    interval_days = _parse_review_interval_days(meta.get("review_interval", "")) or _default_review_interval(rel, classification)
    last = meta.get("last_reviewed", "")
    if not last:
        return (interval_days, None, "missing")
    try:
        reviewed = date.fromisoformat(last)
    except ValueError:
        return (interval_days, None, "parse_error")
    age = (TODAY - reviewed).days
    if interval_days is None:
        return (None, age, "ok")
    return (interval_days, age, "due" if age > interval_days else "ok")


def _recommended_action(classification: str, overgrown: bool, line_compressed: bool, review_status: str) -> str:
    if classification == "GENERATED_CANONICAL":
        return "GENERATED"
    if classification == "DEPRECATED_POINTER":
        return "STUB"
    if classification == "HISTORICAL_ARCHIVE":
        return "ARCHIVE"
    if classification == "DELETE_CANDIDATE":
        return "DELETE"
    if classification == "ORPHAN":
        return "MERGE"
    if overgrown or line_compressed or review_status in {"missing", "due", "parse_error"}:
        return "REFORMAT"
    return "KEEP"


def build_inventory() -> list[dict]:
    active_slugs = active_task_slugs()
    rows: list[dict] = []
    for path in iter_control_plane_markdown():
        rel = _relative(path)
        text = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
        meta = _parse_metadata_block(text)
        classification, replacement, reason = _base_classification(rel, meta)
        owner = _owner_surface(rel, meta, active_slugs)
        line_count, max_line_len, avg_line_len = _line_metrics(text)
        review_interval_days, review_age_days, review_status = _review_info(meta, rel, classification)
        rows.append(
            {
                "path": rel,
                "classification": classification,
                "owner_surface": owner,
                "canonical_replacement": replacement or ("none" if classification == "HISTORICAL_ARCHIVE" else ""),
                "reason": reason,
                "contains_authoritative_language": bool(AUTHORITATIVE_WORD_RE.search(text)),
                "contains_run_ids": bool(RUN_ID_RE.search(text)),
                "contains_machine_local_paths": bool(ABSOLUTE_PATH_RE.search(text)),
                "line_count": line_count,
                "max_line_length": max_line_len,
                "avg_nonblank_line_length": round(avg_line_len, 1),
                "review_interval_days": review_interval_days,
                "review_age_days": review_age_days,
                "review_status": review_status,
                "metadata_status": meta.get("status", ""),
                "metadata_owner_surface": meta.get("owner_surface", ""),
                "metadata_last_reviewed": meta.get("last_reviewed", ""),
                "metadata_review_interval": meta.get("review_interval", ""),
                "metadata_update_rule": meta.get("update_rule", ""),
                "metadata_notes": meta.get("notes", ""),
                "approved_bundle_entry": is_approved_bundle_entry(rel),
            }
        )
    row_map = {row["path"]: row for row in rows}
    indexed = _indexed_paths(row_map)
    for row in rows:
        rel = row["path"]
        row["indexed_from_canonical_entrypoint"] = rel in indexed
        row["overgrown_for_role"] = _overgrown_for_role(rel, row["line_count"])
        row["line_compressed"] = _line_compressed(row["max_line_length"], row["avg_nonblank_line_length"])
        row["review_enforced"] = _review_enforced(rel, row["classification"])
        if row["classification"] in {"CANONICAL", "ACTIVE_SUPPORTING"} and not row["indexed_from_canonical_entrypoint"] and not _allow_unindexed(rel, row["classification"]):
            row["classification"] = "ORPHAN"
            row["reason"] = "Control-plane file is not indexed from canonical entrypoints or active task chains."
            row["review_enforced"] = False
        row["action"] = _recommended_action(
            row["classification"],
            row["overgrown_for_role"],
            row["line_compressed"],
            row["review_status"] if row["review_enforced"] else "ok",
        )
        row["actionable_status"] = (
            "generated"
            if row["classification"] == "GENERATED_CANONICAL"
            else "actionable"
            if row["action"] in {"REFORMAT", "STUB", "ARCHIVE", "MERGE", "DELETE"}
            else "quiet"
        )
    return rows


def find_orphans(inventory: list[dict]) -> list[dict]:
    return [row for row in inventory if row["classification"] == "ORPHAN"]


def deprecation_rows(inventory: list[dict]) -> list[dict]:
    return [
        row
        for row in inventory
        if row["classification"] in {"DEPRECATED_POINTER", "HISTORICAL_ARCHIVE", "LOCAL_ONLY_SECONDARY"}
    ]


def summary_counts(inventory: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in inventory:
        key = row["classification"]
        counts[key] = counts.get(key, 0) + 1
    return counts


def staleness_rows(inventory: list[dict]) -> list[dict]:
    return [
        row
        for row in inventory
        if (
            row["review_enforced"] and row["review_status"] in {"missing", "due", "parse_error"}
        )
        or (row["overgrown_for_role"] and row["classification"] != "HISTORICAL_ARCHIVE")
        or (
            row["line_compressed"]
            and row["classification"] in {"CANONICAL", "ACTIVE_SUPPORTING", "LOCAL_ONLY_SECONDARY"}
        )
    ]


def task_surface_rows() -> list[dict]:
    registry = _registry_entries()
    rows: list[dict] = []
    for slug in active_task_slugs():
        task_page = ROOT / f"docs/bridge/tasks/{slug}.md"
        spec = ROOT / f"tasks/spec/{slug}.md"
        plan = ROOT / f"plans/active/{slug}.md"
        implement = ROOT / f"tasks/implement/{slug}.md"
        status = ROOT / f"tasks/status/{slug}.md"
        registry_entry = registry.get(slug)
        contract_files = sorted((ROOT / "tasks/contracts").glob(f"{slug}*.md"))
        contract_files = [path for path in contract_files if path.name != "_contract_template.md"]
        handoff_files = sorted((ROOT / "tasks/handoffs").glob(f"{slug}*.md"))
        handoff_files = [path for path in handoff_files if path.name != "_handoff_template.md"]
        workflow_class = WORKFLOW_CLASS.get(slug, "")
        contract_required = slug in CONTRACT_REQUIRED_TASKS
        handoff_required = slug in HANDOFF_REQUIRED_TASKS
        rows.append(
            {
                "task_slug": slug,
                "task_page": task_page.exists(),
                "spec": spec.exists(),
                "plan": plan.exists(),
                "implement": implement.exists(),
                "status": status.exists(),
                "contract": bool(contract_files),
                "handoff": bool(handoff_files),
                "workflow_class": workflow_class,
                "contract_required": contract_required,
                "handoff_required": handoff_required,
                "contract_ok": (not contract_required) or bool(contract_files),
                "handoff_ok": (not handoff_required) or bool(handoff_files),
                "contract_paths": ", ".join(_relative(path) for path in contract_files),
                "handoff_paths": ", ".join(_relative(path) for path in handoff_files),
                "registry_backed": bool(registry_entry),
                "registry_state": (registry_entry or {}).get("authoritative_run", {}).get("task_state", ""),
                "registry_run_id": (registry_entry or {}).get("authoritative_run", {}).get("run_id", ""),
                "results_meta_path": f"results_meta/tasks/{slug}.json" if registry_entry else "",
            }
        )
    return rows
