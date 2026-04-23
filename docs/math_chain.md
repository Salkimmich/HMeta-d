# Math Chain: Type 2 Equations and Tolerances

This document records the canonical Phase 2 equations used for the MATLAB -> Python -> Clojure translation.

## Type 2 Equations (Canonical Source)

Canonical source: `Matlab/fit_meta_d_mcmc.m` in the "find estimated t2FAR and t2HR" block.

For each confidence criterion index `i`:

- `est_FAR2_rS2(i) = I_FAR_area_rS2 / I_area_rS2`
- `est_HR2_rS2(i)  = C_HR_area_rS2 / C_area_rS2`
- `est_FAR2_rS1(i) = I_FAR_area_rS1 / I_area_rS1`
- `est_HR2_rS1(i)  = C_HR_area_rS1 / C_area_rS1`

Where:

- `I_FAR_area_rS2 = 1 - Phi(t2c1_upper; S1mu, S1sd)`
- `C_HR_area_rS2  = 1 - Phi(t2c1_upper; S2mu, S2sd)`
- `I_FAR_area_rS1 = Phi(t2c1_lower; S2mu, S2sd)`
- `C_HR_area_rS1  = Phi(t2c1_lower; S1mu, S1sd)`

And:

- `S1mu = -meta_d / 2`, `S2mu = meta_d / 2`
- `S1sd = 1`, `S2sd = 1` (equal-variance case used here)
- `Phi` is the normal CDF.

## Numeric Tolerances

Use these tolerances for tests and cross-language comparisons:

| Quantity | Tolerance | Notes |
|---|---:|---|
| `d1` / `c1` reference checks | `1e-3` to `1e-2` | Depends on test fixture precision |
| Probability clipping (`tol`) | `1e-5` | Matches SDT data structure default |
| Python vs Clojure value checks | `1e-2` | Compare summaries, not chain-wise identity |
| MCMC reproducibility within language | exact with fixed seed | Same code path + seed |

## Why this chain exists

- MATLAB: equations are embedded in imperative code and JAGS interaction.
- Python: equations become inspectable functions (`estimate_type2_rates`, `log_likelihood`).
- Clojure: equations become pure data transformations over maps/vectors.
## Type 2 Probability Equations (for Phase 2)
### MATLAB source (verbatim from fit_meta_d_mcmc.m)

```matlab
I_FAR_area_rS2 = 1-fncdf(t2c1_upper,S1mu,S1sd);
C_HR_area_rS2  = 1-fncdf(t2c1_upper,S2mu,S2sd);

I_FAR_area_rS1 = fncdf(t2c1_lower,S2mu,S2sd);
C_HR_area_rS1  = fncdf(t2c1_lower,S1mu,S1sd);

est_FAR2_rS2(i) = I_FAR_area_rS2 / I_area_rS2;
est_HR2_rS2(i)  = C_HR_area_rS2 / C_area_rS2;

est_FAR2_rS1(i) = I_FAR_area_rS1 / I_area_rS1;
est_HR2_rS1(i)  = C_HR_area_rS1 / C_area_rS1;
```

`est_HR2_rS2(i)`: probability of response `S2` at confidence rating `i` given stimulus `S2`, computed as the correct `S2` tail area above `t2c1_upper` normalised by the total `S2` response area above `c1`.

`est_FAR2_rS2(i)`: probability of response `S2` at confidence rating `i` given stimulus `S1`, computed as the incorrect `S2` tail area above `t2c1_upper` normalised by the total incorrect `S2` response area above `c1`.

`est_HR2_rS1(i)`: probability of response `S1` at confidence rating `i` given stimulus `S1`, computed as the correct `S1` area below `t2c1_lower` normalised by the total `S1` response area below `c1`.

`est_FAR2_rS1(i)`: probability of response `S1` at confidence rating `i` given stimulus `S2`, computed as the incorrect `S1` area below `t2c1_lower` normalised by the total incorrect `S1` response area below `c1`.

The following language blocks are API-shape pseudocode for concept mapping only. Executable implementations live in `python/phase2_sampler.py` and `src/hmeta_d/sampler.clj`.

```python
def type2_hr_rS2(meta_d: float, c1: float, c2: np.ndarray, k: int) -> float:
    """
    Type 2 hit rate for S2 response at confidence rating k.
    MATLAB: est_HR2_rS2(k) = C_HR_area_rS2 / C_area_rS2
    Equation: [1 - Phi(t2c1_upper(k); mu=S2mu, sigma=S2sd)] / [1 - Phi(c1; mu=S2mu, sigma=S2sd)]
    """
    pass


def type2_far_rS2(meta_d: float, c1: float, c2: np.ndarray, k: int) -> float:
    """
    Type 2 false alarm rate for S2 response at confidence rating k.
    MATLAB: est_FAR2_rS2(k) = I_FAR_area_rS2 / I_area_rS2
    Equation: [1 - Phi(t2c1_upper(k); mu=S1mu, sigma=S1sd)] / [1 - Phi(c1; mu=S1mu, sigma=S1sd)]
    """
    pass


def type2_hr_rS1(meta_d: float, c1: float, c2: np.ndarray, k: int) -> float:
    """
    Type 2 hit rate for S1 response at confidence rating k.
    MATLAB: est_HR2_rS1(k) = C_HR_area_rS1 / C_area_rS1
    Equation: Phi(t2c1_lower(k); mu=S1mu, sigma=S1sd) / Phi(c1; mu=S1mu, sigma=S1sd)
    """
    pass


def type2_far_rS1(meta_d: float, c1: float, c2: np.ndarray, k: int) -> float:
    """
    Type 2 false alarm rate for S1 response at confidence rating k.
    MATLAB: est_FAR2_rS1(k) = I_FAR_area_rS1 / I_area_rS1
    Equation: Phi(t2c1_lower(k); mu=S2mu, sigma=S2sd) / Phi(c1; mu=S2mu, sigma=S2sd)
    """
    pass
```

```clojure
(defn type2-hr-rS2
  "Type 2 hit rate for S2 response at confidence rating k.
   MATLAB: est_HR2_rS2(k) = C_HR_area_rS2 / C_area_rS2
   Python: type2_hr_rS2
   Equation: [1 - Phi(t2c1_upper(k); mu=S2mu, sigma=S2sd)] / [1 - Phi(c1; mu=S2mu, sigma=S2sd)]"
  [meta-d c1 c2 k]
  nil)

(defn type2-far-rS2
  "Type 2 false alarm rate for S2 response at confidence rating k.
   MATLAB: est_FAR2_rS2(k) = I_FAR_area_rS2 / I_area_rS2
   Python: type2_far_rS2
   Equation: [1 - Phi(t2c1_upper(k); mu=S1mu, sigma=S1sd)] / [1 - Phi(c1; mu=S1mu, sigma=S1sd)]"
  [meta-d c1 c2 k]
  nil)

(defn type2-hr-rS1
  "Type 2 hit rate for S1 response at confidence rating k.
   MATLAB: est_HR2_rS1(k) = C_HR_area_rS1 / C_area_rS1
   Python: type2_hr_rS1
   Equation: Phi(t2c1_lower(k); mu=S1mu, sigma=S1sd) / Phi(c1; mu=S1mu, sigma=S1sd)"
  [meta-d c1 c2 k]
  nil)

(defn type2-far-rS1
  "Type 2 false alarm rate for S1 response at confidence rating k.
   MATLAB: est_FAR2_rS1(k) = I_FAR_area_rS1 / I_area_rS1
   Python: type2_far_rS1
   Equation: Phi(t2c1_lower(k); mu=S2mu, sigma=S2sd) / Phi(c1; mu=S2mu, sigma=S2sd)"
  [meta-d c1 c2 k]
  nil)
```
