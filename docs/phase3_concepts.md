# Phase 3 Concepts: Hierarchical Model as Data

## MATLAB baseline behavior

In MATLAB, the group model lives in a JAGS `.bugs` file referenced by `fit_meta_d_mcmc_group.m`. It is external text, not a runtime value you can transform in normal MATLAB code.

## Python translation and concept introduced

Python turns the group model into dataclasses (`Prior`, `HierarchicalModel`) in `phase3_hierarchical.py`. This introduces inspectable model configuration and non-destructive modifications with `dataclasses.replace`.

## Clojure translation and what it adds

Clojure represents the full model as a plain map (`hmeta-d-group-model`) in `hierarchical.clj`. It adds direct structural transformations with `assoc-in` and EDN round-tripping without custom serializers.

## Before/after code snippet (MATLAB vs Clojure)

MATLAB:

```matlab
mu_logMratio ~ dnorm(0, 1)
sigma_logMratio ~ dnorm(0, 1)T(0,)
```

Clojure:

```clojure
(def hmeta-d-group-model
  {:priors {:mu-logMratio {:dist :normal :mu 0.0 :sigma 1.0 :truncated false}
            :sigma-logMratio {:dist :half-normal :mu 0.0 :sigma 1.0 :truncated true}}})
```

## Tests that validate the concept

- `python/test_phase3_hierarchical.py` checks inspectability, non-destructive updates, prior behavior, and small-chain `fit_group` shape.
- `test/hmeta_d/hierarchical_test.clj` checks map inspectability, `assoc-in` behavior, prior density checks, EDN round-trip, and `fit-group` output shape.
