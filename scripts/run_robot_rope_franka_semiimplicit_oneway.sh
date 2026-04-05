#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE_WRAPPER="${ROOT}/scripts/run_robot_rope_franka_tabletop_hero.sh"

echo "[run_robot_rope_franka_semiimplicit_oneway] conservative rerun path"
echo "[run_robot_rope_franka_semiimplicit_oneway] deformable rope interaction is handled by SolverSemiImplicit in Newton/phystwin_bridge/demos/demo_robot_rope_franka.py"
echo "[run_robot_rope_franka_semiimplicit_oneway] claim boundary stays one-way robot->rope only; no physical-blocking or full two-way claim"

exec bash "${BASE_WRAPPER}" "$@"
