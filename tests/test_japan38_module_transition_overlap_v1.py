import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "jt",
    ROOT / "analysis/run_japan38_module_transition_overlap_v1.py",
)
assert SPEC and SPEC.loader
jt = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(jt)


class TestJapan38ModuleTransitionOverlap(unittest.TestCase):
    def build_fixture(self, root: Path):
        concept = root / "concept.csv"
        rows = []
        tips = []
        for i in range(1, 39):
            mid = f"JPN_{i:02d}"
            if mid == "JPN_20":
                ids = "S20a|S20b"
                tips.extend(["S20a", "S20b"])
            else:
                sid = f"S{i:02d}"
                ids = sid
                tips.append(sid)
            rows.append({"paper_japan_member_id": mid, "tip_ids": ids})
        with concept.open("w", newline="", encoding="utf-8") as h:
            w = csv.DictWriter(h, fieldnames=["paper_japan_member_id", "tip_ids"])
            w.writeheader()
            w.writerows(rows)

        # Force JPN20 to be an exclusive cherry, with all other biological tips
        # in a ladder. Branch lengths are positive and heterogeneous.
        other = [t for t in tips if t not in {"S20a", "S20b"}]
        subtree = "(S20a:0.01,S20b:0.01):0.02"
        for j, tip in enumerate(other, 1):
            subtree = f"({subtree},{tip}:{0.01 + 0.001*j:.4f}):0.01"
        tree = root / "tree.nwk"
        tree.write_text(f"({subtree},OUTGROUP_saff:0.5);\n", encoding="utf-8")

        trait = root / "traits.csv"
        fields = [
            "paper_japan_member_id",
            "orientation_state",
            "phyllary_posture",
            "stickiness_state",
        ]
        tr = [
            {
                "paper_japan_member_id": "JPN_01",
                "orientation_state": "upward_or_erect",
                "phyllary_posture": "appressed",
                "stickiness_state": "sticky",
            },
            {
                "paper_japan_member_id": "JPN_02",
                "orientation_state": "upward_or_erect",
                "phyllary_posture": "ascending",
                "stickiness_state": "sticky",
            },
            {
                "paper_japan_member_id": "JPN_03",
                "orientation_state": "downward_or_nodding",
                "phyllary_posture": "spreading",
                "stickiness_state": "nonsticky_or_nearly_nonsticky",
            },
            {
                "paper_japan_member_id": "JPN_04",
                "orientation_state": "downward_or_nodding",
                "phyllary_posture": "spreading_or_recurved",
                "stickiness_state": "nonsticky_or_nearly_nonsticky",
            },
            {
                "paper_japan_member_id": "JPN_20",
                "orientation_state": "downward_or_nodding",
                "phyllary_posture": "ascending_or_recurved",
                "stickiness_state": "sticky",
            },
        ]
        with trait.open("w", newline="", encoding="utf-8") as h:
            w = csv.DictWriter(h, fieldnames=fields)
            w.writeheader()
            w.writerows(tr)
        return tree, concept, trait

    @staticmethod
    def break_jpn20_cherry(tree_path: Path):
        txt = tree_path.read_text()
        txt = txt.replace(
            "(S20a:0.01,S20b:0.01):0.02",
            "(S20a:0.01,S01:0.011):0.02",
        )
        txt = txt.replace(",S01:0.0110", ",S20b:0.0110", 1)
        tree_path.write_text(txt)

    def test_fit_and_overlap_keep_missing_ambiguous(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            tree_path, concept_path, trait_path = self.build_fixture(root)
            cmap = jt.concept_map(concept_path)
            tree = jt.load_concept_tree(tree_path, cmap)
            self.assertEqual(len(tree.get_terminals()), 38)
            self.assertEqual({t.name for t in tree.get_terminals()}, set(cmap))
            states = jt.trait_states(trait_path)
            fits = {
                t: jt.fit_trait(tree, states[t], jt.STATE_UNIVERSE[t])
                for t in jt.STATE_UNIVERSE
            }
            self.assertEqual(fits["orientation"]["resolved_tips"], 5)
            self.assertEqual(fits["stickiness"]["resolved_tips"], 5)
            self.assertGreater(fits["orientation"]["q_equal_rates"], 0)
            self.assertTrue(
                any(e["informative"] for e in fits["orientation"]["edges"])
            )
            comp = jt.compare_traits(fits, seed=123, nperm=49)
            self.assertEqual(
                set(comp),
                {
                    "orientation__phyllary",
                    "orientation__stickiness",
                    "phyllary__stickiness",
                },
            )
            for row in comp.values():
                self.assertGreater(row["shared_informative_edges"], 0)
                p = row[
                    "branch_length_stratified_one_sided_p_for_positive_overlap"
                ]
                if p is not None:
                    self.assertGreaterEqual(p, 0)
                    self.assertLessEqual(p, 1)

    def test_edge_ids_are_unique_even_when_internal_labels_repeat(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            tree_path, concept_path, trait_path = self.build_fixture(root)
            cmap = jt.concept_map(concept_path)
            tree = jt.load_concept_tree(tree_path, cmap)
            # Reproduce the real IQ-TREE condition where support strings such as
            # 100/100 can be repeated on several internal nodes.
            for node in tree.get_nonterminals():
                node.name = "100/100"
            states = jt.trait_states(trait_path)
            fit = jt.fit_trait(
                tree, states["orientation"], jt.STATE_UNIVERSE["orientation"]
            )
            ids = [row["edge_id"] for row in fit["edges"]]
            self.assertEqual(len(ids), len(set(ids)))

    def test_nonmonophyletic_observed_jpn20_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            tree_path, concept_path, trait_path = self.build_fixture(root)
            self.break_jpn20_cherry(tree_path)
            cmap, allowed = jt.concept_info(concept_path)
            states = jt.trait_states(trait_path)
            with self.assertRaises(ValueError):
                jt.load_analysis_tree(tree_path, cmap, allowed, states)

    def test_nonmonophyletic_fully_unresolved_jpn20_is_pruned(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            tree_path, concept_path, trait_path = self.build_fixture(root)
            self.break_jpn20_cherry(tree_path)
            rows = list(csv.DictReader(trait_path.open(encoding="utf-8")))
            for row in rows:
                if row["paper_japan_member_id"] == "JPN_20":
                    row["orientation_state"] = "unknown"
                    row["phyllary_posture"] = "unknown"
                    row["stickiness_state"] = "unknown"
            with trait_path.open("w", newline="", encoding="utf-8") as h:
                w = csv.DictWriter(h, fieldnames=rows[0].keys())
                w.writeheader()
                w.writerows(rows)
            cmap, allowed = jt.concept_info(concept_path)
            states = jt.trait_states(trait_path)
            tree, diag = jt.load_analysis_tree(
                tree_path, cmap, allowed, states
            )
            self.assertFalse(diag["replicate_monophyly"])
            self.assertFalse(diag["replicate_resolved_for_any_trait"])
            self.assertEqual(
                diag["replicate_mode"],
                "pruned_fully_unresolved_replicated_concept",
            )
            self.assertEqual(len(tree.get_terminals()), 37)
            self.assertNotIn("JPN_20", {t.name for t in tree.get_terminals()})

    def test_strict_loader_still_rejects_nonmonophyletic_jpn20(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            tree_path, concept_path, _ = self.build_fixture(root)
            self.break_jpn20_cherry(tree_path)
            cmap = jt.concept_map(concept_path)
            with self.assertRaises(ValueError):
                jt.load_concept_tree(tree_path, cmap)


if __name__ == "__main__":
    unittest.main()
