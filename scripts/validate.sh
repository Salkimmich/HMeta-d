#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
REQUIRE_CLOJURE_GATE="${HMD_REQUIRE_CLOJURE_GATE:-0}"

if command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
else
  echo "ERROR: Python executable not found (python/python3)." >&2
  exit 1
fi

echo "==> Python dependency install"
pushd "${REPO_ROOT}/python" >/dev/null
"${PYTHON_BIN}" -m pip install -r requirements-lock.txt

echo "==> Python Phase 1 tests"
"${PYTHON_BIN}" -m pytest test_phase1_sdt.py -v

echo "==> Python Phase 2 tests"
"${PYTHON_BIN}" -m pytest test_phase2_sampler.py -v

echo "==> Python Phase 3 tests"
"${PYTHON_BIN}" -m pytest test_phase3_hierarchical.py -v
popd >/dev/null

echo "==> Clojure tests via Docker"
pushd "${REPO_ROOT}" >/dev/null
ran_clojure_gate=0

if command -v docker >/dev/null 2>&1; then
  if docker info >/dev/null 2>&1; then
    echo "==> Running Clojure tests in Docker"
    docker run --rm -v "$PWD":/work -w /work clojure:temurin-21-tools-deps clojure -M:test
    ran_clojure_gate=1
  else
    echo "WARN: Docker CLI is installed but daemon is unavailable." >&2
  fi
else
  echo "WARN: Docker CLI not found on PATH." >&2
fi

if [[ ${ran_clojure_gate} -eq 0 ]] && command -v clojure >/dev/null 2>&1; then
  echo "==> Falling back to local Clojure CLI"
  clojure -M:test
  ran_clojure_gate=1
fi

if [[ ${ran_clojure_gate} -eq 0 ]]; then
  msg="Skipped Clojure test gate: neither a healthy Docker daemon nor local Clojure CLI is available."
  if [[ "${REQUIRE_CLOJURE_GATE}" == "1" ]]; then
    echo "ERROR: ${msg}" >&2
    exit 1
  fi
  echo "WARN: ${msg} Set HMD_REQUIRE_CLOJURE_GATE=1 to enforce failure instead of skip." >&2
fi
popd >/dev/null

echo "Validation complete."
