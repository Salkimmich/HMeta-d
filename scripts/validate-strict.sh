#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

HMD_REQUIRE_CLOJURE_GATE=1 bash "${SCRIPT_DIR}/validate.sh"
