"""Phase 1 SDT core translation from MATLAB to Python.

MATLAB equivalent: pre-JAGS block in `Matlab/fit_meta_d_mcmc.m`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy.stats import norm


@dataclass(frozen=True)
class SDTData:
    """Immutable SDT data bundle equivalent to MATLAB `datastruct`."""

    d1: float
    c1: float
    counts: np.ndarray
    nratings: int
    nTot: int
    tol: float = 1e-5


def pad_counts(counts: Sequence[float], nratings: int) -> np.ndarray:
    """Add additive smoothing used for type-1 rate stability.

    MATLAB: `adj_f = 1/length(nR_S1)` then `nR_Sx_adj = nR_Sx + adj_f`.
    Since `length(nR_S1) == 2 * nratings`, this is `1 / (2 * nratings)`.
    """

    padded = np.asarray(counts, dtype=float).copy()
    padded += 1.0 / (2.0 * nratings)
    return padded


def compute_rates(nR_S1: Sequence[int], nR_S2: Sequence[int]) -> tuple[float, float, np.ndarray, np.ndarray]:
    """Compute MATLAB-style cumulative rating HR/FAR and return type-1 rates.

    Returns:
        hit_rate: Type-1 hit rate at index `nratings` (MATLAB `t1_index`)
        fa_rate: Type-1 false alarm rate at index `nratings`
        rating_hr: Full cumulative HR vector
        rating_far: Full cumulative FAR vector
    """

    if len(nR_S1) != len(nR_S2):
        raise ValueError("nR_S1 and nR_S2 must have same length")
    if len(nR_S1) % 2 != 0:
        raise ValueError("Input vectors must have an even number of elements")

    n = len(nR_S1)
    nratings = n // 2
    nR_S1_adj = pad_counts(nR_S1, nratings)
    nR_S2_adj = pad_counts(nR_S2, nratings)

    # MATLAB loop: for c = 2:nRatings*2  (1-based indexing)
    rating_hr = []
    rating_far = []
    total_s2 = float(np.sum(nR_S2_adj))
    total_s1 = float(np.sum(nR_S1_adj))
    for c_idx in range(1, n):
        rating_hr.append(float(np.sum(nR_S2_adj[c_idx:]) / total_s2))
        rating_far.append(float(np.sum(nR_S1_adj[c_idx:]) / total_s1))

    rating_hr_arr = np.asarray(rating_hr, dtype=float)
    rating_far_arr = np.asarray(rating_far, dtype=float)
    t1_index = nratings - 1  # MATLAB uses 1-based index nratings
    return rating_hr_arr[t1_index], rating_far_arr[t1_index], rating_hr_arr, rating_far_arr


def compute_dprime(hit_rate: float, fa_rate: float) -> float:
    """Type-1 d-prime via inverse normal CDF difference."""

    return float(norm.ppf(hit_rate) - norm.ppf(fa_rate))


def compute_criterion(hit_rate: float, fa_rate: float) -> float:
    """Type-1 criterion from HR/FAR."""

    return float(-0.5 * (norm.ppf(hit_rate) + norm.ppf(fa_rate)))


def prepare_sdt_data(nR_S1: Sequence[int], nR_S2: Sequence[int]) -> SDTData:
    """Full SDT preparation pipeline.

    MATLAB equivalent: pre-JAGS calculations in `fit_meta_d_mcmc.m`,
    then `datastruct = struct('d1', d1, 'c1', c1, 'counts', counts, ...)`.
    """

    if len(nR_S1) != len(nR_S2):
        raise ValueError("nR_S1 and nR_S2 must have same length")
    if len(nR_S1) % 2 != 0:
        raise ValueError("Input vectors must have an even number of elements")

    nratings = len(nR_S1) // 2
    hit_rate, fa_rate, _, _ = compute_rates(nR_S1, nR_S2)
    d1 = compute_dprime(hit_rate, fa_rate)
    c1 = compute_criterion(hit_rate, fa_rate)

    counts = np.concatenate((np.asarray(nR_S1, dtype=float), np.asarray(nR_S2, dtype=float)))
    n_tot = int(np.sum(counts))

    return SDTData(
        d1=d1,
        c1=c1,
        counts=counts,
        nratings=nratings,
        nTot=n_tot,
        tol=1e-5,
    )
