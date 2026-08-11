import csv
import gzip
import importlib.util
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "analysis" / "build_read2tree_oma_static_marker_pack.py"
SPEC = importlib.util.spec_from_file_location("oma_static", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
sys.modules["oma_static"] = mod
SPEC.loader.exec_module(mod)


def fake_record(omaid: str, aa_len: int = 10):
    aa = "M" + "A" * (aa_len - 1)
    dna = "ATG" + "GCT" * (aa_len - 1)
    return {"omaid": omaid, "sequence": aa, "cdna": dna}


class StaticMarkerTests(unittest.TestCase):
    def test_parse_group_line_requires_exact_three_refs(self):
        line = "123 CYNCS00001 HELAN00002 DAUCS00003 HUMAN00004"
        group = mod.parse_group_line(line, 7)
        self.assertIsNotNone(group)
        self.assertEqual(group.ref_ids, ("CYNCS00001", "HELAN00002", "DAUCS00003"))
        self.assertEqual(group.total_members, 4)
        self.assertIsNone(
            mod.parse_group_line(
                "CYNCS00001 CYNCS00002 HELAN00002 DAUCS00003", 8
            )
        )
        self.assertIsNone(mod.parse_group_line("CYNCS00001 HELAN00002", 9))

    def test_select_groups_prefers_broader_group_membership(self):
        groups = [
            mod.parse_group_line("CYNCS00001 HELAN00001 DAUCS00001", 1),
            mod.parse_group_line(
                "CYNCS00002 HELAN00002 DAUCS00002 HUMAN00001 RATNO00001", 2
            ),
            mod.parse_group_line(
                "CYNCS00003 HELAN00003 DAUCS00003 HUMAN00002", 3
            ),
        ]
        selected = mod.select_groups([g for g in groups if g], target_count=2)
        self.assertEqual(selected[0].source_line_number, 2)
        self.assertEqual(selected[1].source_line_number, 3)

    def test_validate_api_release(self):
        self.assertEqual(
            mod.validate_api_release(
                {"api_version": "1.7", "oma_release": "All.May2026"}
            ),
            "May2026",
        )
        with self.assertRaisesRegex(ValueError, "does not report pinned"):
            mod.validate_api_release({"oma_release": "All.Jul2027"})

    def test_parse_bulk_api17_tuple_response(self):
        ids = ["CYNCS00001", "HELAN00001"]
        payload = [
            ["CYNCS00001", fake_record("CYNCS00001")],
            ["HELAN00001", fake_record("HELAN00001")],
        ]
        parsed = mod.parse_bulk_response(ids, payload)
        self.assertEqual(parsed["CYNCS00001"]["_query_omaid"], "CYNCS00001")

    def test_parse_bulk_direct_dict_response(self):
        ids = ["CYNCS00001", "HELAN00001"]
        payload = {omaid: fake_record(omaid) for omaid in ids}
        parsed = mod.parse_bulk_response(ids, payload)
        self.assertEqual(set(parsed), set(ids))

    def test_sequence_pair_rejects_frame_mismatch(self):
        good = fake_record("CYNCS00001")
        good["_query_omaid"] = "CYNCS00001"
        aa, dna = mod.sequence_pair(good)
        self.assertEqual(len(dna), 3 * len(aa))
        bad = dict(good)
        bad["cdna"] += "A"
        with self.assertRaisesRegex(ValueError, "not divisible by 3"):
            mod.sequence_pair(bad)

    def test_end_to_end_static_pack_with_injected_api(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            group_file = root / "groups.txt.gz"
            lines = [
                "CYNCS00001 HELAN00001 DAUCS00001 HUMAN00001 RATNO00001",
                "CYNCS00002 HELAN00002 DAUCS00002 HUMAN00002",
                "CYNCS00003 HELAN00003 DAUCS00003",
                "CYNCS00004 HELAN00004 HUMAN00004",
            ]
            with gzip.open(group_file, "wt", encoding="utf-8") as handle:
                handle.write("\n".join(lines) + "\n")

            manifest = root / "refs.csv"
            with manifest.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=[
                        "oma_release", "oma_code", "scientific_name", "ncbi_taxid",
                        "reference_role", "verified_in_oma", "verification_url",
                    ],
                )
                writer.writeheader()
                for code, taxid in [
                    ("CYNCS", "59894"),
                    ("HELAN", "4232"),
                    ("DAUCS", "4039"),
                ]:
                    writer.writerow(
                        {
                            "oma_release": "May2026",
                            "oma_code": code,
                            "scientific_name": code,
                            "ncbi_taxid": taxid,
                            "reference_role": "test",
                            "verified_in_oma": "true",
                            "verification_url": "https://example.invalid",
                        }
                    )

            all_ids = [
                f"{code}{i:05d}"
                for i in (1, 2, 3)
                for code in ("CYNCS", "HELAN", "DAUCS")
            ]
            records = {omaid: fake_record(omaid) for omaid in all_ids}

            contract = mod.build_static_pack(
                group_file=group_file,
                reference_manifest=manifest,
                outdir=root / "out",
                target_count=2,
                expected_group_md5=mod.md5_file(group_file),
                api_version_payload={"database_release": "All.May2026"},
                protein_fetcher=lambda ids: {
                    omaid: records[omaid] for omaid in ids
                },
            )
            self.assertEqual(
                contract["profile_id"],
                "oma_may2026_static_broadconservation400_v1",
            )
            self.assertEqual(contract["selection_method"]["target_marker_count"], 2)
            self.assertEqual(contract["api"]["selected_protein_records"], 6)
            self.assertFalse(
                contract["selection_method"]["browser_export_equivalent"]
            )
            export = root / "out" / "oma_static_broadconservation_marker_export.tar.gz"
            self.assertTrue(export.exists())
            with tarfile.open(export, "r:gz") as tar:
                names = sorted(
                    member.name for member in tar.getmembers() if member.isfile()
                )
            self.assertEqual(len(names), 4)
            self.assertTrue(all(name.endswith((".fa", ".fna")) for name in names))
            with (root / "out" / "static_marker_selection.csv").open() as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(int(rows[0]["total_group_members"]), 5)
            self.assertEqual(int(rows[1]["total_group_members"]), 4)

    def test_selection_fingerprint_deterministic_across_member_order(self):
        a = mod.parse_group_line(
            "CYNCS00001 HELAN00001 DAUCS00001 HUMAN00001", 1
        )
        b = mod.parse_group_line(
            "HUMAN00001 DAUCS00001 CYNCS00001 HELAN00001", 2
        )
        self.assertEqual(a.fingerprint, b.fingerprint)
        self.assertEqual(a.member_sha256, b.member_sha256)

    def test_tarball_is_byte_reproducible(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            groups = [
                mod.parse_group_line(
                    "CYNCS00001 HELAN00001 DAUCS00001 HUMAN00001", 1
                )
            ]
            records = {
                omaid: fake_record(omaid)
                for omaid in ("CYNCS00001", "HELAN00001", "DAUCS00001")
            }
            a = root / "a.tar.gz"
            b = root / "b.tar.gz"
            mod.build_export_tarball(groups, records, output_tarball=a)
            mod.build_export_tarball(groups, records, output_tarball=b)
            self.assertEqual(mod.sha256_file(a), mod.sha256_file(b))


if __name__ == "__main__":
    unittest.main()
