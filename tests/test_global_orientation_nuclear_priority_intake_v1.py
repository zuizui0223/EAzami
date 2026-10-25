"""Global U/D priority read-intake gate: source IDs, not reconstructed trees."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))

from build_global_orientation_nuclear_priority_intake_v1 import (  # noqa: E402
    build, classify_area,
)


class WorldwideU2DPriorityIntake(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary, cls.roster, cls.wave, cls.future = build()

    def test_no_public_biosample_or_run_dropped_from_source_roster(self):
        s=self.summary
        self.assertEqual(s["primary_full_nuclear_biosamples"],294)
        self.assertEqual(s["primary_unique_SRRs"],295)
        self.assertEqual(len(self.roster),294)
        self.assertEqual(len(self.future),294)
        self.assertEqual([x["full_jog_tip_id"] for x in self.roster],
                         [f"JOG{i:04d}" for i in range(1,295)])
        self.assertEqual(len({x["biosample"] for x in self.roster}),294)

    def test_real_frozen_strict_U_D_candidate_source_tips(self):
        s=self.summary
        self.assertEqual(s["priority_source_taxon_labels"],35)
        self.assertEqual((s["priority_U"],s["priority_D"]),(24,11))
        self.assertEqual(s["priority_biosamples"],46)
        focus=[r for r in self.wave if r["acquisition_tier"]=="priority_U_D_source"]
        self.assertEqual(len(focus),46)
        self.assertEqual(len({r["analysis_taxon_label"] for r in focus}),35)
        self.assertTrue(all(r["name_review_required"]=="false" for r in focus))
        self.assertTrue(all(r["orientation_candidate"] in {"U","D"} for r in focus))

    def test_background_is_trait_blind_and_not_called_a_transition(self):
        background=[r for r in self.wave if r["acquisition_tier"]=="trait_blind_geographic_anchor"]
        self.assertTrue(background)
        self.assertTrue(all(r["orientation_candidate"]=="" for r in background))
        self.assertTrue(all(r["name_review_required"]=="false" for r in background))
        self.assertEqual(len(background),self.summary["background_trait_blind_biosamples"])
        self.assertLess(len(self.wave),len(self.roster))
        self.assertEqual(len(self.wave),len({r["biosample"] for r in self.wave}))

    def test_broad_geography_uses_recorded_locality_not_morphology(self):
        self.assertEqual(classify_area("USA: Arizona","Outside_target_region"),"North_America")
        self.assertEqual(classify_area("Japan: Honshu","Japan"),"East_NE_Asia")
        self.assertEqual(classify_area("Spain: Huesca","Outside_target_region"),"West_Palearctic")
        self.assertEqual(classify_area("Unknown","Other_or_unresolved"),"Other_or_unresolved")

    def test_future_inference_input_is_explicitly_incomplete(self):
        self.assertFalse(self.summary["nuclear_tree_inferred"])
        self.assertFalse(self.summary["present_climate_ready"])
        self.assertFalse(self.summary["dated_tree_ready"])
        self.assertTrue(all(r["orientation_state_for_model"]=="unresolved" for r in self.future))
        self.assertTrue(all(not r["bio15"] and not r["bio1"] for r in self.future))
        self.assertTrue(all(not r["accepted_taxon"] for r in self.future))
        self.assertTrue(all(x["independent_phylogenetic_branch_confirmed"]=="false" for x in self.wave))

    def test_priority_sampling_appears_once_in_original_JOG_namespace(self):
        full_ids={x["full_jog_tip_id"] for x in self.roster}
        self.assertTrue({x["full_jog_tip_id"] for x in self.wave} <= full_ids)
        self.assertTrue(any(int(x["group_size_at_source_taxon_label"]) > 1 for x in self.wave))
        self.assertTrue(all(x["phenotype_same_voucher_confirmed"]=="false" for x in self.wave))


if __name__=="__main__":
    unittest.main()
