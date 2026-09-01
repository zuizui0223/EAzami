#!/usr/bin/env python3
"""Compare all 63 matched Azami and EAzami trait-environment rows.

Azami is an external frozen comparison surface here. It is not used to select
EAzami rows. Primary direction comparison uses Azami among-taxon min5 versus the
EAzami ML branch-aware coefficient because both are taxon-level estimands.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--contract", type=Path, required=True)
    p.add_argument("--topology-json", type=Path, required=True)
    p.add_argument("--azami-among", type=Path, required=True)
    p.add_argument("--azami-within", type=Path, required=True)
    p.add_argument("--out-json", type=Path, required=True)
    p.add_argument("--out-csv", type=Path, required=True)
    return p.parse_args()


def finite(value) -> float | None:
    try:
        out = float(value)
    except Exception:
        return None
    return out if np.isfinite(out) else None


def sign(value: float | None) -> int:
    if value is None or not np.isfinite(value) or value == 0:
        return 0
    return 1 if value > 0 else -1


def direction_class(a: float | None, b: float | None) -> str:
    sa, sb = sign(a), sign(b)
    if sa == 0 or sb == 0:
        return "not_comparable"
    return "concordant_direction" if sa == sb else "discordant_direction"


def support_pattern(azami: bool, eazami: bool) -> str:
    if azami and eazami:
        return "both_bh_supported"
    if azami:
        return "azami_only_bh_supported"
    if eazami:
        return "eazami_only_bh_supported"
    return "neither_bh_supported"


def main() -> int:
    args = parse_args()
    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    topology = json.loads(args.topology_json.read_text(encoding="utf-8"))
    among = pd.read_csv(args.azami_among, encoding="utf-8-sig")
    within = pd.read_csv(args.azami_within, encoding="utf-8-sig")

    if topology.get("n_rows") != 63:
        raise AssertionError("EAzami topology input is not the complete 63-row atlas")

    among = among.loc[
        among["scope"].astype(str).eq(contract["azami_source"]["among_scope"])
        & among["status"].astype(str).eq("ok")
    ].copy()
    within = within.loc[
        within["scope"].astype(str).eq(contract["azami_source"]["within_scope"])
        & within["status"].astype(str).eq("ok")
    ].copy()

    e_rows = {(r["trait"], r["environment"]): r for r in topology["rows"]}
    if len(e_rows) != 63:
        raise AssertionError("EAzami rows are not unique 7 x 9 keys")

    trait_map = contract["trait_mapping"]
    env_map = contract["environment_mapping"]
    rows: list[dict] = []

    for trait, azami_unit in trait_map.items():
        for env, azami_predictor in env_map.items():
            key = (trait, env)
            e = e_rows[key]
            a = among.loc[(among["unit_id"] == azami_unit) & (among["predictor"] == azami_predictor)]
            w = within.loc[(within["unit_id"] == azami_unit) & (within["predictor"] == azami_predictor)]
            if len(a) != 1 or len(w) != 1:
                raise AssertionError(
                    f"Expected one Azami among and within row for {key}; got {len(a)}, {len(w)}"
                )
            a = a.iloc[0]
            w = w.iloc[0]
            azami_among_beta = finite(a.get("beta_std"))
            azami_within_beta = finite(w.get("beta_std"))
            e_raw = finite(e.get("atlas8_spearman_rho"))
            e_ml = finite(e.get("ml_branch_aware_beta"))
            azami_among_q = finite(a.get("q_fdr_bh_global_family"))
            azami_within_q = finite(w.get("q_fdr_bh_global_family"))
            e_raw_q = finite(e.get("atlas8_bh_q_63"))
            e_ml_q = finite(e.get("ml_bh_q_63"))
            azami_among_supported = bool(azami_among_q is not None and azami_among_q < 0.05)
            azami_within_supported = bool(azami_within_q is not None and azami_within_q < 0.05)
            e_raw_supported = bool(e_raw_q is not None and e_raw_q < 0.05)
            e_ml_supported = bool(e_ml_q is not None and e_ml_q < 0.05)

            rows.append({
                "trait": trait,
                "azami_endpoint": azami_unit,
                "environment": env,
                "azami_predictor": azami_predictor,
                "environment_block": e["environment_block"],
                "eazami_atlas8_rho": e_raw,
                "eazami_atlas8_exact_p": finite(e.get("atlas8_exact_p")),
                "eazami_atlas8_bh_q63": e_raw_q,
                "eazami_atlas8_bh_supported": e_raw_supported,
                "eazami_ml_beta": e_ml,
                "eazami_ml_exact_p": finite(e.get("ml_exact_permutation_p")),
                "eazami_ml_bh_q63": e_ml_q,
                "eazami_ml_bh_supported": e_ml_supported,
                "eazami_ufboot_same_sign_fraction": finite(e.get("ufboot1000_same_sign_fraction_vs_ml")),
                "eazami_topology_sign_class": e.get("topology_sign_class"),
                "azami_among_beta": azami_among_beta,
                "azami_among_p": finite(a.get("p_value")),
                "azami_among_q": azami_among_q,
                "azami_among_bh_supported": azami_among_supported,
                "azami_within_beta": azami_within_beta,
                "azami_within_p": finite(w.get("p_value")),
                "azami_within_q": azami_within_q,
                "azami_within_bh_supported": azami_within_supported,
                "primary_tree_vs_azami_among_direction": direction_class(e_ml, azami_among_beta),
                "raw_eazami_vs_azami_among_direction": direction_class(e_raw, azami_among_beta),
                "eazami_tree_vs_azami_within_direction_context": direction_class(e_ml, azami_within_beta),
                "primary_bh_support_pattern": support_pattern(azami_among_supported, e_ml_supported),
            })

    if len(rows) != 63:
        raise AssertionError(f"Expected 63 matched rows, got {len(rows)}")

    frame = pd.DataFrame(rows)
    comparable = frame.loc[frame["primary_tree_vs_azami_among_direction"] != "not_comparable"].copy()
    concordant = comparable["primary_tree_vs_azami_among_direction"].eq("concordant_direction")
    raw_comparable = frame.loc[frame["raw_eazami_vs_azami_among_direction"] != "not_comparable"].copy()
    raw_concordant = raw_comparable["raw_eazami_vs_azami_among_direction"].eq("concordant_direction")

    vector_rho = float(spearmanr(frame["eazami_ml_beta"], frame["azami_among_beta"]).statistic)
    raw_vector_rho = float(spearmanr(frame["eazami_atlas8_rho"], frame["azami_among_beta"]).statistic)

    by_trait = {}
    for trait, g in frame.groupby("trait", sort=True):
        comp = g[g["primary_tree_vs_azami_among_direction"] != "not_comparable"]
        by_trait[trait] = {
            "n_rows": int(len(g)),
            "concordant": int(comp["primary_tree_vs_azami_among_direction"].eq("concordant_direction").sum()),
            "discordant": int(comp["primary_tree_vs_azami_among_direction"].eq("discordant_direction").sum()),
            "azami_among_bh_supported": int(g["azami_among_bh_supported"].sum()),
            "eazami_ml_bh_supported": int(g["eazami_ml_bh_supported"].sum()),
            "eazami_topology_stable": int(g["eazami_topology_sign_class"].eq("stable_same_direction").sum()),
        }

    by_block = {}
    for block, g in frame.groupby("environment_block", sort=True):
        comp = g[g["primary_tree_vs_azami_among_direction"] != "not_comparable"]
        by_block[block] = {
            "n_rows": int(len(g)),
            "concordant": int(comp["primary_tree_vs_azami_among_direction"].eq("concordant_direction").sum()),
            "discordant": int(comp["primary_tree_vs_azami_among_direction"].eq("discordant_direction").sum()),
        }

    eazami_raw_leads = frame.loc[frame["eazami_atlas8_exact_p"] <= 0.05].copy()
    azami_supported = frame.loc[frame["azami_among_bh_supported"]].copy()

    summary = {
        "matched_rows": int(len(frame)),
        "primary_comparable_rows": int(len(comparable)),
        "primary_concordant_rows": int(concordant.sum()),
        "primary_discordant_rows": int((~concordant).sum()),
        "primary_concordance_fraction": float(concordant.mean()),
        "raw_concordance_fraction": float(raw_concordant.mean()),
        "effect_vector_spearman_eazami_ml_vs_azami_among": vector_rho,
        "effect_vector_spearman_eazami_raw_vs_azami_among": raw_vector_rho,
        "azami_among_bh_supported_mapped_rows": int(frame["azami_among_bh_supported"].sum()),
        "azami_within_bh_supported_mapped_rows": int(frame["azami_within_bh_supported"].sum()),
        "eazami_raw_bh_supported_rows": int(frame["eazami_atlas8_bh_supported"].sum()),
        "eazami_ml_bh_supported_rows": int(frame["eazami_ml_bh_supported"].sum()),
        "eazami_topology_stable_rows": int(frame["eazami_topology_sign_class"].eq("stable_same_direction").sum()),
        "eazami_raw_p_le_0_05_rows": eazami_raw_leads.to_dict("records"),
        "azami_among_bh_supported_rows": azami_supported.to_dict("records"),
        "by_trait": by_trait,
        "by_environment_block": by_block,
    }

    result = {
        "contract_version": "chapter2_azami_eazami_concordance_v1",
        "status_date": "2026-09-01",
        "scope": "post-freeze cross-chapter comparison of all 63 commensurate trait x environment rows",
        "sources": {
            "azami": contract["azami_source"],
            "eazami": contract["eazami_source"],
        },
        "trait_mapping": trait_map,
        "environment_mapping": env_map,
        "rows": rows,
        "summary": summary,
        "interpretation_boundary": (
            "Azami among-taxon and EAzami taxon-level directions are comparable as broad species-level "
            "effect directions, but they are not the same coefficient because taxon sets, geographic extents "
            "and estimators differ. Concordance is descriptive consistency; discordance is a lineage/scale "
            "difference that requires historical or mechanistic testing rather than post hoc row selection."
        ),
        "claim_boundary": contract["claim_boundary"],
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    frame.to_csv(args.out_csv, index=False)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
