import csv
import itertools
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/evidence/experimental_pollinator_selection_gradients_v1.csv"
OUTPUT = ROOT / "data/evidence/experimental_pollinator_selection_leverage_meta_v1.json"
ARTICLE_CLASS = ROOT / "data/evidence/experimental_pollinator_selection_article_class_v1.csv"

PRIMARY_CLASSES = ["phenology", "plant_display", "flower_sensory", "pollination_efficiency"]


def f(x):
    return float(x) if x not in (None, "") else math.nan


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else math.nan


def median(xs):
    xs = sorted(xs)
    n = len(xs)
    if not n:
        return math.nan
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


def exact_signflip_p(values):
    values = list(values)
    if not values:
        return math.nan
    observed = abs(mean(values))
    exceed = 0
    total = 0
    for signs in itertools.product((-1.0, 1.0), repeat=len(values)):
        stat = abs(mean(v * s for v, s in zip(values, signs)))
        total += 1
        if stat + 1e-15 >= observed:
            exceed += 1
    return exceed / total


def loo_range(values_by_article):
    articles = list(values_by_article)
    if len(articles) <= 1:
        return [math.nan, math.nan]
    vals = []
    for left in articles:
        kept = [v for a, v in values_by_article.items() if a != left]
        vals.append(mean(kept))
    return [min(vals), max(vals)]


def read_rows():
    with INPUT.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    for r in rows:
        r["publication_year"] = int(r["publication_year"])
        r["included_primary"] = int(r["included_primary"])
        r["delta_beta"] = f(r["delta_beta"])
        stored_se = f(r["se_delta"])
        if r["se_delta_source"] == "computed_independent_groups":
            # Recompute from the published rounded treatment-specific SEs instead of
            # trusting a hand-entered derived value.
            r["se_delta"] = math.sqrt(f(r["se_open"]) ** 2 + f(r["se_hand"]) ** 2)
            r["stored_vs_recomputed_se_abs_diff"] = abs(stored_se - r["se_delta"])
        else:
            r["se_delta"] = stored_se
            r["stored_vs_recomputed_se_abs_diff"] = 0.0
        r["abs_delta"] = abs(r["delta_beta"])
        # Sensitivity only: a truncated noise-subtracted magnitude proxy.
        r["noise_subtracted_strength"] = math.sqrt(max(r["delta_beta"] ** 2 - r["se_delta"] ** 2, 0.0))
    return rows


def article_class_table(rows):
    grouped = defaultdict(list)
    for r in rows:
        if r["included_primary"] != 1 or r["functional_class"] not in PRIMARY_CLASSES:
            continue
        grouped[(r["article_cluster"], r["functional_class"])].append(r)
    out = []
    for (article, cls), rr in sorted(grouped.items()):
        out.append({
            "article_cluster": article,
            "functional_class": cls,
            "publication_year": min(x["publication_year"] for x in rr),
            "n_gradient_rows": len(rr),
            "mean_abs_delta": mean(x["abs_delta"] for x in rr),
            "mean_noise_subtracted_strength": mean(x["noise_subtracted_strength"] for x in rr),
        })
    return out


def write_article_class(rows):
    fields = ["article_cluster", "functional_class", "publication_year", "n_gradient_rows", "mean_abs_delta", "mean_noise_subtracted_strength"]
    with ARTICLE_CLASS.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def summarize_classes(ac_rows, min_year=None):
    classes = {}
    for cls in PRIMARY_CLASSES:
        vals = [r["mean_abs_delta"] for r in ac_rows if r["functional_class"] == cls and (min_year is None or r["publication_year"] >= min_year)]
        noise = [r["mean_noise_subtracted_strength"] for r in ac_rows if r["functional_class"] == cls and (min_year is None or r["publication_year"] >= min_year)]
        if vals:
            classes[cls] = {
                "n_articles": len(vals),
                "article_balanced_mean_abs_delta": mean(vals),
                "article_balanced_median_abs_delta": median(vals),
                "article_balanced_mean_noise_subtracted_strength": mean(noise),
            }
    return classes


def paired_contrast(ac_rows, class_a, class_b):
    by = defaultdict(dict)
    for r in ac_rows:
        by[r["article_cluster"]][r["functional_class"]] = r["mean_abs_delta"]
    diffs = {}
    for article, d in by.items():
        if class_a in d and class_b in d:
            diffs[article] = d[class_a] - d[class_b]
    values = list(diffs.values())
    return {
        "class_a": class_a,
        "class_b": class_b,
        "n_paired_articles": len(values),
        "article_differences": diffs,
        "mean_difference_abs_delta": mean(values) if values else math.nan,
        "two_sided_exact_signflip_p": exact_signflip_p(values),
        "leave_one_article_out_mean_difference_range": loo_range(diffs),
    }


def lobelia_context_test(rows):
    rr = [r for r in rows if r["article_cluster"] == "Lobelia2023" and r["included_primary"] == 1]
    by_trait = defaultdict(dict)
    class_by_trait = {}
    for r in rr:
        by_trait[r["trait"]][r["context"]] = r["abs_delta"]
        class_by_trait[r["trait"]] = r["functional_class"]
    differences = {}
    class_diffs = defaultdict(list)
    for trait, d in by_trait.items():
        if "ambient" in d and "reduced" in d:
            diff = d["reduced"] - d["ambient"]
            differences[trait] = diff
            class_diffs[class_by_trait[trait]].append(diff)
    vals = list(differences.values())
    return {
        "pollen_limitation_log_response_ratio": {
            "ambient": {"estimate": 0.062, "se": 0.065},
            "reduced": {"estimate": 0.259, "se": 0.072},
        },
        "trait_abs_selection_change_reduced_minus_ambient": differences,
        "mean_abs_selection_change": mean(vals),
        "traits_stronger_under_reduced": sum(v > 0 for v in vals),
        "traits_weaker_under_reduced": sum(v < 0 for v in vals),
        "two_sided_exact_signflip_p_exploratory": exact_signflip_p(vals),
        "class_mean_changes": {k: mean(v) for k, v in sorted(class_diffs.items())},
        "boundary": "Within one experiment; trait-level sign-flip is exploratory because gradients share plants and the supplemental reference group.",
    }


def main():
    rows = read_rows()
    primary = [r for r in rows if r["included_primary"] == 1 and r["functional_class"] in PRIMARY_CLASSES]
    articles = sorted({r["article_cluster"] for r in primary})
    taxa = sorted({r["taxon"] for r in primary})
    ac = article_class_table(rows)
    write_article_class(ac)

    contrasts = [
        paired_contrast(ac, "pollination_efficiency", "flower_sensory"),
        paired_contrast(ac, "pollination_efficiency", "plant_display"),
        paired_contrast(ac, "plant_display", "flower_sensory"),
        paired_contrast(ac, "phenology", "plant_display"),
        paired_contrast(ac, "phenology", "flower_sensory"),
    ]
    identified = [c for c in contrasts if c["n_paired_articles"] >= 3 and c["two_sided_exact_signflip_p"] < 0.05]

    summary = {
        "version": "v1",
        "analysis_question": "Does broad floral functional class robustly predict the strength of experimentally isolated pollinator-mediated directional selection, and does stronger pollen limitation uniformly strengthen selection?",
        "primary_gradient_rows": len(primary),
        "independent_article_clusters": len(articles),
        "taxon_count": len(taxa),
        "articles": articles,
        "taxa": taxa,
        "max_abs_stored_vs_recomputed_delta_se_difference": max(r["stored_vs_recomputed_se_abs_diff"] for r in rows),
        "functional_class_summary_all": summarize_classes(ac),
        "functional_class_summary_post2018_sensitivity": summarize_classes(ac, min_year=2019),
        "paired_article_contrasts": contrasts,
        "functional_class_hierarchy_identified": bool(identified),
        "significant_paired_class_contrasts": identified,
        "lobelia_pollinator_decline_context_test": lobelia_context_test(rows),
        "interpretation": {
            "functional_class": "This restricted article-balanced reanalysis does not identify a universal hierarchy among phenology, plant display, flower sensory/display and pollination-efficiency classes. Broad functional class is therefore an incomplete proxy for the trait-to-interaction leverage operating in a particular population.",
            "interaction_intensity": "In Lobelia, experimentally increased pollen limitation increased mean absolute pollinator-mediated selection modestly but not uniformly across traits; interaction intensity creates opportunity for selection but does not determine every trait response.",
            "refined_hypothesis": "Realized biotic selection is generated by interaction intensity x local trait-to-interaction functional leverage x downstream fitness gating, rather than by agent intensity or broad trait class alone.",
        },
        "claim_boundary": "Restricted experimental-gradient meta-analysis using published standardized directional selection gradients. Article-balanced magnitude summaries are not an inverse-variance random-effects estimate; exact paired sign-flip tests preserve article clustering. Functional classifications are prospective ecological labels and uncertain classifications are excluded from the primary analysis.",
    }
    OUTPUT.write_text(json.dumps(summary, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
