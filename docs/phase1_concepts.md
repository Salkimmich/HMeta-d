# Phase 1 Concepts: SDT Core as Pure Functions

## MATLAB baseline behavior

MATLAB computes padded counts, cumulative type-1 HR/FAR, then derives `d1` and `c1` with `norminv` in `fit_meta_d_mcmc.m`. The steps are imperative and live inline in one procedure.

## Python translation and concept introduced

Python splits the same behavior into named functions (`pad_counts`, `compute_rates`, `compute_dprime`, `compute_criterion`, `prepare_sdt_data`). This introduces composable data pipelines and immutable return objects (`SDTData` dataclass).

## Clojure translation and what it adds

Clojure keeps the same math but expresses it as pure functions over vectors/maps (`pad-counts`, `compute-rates`, `prepare-sdt-data`). It adds declarative sequence operations and first-class immutable maps.

## Before/after code snippet (MATLAB vs Clojure)

MATLAB:

```matlab
ratingHR(end+1) = sum(nR_S2_adj(c:end)) / sum(nR_S2_adj);
ratingFAR(end+1) = sum(nR_S1_adj(c:end)) / sum(nR_S1_adj);
d1 = norminv(HR) - norminv(FAR);
```

Clojure:

```clojure
(let [rating-hr (mapv (fn [c] (/ (reduce + (subvec nR-S2-adj c n)) total-s2)) idxs)
      rating-far (mapv (fn [c] (/ (reduce + (subvec nR-S1-adj c n)) total-s1)) idxs)]
  (- (normal-ppf hit-rate) (normal-ppf fa-rate)))
```

## Tests that validate the concept

- `python/test_phase1_sdt.py` checks reference `d1`/`c1`.
- `test/hmeta_d/sdt_test.clj` checks Clojure output against the same reference values.
