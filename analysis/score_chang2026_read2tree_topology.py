#!/usr/bin/env python3
"""Score a Read2Tree six-sample tree against the pre-registered Chang 2026
var. takaoense topology hypotheses.

The Read2Tree fast screen contains six focal morph-labelled samples plus OMA
reference taxa.  This scorer is deliberately conservative:

1. parse the IQ-TREE Newick and verify all six focal samples exactly once;
2. root the tree on a source-declared OMA outgroup (default DAUCS);
3. require the six focal samples to be monophyletic relative to all OMA
   references before any within-takaoense hypothesis is scored;
4. collapse internal branches below each requested support threshold and require
   focal monophyly again; and
5. compare the supported six-tip rooted clusters against the one published
   candidate-regain topology and all seven nearest loss-only alternatives using
   the same conflict -> rooted-RF -> recovered-cluster ranking used by the
   per-gene scorer.

Reference taxa are never silently pruned before the focal-monophyly gate.  A
failure of that gate is reported as unresolved/incompatible, not forced into one
of the eight hypotheses.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import build_chang2026_gene_tree_panel as panel_builder
import score_chang2026_gene_tree_hypotheses as scorer

DEFAULT_NEAREST = Path("analysis/chang2026_takaoense_nearest_no_regain_topologies.csv")
DEFAULT_ROBUSTNESS = Path("analysis/chang2026_takaoense_topology_robustness_summary.json")
DEFAULT_THRESHOLDS = (0.0, 50.0, 70.0, 90.0)

DETAIL_FIELDS = (
    "support_threshold",
    "analysis_status",
    "raw_focal_monophyletic",
    "threshold_focal_monophyletic",
    "focal_cluster_count",
    "best_hypothesis_ids",
    "best_history_classes",
    "classification",
    "published_conflict_count",
    "published_rooted_rf_distance",
    "published_recovered_cluster_count",
    "best_loss_only_conflict_count",
    "best_loss_only_rooted_rf_distance",
    "best_loss_only_recovered_cluster_count",
    "published_minus_loss_conflict",
    "published_minus_loss_rf",
    "exact_hypothesis_match",
    "interpretation",
)

HYPOTHESIS_FIELDS = (
    "support_threshold",
    "hypothesis_id",
    "history_class",
    "conflicting_focal_clusters",
    "rooted_rf_distance",
    "hypothesis_clusters_recovered",
    "hypothesis_cluster_count",
    "focal_cluster_count",
    "rank_key",
    "is_best",
)


def clean(value: object) -> str:
    return str(value or "").strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [{k: clean(v) for k, v in row.items()} for row in csv.DictReader(handle)]


def read_panel(path: Path) -> tuple[list[dict[str, str]], dict[str, str]]:
    rows = read_csv(path)
    if len(rows) != 6:
        raise ValueError(f"Expected six focal panel rows, observed {len(rows)}")
    sample_ids = [clean(row.get("sample_id")) for row in rows]
    if any(not sample_id for sample_id in sample_ids):
        raise ValueError("Focal panel contains a missing sample_id")
    if len(sample_ids) != len(set(sample_ids)):
        raise ValueError("Focal sample_id values are not unique")
    morphs = Counter(clean(row.get("morph")).upper() for row in rows)
    if dict(morphs) != {"BP": 3, "W": 3}:
        raise ValueError(f"Expected three BP and three W focal rows: {dict(morphs)}")
    labels: dict[str, str] = {}
    for row in rows:
        if clean(row.get("panel_role")) != "focal_colour_morph":
            raise ValueError("Read2Tree panel may contain only focal_colour_morph rows")
        labels[row["sample_id"]] = scorer.focal_hypothesis_label(row)
    return rows, labels


def read_reference_manifest(path: Path) -> tuple[list[dict[str, str]], set[str]]:
    rows = read_csv(path)
    if not rows:
        raise ValueError("OMA reference manifest is empty")
    codes = [clean(row.get("oma_code")) for row in rows]
    if any(not code for code in codes):
        raise ValueError("OMA reference manifest has a missing oma_code")
    if len(codes) != len(set(codes)):
        raise ValueError("OMA reference codes are not unique")
    if any(clean(row.get("verified_in_oma")).lower() != "true" for row in rows):
        raise ValueError("Every OMA reference must be independently verified")
    return rows, set(codes)


def build_hypotheses(nearest_path: Path, robustness_path: Path) -> list[dict[str, object]]:
    rows = panel_builder.build_hypotheses(
        read_csv(nearest_path),
        json.loads(robustness_path.read_text(encoding="utf-8")),
    )
    output: list[dict[str, object]] = []
    seen: set[str] = set()
    for row in rows:
        hid = clean(row.get("hypothesis_id"))
        if not hid or hid in seen:
            raise ValueError(f"Missing or duplicate hypothesis_id: {hid!r}")
        seen.add(hid)
        tree = scorer.parse_newick(clean(row.get("topology_newick")))
        clusters = scorer.rooted_clusters(tree)
        labels = scorer.descendant_names(tree)
        if len(labels) != 6:
            raise ValueError(f"Hypothesis {hid} does not contain six unique tips")
        output.append({**row, "tree": tree, "clusters": clusters, "labels": labels})
    if len(output) != 8 or scorer.PUBLISHED_HYPOTHESIS not in seen:
        raise ValueError("Expected one published and seven loss-only hypotheses")
    return output


@dataclass(frozen=True)
class Edge:
    target: int
    support: float | None
    length: float | None


def _graph_from_tree(root: scorer.Node) -> tuple[dict[int, scorer.Node], dict[int, list[Edge]]]:
    nodes: dict[int, scorer.Node] = {}
    adjacency: dict[int, list[Edge]] = defaultdict(list)
    counter = 0

    def walk(node: scorer.Node) -> int:
        nonlocal counter
        idx = counter
        counter += 1
        nodes[idx] = node
        for child in node.children:
            child_idx = walk(child)
            # IQ-TREE support labels belong to internal edges. Preserve the
            # child-side support as an undirected edge annotation before rerooting.
            support = child.support if not child.is_leaf else None
            adjacency[idx].append(Edge(child_idx, support, child.length))
            adjacency[child_idx].append(Edge(idx, support, child.length))
        return idx

    walk(root)
    return nodes, adjacency


def _orient_from_graph(
    current: int,
    parent: int | None,
    nodes: Mapping[int, scorer.Node],
    adjacency: Mapping[int, Sequence[Edge]],
    incoming_support: float | None = None,
    incoming_length: float | None = None,
) -> scorer.Node:
    source = nodes[current]
    children: list[scorer.Node] = []
    for edge in adjacency.get(current, ()):
        if edge.target == parent:
            continue
        children.append(
            _orient_from_graph(
                edge.target,
                current,
                nodes,
                adjacency,
                incoming_support=edge.support,
                incoming_length=edge.length,
            )
        )
    return scorer.Node(
        name=source.name if source.is_leaf else "",
        support=incoming_support if children else None,
        length=incoming_length,
        children=children,
    )


def reroot_on_leaf(tree: scorer.Node, outgroup: str) -> scorer.Node:
    nodes, adjacency = _graph_from_tree(tree)
    matches = [idx for idx, node in nodes.items() if node.is_leaf and node.name == outgroup]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one outgroup leaf {outgroup!r}, observed {len(matches)}")
    out_idx = matches[0]
    edges = adjacency.get(out_idx, [])
    if len(edges) != 1:
        raise ValueError(f"Outgroup {outgroup!r} is not a terminal leaf")
    edge = edges[0]
    out_leaf = scorer.Node(name=outgroup, length=edge.length)
    ingroup = _orient_from_graph(
        edge.target,
        out_idx,
        nodes,
        adjacency,
        incoming_support=edge.support,
        incoming_length=edge.length,
    )
    return scorer.Node(children=[out_leaf, ingroup])


def leaf_counts(tree: scorer.Node) -> Counter[str]:
    return Counter(leaf.name for leaf in scorer.iter_leaves(tree))


def exact_clade(tree: scorer.Node, target: set[str]) -> scorer.Node | None:
    matches: list[scorer.Node] = []

    def walk(node: scorer.Node) -> frozenset[str]:
        names = scorer.descendant_names(node)
        if set(names) == target:
            matches.append(node)
        return names

    def visit(node: scorer.Node) -> None:
        walk(node)
        for child in node.children:
            visit(child)

    visit(tree)
    if len(matches) > 1:
        raise ValueError("Multiple nodes encode the same exact focal clade")
    return matches[0] if matches else None


def relabel_focal(tree: scorer.Node, mapping: Mapping[str, str]) -> scorer.Node:
    if tree.is_leaf:
        if tree.name not in mapping:
            raise ValueError(f"Unexpected non-focal leaf in focal clade: {tree.name}")
        return scorer.Node(name=mapping[tree.name], length=tree.length)
    return scorer.Node(
        name=tree.name,
        support=tree.support,
        length=tree.length,
        children=[relabel_focal(child, mapping) for child in tree.children],
    )


def score_clusters(
    focal_clusters: frozenset[frozenset[str]],
    hypotheses: Sequence[Mapping[str, object]],
) -> tuple[dict[str, object], list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    for hypothesis in hypotheses:
        hclusters = hypothesis["clusters"]
        conflict = scorer.conflicting_gene_clusters(focal_clusters, hclusters)
        rf = scorer.rooted_rf_distance(focal_clusters, hclusters)
        recovered = len(set(focal_clusters) & set(hclusters))
        rank = (conflict, rf, -recovered)
        rows.append(
            {
                "hypothesis_id": hypothesis["hypothesis_id"],
                "history_class": hypothesis["history_class"],
                "conflicting_focal_clusters": conflict,
                "rooted_rf_distance": rf,
                "hypothesis_clusters_recovered": recovered,
                "hypothesis_cluster_count": len(hclusters),
                "focal_cluster_count": len(focal_clusters),
                "rank_key": f"{conflict}|{rf}|{-recovered}",
                "is_best": "false",
                "_rank": rank,
            }
        )
    best_rank = min(row["_rank"] for row in rows)
    best = [row for row in rows if row["_rank"] == best_rank]
    for row in best:
        row["is_best"] = "true"
    published = next(row for row in rows if row["hypothesis_id"] == scorer.PUBLISHED_HYPOTHESIS)
    loss_rows = [row for row in rows if row["history_class"] == scorer.LOSS_ONLY_CLASS]
    best_loss_rank = min(row["_rank"] for row in loss_rows)
    best_loss = next(row for row in loss_rows if row["_rank"] == best_loss_rank)
    best_ids = sorted(str(row["hypothesis_id"]) for row in best)
    best_classes = sorted({str(row["history_class"]) for row in best})
    published_best = scorer.PUBLISHED_HYPOTHESIS in best_ids
    loss_best = any(row["history_class"] == scorer.LOSS_ONLY_CLASS for row in best)
    if not focal_clusters:
        classification = "unresolved_all_hypotheses_tie"
    elif published_best and loss_best:
        classification = "tie_published_loss_only"
    elif published_best:
        classification = "published_best"
    else:
        classification = "loss_only_best"
    exact = sorted(str(row["hypothesis_id"]) for row in rows if int(row["rooted_rf_distance"]) == 0)
    detail = {
        "best_hypothesis_ids": "|".join(best_ids),
        "best_history_classes": "|".join(best_classes),
        "classification": classification,
        "published_conflict_count": published["conflicting_focal_clusters"],
        "published_rooted_rf_distance": published["rooted_rf_distance"],
        "published_recovered_cluster_count": published["hypothesis_clusters_recovered"],
        "best_loss_only_conflict_count": best_loss["conflicting_focal_clusters"],
        "best_loss_only_rooted_rf_distance": best_loss["rooted_rf_distance"],
        "best_loss_only_recovered_cluster_count": best_loss["hypothesis_clusters_recovered"],
        "published_minus_loss_conflict": int(published["conflicting_focal_clusters"]) - int(best_loss["conflicting_focal_clusters"]),
        "published_minus_loss_rf": int(published["rooted_rf_distance"]) - int(best_loss["rooted_rf_distance"]),
        "exact_hypothesis_match": "|".join(exact),
    }
    for row in rows:
        row.pop("_rank", None)
    return detail, rows


def thresholds_from_text(text: str) -> tuple[float, ...]:
    values = scorer.thresholds_from_text(text)
    return values


def analyse(
    *,
    tree: scorer.Node,
    focal_mapping: Mapping[str, str],
    reference_codes: set[str],
    outgroup: str,
    hypotheses: Sequence[Mapping[str, object]],
    thresholds: Sequence[float],
) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    counts = leaf_counts(tree)
    focal_samples = set(focal_mapping)
    missing = sorted(focal_samples - set(counts))
    duplicates = sorted(sample for sample in focal_samples if counts[sample] != 1 and sample in counts)
    unexpected = sorted(set(counts) - focal_samples - reference_codes)
    if missing or duplicates or unexpected:
        raise ValueError(
            "Read2Tree tree leaf contract failed: "
            f"missing={missing}, duplicate_or_nonunique={duplicates}, unexpected={unexpected}"
        )
    if outgroup not in reference_codes:
        raise ValueError(f"Outgroup {outgroup!r} is not in the frozen reference manifest")
    rooted = reroot_on_leaf(tree, outgroup)
    raw_clade = exact_clade(rooted, focal_samples)
    raw_monophyletic = raw_clade is not None
    details: list[dict[str, object]] = []
    hypothesis_details: list[dict[str, object]] = []

    for threshold in thresholds:
        base = {
            "support_threshold": f"{threshold:g}",
            "raw_focal_monophyletic": str(raw_monophyletic).lower(),
            "threshold_focal_monophyletic": "false",
            "focal_cluster_count": "",
            "best_hypothesis_ids": "",
            "best_history_classes": "",
            "classification": "not_scored",
            "published_conflict_count": "",
            "published_rooted_rf_distance": "",
            "published_recovered_cluster_count": "",
            "best_loss_only_conflict_count": "",
            "best_loss_only_rooted_rf_distance": "",
            "best_loss_only_recovered_cluster_count": "",
            "published_minus_loss_conflict": "",
            "published_minus_loss_rf": "",
            "exact_hypothesis_match": "",
        }
        if not raw_monophyletic:
            details.append(
                {
                    **base,
                    "analysis_status": "focal_not_monophyletic_raw_tree",
                    "interpretation": "Six focal samples are not monophyletic relative to the frozen OMA references; within-takaoense histories are not scored.",
                }
            )
            continue

        collapsed = scorer.collapse_low_support(rooted, threshold, missing_support_policy="collapse")
        focal_clade = exact_clade(collapsed, focal_samples)
        if focal_clade is None:
            details.append(
                {
                    **base,
                    "analysis_status": "focal_monophyly_unresolved_at_threshold",
                    "interpretation": "The raw tree is focal-monophyletic, but the branch defining that clade is not retained at this support threshold; no eight-hypothesis score is reported.",
                }
            )
            continue

        relabelled = relabel_focal(focal_clade, focal_mapping)
        clusters = scorer.rooted_clusters(relabelled)
        scored, per_hypothesis = score_clusters(clusters, hypotheses)
        details.append(
            {
                **base,
                **scored,
                "analysis_status": "scored_focal_monophyletic",
                "threshold_focal_monophyletic": "true",
                "focal_cluster_count": len(clusters),
                "interpretation": "Six focal samples remain monophyletic relative to OMA references; the supported focal rooted clusters are ranked against the eight pre-registered histories.",
            }
        )
        for row in per_hypothesis:
            hypothesis_details.append({"support_threshold": f"{threshold:g}", **row})

    payload = {
        "analysis": "Read2Tree six-sample topology versus pre-registered Chang 2026 histories",
        "outgroup": outgroup,
        "focal_sample_ids": sorted(focal_samples),
        "focal_hypothesis_labels": dict(sorted(focal_mapping.items())),
        "reference_codes_present": sorted(code for code in reference_codes if code in counts),
        "raw_focal_monophyletic": raw_monophyletic,
        "support_thresholds": list(thresholds),
        "classification_by_threshold": {
            row["support_threshold"]: row["classification"] for row in details
        },
        "claim_limit": "A Read2Tree concatenated topology is a reference-guided raw-read sensitivity screen. Even exact agreement with H_REG_PUBLISHED does not distinguish introgression from incomplete lineage sorting or demonstrate molecular anthocyanin reactivation.",
    }
    return details, hypothesis_details, payload


def write_csv(path: Path, rows: Iterable[Mapping[str, object]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), extrasaction="ignore")
        writer.writeheader(); writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--tree", type=Path, required=True)
    p.add_argument("--panel", type=Path, required=True)
    p.add_argument("--reference-manifest", type=Path, required=True)
    p.add_argument("--outgroup", default="DAUCS")
    p.add_argument("--nearest", type=Path, default=DEFAULT_NEAREST)
    p.add_argument("--robustness-summary", type=Path, default=DEFAULT_ROBUSTNESS)
    p.add_argument("--thresholds", default=",".join(str(int(v)) for v in DEFAULT_THRESHOLDS))
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--hypothesis-output", type=Path, required=True)
    p.add_argument("--summary-json", type=Path, required=True)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    _, focal_mapping = read_panel(args.panel)
    _, refs = read_reference_manifest(args.reference_manifest)
    hypotheses = build_hypotheses(args.nearest, args.robustness_summary)
    tree = scorer.parse_newick(args.tree.read_text(encoding="utf-8"))
    details, hypothesis_details, payload = analyse(
        tree=tree,
        focal_mapping=focal_mapping,
        reference_codes=refs,
        outgroup=args.outgroup,
        hypotheses=hypotheses,
        thresholds=thresholds_from_text(args.thresholds),
    )
    write_csv(args.output, details, DETAIL_FIELDS)
    write_csv(args.hypothesis_output, hypothesis_details, HYPOTHESIS_FIELDS)
    args.summary_json.parent.mkdir(parents=True, exist_ok=True)
    args.summary_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"raw_focal_monophyletic={str(payload['raw_focal_monophyletic']).lower()}")
    for threshold, classification in payload["classification_by_threshold"].items():
        print(f"threshold={threshold} classification={classification}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
