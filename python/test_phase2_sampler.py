"""Tests for Phase 2 sampler translation."""

from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

sys.path.append(str(pathlib.Path(__file__).resolve().parent))

from phase1_sdt import prepare_sdt_data
from phase2_sampler import estimate_type2_rates, log_likelihood, mh_chain


def _load_parity_fixture() -> dict:
    fixture_path = pathlib.Path(__file__).resolve().parent.parent / "docs" / "fixtures" / "type2_parity_fixture.json"
    return json.loads(fixture_path.read_text(encoding="utf-8"))


def _load_posterior_fixture() -> dict:
    fixture_path = pathlib.Path(__file__).resolve().parent.parent / "docs" / "fixtures" / "posterior_summary_fixture.json"
    return json.loads(fixture_path.read_text(encoding="utf-8"))


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


def test_type2_rates_match_shared_parity_fixture():
    fixture = _load_parity_fixture()
    data = prepare_sdt_data(fixture["nR_S1"], fixture["nR_S2"])
    rates = estimate_type2_rates(
        meta_d=float(fixture["meta_d"]),
        c1=data.c1,
        c2=np.asarray(fixture["c2"], dtype=float),
        nratings=data.nratings,
    )
    tol = float(fixture["tolerance"])
    expected = fixture["expected_rates"]
    assert np.allclose(rates.far_s1, np.asarray(expected["far_s1"], dtype=float), atol=tol, rtol=0.0)
    assert np.allclose(rates.hr_s1, np.asarray(expected["hr_s1"], dtype=float), atol=tol, rtol=0.0)
    assert np.allclose(rates.far_s2, np.asarray(expected["far_s2"], dtype=float), atol=tol, rtol=0.0)
    assert np.allclose(rates.hr_s2, np.asarray(expected["hr_s2"], dtype=float), atol=tol, rtol=0.0)


def test_phase2_posterior_summary_matches_fixture():
    fixture = _load_posterior_fixture()["phase2"]
    data = _reference_data()
    init = {
        "meta_d": float(fixture["init"]["meta_d"]),
        "c2": np.asarray(fixture["init"]["c2"], dtype=float),
    }
    chain = mh_chain(
        init,
        data,
        step_size=float(fixture["step_size"]),
        n_samples=int(fixture["n_samples"]),
        n_burnin=int(fixture["n_burnin"]),
        seed=int(fixture["seed"]),
    )
    meta_mean = float(np.mean([sample["meta_d"] for sample in chain]))
    c2_mean = float(np.mean([np.mean(sample["c2"]) for sample in chain]))
    expected = fixture["expected_means"]
    tol = float(fixture["tolerance"])
    assert np.isclose(meta_mean, float(expected["meta_d"]), atol=tol, rtol=0.0)
    assert np.isclose(c2_mean, float(expected["c2_mean"]), atol=tol, rtol=0.0)
