#!/usr/bin/env python3
"""Build a conservative public dated event registry on the six-taxon East-Asian scaffold.

The goal is not to create a complete chronogram. It enumerates every minimum-cost
binary-state history on three frozen topology variants and reports only changes
that are forced across all minimum histories. Calendar windows are parent-child
branch bounds from published node-age scaffolds; no midpoint event dates are used.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

AGES = {
    "ROOT": 1.02,
    "ARENI": 0.93,
    "NIPPO": 0.79,
    "TRIO": 0.47,
    "PAIR": 0.35,
    "Cirsium brevicaule": 0.0,
    "Cirsium irumtiense": 0.0,
    "Cirsium morii": 0.0,
    "Cirsium pengii": 0.0,
    "Cirsium kawakamii": 0.0,
    "Cirsium tatakaense": 0.0,
}

TOPOLOGIES = {
    "published_pengii_basal": {
        "ROOT": ["ARENI", "NIPPO"],
        "ARENI": ["Cirsium brevicaule", "Cirsium irumtiense"],
        "NIPPO": ["Cirsium morii", "TRIO"],
        "TRIO": ["Cirsium pengii", "PAIR"],
        "PAIR": ["Cirsium kawakamii", "Cirsium tatakaense"],
    },
    "alternative_kawakamii_basal": {
        "ROOT": ["ARENI", "NIPPO"],
        "ARENI": ["Cirsium brevicaule", "Cirsium irumtiense"],
        "NIPPO": ["Cirsium morii", "TRIO"],
        "TRIO": ["Cirsium kawakamii", "PAIR"],
        "PAIR": ["Cirsium pengii", "Cirsium tatakaense"],
    },
    "alternative_tatakaense_basal": {
        "ROOT": ["ARENI", "NIPPO"],
        "ARENI": ["Cirsium brevicaule", "Cirsium irumtiense"],
        "NIPPO": ["Cirsium morii", "TRIO"],
        "TRIO": ["Cirsium tatakaense", "PAIR"],
        "PAIR": ["Cirsium pengii", "Cirsium kawakamii"],
    },
}

TRAITS = {
    "orientation": {
        "states": ["U", "D"],
        "tips": {
            "Cirsium brevicaule": "U",
            "Cirsium irumtiense": "U",
            "Cirsium morii": "U",
            "Cirsium pengii": "D",
            "Cirsium kawakamii": "D",
            "Cirsium tatakaense": "D",
        },
    },
    "flower_colour": {
        "states": ["C", "W"],
        "tips": {
            "Cirsium brevicaule": "W",
            "Cirsium irumtiense": "C",
            "Cirsium morii": "C",
            "Cirsium pengii": "C",
            "Cirsium kawakamii": "W",
            "Cirsium tatakaense": "C",
        },
    },
}

PROCESS_CONTEXT = {
    ("orientation", "TRIO"): {
        "event_id": "ORI_TAIWAN_TRIO_STEM",
        "biogeographic_context": "within-Taiwan Nipponocirsium diversification",
        "context_status": "source-supported regional lineage context; not evidence that dispersal or fragmentation caused the trait transition",
    },
    ("flower_colour", "Cirsium brevicaule"): {
        "event_id": "COL_BREVICAULE_TERMINAL",
        "biogeographic_context": "post-split Arenicola lineage in the central Ryukyus; C. brevicaule and C. irumtiense are separated across the Miyako Strait",
        "context_status": "source-supported lineage/range context; exact colour-transition timing and causal role of the strait remain unresolved",
    },
    ("flower_colour", "Cirsium kawakamii"): {
        "event_id": "COL_KAWAKAMII_TERMINAL",
        "biogeographic_context": "within-Taiwan Nipponocirsium terminal diversification",
        "context_status": "source-supported regional lineage context; not evidence that glaciation, refuge isolation or elevation caused the colour transition",
    },
}


def edges(tree):
    return [(p, c) for p, children in tree.items() for c in children]


def minimum_histories(tree, trait):
    internal = list(tree.keys())
    tips = TRAITS[trait]["tips"]
    states = TRAITS[trait]["states"]
    best_cost = None
    best = []
    for vals in itertools.product(states, repeat=len(internal)):
        assign = dict(zip(internal, vals))
        assign.update(tips)
        changed = []
        cost = 0
        for p, c in edges(tree):
            if assign[p] != assign[c]:
                cost += 1
                changed.append((p, c, assign[p], assign[c]))
        if best_cost is None or cost < best_cost:
            best_cost = cost
            best = [(assign, changed)]
        elif cost == best_cost:
            best.append((assign, changed))
    return best_cost, best


def per_topology_summary(name, tree, trait):
    min_cost, histories = minimum_histories(tree, trait)
    out_edges = []
    for p, c in edges(tree):
        changes = []
        for assign, changed in histories:
            hit = [x for x in changed if x[0] == p and x[1] == c]
            changes.append(hit[0][2:] if hit else None)
        n_change = sum(x is not None for x in changes)
        dirs = sorted({f"{x[0]}->{x[1]}" for x in changes if x is not None})
        out_edges.append({
            "parent": p,
            "child": c,
            "parent_age_ma": AGES[p],
            "child_age_ma": AGES[c],
            "window_ma": [AGES[c], AGES[p]],
            "change_fraction_among_min_histories": n_change / len(histories),
            "forced_in_all_min_histories": n_change == len(histories),
            "possible_directions": dirs,
        })
    return {
        "topology": name,
        "minimum_steps": min_cost,
        "n_minimum_histories": len(histories),
        "edges": out_edges,
    }


def aggregate_events(trait, summaries):
    events = []
    # biological event units are identified by the descendant lineage/clade,
    # allowing the parent edge to vary across topology variants.
    candidates = []
    if trait == "orientation":
        candidates = ["TRIO"]
    elif trait == "flower_colour":
        candidates = ["Cirsium brevicaule", "Cirsium kawakamii"]

    for child in candidates:
        per_top = []
        for s in summaries:
            matches = [e for e in s["edges"] if e["child"] == child]
            if len(matches) != 1:
                raise AssertionError((trait, child, s["topology"], matches))
            per_top.append({"topology": s["topology"], **matches[0]})
        forced = all(e["forced_in_all_min_histories"] for e in per_top)
        directions = sorted({d for e in per_top for d in e["possible_directions"]})
        young = min(e["child_age_ma"] for e in per_top)
        old = max(e["parent_age_ma"] for e in per_top)
        ctx = PROCESS_CONTEXT[(trait, child)]
        events.append({
            **ctx,
            "trait": trait,
            "descendant_lineage": child,
            "forced_across_all_topologies_and_min_histories": forced,
            "transition_directions": directions,
            "combined_admissible_window_ma": [young, old],
            "per_topology_edges": per_top,
            "calendar_semantics": "transition may occur anywhere on the parent-child branch; no midpoint date is assigned",
        })
    return events


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    trait_results = {}
    all_events = []
    for trait in TRAITS:
        summaries = [per_topology_summary(name, tree, trait) for name, tree in TOPOLOGIES.items()]
        trait_results[trait] = summaries
        all_events.extend(aggregate_events(trait, summaries))

    # Scientific invariants expected from the frozen public six-taxon scaffold.
    assert {x["minimum_steps"] for x in trait_results["orientation"]} == {1}
    assert {x["minimum_steps"] for x in trait_results["flower_colour"]} == {2}
    by_id = {x["event_id"]: x for x in all_events}
    assert by_id["ORI_TAIWAN_TRIO_STEM"]["forced_across_all_topologies_and_min_histories"]
    assert by_id["ORI_TAIWAN_TRIO_STEM"]["combined_admissible_window_ma"] == [0.47, 0.79]
    assert by_id["COL_BREVICAULE_TERMINAL"]["forced_across_all_topologies_and_min_histories"]
    assert by_id["COL_BREVICAULE_TERMINAL"]["combined_admissible_window_ma"] == [0.0, 0.93]
    assert by_id["COL_KAWAKAMII_TERMINAL"]["forced_across_all_topologies_and_min_histories"]
    assert by_id["COL_KAWAKAMII_TERMINAL"]["combined_admissible_window_ma"] == [0.0, 0.47]

    result = {
        "contract_version": "chapter2_public_dated_event_registry_v1",
        "scope": "public six-taxon East-Asian dated sensitivity only; not a complete Japan38 chronogram",
        "sources": [
            "Chang et al. 2026, BMC Plant Biology, DOI 10.1186/s12870-026-08097-6",
            "Chang et al. 2025, Botanical Studies, DOI 10.1186/s40529-025-00454-2",
            "data/evidence/arenicola_dated_asr_scaffold_v1.json",
        ],
        "trait_results": trait_results,
        "event_registry": all_events,
        "claim_boundary": [
            "forced means forced conditional on this six-taxon state coding, topology set and unordered minimum-change criterion",
            "calendar windows are branch bounds, not exact transition dates or posterior event times",
            "flower-colour events here are a local published-state sensitivity and do not replace the unresolved Japan38 colour history",
            "biogeographic context is an exposure/process context, not evidence that range change caused the trait transition",
            "no event is called adaptation or convergence",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "minimum_steps": {k: [x["minimum_steps"] for x in v] for k, v in trait_results.items()},
        "events": all_events,
    }, indent=2))


if __name__ == "__main__":
    main()
