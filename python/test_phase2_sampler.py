"""Tests for Phase 2 sampler translation."""

from __future__ import annotations

import pathlib
import sys

import numpy as np

sys.path.append(str(pathlib.Path(__file__).resolve().parent))

from phase1_sdt import prepare_sdt_data
from phase2_sampler import estimate_type2_rates, log_likelihood, mh_chain


def _reference_data():
    return prepare_sdt_data(
        [36, 24, 17, 20, 10, 12, 34, 22],
        [21, 19, 23, 28, 33, 28, 20, 19],
    )


def test_estimate_type2_rates_shape_and_range():
    data = _reference_data()
    c2 = np.array([0.3, 0.6, 0.9], dtype=float)
    rates = estimate_type2_rates(meta_d=0.9, c1=data.c1, c2=c2, nratings=data.nratings)
    assert rates.far_s1.shape == (data.nratings - 1,)
    assert rates.hr_s2.shape == (data.nratings - 1,)
    assert np.all((rates.far_s1 >= 0) & (rates.far_s1 <= 1))
    assert np.all((rates.hr_s2 >= 0) & (rates.hr_s2 <= 1))


def test_log_likelihood_returns_finite_for_valid_params():
    data = _reference_data()
    params = {"meta_d": 1.0, "c2": np.array([0.25, 0.55, 0.8], dtype=float)}
    ll = log_likelihood(params, data)
    assert np.isfinite(ll)


def test_log_likelihood_rejects_non_positive_c2():
    data = _reference_data()
    bad_params = {"meta_d": 1.0, "c2": np.array([0.25, -0.1, 0.8], dtype=float)}
    assert log_likelihood(bad_params, data) == -np.inf


def test_mh_chain_runs_deterministically_with_seed():
    data = _reference_data()
    init = {"meta_d": 0.8, "c2": np.array([0.4, 0.6, 0.8], dtype=float)}
    chain_a = mh_chain(init, data, step_size=0.05, n_samples=20, n_burnin=10, seed=123)
    chain_b = mh_chain(init, data, step_size=0.05, n_samples=20, n_burnin=10, seed=123)
    assert len(chain_a) == 20
    assert len(chain_b) == 20
    assert chain_a[-1]["meta_d"] == chain_b[-1]["meta_d"]
    assert np.allclose(chain_a[-1]["c2"], chain_b[-1]["c2"])
