# Session 1 Open Questions - Resolved

This note captures the three blockers identified before Session 2, along with the decisions to use going forward.

## 1) Fastmath inverse normal CDF function

- `fastmath.stats/normal-inverse-cdf` was not confirmed as a valid public function in fastmath 2.x.
- `fastmath.core/normal-ppf` was also not confirmed as a valid public function in fastmath 2.x.
- Use `fastmath.random/icdf` with `fastmath.random/default-normal` for inverse normal CDF behavior equivalent to `scipy.stats.norm.ppf`.

Recommended Clojure call:

```clojure
(require '[fastmath.random :as r])
(r/icdf r/default-normal 0.841) ; approximately 1.0
```

## 2) Type 2 probability equations for Phase 2 likelihood

- Treat the equations in `Matlab/fit_meta_d_mcmc.m` as canonical for translation.
- Specifically, transcribe the CDF-based `est_FAR2_*` and `est_HR2_*` calculations in the "find estimated t2FAR and t2HR" block.
- This avoids drift from informal re-derivations and keeps Python/Clojure behavior aligned to the MATLAB reference.

## 3) Cross-language seeding strategy for sampler tests

- Do not require Python and Clojure chains to match sample-by-sample.
- Use deterministic seeding within each language for reproducibility.
- Compare value-level outcomes across languages (posterior means/intervals within tolerance), not exact chain trajectories.

## Session 2 guardrails

- Use the fastmath inverse CDF call above in `src/hmeta_d/sdt.clj`.
- Keep Phase 2 equations source-aligned with the MATLAB implementation.
- Write tests to assert statistical agreement, not RNG stream identity.
