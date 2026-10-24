#!/usr/bin/env python3
"""Real Siniscalchi et al. (2023) North American Compositae1061 phylogeny × traits.

This is a *published, molecular-inferred, time-calibrated North American tree*
and the SAME AUTHORS' explicit trait + source environmental table, NOT a new
Moreyra worldwide nuclear tree. Keep published author coding and tip labels.

PINNED original source:
  https://github.com/carol-siniscalchi/cirsium/tree/c925d4af86160064448f794a9715f70b917a2786

Model-ready outputs are exploratory, not validated native-range/current-voucher
geographic history or a direct paleoclimate-on-branch effect.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

from Bio import Phylo

ORIGIN_REPO = "carol-siniscalchi/cirsium"
ORIGIN_SHA = "c925d4af86160064448f794a9715f70b917a2786"
ARTICLE = "https://doi.org/10.1086/724310"
OUTGROUP = "Cirsium_vulgare"
ASSETS = {
    "traits/traits.csv": "fa127f0587b676e6e004ea121424d26069586bcb",
    "traits/cirsium.trait.rec.R": "43a37f4b5d3d9d4b18364c5aaefea587b9c2edcc",
    "environmental/cirsium.phyluce95p.ultrametric.tre": "6417a38793427bc7c8562dc0e2cab59b74d8c316",
    "environmental/cirsium_environmental_allcombined_DR.csv": "6ca878423881db13f2af4624380bdce342afdf1b",
}
# The R script explicitly prints legends in numeric factor level order.
HEAD = {"0": "U", "1": "D"}
COLOUR = {
    "0": "red",
    "1": "reddish-purple",
    "2": "white/pink/purple COMBINED",
    "3": "yellow",
}
FLORA_MIXED_HEADS = {"Cirsium_eatonii", "Cirsium_joannae"}
TIP_FIELDS = [
    "tip_id", "accepted_taxon", "orientation_state", "bio15", "bio1",
    "biogeographic_region", "orientation_source", "climate_source", "exclusion_reason",
]


def git_blob_sha1(content: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()


def acquire(asset_dir: Path):
    files = {}
    for name, expected in ASSETS.items():
        target = asset_dir / name
        if target.exists() and git_blob_sha1(target.read_bytes()) == expected:
            files[name] = target
            continue
        url = f"https://raw.githubusercontent.com/{ORIGIN_REPO}/{ORIGIN_SHA}/{name}"
        last = None
        for attempt in range(3):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "EAzami-source-verified-Siniscalchi-phylogeny/1.0"})
                with urllib.request.urlopen(req, timeout=45) as handle:
                    raw = handle.read()
                if git_blob_sha1(raw) != expected:
                    raise ValueError("published-source Git blob changed: " + name)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
                files[name] = target
                break
            except (OSError, TimeoutError, urllib.error.HTTPError) as e:
                last = e
                time.sleep(attempt + 1)
        if name not in files:
            raise RuntimeError("failed to download authenticated author data: " + name) from last
    return files


def read_table(path: Path, key: str):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        d = csv.DictReader(handle)
        if not d.fieldnames or key not in d.fieldnames:
            raise ValueError("missing source taxon column")
        rows = list(d)
    if len(rows) != len({r[key] for r in rows}):
        raise ValueError("source data contain repeated taxon identifiers")
    if not rows:
        raise ValueError("empty source table")
    return {r[key]: r for r in rows}


def fitch(node, states, universe):
    if node.is_terminal():
        return {states.get(node.name, x) for x in universe} if node.name not in states else {states[node.name]}, 0
    children = [fitch(c, states, universe) for c in node.clades]
    current, n = children[0]
    for other, steps in children[1:]:
        n += steps
        intersection = current.intersection(other)
        if intersection:
            current = intersection
        else:
            current = current | other
            n += 1
    return current, n


def make_source_panels(outdir: Path, tree, traits, env):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    from matplotlib.lines import Line2D

    terminals = tree.get_terminals()
    max_len = max(tree.distance(x) for x in terminals)
    x_pos, y_pos = {}, {}
    for n in tree.find_clades():
        x_pos[n] = float(tree.distance(n))
    for i, tip in enumerate(terminals):
        y_pos[tip] = len(terminals) - i - 1
    def internal_y(n):
        if n in y_pos:
            return y_pos[n]
        children = [internal_y(c) for c in n.clades]
        y_pos[n] = sum(children) / len(children)
        return y_pos[n]
    internal_y(tree.root)

    figure_height = max(14, len(terminals) * .27)
    fig, ax = plt.subplots(figsize=(15, figure_height))
    fig.patch.set_facecolor("white")
    for n in tree.find_clades():
        if not n.clades:
            continue
        yy = [y_pos[c] for c in n.clades]
        ax.plot([x_pos[n], x_pos[n]], [min(yy), max(yy)], color="#7E8791", lw=.65)
        for c in n.clades:
            ax.plot([x_pos[n], x_pos[c]], [y_pos[c], y_pos[c]], color="#7E8791", lw=.65)

    annot_x = max_len + .20
    col_x = [annot_x + .00, annot_x + .24, annot_x + .50, annot_x + .77]
    head_palette = {"0": "#3D8DB8", "1": "#E18230"}
    color_palette = {"0": "#D44856", "1": "#9A4D98", "2": "#C5C1D2", "3": "#E2C344"}
    ridge_palette = {"0": "#E4E8EA", "1": "#5A856E"}
    bract_palette = {"0": "#D4D7DA", "1": "#697D92", "2": "#544E8D"}
    cols = ["Head U/D", "Corolla", "Sticky", "Outer bracts"]
    for x, label in zip(col_x, cols):
        ax.text(x + .095, len(terminals) + 1.2, label, rotation=45, ha="left", va="bottom", size=8)
    label_x = max_len + 1.08
    for tip in terminals:
        taxon = tip.name
        r = traits[taxon]
        y = y_pos[tip]
        cols = [
            head_palette[r["HeadPosition"]],
            color_palette[r["CorollaColor"]],
            ridge_palette[r["GlutinousRidge"]],
            bract_palette[r["OuterPhyllaryPosition"]],
        ]
        for x, color in zip(col_x, cols):
            ax.add_patch(Rectangle((x, y - .34), .18, .68, facecolor=color, edgecolor="white", linewidth=.4))
        ax.text(label_x, y, taxon.replace("_", " "), va="center", fontsize=6.5,
                color="#4D5660" if taxon not in FLORA_MIXED_HEADS else "#9A4D4D")

    ax.set_ylim(-1.3, len(terminals) + 3.8)
    ax.set_xlim(-.08, max_len + 5.4)
    ax.set_yticks([])
    ax.set_xlabel("Published calibrated root-to-tip branch lengths (source time scale, Ma)", fontsize=9)
    ax.set_title(
        "Published North American Cirsium nuclear phylogeny — original head, colour and bract states",
        fontsize=13, weight="semibold", loc="left", pad=26,
    )
    ax.text(.01, 1.008,
        "Siniscalchi et al. 2023  |  original 63-tip time-calibrated Compositae1061 tree  |  not the Moreyra global tree",
        transform=ax.transAxes, ha="left", fontsize=8, color="#67727A")
    legend = [
        Line2D([0], [0], marker="s", linestyle="None", markersize=8, markerfacecolor="#3D8DB8", markeredgecolor="white", label="Head U erect (0)"),
        Line2D([0], [0], marker="s", linestyle="None", markersize=8, markerfacecolor="#E18230", markeredgecolor="white", label="Head D pendent (1)"),
        Line2D([0], [0], marker="s", linestyle="None", markersize=8, markerfacecolor="#D44856", markeredgecolor="white", label="Corolla 0 red"),
        Line2D([0], [0], marker="s", linestyle="None", markersize=8, markerfacecolor="#9A4D98", markeredgecolor="white", label="Corolla 1 reddish-purple"),
        Line2D([0], [0], marker="s", linestyle="None", markersize=8, markerfacecolor="#C5C1D2", markeredgecolor="white", label="Corolla 2 white/pink/purple (mixed class)"),
        Line2D([0], [0], marker="s", linestyle="None", markersize=8, markerfacecolor="#E2C344", markeredgecolor="white", label="Corolla 3 yellow"),
        Line2D([0], [0], marker="s", linestyle="None", markersize=8, markerfacecolor="#5A856E", markeredgecolor="white", label="Glutinous ridge present"),
    ]
    ax.legend(handles=legend, frameon=False, loc="lower left", fontsize=8, ncol=3, bbox_to_anchor=(0, -0.12))
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(axis="x", alpha=.16)
    fig.subplots_adjust(bottom=.12, top=.92, left=.06, right=.98)
    fig.savefig(outdir / "independent_north_america_nuclear_trait_map.png", dpi=175, bbox_inches="tight")
    fig.savefig(outdir / "independent_north_america_nuclear_trait_map.svg", bbox_inches="tight")
    plt.close(fig)


def build(asset_dir: Path, outdir: Path, skip_figure: bool = False):
    files = acquire(asset_dir)
    tree = Phylo.read(io.StringIO(files["environmental/cirsium.phyluce95p.ultrametric.tre"].read_text(encoding="utf-8")), "newick")
    taxa = [x.name for x in tree.get_terminals()]
    if len(taxa) != 63 or len(set(taxa)) != 63 or OUTGROUP not in taxa:
        raise ValueError("original Siniscalchi tree must have exactly 63 unique tips including C. vulgare")
    traits = read_table(files["traits/traits.csv"], "Species")
    env = read_table(files["environmental/cirsium_environmental_allcombined_DR.csv"], "taxa")
    if set(taxa) != set(traits) or set(taxa) != set(env):
        raise ValueError("original published molecular tips ↔ full traits ↔ climate do not exactly join")
    script = files["traits/cirsium.trait.rec.R"].read_text(encoding="utf-8")
    # These are the ORIGINAL author's numeric-state-to-morphology legends.
    for fragment in ('"erect","pending"', '"red","reddish-purple", "white, pink, purple", "yellow"', "HeadPosition<-as.factor", "CorollaColor<-as.factor"):
        if fragment not in script:
            raise ValueError("published author trait ontology has changed: " + fragment)
    for t in taxa:
        r=traits[t]
        for trait,allowed in [
            ("HeadPosition", HEAD),("CorollaColor", COLOUR),
            ("GlutinousRidge", {"0":0,"1":1}),
            ("OuterPhyllaryPosition", {"0":0,"1":1,"2":2}),
        ]:
            if r[trait] not in allowed:
                raise ValueError("unapproved source code " + t + " " + trait)
        for axis in ("BIO1", "BIO15"):
            value = float(env[t][axis])
            if not math.isfinite(value):
                raise ValueError("invalid source environmental predictor")

    _, min_head = fitch(tree.root, {t: traits[t]["HeadPosition"] for t in taxa}, {"0", "1"})
    _, min_colour = fitch(tree.root, {t: traits[t]["CorollaColor"] for t in taxa}, set(COLOUR))
    if (min_head, min_colour) != (4, 12):
        raise ValueError("published nuclear-tree parsimony changed unexpectedly")
    counts = {a: dict(Counter(traits[t][a] for t in taxa)) for a in (
        "HeadPosition","CorollaColor","GlutinousRidge","OuterPhyllaryPosition"
    )}
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "siniscalchi_2023_north_american_nuclear_tree.nwk").write_text(
        files["environmental/cirsium.phyluce95p.ultrametric.tre"].read_text(encoding="utf-8").strip()+"\n",
        encoding="utf-8",
    )
    audits=[]
    for sensitivity in ("published_author_coding", "ambiguous_head_excluded"):
        rows = []
        for tip in taxa:
            if tip == OUTGROUP:
                continue
            source = traits[tip]
            unresolved = (sensitivity=="ambiguous_head_excluded" and tip in FLORA_MIXED_HEADS)
            rows.append({
                "tip_id": tip, "accepted_taxon": tip,  # Original source concept; NOT synonym-resolved.
                "orientation_state": "unresolved" if unresolved else HEAD[source["HeadPosition"]],
                "bio15": env[tip]["BIO15"], "bio1": env[tip]["BIO1"],
                "biogeographic_region": "North_America",
                "orientation_source": (f"{ARTICLE}; pinned author traits.csv at {ORIGIN_SHA}"),
                "climate_source": (f"{ARTICLE}; pinned author environmental CSV at {ORIGIN_SHA}"),
                "exclusion_reason": "FNA_explicit_erect_or_nodding_taxon_level" if unresolved else "",
            })
        if len(rows)!=62:
            raise ValueError("NA ingroup is not 62 published tree tips")
        dest=outdir / ("na_full_author_trait_climate_join.csv" if sensitivity=="published_author_coding" else "na_mixed_head_sensitivity_trait_climate_join.csv")
        with dest.open("w", encoding="utf-8", newline="") as h:
            w=csv.DictWriter(h,fieldnames=TIP_FIELDS)
            w.writeheader();w.writerows(rows)
        st=Counter(r["orientation_state"] for r in rows)
        audits.append({"case":sensitivity,"tips_in_metadata":len(rows),
                       "resolved_U":st.get("U",0),"resolved_D":st.get("D",0),
                       "explicit_unresolved":st.get("unresolved",0),
                       "tip_table":dest.name})
    with (outdir / "original_published_trait_states.csv").open("w", encoding="utf-8",newline="") as h:
        columns=["source_tip",*list(next(iter(traits.values())).keys())[1:]]
        w=csv.DictWriter(h,fieldnames=columns)
        w.writeheader()
        for tip in taxa:
            w.writerow({"source_tip":tip,**{k:traits[tip][k] for k in columns[1:]}})
    manifest={
        "contract_version":"independent_north_america_nuclear_multitrait_source_v1",
        "source":"Siniscalchi, Ackerfield & Folk 2023; https://doi.org/10.1086/724310",
        "upstream_repository":f"https://github.com/{ORIGIN_REPO}",
        "immutable_commit":ORIGIN_SHA,
        "authenticated_original_git_blobs":ASSETS,
        "tree_type":"published time-calibrated nuclear Compositae1061 phylogeny of North American Cirsium",
        "not":"Moreyra 2025 worldwide complete nuclear phylogeny",
        "total_published_tree_tips":len(taxa),
        "published_tree_outgroup":OUTGROUP,
        "ingroup_taxa_for_model":len(taxa)-1,
        "original_author_trait_counts":counts,
        "author_original_coding":{"HeadPosition":{"0":"U erect","1":"D pendent"},
                                  "CorollaColor":COLOUR},
        "Fitch_minimum_changes":{"HeadPosition":min_head,"CorollaColor":min_colour},
        "external_authoritative_head_polymorphism_veto_in_sensitivity":sorted(FLORA_MIXED_HEADS),
        "model_sensitivity_panels":audits,
        "environmental_data":"published source means BIO1 and BIO15, not EAzami GBIF/CHELSA new extraction",
        "same_sequenced_voucher_phenotyped":False,
        "chronogram_is_world_phylogeny":False,
        "claims_not_estimated":["historical paleoclimate on U/D transition branches",
            "ancestral pollinators or adaptive benefit","global all-genus U/D evolution"],
    }
    (outdir/"source_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if not skip_figure:
        make_source_panels(outdir,tree,traits,env)
    print(json.dumps({"n_tree_tips":len(taxa),"head_states":counts["HeadPosition"],
                      "color_states":counts["CorollaColor"],
                      "Fitch_minimum_changes":manifest["Fitch_minimum_changes"],
                      "sensitivity_panels":audits},indent=2))
    return manifest


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--asset-dir",type=Path,required=True)
    p.add_argument("--outdir",type=Path,required=True)
    p.add_argument("--skip-figure",action="store_true")
    a=p.parse_args()
    build(a.asset_dir,a.outdir,a.skip_figure)


if __name__=="__main__":
    main()
