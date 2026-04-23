# Validation Guide

This document states what each validation gate proves and how to run it.

## Local Gate (same intent as CI)

- Windows: `powershell -ExecutionPolicy Bypass -File .\scripts\validate.ps1`
- macOS/Linux: `bash ./scripts/validate.sh`

Both scripts run:

1. Python dependency install from `python/requirements-lock.txt`
2. Phase 1 pytest (`python/test_phase1_sdt.py`)
3. Phase 2 pytest (`python/test_phase2_sampler.py`)
4. Phase 3 pytest (`python/test_phase3_hierarchical.py`)
5. Clojure suite via Docker (`clojure -M:test`)

## CI Gates

- Workflow: `.github/workflows/ci.yml`
- Python job validates Phase 1-3 tests on Python 3.12.
- Clojure job validates `:test` alias via Docker image `clojure:temurin-21-tools-deps`.

## What Is Proven

- Phase 1: SDT preparation and reference-value checks for type-1 metrics.
- Phase 2: Type-2 likelihood behavior and sampling invariants (including seeded determinism within language).
- Phase 3: Hierarchical model structure, non-destructive updates, and serialization behavior.
- Deterministic posterior-summary regression checks:
  - Phase 2 chain summaries are compared to `docs/fixtures/posterior_summary_fixture.json`.
  - Phase 3 group-chain summaries are compared to the same fixture.

## Tolerance Policy

Numerical tolerance and parity guidance is defined in `docs/math_chain.md`.
Use those tolerances for cross-language comparison claims.
Posterior-summary regression tolerances are fixture-local and intentionally small (`0.05`) to catch behavioral drift while allowing expected floating-point variation.

## Current Limits

- CI does not claim byte-identical chain trajectories across languages.
- Cross-language equivalence is expressed as tolerance-bounded metric agreement.

## Dependency Reproducibility

- `python/requirements.txt`: minimum compatible versions for development.
- `python/requirements-lock.txt`: pinned baseline used by CI and validation scripts.
