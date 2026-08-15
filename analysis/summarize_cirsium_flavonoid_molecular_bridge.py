#!/usr/bin/env python3
"""Summarize source-typed molecular coverage relevant to HMM1/HMM5.

The output measures published targeted-panel coverage. A family that is not
reported/targeted is never interpreted as absent from a genome/transcriptome.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

PANEL = {
    "entry": {"PAL", "C4H", "4CL"},
    "flavonoid_core": {"CHS", "CHI", "F3H", "F3'H"},
    "branch_competition": {"FLS", "FSII"},
    "anthocyanin_committed": {"DFR"},
    "anthocyanin_terminal": {"ANS", "UFGT"},
    "regulatory": {"MYB", "bHLH", "WD40"},
    "transport": {"GST", "MATE"},
}
DIRECT = {"reported_directly"}


def read_rows(path: str):
    with Path(path).open(encoding="utf-8-sig", newline="") as h:
        return list(csv.DictReader(h))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/evidence/cirsium_flavonoid_molecular_bridge_v1.csv")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    rows = read_rows(args.input)
    sources = sorted({r["source_id"] for r in rows})
    expected = sum(len(v) for v in PANEL.values())
    if expected != 17:
        raise AssertionError(expected)
    for src in sources:
        fams = {r["gene_family"] for r in rows if r["source_id"] == src}
        if fams != set().union(*PANEL.values()):
            raise ValueError(f"{src} does not cover the frozen 17-family audit panel")

    source_summary = {}
    for src in sources:
        rr = [r for r in rows if r["source_id"] == src]
        direct = {r["gene_family"] for r in rr if r["evidence_status"] in DIRECT}
        by_module = {}
        for module, fams in PANEL.items():
            d = sorted(fams & direct)
            by_module[module] = {
                "families_total": len(fams),
                "directly_reported": len(d),
                "directly_reported_families": d,
                "direct_fraction": len(d) / len(fams),
            }
        source_summary[src] = {
            "rows": len(rr),
            "directly_reported_families": len(direct),
            "panel_families": expected,
            "direct_fraction": len(direct) / expected,
            "by_module": by_module,
            "status_counts": dict(sorted(Counter(r["evidence_status"] for r in rr).items())),
        }

    any_direct = {
        r["gene_family"]
        for r in rows
        if r["evidence_status"] in DIRECT
    }
    any_by_module = {}
    for module, fams in PANEL.items():
        d = sorted(fams & any_direct)
        any_by_module[module] = {
            "families_total": len(fams),
            "directly_reported_in_at_least_one_source": len(d),
            "directly_reported_families": d,
            "direct_fraction": len(d) / len(fams),
        }

    upstream = PANEL["entry"] | PANEL["flavonoid_core"] | PANEL["branch_competition"]
    color_specific_bridge = PANEL["anthocyanin_committed"] | PANEL["anthocyanin_terminal"] | PANEL["regulatory"] | PANEL["transport"]
    terminal_reg_transport = PANEL["anthocyanin_terminal"] | PANEL["regulatory"] | PANEL["transport"]

    result = {
        "contract_version": "cirsium_flavonoid_molecular_bridge_v1",
        "source_count": len(sources),
        "sources": sources,
        "audit_panel_families": expected,
        "source_summaries": source_summary,
        "cross_source_coverage": {
            "directly_reported_in_at_least_one_source": len(any_direct),
            "direct_fraction": len(any_direct) / expected,
            "by_module": any_by_module,
        },
        "micro_to_macro_gap": {
            "upstream_core_branch_families": len(upstream),
            "upstream_core_branch_directly_reported": len(upstream & any_direct),
            "upstream_core_branch_fraction": len(upstream & any_direct) / len(upstream),
            "anthocyanin_plus_regulatory_transport_families": len(color_specific_bridge),
            "anthocyanin_plus_regulatory_transport_directly_reported": len(color_specific_bridge & any_direct),
            "anthocyanin_plus_regulatory_transport_fraction": len(color_specific_bridge & any_direct) / len(color_specific_bridge),
            "terminal_regulatory_transport_families": len(terminal_reg_transport),
            "terminal_regulatory_transport_directly_reported": len(terminal_reg_transport & any_direct),
            "terminal_regulatory_transport_fraction": len(terminal_reg_transport & any_direct) / len(terminal_reg_transport),
            "interpretation": "Published Cirsium molecular studies directly anchor the entry/flavonoid-core/branch machinery and DFR, but their named targeted panels do not yet give comparable direct coverage of ANS/UFGT, MBW regulators, or anthocyanin transport. This is an assay/panel-resolution gap, not evidence that these genes are absent.",
        },
        "published_expression_anchors": {
            "PARK2020": {
                "orthologs_in_named_phenylpropanoid_panel": 29,
                "flavonoid_gene_flower_vs_leaf_range_fold": [2.6, 500.0],
                "examples": {
                    "CjCHS1_flower_vs_leaf": 500.0,
                    "CjCHS2_flower_vs_leaf": 112.0,
                    "CjF3Hprime_flower_vs_leaf": 16.6,
                    "CjCHI_flower_vs_leaf": 13.0,
                    "CjFLS_flower_vs_leaf": 5.6,
                    "CjFSII_flower_vs_leaf": 3.3,
                    "CjDFR_isoform_root_vs_leaf": [22.0, 2.6],
                },
            },
            "ROY2018": {
                "assembled_unigenes": 51133,
                "direct_panel_scope": "taxifolin/coniferyl/silymarin precursor enzymes",
            },
        },
        "EAzami_problem": {
            "id": "P_MICRO_MACRO_07_terminal_regulatory_resolution_gap",
            "result": "The directly documented Cirsium molecular evidence is much denser for upstream/core flavonoid machinery than for the terminal anthocyanin + MBW + transport layers most diagnostic of reversible white/coloured switching.",
            "why_problem": "A pathway can be demonstrably present and flower-biased while the evolutionary switch remains unresolved because the decisive terminal/regulatory layer is not comparably assayed across colour lineages.",
            "linked_hypotheses": ["HMM1", "HMM5"],
        },
        "existing_data_next_test": {
            "priority_1": ["ANS", "UFGT", "MYB", "bHLH", "WD40", "GST", "MATE"],
            "priority_2": ["DFR"],
            "priority_3_control": sorted(upstream),
            "action": "Mine the full published transcriptome/annotation resources and current public East-Asian RNA/genome data for ortholog presence, copy number, coding variation and gene trees; preserve tissue-specific non-expression as missing/assay-limited rather than deletion.",
        },
        "claim_boundary": "This synthesis describes coverage of named/reviewed molecular evidence panels. 'Not targeted' or 'not reported' never means genomic absence. Existing C. japonicum tissue-expression data do not establish the historical cause of white/coloured evolution in takaoense, Arenicola, or other lineages.",
    }

    Path(args.output).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
