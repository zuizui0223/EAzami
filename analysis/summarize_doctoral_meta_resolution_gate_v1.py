import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/evidence/doctoral_meta_resolution_gate_v1.csv"
OUTPUT = ROOT / "data/evidence/doctoral_meta_resolution_gate_v1.json"


def main():
    with INPUT.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    ids = [r["hypothesis_id"] for r in rows]
    if ids != [f"HGA{i}" for i in range(6)]:
        raise RuntimeError(f"Expected HGA0-HGA5 in order, got {ids}")
    if len(ids) != len(set(ids)):
        raise RuntimeError("Duplicate hypothesis IDs")

    for r in rows:
        r["meta_ceiling_reached"] = int(r["meta_ceiling_reached"])
        for required in [
            "meta_general_status",
            "focal_cirsium_status",
            "current_evidence_basis",
            "why_more_generic_meta_will_not_resolve_it",
            "decisive_next_data",
            "new_literature_reopens_gate_if",
        ]:
            if not r[required].strip():
                raise RuntimeError(f"{r['hypothesis_id']} missing {required}")

    summary = {
        "version": "v1",
        "hypothesis_count": len(rows),
        "meta_ceiling_reached_count": sum(r["meta_ceiling_reached"] for r in rows),
        "meta_general_status_counts": dict(sorted(Counter(r["meta_general_status"] for r in rows).items())),
        "focal_cirsium_status_counts": dict(sorted(Counter(r["focal_cirsium_status"] for r in rows).items())),
        "hypotheses": rows,
        "mainline_decision": (
            "Generic interaction meta-analysis has reached its current decision ceiling for all six HGA hypotheses. "
            "HGA0 is weakened; HGA1-HGA2 have working cross-study support; HGA3 now has working general meta-support for a selection mosaic; "
            "HGA4 remains a mechanistic candidate and HGA5 remains unresolved. Further generic literature accumulation is stopped unless a prespecified reopening trigger appears."
        ),
        "next_empirical_priority": (
            "Move Aim 2 to focal same-population discrimination: orientation first, then W/coloured where flowering overlaps; "
            "nest pollination supplementation x post-anthesis antagonist protection in a feasible subset; estimate local trait-to-effective-contact and trait-to-damage leverage; "
            "run seed-to-recruitment microsite work only after a seed-output contrast is demonstrated."
        ),
        "claim_boundary": (
            "Meta-ceiling means additional heterogeneous generic studies are not expected to change the current doctoral sampling or discriminating design. "
            "It does not mean the focal Cirsium hypotheses are biologically resolved."
        ),
    }
    OUTPUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
