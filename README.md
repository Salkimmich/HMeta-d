# HMeta-d Translation Lab

This repository ports HMeta-d across three language generations (MATLAB -> Python -> Clojure) as a functional programming teaching vehicle. The original methodological reference is Fleming (2017), which introduces hierarchical Bayesian estimation of metacognitive efficiency ([doi:10.1093/nc/nix007](https://doi.org/10.1093/nc/nix007)).

Moving from MATLAB to Python teaches the shift from opaque external model execution (JAGS + imperative scripts) to explicit functions and inspectable data structures. In this repository, Phase 1 and Phase 2 make SDT and MCMC state visible instead of hidden behind a JAGS call.

Moving from Python to Clojure teaches a second shift: from object-oriented containers toward uniform immutable data and transformations. The model specification becomes a plain EDN map that can be modified with `assoc-in`, reduced over with `reduce-kv`, and serialized/deserialized without custom code.

Teaching annotation pattern used in implementation comments:

```text
MATLAB: <what MATLAB does here, what file>
Python: <what this introduces beyond MATLAB>
Clojure: <what this adds beyond Python>
```

## Repository Structure

```text
.
├── .github/workflows/
├── CPC_metacog_tutorial/
├── Matlab/
├── R/
├── docs/
├── python/
│   ├── phase1_sdt.py
│   ├── phase2_sampler.py
│   ├── phase3_hierarchical.py
│   ├── test_phase1_sdt.py
│   ├── test_phase2_sampler.py
│   └── test_phase3_hierarchical.py
├── src/hmeta_d/
│   ├── sdt.clj
│   ├── sampler.clj
│   └── hierarchical.clj
└── test/hmeta_d/
    ├── sdt_test.clj
    ├── sampler_test.clj
    ├── hierarchical_test.clj
    └── test_runner.clj
```

## Running The Code

- Python:
  - `cd python && pip install -r requirements.txt && python -m pytest -v`
- Clojure (Docker):
  - `docker run --rm -v "$PWD":/work -w /work clojure:temurin-21-tools-deps clojure -M:test`

## Phase Summaries

Phase 1 implements SDT core preparation (`d1`, `c1`, count handling) from MATLAB in Python and Clojure. The key concept is turning script-local calculations into composable pure functions returning structured data. Tests validate known reference values for type-1 measures.

Phase 2 implements type-2 likelihood and Metropolis-Hastings sampling in both languages. The key concept is making MCMC state transitions explicit and testable, rather than implicit in JAGS internals. Tests validate likelihood finiteness/rejection behavior and deterministic seeded sampling behavior within language.

Phase 3 implements the group-level hierarchical model as first-class data (`dataclass` in Python, plain map in Clojure). The key concept is model inspectability and non-destructive transformation (`dataclasses.replace`/`assoc-in`) rather than file-editing an external DSL. Tests validate prior behavior, non-destructive model edits, EDN round-trip, and group-fit output structure.

## Key Concepts Table

| Concept | MATLAB | Python | Clojure |
|---|---|---|---|
| Immutable data | struct (mutable) | frozen dataclass | plain map |
| Pipeline | sequential statements | function composition | threading macros |
| MCMC state | hidden in JAGS | explicit loop | lazy sequence |
| Model spec | .bugs file | dataclass | EDN map + assoc-in |
| Inverse normal CDF | norminv() | scipy.stats.norm.ppf | r/icdf r/default-normal |

## Citation

Fleming, S.M. (2017). HMeta-d: hierarchical Bayesian estimation of metacognitive efficiency from confidence ratings. *Neuroscience of Consciousness*, 3(1), nix007. [https://doi.org/10.1093/nc/nix007](https://doi.org/10.1093/nc/nix007)
