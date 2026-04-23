#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "==> Python dependency install"
pushd "${REPO_ROOT}/python" >/dev/null
pip install -r requirements-lock.txt

echo "==> Python Phase 1 tests"
python -m pytest test_phase1_sdt.py -v

echo "==> Python Phase 2 tests"
python -m pytest test_phase2_sampler.py -v

echo "==> Python Phase 3 tests"
python -m pytest test_phase3_hierarchical.py -v
popd >/dev/null

echo "==> Clojure tests via Docker"
pushd "${REPO_ROOT}" >/dev/null
docker run --rm -v "$PWD":/work -w /work clojure:temurin-21-tools-deps clojure -M:test
popd >/dev/null

echo "Validation complete."
