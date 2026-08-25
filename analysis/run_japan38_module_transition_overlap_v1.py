#!/usr/bin/env python3
"""Branch-wise transition-overlap diagnostic for Japan38 capitulum modules.

This is a model-based diagnostic, not a causal/adaptive test. It fits a
single-rate symmetric Mk model separately to orientation, phyllary posture,
and stickiness on the reconstructed Japan38 concept tree, then estimates
posterior transition probability for each informative branch. Cross-module
overlap is summarized with rank correlation and a branch-length-stratified
permutation null.

Missing/ambiguous tip states remain ambiguous. A replicated concept is
collapsed only when monophyletic if it has an observed analysed trait. A
replicated concept that is fully unresolved for every analysed trait may be
pruned without blocking the analysis, while its monophyly remains a separate
tree diagnostic. Concepts disallowed by the frozen trait-ASR reconciliation
(e.g. JPN_31) are pruned. Branches are matched across modules by their unique
descendant-tip signature, never by potentially duplicated internal support
labels.
"""
from __future__ import annotations

import argparse, csv, json, math, random, statistics
from pathlib import Path
from Bio import Phylo

STATE_UNIVERSE = {
    "orientation": ("U", "D"),
    "phyllary": ("appressed", "ascending", "spreading", "recurved"),
    "stickiness": ("sticky", "nonsticky"),
}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as h:
        return list(csv.DictReader(h))


def concept_info(path: Path):
    rows = read_csv(path)
    cmap = {
        r["paper_japan_member_id"]: [x for x in r["tip_ids"].split("|") if x]
        for r in rows
    }
    allowed = {
        r["paper_japan_member_id"]: (
            (r.get("trait_asr_primary_allowed") or "true").strip().lower() != "false"
        )
        for r in rows
    }
    if len(cmap) != 38:
        raise ValueError(f"expected 38 concepts, found {len(cmap)}")
    return cmap, allowed


def concept_map(path: Path):
    return concept_info(path)[0]


def trait_state(row, trait):
    if trait == "orientation":
        x = (row.get("orientation_state") or "").strip()
        if x in {"upward_or_erect", "upward_or_ascending"}:
            return {"U"}
        if x == "downward_or_nodding":
            return {"D"}
    elif trait == "phyllary":
        x = (row.get("phyllary_posture") or "").strip()
        mapping = {
            "appressed": {"appressed"},
            "ascending": {"ascending"},
            "spreading": {"spreading"},
            "appressed_or_ascending": {"appressed", "ascending"},
            "ascending_or_recurved": {"ascending", "recurved"},
            "spreading_or_recurved": {"spreading", "recurved"},
        }
        if x in mapping:
            return mapping[x]
    elif trait == "stickiness":
        x = (row.get("stickiness_state") or "").strip()
        if x == "sticky":
            return {"sticky"}
        if x == "nonsticky_or_nearly_nonsticky":
            return {"nonsticky"}
    return set(STATE_UNIVERSE[trait])


def trait_states(path: Path):
    rows = read_csv(path)
    by = {r["paper_japan_member_id"]: r for r in rows}
    return {
        trait: {mid: trait_state(row, trait) for mid, row in by.items()}
        for trait in STATE_UNIVERSE
    }


def resolved_for_any_trait(states, mid):
    return any(
        states[trait].get(mid, set(universe)) != set(universe)
        for trait, universe in STATE_UNIVERSE.items()
    )


def _validate_raw_tree(tree, cmap):
    names = {t.name for t in tree.get_terminals()}
    expected = {x for xs in cmap.values() for x in xs} | {"OUTGROUP_saff"}
    if names != expected:
        raise ValueError(
            f"tree tip mismatch missing={sorted(expected-names)} extra={sorted(names-expected)}"
        )
    tree.root_with_outgroup("OUTGROUP_saff")
    reps = [(m, xs) for m, xs in cmap.items() if len(xs) > 1]
    if len(reps) != 1 or reps[0][0] != "JPN_20" or len(reps[0][1]) != 2:
        raise ValueError(f"unexpected replicated concepts: {reps}")
    return reps[0]


def load_concept_tree(tree_path: Path, cmap):
    """Strict legacy loader used by tests/diagnostics when JPN20 is observed."""
    tree = Phylo.read(str(tree_path), "newick")
    _, two = _validate_raw_tree(tree, cmap)
    mrca = tree.common_ancestor({"name": two[0]}, {"name": two[1]})
    if {x.name for x in mrca.get_terminals()} != set(two):
        raise ValueError("JPN_20 biological replicates are not monophyletic")
    mrca.clades = []
    mrca.name = "JPN_20"
    reverse = {xs[0]: mid for mid, xs in cmap.items() if len(xs) == 1}
    for tip in tree.get_terminals():
        if tip.name in reverse:
            tip.name = reverse[tip.name]
    tree.prune(target="OUTGROUP_saff")
    if {t.name for t in tree.get_terminals()} != set(cmap):
        raise ValueError("concept-tree tip set mismatch")
    return tree


def load_analysis_tree(tree_path: Path, cmap, allowed, states):
    """Prepare the primary trait tree without forcing unobserved/conflicted concepts."""
    tree = Phylo.read(str(tree_path), "newick")
    mid, two = _validate_raw_tree(tree, cmap)
    mrca = tree.common_ancestor({"name": two[0]}, {"name": two[1]})
    descendants = {x.name for x in mrca.get_terminals()}
    monophyletic = descendants == set(two)
    replicate_resolved = resolved_for_any_trait(states, mid)
    excluded = []

    if replicate_resolved:
        if not monophyletic:
            raise ValueError(
                "JPN_20 biological replicates are not monophyletic but JPN_20 has an observed analysed trait"
            )
        mrca.clades = []
        mrca.name = mid
        replicate_mode = "collapsed_monophyletic_replicated_concept"
    else:
        for tip in two:
            tree.prune(target=tip)
        excluded.append(mid)
        replicate_mode = "pruned_fully_unresolved_replicated_concept"

    for concept, xs in cmap.items():
        if allowed.get(concept, True) or len(xs) != 1:
            continue
        if xs[0] in {t.name for t in tree.get_terminals()}:
            tree.prune(target=xs[0])
        excluded.append(concept)

    reverse = {
        xs[0]: concept
        for concept, xs in cmap.items()
        if len(xs) == 1 and allowed.get(concept, True)
    }
    for tip in tree.get_terminals():
        if tip.name in reverse:
            tip.name = reverse[tip.name]

    tree.prune(target="OUTGROUP_saff")
    expected = {
        concept
        for concept in cmap
        if allowed.get(concept, True) and concept not in set(excluded)
    }
    final = {t.name for t in tree.get_terminals()}
    if final != expected:
        raise ValueError(
            f"analysis-tree tip mismatch missing={sorted(expected-final)} extra={sorted(final-expected)}"
        )
    return tree, {
        "replicate_monophyly": monophyletic,
        "replicate_resolved_for_any_trait": replicate_resolved,
        "replicate_mode": replicate_mode,
        "replicate_mrca_descendants": sorted(descendants),
        "excluded_concepts": sorted(set(excluded)),
        "concept_tips": len(final),
    }


def transition_matrix(k, q, t):
    e = math.exp(-k * q * max(float(t or 0.0), 0.0))
    same = 1.0 / k + (1.0 - 1.0 / k) * e
    diff = 1.0 / k - (1.0 / k) * e
    return [[same if i == j else diff for j in range(k)] for i in range(k)]


def postorder(clade):
    for c in clade.clades:
        yield from postorder(c)
    yield clade


def preorder(clade):
    yield clade
    for c in clade.clades:
        yield from preorder(c)


def resolved_tip_names(states, universe):
    u = set(universe)
    return {mid for mid, s in states.items() if set(s) != u}


def edge_id(child):
    """Unique rooted-tree branch identifier independent of duplicated node labels."""
    return "|".join(sorted(t.name for t in child.get_terminals()))


def fit_trait(tree, states, universe):
    state_list = list(universe)
    k = len(state_list)
    nodes = list(preorder(tree.root))
    positive = [
        float(c.branch_length)
        for c in nodes
        if c is not tree.root and (c.branch_length or 0) > 0
    ]
    median_t = statistics.median(positive) if positive else 1.0
    u = set(universe)
    allowed = {}
    for tip in tree.get_terminals():
        ss = set(states.get(tip.name, u))
        v = [1.0 if s in ss else 0.0 for s in state_list]
        z = sum(v)
        if z <= 0:
            raise ValueError(f"no allowed states for {tip.name}")
        allowed[tip] = [x / z for x in v]

    def likelihood(q, want_messages=False):
        up, logscale, child_msg = {}, {}, {}
        for node in postorder(tree.root):
            if node.is_terminal():
                up[node] = allowed[node][:]
                logscale[node] = 0.0
            else:
                raw = [1.0] * k
                scale = 0.0
                for child in node.clades:
                    P = transition_matrix(k, q, child.branch_length or 0.0)
                    msg = [
                        sum(P[i][j] * up[child][j] for j in range(k))
                        for i in range(k)
                    ]
                    child_msg[(node, child)] = msg
                    for i in range(k):
                        raw[i] *= msg[i]
                    scale += logscale[child]
                z = sum(raw)
                if z <= 0 or not math.isfinite(z):
                    return -math.inf if not want_messages else None
                up[node] = [x / z for x in raw]
                logscale[node] = scale + math.log(z)
        root_like = sum((1.0 / k) * up[tree.root][i] for i in range(k))
        ll = math.log(root_like) + logscale[tree.root]
        if not want_messages:
            return ll
        return ll, up, child_msg

    xs = [10 ** (-3 + 4 * i / 160) for i in range(161)]
    qs = [x / median_t for x in xs]
    ll_best, q_best = max((likelihood(q), q) for q in qs)
    _, up, child_msg = likelihood(q_best, want_messages=True)
    down = {tree.root: [1.0 / k] * k}
    edge_rows = []
    resolved = resolved_tip_names(states, universe)
    total_resolved = len(resolved)

    def descendant_resolved(node):
        return sum(1 for t in node.get_terminals() if t.name in resolved)

    for parent in preorder(tree.root):
        if parent.is_terminal():
            continue
        for child in parent.clades:
            siblings = [s for s in parent.clades if s is not child]
            outside_parent = down[parent][:]
            for sib in siblings:
                msg = child_msg[(parent, sib)]
                outside_parent = [
                    outside_parent[i] * msg[i] for i in range(k)
                ]
            z = sum(outside_parent)
            if z > 0:
                outside_parent = [x / z for x in outside_parent]
            P = transition_matrix(k, q_best, child.branch_length or 0.0)
            dchild = [
                sum(outside_parent[i] * P[i][j] for i in range(k))
                for j in range(k)
            ]
            z = sum(dchild)
            down[child] = (
                [x / z for x in dchild] if z > 0 else [1.0 / k] * k
            )
            joint = [
                [
                    outside_parent[i] * P[i][j] * up[child][j]
                    for j in range(k)
                ]
                for i in range(k)
            ]
            z = sum(sum(r) for r in joint)
            pchg = (
                None
                if z <= 0
                else 1.0 - sum(joint[i][i] for i in range(k)) / z
            )
            prior_pchg = (
                (k - 1.0) / k
                * (1.0 - math.exp(-k * q_best * float(child.branch_length or 0.0)))
            )
            inside = descendant_resolved(child)
            edge_rows.append(
                {
                    "edge_id": edge_id(child),
                    "parent_label": parent.name,
                    "child_label": child.name,
                    "branch_length": float(child.branch_length or 0.0),
                    "resolved_inside": inside,
                    "resolved_outside": total_resolved - inside,
                    "informative": inside > 0 and inside < total_resolved,
                    "transition_posterior": pchg,
                    "branch_length_prior_transition": prior_pchg,
                    "transition_excess_over_branch_prior": (
                        None if pchg is None else pchg - prior_pchg
                    ),
                }
            )

    # No two rooted branches may share a descendant-tip signature.
    ids = [r["edge_id"] for r in edge_rows]
    if len(ids) != len(set(ids)):
        raise ValueError("non-unique descendant-tip edge identifiers")

    k_q_median = k * q_best * median_t
    prior_change_median = (
        (k - 1.0) / k * (1.0 - math.exp(-k_q_median))
    )
    return {
        "states": state_list,
        "resolved_tips": total_resolved,
        "q_equal_rates": q_best,
        "log_likelihood": ll_best,
        "median_positive_branch_length": median_t,
        "k_q_times_median_branch": k_q_median,
        "prior_transition_probability_at_median_branch": prior_change_median,
        "saturation_warning": k_q_median >= 3.0,
        "edges": edge_rows,
    }


def rankdata(vals):
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    ranks = [0.0] * len(vals)
    i = 0
    while i < len(order):
        j = i + 1
        while j < len(order) and vals[order[j]] == vals[order[i]]:
            j += 1
        r = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[order[k]] = r
        i = j
    return ranks


def pearson(x, y):
    if len(x) < 3:
        return None
    mx, my = statistics.mean(x), statistics.mean(y)
    dx, dy = [v - mx for v in x], [v - my for v in y]
    den = math.sqrt(sum(v * v for v in dx) * sum(v * v for v in dy))
    return sum(a * b for a, b in zip(dx, dy)) / den if den > 0 else None


def spearman(x, y):
    return pearson(rankdata(x), rankdata(y))


def branch_bins(lengths, bins=4):
    order = sorted(range(len(lengths)), key=lambda i: lengths[i])
    labels = [0] * len(lengths)
    for rank, idx in enumerate(order):
        labels[idx] = min(bins - 1, int(rank * bins / len(order)))
    return labels


def stratified_perm_p(x, y, lengths, observed, rng, nperm):
    if observed is None or len(x) < 4:
        return None
    labels = branch_bins(lengths, bins=min(4, max(2, len(x) // 4)))
    idx_by = {}
    for i, b in enumerate(labels):
        idx_by.setdefault(b, []).append(i)
    ge = valid = 0
    for _ in range(nperm):
        yp = y[:]
        for inds in idx_by.values():
            vals = [yp[i] for i in inds]
            rng.shuffle(vals)
            for i, v in zip(inds, vals):
                yp[i] = v
        r = spearman(x, yp)
        if r is None:
            continue
        valid += 1
        if r >= observed - 1e-12:
            ge += 1
    return (ge + 1) / (valid + 1) if valid else None


def compare_traits(fits, seed=20260825, nperm=999):
    rng = random.Random(seed)
    out = {}
    traits = list(fits)
    for ai in range(len(traits)):
        for bi in range(ai + 1, len(traits)):
            a, b = traits[ai], traits[bi]
            ea = {
                r["edge_id"]: r
                for r in fits[a]["edges"]
                if r["informative"] and r["transition_posterior"] is not None
            }
            eb = {
                r["edge_id"]: r
                for r in fits[b]["edges"]
                if r["informative"] and r["transition_posterior"] is not None
            }
            keys = sorted(set(ea) & set(eb))
            x = [ea[k]["transition_posterior"] for k in keys]
            y = [eb[k]["transition_posterior"] for k in keys]
            xe = [ea[k]["transition_excess_over_branch_prior"] for k in keys]
            ye = [eb[k]["transition_excess_over_branch_prior"] for k in keys]
            lengths = [ea[k]["branch_length"] for k in keys]
            rho = spearman(x, y)
            rho_excess = spearman(xe, ye)
            out[f"{a}__{b}"] = {
                "shared_informative_edges": len(keys),
                "spearman_transition_posterior": rho,
                "branch_length_stratified_one_sided_p_for_positive_overlap": stratified_perm_p(
                    x, y, lengths, rho, rng, nperm
                ),
                "spearman_transition_excess_over_branch_prior": rho_excess,
                "branch_length_stratified_one_sided_p_for_positive_excess_overlap": stratified_perm_p(
                    xe, ye, lengths, rho_excess, rng, nperm
                ),
                "sum_product_transition_posterior": sum(i * j for i, j in zip(x, y)),
            }
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--tree", type=Path, required=True)
    p.add_argument("--concept-map", type=Path, required=True)
    p.add_argument("--trait-seed", type=Path, required=True)
    p.add_argument("--permutations", type=int, default=999)
    p.add_argument("--seed", type=int, default=20260825)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()

    cmap, allowed = concept_info(a.concept_map)
    states = trait_states(a.trait_seed)
    tree, tree_diag = load_analysis_tree(a.tree, cmap, allowed, states)
    fits = {
        t: fit_trait(tree, states[t], STATE_UNIVERSE[t])
        for t in STATE_UNIVERSE
    }
    result = {
        "contract_version": "japan38_module_transition_overlap_v1",
        "model": "separate symmetric equal-rates Mk per module",
        "tree_diagnostic": tree_diag,
        "traits": {
            t: {k: v for k, v in fit.items() if k != "edges"}
            for t, fit in fits.items()
        },
        "pairwise_overlap": compare_traits(fits, a.seed, a.permutations),
        "permutations": a.permutations,
        "seed": a.seed,
        "branch_identity": "unique descendant-tip signature on the rooted analysis tree",
        "claim_boundary": (
            "Branch-wise transition-posterior overlap diagnostic only. Positive overlap can motivate common-lability; "
            "weak/heterogeneous overlap can motivate modularity. It does not identify shared developmental genetics, "
            "ecological adaptation, or causal selection. Missing/ambiguous states remain uncertain. Fully unresolved "
            "replicated concepts and concepts disallowed by the frozen trait-ASR reconciliation are pruned. High Mk "
            "saturation diagnostics require caution because transition posteriors can become weakly discriminating."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
