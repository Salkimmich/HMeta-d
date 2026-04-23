# Phase 3 Completion Release Notes

## Summary

This release completes the MATLAB -> Python -> Clojure teaching translation through Phase 3, where the hierarchical group model is represented as first-class data structures rather than an opaque external JAGS model file.

## Included Work

- Phase 2 sampler and likelihood implementations in Python and Clojure.
- Phase 3 hierarchical model implementations:
  - Python: dataclass-based model specification.
  - Clojure: EDN map-based model specification.
- Cross-language concept documentation:
  - `docs/phase1_concepts.md`
  - `docs/phase2_concepts.md`
  - `docs/phase3_concepts.md`
  - `docs/math_chain.md`
- CI hardening:
  - Python Phase 1 + 2 + 3 tests in GitHub Actions.
  - Clojure tests executed via Docker in GitHub Actions.

## Validation

- Local Python tests for Phases 1, 2, and 3 pass.
- Remote CI passes for:
  - Python Phase 1 + 2 + 3
  - Clojure Docker test suite

## Teaching Outcome

The repository now demonstrates a full progression:

1. SDT computation as pure functions.
2. Explicit likelihood + MCMC state transitions.
3. Hierarchical model as transformable data.
