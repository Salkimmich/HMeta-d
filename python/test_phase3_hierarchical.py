"""Tests for Phase 3 hierarchical model."""

from __future__ import annotations

import dataclasses
import json
import pathlib

import numpy as np

from phase1_sdt import prepare_sdt_data
from phase3_hierarchical import (
    HMETA_D_GROUP_MODEL,
    HierarchicalModel,
    Prior,
    fit_group,
    log_prior_group,
    sample_prior,
)


SUBJECT_DATA = [
    prepare_sdt_data([36, 24, 17, 20, 10, 12, 34, 22], [21, 19, 23, 28, 33, 28, 20, 19]),
    prepare_sdt_data([30, 20, 18, 22, 12, 10, 36, 24], [22, 18, 24, 26, 30, 26, 22, 20]),
]


def _load_posterior_fixture() -> dict:
    fixture_path = pathlib.Path(__file__).resolve().parent.parent / "docs" / "fixtures" / "posterior_summary_fixture.json"
    return json.loads(fixture_path.read_text(encoding="utf-8"))


class TestModelAsData:
    def test_model_is_inspectable(self):
        assert "mu_logMratio" in HMETA_D_GROUP_MODEL.group_priors
        assert HMETA_D_GROUP_MODEL.group_priors["mu_logMratio"].sigma == 1.0

    def test_prior_modification_is_non_destructive(self):
        tighter = dataclasses.replace(
            HMETA_D_GROUP_MODEL,
            group_priors={
                **HMETA_D_GROUP_MODEL.group_priors,
                "sigma_logMratio": Prior("half_normal", mu=0, sigma=0.5, truncated=True),
            },
        )
        assert tighter.group_priors["sigma_logMratio"].sigma == 0.5
        assert HMETA_D_GROUP_MODEL.group_priors["sigma_logMratio"].sigma == 1.0

    def test_log_prior_group_returns_finite(self):
        group_params = {"mu_logMratio": 0.0, "sigma_logMratio": 0.5, "mu_c2": 0.0, "sigma_c2": 0.5}
        lp = log_prior_group(group_params, HMETA_D_GROUP_MODEL)
        assert np.isfinite(lp)

    def test_half_normal_rejects_negative(self):
        group_params = {"mu_logMratio": 0.0, "sigma_logMratio": -0.1, "mu_c2": 0.0, "sigma_c2": 0.5}
        lp = log_prior_group(group_params, HMETA_D_GROUP_MODEL)
        assert lp == -np.inf

    def test_tighter_prior_changes_density(self):
        tight_model = dataclasses.replace(
            HMETA_D_GROUP_MODEL,
            group_priors={
                **HMETA_D_GROUP_MODEL.group_priors,
                "sigma_logMratio": Prior("half_normal", mu=0, sigma=0.1, truncated=True),
            },
        )
        params = {"mu_logMratio": 0.0, "sigma_logMratio": 0.8, "mu_c2": 0.0, "sigma_c2": 0.5}
        lp_wide = log_prior_group(params, HMETA_D_GROUP_MODEL)
        lp_tight = log_prior_group(params, tight_model)
        assert lp_tight < lp_wide

    def test_sample_prior_half_normal_non_negative(self):
        rng = np.random.default_rng(10)
        val = sample_prior(Prior("half_normal", mu=0, sigma=1, truncated=True), rng)
        assert val >= 0

    def test_fit_group_returns_configured_shapes(self):
        model = HierarchicalModel(
            group_priors=HMETA_D_GROUP_MODEL.group_priors,
            mcmc={"n_chains": 2, "n_samples": 5, "n_burnin": 2, "step_size": 0.05, "seed": 7},
        )
        chains = fit_group(model, SUBJECT_DATA)
        assert len(chains) == 2
        assert len(chains[0]) == 5

    def test_phase3_posterior_summary_matches_fixture(self):
        fixture = _load_posterior_fixture()["phase3"]
        model = HierarchicalModel(
            group_priors=HMETA_D_GROUP_MODEL.group_priors,
            mcmc=fixture["mcmc"],
        )
        chains = fit_group(model, SUBJECT_DATA)
        flat = [draw for chain in chains for draw in chain]
        means = {
            "mu_logMratio": float(np.mean([draw["mu_logMratio"] for draw in flat])),
            "sigma_logMratio": float(np.mean([draw["sigma_logMratio"] for draw in flat])),
            "mu_c2": float(np.mean([draw["mu_c2"] for draw in flat])),
            "sigma_c2": float(np.mean([draw["sigma_c2"] for draw in flat])),
        }
        tol = float(fixture["tolerance"])
        expected = fixture["expected_means"]
        for key, expected_value in expected.items():
            assert np.isclose(means[key], float(expected_value), atol=tol, rtol=0.0)
