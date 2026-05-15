#!/bin/bash
# =====================================================
# PQC-IoT Research — Run All Experiments in Sequence
# =====================================================
set -e
BASE="$(cd "$(dirname "$0")" && pwd)"
PASS=0
FAIL=0

run_exp() {
    local name=$1
    local script=$2
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Running: $name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if bash "$script"; then
        echo "  ✅ $name: PASSED"
        ((PASS++))
    else
        echo "  ❌ $name: FAILED"
        ((FAIL++))
    fi
}

run_exp "EXP01 Baseline"        "$BASE/experiments/exp01_baseline/run.sh"
# Uncomment as you add experiments:
run_exp "EXP02 PQC Stubs" "$BASE/experiments/exp02_pqc_stubs/run.sh"
# run_exp "EXP03 Star Topology" "$BASE/experiments/exp03_star_topology/run.sh"
# run_exp "EXP04 Mesh Topology" "$BASE/experiments/exp04_mesh_topology/run.sh"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  SUMMARY: $PASS passed, $FAIL failed"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
[ $FAIL -eq 0 ] && exit 0 || exit 1
