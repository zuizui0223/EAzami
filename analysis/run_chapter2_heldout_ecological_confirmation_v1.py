#!/usr/bin/env python3
"""Run the frozen held-out ecological confirmation on a precomputed taxon environment table.

Expected environment CSV columns:
analysis_taxon,BIO1,BIO12,BIO15,GSP

This script does not fetch or choose taxa. Eligibility is determined only by the
frozen trait-state audit plus the frozen occurrence-support audit.
"""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
from pathlib import Path


def mean(xs):
    return sum(xs) / len(xs)


def sample_sd(xs):
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def zscores(xs):
    m = mean(xs)
    s = sample_sd(xs)
    if s == 0:
        return [0.0 for _ in xs]
    return [(x - m) / s for x in xs]


def exact_one_sided(values, labels, positive_label):
    labels = list(labels)
    n = len(labels)
    n_pos = sum(x == positive_label for x in labels)
    obs = mean([v for v, l in zip(values, labels) if l == positive_label]) - mean(
        [v for v, l in zip(values, labels) if l != positive_label]
    )
    exceed = 0
    total = 0
    for combo in itertools.combinations(range(n), n_pos):
        pos = set(combo)
        stat = mean([values[i] for i in range(n) if i in pos]) - mean(
            [values[i] for i in range(n) if i not in pos]
        )
        total += 1
        if stat >= obs - 1e-12:
            exceed += 1
    return {"observed": obs, "rank_count": exceed, "n_maps": total, "p_one_sided": exceed / total}


def read_csv(path):
    with Path(path).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def fnum(x):
    try:
        v = float(x)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--traits", type=Path, required=True)
    p.add_argument("--occurrence-support", type=Path, required=True)
    p.add_argument("--environment", type=Path, required=True)
    p.add_argument("--contract", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()

    contract = json.loads(a.contract.read_text(encoding="utf-8"))
    alpha = float(contract["hypotheses"]["orientation"]["alpha"])
    min_state = int(contract["heldout_scope"]["minimum_taxa_per_compared_state_after_occurrence_gate"])

    traits = {r["analysis_taxon"]: r for r in read_csv(a.traits)}
    occ = {
        r["analysis_taxon"]: r
        for r in read_csv(a.occurrence_support)
        if str(r.get("passes_primary_occurrence_gate", "")).casefold() == "true"
    }
    env = {r["analysis_taxon"]: r for r in read_csv(a.environment)}

    result = {
        "version": "chapter2_heldout_ecological_confirmation_result_v1",
        "prospective_contract": contract["version"],
        "orientation": {"status": "not_evaluable"},
        "stickiness": {"status": "not_evaluable"},
        "claim_boundary": contract["claim_boundary"],
    }

    # Orientation
    o = []
    for name, tr in traits.items():
        if tr.get("orientation_pool_status") != "candidate_primary" or name not in occ or name not in env:
            continue
        state = tr.get("orientation_state")
        if state not in {"downward_or_nodding", "upward_or_erect"}:
            continue
        b1, b15 = fnum(env[name].get("BIO1")), fnum(env[name].get("BIO15"))
        if b1 is not None and b15 is not None:
            o.append((name, state, b1, b15))

    if o:
        counts = {s: sum(x[1] == s for x in o) for s in {"downward_or_nodding", "upward_or_erect"}}
        if min(counts.values()) >= min_state:
            z1 = zscores([x[2] for x in o])
            z15 = zscores([x[3] for x in o])
            composite = [(b15 - b1) / math.sqrt(2) for b15, b1 in zip(z15, z1)]
            labels = [x[1] for x in o]
            primary = exact_one_sided(composite, labels, "downward_or_nodding")
            bio15 = exact_one_sided(z15, labels, "downward_or_nodding")
            # For BIO1, lower in D means test -BIO1 for a positive D-U effect.
            bio1_direction = exact_one_sided([-x for x in z1], labels, "downward_or_nodding")
            passed = (
                primary["observed"] > 0
                and bio15["observed"] > 0
                and bio1_direction["observed"] > 0
                and primary["p_one_sided"] < alpha
            )
            result["orientation"] = {
                "status": "evaluated",
                "n_taxa": len(o),
                "state_counts": counts,
                "taxa": [x[0] for x in o],
                "primary_composite": primary,
                "BIO15_D_minus_U": bio15,
                "negative_BIO1_D_minus_U": bio1_direction,
                "confirmation_pass": passed,
            }
        else:
            result["orientation"] = {
                "status": "not_evaluable_state_replication",
                "state_counts": counts,
                "minimum_taxa_per_state": min_state,
            }

    # Stickiness
    k = []
    for name, tr in traits.items():
        if tr.get("stickiness_pool_status") != "candidate_primary" or name not in occ or name not in env:
            continue
        state = tr.get("stickiness_state")
        if state not in {"sticky", "nonsticky"}:
            continue
        b12, gsp = fnum(env[name].get("BIO12")), fnum(env[name].get("GSP"))
        if b12 is not None:
            k.append((name, state, b12, gsp))

    if k:
        counts = {s: sum(x[1] == s for x in k) for s in {"sticky", "nonsticky"}}
        if min(counts.values()) >= min_state:
            z12 = zscores([x[2] for x in k])
            labels = [x[1] for x in k]
            primary = exact_one_sided(z12, labels, "sticky")
            passed = primary["observed"] > 0 and primary["p_one_sided"] < alpha
            sec = None
            if all(x[3] is not None for x in k):
                zgsp = zscores([x[3] for x in k])
                sec = exact_one_sided(zgsp, labels, "sticky")
            result["stickiness"] = {
                "status": "evaluated",
                "n_taxa": len(k),
                "state_counts": counts,
                "taxa": [x[0] for x in k],
                "BIO12_primary": primary,
                "GSP_secondary": sec,
                "confirmation_pass": passed,
            }
        else:
            result["stickiness"] = {
                "status": "not_evaluable_state_replication",
                "state_counts": counts,
                "minimum_taxa_per_state": min_state,
            }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
