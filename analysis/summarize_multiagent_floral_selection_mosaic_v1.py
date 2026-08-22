import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/evidence/multiagent_floral_selection_mosaic_registry_v1.csv"
OUTPUT = ROOT / "data/evidence/multiagent_floral_selection_mosaic_summary_v1.json"

DOMINANCE_MAP = {
    "pollinator_dominant": "pollinator",
    "antagonist_dominant": "antagonist",
    "similar_or_trait_dependent": "mixed",
    "mosaic_no_fixed_dominance": "mixed",
    "antagonist_context_suppresses_pollinator_selection": "mixed",
    "mixed_dual_role_agent": "mixed",
}


def load_rows():
    with INPUT.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        for key in [
            "pollination_manipulated",
            "antagonist_manipulated",
            "strict_primary",
            "opposing_or_reinforcing_same_trait",
            "context_dependence_or_nonadditivity",
        ]:
            row[key] = int(row[key])
        row["publication_year"] = int(row["publication_year"])
        row["dominance_class"] = DOMINANCE_MAP[row["agent_dominance"]]
    return rows


def collapse_programs(rows):
    grouped = defaultdict(list)
    for r in rows:
        grouped[r["program_cluster"]].append(r)
    out = []
    for program, rr in sorted(grouped.items()):
        doms = {r["dominance_class"] for r in rr}
        dominance = next(iter(doms)) if len(doms) == 1 else "mixed"
        out.append(
            {
                "program_cluster": program,
                "taxa": sorted({r["taxon"] for r in rr}),
                "dominance_class": dominance,
                "context_dependence_or_nonadditivity": max(r["context_dependence_or_nonadditivity"] for r in rr),
                "opposing_or_reinforcing_same_trait": max(r["opposing_or_reinforcing_same_trait"] for r in rr),
                "strict_primary": max(r["strict_primary"] for r in rr),
                "studies": sorted(r["study_id"] for r in rr),
            }
        )
    return out


def dominance_counts(rows):
    return dict(sorted(Counter(r["dominance_class"] for r in rows).items()))


def leave_one_out_category_counts(rows):
    results = {}
    for i, left in enumerate(rows):
        kept = rows[:i] + rows[i + 1 :]
        results[left["program_cluster"]] = dominance_counts(kept)
    return results


def main():
    rows = load_rows()
    programs = collapse_programs(rows)
    strict = [r for r in programs if r["strict_primary"] == 1]
    sensitivity = programs

    strict_dom = dominance_counts(strict)
    loo = leave_one_out_category_counts(strict)
    loo_min_categories = min(len(x) for x in loo.values()) if loo else 0

    strict_context = sum(r["context_dependence_or_nonadditivity"] for r in strict)
    strict_same_trait = sum(r["opposing_or_reinforcing_same_trait"] for r in strict)

    summary = {
        "version": "v1",
        "analysis_question": "Do manipulative multi-agent floral-selection studies support a universal selective-agent dominance or a context-dependent selection mosaic?",
        "registry_study_count": len(rows),
        "program_cluster_count": len(programs),
        "strict_factorial_program_count": len(strict),
        "strict_taxon_count": len({taxon for r in strict for taxon in r["taxa"]}),
        "strict_dominance_counts": strict_dom,
        "strict_context_dependence_or_nonadditivity": {
            "supported_programs": strict_context,
            "total_programs": len(strict),
            "fraction": strict_context / len(strict),
        },
        "strict_opposing_or_reinforcing_same_trait": {
            "supported_programs": strict_same_trait,
            "total_programs": len(strict),
            "fraction": strict_same_trait / len(strict),
        },
        "leave_one_program_out_dominance_counts": loo,
        "leave_one_program_out_minimum_dominance_categories": loo_min_categories,
        "fixed_pollinator_dominance_falsified": strict_dom.get("antagonist", 0) >= 2 and loo_min_categories >= 2,
        "fixed_antagonist_dominance_falsified": strict_dom.get("pollinator", 0) >= 1 and strict_dom.get("mixed", 0) >= 1 and loo_min_categories >= 2,
        "universal_nonadditivity_falsified": any(r["context_dependence_or_nonadditivity"] == 0 for r in strict),
        "universal_additivity_falsified": sum(r["context_dependence_or_nonadditivity"] == 1 for r in strict) >= 2,
        "selection_mosaic_working_support": (
            len(strict_dom) >= 3
            and loo_min_categories >= 2
            and sum(r["opposing_or_reinforcing_same_trait"] for r in strict) >= 2
        ),
        "sensitivity_program_dominance_counts": dominance_counts(sensitivity),
        "sensitivity_context_dependence_or_nonadditivity_fraction": sum(r["context_dependence_or_nonadditivity"] for r in sensitivity) / len(sensitivity),
        "interpretation": {
            "agent_dominance": "The strict factorial literature contains pollinator-dominant, antagonist-dominant, and mixed/no-fixed-dominance outcomes, and at least two dominance categories remain after leaving out any one programme. A universal pollinator- or antagonist-dominance model is therefore not defensible.",
            "additivity": "Some systems show diffuse/nonadditive selection while others show additive effects. Context dependence is common but is not itself universal; a selection mosaic can arise either from statistical nonadditivity or from additive opposing effects whose relative intensities change across populations or times.",
            "EAzami": "For focal Cirsium, the meta-level architecture supports HGA3 as a general working mechanism but does not identify which agent dominates any focal population. The decisive test remains same-population pollination x antagonist manipulation with local functional-leverage measurements on one seed-fitness scale.",
        },
        "claim_boundary": "Study-program-level falsification meta-synthesis. Heterogeneous selection metrics and designs are not pooled into a common effect size. Strict inference uses only five programmes that experimentally manipulate both pollination and antagonism; lower-directness and dual-role-agent studies are sensitivity evidence and repeated Primula work is clustered as one programme.",
    }
    OUTPUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
