from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/evidence/experimental_pollinator_selection_gradients_v1.csv"

PIGMENT_TRAITS = {
    "petal_brightness",
    "petal_chroma",
    "lip_patch_size",
    "lip_patch_contrast",
    "lip_spot_area",
}
SIZE_TRAITS = {"corolla_size", "corolla_area", "corolla_projected_area", "flower_size"}


def module_for(row: dict[str, str]) -> str | None:
    if row["included_primary"] != "1":
        return None
    if row["functional_class"] == "plant_display":
        return "display_quantity_analog"
    if row["trait"] in PIGMENT_TRAITS:
        return "pigmentation_sensory_analog"
    if row["trait"] in SIZE_TRAITS:
        return "flower_size_display_proxy"
    if row["functional_class"] == "pollination_efficiency":
        return "pollination_efficiency_reference"
    return None


def read_rows() -> list[dict[str, str]]:
    with INPUT.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def summarize_module(rows: list[dict[str, str]], module: str) -> dict:
    selected = [r for r in rows if module_for(r) == module]
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in selected:
        grouped[row["article_cluster"]].append(abs(float(row["delta_beta"])))
    article_means = {
        article: sum(values) / len(values)
        for article, values in sorted(grouped.items())
    }
    vals = list(article_means.values())
    mean = sum(vals) / len(vals) if vals else None
    loo = []
    if len(vals) >= 2:
        for omitted in article_means:
            kept = [v for a, v in article_means.items() if a != omitted]
            loo.append(sum(kept) / len(kept))
    return {
        "module": module,
        "effect_rows": len(selected),
        "article_count": len(article_means),
        "article_mean_abs_delta_beta": {k: round(v, 6) for k, v in article_means.items()},
        "article_balanced_mean_abs_delta_beta": None if mean is None else round(mean, 6),
        "leave_one_article_out_range": None if not loo else [round(min(loo), 6), round(max(loo), 6)],
        "interpretation_status": (
            "seed_only_k_lt_3" if len(article_means) < 3 else "quantitative_seed_not_final_meta"
        ),
    }


def build() -> dict:
    rows = read_rows()
    modules = [
        "display_quantity_analog",
        "pigmentation_sensory_analog",
        "flower_size_display_proxy",
        "pollination_efficiency_reference",
    ]
    summaries = [summarize_module(rows, m) for m in modules]
    by_module = {x["module"]: x for x in summaries}

    return {
        "contract_version": "existing_capitulum_module_pollinator_analogs_v1",
        "source": INPUT.relative_to(ROOT).as_posix(),
        "estimand": "absolute experimentally isolated pollinator-mediated directional selection magnitude |delta_beta|",
        "collapse_rule": "mean within article x module analog, then equal-weight articles; repeated years/contexts remain within article cluster",
        "modules": summaries,
        "key_result": {
            "display_quantity_analog_mean": by_module["display_quantity_analog"]["article_balanced_mean_abs_delta_beta"],
            "pigmentation_sensory_analog_mean": by_module["pigmentation_sensory_analog"]["article_balanced_mean_abs_delta_beta"],
            "flower_size_display_proxy_mean": by_module["flower_size_display_proxy"]["article_balanced_mean_abs_delta_beta"],
            "pollination_efficiency_reference_mean": by_module["pollination_efficiency_reference"]["article_balanced_mean_abs_delta_beta"],
            "pigmentation_article_count": by_module["pigmentation_sensory_analog"]["article_count"],
        },
        "decision": "Existing gradients provide quantitative seeds for display and pigmentation hypotheses, but no EAzami module ranking is authorized. Pigmentation has only two independent articles and a wide leave-one-article-out range; orientation, spine/phyllary and stickiness are not represented by homologous pollinator-selection gradients.",
        "claim_boundary": "These are analogs from non-Cirsium flowering plants and use selection-gradient magnitude, not direct trait->mechanism response ratios. Direction is not pooled because increasing different traits is not biologically homologous. This pilot informs search priorities but is not the final FDT1 cross-module meta-analysis.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    out = build()
    text = json.dumps(out, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
