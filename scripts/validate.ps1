$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path "$PSScriptRoot\..").Path

Write-Host "==> Python dependency install"
Push-Location (Join-Path $repoRoot "python")
pip install -r requirements-lock.txt

Write-Host "==> Python Phase 1 tests"
python -m pytest test_phase1_sdt.py -v

Write-Host "==> Python Phase 2 tests"
python -m pytest test_phase2_sampler.py -v

Write-Host "==> Python Phase 3 tests"
python -m pytest test_phase3_hierarchical.py -v
Pop-Location

Write-Host "==> Clojure tests via Docker"
Push-Location $repoRoot
docker run --rm -v "${PWD}:/work" -w /work clojure:temurin-21-tools-deps clojure -M:test
Pop-Location

Write-Host "Validation complete."
