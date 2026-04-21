# Phase 2 Concepts: Likelihood + Explicit MCMC State

## MATLAB baseline behavior

MATLAB delegates MCMC to JAGS and computes type-2 equation components inside `fit_meta_d_mcmc.m` with procedural loops (`est_FAR2_*`, `est_HR2_*`).

## Python translation and concept introduced

Python implements explicit `estimate_type2_rates`, `log_likelihood`, and `mh_chain`. This introduces visible MCMC state transitions (propose/evaluate/accept) and inspectable posterior logic.

## Clojure translation and what it adds

Clojure implements the same equations with pure functions over maps (`estimate-type2-rates`, `log-likelihood`, `mh-chain`). It adds immutable state passing and sequence-based chain construction.

## Before/after code snippet (MATLAB vs Clojure)

MATLAB:

```matlab
est_FAR2_rS2(i) = I_FAR_area_rS2 / I_area_rS2;
est_HR2_rS2(i)  = C_HR_area_rS2 / C_area_rS2;
```

Clojure:

```clojure
(-> acc
    (update :far-s2 conj (/ i-far-area-rs2 i-area-rs2))
    (update :hr-s2 conj (/ c-hr-area-rs2 c-area-rs2)))
```

## Tests that validate the concept

- `python/test_phase2_sampler.py` validates type-2 ranges, finite likelihood, invalid parameter rejection, and seeded determinism.
- `test/hmeta_d/sampler_test.clj` validates shape/range, likelihood behavior, and chain length.
