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

## Who This Is For

- Researchers who know HMeta-d from MATLAB and want to understand a transparent implementation.
- Developers learning functional design by translating one mathematical model across languages.
- Contributors who want runnable tests and clear cross-language equivalence checks.

## What You Can Do Here

- Run a phase-by-phase translation of SDT + meta-d computations.
- Compare how the same model is represented in MATLAB scripts, Python dataclasses, and Clojure maps.
- Validate behavior with both local tests and remote GitHub Actions gates.

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

## Concept Progression (Phase 1 -> 3)

1. **Phase 1 (`sdt`)**  
   Type-1 SDT preparation (`d1`, `c1`, cumulative rates) as pure functions.
2. **Phase 2 (`sampler`)**  
   Type-2 likelihood and Metropolis-Hastings made explicit (no hidden JAGS state machine).
3. **Phase 3 (`hierarchical`)**  
   Group model as first-class data (`dataclass` / plain map), supporting non-destructive model edits.

## Setup And Quickstart

### Prerequisites

- Python 3.12+ (3.14 also works in this repo)
- `pip`
- Git
- Optional local Clojure path:
  - Docker Desktop with Linux containers enabled
  - Windows note: virtualization must be enabled in BIOS/UEFI for Docker Desktop

### Install links by platform

- Python:
  - Windows/macOS/Linux: [https://www.python.org/downloads/](https://www.python.org/downloads/)
- Docker:
  - Windows/macOS: [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
  - Linux Engine: [https://docs.docker.com/engine/install/](https://docs.docker.com/engine/install/)
- Git:
  - Windows/macOS/Linux: [https://git-scm.com/downloads](https://git-scm.com/downloads)

### Cross-platform command guide

Use the command style that matches your shell:

- **Windows (PowerShell)**
  - Use `cd python; pip install -r requirements.txt; python -m pytest -v`
  - Docker mount from repo root:
    - `docker run --rm -v ${PWD}:/work -w /work clojure:temurin-21-tools-deps clojure -M:test`
- **macOS/Linux (bash/zsh)**
  - Use `cd python && pip install -r requirements.txt && python -m pytest -v`
  - Docker mount from repo root:
    - `docker run --rm -v "$PWD":/work -w /work clojure:temurin-21-tools-deps clojure -M:test`

Path note:

- `src/hmeta_d/...` and `test/hmeta_d/...` use forward slashes in docs for portability.
- PowerShell accepts forward slashes in many commands, but use `${PWD}` for Docker volume mounting.

### 5-minute start (Python only)

```bash
cd python
pip install -r requirements.txt
python -m pytest -v
```

### Full local validation (Python + Clojure)

From repository root:

```bash
# Python phase gates
cd python && python -m pytest test_phase2_sampler.py -v
cd python && python -m pytest test_phase3_hierarchical.py -v

# Clojure gate via Docker
docker run --rm -v "$PWD":/work -w /work clojure:temurin-21-tools-deps clojure -M:test
```

PowerShell equivalent:

```powershell
cd python; python -m pytest test_phase2_sampler.py -v
cd python; python -m pytest test_phase3_hierarchical.py -v
cd ..; docker run --rm -v ${PWD}:/work -w /work clojure:temurin-21-tools-deps clojure -M:test
```

### If Docker is unavailable locally

This repository includes GitHub Actions CI that runs:

- Python Phase 2 + 3 tests
- Clojure tests in Docker

Use CI status as the strict validation path on machines where virtualization is restricted.

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

## Documentation Map

- `docs/math_chain.md`: canonical type-2 equations and numeric tolerances.
- `docs/phase1_concepts.md`: SDT core translation concepts.
- `docs/phase2_concepts.md`: likelihood + explicit MCMC concepts.
- `docs/phase3_concepts.md`: hierarchical model-as-data concepts.

## Contributing Workflow

1. Create a branch from `master`.
2. Implement or update one phase-concept chunk at a time.
3. Run local tests relevant to your changes:
   - Python: `cd python && python -m pytest -v`
   - Clojure: `docker run --rm -v "$PWD":/work -w /work clojure:temurin-21-tools-deps clojure -M:test`
4. Push branch and open a pull request.
5. Wait for CI to pass before merge.

## Troubleshooting

- **`No module named pytest` in CI/local**  
  Ensure `pip install -r python/requirements.txt` was run.
- **Docker fails to start on Windows**  
  Check firmware virtualization and Docker Desktop engine status.
- **Clojure test errors about fastmath vars**  
  Ensure latest repository state is checked out; current implementation uses `fastmath.random` distribution APIs.

## Citation

Fleming, S.M. (2017). HMeta-d: hierarchical Bayesian estimation of metacognitive efficiency from confidence ratings. *Neuroscience of Consciousness*, 3(1), nix007. [https://doi.org/10.1093/nc/nix007](https://doi.org/10.1093/nc/nix007)
