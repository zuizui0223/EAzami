from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/evidence/fdt1_tierA_effect_extraction_seed_v1.csv"


def rows() -> list[dict[str, str]]:
    with INPUT.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def as_float(value: str) -> float | None:
    return None if value == "" else float(value)


def candidate_lnrr(row: dict[str, str]) -> tuple[float | None, float | None]:
    ma = as_float(row["mean_a"])
    mb = as_float(row["mean_b"])
    sea = as_float(row["se_a"])
    seb = as_float(row["se_b"])
    if ma is not None and mb is not None and ma > 0 and mb > 0:
        est = math.log(ma / mb)
        if sea is not None and seb is not None:
            # Delta-method approximation from reported mean ± SE.
            se = math.sqrt((sea / ma) ** 2 + (seb / mb) ** 2)
            return est, se
        return est, None
    if row["effect_id"] == "TA_STK_BEJARIA_FRUIT":
        # The paper reports washed/non-sticky fruit set as 32.5% lower than sticky control.
        return math.log(1.0 / 0.675), None
    if row["effect_id"] == "TA_ORI_MERT_FUS":
        # Horizontal seed set reported as 36% higher than upright on average.
        return math.log(1.36), None
    return None, None


def build() -> dict:
    data = rows()
    ids = [r["effect_id"] for r in data]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate Tier-A effect_id")

    extracted = []
    for row in data:
        estimate, se = candidate_lnrr(row)
        extracted.append({
            "effect_id": row["effect_id"],
            "candidate_lnRR_A_over_B": None if estimate is None else round(estimate, 6),
            "candidate_delta_SE": None if se is None else round(se, 6),
            "variance_status": row["variance_status"],
            "independence_cluster": row["independence_cluster"],
            "primary_or_mediator": row["primary_or_mediator"],
        })

    primary = [r for r in data if r["primary_or_mediator"] == "primary_fitness"]
    exact_primary = [r for r in primary if r["mean_a"] and r["mean_b"] and r["se_a"] and r["se_b"]]
    variance_missing_primary = [r for r in primary if "missing" in r["variance_status"] or "not_yet" in r["variance_status"]]

    return {
        "contract_version": "fdt1_tierA_effect_extraction_seed_v1",
        "effect_rows": len(data),
        "independence_clusters": len({r["independence_cluster"] for r in data}),
        "module_counts": dict(sorted(Counter(r["module"] for r in data).items())),
        "primary_fitness_rows": len(primary),
        "primary_fitness_rows_with_reported_mean_se": len(exact_primary),
        "primary_fitness_rows_needing_more_variance_or_exact_values": len(variance_missing_primary),
        "candidate_effects": extracted,
        "key_quantitative_seed": {
            "Polygonatum_seed_number_lnRR_downward_over_upward": next(x["candidate_lnRR_A_over_B"] for x in extracted if x["effect_id"] == "TA_ORI_POLY_SEEDNUM"),
            "Polygonatum_seed_number_delta_SE": next(x["candidate_delta_SE"] for x in extracted if x["effect_id"] == "TA_ORI_POLY_SEEDNUM"),
            "Thunia_fruit_set_lnRR_intact_over_removed_bracts": next(x["candidate_lnRR_A_over_B"] for x in extracted if x["effect_id"] == "TA_DEF_THUNIA_FRUIT"),
            "Thunia_fruit_set_delta_SE": next(x["candidate_delta_SE"] for x in extracted if x["effect_id"] == "TA_DEF_THUNIA_FRUIT"),
            "Bejaria_fruit_set_lnRR_sticky_over_washed_from_reported_32_5pct_drop": next(x["candidate_lnRR_A_over_B"] for x in extracted if x["effect_id"] == "TA_STK_BEJARIA_FRUIT"),
        },
        "decision": "Tier-A literature already contains directly extractable fitness effects for orientation and protective bracts, while several otherwise strong systems still require exact table/figure extraction. Do not meta-analyze these rows together: module, mechanism, endpoint and data-generation cluster remain distinct.",
        "next_extraction_order": [
            "complete exact orientation effects for Mertensia and Platycodon where reconstructable",
            "extract year/population-specific Pedicularis bract-drainage effects",
            "extract Rheum bract-removal fecundity and seed-predation pathways",
            "recover Bejaria manipulated fruit-set variance/n",
            "recover Ipomopsis display-treatment pollinator, enemy and maternal-fitness contrasts"
        ],
        "claim_boundary": "Delta-method SE values are provisional arithmetic transforms of published mean±SE and are not final sampling variances for binomial/clustered GLM endpoints. Final meta-analysis must use the most appropriate reconstructable sampling model and one preregistered primary endpoint per data-generation cluster."
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    out = build()
    text = json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
