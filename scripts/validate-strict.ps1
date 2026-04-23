$ErrorActionPreference = "Stop"

$env:HMD_REQUIRE_CLOJURE_GATE = "1"
$scriptPath = Join-Path $PSScriptRoot "validate.ps1"

powershell -NoProfile -ExecutionPolicy Bypass -File $scriptPath
