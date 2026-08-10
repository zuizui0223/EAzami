#!/usr/bin/env python3
"""Score Chang 2026 gene trees against one regain and seven loss-only hypotheses.

The primary topology hypothesis is the published six-tip var. takaoense ordering.
The null set contains every nearest rooted loss-only topology identified by the
exhaustive 945-topology sensitivity analysis.  This script compares each rooted
single-copy gene tree with all eight hypotheses at one or more support thresholds.

The comparison is deliberately topology-only:

* low-support internal nodes are collapsed before scoring;
* rooted cluster conflict count is the primary distance;
* rooted Robinson-Foulds distance is the secondary distance;
* unresolved stars therefore tie all hypotheses rather than creating evidence;
* missing or duplicated focal samples are reported and excluded;
* sister-affinity summaries are exploratory screens for discordance, not tests of
  introgression by themselves.

Input gene trees should already be rooted on the two Cirsium lineare outgroups.
For single-copy orthogroups, alignment headers should be the panel ``sample_id``
(or ``sample_id|sequence``).  No branch lengths are used.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator, Mapping, Sequence

DEFAULT_THRESHOLDS = (0.0, 50.0, 70.0, 90.0)
PUBLISHED_HYPOTHESIS = "H_REG_PUBLISHED"
LOSS_ONLY_CLASS = "nearest_loss_only_topology"

DETAIL_FIELDS = (
    "gene_id",
    "tree_file",
    "support_threshold",
    "analysis_status",
    "focal_leaf_count",
    "missing_focal_samples",
    "duplicate_focal_samples",
    "unmapped_leaf_count",
    "gene_cluster_count",
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
    "bp_external_sister_affinity",
    "white_external_sister_affinity",
    "interpretation",
)

HYPOTHESIS_DETAIL_FIELDS = (
    "gene_id",
    "support_threshold",
    "hypothesis_id",
    "history_class",
    "conflicting_gene_clusters",
    "rooted_rf_distance",
    "hypothesis_clusters_recovered",
    "hypothesis_cluster_count",
    "gene_cluster_count",
    "rank_key",
    "is_best",
)

SUMMARY_FIELDS = (
    "support_threshold",
    "tree_files",
    "complete_single_copy_gene_trees",
    "incomplete_focal_gene_trees",
    "multicopy_focal_gene_trees",
    "parse_or_root_error_gene_trees",
    "published_best",
    "loss_only_best",
    "tie_published_loss_only",
    "published_exact_match",
    "loss_only_exact_match",
    "unresolved_all_hypotheses_tie",
    "published_best_fraction_of_complete",
    "loss_only_best_fraction_of_complete",
    "tie_fraction_of_complete",
    "interpretation",
)


@dataclass
class Node:
    name: str = ""
    support: float | None = None
    length: float | None = None
    children: list["Node"] = field(default_factory=list)

    @property
    def is_leaf(self) -> bool:
        return not self.children

    def copy(self) -> "Node":
        return Node(
            name=self.name,
            support=self.support,
            length=self.length,
            children=[child.copy() for child in self.children],
        )


class NewickParser:
    def __init__(self, text: str):
        self.text = self._remove_comments(text.strip())
        self.index = 0

    @staticmethod
    def _remove_comments(text: str) -> str:
        output: list[str] = []
        depth = 0
        quoted = False
        index = 0
        while index < len(text):
            char = text[index]
            if char == "'":
                if quoted and index + 1 < len(text) and text[index + 1] == "'":
                    output.extend((char, text[index + 1]))
                    index += 2
                    continue
                quoted = not quoted
                if depth == 0:
                    output.append(char)
                index += 1
                continue
            if not quoted and char == "[":
                depth += 1
                index += 1
                continue
            if not quoted and char == "]" and depth:
                depth -= 1
                index += 1
                continue
            if depth == 0:
                output.append(char)
            index += 1
        return "".join(output)

    def parse(self) -> Node:
        node = self._subtree()
        self._skip_space()
        if self._peek() == ";":
            self.index += 1
        self._skip_space()
        if self.index != len(self.text):
            raise ValueError(
                f"Unexpected Newick content at position {self.index}: "
                f"{self.text[self.index:self.index + 30]!r}"
            )
        return node

    def _subtree(self) -> Node:
        self._skip_space()
        if self._peek() == "(":
            self.index += 1
            children = [self._subtree()]
            while True:
                self._skip_space()
                char = self._peek()
                if char == ",":
                    self.index += 1
                    children.append(self._subtree())
                elif char == ")":
                    self.index += 1
                    break
                else:
                    raise ValueError(
                        f"Expected ',' or ')' at {self.index}, observed {char!r}"
                    )
            label = self._label(optional=True)
            length = self._branch_length()
            return Node(
                name=label,
                support=parse_support(label),
                length=length,
                children=children,
            )
        label = self._label(optional=False)
        length = self._branch_length()
        return Node(name=label, length=length)

    def _label(self, *, optional: bool) -> str:
        self._skip_space()
        if self._peek() == "'":
            self.index += 1
            chars: list[str] = []
            while self.index < len(self.text):
                char = self.text[self.index]
                if char == "'":
                    if (
                        self.index + 1 < len(self.text)
                        and self.text[self.index + 1] == "'"
                    ):
                        chars.append("'")
                        self.index += 2
                        continue
                    self.index += 1
                    return "".join(chars)
                chars.append(char)
                self.index += 1
            raise ValueError("Unterminated quoted Newick label")

        start = self.index
        while self.index < len(self.text):
            char = self.text[self.index]
            if char in ",():;" or char.isspace():
                break
            self.index += 1
        label = self.text[start:self.index]
        if not label and not optional:
            raise ValueError(f"Missing Newick leaf label at position {start}")
        return label

    def _branch_length(self) -> float | None:
        self._skip_space()
        if self._peek() != ":":
            return None
        self.index += 1
        self._skip_space()
        start = self.index
        while self.index < len(self.text):
            char = self.text[self.index]
            if char in ",();" or char.isspace():
                break
            self.index += 1
        text = self.text[start:self.index]
        try:
            return float(text)
        except ValueError as exc:
            raise ValueError(f"Invalid Newick branch length: {text!r}") from exc

    def _skip_space(self) -> None:
        while self.index < len(self.text) and self.text[self.index].isspace():
            self.index += 1

    def _peek(self) -> str:
        return self.text[self.index] if self.index < len(self.text) else ""


def parse_support(label: str) -> float | None:
    """Return the last numeric support in an internal label.

    IQ-TREE commonly emits ``SH-aLRT/UFBoot`` labels such as ``95/100``; the
    second value is used.  Proportions in [0, 1] are converted to percentages.
    """
    numbers = re.findall(r"(?<![A-Za-z])[-+]?(?:\d+(?:\.\d*)?|\.\d+)", label)
    if not numbers:
        return None
    value = float(numbers[-1])
    if 0.0 <= value <= 1.0:
        value *= 100.0
    return value


def parse_newick(text: str) -> Node:
    return NewickParser(text).parse()


def iter_leaves(node: Node) -> Iterator[Node]:
    if node.is_leaf:
        yield node
        return
    for child in node.children:
        yield from iter_leaves(child)


def descendant_names(node: Node) -> frozenset[str]:
    if node.is_leaf:
        return frozenset((node.name,))
    output: set[str] = set()
    for child in node.children:
        output.update(descendant_names(child))
    return frozenset(output)


def collapse_low_support(
    node: Node,
    threshold: float,
    *,
    missing_support_policy: str = "collapse",
    is_root: bool = True,
) -> Node:
    """Collapse low-support internal branches into multifurcations."""
    if node.is_leaf:
        return node.copy()
    collapsed_children: list[Node] = []
    for child in node.children:
        processed = collapse_low_support(
            child,
            threshold,
            missing_support_policy=missing_support_policy,
            is_root=False,
        )
        if processed.is_leaf:
            collapsed_children.append(processed)
            continue
        supported = (
            processed.support is not None and processed.support >= threshold
        )
        if threshold <= 0:
            supported = True
        elif processed.support is None and missing_support_policy == "keep":
            supported = True
        if supported:
            collapsed_children.append(processed)
        else:
            collapsed_children.extend(processed.children)
    return Node(
        name=node.name,
        support=node.support,
        length=node.length,
        children=collapsed_children,
    )


def prune_tree(node: Node, keep: set[str]) -> Node | None:
    if node.is_leaf:
        return node.copy() if node.name in keep else None
    children = [
        pruned
        for child in node.children
        if (pruned := prune_tree(child, keep)) is not None
    ]
    if not children:
        return None
    if len(children) == 1:
        return children[0]
    return Node(
        name=node.name,
        support=node.support,
        length=node.length,
        children=children,
    )


def rooted_clusters(node: Node) -> frozenset[frozenset[str]]:
    full = descendant_names(node)
    clusters: set[frozenset[str]] = set()

    def walk(current: Node) -> frozenset[str]:
        if current.is_leaf:
            return frozenset((current.name,))
        descendants: set[str] = set()
        for child in current.children:
            descendants.update(walk(child))
        cluster = frozenset(descendants)
        if 1 < len(cluster) < len(full):
            clusters.add(cluster)
        return cluster

    walk(node)
    return frozenset(clusters)


def clusters_compatible(left: frozenset[str], right: frozenset[str]) -> bool:
    return left <= right or right <= left or left.isdisjoint(right)


def conflicting_gene_clusters(
    gene_clusters: Iterable[frozenset[str]],
    hypothesis_clusters: Iterable[frozenset[str]],
) -> int:
    hypothesis = tuple(hypothesis_clusters)
    return sum(
        not all(clusters_compatible(cluster, other) for other in hypothesis)
        for cluster in gene_clusters
    )


def rooted_rf_distance(
    left: Iterable[frozenset[str]],
    right: Iterable[frozenset[str]],
) -> int:
    return len(set(left) ^ set(right))


def canonical_taxon(value: str) -> str:
    text = str(value or "").strip().replace("_", " ")
    text = re.sub(r"^C\.\s+", "Cirsium ", text, flags=re.I)
    return re.sub(r"\s+", " ", text).strip().casefold()


def focal_hypothesis_label(row: Mapping[str, str]) -> str:
    code = str(row.get("code", "")).strip()
    voucher = str(row.get("voucher", "")).strip()
    morph = str(row.get("morph", "")).strip()
    digits = "".join(re.findall(r"\d+", voucher))
    if not code or not digits or morph not in {"W", "BP"}:
        raise ValueError(
            f"Cannot construct hypothesis label from code={code!r}, "
            f"voucher={voucher!r}, morph={morph!r}"
        )
    return f"{code}_{digits}_{morph}"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [
            {key: str(value or "").strip() for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def panel_metadata(
    path: Path,
) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    rows = read_csv(path)
    focal: dict[str, str] = {}
    role: dict[str, str] = {}
    morph: dict[str, str] = {}
    for row in rows:
        sample_id = row.get("sample_id", "")
        if not sample_id:
            raise ValueError("Panel row lacks sample_id")
        if sample_id in role:
            raise ValueError(f"Duplicate panel sample_id: {sample_id}")
        role[sample_id] = row.get("panel_role", "")
        morph[sample_id] = row.get("morph", "")
        if canonical_taxon(row.get("taxon", "")) == (
            "cirsium japonicum var. takaoense"
        ):
            focal[sample_id] = focal_hypothesis_label(row)
    if len(focal) != 6:
        raise ValueError(f"Expected six focal takaoense samples, observed {len(focal)}")
    if set(morph[sample_id] for sample_id in focal) != {"W", "BP"}:
        raise ValueError("Focal panel does not contain both W and BP morphs")
    return focal, role, morph


def hypothesis_metadata(path: Path) -> list[dict[str, object]]:
    rows = read_csv(path)
    output: list[dict[str, object]] = []
    ids: set[str] = set()
    for row in rows:
        hypothesis_id = row.get("hypothesis_id", "")
        if not hypothesis_id or hypothesis_id in ids:
            raise ValueError(f"Missing or duplicate hypothesis_id: {hypothesis_id!r}")
        ids.add(hypothesis_id)
        tree = parse_newick(row.get("topology_newick", ""))
        labels = descendant_names(tree)
        if len(labels) != 6:
            raise ValueError(
                f"Hypothesis {hypothesis_id} does not contain six unique tips"
            )
        output.append(
            {
                **row,
                "tree": tree,
                "clusters": rooted_clusters(tree),
                "labels": labels,
            }
        )
    if PUBLISHED_HYPOTHESIS not in ids:
        raise ValueError("Published hypothesis is absent")
    if len(rows) != 8:
        raise ValueError(f"Expected eight hypotheses, observed {len(rows)}")
    return output


def leaf_to_sample(
    leaf_name: str,
    sample_ids: Sequence[str],
) -> str | None:
    if leaf_name in sample_ids:
        return leaf_name
    candidates = [
        sample_id
        for sample_id in sample_ids
        if leaf_name.startswith(sample_id + "|")
        or leaf_name.startswith(sample_id + "__")
    ]
    if len(candidates) == 1:
        return candidates[0]
    return None


def relabel_tree(
    node: Node,
    sample_ids: Sequence[str],
    focal_labels: Mapping[str, str],
) -> tuple[Node, dict[str, list[str]], int]:
    assignments: dict[str, list[str]] = defaultdict(list)
    unmapped = 0

    def walk(current: Node) -> Node:
        nonlocal unmapped
        if current.is_leaf:
            sample = leaf_to_sample(current.name, sample_ids)
            if sample is None:
                unmapped += 1
                return Node(name=current.name)
            assignments[sample].append(current.name)
            return Node(name=focal_labels.get(sample, sample))
        return Node(
            name=current.name,
            support=current.support,
            length=current.length,
            children=[walk(child) for child in current.children],
        )

    return walk(node), assignments, unmapped


def external_sister_affinity(
    node: Node,
    focal_label_to_sample: Mapping[str, str],
    roles: Mapping[str, str],
    focal_morphs: Mapping[str, str],
) -> tuple[str, str]:
    """Summarize the first external sister context for each focal tip."""
    parent: dict[int, Node] = {}
    leaves: dict[str, Node] = {}

    def index(current: Node) -> None:
        if current.is_leaf:
            leaves[current.name] = current
            return
        for child in current.children:
            parent[id(child)] = current
            index(child)

    index(node)

    def sample_for_label(label: str) -> str:
        if label in focal_label_to_sample:
            return focal_label_to_sample[label]
        return label

    def role_for_label(label: str) -> str:
        return roles.get(sample_for_label(label), "unmapped")

    bp: list[str] = []
    white: list[str] = []
    for label, sample_id in sorted(focal_label_to_sample.items()):
        leaf = leaves.get(label)
        if leaf is None:
            continue
        current = leaf
        affinity = "none_or_unresolved"
        while id(current) in parent:
            ancestor = parent[id(current)]
            sister_labels: set[str] = set()
            for child in ancestor.children:
                if child is current:
                    continue
                sister_labels.update(descendant_names(child))
            external_roles = sorted(
                {
                    role_for_label(sister)
                    for sister in sister_labels
                    if role_for_label(sister) != "focal_colour_morph"
                }
            )
            if external_roles:
                affinity = "+".join(external_roles)
                break
            current = ancestor
        item = f"{label}={affinity}"
        if focal_morphs.get(sample_id) == "BP":
            bp.append(item)
        else:
            white.append(item)
    return ";".join(bp), ";".join(white)


def score_one_tree(
    *,
    gene_id: str,
    tree_file: str,
    tree: Node,
    threshold: float,
    focal_labels: Mapping[str, str],
    roles: Mapping[str, str],
    morphs: Mapping[str, str],
    hypotheses: Sequence[Mapping[str, object]],
) -> tuple[dict[str, object], list[dict[str, object]]]:
    sample_ids = tuple(roles)
    relabelled, assignments, unmapped = relabel_tree(
        tree, sample_ids, focal_labels
    )
    missing = sorted(sample for sample in focal_labels if not assignments.get(sample))
    duplicate = sorted(
        sample for sample in focal_labels if len(assignments.get(sample, [])) > 1
    )

    base: dict[str, object] = {
        "gene_id": gene_id,
        "tree_file": tree_file,
        "support_threshold": f"{threshold:g}",
        "focal_leaf_count": sum(bool(assignments.get(sample)) for sample in focal_labels),
        "missing_focal_samples": "|".join(missing),
        "duplicate_focal_samples": "|".join(duplicate),
        "unmapped_leaf_count": unmapped,
        "gene_cluster_count": "",
        "best_hypothesis_ids": "",
        "best_history_classes": "",
        "classification": "",
        "published_conflict_count": "",
        "published_rooted_rf_distance": "",
        "published_recovered_cluster_count": "",
        "best_loss_only_conflict_count": "",
        "best_loss_only_rooted_rf_distance": "",
        "best_loss_only_recovered_cluster_count": "",
        "published_minus_loss_conflict": "",
        "published_minus_loss_rf": "",
        "exact_hypothesis_match": "",
        "bp_external_sister_affinity": "",
        "white_external_sister_affinity": "",
    }

    if duplicate:
        return (
            {
                **base,
                "analysis_status": "multicopy_focal_samples",
                "classification": "excluded_multicopy",
                "interpretation": "At least one focal sample has multiple leaves in the gene tree.",
            },
            [],
        )
    if missing:
        return (
            {
                **base,
                "analysis_status": "incomplete_focal_samples",
                "classification": "excluded_incomplete",
                "interpretation": "The gene tree lacks one or more focal morph-labelled samples.",
            },
            [],
        )

    collapsed = collapse_low_support(
        relabelled,
        threshold,
        missing_support_policy="collapse",
    )
    keep = set(focal_labels.values())
    pruned = prune_tree(collapsed, keep)
    if pruned is None or descendant_names(pruned) != keep:
        return (
            {
                **base,
                "analysis_status": "prune_or_root_error",
                "classification": "excluded_error",
                "interpretation": "The six-tip rooted subtree could not be reconstructed.",
            },
            [],
        )

    gene_clusters = rooted_clusters(pruned)
    hypothesis_rows: list[dict[str, object]] = []
    for hypothesis in hypotheses:
        h_clusters = hypothesis["clusters"]
        conflict = conflicting_gene_clusters(gene_clusters, h_clusters)
        rf = rooted_rf_distance(gene_clusters, h_clusters)
        recovered = len(set(gene_clusters) & set(h_clusters))
        rank_key = (conflict, rf, -recovered)
        hypothesis_rows.append(
            {
                "gene_id": gene_id,
                "support_threshold": f"{threshold:g}",
                "hypothesis_id": hypothesis["hypothesis_id"],
                "history_class": hypothesis["history_class"],
                "conflicting_gene_clusters": conflict,
                "rooted_rf_distance": rf,
                "hypothesis_clusters_recovered": recovered,
                "hypothesis_cluster_count": len(h_clusters),
                "gene_cluster_count": len(gene_clusters),
                "rank_key": f"{conflict}|{rf}|{-recovered}",
                "is_best": "false",
                "_rank": rank_key,
            }
        )

    best_rank = min(row["_rank"] for row in hypothesis_rows)
    best = [row for row in hypothesis_rows if row["_rank"] == best_rank]
    for row in best:
        row["is_best"] = "true"
    best_ids = [str(row["hypothesis_id"]) for row in best]
    best_classes = sorted({str(row["history_class"]) for row in best})

    published = next(
        row for row in hypothesis_rows if row["hypothesis_id"] == PUBLISHED_HYPOTHESIS
    )
    loss_rows = [
        row for row in hypothesis_rows if row["history_class"] == LOSS_ONLY_CLASS
    ]
    best_loss_rank = min(row["_rank"] for row in loss_rows)
    best_losses = [row for row in loss_rows if row["_rank"] == best_loss_rank]
    best_loss = best_losses[0]

    published_best = PUBLISHED_HYPOTHESIS in best_ids
    loss_best = any(row["history_class"] == LOSS_ONLY_CLASS for row in best)
    if published_best and loss_best:
        classification = "tie_published_loss_only"
    elif published_best:
        classification = "published_best"
    else:
        classification = "loss_only_best"

    exact = [
        str(row["hypothesis_id"])
        for row in hypothesis_rows
        if int(row["rooted_rf_distance"]) == 0
    ]
    if not gene_clusters:
        classification = "unresolved_all_hypotheses_tie"

    label_to_sample = {label: sample for sample, label in focal_labels.items()}
    bp_affinity, white_affinity = external_sister_affinity(
        collapsed,
        label_to_sample,
        roles,
        morphs,
    )

    for row in hypothesis_rows:
        row.pop("_rank", None)

    return (
        {
            **base,
            "analysis_status": "complete_single_copy",
            "gene_cluster_count": len(gene_clusters),
            "best_hypothesis_ids": "|".join(sorted(best_ids)),
            "best_history_classes": "|".join(best_classes),
            "classification": classification,
            "published_conflict_count": published["conflicting_gene_clusters"],
            "published_rooted_rf_distance": published["rooted_rf_distance"],
            "published_recovered_cluster_count": published[
                "hypothesis_clusters_recovered"
            ],
            "best_loss_only_conflict_count": best_loss[
                "conflicting_gene_clusters"
            ],
            "best_loss_only_rooted_rf_distance": best_loss[
                "rooted_rf_distance"
            ],
            "best_loss_only_recovered_cluster_count": best_loss[
                "hypothesis_clusters_recovered"
            ],
            "published_minus_loss_conflict": int(
                published["conflicting_gene_clusters"]
            )
            - int(best_loss["conflicting_gene_clusters"]),
            "published_minus_loss_rf": int(published["rooted_rf_distance"])
            - int(best_loss["rooted_rf_distance"]),
            "exact_hypothesis_match": "|".join(sorted(exact)),
            "bp_external_sister_affinity": bp_affinity,
            "white_external_sister_affinity": white_affinity,
            "interpretation": (
                "Hypotheses are ranked by supported-cluster conflict, rooted RF distance, and recovered hypothesis clusters."
            ),
        },
        hypothesis_rows,
    )


def thresholds_from_text(value: str) -> tuple[float, ...]:
    values = tuple(float(item.strip()) for item in value.split(",") if item.strip())
    if not values:
        raise ValueError("No support thresholds were supplied")
    if any(not math.isfinite(item) or item < 0 or item > 100 for item in values):
        raise ValueError(f"Support thresholds must be in [0, 100]: {values}")
    return tuple(sorted(set(values)))


def tree_files(directory: Path, pattern: str) -> list[Path]:
    return sorted(path for path in directory.glob(pattern) if path.is_file())


def summarize(details: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    thresholds = sorted({str(row["support_threshold"]) for row in details}, key=float)
    for threshold in thresholds:
        rows = [row for row in details if str(row["support_threshold"]) == threshold]
        status = Counter(str(row["analysis_status"]) for row in rows)
        classification = Counter(str(row["classification"]) for row in rows)
        complete = status.get("complete_single_copy", 0)
        exact_published = sum(
            PUBLISHED_HYPOTHESIS
            in str(row["exact_hypothesis_match"]).split("|")
            for row in rows
            if row["analysis_status"] == "complete_single_copy"
        )
        exact_loss = sum(
            bool(str(row["exact_hypothesis_match"]))
            and PUBLISHED_HYPOTHESIS
            not in str(row["exact_hypothesis_match"]).split("|")
            for row in rows
            if row["analysis_status"] == "complete_single_copy"
        )
        output.append(
            {
                "support_threshold": threshold,
                "tree_files": len(rows),
                "complete_single_copy_gene_trees": complete,
                "incomplete_focal_gene_trees": status.get(
                    "incomplete_focal_samples", 0
                ),
                "multicopy_focal_gene_trees": status.get(
                    "multicopy_focal_samples", 0
                ),
                "parse_or_root_error_gene_trees": status.get(
                    "parse_or_root_error", 0
                )
                + status.get("prune_or_root_error", 0),
                "published_best": classification.get("published_best", 0),
                "loss_only_best": classification.get("loss_only_best", 0),
                "tie_published_loss_only": classification.get(
                    "tie_published_loss_only", 0
                ),
                "published_exact_match": exact_published,
                "loss_only_exact_match": exact_loss,
                "unresolved_all_hypotheses_tie": classification.get(
                    "unresolved_all_hypotheses_tie", 0
                ),
                "published_best_fraction_of_complete": (
                    f"{classification.get('published_best', 0) / complete:.6f}"
                    if complete
                    else ""
                ),
                "loss_only_best_fraction_of_complete": (
                    f"{classification.get('loss_only_best', 0) / complete:.6f}"
                    if complete
                    else ""
                ),
                "tie_fraction_of_complete": (
                    f"{classification.get('tie_published_loss_only', 0) / complete:.6f}"
                    if complete
                    else ""
                ),
                "interpretation": (
                    "Counts describe gene-tree topology support after collapsing internal nodes below the threshold; they are not independent-locus probabilities unless orthology and linkage filters justify that assumption."
                ),
            }
        )
    return output


def write_csv(
    path: Path,
    rows: Iterable[Mapping[str, object]],
    fields: Sequence[str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(fields), extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--hypotheses", type=Path, required=True)
    parser.add_argument("--trees-dir", type=Path, required=True)
    parser.add_argument("--pattern", default="*.treefile")
    parser.add_argument(
        "--thresholds",
        default=",".join(str(int(value)) for value in DEFAULT_THRESHOLDS),
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--hypothesis-output", type=Path, required=True)
    parser.add_argument("--summary-output", type=Path, required=True)
    parser.add_argument("--summary-json", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    focal_labels, roles, morphs = panel_metadata(args.panel)
    hypotheses = hypothesis_metadata(args.hypotheses)
    thresholds = thresholds_from_text(args.thresholds)
    paths = tree_files(args.trees_dir, args.pattern)
    if not paths:
        raise SystemExit(
            f"No gene trees matching {args.pattern!r} in {args.trees_dir}"
        )

    details: list[dict[str, object]] = []
    hypothesis_details: list[dict[str, object]] = []
    for path in paths:
        gene_id = path.name
        for suffix in (".treefile", ".nwk", ".newick", ".tre", ".tree"):
            if gene_id.endswith(suffix):
                gene_id = gene_id[: -len(suffix)]
                break
        try:
            tree = parse_newick(path.read_text(encoding="utf-8"))
        except Exception as exc:
            for threshold in thresholds:
                details.append(
                    {
                        "gene_id": gene_id,
                        "tree_file": str(path),
                        "support_threshold": f"{threshold:g}",
                        "analysis_status": "parse_or_root_error",
                        "focal_leaf_count": "",
                        "missing_focal_samples": "",
                        "duplicate_focal_samples": "",
                        "unmapped_leaf_count": "",
                        "gene_cluster_count": "",
                        "best_hypothesis_ids": "",
                        "best_history_classes": "",
                        "classification": "excluded_error",
                        "published_conflict_count": "",
                        "published_rooted_rf_distance": "",
                        "published_recovered_cluster_count": "",
                        "best_loss_only_conflict_count": "",
                        "best_loss_only_rooted_rf_distance": "",
                        "best_loss_only_recovered_cluster_count": "",
                        "published_minus_loss_conflict": "",
                        "published_minus_loss_rf": "",
                        "exact_hypothesis_match": "",
                        "bp_external_sister_affinity": "",
                        "white_external_sister_affinity": "",
                        "interpretation": f"{type(exc).__name__}: {exc}",
                    }
                )
            continue

        for threshold in thresholds:
            detail, per_hypothesis = score_one_tree(
                gene_id=gene_id,
                tree_file=str(path),
                tree=tree,
                threshold=threshold,
                focal_labels=focal_labels,
                roles=roles,
                morphs=morphs,
                hypotheses=hypotheses,
            )
            details.append(detail)
            hypothesis_details.extend(per_hypothesis)

    summary = summarize(details)
    payload = {
        "tree_file_count": len(paths),
        "support_thresholds": list(thresholds),
        "panel": str(args.panel),
        "hypotheses": str(args.hypotheses),
        "published_hypothesis": PUBLISHED_HYPOTHESIS,
        "loss_only_hypothesis_count": sum(
            hypothesis["history_class"] == LOSS_ONLY_CLASS
            for hypothesis in hypotheses
        ),
        "summary": summary,
        "claim_limit": (
            "Per-gene topology counts measure concordance with predefined rooted histories. They do not by themselves distinguish introgression from incomplete lineage sorting, establish locus independence, or demonstrate molecular anthocyanin reactivation."
        ),
    }

    write_csv(args.output, details, DETAIL_FIELDS)
    write_csv(
        args.hypothesis_output,
        hypothesis_details,
        HYPOTHESIS_DETAIL_FIELDS,
    )
    write_csv(args.summary_output, summary, SUMMARY_FIELDS)
    args.summary_json.parent.mkdir(parents=True, exist_ok=True)
    args.summary_json.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"tree_files={len(paths)}")
    for row in summary:
        print(
            f"threshold={row['support_threshold']} "
            f"complete={row['complete_single_copy_gene_trees']} "
            f"published={row['published_best']} "
            f"loss_only={row['loss_only_best']} "
            f"tie={row['tie_published_loss_only']}"
        )
    print(args.summary_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
