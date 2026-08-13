#!/usr/bin/env python3
"""Interpret an accepted public Japanese-origin compatibility tree.

This script is deliberately downstream of tree-artifact acceptance. It asks the
topological questions needed to decide where new continental sampling would
add information, without converting one concatenated topology into a
biogeographic direction claim.

It tests the published Moreyra Japan-38 main-radiation membership, Ryukyu
Arenicola placement, and the neighbourhoods of C. dipsacolepis and C. lineare.
Candidate sister-neighbour taxa are written as a sampling shortlist only. New
China sampling remains unfrozen until mapping and gene-tree/coalescent
sensitivities agree.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence

EXCEPTIONS = {"Cirsium dipsacolepis", "Cirsium lineare"}
AREN_TAXA = {"Cirsium brevicaule", "Cirsium irumtiense"}


class Node:
    __slots__ = ("name", "length", "children", "parent")
    def __init__(self, name: str = "", length: float | None = None):
        self.name = name
        self.length = length
        self.children: list[Node] = []
        self.parent: Node | None = None
    @property
    def is_tip(self) -> bool:
        return not self.children


class NewickParser:
    def __init__(self, text: str):
        self.text = text.strip()
        self.i = 0
    def ws(self):
        while self.i < len(self.text) and self.text[self.i].isspace():
            self.i += 1
    def label(self) -> str:
        self.ws()
        if self.i >= len(self.text) or self.text[self.i] in ",():;":
            return ""
        if self.text[self.i] in "'\"":
            q = self.text[self.i]
            self.i += 1
            out = []
            while self.i < len(self.text):
                c = self.text[self.i]
                self.i += 1
                if c == q:
                    if self.i < len(self.text) and self.text[self.i] == q:
                        out.append(q); self.i += 1; continue
                    break
                out.append(c)
            return "".join(out).strip()
        start = self.i
        while self.i < len(self.text) and self.text[self.i] not in ",():;":
            self.i += 1
        return self.text[start:self.i].strip()
    def length(self) -> float | None:
        self.ws()
        if self.i >= len(self.text) or self.text[self.i] != ":":
            return None
        self.i += 1; self.ws(); start = self.i
        while self.i < len(self.text) and self.text[self.i] not in ",();":
            self.i += 1
        token = self.text[start:self.i].strip()
        if not token:
            raise ValueError("empty branch length")
        return float(token)
    def subtree(self) -> Node:
        self.ws()
        if self.i >= len(self.text):
            raise ValueError("unexpected end of Newick")
        if self.text[self.i] == "(":
            self.i += 1
            n = Node()
            while True:
                c = self.subtree(); c.parent = n; n.children.append(c); self.ws()
                if self.i >= len(self.text):
                    raise ValueError("unclosed Newick group")
                if self.text[self.i] == ",":
                    self.i += 1; continue
                if self.text[self.i] == ")":
                    self.i += 1; break
                raise ValueError(f"unexpected Newick character {self.text[self.i]!r}")
            n.name = self.label(); n.length = self.length(); return n
        name = self.label()
        if not name:
            raise ValueError(f"missing tip label near offset {self.i}")
        return Node(name, self.length())
    def parse(self) -> Node:
        root = self.subtree(); self.ws()
        if self.i < len(self.text) and self.text[self.i] == ";":
            self.i += 1
        self.ws()
        if self.i != len(self.text):
            raise ValueError(f"trailing Newick text at offset {self.i}")
        return root


def clean(x: object) -> str:
    return "" if x is None else str(x).strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as h:
        rows = [{k: clean(v) for k, v in r.items()} for r in csv.DictReader(h)
                if any(clean(v) for v in r.values())]
    if not rows:
        raise ValueError(f"{path}: no rows")
    return rows


def descendants(node: Node) -> set[str]:
    if node.is_tip:
        return {node.name}
    out: set[str] = set()
    for c in node.children:
        out.update(descendants(c))
    return out


def tip_index(root: Node) -> dict[str, Node]:
    out: dict[str, Node] = {}
    def walk(n: Node):
        if n.is_tip:
            if n.name in out:
                raise ValueError(f"duplicate tree tip {n.name}")
            out[n.name] = n; return
        for c in n.children: walk(c)
    walk(root)
    return out


def reroot_on_reference_clade(root: Node, references: set[str]) -> Node:
    """Root an arbitrarily rooted Newick on the edge separating references.

    The input root is suppressed when it is an unlabelled degree-two artifact.
    This makes individual concatenated and unrooted ASTRAL trees comparable
    without treating their serialized root position as biological evidence.
    """
    observed = set(tip_index(root))
    if not references or not references < observed:
        raise ValueError("reference rooting requires a non-empty proper tip subset")
    missing = sorted(references - observed)
    if missing:
        raise ValueError(f"reference tips absent from tree: {missing}")

    adjacency: dict[Node, list[Node]] = defaultdict(list)

    def connect(node: Node) -> None:
        for child in node.children:
            adjacency[node].append(child)
            adjacency[child].append(node)
            connect(child)

    connect(root)
    if not root.name and len(adjacency[root]) == 2:
        left, right = adjacency.pop(root)
        adjacency[left].remove(root)
        adjacency[right].remove(root)
        adjacency[left].append(right)
        adjacency[right].append(left)

    def component_tips(start: Node, blocked: Node) -> set[str]:
        tips: set[str] = set()
        stack = [(start, blocked)]
        while stack:
            node, parent = stack.pop()
            neighbours = [item for item in adjacency[node] if item is not parent]
            if not neighbours:
                if not node.name:
                    raise ValueError("unlabelled leaf encountered while rerooting")
                tips.add(node.name)
            else:
                stack.extend((item, node) for item in neighbours)
        return tips

    split: tuple[Node, Node] | None = None
    seen_edges: set[frozenset[Node]] = set()
    for left, neighbours in adjacency.items():
        for right in neighbours:
            edge = frozenset((left, right))
            if edge in seen_edges:
                continue
            seen_edges.add(edge)
            side = component_tips(left, right)
            if side == references:
                split = (left, right)
                break
            if observed - side == references:
                split = (right, left)
                break
        if split:
            break
    if split is None:
        raise ValueError("declared reference tips do not form a separable clade")

    def orient(node: Node, parent: Node) -> Node:
        neighbours = [item for item in adjacency[node] if item is not parent]
        clone = Node(node.name if not neighbours else "", node.length)
        for neighbour in neighbours:
            child = orient(neighbour, node)
            child.parent = clone
            clone.children.append(child)
        return clone

    reference_side, focal_side = split
    new_root = Node()
    for node, parent in ((reference_side, focal_side), (focal_side, reference_side)):
        child = orient(node, parent)
        child.parent = new_root
        new_root.children.append(child)
    return new_root


def mrca(index: Mapping[str, Node], names: Iterable[str]) -> Node:
    wanted = list(dict.fromkeys(x for x in names if x))
    if not wanted:
        raise ValueError("MRCA requested for empty group")
    missing = sorted(set(wanted) - set(index))
    if missing:
        raise ValueError(f"MRCA tips absent from tree: {missing[:8]}")
    paths: list[list[Node]] = []
    sets: list[set[Node]] = []
    for name in wanted:
        cur: Node | None = index[name]; path = []
        while cur is not None:
            path.append(cur); cur = cur.parent
        paths.append(path); sets.append(set(path))
    for n in paths[0]:
        if all(n in s for s in sets[1:]):
            return n
    raise ValueError("MRCA not found")


def group_stats(index: Mapping[str, Node], group: set[str], focal: set[str]) -> dict[str, object]:
    if not group:
        return {"tip_count": 0, "monophyletic": False, "mrca_focal_tip_count": 0,
                "intruder_tip_count": 0, "intruder_tips": [], "focal_purity": 0.0}
    d = descendants(mrca(index, group)) & focal
    intruders = sorted(d - group)
    return {"tip_count": len(group), "monophyletic": d == group,
            "mrca_focal_tip_count": len(d), "intruder_tip_count": len(intruders),
            "intruder_tips": intruders,
            "focal_purity": round(len(group) / len(d), 6) if d else 0.0}


def neighbourhood(index: Mapping[str, Node], group: set[str], focal: set[str]) -> tuple[str, set[str]]:
    if not group:
        return "empty_group", set()
    n = mrca(index, group); d = descendants(n) & focal
    if d != group:
        return "mrca_intruders", d - group
    if n.parent is None:
        return "root_clade_no_sibling", set()
    out: set[str] = set()
    for c in n.parent.children:
        if c is not n:
            out.update(descendants(c) & focal)
    return "immediate_sibling_branch", out


def derive_main_labels(rows: Sequence[Mapping[str, str]]) -> tuple[set[str], list[str]]:
    req = {"paper_taxon_concept", "tree_codes"}
    if not req <= set(rows[0]):
        raise ValueError(f"Japan-38 audit missing columns {sorted(req - set(rows[0]))}")
    labels: set[str] = set(); excluded: list[str] = []
    for r in rows:
        codes = {x for x in clean(r["tree_codes"]).split("|") if x}
        if codes & EXCEPTIONS:
            excluded.append(clean(r["paper_taxon_concept"])); continue
        labels.update(codes)
    return labels, excluded


def join_metadata(manifest: Sequence[Mapping[str, str]], panel: Sequence[Mapping[str, str]]) -> dict[str, dict[str, str]]:
    mreq = {"tip_id", "panel_id", "source_study", "analysis_taxon_label"}
    preq = {"panel_id", "region", "location"}
    if not mreq <= set(manifest[0]):
        raise ValueError(f"manifest missing {sorted(mreq - set(manifest[0]))}")
    if not preq <= set(panel[0]):
        raise ValueError(f"source panel missing {sorted(preq - set(panel[0]))}")
    pmap = {r["panel_id"]: r for r in panel}
    if len(pmap) != len(panel): raise ValueError("duplicate source panel_id")
    out = {}
    for r in manifest:
        if r["panel_id"] not in pmap:
            raise ValueError(f"manifest panel_id missing from source panel: {r['panel_id']}")
        p = pmap[r["panel_id"]]; tip = r["tip_id"]
        if tip in out: raise ValueError(f"duplicate manifest tip {tip}")
        try:
            constituent_count = int(clean(r.get("constituent_tip_count")) or "1")
        except ValueError as error:
            raise ValueError(f"manifest tip {tip} has invalid constituent_tip_count") from error
        if constituent_count < 1:
            raise ValueError(f"manifest tip {tip} has non-positive constituent_tip_count")
        out[tip] = {"tip_id": tip, "panel_id": r["panel_id"],
                     "source_study": r["source_study"],
                     "analysis_taxon_label": r["analysis_taxon_label"],
                     "region": clean(p.get("region")), "location": clean(p.get("location")),
                     "name_review_required": clean(p.get("name_review_required") or
                                                   p.get("name_or_geography_review_required")).casefold(),
                     "constituent_tip_count": constituent_count}
    return out


def classify_arenicola(index: Mapping[str, Node], main: set[str], aren: set[str], focal: set[str]) -> str:
    if not main or not aren: return "insufficient_group_membership"
    mn = mrca(index, main); an = mrca(index, aren)
    md = descendants(mn) & focal; ad = descendants(an) & focal
    mm = md == main; am = ad == aren
    if not am: return "arenicola_nonmonophyletic"
    if not mm and aren <= md: return "arenicola_nested_within_published_main_radiation_mrca"
    if mm:
        if mn.parent is not None and mn.parent is an.parent:
            return "arenicola_immediate_sister_to_published_main_radiation"
        common = mrca(index, main | aren)
        if (descendants(common) & focal) == main | aren:
            return "arenicola_exclusive_sister_to_main_radiation"
        kind, sib = neighbourhood(index, aren, focal)
        if kind == "immediate_sibling_branch" and sib & main:
            return "arenicola_attached_to_subclade_of_main_radiation"
        return "arenicola_separate_from_published_main_radiation"
    return "unresolved_relative_to_nonmonophyletic_main_set"


def priority(focal_group: str, region: str) -> str:
    r = region.casefold(); ct = "china" in r or "taiwan" in r
    ne = any(k in r for k in ("russia", "mongol", "korea"))
    if focal_group in {"arenicola", "main_japanese_radiation"}:
        if ct: return "S"
        if ne: return "A"
    if focal_group in EXCEPTIONS:
        if ct: return "A"
        if ne: return "B"
    if "japan" in r: return "C"
    return "B"


def build_candidates(index: Mapping[str, Node], groups: Mapping[str, set[str]], focal: set[str],
                     meta: Mapping[str, Mapping[str, str]]) -> list[dict[str, str]]:
    agg: dict[tuple[str, str, str, str], list[str]] = defaultdict(list)
    for gname, gtips in groups.items():
        kind, ntips = neighbourhood(index, gtips, focal)
        for tip in sorted(ntips):
            m = meta[tip]
            key = (gname, kind, m["analysis_taxon_label"], m["region"])
            agg[key].append(tip)
    rows = []
    for (g, kind, taxon, region), tips in sorted(agg.items()):
        rows.append({"focal_group": g, "neighbourhood_kind": kind,
                      "candidate_taxon": taxon, "region": region,
                      "source_study": "|".join(sorted({
                          study
                          for tip in tips
                          for study in meta[tip]["source_study"].split("|")
                          if study
                      })),
                      "tip_count": str(len(tips)), "tip_ids": "|".join(sorted(tips)),
                      "name_review_required": str(any(
                          meta[tip]["name_review_required"] == "true" for tip in tips
                      )).lower(),
                      "sampling_priority_if_public_data_remain_unresolved": priority(g, region),
                     "interpretation_limit": "Topological neighbourhood only; not dispersal direction, direct ancestry or introgression."})
    return rows


def analyze(tree: Path, manifest: Path, source_panel: Path, japan38: Path,
            acceptance: Path | None = None, require_38: bool = True):
    mr = read_csv(manifest); pr = read_csv(source_panel); jr = read_csv(japan38)
    if require_38 and len(jr) != 38: raise ValueError(f"expected 38 Japan-38 rows, found {len(jr)}")
    accepted = False; acceptance_contract = ""; reference_tips: set[str] = set()
    tree_hash = hashlib.sha256(tree.read_bytes()).hexdigest()
    if acceptance:
        ac = json.loads(acceptance.read_text(encoding="utf-8"))
        if not ac.get("tree_artifact_accepted"):
            raise ValueError("tree has not passed artifact acceptance")
        if clean(ac.get("tree_sha256")) != tree_hash:
            raise ValueError("tree artifact acceptance SHA does not match interpreted tree")
        acceptance_contract = clean(ac.get("contract_version"))
        reference_tips = set(ac.get("reference_tips") or ac.get("required_reference_tips") or [])
        accepted = True
    root = NewickParser(tree.read_text(encoding="utf-8")).parse()
    if reference_tips:
        root = reroot_on_reference_clade(root, reference_tips)
    idx = tip_index(root)
    meta = join_metadata(mr, pr); focal = set(meta)
    missing = sorted(focal - set(idx))
    if missing: raise ValueError(f"manifest tips absent from tree: {missing[:8]}")
    main_labels, excluded = derive_main_labels(jr)
    main = {t for t,m in meta.items() if "Moreyra2025" in m["source_study"].split("|") and m["analysis_taxon_label"] in main_labels}
    main_clean = {t for t in main if meta[t]["name_review_required"] != "true"}
    brev = {t for t,m in meta.items() if m["analysis_taxon_label"] == "Cirsium brevicaule"}
    irum = {t for t,m in meta.items() if m["analysis_taxon_label"] == "Cirsium irumtiense"}
    aren = brev | irum
    dips = {t for t,m in meta.items() if m["analysis_taxon_label"] == "Cirsium dipsacolepis"}
    line = {t for t,m in meta.items() if m["analysis_taxon_label"] == "Cirsium lineare"}
    japan = {t for t,m in meta.items() if "japan" in m["region"].casefold()}
    individual_counts = {
        name: sum(meta[tip]["constituent_tip_count"] for tip in tips)
        for name, tips in {
            "Cirsium brevicaule": brev,
            "Cirsium irumtiense": irum,
        }.items()
    }
    if individual_counts["Cirsium brevicaule"] < 3 or individual_counts["Cirsium irumtiense"] < 3:
        raise ValueError("Arenicola public replication fell below 3+3")
    if not dips or not line: raise ValueError("published separate-invasion anchors missing")
    if len(main) < 20: raise ValueError(f"too few published main-radiation tips: {len(main)}")
    groups = {"main_japanese_radiation": main,
              "main_japanese_radiation_clean_name_subset": main_clean,
              "all_public_japan_region_tips": japan,
              "arenicola": aren, "Cirsium brevicaule": brev, "Cirsium irumtiense": irum,
              "Cirsium dipsacolepis": dips, "Cirsium lineare": line}
    stats = {g: group_stats(idx, tips, focal) for g,tips in groups.items()}
    for group_name, tips in groups.items():
        stats[group_name]["constituent_individual_count"] = sum(
            meta[tip]["constituent_tip_count"] for tip in tips
        )
    relation = classify_arenicola(idx, main, aren, focal)
    main_mrca_descendants = descendants(mrca(idx, main)) & focal
    exception_relationships = {}
    for name, tips in (("Cirsium dipsacolepis", dips), ("Cirsium lineare", line)):
        inside = tips & main_mrca_descendants
        if not inside:
            state = "outside_published_main_radiation_mrca"
        elif inside == tips:
            state = "inside_published_main_radiation_mrca"
        else:
            state = "partly_inside_published_main_radiation_mrca"
        exception_relationships[name] = state
    neigh = {}; cand_groups = {k:groups[k] for k in ("main_japanese_radiation","arenicola","Cirsium dipsacolepis","Cirsium lineare")}
    for g,tips in cand_groups.items():
        kind, ns = neighbourhood(idx, tips, focal)
        neigh[g] = {"neighbourhood_kind": kind, "tip_count": len(ns),
                    "taxa": dict(sorted(Counter(meta[t]["analysis_taxon_label"] for t in ns).items())),
                    "regions": dict(sorted(Counter(meta[t]["region"] for t in ns).items())),
                    "source_studies": dict(sorted(Counter(meta[t]["source_study"] for t in ns).items()))}
    candidates = build_candidates(idx, cand_groups, focal, meta)
    result = {"contract_version":"japan_origin_global_topology_interpretation_v2",
              "tree_sha256": tree_hash,
              "tree_artifact_acceptance_verified": accepted,
              "tree_artifact_acceptance_contract_version": acceptance_contract,
              "reference_tips_used_for_rooting": sorted(reference_tips),
              "focal_public_tip_count": len(focal), "tree_tip_count": len(idx),
              "focal_public_individual_count": sum(
                  item["constituent_tip_count"] for item in meta.values()
              ),
              "analysis_unit": (
                  "individual_tip" if all(item["constituent_tip_count"] == 1 for item in meta.values())
                  else "source_label_tip"
              ),
              "japan38_audit_rows": len(jr),
              "published_main_radiation_concept_count": len(jr)-len(excluded),
              "published_exception_concepts": excluded,
              "main_radiation_tree_code_count": len(main_labels),
              "group_statistics": stats,
              "arenicola_relative_to_main_radiation": relation,
              "published_exception_relationships": exception_relationships,
              "sibling_neighbourhoods": neigh,
              "dispersal_direction_inferred": False, "direct_ancestry_inferred": False,
              "introgression_inferred": False,
              "topology_based_sampling_shortlist_allowed": accepted,
              "new_china_sampling_freeze_allowed": False,
              "sampling_freeze_blockers":["compare BWA-primary and BLASTx mapping-sensitivity topologies",
                  "compare concatenated topology with gene-tree/coalescent sensitivity",
                  "review name-conflicted tips in focal sister neighbourhoods",
                  "only then convert stable public sister neighbourhoods into new continental sampling targets"],
              "candidate_row_count": len(candidates)}
    return result, candidates


def write_candidates(path: Path, rows: Sequence[Mapping[str,str]]):
    fields=["focal_group","neighbourhood_kind","candidate_taxon","region","source_study","tip_count","tip_ids","name_review_required","sampling_priority_if_public_data_remain_unresolved","interpretation_limit"]
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as h:
        w=csv.DictWriter(h,fieldnames=fields); w.writeheader(); w.writerows(rows)


def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument("--tree",type=Path,required=True); p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--source-panel",type=Path,required=True); p.add_argument("--japan38-audit",type=Path,default=Path("data/evidence/moreyra2025_japan_38_membership_audit_2026-08-10.csv"))
    p.add_argument("--tree-acceptance",type=Path); p.add_argument("--output",type=Path,required=True); p.add_argument("--candidates",type=Path,required=True); a=p.parse_args()
    result,candidates=analyze(a.tree,a.manifest,a.source_panel,a.japan38_audit,a.tree_acceptance,True)
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    write_candidates(a.candidates,candidates)
    print(f"arenicola_relative_to_main_radiation={result['arenicola_relative_to_main_radiation']}")
    print("main_radiation_monophyletic="+str(result["group_statistics"]["main_japanese_radiation"]["monophyletic"]).lower())
    print(f"candidate_rows={result['candidate_row_count']}"); print("new_china_sampling_freeze_allowed=false")
    return 0

if __name__ == "__main__": raise SystemExit(main())
