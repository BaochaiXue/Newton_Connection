#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict, deque
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
GENERATED_DIR = ROOT / "docs/generated"
INVENTORY_MD = GENERATED_DIR / "md_inventory.md"
INVENTORY_JSON = GENERATED_DIR / "md_inventory.json"
CLEANUP_REPORT_MD = GENERATED_DIR / "md_cleanup_report.md"
ORPHANS_MD = GENERATED_DIR / "md_orphans.md"
DEPRECATION_MATRIX_MD = GENERATED_DIR / "md_deprecation_matrix.md"

ROOT_CONTROL_FILES = [
    ROOT / "AGENTS.md",
    ROOT / "TODO.md",
    ROOT / "Plan.md",
    ROOT / "Prompt.md",
    ROOT / "Status.md",
    ROOT / "DecisionLog.md",
]
SCAN_DIRS = [
    ROOT / "docs",
    ROOT / "tasks",
    ROOT / "plans",
    ROOT / "results_meta",
]
ROOT_SINGLETONS = {"Plan.md", "Prompt.md", "Status.md", "DecisionLog.md"}
AUTHORITATIVE_RE = re.compile(r"\b(authoritative|current|latest|promoted|best run|final)\b", re.IGNORECASE)
RUN_ID_RE = re.compile(r"\b(?:\d{8}_\d{6}_[A-Za-z0-9_]+|final_self_collision_campaign_\d{8}_\d{6}_[A-Za-z0-9]+)\b")
ABSOLUTE_PATH_RE = re.compile(r"(^|[^A-Za-z])(/home/[^\s`'\"<>()]+)")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+\.md)\)")
META_LINE_RE = re.compile(r"^>\s*([a-z_]+):\s*(.+?)\s*$", re.IGNORECASE)
ACTIVE_LINK_RE = re.compile(r"\[[^\]]+\.md\]\(\./([^)]+\.md)\)")
POINTER_TERMS = ("BEST_RUN.md", "LATEST_SUCCESS.txt", "LATEST_ATTEMPT.txt", "BEST_RUN/")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _parse_front_matter(lines: list[str]) -> dict[str, str]:
    if not lines or lines[0].strip() != "---":
        return {}
    out: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        out[key.strip()] = value.strip().strip("`")
    return out


def _parse_block_meta(lines: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in lines[:14]:
        match = META_LINE_RE.match(line.strip())
        if not match:
            continue
        out[match.group(1).strip()] = match.group(2).strip().strip("`")
    return out


def _parse_metadata(text: str) -> dict[str, str]:
    lines = text.splitlines()
    meta = _parse_front_matter(lines)
    if meta:
        return meta
    return _parse_block_meta(lines)


def _active_task_slugs() -> list[str]:
    readme = ROOT / "docs/bridge/tasks/README.md"
    slugs: list[str] = []
    in_active = False
    for raw in _read(readme).splitlines():
        line = raw.strip()
        if line == "## Active Task Set":
            in_active = True
            continue
        if in_active and line.startswith("## "):
            break
        if not in_active:
            continue
        match = ACTIVE_LINK_RE.search(line)
        if match:
            slug = Path(match.group(1)).stem
            if not slug.startswith("_"):
                slugs.append(slug)
    return slugs


def _scan_markdown_paths() -> list[Path]:
    paths: set[Path] = set()
    for path in ROOT_CONTROL_FILES:
        if path.exists():
            paths.add(path)
    for root in SCAN_DIRS:
        for path in root.rglob("*.md"):
            paths.add(path)
    return sorted(paths)


def _infer_owner(rel_path: str, meta: dict[str, str]) -> str:
    if meta.get("owner_surface"):
        return meta["owner_surface"]
    path = Path(rel_path)
    if rel_path in ("AGENTS.md", "TODO.md"):
        return "repo_harness"
    if rel_path.startswith("docs/generated/"):
        return "generated_control_plane"
    if rel_path.startswith("results_meta/"):
        return "results_registry"
    if len(path.parts) >= 3 and path.parts[:3] == ("docs", "bridge", "tasks"):
        return path.stem
    if len(path.parts) >= 2 and path.parts[0] == "tasks":
        return path.stem
    if len(path.parts) >= 2 and path.parts[:2] in (("plans", "active"), ("plans", "completed")):
        return path.stem
    if path.name == "README.md":
        return f"{path.parent.as_posix()}_readme"
    return path.parent.as_posix().replace("/", "_") or "repo_harness"


def _classify(rel_path: str, text: str, meta: dict[str, str]) -> str:
    status = (meta.get("status") or "").strip().lower()
    if status in {"active", "canonical"}:
        return "canonical"
    if status == "deprecated":
        return "deprecated-pointer"
    if status == "historical":
        return "historical"
    if status == "generated":
        return "generated"
    if rel_path.startswith("docs/generated/") or rel_path in {"results_meta/INDEX.md", "results_meta/LATEST.md"}:
        return "generated"
    if Path(rel_path).name in ROOT_SINGLETONS:
        return "delete-candidate"
    head = "\n".join(text.splitlines()[:16]).lower()
    if "deprecated alias" in head or "deprecated slug" in head:
        return "deprecated-pointer"
    if "historical task family" in head or "historical note" in head or "historical one-off" in head:
        return "historical"
    return "canonical"


def _action_for(classification: str) -> str:
    return {
        "canonical": "KEEP",
        "deprecated-pointer": "STUB",
        "historical": "ARCHIVE",
        "generated": "GENERATED",
        "delete-candidate": "DELETE",
    }[classification]


def _reason_for(classification: str, meta: dict[str, str], rel_path: str) -> str:
    if meta.get("notes"):
        return meta["notes"]
    if classification == "canonical":
        return "Live canonical control-plane surface."
    if classification == "deprecated-pointer":
        return "Deprecated discoverability stub; do not use as source of truth."
    if classification == "historical":
        return "Historical archive surface preserved for traceability."
    if classification == "generated":
        return "Generated or machine-maintained control-plane artifact."
    return "Retired root singleton should be absent or reduced to a stub."


def _canonical_replacement(rel_path: str, meta: dict[str, str]) -> str:
    return (meta.get("canonical_replacement") or "").strip().strip("`")


def _inventory_entries() -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for path in _scan_markdown_paths():
        rel_path = _rel(path)
        text = _read(path)
        meta = _parse_metadata(text)
        classification = _classify(rel_path, text, meta)
        entries.append(
            {
                "path": rel_path,
                "classification": classification,
                "owner_surface": _infer_owner(rel_path, meta),
                "canonical_replacement": _canonical_replacement(rel_path, meta),
                "action": _action_for(classification),
                "reason": _reason_for(classification, meta, rel_path),
                "contains_authoritative_language": bool(AUTHORITATIVE_RE.search(text)),
                "contains_run_ids": bool(RUN_ID_RE.search(text)),
                "contains_machine_local_paths": bool(ABSOLUTE_PATH_RE.search(text)),
            }
        )
    generated_targets = [
        "docs/generated/md_inventory.md",
        "docs/generated/md_cleanup_report.md",
        "docs/generated/md_orphans.md",
        "docs/generated/md_deprecation_matrix.md",
    ]
    known_paths = {entry["path"] for entry in entries}
    for rel_path in generated_targets:
        if rel_path in known_paths:
            continue
        entries.append(
            {
                "path": rel_path,
                "classification": "generated",
                "owner_surface": "markdown_truthfulness_cleanup",
                "canonical_replacement": "python scripts/generate_md_inventory.py",
                "action": "GENERATED",
                "reason": "Generated markdown truthfulness artifact.",
                "contains_authoritative_language": True,
                "contains_run_ids": False,
                "contains_machine_local_paths": False,
            }
        )
    return sorted(entries, key=lambda row: row["path"])


def _resolve_link(src: str, target: str) -> str | None:
    target = target.split("#", 1)[0]
    if not target.endswith(".md"):
        return None
    base = ROOT / src
    resolved = (base.parent / target).resolve()
    try:
        rel = resolved.relative_to(ROOT)
    except ValueError:
        return None
    rel_path = str(rel)
    if not (ROOT / rel_path).exists():
        return None
    return rel_path


def _reachable_paths(entries: list[dict[str, Any]]) -> set[str]:
    existing_paths = {entry["path"] for entry in entries if (ROOT / entry["path"]).exists()}
    seeds = {
        "AGENTS.md",
        "TODO.md",
        "docs/README.md",
        "docs/generated/README.md",
        "docs/generated/harness_audit.md",
        "docs/generated/harness_deprecations.md",
        "docs/runbooks/README.md",
        "docs/bridge/current_status.md",
        "docs/bridge/tasks/README.md",
        "tasks/README.md",
        "plans/README.md",
        "results_meta/README.md",
        "results_meta/INDEX.md",
        "results_meta/LATEST.md",
        "results_meta/DEPRECATED.md",
    }
    for slug in _active_task_slugs():
        for rel_path in (
            f"docs/bridge/tasks/{slug}.md",
            f"tasks/spec/{slug}.md",
            f"plans/active/{slug}.md",
            f"tasks/implement/{slug}.md",
            f"tasks/status/{slug}.md",
        ):
            if (ROOT / rel_path).exists():
                seeds.add(rel_path)
    queue = deque(sorted(path for path in seeds if path in existing_paths))
    visited: set[str] = set()
    while queue:
        rel_path = queue.popleft()
        if rel_path in visited:
            continue
        visited.add(rel_path)
        text = _read(ROOT / rel_path)
        for match in LINK_RE.findall(text):
            resolved = _resolve_link(rel_path, match)
            if resolved and resolved in existing_paths and resolved not in visited:
                queue.append(resolved)
    return visited


def _pointer_warnings(entries: list[dict[str, Any]]) -> list[str]:
    warnings: list[str] = []
    for entry in entries:
        if entry["classification"] != "canonical":
            continue
        path = ROOT / entry["path"]
        if not path.exists():
            continue
        for lineno, raw in enumerate(_read(path).splitlines(), start=1):
            if not any(term in raw for term in POINTER_TERMS):
                continue
            lower = raw.lower()
            if "local-only" in lower or "secondary" in lower or "committed" in lower:
                continue
            warnings.append(f"{entry['path']}:{lineno}")
    return warnings


def _render_inventory_md(entries: list[dict[str, Any]]) -> str:
    lines = [
        "# Markdown Inventory",
        "",
        "> status: generated",
        "> canonical_replacement: `python scripts/generate_md_inventory.py`",
        "> owner_surface: `markdown_truthfulness_cleanup`",
        f"> last_reviewed: `{date.today().isoformat()}`",
        "> notes: Generated control-plane inventory. Regenerate instead of hand-editing.",
        "",
        "| Path | Class | Owner | Replacement | Action | Auth | Run IDs | Abs Paths | Reason |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in entries:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['path']}`",
                    f"`{row['classification']}`",
                    f"`{row['owner_surface']}`",
                    f"`{row['canonical_replacement'] or '-'}`",
                    f"`{row['action']}`",
                    "`yes`" if row["contains_authoritative_language"] else "`no`",
                    "`yes`" if row["contains_run_ids"] else "`no`",
                    "`yes`" if row["contains_machine_local_paths"] else "`no`",
                    row["reason"].replace("|", "\\|"),
                ]
            )
            + " |"
        )
    return "\n".join(lines).rstrip() + "\n"


def _render_cleanup_report(entries: list[dict[str, Any]], reachable: set[str], pointer_warnings: list[str]) -> str:
    counts = Counter(row["classification"] for row in entries)
    root_present = [row["path"] for row in entries if Path(row["path"]).name in ROOT_SINGLETONS]
    orphan_canonical = [
        row["path"] for row in entries if row["classification"] == "canonical" and row["path"] not in reachable
    ]
    abs_path_live = [
        row["path"]
        for row in entries
        if row["classification"] == "canonical" and row["contains_machine_local_paths"]
    ]
    lines = [
        "# Markdown Cleanup Report",
        "",
        "> status: generated",
        "> canonical_replacement: `python scripts/generate_md_inventory.py`",
        "> owner_surface: `markdown_truthfulness_cleanup`",
        f"> last_reviewed: `{date.today().isoformat()}`",
        "> notes: Generated cleanup summary across control-plane Markdown surfaces.",
        "",
        "## Summary",
        "",
        f"- total inventoried markdown surfaces: `{len(entries)}`",
        f"- canonical: `{counts['canonical']}`",
        f"- deprecated pointers: `{counts['deprecated-pointer']}`",
        f"- historical: `{counts['historical']}`",
        f"- generated: `{counts['generated']}`",
        f"- delete-candidate: `{counts['delete-candidate']}`",
        "",
        "## Key Checks",
        "",
        f"- retired root singleton docs present: `{len(root_present)}`",
        f"- canonical markdown surfaces with machine-local paths: `{len(abs_path_live)}`",
        f"- canonical markdown surfaces still orphaned from the control-plane graph: `{len(orphan_canonical)}`",
        f"- canonical markdown lines that still mention local-only pointer surfaces without a qualifier: `{len(pointer_warnings)}`",
        "",
        "## Root Singleton State",
        "",
    ]
    if root_present:
        for rel_path in root_present:
            lines.append(f"- still present: `{rel_path}`")
    else:
        lines.append("- `Plan.md`, `Prompt.md`, `Status.md`, and `DecisionLog.md` are absent from the repo root.")
    lines.extend(
        [
            "",
            "## Remaining Warnings",
            "",
        ]
    )
    remaining = orphan_canonical + abs_path_live + pointer_warnings
    if remaining:
        for item in remaining:
            lines.append(f"- `{item}`")
    else:
        lines.append("- none")
    return "\n".join(lines).rstrip() + "\n"


def _render_orphans(entries: list[dict[str, Any]], reachable: set[str]) -> str:
    unresolved: list[dict[str, Any]] = []
    resolved: list[dict[str, Any]] = []
    for row in entries:
        if row["path"] in reachable:
            continue
        if row["classification"] == "canonical":
            unresolved.append(row)
        else:
            resolved.append(row)
    lines = [
        "# Markdown Orphans",
        "",
        "> status: generated",
        "> canonical_replacement: `python scripts/generate_md_inventory.py`",
        "> owner_surface: `markdown_truthfulness_cleanup`",
        f"> last_reviewed: `{date.today().isoformat()}`",
        "> notes: Generated orphan report for control-plane Markdown surfaces.",
        "",
        "## Unresolved Canonical Orphans",
        "",
    ]
    if unresolved:
        for row in unresolved:
            lines.append(f"- `{row['path']}`")
    else:
        lines.append("- none")
    lines.extend(["", "## Classified Non-Canonical Orphans", ""])
    if resolved:
        for row in resolved:
            lines.append(
                f"- `{row['path']}` -> `{row['classification']}` via `{row['action']}` (`{row['canonical_replacement'] or 'none'}`)"
            )
    else:
        lines.append("- none")
    return "\n".join(lines).rstrip() + "\n"


def _render_deprecation_matrix(entries: list[dict[str, Any]]) -> str:
    rows = [
        row for row in entries if row["classification"] in {"deprecated-pointer", "historical"}
    ]
    lines = [
        "# Markdown Deprecation Matrix",
        "",
        "> status: generated",
        "> canonical_replacement: `python scripts/generate_md_inventory.py`",
        "> owner_surface: `markdown_truthfulness_cleanup`",
        f"> last_reviewed: `{date.today().isoformat()}`",
        "> notes: Generated matrix of deprecated and historical control-plane Markdown surfaces.",
        "",
        "| Path | Class | Replacement | Action | Reason |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['path']}`",
                    f"`{row['classification']}`",
                    f"`{row['canonical_replacement'] or 'none'}`",
                    f"`{row['action']}`",
                    row["reason"].replace("|", "\\|"),
                ]
            )
            + " |"
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    entries = _inventory_entries()
    reachable = _reachable_paths(entries)
    pointer_warnings = _pointer_warnings(entries)
    inventory_payload = {
        "generated_at": date.today().isoformat(),
        "entries": entries,
    }
    INVENTORY_JSON.write_text(json.dumps(inventory_payload, indent=2) + "\n", encoding="utf-8")
    INVENTORY_MD.write_text(_render_inventory_md(entries), encoding="utf-8")
    CLEANUP_REPORT_MD.write_text(_render_cleanup_report(entries, reachable, pointer_warnings), encoding="utf-8")
    ORPHANS_MD.write_text(_render_orphans(entries, reachable), encoding="utf-8")
    DEPRECATION_MATRIX_MD.write_text(_render_deprecation_matrix(entries), encoding="utf-8")
    print(f"Wrote {_rel(INVENTORY_MD)}")
    print(f"Wrote {_rel(INVENTORY_JSON)}")
    print(f"Wrote {_rel(CLEANUP_REPORT_MD)}")
    print(f"Wrote {_rel(ORPHANS_MD)}")
    print(f"Wrote {_rel(DEPRECATION_MATRIX_MD)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
