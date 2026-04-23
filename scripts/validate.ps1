$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path "$PSScriptRoot\..").Path
$requireClojureGate = $env:HMD_REQUIRE_CLOJURE_GATE -eq "1"

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
  $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
  if ($pyLauncher) {
    $pythonExe = "py -3"
  } else {
    throw "Python executable not found. Install Python or add it to PATH."
  }
} else {
  $pythonExe = "python"
}

Write-Host "==> Python dependency install"
Push-Location (Join-Path $repoRoot "python")
Invoke-Expression "$pythonExe -m pip install -r requirements-lock.txt"

Write-Host "==> Python Phase 1 tests"
Invoke-Expression "$pythonExe -m pytest test_phase1_sdt.py -v"

Write-Host "==> Python Phase 2 tests"
Invoke-Expression "$pythonExe -m pytest test_phase2_sampler.py -v"

Write-Host "==> Python Phase 3 tests"
Invoke-Expression "$pythonExe -m pytest test_phase3_hierarchical.py -v"
Pop-Location

Write-Host "==> Clojure tests via Docker"
Push-Location $repoRoot
$dockerCmd = Get-Command docker -ErrorAction SilentlyContinue
$clojureCmd = Get-Command clojure -ErrorAction SilentlyContinue
$ranClojureGate = $false

if ($dockerCmd) {
  $dockerHealthy = $false
  try {
    docker info *> $null
    $dockerHealthy = ($LASTEXITCODE -eq 0)
  } catch {
    $dockerHealthy = $false
  }

  if ($dockerHealthy) {
    Write-Host "==> Running Clojure tests in Docker"
    docker run --rm -v "${PWD}:/work" -w /work clojure:temurin-21-tools-deps clojure -M:test
    $ranClojureGate = $true
  } else {
    Write-Warning "Docker CLI is installed but daemon is unavailable."
  }
} else {
  Write-Warning "Docker CLI not found on PATH."
}

if (-not $ranClojureGate -and $clojureCmd) {
  Write-Host "==> Falling back to local Clojure CLI"
  clojure -M:test
  $ranClojureGate = $true
}

if (-not $ranClojureGate) {
  $msg = "Skipped Clojure test gate: neither a healthy Docker daemon nor local Clojure CLI is available."
  if ($requireClojureGate) {
    throw $msg
  }
  Write-Warning "$msg Set HMD_REQUIRE_CLOJURE_GATE=1 to enforce failure instead of skip."
}
Pop-Location

Write-Host "Validation complete."
