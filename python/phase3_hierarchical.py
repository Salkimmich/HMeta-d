"""
Phase 3: Hierarchical model as data.

MATLAB equivalent: the group JAGS model file (`fit_meta_d_mcmc_group.m`).
Teaching goal: model specification becomes a Python dataclass.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from scipy.stats import norm

from phase1_sdt import SDTData
from phase2_sampler import log_likelihood, mh_chain


@dataclass(frozen=True)
class Prior:
    """
    MATLAB: one prior line in JAGS model block.
    Python: frozen dataclass value, inspectable and immutable.
    """

    distribution: str
    mu: float = 0.0
    sigma: float = 1.0
    truncated: bool = False


@dataclass
class HierarchicalModel:
    """
    MATLAB: external .bugs file.
    Python: in-memory model specification with priors and MCMC config.
    """

    group_priors: dict[str, Prior]
    mcmc: dict[str, Any] = field(
        default_factory=lambda: {
            "n_chains": 3,
            "n_samples": 1000,
            "n_burnin": 200,
            "step_size": 0.1,
            "seed": 42,
        }
    )


HMETA_D_GROUP_MODEL = HierarchicalModel(
    group_priors={
        "mu_logMratio": Prior("normal", mu=0.0, sigma=1.0),
        "sigma_logMratio": Prior("half_normal", mu=0.0, sigma=1.0, truncated=True),
        "mu_c2": Prior("normal", mu=0.0, sigma=1.0),
        "sigma_c2": Prior("half_normal", mu=0.0, sigma=1.0, truncated=True),
    }
)


def sample_prior(prior: Prior, rng: np.random.Generator) -> float:
    """
    MATLAB: JAGS samples priors implicitly.
    Python: explicit prior sampling function.
    """

    if prior.distribution in {"normal", "half_normal"}:
        value = float(rng.normal(prior.mu, prior.sigma))
        return abs(value) if prior.truncated or prior.distribution == "half_normal" else value
    raise ValueError(f"Unknown distribution: {prior.distribution}")


def log_prior_group(group_params: dict[str, float], model: HierarchicalModel) -> float:
    """
    MATLAB: prior block in JAGS model.
    Python: compute prior log-density by walking model.group_priors.
    """

    lp = 0.0
    for name, prior in model.group_priors.items():
        value = float(group_params[name])
        if (prior.truncated or prior.distribution == "half_normal") and value < 0:
            return -np.inf
        if prior.distribution in {"normal", "half_normal"}:
            lp += float(norm.logpdf(value, loc=prior.mu, scale=prior.sigma))
        else:
            raise ValueError(f"Unknown distribution: {prior.distribution}")
    return lp


def group_log_likelihood(group_params: dict[str, Any], subject_data: list[SDTData]) -> float:
    """
    MATLAB: nested subject block in group JAGS model.
    Python: explicit loop over subjects and latent subject-level parameters.
    """

    rng = np.random.default_rng(int(group_params.get("_seed", 0)))
    mu = float(group_params["mu_logMratio"])
    sigma = float(group_params["sigma_logMratio"])
    mu_c2 = float(group_params["mu_c2"])
    sigma_c2 = max(1e-6, float(group_params["sigma_c2"]))

    total = 0.0
    for data in subject_data:
        log_mratio = float(rng.normal(mu, sigma))
        mratio = float(np.exp(log_mratio))
        meta_d = mratio * data.d1
        c2_vec = np.abs(rng.normal(mu_c2, sigma_c2, size=data.nratings - 1))
        total += float(log_likelihood({"meta_d": meta_d, "c2": c2_vec}, data))
    return total


def fit_group(model: HierarchicalModel, subject_data: list[SDTData]) -> list[list[dict[str, Any]]]:
    """
    MATLAB: `fit_meta_d_mcmc_group` delegates to JAGS.
    Python: run MH directly with model dataclass configuring all settings.
    """

    cfg = model.mcmc
    n_chains = int(cfg["n_chains"])
    n_samples = int(cfg["n_samples"])
    n_burnin = int(cfg["n_burnin"])
    step_size = float(cfg["step_size"])
    base_seed = int(cfg.get("seed", 42))

    def log_post(params: dict[str, Any]) -> float:
        prior_params = {
            "mu_logMratio": float(params["mu_logMratio"]),
            "sigma_logMratio": float(params["sigma_logMratio"]),
            "mu_c2": float(params["mu_c2"]),
            "sigma_c2": float(params["sigma_c2"]),
        }
        ll_params = {**prior_params, "_seed": int(params.get("_seed", base_seed))}
        return log_prior_group(prior_params, model) + group_log_likelihood(ll_params, subject_data)

    chains: list[list[dict[str, Any]]] = []
    for chain_idx in range(n_chains):
        init = {
            "mu_logMratio": 0.0,
            "sigma_logMratio": 0.5,
            "mu_c2": 0.5,
            "sigma_c2": 0.5,
            "_seed": float(base_seed + chain_idx),
        }
        chain = mh_chain(
            init,
            {"log_posterior": log_post},
            step_size=step_size,
            n_samples=n_samples,
            n_burnin=n_burnin,
            seed=base_seed + chain_idx,
        )
        chains.append(chain)
    return chains
