from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "sampling/JAPAN_WIDE_PHYLOGENY_ORIENTATION_ADDITION_PANEL_V1.csv"


def load_rows():
    with PANEL.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_panel_has_unique_taxa_and_required_fields():
    rows = load_rows()
    taxa = [r["taxon"] for r in rows]
    assert len(rows) >= 25
    assert len(taxa) == len(set(taxa))
    for row in rows:
        assert row["priority"] in {"P0", "P1", "P2", "CORE"}
        assert row["region_or_stratum"]
        assert row["current_nuclear_status"]
        assert row["primary_reason"]
        assert row["backbone_target_capture_minimum"]
        assert row["cytotype_priority"] == "high"


def test_northern_gap_panel_is_protected():
    by_taxon = {r["taxon"]: r for r in load_rows()}
    required = {
        "Cirsium boreale",
        "Cirsium albrechtii",
        "Cirsium grayanum",
        "Cirsium yezoalpinum",
        "Cirsium umezawanum",
        "Cirsium kenji-horieanum",
        "Cirsium teshioense",
        "Cirsium austrohidakaense",
        "Cirsium iito-kojianum",
        "Cirsium chikabumiense",
    }
    assert required <= set(by_taxon)
    assert all(by_taxon[t]["priority"] == "P0" for t in required)
    states = {by_taxon[t]["nmns_orientation"] for t in required}
    assert "upward_or_erect" in states
    assert "downward_or_nodding" in states


def test_origin_falsifiers_and_identity_repairs_are_p0():
    by_taxon = {r["taxon"]: r for r in load_rows()}
    for taxon in (
        "Cirsium lineare",
        "Cirsium dipsacolepis",
        "Cirsium yuki-uenoanum",
        "Cirsium effusum",
    ):
        assert by_taxon[taxon]["priority"] == "P0"


def test_island_extremes_are_present():
    taxa = {r["taxon"] for r in load_rows()}
    assert {
        "Cirsium hachijoense",
        "Cirsium boninense",
        "Cirsium yakushimense",
        "Cirsium spinosum",
    } <= taxa


def test_core190_taxa_are_not_replaced_by_broad_panel():
    by_taxon = {r["taxon"]: r for r in load_rows()}
    for taxon in (
        "Cirsium brevicaule",
        "Cirsium irumtiense",
        "Cirsium pendulum",
        "Cirsium sieboldii",
    ):
        # Priority, not note wording, is the contract: the Japan-wide breadth
        # panel may reuse representatives but must never demote or replace the
        # protected population-replicated core.
        assert by_taxon[taxon]["priority"] == "CORE"


def test_species_backbone_is_not_defined_as_radseq_everywhere():
    rows = [r for r in load_rows() if r["priority"] in {"P0", "P1"}]
    # The common species backbone must remain target-capture/common-locus based;
    # population RADseq is selective, not mandatory for every taxon.
    assert all(r["backbone_target_capture_minimum"] for r in rows)
    assert sum(r["population_RADseq_role"].startswith("yes_") or "high_priority" in r["population_RADseq_role"] for r in rows) < len(rows) / 2
