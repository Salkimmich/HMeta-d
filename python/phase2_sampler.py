"""Phase 2: Likelihood + MH sampler translation from MATLAB to Python.

MATLAB equivalent: the type-2 likelihood and MCMC setup in `Matlab/fit_meta_d_mcmc.m`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy.stats import binom, norm

from phase1_sdt import SDTData


@dataclass(frozen=True)
class Type2Rates:
    """Container for estimated type-2 ROC rates."""

    far_s1: np.ndarray
    hr_s1: np.ndarray
    far_s2: np.ndarray
    hr_s2: np.ndarray


def _build_t2_criteria(c1: float, c2: np.ndarray, nratings: int) -> np.ndarray:
    """Build MATLAB-style stacked criteria around c1.

    MATLAB: `t2c1 = [fit.t2ca_rS1 fit.t2ca_rS2]`.
    Python: derive both sides from one symmetric offset vector `c2`.
    """

    if len(c2) != nratings - 1:
        raise ValueError("c2 must have length nratings - 1")
    left = c1 - c2[::-1]
    right = c1 + c2
    return np.concatenate([left, right])


def estimate_type2_rates(meta_d: float, c1: float, c2: np.ndarray, nratings: int) -> Type2Rates:
    """Estimate type-2 FAR/HR curves from SDT latent parameters.

    MATLAB: "find estimated t2FAR and t2HR" block in `fit_meta_d_mcmc.m`.
    Python: same equations with explicit array handling.
    """

    s1_mu, s1_sd = -meta_d / 2.0, 1.0
    s2_mu, s2_sd = meta_d / 2.0, 1.0

    c_area_rs2 = 1.0 - norm.cdf(c1, loc=s2_mu, scale=s2_sd)
    i_area_rs2 = 1.0 - norm.cdf(c1, loc=s1_mu, scale=s1_sd)
    c_area_rs1 = norm.cdf(c1, loc=s1_mu, scale=s1_sd)
    i_area_rs1 = norm.cdf(c1, loc=s2_mu, scale=s2_sd)

    if min(c_area_rs2, i_area_rs2, c_area_rs1, i_area_rs1) <= 0:
        return Type2Rates(
            far_s1=np.full(nratings - 1, np.nan),
            hr_s1=np.full(nratings - 1, np.nan),
            far_s2=np.full(nratings - 1, np.nan),
            hr_s2=np.full(nratings - 1, np.nan),
        )

    t2c1 = _build_t2_criteria(c1, c2, nratings)
    far_s1, hr_s1, far_s2, hr_s2 = [], [], [], []

    for i in range(1, nratings):
        lower = t2c1[nratings - i - 1]
        upper = t2c1[nratings - 2 + i]

        i_far_area_rs2 = 1.0 - norm.cdf(upper, loc=s1_mu, scale=s1_sd)
        c_hr_area_rs2 = 1.0 - norm.cdf(upper, loc=s2_mu, scale=s2_sd)
        i_far_area_rs1 = norm.cdf(lower, loc=s2_mu, scale=s2_sd)
        c_hr_area_rs1 = norm.cdf(lower, loc=s1_mu, scale=s1_sd)

        far_s2.append(i_far_area_rs2 / i_area_rs2)
        hr_s2.append(c_hr_area_rs2 / c_area_rs2)
        far_s1.append(i_far_area_rs1 / i_area_rs1)
        hr_s1.append(c_hr_area_rs1 / c_area_rs1)

    return Type2Rates(
        far_s1=np.asarray(far_s1, dtype=float),
        hr_s1=np.asarray(hr_s1, dtype=float),
        far_s2=np.asarray(far_s2, dtype=float),
        hr_s2=np.asarray(hr_s2, dtype=float),
    )


def _observed_type2_counts(data: SDTData) -> dict[str, tuple[np.ndarray, int]]:
    """Extract observed cumulative type-2 counts from rating bins.

    MATLAB: the `obs_FAR2_*` and `obs_HR2_*` loops.
    Python: return cumulative numerators + fixed denominators per side.
    """

    nratings = data.nratings
    n = 2 * nratings
    nR_S1 = data.counts[:n]
    nR_S2 = data.counts[n:]

    i_nR_rS2 = nR_S1[nratings:]
    i_nR_rS1 = nR_S2[nratings - 1 :: -1]
    c_nR_rS2 = nR_S2[nratings:]
    c_nR_rS1 = nR_S1[nratings - 1 :: -1]

    idxs = range(1, nratings)
    obs_far_s2 = np.asarray([np.sum(i_nR_rS2[i:]) for i in idxs], dtype=float)
    obs_hr_s2 = np.asarray([np.sum(c_nR_rS2[i:]) for i in idxs], dtype=float)
    obs_far_s1 = np.asarray([np.sum(i_nR_rS1[i:]) for i in idxs], dtype=float)
    obs_hr_s1 = np.asarray([np.sum(c_nR_rS1[i:]) for i in idxs], dtype=float)

    return {
        "far_s2": (obs_far_s2, int(np.sum(i_nR_rS2))),
        "hr_s2": (obs_hr_s2, int(np.sum(c_nR_rS2))),
        "far_s1": (obs_far_s1, int(np.sum(i_nR_rS1))),
        "hr_s1": (obs_hr_s1, int(np.sum(c_nR_rS1))),
    }


def log_likelihood(params: dict[str, Any], data: SDTData) -> float:
    """Compute type-2 binomial log-likelihood.

    MATLAB: JAGS handles this implicitly.
    Python: evaluate it directly for MH acceptance decisions.
    """

    meta_d = float(params["meta_d"])
    c2 = np.asarray(params["c2"], dtype=float)

    rates = estimate_type2_rates(meta_d, data.c1, c2, data.nratings)
    if np.any(~np.isfinite(rates.far_s1)) or np.any(c2 <= 0):
        return -np.inf

    obs = _observed_type2_counts(data)
    ll = 0.0
    predicted = {
        "far_s1": np.clip(rates.far_s1, data.tol, 1.0 - data.tol),
        "hr_s1": np.clip(rates.hr_s1, data.tol, 1.0 - data.tol),
        "far_s2": np.clip(rates.far_s2, data.tol, 1.0 - data.tol),
        "hr_s2": np.clip(rates.hr_s2, data.tol, 1.0 - data.tol),
    }

    for key in ("far_s1", "hr_s1", "far_s2", "hr_s2"):
        successes, total = obs[key]
        ll += float(np.sum(binom.logpmf(successes.astype(int), total, predicted[key])))
    return ll


def log_posterior(params: dict[str, Any], data: SDTData) -> float:
    """Simple regularized posterior used for didactic MH sampling."""

    meta_d = float(params["meta_d"])
    c2 = np.asarray(params["c2"], dtype=float)
    if np.any(c2 <= 0):
        return -np.inf
    lp = norm.logpdf(meta_d, loc=data.d1, scale=2.0)
    lp += float(np.sum(norm.logpdf(c2, loc=0.5, scale=1.0)))
    return float(lp + log_likelihood(params, data))


def _perturb(value: Any, step_size: float, rng: np.random.Generator) -> Any:
    """Gaussian random-walk proposal for scalars and vectors."""

    arr = np.asarray(value, dtype=float)
    out = arr + rng.normal(0.0, step_size, size=arr.shape)
    if np.isscalar(value):
        return float(out)
    return out


def mh_chain(
    init_params: dict[str, Any],
    data_or_cfg: Any,
    step_size: float = 0.1,
    n_samples: int = 1000,
    n_burnin: int = 0,
    seed: int | None = 0,
) -> list[dict[str, Any]]:
    """Run a basic random-walk Metropolis-Hastings chain.

    MATLAB: MCMC is hidden behind JAGS.
    Python: explicit transition loop over inspectable parameter dicts.
    """

    rng = np.random.default_rng(seed)
    if isinstance(data_or_cfg, dict) and "log_posterior" in data_or_cfg:
        log_post_fn = data_or_cfg["log_posterior"]
    else:
        log_post_fn = lambda p: log_posterior(p, data_or_cfg)

    current = {k: (np.asarray(v, dtype=float).copy() if not np.isscalar(v) else float(v)) for k, v in init_params.items()}
    current_lp = float(log_post_fn(current))
    draws: list[dict[str, Any]] = []

    total_iters = n_burnin + n_samples
    for it in range(total_iters):
        proposal = {k: _perturb(v, step_size, rng) for k, v in current.items()}
        proposal_lp = float(log_post_fn(proposal))
        if np.isfinite(proposal_lp):
            accept_logp = proposal_lp - current_lp
            if np.log(rng.uniform()) < accept_logp:
                current = proposal
                current_lp = proposal_lp
        if it >= n_burnin:
            draws.append({k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in current.items()})
    return draws
