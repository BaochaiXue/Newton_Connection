#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

from md_truth_inventory_lib import (
    ROOT,
    PUBLIC_GENERATOR_CMD,
    CONTRACT_REQUIRED_TASKS,
    HANDOFF_REQUIRED_TASKS,
    active_task_slugs,
    build_inventory,
    is_approved_bundle_entry,
    root_allowlist_violations,
)


TASK_PAGE_DIR = ROOT / "docs/bridge/tasks"
SPEC_DIR = ROOT / "tasks/spec"
PLAN_DIR = ROOT / "plans/active"
IMPLEMENT_DIR = ROOT / "tasks/implement"
STATUS_DIR = ROOT / "tasks/status"
TASK_HISTORY_DIR = ROOT / "tasks/history"
CURRENT_STATUS = ROOT / "docs/bridge/current_status.md"
TASKS_README = ROOT / "docs/bridge/tasks/README.md"
DOC_GARDENING = ROOT / "docs/runbooks/doc_gardening.md"
AGENT_REPORTING = ROOT / "docs/runbooks/agent_reporting.md"
GENERATED_README = ROOT / "docs/generated/README.md"
RESULTS_README = ROOT / "results_meta/README.md"
MD_INVENTORY_JSON = ROOT / "docs/generated/md_inventory.json"
ROOT_AGENTS = ROOT / "AGENTS.md"
TASKS_AGENTS = ROOT / "tasks/AGENTS.md"
SESSION_START_HOOK = ROOT / ".codex/hooks/session_start.py"
POST_TOOL_HOOK = ROOT / ".codex/hooks/post_tool_use_review.py"
STOP_HOOK = ROOT / ".codex/hooks/stop_continue.py"
GENERATED_REQUIRED = [
    ROOT / "docs/generated/md_inventory.md",
    ROOT / "docs/generated/md_inventory.json",
    ROOT / "docs/generated/md_cleanup_report.md",
    ROOT / "docs/generated/md_orphans.md",
    ROOT / "docs/generated/md_deprecation_matrix.md",
    ROOT / "docs/generated/md_staleness_report.md",
    ROOT / "docs/generated/task_surface_matrix.md",
]
REGISTRY_TASKS_DIR = ROOT / "results_meta/tasks"

ROOT_SINGLETONS = ("Plan.md", "Prompt.md", "Status.md", "DecisionLog.md")
RUN_ID_RE = re.compile(
    r"\b(?:20\d{6}(?:_\d{6})?(?:_[A-Za-z0-9]+)+|final_self_collision_campaign_\d{8}_\d{6}_[A-Za-z0-9]+)\b"
)
CANONICAL_WORD_RE = re.compile(
    r"\b(authoritative|current|latest|best run|best|promoted|source of truth|canonical)\b",
    re.IGNORECASE,
)
NONCANONICAL_MARKERS = ("local-only", "secondary", "historical", "deprecated", "scratch", "rejected", "superseded")
BASE_REQUIRED_METADATA_SURFACES = {
    "TODO.md",
    "docs/bridge/current_status.md",
    "docs/bridge/tasks/README.md",
    "docs/bridge/experiment_index.md",
    "docs/bridge/open_questions.md",
    "docs/archive/README.md",
    "docs/archive/tasks/README.md",
    "docs/generated/README.md",
    "docs/runbooks/agent_reporting.md",
    "docs/runbooks/doc_gardening.md",
    "results_meta/README.md",
    "results_meta/DEPRECATED.md",
    "results_meta/schema.md",
    "docs/bridge/tasks/markdown_harness_maintenance_upgrade.md",
    "tasks/spec/markdown_harness_maintenance_upgrade.md",
    "plans/active/markdown_harness_maintenance_upgrade.md",
    "tasks/implement/markdown_harness_maintenance_upgrade.md",
    "tasks/status/markdown_harness_maintenance_upgrade.md",
}


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _load_generated_inventory() -> list[dict[str, Any]]:
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


def _metadata_present(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="ignore").splitlines()[:10]
    required = {"status:", "owner_surface:", "last_reviewed:", "review_interval:", "update_rule:", "notes:"}
    found = {line[2:].split(":", 1)[0].strip() + ":" for line in text if line.startswith("> ") and ":" in line}
    return required.issubset(found)


def _required_metadata_surfaces(active_slugs: list[str]) -> set[str]:
    surfaces = set(BASE_REQUIRED_METADATA_SURFACES)
    for slug in active_slugs:
        surfaces.add(f"docs/bridge/tasks/{slug}.md")
    return surfaces


def _issues_from_generated_inventory(fresh: list[dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    generated = _load_generated_inventory()
    if not generated:
        issues.append("missing generated markdown inventory JSON; run python scripts/generate_md_inventory.py")
        return issues

    fresh_by_path = {row["path"]: row for row in fresh}
    generated_by_path = {row["path"]: row for row in generated}
    fresh_paths = set(fresh_by_path)
    generated_paths = set(generated_by_path)
    if fresh_paths != generated_paths:
        missing = sorted(fresh_paths - generated_paths)
        extra = sorted(generated_paths - fresh_paths)
        if missing:
            issues.append("generated inventory is missing current control-plane paths: " + ", ".join(missing))
        if extra:
            issues.append("generated inventory still lists stale paths: " + ", ".join(extra))
        return issues

    for path, fresh_row in fresh_by_path.items():
        gen_row = generated_by_path[path]
        for key in ("classification", "action", "contains_machine_local_paths", "indexed_from_canonical_entrypoint"):
            if gen_row.get(key) != fresh_row.get(key):
                issues.append(
                    f"generated inventory is stale for `{path}` field `{key}`: generated={gen_row.get(key)!r}, fresh={fresh_row.get(key)!r}"
                )
    return issues


def _issues_from_root_singletons() -> list[str]:
    issues: list[str] = []
    for rel in ROOT_SINGLETONS:
        if (ROOT / rel).exists():
            issues.append(f"retired root singleton recreated: {rel}")
    return issues


def _issues_from_active_task_chain(active_slugs: list[str]) -> list[str]:
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
    for directory in (SPEC_DIR, IMPLEMENT_DIR, STATUS_DIR):
        for path in sorted(directory.glob("*.md")):
            if path.name in {"README.md", "_spec_template.md", "_implement_template.md", "_status_template.md"}:
                continue
            if path.stem not in active_slugs:
                issues.append(f"historical or non-active file still lives in active execution dir: {_relative(path)}")
    return issues


def _issues_from_workflow_requirements(active_slugs: list[str]) -> list[str]:
    issues: list[str] = []
    for slug in active_slugs:
        if slug in CONTRACT_REQUIRED_TASKS and not (ROOT / f"tasks/contracts/{slug}.md").exists():
            issues.append(f"required-workflow task `{slug}` is missing tasks/contracts/{slug}.md")
        if slug in HANDOFF_REQUIRED_TASKS and not (ROOT / f"tasks/handoffs/{slug}.md").exists():
            issues.append(f"required-workflow task `{slug}` is missing tasks/handoffs/{slug}.md")
    return issues


def _issues_from_task_index(active_slugs: list[str]) -> list[str]:
    issues: list[str] = []
    text = TASKS_README.read_text(encoding="utf-8", errors="ignore")
    active_only = text.split("## Historical / Archive Routing")[0]
    if "harness_engineering_upgrade.md" in active_only:
        issues.append("docs/bridge/tasks/README.md still lists `harness_engineering_upgrade` as active")
    if "markdown_truthfulness_cleanup.md" in active_only:
        issues.append("docs/bridge/tasks/README.md still lists `markdown_truthfulness_cleanup` as active")
    if "markdown_harness_maintenance_upgrade.md" not in text:
        issues.append("docs/bridge/tasks/README.md does not list `markdown_harness_maintenance_upgrade`")
    archive_links = [
        link
        for link in re.findall(r"\.\./\.\./archive/tasks/([^)]+\.md)", text)
        if link != "README.md"
    ]
    if archive_links:
        issues.append(
            "docs/bridge/tasks/README.md should route history via docs/archive/tasks/README.md instead of inline archive links: "
            + ", ".join(sorted(archive_links))
        )
    return issues


def _issues_from_doc_task_neighborhood(active_slugs: list[str]) -> list[str]:
    issues: list[str] = []
    keep_names = {"README.md", "AGENTS.md", "_task_template.md"}
    for path in sorted(TASK_PAGE_DIR.glob("*.md")):
        if path.name in keep_names:
            continue
        if path.stem not in active_slugs:
            issues.append(f"historical or non-active task page still lives in docs/bridge/tasks/: {_relative(path)}")
    return issues


def _issues_from_current_status(fresh_inventory: list[dict[str, Any]], registry_entries: dict[str, dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    if not CURRENT_STATUS.exists():
        issues.append("missing docs/bridge/current_status.md")
        return issues
    text = CURRENT_STATUS.read_text(encoding="utf-8", errors="ignore")
    line_count = len(text.splitlines())
    if line_count > 140:
        issues.append(f"current_status.md is too long for a dashboard: {line_count} lines")
    if re.search(r"^##\s+20\d{2}-\d{2}-\d{2}", text, flags=re.MULTILINE):
        issues.append("current_status.md contains dated changelog-style sections; move those details into task status pages")
    if "results_meta/INDEX.md" not in text or "results_meta/LATEST.md" not in text:
        issues.append("current_status.md must point readers to results_meta/INDEX.md and results_meta/LATEST.md")
    missing_slugs = [slug for slug in active_task_slugs() if f"`{slug}`" not in text]
    if missing_slugs:
        issues.append(
            "current_status.md is missing active task slugs from the dashboard/workstream view: "
            + ", ".join(sorted(missing_slugs))
        )
    run_ids = set(RUN_ID_RE.findall(text))
    allowed_run_ids = {
        str((entry.get("authoritative_run") or {}).get("run_id") or "")
        for entry in registry_entries.values()
    }
    for run_id in sorted(run_ids):
        if run_id and run_id not in allowed_run_ids and "historical" not in text.lower():
            issues.append(f"current_status.md contains non-registry run id without historical marker: {run_id}")
    fresh_row = next((row for row in fresh_inventory if row["path"] == "docs/bridge/current_status.md"), None)
    if fresh_row and fresh_row["overgrown_for_role"]:
        issues.append("current_status.md is still flagged as overgrown in the fresh inventory")
    return issues


def _issues_from_root_allowlist() -> list[str]:
    return [f"tracked root component is outside the root allowlist: {component}" for component in root_allowlist_violations()]


def _issues_from_bundle_entry_policy(fresh_inventory: list[dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    for row in fresh_inventory:
        rel = row["path"]
        if not rel.startswith(("results/", "Newton/phystwin_bridge/results/")):
            continue
        if not is_approved_bundle_entry(rel):
            issues.append(f"deep bundle markdown must not be indexed unless explicitly approved as an entry surface: {rel}")
            continue
        if row["classification"] not in {"LOCAL_ONLY_SECONDARY", "DEPRECATED_POINTER", "HISTORICAL_ARCHIVE"}:
            issues.append(
                f"approved deep bundle entry surface must stay local-only, deprecated-pointer, or historical: {rel}"
            )
    return issues


def _issues_from_metadata(active_slugs: list[str], fresh_inventory: list[dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    required_surfaces = _required_metadata_surfaces(active_slugs)
    for rel in sorted(required_surfaces):
        path = ROOT / rel
        if not path.exists():
            issues.append(f"required metadata surface is missing: {rel}")
            continue
        if not _metadata_present(path):
            issues.append(f"required metadata surface lacks the standard metadata block: {rel}")
    for row in fresh_inventory:
        if row["path"] not in required_surfaces:
            continue
        if row["review_status"] in {"missing", "parse_error", "due"}:
            issues.append(
                f"required metadata surface has stale or invalid review metadata: {row['path']} ({row['review_status']})"
            )
    return issues


def _issues_from_generator_story() -> list[str]:
    issues: list[str] = []
    docs = {
        "docs/generated/README.md": GENERATED_README.read_text(encoding="utf-8", errors="ignore"),
        "docs/runbooks/doc_gardening.md": DOC_GARDENING.read_text(encoding="utf-8", errors="ignore"),
    }
    for rel, text in docs.items():
        if PUBLIC_GENERATOR_CMD not in text:
            issues.append(f"{rel} does not point to the canonical generator entrypoint `{PUBLIC_GENERATOR_CMD}`")
        lowered = text.lower()
        if "generate_md_truth_inventory.py" in text and "compatibility alias" not in lowered:
            issues.append(f"{rel} still presents generate_md_truth_inventory.py as a public workflow")
    for path in GENERATED_REQUIRED:
        if not path.exists():
            issues.append(f"missing generated markdown artifact: {_relative(path)}")
            continue
        if path.suffix == ".md":
            text = path.read_text(encoding="utf-8", errors="ignore")
            if PUBLIC_GENERATOR_CMD not in text:
                issues.append(f"generated markdown artifact does not cite the public generator entrypoint: {_relative(path)}")
            lowered = text.lower()
            if "generate_md_truth_inventory.py" in text and "compatibility alias" not in lowered:
                issues.append(f"generated markdown artifact still cites the private generator alias: {_relative(path)}")
    return issues


def _issues_from_reporting_discipline() -> list[str]:
    issues: list[str] = []
    if not AGENT_REPORTING.exists():
        issues.append("missing docs/runbooks/agent_reporting.md")
        return issues

    runbook_text = AGENT_REPORTING.read_text(encoding="utf-8", errors="ignore").lower()
    for needle in ("what changed", "problem", "conclusion", "next step"):
        if needle not in runbook_text:
            issues.append(f"agent_reporting.md is missing required reporting guidance: {needle}")

    ag_text = ROOT_AGENTS.read_text(encoding="utf-8", errors="ignore")
    if "docs/runbooks/agent_reporting.md" not in ag_text:
        issues.append("AGENTS.md must point to docs/runbooks/agent_reporting.md")

    tasks_text = TASKS_AGENTS.read_text(encoding="utf-8", errors="ignore")
    if "docs/runbooks/agent_reporting.md" not in tasks_text:
        issues.append("tasks/AGENTS.md must point to docs/runbooks/agent_reporting.md")

    session_text = SESSION_START_HOOK.read_text(encoding="utf-8", errors="ignore").lower()
    if "what changed" not in session_text or "next step" not in session_text:
        issues.append("session_start hook does not remind agents to report changes and next step")

    post_text = POST_TOOL_HOOK.read_text(encoding="utf-8", errors="ignore").lower()
    if "what changed" not in post_text or "conclusion" not in post_text:
        issues.append("post_tool_use_review hook does not reinforce outcome-first reporting")

    stop_text = STOP_HOOK.read_text(encoding="utf-8", errors="ignore").lower()
    if "outcome-first" not in stop_text or "before vs after" not in stop_text:
        issues.append("stop_continue hook does not enforce the reporting-discipline heuristic")
    return issues


def _issues_from_authority_surfaces(fresh_inventory: list[dict[str, Any]], registry_entries: dict[str, dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    fresh_by_path = {row["path"]: row for row in fresh_inventory}

    robot_root = fresh_by_path.get("Newton/phystwin_bridge/results/robot_rope_franka/README.md")
    robot_best = fresh_by_path.get("Newton/phystwin_bridge/results/robot_rope_franka/BEST_RUN/README.md")
    for row in (robot_root, robot_best):
        if row and row["classification"] != "LOCAL_ONLY_SECONDARY":
            issues.append(f"robot tabletop local result surface must be LOCAL_ONLY_SECONDARY: {row['path']}")

    for rel in (
        "Newton/phystwin_bridge/results/final_self_collision_campaign_20260330_205935_4fdef39/README.md",
        "Newton/phystwin_bridge/results/final_self_collision_campaign_20260331_033636_533f3d0/README.md",
        "Newton/phystwin_bridge/results/final_self_collision_campaign_20260331_033636_533f3d0/FINAL_STATUS.md",
        "Newton/phystwin_bridge/results/robot_rope_franka/README.md",
        "Newton/phystwin_bridge/results/robot_rope_franka/BEST_RUN/README.md",
        "results/rope_perf_apples_to_apples/BEST_EVIDENCE.md",
        "results/robot_deformable_demo/runs/README.md",
        "results/native_robot_rope_drop_release/runs/20260331_232106_native_franka_recoilfix_drag_off_w5/README.md",
    ):
        path = ROOT / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        if (
            "local-only" not in text
            and "historical" not in text
            and "do not use this page as the committed source of truth" not in text
            and "do not use it as the current source of truth" not in text
        ):
            issues.append(f"local result surface lacks explicit local-only truth banner: {rel}")
        if "/home/" in text:
            issues.append(f"local result surface still contains machine-local absolute path: {rel}")

    slide_status = ROOT / "tasks/status/slide_deck_overhaul.md"
    if slide_status.exists():
        text = slide_status.read_text(encoding="utf-8", errors="ignore")
        current_counts = sorted(set(re.findall(r"current deck:\s*`(\d+)`\s*slides", text, flags=re.IGNORECASE)))
        if len(current_counts) > 1:
            issues.append(
                "tasks/status/slide_deck_overhaul.md contains multiple conflicting current deck counts in one live status surface"
            )
        review_counts = sorted(set(re.findall(r"current review pdf:\s*`(\d+)`\s*paired review pages", text, flags=re.IGNORECASE)))
        if len(review_counts) > 1:
            issues.append(
                "tasks/status/slide_deck_overhaul.md contains multiple conflicting current review-PDF counts in one live status surface"
            )

    robot_status = ROOT / "tasks/status/robot_rope_franka_tabletop_push_hero.md"
    if robot_status.exists():
        text = robot_status.read_text(encoding="utf-8", errors="ignore")
        if "results_meta/tasks/robot_rope_franka_tabletop_push_hero.json" not in text:
            issues.append("robot_rope_franka_tabletop_push_hero status page does not point to its committed registry entry")
        run_id = str((registry_entries.get("robot_rope_franka_tabletop_push_hero", {}).get("authoritative_run") or {}).get("run_id") or "")
        if run_id and run_id not in text:
            issues.append("robot_rope_franka_tabletop_push_hero status page does not mention its current registry run id")

    task_page = ROOT / "docs/bridge/tasks/robot_rope_franka_tabletop_push_hero.md"
    if task_page.exists():
        text = task_page.read_text(encoding="utf-8", errors="ignore")
        if "if this task gains a promoted result" in text:
            issues.append("robot_rope_franka_tabletop_push_hero task page still treats results_meta mirroring as conditional")

    interactive = ROOT / "docs/bridge/tasks/interactive_playground_profiling.md"
    if interactive.exists():
        text = interactive.read_text(encoding="utf-8", errors="ignore")
        if "collision is the largest single hotspot" in text:
            issues.append("interactive_playground_profiling.md still carries stale hotspot language that conflicts with the rope benchmark truth")
        if "results_meta/tasks/rope_perf_apples_to_apples.json" not in text:
            issues.append("interactive_playground_profiling.md must point to rope_perf_apples_to_apples for committed current result meaning")

    for entry in registry_entries.values():
        for rel in entry.get("local_only_surfaces", []):
            path = ROOT / rel
            if not path.exists() or path.suffix.lower() != ".md":
                continue
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
            if "do not use this page as the committed source of truth" not in text and not any(
                marker in text for marker in NONCANONICAL_MARKERS
            ):
                issues.append(f"registry-declared local-only markdown surface lacks an explicit local-only/historical banner: {rel}")
            if "/home/" in text:
                issues.append(f"registry-declared local-only markdown surface still contains machine-local absolute path: {rel}")
    return issues


def _issues_from_archived_task_pages() -> list[str]:
    issues: list[str] = []
    archive_dir = ROOT / "docs/archive/tasks"
    if not archive_dir.exists():
        return issues
    for path in sorted(archive_dir.glob("*.md")):
        if path.name == "README.md":
            continue
        head = "\n".join(path.read_text(encoding="utf-8", errors="ignore").splitlines()[:12]).lower()
        if "> status: historical" not in head and "> status: deprecated" not in head:
            issues.append(f"archived task page lacks historical/deprecated metadata banner: {_relative(path)}")
        if "> status: active" in head:
            issues.append(f"archived task page still looks active: {_relative(path)}")
    return issues


def _issues_from_registry_json(registry_entries: dict[str, dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    robot_entry = registry_entries.get("robot_rope_franka_tabletop_push_hero")
    if robot_entry:
        task_state = str((robot_entry.get("authoritative_run") or {}).get("task_state") or "")
        local_only = set(robot_entry.get("local_only_surfaces", []))
        required = {
            "Newton/phystwin_bridge/results/robot_rope_franka/README.md",
            "Newton/phystwin_bridge/results/robot_rope_franka/manifest.json",
            "Newton/phystwin_bridge/results/robot_rope_franka/BEST_RUN/README.md",
            "Newton/phystwin_bridge/results/robot_rope_franka/BEST_RUN/manifest.json",
        }
        missing = sorted(required - local_only)
        if missing:
            issues.append(
                "robot_rope_franka_tabletop_push_hero registry entry is missing local-only surfaces: "
                + ", ".join(missing)
            )
        if task_state != "historical":
            manifest = ROOT / "Newton/phystwin_bridge/results/robot_rope_franka/manifest.json"
            if manifest.exists():
                obj = json.loads(manifest.read_text(encoding="utf-8"))
                if obj.get("status") == "planned":
                    issues.append("robot_rope_franka root manifest still says planned after promotion")
    return issues


def _collect_issues() -> list[str]:
    issues: list[str] = []
    active_slugs = active_task_slugs()
    registry_entries = _registry_entries()
    fresh_inventory = build_inventory()

    issues.extend(_issues_from_generated_inventory(fresh_inventory))
    issues.extend(_issues_from_root_singletons())
    issues.extend(_issues_from_active_task_chain(active_slugs))
    issues.extend(_issues_from_workflow_requirements(active_slugs))
    issues.extend(_issues_from_task_index(active_slugs))
    issues.extend(_issues_from_doc_task_neighborhood(active_slugs))
    issues.extend(_issues_from_current_status(fresh_inventory, registry_entries))
    issues.extend(_issues_from_metadata(active_slugs, fresh_inventory))
    issues.extend(_issues_from_generator_story())
    issues.extend(_issues_from_reporting_discipline())
    issues.extend(_issues_from_root_allowlist())
    issues.extend(_issues_from_bundle_entry_policy(fresh_inventory))
    issues.extend(_issues_from_authority_surfaces(fresh_inventory, registry_entries))
    issues.extend(_issues_from_archived_task_pages())
    issues.extend(_issues_from_registry_json(registry_entries))

    for row in fresh_inventory:
        if row["classification"] == "ORPHAN":
            issues.append(f"orphan control-plane surface remains indexed as current: {row['path']}")
        if row["classification"] in {"CANONICAL", "ACTIVE_SUPPORTING"} and row["contains_machine_local_paths"]:
            issues.append(f"machine-local absolute path in live control-plane markdown: {row['path']}")
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
