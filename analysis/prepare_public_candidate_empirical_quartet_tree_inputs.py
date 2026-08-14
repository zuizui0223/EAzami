#!/usr/bin/env python3
"""Audit aligned quartet loci, select phylogenetically informative loci, and concatenate all common loci."""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

TIPS = ("MRY_YOSHINOI", "PUBEA001", "MRY_SAIRAMENSE", "PUBEA002")


def read_fasta(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}; name = None; seq: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line: continue
        if line.startswith(">"):
            if name is not None: out[name] = "".join(seq).upper()
            name = line[1:].split()[0]; seq = []
        else: seq.append(line)
    if name is not None: out[name] = "".join(seq).upper()
    if set(out) != set(TIPS):
        raise ValueError(f"{path}: expected exactly {TIPS}, observed {sorted(out)}")
    lengths = {len(x) for x in out.values()}
    if len(lengths) != 1: raise ValueError(f"ragged alignment: {path}")
    return out


def site_counts(seqs: dict[str, str]) -> tuple[int, int]:
    n = len(next(iter(seqs.values())))
    variable = 0; informative = 0
    for i in range(n):
        chars = [seqs[t][i] for t in TIPS]
        called = [c for c in chars if c in "ACGT"]
        if len(called) < 4: continue
        counts = Counter(called)
        if len(counts) > 1: variable += 1
        if sum(v >= 2 for v in counts.values()) >= 2: informative += 1
    return variable, informative


def prepare(common_loci: Path, alignment_dir: Path, outdir: Path) -> dict[str, object]:
    loci = [x.strip() for x in common_loci.read_text(encoding="utf-8").splitlines() if x.strip()]
    if len(loci) < 100 or len(loci) != len(set(loci)):
        raise ValueError("quartet tree inputs require >=100 unique common loci")
    concat = {tip: [] for tip in TIPS}; rows=[]; parts=[]; informative_loci=[]; start=1
    for locus in loci:
        path = alignment_dir / f"{locus}.aln.fasta"
        seqs = read_fasta(path)
        length = len(next(iter(seqs.values())))
        variable, informative = site_counts(seqs)
        if informative > 0: informative_loci.append(locus)
        rows.append({"locus":locus,"alignment_length":length,"variable_sites":variable,"parsimony_informative_sites":informative,"gene_tree_informative":informative>0})
        for tip in TIPS: concat[tip].append(seqs[tip])
        parts.append({"locus":locus,"start":start,"end":start+length-1}); start += length
    outdir.mkdir(parents=True, exist_ok=True)
    with (outdir/"concat.fasta").open("w",encoding="utf-8") as h:
        for tip in TIPS:
            seq="".join(concat[tip]); h.write(f">{tip}\n")
            for i in range(0,len(seq),80): h.write(seq[i:i+80]+"\n")
    with (outdir/"locus_information.csv").open("w",encoding="utf-8",newline="") as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    with (outdir/"partitions.csv").open("w",encoding="utf-8",newline="") as h:
        w=csv.DictWriter(h,fieldnames=["locus","start","end"]); w.writeheader(); w.writerows(parts)
    (outdir/"informative_loci.txt").write_text("".join(x+"\n" for x in informative_loci),encoding="utf-8")
    summary={
        "contract_version":"public_candidate_empirical_quartet_tree_inputs_v1",
        "four_way_common_strict_loci":len(loci),
        "gene_tree_informative_loci":len(informative_loci),
        "total_alignment_length":start-1,
        "total_variable_sites":sum(r["variable_sites"] for r in rows),
        "total_parsimony_informative_sites":sum(r["parsimony_informative_sites"] for r in rows),
        "concatenation_uses_all_common_loci":True,
        "gene_tree_subset_rule":"at least one fully-called 2+2 parsimony-informative site among the four tips",
        "full_294_tip_promotion_allowed_from_this_pilot":False,
    }
    (outdir/"tree_input_summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2)); return summary


def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("--common-loci",type=Path,required=True); p.add_argument("--alignment-dir",type=Path,required=True); p.add_argument("--outdir",type=Path,required=True); a=p.parse_args(); prepare(a.common_loci,a.alignment_dir,a.outdir); return 0

if __name__=="__main__": raise SystemExit(main())
