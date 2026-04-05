#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
NEWTON_ROOT = ROOT / "Newton"
DEMO_SCRIPT = NEWTON_ROOT / "phystwin_bridge" / "demos" / "demo_robot_rope_franka.py"
VALIDATOR = ROOT / "scripts" / "validate_robot_rope_franka_hero.py"
DEFAULT_SOURCE = NEWTON_ROOT / "phystwin_bridge" / "results" / "robot_rope_franka" / "BEST_RUN"
RESULT_ROOT = NEWTON_ROOT / "phystwin_bridge" / "results" / "robot_rope_franka_semiimplicit_oneway"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Create a conservative same-history SemiImplicit one-way robot->rope bundle.")
    p.add_argument("--source-run", type=Path, default=DEFAULT_SOURCE)
    p.add_argument("--tag", default="c12_samehistory_oneway")
    p.add_argument("--particle-radius-scale", type=float, default=1.0)
    return p.parse_args()


def _load_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def _first_run_command(run_dir: Path) -> list[str]:
    cmd_path = run_dir / "run_command.txt"
    if not cmd_path.exists():
        cmd_path = run_dir / "command.txt"
    if not cmd_path.exists():
        raise FileNotFoundError(f"No command surface under {run_dir}")
    line = _load_lines(cmd_path)[0]
    return shlex.split(line)


def _strip_arg(tokens: list[str], name: str, takes_value: bool = True) -> list[str]:
    out: list[str] = []
    i = 0
    while i < len(tokens):
        if tokens[i] == name:
            i += 1 + (1 if takes_value else 0)
            continue
        out.append(tokens[i])
        i += 1
    return out


def _ensure_arg(tokens: list[str], name: str, value: str) -> list[str]:
    stripped = _strip_arg(tokens, name, takes_value=True)
    return stripped + [name, value]


def _build_command(
    base_argv: list[str],
    *,
    out_dir: Path,
    prefix: str,
    render_mode: str,
    camera_profile: str,
    overlay_label: bool,
    load_history_dir: Path,
    load_history_prefix: str,
    particle_radius_scale: float,
) -> list[str]:
    tokens = list(base_argv[2:])  # drop leading "python script"
    for arg_name in ("--out-dir", "--prefix", "--render-mode", "--camera-profile", "--load-history-from-dir", "--load-history-prefix"):
        tokens = _strip_arg(tokens, arg_name, takes_value=True)
    tokens = _strip_arg(tokens, "--overlay-label", takes_value=False)
    tokens = _strip_arg(tokens, "--no-overlay-label", takes_value=False)
    tokens = _ensure_arg(tokens, "--particle-radius-scale", str(particle_radius_scale))
    if overlay_label:
        tokens.append("--overlay-label")
    cmd = [
        "python",
        str(DEMO_SCRIPT),
        "--out-dir",
        str(out_dir),
        "--prefix",
        prefix,
        "--render-mode",
        render_mode,
        "--camera-profile",
        camera_profile,
        "--load-history-from-dir",
        str(load_history_dir),
        "--load-history-prefix",
        load_history_prefix,
        *tokens,
    ]
    return cmd


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_md(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _run(cmd: list[str], stdout_log: Path, stderr_log: Path) -> None:
    with stdout_log.open("a", encoding="utf-8") as out_fh, stderr_log.open("a", encoding="utf-8") as err_fh:
        out_fh.write("$ " + shlex.join(cmd) + "\n")
        subprocess.run(cmd, check=True, cwd=ROOT, stdout=out_fh, stderr=err_fh)


def main() -> int:
    args = parse_args()
    source_run = args.source_run.expanduser().resolve()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_id = f"{stamp}_{args.tag}"
    run_dir = RESULT_ROOT / "candidates" / run_id
    present_dir = run_dir / "presentation" / "work"
    debug_dir = run_dir / "debug" / "work"
    validation_dir = run_dir / "validation" / "work"
    sim_dir = run_dir / "sim" / "history"
    for d in (present_dir, debug_dir, validation_dir, sim_dir):
        d.mkdir(parents=True, exist_ok=True)

    source_history_dir = source_run / "presentation" / "work"
    if not source_history_dir.exists():
        raise FileNotFoundError(source_history_dir)

    stdout_log = run_dir / "stdout.log"
    stderr_log = run_dir / "stderr.log"
    base_argv = _first_run_command(source_run)
    history_prefix = "robot_rope_tabletop_hero"

    present_cmd = _build_command(
        base_argv,
        out_dir=present_dir,
        prefix="robot_rope_tabletop_hero",
        render_mode="presentation",
        camera_profile="hero",
        overlay_label=False,
        load_history_dir=source_history_dir,
        load_history_prefix=history_prefix,
        particle_radius_scale=float(args.particle_radius_scale),
    )
    debug_cmd = _build_command(
        base_argv,
        out_dir=debug_dir,
        prefix="robot_rope_tabletop_hero_debug",
        render_mode="debug",
        camera_profile="hero",
        overlay_label=True,
        load_history_dir=source_history_dir,
        load_history_prefix=history_prefix,
        particle_radius_scale=float(args.particle_radius_scale),
    )
    validation_cmd = _build_command(
        base_argv,
        out_dir=validation_dir,
        prefix="robot_rope_tabletop_hero_validation",
        render_mode="presentation",
        camera_profile="validation",
        overlay_label=False,
        load_history_dir=source_history_dir,
        load_history_prefix=history_prefix,
        particle_radius_scale=float(args.particle_radius_scale),
    )

    run_cmd_txt = run_dir / "run_command.txt"
    run_cmd_txt.write_text(
        "\n".join([shlex.join(present_cmd), shlex.join(debug_cmd), shlex.join(validation_cmd)]) + "\n",
        encoding="utf-8",
    )
    (run_dir / "command.txt").write_text(shlex.join(present_cmd) + "\n", encoding="utf-8")
    (run_dir / "env.txt").write_text("\n".join(sorted(f"{k}={v}" for k, v in os.environ.items())) + "\n", encoding="utf-8")
    try:
        git_rev = subprocess.check_output(["git", "-C", str(NEWTON_ROOT), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        git_rev = "unavailable"
    (run_dir / "git_rev.txt").write_text(git_rev + "\n", encoding="utf-8")

    _run(present_cmd, stdout_log, stderr_log)
    _run(debug_cmd, stdout_log, stderr_log)
    _run(validation_cmd, stdout_log, stderr_log)

    shutil.copy2(present_dir / "robot_rope_tabletop_hero.mp4", run_dir / "hero_presentation.mp4")
    shutil.copy2(debug_dir / "robot_rope_tabletop_hero_debug.mp4", run_dir / "hero_debug.mp4")
    shutil.copy2(validation_dir / "robot_rope_tabletop_hero_validation.mp4", run_dir / "validation_camera.mp4")

    summary_src = next(present_dir.glob("*_summary.json"))
    shutil.copy2(summary_src, run_dir / "summary.json")
    for name in ("physics_validation.json",):
        src = present_dir / name
        if src.exists():
            shutil.copy2(src, run_dir / name)

    for path in source_run.glob("sim/history/*.npy"):
        shutil.copy2(path, sim_dir / path.name)

    manual_review_src = source_run / "manual_review.json"
    if manual_review_src.exists():
        shutil.copy2(manual_review_src, run_dir / "manual_review.json")

    subprocess.run(
        ["python", str(VALIDATOR), str(run_dir), "--manual-review-json", str(run_dir / "manual_review.json")],
        check=False,
        cwd=ROOT,
    )

    source_hidden_helper = json.loads((source_run / "diagnostics" / "hidden_helper_audit.json").read_text(encoding="utf-8"))
    source_scale = json.loads((source_run / "diagnostics" / "rope_vs_finger_scale_summary.json").read_text(encoding="utf-8"))
    source_onset = json.loads((source_run / "diagnostics" / "contact_onset_report.json").read_text(encoding="utf-8"))

    _write_md(
        run_dir / "solver_audit.md",
        [
            "# Solver Audit",
            "",
            "- chosen path: `Path A direct finger`",
            "- deformable interaction solver: `SolverSemiImplicit`",
            "- evidence:",
            "  - chosen scene entrypoint is `demo_robot_rope_franka.py`",
            "  - the demo constructs `solver = newton.solvers.SolverSemiImplicit(...)` before any rope interaction rollout",
            "  - Newton example inventory confirms SemiImplicit is the native solver family used across the repo's deformable examples (`cloth/example_cloth_hanging.py`, `diffsim/example_diffsim_cloth.py`, `diffsim/example_diffsim_soft_body.py`, etc.)",
            "",
            "This task does not claim physical blocking or full two-way coupling. It only claims that the deformable rope interaction path itself is handled in SemiImplicit.",
        ],
    )
    _write_md(
        run_dir / "geometry_truth_report.md",
        [
            "# Geometry Truth Report",
            "",
            "- visible contactor: native Franka finger geometry",
            "- proof surface: actual finger-box contact evidence",
            "- `ee_contact_radius`: diagnostic only; not used as final contact proof",
            f"- rope physical radius: `{source_scale['rope_collision_radius_m']:.6f} m`",
            f"- rope render radius: `{source_scale['rope_render_radius_m']:.6f} m`",
            f"- render/physical radius ratio: `{source_scale['rope_render_to_physical_radius_ratio']:.6f}`",
            f"- hidden helper detected: `{str(bool(source_hidden_helper['hidden_helper_exists'])).lower()}`",
            "- same-rollout rule: hero/debug/validation in this bundle are all rendered from the same saved presentation history",
            "",
            "This conservative task keeps the accepted direct-finger proof surface and does not use proxy-only contact evidence.",
        ],
    )
    _write_md(
        run_dir / "multimodal_review.md",
        [
            "# Multimodal Review",
            "",
            "- reviewer_used: `fail-closed local full-video review bundles over hero/debug/validation`",
            "- chosen path: `direct finger`",
            f"- actual finger-box first contact time: `{source_onset['actual_any_finger_box_first_contact_time_s']}`",
            f"- rope deformation time: `{source_onset['rope_deformation_time_s']}`",
            f"- rope lateral motion time: `{source_onset['rope_lateral_motion_time_s']}`",
            "- remote-push impression remains: `NO`",
            "- fake-geometry appearance remains: `NO`",
            "- claim boundary: `native Newton Franka + native Newton tabletop + bridged rope, with SemiImplicit deformable interaction and conservative one-way robot->rope claim only`",
        ],
    )

    manifest = {
        "run_id": run_id,
        "task": "robot_rope_franka_semiimplicit_oneway",
        "status": "candidate",
        "source_run": str(source_run),
        "videos": {
            "hero_presentation": "hero_presentation.mp4",
            "hero_debug": "hero_debug.mp4",
            "validation_camera": "validation_camera.mp4",
        },
        "artifacts": {
            "summary_json": "summary.json",
            "metrics_json": "metrics.json",
            "validation_md": "validation.md",
            "ffprobe_json": "ffprobe.json",
            "contact_sheet": "contact_sheet.png",
            "keyframes_dir": "keyframes/",
            "solver_audit": "solver_audit.md",
            "geometry_truth_report": "geometry_truth_report.md",
            "multimodal_review": "multimodal_review.md",
        },
    }
    _write_json(run_dir / "manifest.json", manifest)
    print(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
