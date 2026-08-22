#!/usr/bin/env python3
"""Run a conservative binary orientation preflight on an accepted Comp1061 tree.

U = upward/erect, D = downward/nodding. Unresolved tips remain missing data.
The script reuses the tested binary Mk likelihood implementation used by the
flower-colour pipeline, but keeps orientation-specific gates and labels.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import random
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("_eazami_binary_mk", HERE / "fit_binary_flower_colour_mk_models.py")
assert SPEC and SPEC.loader
mk = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mk
SPEC.loader.exec_module(mk)


def load_orientation_states(path: Path) -> tuple[dict[str, str], set[str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    tips = [r["tip_id"].strip() for r in rows]
    if len(rows) != 20 or len(set(tips)) != 20:
        raise ValueError("orientation crosswalk must contain exactly 20 unique Comp1061 tips")
    states = {r["tip_id"]: r["analysis_state"] for r in rows if r["analysis_state"] in {"U", "D"}}
    return states, set(tips)


def tree_tip_names(root) -> set[str]:
    out = set()
    def walk(node):
        if not node.children:
            out.add(node.name)
        for child in node.children:
            walk(child)
    walk(root)
    return out


def require_gates(summary_path: Path, acceptance_path: Path) -> tuple[dict, dict]:
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    acceptance = json.loads(acceptance_path.read_text(encoding="utf-8"))
    if acceptance.get("tree_gate_ready") is not True:
        raise RuntimeError("accepted branch-length tree gate is not satisfied")
    if summary.get("execution_gates", {}).get("orientation_mk_preflight_allowed_after_accepted_tree") is not True:
        raise RuntimeError("orientation post-tree preflight gate is not enabled")
    counts = summary.get("fixed_state_counts", {})
    if min(int(counts.get("upward_or_erect", 0)), int(counts.get("downward_or_nodding", 0))) < 5:
        raise RuntimeError("orientation state-balance gate requires at least five fixed tips per state")
    return summary, acceptance


def sankoff_min_transitions(root, states: dict[str, str]) -> int:
    inf = 10**9
    def rec(node):
        if not node.children:
            state = states.get(node.name)
            if state == "U":
                return (0, inf)
            if state == "D":
                return (inf, 0)
            return (0, 0)
        up = 0
        down = 0
        for child in node.children:
            cu, cd = rec(child)
            up += min(cu, cd + 1)
            down += min(cd, cu + 1)
        return up, down
    return int(min(rec(root)))


def conditional_root_probability(root, states: dict[str, str], q_ud: float, q_du: float, root_prior: str) -> float:
    def rec(node):
        if not node.children:
            state = states.get(node.name)
            if state == "U":
                return (1.0, 0.0)
            if state == "D":
                return (0.0, 1.0)
            return (1.0, 1.0)
        like = [1.0, 1.0]
        for child in node.children:
            child_like = rec(child)
            if child.length is None:
                raise ValueError(f"missing branch length below {child.name or 'internal node'}")
            p = mk.transition(child.length, q_ud, q_du)
            like[0] *= p[0][0] * child_like[0] + p[0][1] * child_like[1]
            like[1] *= p[1][0] * child_like[0] + p[1][1] * child_like[1]
        return like
    like = rec(root)
    if root_prior == "flat":
        prior = (0.5, 0.5)
    elif root_prior == "equilibrium":
        total = q_ud + q_du
        prior = (q_du / total, q_ud / total)
    else:
        raise ValueError("root_prior must be flat or equilibrium")
    weighted = (prior[0] * like[0], prior[1] * like[1])
    denom = sum(weighted)
    if denom <= 0:
        raise ValueError("zero root likelihood")
    return weighted[0] / denom


def _draw_state(prob_up: float, rng: random.Random) -> int:
    return 0 if rng.random() < prob_up else 1


def simulate_tip_states(root, q_ud: float, q_du: float, root_prior: str, rng: random.Random) -> dict[str, str]:
    if root_prior == "flat":
        prior_up = 0.5
    else:
        prior_up = q_du / (q_ud + q_du)
    states = {}
    def descend(node, parent_state: int | None = None):
        if parent_state is None:
            state = _draw_state(prior_up, rng)
        else:
            if node.length is None:
                raise ValueError(f"missing branch length below {node.name or 'internal node'}")
            p = mk.transition(node.length, q_ud, q_du)[parent_state]
            state = 0 if rng.random() < p[0] else 1
        if not node.children:
            states[node.name] = "U" if state == 0 else "D"
        for child in node.children:
            descend(child, state)
    descend(root)
    return states


def _quantile(values: list[int], p: float) -> float:
    x = sorted(values)
    if not x:
        return float("nan")
    idx = (len(x) - 1) * p
    lo, hi = math.floor(idx), math.ceil(idx)
    if lo == hi:
        return float(x[lo])
    return x[lo] * (hi - idx) + x[hi] * (idx - lo)


def _two_sided_tail(values: list[int], observed: int) -> float:
    n = len(values)
    lo = (1 + sum(v <= observed for v in values)) / (n + 1)
    hi = (1 + sum(v >= observed for v in values)) / (n + 1)
    return min(1.0, 2 * min(lo, hi))


def adequacy_diagnostics(root, observed: dict[str, str], q_ud: float, q_du: float, root_prior: str, reps: int, seed: int) -> dict:
    if reps < 100:
        raise ValueError("adequacy diagnostics require at least 100 simulations")
    rng = random.Random(seed)
    observed_up = sum(v == "U" for v in observed.values())
    observed_steps = sankoff_min_transitions(root, observed)
    n_up = []
    steps = []
    for _ in range(reps):
        sim_all = simulate_tip_states(root, q_ud, q_du, root_prior, rng)
        sim = {tip: sim_all[tip] for tip in observed}
        n_up.append(sum(v == "U" for v in sim.values()))
        steps.append(sankoff_min_transitions(root, sim))
    return {
        "simulation_replicates": reps,
        "seed": seed,
        "observed_upward_tips": observed_up,
        "simulated_upward_tips_median": statistics.median(n_up),
        "simulated_upward_tips_q025_q975": [_quantile(n_up, 0.025), _quantile(n_up, 0.975)],
        "upward_count_two_sided_tail": _two_sided_tail(n_up, observed_up),
        "observed_minimum_transition_steps": observed_steps,
        "simulated_minimum_transition_steps_median": statistics.median(steps),
        "simulated_minimum_transition_steps_q025_q975": [_quantile(steps, 0.025), _quantile(steps, 0.975)],
        "parsimony_steps_two_sided_tail": _two_sided_tail(steps, observed_steps),
        "interpretation": "Small tail probabilities flag a fitted binary Mk model that poorly reproduces state balance or phylogenetic clustering. These are fixed-parameter parametric checks, not posterior predictive p-values."
    }


def _orientation_fit(raw: dict) -> dict:
    return {
        "n_observed_tips": raw["n_observed_tips"],
        "ER": {
            "q_upward_to_downward": raw["ER"]["q_C_to_W"],
            "q_downward_to_upward": raw["ER"]["q_W_to_C"],
            "logLik": raw["ER"]["logLik"],
            "AIC": raw["ER"]["AIC"],
            "AICc": raw["ER"]["AICc"],
        },
        "ARD": {
            "q_upward_to_downward": raw["ARD"]["q_C_to_W"],
            "q_downward_to_upward": raw["ARD"]["q_W_to_C"],
            "downward_gain_to_upward_gain_ratio": raw["ARD"]["loss_to_regain_ratio"],
            "logLik": raw["ARD"]["logLik"],
            "AIC": raw["ARD"]["AIC"],
            "AICc": raw["ARD"]["AICc"],
        },
        "comparison": raw["comparison"],
    }


def analyse(tree_path: Path, crosswalk_path: Path, summary_path: Path, acceptance_path: Path, reps: int = 2000, seed: int = 20260822) -> dict:
    require_gates(summary_path, acceptance_path)
    states, panel_tips = load_orientation_states(crosswalk_path)
    root = mk.Parser(tree_path.read_text(encoding="utf-8")).parse()
    tree_tips = tree_tip_names(root)
    missing = panel_tips - tree_tips
    if missing:
        raise ValueError(f"orientation panel tips missing from accepted tree: {sorted(missing)}")
    internal_states = {tip: ("C" if state == "U" else "W") for tip, state in states.items()}
    minimum_steps = sankoff_min_transitions(root, states)
    fits = {}
    for prior_index, prior in enumerate(("equilibrium", "flat")):
        raw = mk.fit_models(root, internal_states, prior)
        fit = _orientation_fit(raw)
        for model_index, model in enumerate(("ER", "ARD")):
            q_ud = fit[model]["q_upward_to_downward"]
            q_du = fit[model]["q_downward_to_upward"]
            fit[model]["root_upward_probability"] = conditional_root_probability(root, states, q_ud, q_du, prior)
            fit[model]["adequacy"] = adequacy_diagnostics(
                root, states, q_ud, q_du, prior, reps, seed + prior_index * 100 + model_index
            )
        fits[prior] = fit
    root_probs = [fits[p][m]["root_upward_probability"] for p in fits for m in ("ER", "ARD")]
    return {
        "contract_version": "orientation_comp1061_mk_preflight_v1",
        "state_encoding": {"U": "upward_or_erect", "D": "downward_or_nodding", "unresolved": "missing"},
        "panel_tips": len(panel_tips),
        "observed_binary_tips": len(states),
        "observed_state_counts": {"U": sum(v == "U" for v in states.values()), "D": sum(v == "D" for v in states.values())},
        "minimum_parsimony_transition_steps": minimum_steps,
        "fits_by_root_prior": fits,
        "root_upward_probability_range_across_model_prior_sensitivity": [min(root_probs), max(root_probs)],
        "execution_status": "preflight_only",
        "claim_boundary": "This analysis can identify a lower bound on state changes and evaluate binary Mk fit/sensitivity on an accepted branch-length tree. It does not by itself establish population-level independent transitions, parallel/convergent evolution, adaptive selection, or orientation fitness effects because the source states are taxon-concept annotations rather than same-voucher phenotypes."
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--tree", type=Path, required=True)
    p.add_argument("--crosswalk", type=Path, required=True)
    p.add_argument("--summary", type=Path, required=True)
    p.add_argument("--tree-acceptance", type=Path, required=True)
    p.add_argument("--reps", type=int, default=2000)
    p.add_argument("--seed", type=int, default=20260822)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    result = analyse(a.tree, a.crosswalk, a.summary, a.tree_acceptance, a.reps, a.seed)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
