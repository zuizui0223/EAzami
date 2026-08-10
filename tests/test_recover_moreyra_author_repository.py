#!/usr/bin/env python3
"""Offline tests for the Moreyra author-repository audit."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "analysis" / "recover_moreyra_author_repository.py"
SPEC = importlib.util.spec_from_file_location("recover_moreyra_author_repository", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
sys.modules["recover_moreyra_author_repository"] = mod
SPEC.loader.exec_module(mod)


class MoreyraAuthorRepositoryTests(unittest.TestCase):
    def test_hybpiper_summary(self) -> None:
        rows = [
            {
                "Name": "Cirsium-a_1",
                "GenesMapped": "1060",
                "GenesWithSeqs": "1000",
                "GenesAt50pct": "900",
                "GenesAt75pct": "800",
                "ParalogWarningsLong": "20",
                "ParalogWarningsDepth": "30",
                "GenesWithChimeraWarning": "0",
            },
            {
                "Name": "Cirsium-b_2",
                "GenesMapped": "1050",
                "GenesWithSeqs": "980",
                "GenesAt50pct": "850",
                "GenesAt75pct": "700",
                "ParalogWarningsLong": "40",
                "ParalogWarningsDepth": "50",
                "GenesWithChimeraWarning": "2",
            },
        ]
        summary = mod.summarize_hybpiper_stats(rows)
        self.assertEqual(summary["sample_rows"], 2)
        self.assertEqual(summary["genes_mapped_max"], 1060)
        self.assertEqual(summary["genes_with_sequences_median"], 990)
        self.assertEqual(summary["samples_with_any_chimera_warning"], 1)

    def test_seq_length_occupancy(self) -> None:
        rows = [
            {"Name": "Cirsium-a_1", "gene1": "100", "gene2": "", "gene3": "300"},
            {"Name": "Cirsium-b_2", "gene1": "120", "gene2": "200", "gene3": "0"},
        ]
        summary, loci = mod.summarize_seq_lengths(rows)
        self.assertEqual(summary["target_locus_columns"], 3)
        by_name = {row["locus"]: row for row in loci}
        self.assertEqual(by_name["gene1"]["occupancy"], 1.0)
        self.assertEqual(by_name["gene2"]["occupancy"], 0.5)
        self.assertEqual(by_name["gene3"]["occupancy"], 0.5)

    def test_unexpected_seq_length_layout_fails(self) -> None:
        with self.assertRaises(ValueError):
            mod.summarize_seq_lengths([{"Gene": "gene1", "sample1": "100"}])

    def test_minimal_xlsx_extraction(self) -> None:
        workbook_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
          xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
          <sheets><sheet name="Warnings" sheetId="1" r:id="rId1"/></sheets>
        </workbook>'''
        rels_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
          <Relationship Id="rId1" Target="worksheets/sheet1.xml"
            Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"/>
        </Relationships>'''
        shared_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="2" uniqueCount="2">
          <si><t>Gene</t></si><si><t>gene1</t></si>
        </sst>'''
        sheet_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
          <sheetData>
            <row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="inlineStr"><is><t>Warnings</t></is></c></row>
            <row r="2"><c r="A2" t="s"><v>1</v></c><c r="B2"><v>3</v></c></row>
          </sheetData>
        </worksheet>'''
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.xlsx"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("xl/workbook.xml", workbook_xml)
                archive.writestr("xl/_rels/workbook.xml.rels", rels_xml)
                archive.writestr("xl/sharedStrings.xml", shared_xml)
                archive.writestr("xl/worksheets/sheet1.xml", sheet_xml)
            metadata, matrices = mod.extract_xlsx(path, Path(tmp) / "out")
            self.assertEqual(len(metadata), 1)
            self.assertEqual(metadata[0]["sheet_name"], "Warnings")
            self.assertEqual(matrices["Warnings"], [["Gene", "Warnings"], ["gene1", "3"]])

    def test_column_index(self) -> None:
        self.assertEqual(mod.column_index("A1"), 0)
        self.assertEqual(mod.column_index("Z1"), 25)
        self.assertEqual(mod.column_index("AA1"), 26)


if __name__ == "__main__":
    unittest.main()
