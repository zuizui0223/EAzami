from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/'analysis/build_japan_origin_max_public_panel.py'
spec=importlib.util.spec_from_file_location('jomp',MOD);assert spec and spec.loader
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)


def mrow(tree,bio,run,region,*,relation='exact',priority='low',geo='concordant',scope='core_east_asia'):
    return {
        'tree_code':tree,'biosample':bio,'run':run,'region_class':region,
        'scope_class':scope,'sra_link_status':'linked_runinfo',
        'geographic_evidence_relation':geo,'name_reconciliation_priority':priority,
        'published_species':tree,'voucher_and_herbarium':f'voucher {bio}',
        'sra_scientific_name':tree,'geographic_location':region,
        'experiment':run.replace('SRR','SRX'),'tree_code_vs_sra_name':relation,
    }


def c25(taxon,i,loc,voucher):
    return {'taxon':taxon,'sample_index':str(i),'collecting_location':loc,'voucher':voucher,'bioproject':'PRJNA1158676'}


def c26(taxon,i,loc,voucher,accession=''):
    return {'taxon':taxon,'sample_number_within_taxon':str(i),'location':loc,'voucher':voucher,
            'herbarium':'TCF','embedded_public_accession':accession,'bioproject':'PRJNA1311153'}


class JapanOriginMaxPublicPanelTests(unittest.TestCase):
    def fixture(self):
        more=[
            mrow('Cirsium domonii','SAMN1','SRR1','Japan'),
            mrow('Cirsium dipsacolepis','SAMN2','SRR2','Japan'),
            mrow('Cirsium lineare','SAMN3','SRR3','Japan'),
            mrow('Cirsium fanjingshanense','SAMN4','SRR4','China'),
            mrow('Cirsium pendulum','SAMN5','SRR5','Russian_Inner_NE_Asia',scope='northeast_asia_bridge'),
            mrow('Cirsium abukumense','SAMN6','SRR6','Japan'),
            mrow('Cirsium abukumense','SAMN6','SRR7','Japan'),
            mrow('Cirsium yuki-uenoanum','SAMN7','SRR8','Japan|Outside_target_region',
                 relation='different_submitted_or_published_name',priority='high',
                 geo='conflicting_resolved_regions',scope='source_conflict_target_vs_outside'),
        ]
        ch25=[c25('Cirsium kujuense',1,'JAPAN. Oita','ccy25')]
        ch26=[]
        for i,v in enumerate(('ccyB1','ccyB2','ccyB3'),1): ch26.append(c26('C. brevicaule',i,'JAPAN. Okinawa',v))
        for i,v in enumerate(('ccyI1','ccyI2','ccyI3'),1): ch26.append(c26('C. irumtiense',i,'JAPAN. Okinawa',v))
        ch26.append(c26('C. morii',1,'TAIWAN. Hualien','ccyM', 'SRR999'))
        return more,ch25,ch26

    def test_groups_biosamples_and_excludes_geography_conflict(self):
        more,ch25,ch26=self.fixture()
        mrows,ex=m.build_moreyra(more)
        ab=[r for r in mrows if r['analysis_taxon_label']=='Cirsium abukumense']
        self.assertEqual(len(ab),1)
        self.assertEqual(ab[0]['run_accessions'],'SRR6|SRR7')
        self.assertEqual(len(ex),1)
        self.assertEqual(ex[0]['analysis_taxon_label'],'Cirsium yuki-uenoanum')
        panel=mrows+m.build_chang2025(ch25)+m.build_chang2026(ch26)
        summary=m.validate_panel(panel,ex)
        self.assertFalse(summary['japan_all_taxa_monophyly_claim_allowed'])
        self.assertFalse(summary['joint_common_locus_tree_executed'])
        self.assertFalse(summary['new_china_sampling_freeze_allowed'])
        self.assertEqual(summary['ryukyu_public_replicates']['Cirsium brevicaule'],3)
        self.assertEqual(summary['ryukyu_public_replicates']['Cirsium irumtiense'],3)

    def test_retains_name_conflicts_without_silent_relabelling(self):
        row=mrow('Cirsium coryletorum','SAMN8','SRR9','Russian_Far_East',
                 relation='different_submitted_or_published_name',priority='high',
                 scope='northeast_asia_bridge')
        panel,ex=m.build_moreyra([row])
        self.assertEqual(ex,[])
        self.assertEqual(panel[0]['analysis_taxon_label'],'Cirsium coryletorum')
        self.assertEqual(panel[0]['name_or_geography_review_required'],'true')
        self.assertEqual(panel[0]['automatic_use'],'true')

    def test_chang_accession_states_are_not_invented(self):
        rows=[c26('C. brevicaule',1,'JAPAN. Amami','ccy1'),
              c26('C. lineare',1,'TAIWAN. Miaoli','ccy2','SRR123')]
        out=m.build_chang2026(rows)
        self.assertEqual(out[0]['run_resolution_state'],'bioproject_public_run_join_required')
        self.assertEqual(out[0]['run_accessions'],'')
        self.assertEqual(out[1]['run_resolution_state'],'embedded_public_identifier_present')
        self.assertEqual(out[1]['run_accessions'],'SRR123')

if __name__=='__main__': unittest.main()
