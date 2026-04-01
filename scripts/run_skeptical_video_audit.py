#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run a fail-closed skeptical audit over a prepared video review bundle.")
    p.add_argument("--review-bundle", type=Path, required=True, help="Directory containing review_manifest.json")
    claim = p.add_mutually_exclusive_group(required=True)
    claim.add_argument("--claim", type=str)
    claim.add_argument("--claim-file", type=Path)
    p.add_argument("--manual-review-json", type=Path, default=None)
    p.add_argument("--motion-density-min", type=float, default=0.35)
    p.add_argument("--repeat-transition-max", type=float, default=0.60)
    p.add_argument("--max-static-run-fraction", type=float, default=0.50)
    return p.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_md(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Skeptical Video Audit",
        "",
        f"- verdict: `{payload['verdict']}`",
        f"- claim boundary: {payload['claim_boundary']}",
        "",
        "## Hard-Fail Reasons",
    ]
    if payload["hard_fail_reasons"]:
        for item in payload["hard_fail_reasons"]:
            lines.append(f"- {item}")
    else:
        lines.append("- none")
    lines.extend(["", "## Evidence"])
    for item in payload["evidence"]:
        lines.extend(
            [
                f"- timestamp: `{item['timestamp_s']}`",
                f"  - frame index: `{item['frame_index']}`",
                f"  - frame path: `{item['frame_path']}`",
                f"  - observation: {item['observation']}",
                f"  - supports claim: `{item['supports_claim']}`",
            ]
        )
    lines.extend(["", "## Missing Or Ambiguous"])
    if payload["missing_or_ambiguous"]:
        for item in payload["missing_or_ambiguous"]:
            lines.append(f"- {item}")
    else:
        lines.append("- none")
    lines.extend(["", "## Summary", "", payload["summary"]])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    review_dir = args.review_bundle.expanduser().resolve()
    manifest = _load_json(review_dir / "review_manifest.json")
    claim_boundary = args.claim if args.claim is not None else args.claim_file.expanduser().resolve().read_text(encoding="utf-8").strip()
    hard_fail_reasons: list[str] = []
    missing_or_ambiguous: list[str] = []

    required_assets = manifest.get("required_assets_present") or {}
    for key, present in required_assets.items():
        if not present:
            hard_fail_reasons.append(f"missing required review-bundle asset: {key}")

    if float(manifest.get("black_frame_fraction", 0.0)) > 0.0:
        hard_fail_reasons.append("review bundle includes black/blank sampled frames")
    if float(manifest.get("motion_density", 0.0)) < float(args.motion_density_min):
        hard_fail_reasons.append("sampled transitions are too static for conservative acceptance")
    if float(manifest.get("repeat_transition_fraction", 0.0)) > float(args.repeat_transition_max):
        hard_fail_reasons.append("too many repeated/static sampled transitions")
    if float(manifest.get("max_static_run_fraction", 0.0)) > float(args.max_static_run_fraction):
        hard_fail_reasons.append("one long static run dominates the sampled transitions")
    if not manifest.get("windows"):
        hard_fail_reasons.append("no consecutive-frame windows were prepared")

    evidence: list[dict[str, Any]] = []
    sampled = manifest.get("sampled_frames") or []
    if sampled:
        first = sampled[0]
        evidence.append(
            {
                "timestamp_s": first.get("timestamp_s", 0.0),
                "frame_index": first.get("frame_index", 0),
                "frame_path": first.get("frame_path", ""),
                "observation": "Review bundle contains evenly sampled frames across the video.",
                "supports_claim": False if hard_fail_reasons else True,
            }
        )
    else:
        missing_or_ambiguous.append("no sampled frames recorded in review_manifest.json")

    manual_review = None
    if args.manual_review_json is not None and args.manual_review_json.exists():
        manual_review = _load_json(args.manual_review_json.expanduser().resolve())
    else:
        missing_or_ambiguous.append(
            "no separate manual skeptical review JSON was provided; fail closed until a reviewer cites timestamps and frames"
        )

    verdict = "FAIL"
    if not hard_fail_reasons and manual_review is not None:
        if str(manual_review.get("verdict", "")).upper() == "PASS" and manual_review.get("evidence"):
            verdict = "PASS"
            for item in manual_review.get("evidence", []):
                evidence.append(
                    {
                        "timestamp_s": item.get("timestamp_s"),
                        "frame_index": item.get("frame_index"),
                        "frame_path": item.get("frame_path"),
                        "observation": item.get("observation", ""),
                        "supports_claim": bool(item.get("supports_claim", True)),
                    }
                )
        else:
            hard_fail_reasons.append("manual skeptical review did not explicitly support PASS")

    summary = (
        "FAIL closed. Either a hard-fail criterion triggered or no separate skeptical reviewer supplied a defensible PASS."
        if verdict != "PASS"
        else "PASS. No hard-fail criterion triggered and the separate skeptical review supplied explicit timestamped evidence."
    )
    payload = {
        "verdict": verdict,
        "claim_boundary": claim_boundary,
        "hard_fail_reasons": hard_fail_reasons,
        "evidence": evidence,
        "missing_or_ambiguous": missing_or_ambiguous,
        "summary": summary,
    }
    json_path = review_dir / "skeptical_audit.json"
    md_path = review_dir / "skeptical_audit.md"
    _write_json(json_path, payload)
    _write_md(md_path, payload)
    print(json_path)
    print(md_path)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
