#!/usr/bin/env python3
"""Generate Azami-compatible synthetic 18D capitulum phenotypes on a fixed environment design.

The environment design is exogenous conditioning information.  No observed response
phenotype or Azami target value is read by this generator.  Model families and priors
are frozen in azami_capitulum_v3_generator_contract_v1.json before target distances
are inspected.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

AZAMI_CAPITULUM_V3_OBSERVATION_SCHEMA = "azami_capitulum_v3_estimand_contract_v1"

ENDPOINTS = [
    "orientation_image_vertical_angle",
    "corolla_lab_lightness",
    "corolla_lab_chroma",
    "corolla_hue_sin",
    "corolla_hue_cos",
    "capitulum_outline_aspect_ratio",
    "capitulum_outline_circularity",
    "capitulum_outline_solidity",
    "capitulum_width_profile_cv",
    "involucre_length_width_ratio",
    "involucre_apical_taper_ratio",
    "involucre_basal_taper_ratio",
    "bract_projection_roughness",
    "bract_projection_p95",
    "bract_spread_fraction",
    "bract_projection_asymmetry",
    "bract_projection_maximum",
    "bract_projection_peak_density",
]
ENVIRONMENT = [
    "chelsa_bio01",
    "chelsa_bio04",
    "chelsa_bio12",
    "chelsa_bio15",
    "chelsa_rsds_mean",
    "chelsa_vpd_mean",
    "chelsa_sfcwind_mean",
    "chelsa_gsp",
    "chelsa_npp",
]
CORE4 = ["chelsa_bio01", "chelsa_bio04", "chelsa_bio12", "chelsa_bio15"]
PROCESS5 = ["chelsa_rsds_mean", "chelsa_vpd_mean", "chelsa_sfcwind_mean", "chelsa_gsp", "chelsa_npp"]
HUE = {"corolla_hue_sin", "corolla_hue_cos"}

MODULE_BY_ENDPOINT = {
    "orientation_image_vertical_angle": "orientation",
    "corolla_lab_lightness": "colour",
    "corolla_lab_chroma": "colour",
    "corolla_hue_sin": "colour",
    "corolla_hue_cos": "colour",
    "capitulum_outline_aspect_ratio": "shape",
    "capitulum_outline_circularity": "shape",
    "capitulum_outline_solidity": "shape",
    "capitulum_width_profile_cv": "shape",
    "involucre_length_width_ratio": "involucre_architecture",
    "involucre_apical_taper_ratio": "involucre_architecture",
    "involucre_basal_taper_ratio": "involucre_architecture",
    "bract_projection_roughness": "involucre_architecture",
    "bract_projection_p95": "involucre_architecture",
    "bract_spread_fraction": "involucre_architecture",
    "bract_projection_asymmetry": "involucre_architecture",
    "bract_projection_maximum": "armature",
    "bract_projection_peak_density": "armature",
}
MODULES = sorted(set(MODULE_BY_ENDPOINT.values()))

FAMILY_AXES = {
    "NULL_COUPLED": ("NONE", "SHARED", "COUPLED"),
    "NULL_MODULAR": ("NONE", "SHARED", "MODULAR"),
    "CORE4_SHARED_COUPLED": ("CORE4", "SHARED", "COUPLED"),
    "CORE4_SHARED_MODULAR": ("CORE4", "SHARED", "MODULAR"),
    "CORE4_INDEPENDENT_COUPLED": ("CORE4", "INDEPENDENT", "COUPLED"),
    "CORE4_INDEPENDENT_MODULAR": ("CORE4", "INDEPENDENT", "MODULAR"),
    "PROCESS_BOTH_SHARED_COUPLED": ("PROCESS_BOTH", "SHARED", "COUPLED"),
    "PROCESS_BOTH_SHARED_MODULAR": ("PROCESS_BOTH", "SHARED", "MODULAR"),
    "PROCESS_BOTH_INDEPENDENT_COUPLED": ("PROCESS_BOTH", "INDEPENDENT", "COUPLED"),
    "PROCESS_BOTH_INDEPENDENT_MODULAR": ("PROCESS_BOTH", "INDEPENDENT", "MODULAR"),
    "PROCESS_AMONG_ONLY_SHARED_COUPLED": ("PROCESS_AMONG_ONLY", "SHARED", "COUPLED"),
    "PROCESS_AMONG_ONLY_SHARED_MODULAR": ("PROCESS_AMONG_ONLY", "SHARED", "MODULAR"),
    "PROCESS_AMONG_ONLY_INDEPENDENT_COUPLED": ("PROCESS_AMONG_ONLY", "INDEPENDENT", "COUPLED"),
    "PROCESS_AMONG_ONLY_INDEPENDENT_MODULAR": ("PROCESS_AMONG_ONLY", "INDEPENDENT", "MODULAR"),
}


def stable_seed(seed: int, *parts: str) -> int:
    payload = "|".join([str(seed), *parts]).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "little")


def stable_rng(seed: int, *parts: str) -> np.random.Generator:
    return np.random.default_rng(stable_seed(seed, *parts))


def endpoint_loading(endpoint: str) -> float:
    digest = hashlib.sha256(endpoint.encode("utf-8")).digest()
    u = int.from_bytes(digest[:8], "little") / float(2**64 - 1)
    return 0.80 + 0.40 * u


def weighted_standardize_columns(frame: pd.DataFrame, taxa: pd.Series) -> pd.DataFrame:
    counts = taxa.value_counts()
    weights = taxa.map(lambda x: 1.0 / counts[x]).to_numpy(float)
    w = weights / weights.sum()
    a = frame.to_numpy(float)
    mu = (w[:, None] * a).sum(axis=0)
    var = (w[:, None] * (a - mu) ** 2).sum(axis=0)
    sd = np.sqrt(var)
    if np.any(~np.isfinite(sd)) or np.any(sd <= 0):
        raise ValueError("invalid weighted environment standard deviation")
    return pd.DataFrame((a - mu) / sd, columns=frame.columns, index=frame.index)


def standardize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    a = frame.to_numpy(float)
    sd = a.std(axis=0, ddof=0)
    if np.any(~np.isfinite(sd)) or np.any(sd <= 0):
        raise ValueError("invalid environment standard deviation")
    return pd.DataFrame((a - a.mean(axis=0)) / sd, columns=frame.columns, index=frame.index)


def validate_design(design: pd.DataFrame, contract: dict, strict_frozen_design: bool) -> pd.DataFrame:
    required = ["design_row_id", "taxon_name", *ENVIRONMENT]
    missing = [x for x in required if x not in design.columns]
    if missing:
        raise ValueError(f"environment design missing columns: {missing}")
    if design["design_row_id"].astype(str).duplicated().any():
        raise ValueError("design_row_id must be unique")
    out = design[required].copy()
    for col in ENVIRONMENT:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    if out[ENVIRONMENT].isna().any().any():
        raise ValueError("all nine environment predictors must be finite")
    if strict_frozen_design:
        d = contract["environment_design"]
        if len(out) != int(d["expected_rows"]):
            raise ValueError("frozen design row count mismatch")
        if out["taxon_name"].nunique() != int(d["expected_taxa"]):
            raise ValueError("frozen design taxon count mismatch")
        counts = out.groupby("taxon_name").size()
        if int((counts >= 5).sum()) != int(d["expected_taxa_min5"]):
            raise ValueError("frozen design min5 taxon count mismatch")
        if int((counts >= 2).sum()) != int(d["expected_taxa_min2"]):
            raise ValueError("frozen design min2 taxon count mismatch")
    return out


def environment_components(design: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    med = design.groupby("taxon_name")[ENVIRONMENT].median()
    med_z = standardize_columns(med)
    among = design[["taxon_name"]].join(med_z, on="taxon_name")[ENVIRONMENT]

    centred = design[ENVIRONMENT] - design.groupby("taxon_name")[ENVIRONMENT].transform("mean")
    within = weighted_standardize_columns(centred, design["taxon_name"])
    return among, within


def allowed_predictors(environment_mode: str, scale: str) -> list[str]:
    if environment_mode == "NONE":
        return []
    if environment_mode == "CORE4":
        return CORE4[:]
    if environment_mode == "PROCESS_BOTH":
        return [*CORE4, *PROCESS5]
    if environment_mode == "PROCESS_AMONG_ONLY":
        return [*CORE4, *PROCESS5] if scale == "among" else CORE4[:]
    raise ValueError(environment_mode)


def coefficient_vector(
    module: str,
    scale: str,
    environment_mode: str,
    scale_architecture: str,
    seed: int,
    contract: dict,
) -> dict[str, float]:
    priors = contract["priors"]
    out = {p: 0.0 for p in ENVIRONMENT}
    permitted = allowed_predictors(environment_mode, scale)
    for predictor in permitted:
        sd = float(priors["core_module_coefficient_sd"] if predictor in CORE4 else priors["process_module_coefficient_sd"])
        coefficient_scale_key = "shared" if scale_architecture == "SHARED" else scale
        rng = stable_rng(seed, "coef", module, predictor, coefficient_scale_key)
        out[predictor] = float(rng.normal(0.0, sd))
    return out


def environmental_effect(component: pd.DataFrame, coefficients: dict[str, float]) -> np.ndarray:
    effect = np.zeros(len(component), dtype=float)
    for predictor, beta in coefficients.items():
        if beta != 0.0:
            effect += component[predictor].to_numpy(float) * beta
    return effect


def module_residuals(
    n_rows: int,
    n_taxa: int,
    taxon_codes: np.ndarray,
    residual_architecture: str,
    scale: str,
    seed: int,
    contract: dict,
) -> dict[str, np.ndarray]:
    priors = contract["priors"]
    residual_sd = float(priors["among_taxon_residual_sd"] if scale == "among" else priors["within_taxon_residual_sd"])
    if scale == "among":
        size = n_taxa
    else:
        size = n_rows

    if residual_architecture == "COUPLED":
        f = float(priors["coupled_shared_residual_variance_fraction"])
        shared = stable_rng(seed, "residual", scale, "shared").normal(0.0, 1.0, size=size)
        result = {}
        for module in MODULES:
            specific = stable_rng(seed, "residual", scale, module).normal(0.0, 1.0, size=size)
            latent = residual_sd * (np.sqrt(f) * shared + np.sqrt(1.0 - f) * specific)
            result[module] = latent[taxon_codes] if scale == "among" else latent
        return result
    if residual_architecture == "MODULAR":
        result = {}
        for module in MODULES:
            latent = stable_rng(seed, "residual", scale, module).normal(0.0, residual_sd, size=size)
            result[module] = latent[taxon_codes] if scale == "among" else latent
        return result
    raise ValueError(residual_architecture)


def generate(design: pd.DataFrame, family: str, seed: int, contract: dict, strict_frozen_design: bool = False) -> pd.DataFrame:
    if family not in FAMILY_AXES:
        raise ValueError(f"unknown model family {family}")
    if family not in contract["model_families"]:
        raise ValueError(f"family {family} not frozen in generator contract")
    design = validate_design(design, contract, strict_frozen_design)
    environment_mode, scale_architecture, residual_architecture = FAMILY_AXES[family]
    among_env, within_env = environment_components(design)

    taxa = sorted(design["taxon_name"].astype(str).unique())
    taxon_index = {taxon: i for i, taxon in enumerate(taxa)}
    taxon_codes = design["taxon_name"].astype(str).map(taxon_index).to_numpy(int)

    among_resid = module_residuals(len(design), len(taxa), taxon_codes, residual_architecture, "among", seed, contract)
    within_resid = module_residuals(len(design), len(taxa), taxon_codes, residual_architecture, "within", seed, contract)
    module_latent: dict[str, np.ndarray] = {}

    for module in MODULES:
        ba = coefficient_vector(module, "among", environment_mode, scale_architecture, seed, contract)
        bw = coefficient_vector(module, "within", environment_mode, scale_architecture, seed, contract)
        among_effect = environmental_effect(among_env, ba)
        within_effect = environmental_effect(within_env, bw)
        module_latent[module] = among_effect + within_effect + among_resid[module] + within_resid[module]

    output = design.copy()
    output = output.rename(columns={"design_row_id": "obs_id"})
    priors = contract["priors"]
    endpoint_noise_sd = float(priors["endpoint_noise_sd"])

    colour_latent = module_latent["colour"]
    theta = (
        0.60 * colour_latent
        + stable_rng(seed, "endpoint", "corolla_hue_theta").normal(0.0, 0.35, size=len(output))
    )
    for endpoint in ENDPOINTS:
        if endpoint == "corolla_hue_sin":
            output[endpoint] = np.sin(theta)
        elif endpoint == "corolla_hue_cos":
            output[endpoint] = np.cos(theta)
        else:
            module = MODULE_BY_ENDPOINT[endpoint]
            noise = stable_rng(seed, "endpoint", endpoint).normal(0.0, endpoint_noise_sd, size=len(output))
            output[endpoint] = endpoint_loading(endpoint) * module_latent[module] + noise

    columns = ["obs_id", "taxon_name", *ENVIRONMENT, *ENDPOINTS]
    result = output[columns].copy()
    if len(result) != len(design) or result["obs_id"].duplicated().any():
        raise RuntimeError("v3 generator output identity failure")
    if result[[*ENVIRONMENT, *ENDPOINTS]].isna().any().any():
        raise RuntimeError("v3 generator emitted nonfinite values")
    return result


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--design", type=Path, required=True)
    p.add_argument("--family", required=True, choices=list(FAMILY_AXES))
    p.add_argument("--seed", type=int, default=20260827)
    p.add_argument("--contract", type=Path, default=Path("data/evidence/azami_capitulum_v3_generator_contract_v1.json"))
    p.add_argument("--strict-frozen-design", action="store_true")
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    contract = json.loads(a.contract.read_text(encoding="utf-8"))
    design = pd.read_csv(a.design, low_memory=False)
    result = generate(design, a.family, a.seed, contract, a.strict_frozen_design)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(a.out, index=False)
    print(json.dumps({
        "schema": AZAMI_CAPITULUM_V3_OBSERVATION_SCHEMA,
        "generator_contract": contract["contract_version"],
        "family": a.family,
        "seed": a.seed,
        "rows": len(result),
        "taxa": int(result["taxon_name"].nunique()),
        "response_endpoints": len(ENDPOINTS),
        "environment_predictors": len(ENVIRONMENT),
        "claim_boundary": "synthetic phenotype generation only; no target distance or mechanism claim",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
