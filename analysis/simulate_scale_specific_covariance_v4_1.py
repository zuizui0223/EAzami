#!/usr/bin/env python3
"""Run the interpretable scale-specific covariance v4.1 screen.

The first v4 implementation used mean-centred local factors.  Because Azami's
among-taxon phenotype summaries are taxon medians, zero mean alone did not make
the declared within-only factor absent from the among-taxon estimand.  This
wrapper supersedes the uninspected run 33043095287 and changes only that
implementation detail: local module-factor values are generated in symmetric
pairs within every taxon, with an additional zero when replication is odd.
They therefore have exact zero mean and median before unit loadings are applied.

All shared priors, family definitions, targets, distances, simulation sizes and
promotion gates remain unchanged.  Only results produced through this v4.1
entry point are interpretable.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import simulate_scale_specific_covariance_v4 as base  # noqa: E402


EXPECTED_PRIOR_VERSION = "scale_specific_covariance_v4_1_implementation_priors_2026-08-27"
EXPECTED_STATUS = "amended_before_v4_family_outcome_inspection"
SUPERSEDED_RUN = "33043095287"
ORIGINAL_VALIDATE_PRIORS = base.validate_priors


def paired_symmetric_by_taxon(
    taxa: np.ndarray,
    n_columns: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Generate taxon-wise values with exact zero mean and median.

    For each taxon and column, draws occur in +x/-x pairs.  Odd replication gets
    one exact zero.  Rows are shuffled within taxon, so no population position is
    assigned a deterministic sign.  Multiplication by a taxon-constant unit
    loading preserves both zero mean and zero median.
    """
    taxa = np.asarray(taxa)
    out = np.zeros((len(taxa), n_columns), dtype=float)
    for taxon in np.unique(taxa):
        idx = np.flatnonzero(taxa == taxon)
        n = len(idx)
        half = n // 2
        draws = rng.normal(size=(half, n_columns))
        values = np.vstack([draws, -draws])
        if n % 2:
            values = np.vstack([values, np.zeros((1, n_columns), dtype=float)])
        values = values[rng.permutation(n)]
        out[idx] = values
        if not np.allclose(values.mean(axis=0), 0.0, atol=1e-15, rtol=0.0):
            raise RuntimeError("Paired-symmetric factor failed exact zero-mean check")
        if not np.allclose(np.median(values, axis=0), 0.0, atol=1e-15, rtol=0.0):
            raise RuntimeError("Paired-symmetric factor failed exact zero-median check")
    return out


def validate_priors(contract: dict[str, Any], priors: dict[str, Any]) -> None:
    if priors.get("version") != EXPECTED_PRIOR_VERSION:
        raise ValueError("Unexpected v4.1 implementation-prior version")
    if priors.get("status") != EXPECTED_STATUS:
        raise ValueError("v4.1 priors must preserve the pre-outcome amendment status")
    note = str(priors.get("amendment_note", ""))
    for term in [SUPERSEDED_RUN, "No result, log or artifact", "superseded", "zero taxon mean and median"]:
        if term not in note:
            raise ValueError(f"v4.1 amendment boundary missing term: {term}")
    within = priors["within_only_module_factor"]
    if within.get("factor_distribution") != (
        "paired_symmetric_standard_normal_values_per_taxon_and_registered_module_"
        "with_exact_zero_mean_and_median"
    ):
        raise ValueError("v4.1 within-only factor distribution changed")
    if float(within.get("exact_taxon_mean")) != 0.0 or float(within.get("exact_taxon_median")) != 0.0:
        raise ValueError("v4.1 local factor must have exact zero taxon mean and median")

    # Reuse every range/size/family-independent validation from v4 by presenting
    # only the legacy version/status labels to that validator.  Scientific fields
    # and numerical prior ranges are not altered.
    compatible = dict(priors)
    compatible["version"] = "scale_specific_covariance_v4_implementation_priors_2026-08-27"
    compatible["status"] = "frozen_before_v4_family_outcomes"
    ORIGINAL_VALIDATE_PRIORS(contract, compatible)


def add_within_only_factor(
    endpoints: np.ndarray,
    taxa: np.ndarray,
    unit_ids: list[str],
    module_index: np.ndarray,
    endpoint_index: dict[str, tuple[int, ...]],
    priors: dict[str, Any],
    rng: np.random.Generator,
) -> tuple[np.ndarray, dict[str, float]]:
    n_modules = int(module_index.max()) + 1
    factors = paired_symmetric_by_taxon(taxa, n_modules, rng)
    raw_loadings = rng.normal(size=len(unit_ids))
    loadings = base.rms_normalize_within_modules(raw_loadings[:, None], module_index)[:, 0]
    scale_dist = priors["within_only_module_factor"]["common_scale_distribution"]
    scale = rng.uniform(scale_dist["low"], scale_dist["high"])
    effects = scale * factors[:, module_index] * loadings[None, :]

    # The exact unit-effect median is the critical estimand-level gate.  It is
    # checked before the nonlinear hue sine/cosine representation is rebuilt.
    for taxon in np.unique(taxa):
        idx = taxa == taxon
        if not np.allclose(effects[idx].mean(axis=0), 0.0, atol=1e-14, rtol=0.0):
            raise RuntimeError("Within-only unit effects acquired nonzero taxon mean")
        if not np.allclose(np.median(effects[idx], axis=0), 0.0, atol=1e-14, rtol=0.0):
            raise RuntimeError("Within-only unit effects acquired nonzero taxon median")

    return base.unit_effects_to_endpoints(
        endpoints, effects, unit_ids, endpoint_index
    ), {
        "within_only_module_scale": float(scale),
    }


def main() -> int:
    args = base.parse_args()
    v4_contract = json.loads(args.contract.read_text(encoding="utf-8"))
    priors = json.loads(args.priors.read_text(encoding="utf-8"))
    v3_contract = json.loads(args.v3_contract.read_text(encoding="utf-8"))
    validate_priors(v4_contract, priors)

    # Patch only the declared local-factor implementation.  All other generator,
    # summary, distance, replication, context and selection code is inherited.
    base.add_within_only_factor = add_within_only_factor

    targets = base.v3.load_observed(v3_contract, args.structure, args.incremental)
    context_targets = base.load_context_targets(args.environment)
    heldout = base.v3.load_v2_heldout(args.v2_heldout)[
        "full_tradeoff_common_lability"
    ]
    screen = v4_contract["screen_design"]
    draws = args.draws_per_seed or int(screen["draws_per_seed_per_family"])
    seeds = (
        [int(value) for value in args.seeds.split(",") if value.strip()]
        if args.seeds
        else [int(value) for value in screen["seeds"]]
    )
    accept_fraction = args.accept_fraction or float(screen["accept_fraction"])
    if not math.isclose(
        accept_fraction, float(screen["accept_fraction"]), rel_tol=0.0, abs_tol=0.0
    ):
        raise ValueError("The registered v4.1 screen does not allow changing accept_fraction")
    if draws <= 0 or not seeds:
        raise ValueError("Invalid v4.1 screen request")

    result = base.run_screen(
        v4_contract,
        priors,
        v3_contract,
        targets,
        context_targets,
        heldout,
        draws,
        seeds,
    )
    result["screen_version"] = "scale_specific_covariance_v4_1_screen_1"
    result["status"] = (
        "completed_nested_prior_predictive_structural_sufficiency_screen_"
        "with_zero_mean_zero_median_within_only_factor"
    )
    result["superseded_uninspected_run_boundary"] = priors["amendment_note"]
    base.write_outputs(args.out_dir, result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
