from __future__ import annotations

import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/'analysis/validate_fixed_white_public_nuclear_recovery_audit.py'
spec=importlib.util.spec_from_file_location('fwpub',MOD);assert spec and spec.loader
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
FIELDS=['candidate_id','taxon','search_route','query_or_identifier','result_status','evidence_source','evidence_locator','implication','next_action','claim_limit']

class FixedWhitePublicAuditTests(unittest.TestCase):
    def fixture(self,root:Path,*,bad_status:bool=False):
        p=root/'audit.csv'
        rows=[
            ['WREC01','Cirsium boninense','conference','title','existing_genetic_study_identified','J-GLOBAL','x','study exists','recover data','not a tip'],
            ['WREC01','Cirsium boninense','lab list','title','study_metadata_independently_corrobated','lab','x','confirmed','recover data','not a tip'],
            ['WREC01','Cirsium boninense','proceedings','RA241-R8 p69','proceedings_copy_route_identified','NDL','x','source route','read p69','catalogue only'],
            ['WREC01','Cirsium boninense','index','Iriomote','iriomote_indexing_clue_identified','J-GLOBAL','x','index clue','verify abstract','not sequencing evidence'],
            ['WREC01','Cirsium boninense','PAFTOL current','taxon','paftol_current_release_exact_taxon_absent','Kew','x','no exact current sample','focus study','current release only'],
            ['WREC01','Cirsium boninense','PAFTOL deleted','taxon','paftol_current_deleted_exact_taxon_absent','Kew','x','no exact deleted entry','focus study','not all history'],
            ['WREC01','Cirsium boninense','archive','taxon','no_exact_indexed_plant_asset_recovered','NCBI/DDBJ','x','no recovery','recover study','not absence proof'],
            ['WREC01','Cirsium boninense','followup','title/authors','no_followup_publication_or_thesis_recovered','bounded search','x','no recovery','recover p69','not absence proof'],
            ['WREC02','Cirsium wulongense','voucher','XLS21-095','voucher_anchor_recovered','paper','x','anchor','search data','not DNA'],
            ['WREC02','Cirsium wulongense','voucher','XLS21-093','additional_voucher_anchor_recovered','paper','x','anchor','search data','not DNA'],
            ['WREC02','Cirsium wulongense','paper methods','morphology','published_taxonomic_study_morphology_only_no_molecular_data','paper','x','no molecular analysis in paper','continue public routes','not proof of no separate data'],
            ['WREC02','Cirsium wulongense','specimen index','vouchers','no_public_digitized_voucher_record_recovered','CVH/IBSC','x','no indexed digitized record','retain anchors','not specimen absence'],
            ['WREC02','Cirsium wulongense','image locality','PPBC','secondary_locality_image_evidence_identified','paper/PPBC','x','second locality','future sampling lead','not a nuclear sample'],
            ['WREC02','Cirsium wulongense','archive','taxon','nuclear_tip_ready' if bad_status else 'no_exact_indexed_asset_recovered','NCBI/DDBJ','x','no recovery','public search/new sampling','not absence proof'],
        ]
        with p.open('w',newline='',encoding='utf-8') as h:
            w=csv.writer(h);w.writerow(FIELDS);w.writerows(rows)
        return p

    def test_current_discovery_states_do_not_promote_tip(self):
        with tempfile.TemporaryDirectory() as td:
            out=m.validate(self.fixture(Path(td)))
            self.assertFalse(out['usable_nuclear_tip_recovered'])
            self.assertFalse(out['rate_fit_tip_promotion_allowed'])
            self.assertFalse(out['boninense_paftol_current_release_exact_taxon_present'])
            self.assertFalse(out['boninense_existing_2025_genetic_study_data_recovered'])
            self.assertFalse(out['wulongense_published_study_contains_molecular_analysis'])
            self.assertFalse(out['wulongense_public_digitized_exact_voucher_recovered'])
            self.assertEqual(out['evidence_rows'],14)
            self.assertEqual(out['contract_version'],'fixed_white_public_nuclear_recovery_audit_v3')

    def test_rejects_ready_status_in_discovery_audit(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,'unsupported result_status'):
                m.validate(self.fixture(Path(td),bad_status=True))

if __name__=='__main__':unittest.main()
