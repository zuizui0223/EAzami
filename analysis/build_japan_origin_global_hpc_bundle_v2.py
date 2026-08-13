#!/usr/bin/env python3
"""Build the deduplicated 294-tip/295-SRR public nuclear-tree HPC bundle.

This v2 wrapper reuses the already-validated shell primitives from the v1 bundle,
but replaces the duplicated 302-tip inventory with the v2 biological panel and
adds an executed ASTRAL-III species-tree sensitivity from the per-locus IQ-TREE
gene trees.
"""
from __future__ import annotations
import argparse,csv,importlib.util,json
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('jog_legacy',ROOT/'analysis/build_japan_origin_global_hpc_bundle.py')
assert SPEC and SPEC.loader
legacy=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(legacy)
EXPECTED_SAMPLES=294;EXPECTED_RUNS=295

def clean(x):return str(x or '').strip()
def read_panel(path):
 with path.open(encoding='utf-8-sig',newline='') as h:rows=[{k:clean(v) for k,v in r.items()} for r in csv.DictReader(h)]
 req={'panel_id','source_studies','assay','analysis_taxon_label','voucher','biosample','run_accessions','run_count','japan38_member_ids','shared_cross_paper_sample'}
 if not rows or not req<=set(rows[0]):raise ValueError(f'v2 panel requires columns {sorted(req)}')
 if len(rows)!=EXPECTED_SAMPLES or len({r['biosample'] for r in rows})!=EXPECTED_SAMPLES:raise ValueError(f'expected {EXPECTED_SAMPLES} unique biological samples')
 all_runs=[]
 for r in rows:
  runs=[x for x in r['run_accessions'].split('|') if x]
  if len(runs)!=int(r['run_count']) or any(not x.startswith('SRR') for x in runs):raise ValueError(f'invalid run list for {r["panel_id"]}')
  all_runs.extend(runs)
 if len(all_runs)!=EXPECTED_RUNS or len(set(all_runs))!=EXPECTED_RUNS:raise ValueError(f'expected {EXPECTED_RUNS} unique public SRRs')
 return rows
def write(path,text,mode=0o644):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8');path.chmod(mode)
def sample_manifests(outdir,rows):
 fields=['index','tip_id','panel_id','source_study','assay','analysis_taxon_label','voucher','biosample','run_accessions','run_count','japan38_member_ids','shared_cross_paper_sample'];data=[]
 for i,r in enumerate(rows):data.append({'index':str(i),'tip_id':f'JOG{i+1:04d}','panel_id':r['panel_id'],'source_study':r['source_studies'],'assay':r['assay'],'analysis_taxon_label':r['analysis_taxon_label'],'voucher':r['voucher'],'biosample':r['biosample'],'run_accessions':r['run_accessions'],'run_count':r['run_count'],'japan38_member_ids':r['japan38_member_ids'],'shared_cross_paper_sample':r['shared_cross_paper_sample']})
 for fn,delim in [('sample_manifest.tsv','\t'),('sample_manifest.csv',',')]:
  with (outdir/fn).open('w',encoding='utf-8',newline='') as h:w=csv.DictWriter(h,fieldnames=fields,delimiter=delim,lineterminator='\n');w.writeheader();w.writerows(data)
 return data
def species_map(outdir,data):
 by=defaultdict(list)
 for r in data:by[r['analysis_taxon_label']].append(r['tip_id'])
 rows=[{'species_id':f'SP{i:04d}','analysis_taxon_label':taxon,'tip_ids':'|'.join(sorted(by[taxon])),'n_tips':str(len(by[taxon]))} for i,taxon in enumerate(sorted(by),1)]
 with (outdir/'astral_species_map.csv').open('w',encoding='utf-8',newline='') as h:w=csv.DictWriter(h,fieldnames=['species_id','analysis_taxon_label','tip_ids','n_tips']);w.writeheader();w.writerows(rows)
 lines=[f"{r['species_id']}:{','.join(r['tip_ids'].split('|'))}" for r in rows]+['OUTGROUP_lett:OUTGROUP_lett','OUTGROUP_sunf:OUTGROUP_sunf'];(outdir/'astral_map.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8');return rows
def patch(text):
 return (text.replace('--array=0-301','--array=0-293').replace('results/japan_origin_global','results/japan_origin_global_v2').replace('$REPO_ROOT/analysis/summarize_japan_origin_global_comp1061_qc.py','$BUNDLE_DIR/helpers/summarize_japan_origin_global_comp1061_qc_v2.py').replace('$REPO_ROOT/analysis/prepare_japan_origin_global_comp1061_tree_inputs.py','$BUNDLE_DIR/helpers/prepare_japan_origin_global_comp1061_tree_inputs_v2.py').replace('$REPO_ROOT/analysis/validate_japan_origin_global_tree.py','$BUNDLE_DIR/helpers/validate_japan_origin_global_tree_v2.py').replace('302 public biological samples / 303 runs','294 unique biological samples / 295 unique runs').replace('EAzami 302-sample','EAzami 294-tip').replace('all 302 samples','all 294 samples'))
def helper_sources(outdir):
 mapping={
  'summarize_japan_origin_global_comp1061_qc.py':'summarize_japan_origin_global_comp1061_qc_v2.py',
  'prepare_japan_origin_global_comp1061_tree_inputs.py':'prepare_japan_origin_global_comp1061_tree_inputs_v2.py',
  'validate_japan_origin_global_tree.py':'validate_japan_origin_global_tree_v2.py',
 }
 for old,new in mapping.items():
  text=(ROOT/'analysis'/old).read_text(encoding='utf-8').replace('302','294').replace('_v1','_v2')
  write(outdir/'helpers'/new,text,0o755)
 astral_validator='''#!/usr/bin/env python3
import argparse,csv,hashlib,json,re
from pathlib import Path
def tips(text):return re.findall(r'(?<=[(,])\\s*([A-Za-z0-9_]+)\\s*(?=[:),])',text)
def main():
 p=argparse.ArgumentParser();p.add_argument('--tree',type=Path,required=True);p.add_argument('--species-map',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 with a.species_map.open(encoding='utf-8-sig',newline='') as h:rows=list(csv.DictReader(h))
 focal={r['species_id'] for r in rows};seen_list=tips(a.tree.read_text(encoding='utf-8'));seen=set(seen_list);required={'OUTGROUP_lett','OUTGROUP_sunf'};allowed=focal|required|{'OUTGROUP_saff'}
 if required-seen:raise ValueError(f'ASTRAL required outgroups missing: {sorted(required-seen)}')
 if focal-seen:raise ValueError(f'ASTRAL missing {len(focal-seen)} mapped source-label taxa')
 if seen-allowed:raise ValueError(f'ASTRAL unexpected tips: {sorted(seen-allowed)[:10]}')
 if len(seen_list)!=len(seen):raise ValueError('ASTRAL output has duplicate tip labels')
 out={'contract_version':'japan_origin_astral_tree_acceptance_v2','tree_sha256':hashlib.sha256(a.tree.read_bytes()).hexdigest(),'mapped_source_label_taxa':len(focal),'tree_tips':len(seen),'required_outgroups_present':True,'tree_artifact_accepted':True,'rooting_status':'ASTRAL output is unrooted; root downstream with OUTGROUP_lett/OUTGROUP_sunf before biogeographic interpretation.','claim_limit':'ASTRAL sensitivity does not by itself establish dispersal direction, Japanese monophyly or Arenicola origin.'};a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
'''
 write(outdir/'helpers'/'validate_japan_origin_astral_tree_v2.py',astral_validator,0o755)
def env_yml():
 text=legacy.env_yml()
 if 'astral-tree' not in text:text=text.replace('  - biopython\n','  - biopython\n  - astral-tree=5.7.8\n')
 return text
def astral_script():return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-jogv2-astral
#SBATCH --cpus-per-task=4
#SBATCH --mem=96G
#SBATCH --time=12:00:00
'''+patch(legacy.common())+'''MODE="${MODE:-bwa}"; TREE="$RESULT_ROOT/tree_$MODE"; OUT="$TREE/astral"; mkdir -p "$OUT"; GT="$OUT/gene_trees.tre"; : > "$GT"
while IFS= read -r LOCUS; do test -s "$TREE/gene_trees/$LOCUS.treefile"; cat "$TREE/gene_trees/$LOCUS.treefile" >> "$GT"; printf '\n' >> "$GT"; done < "$TREE/inputs/eligible_loci.txt"
test -s "$GT"; MAP="$OUT/astral_map_runtime.txt"; cp "$BUNDLE_DIR/astral_map.txt" "$MAP"; if grep -q 'OUTGROUP_saff' "$GT"; then echo 'OUTGROUP_saff:OUTGROUP_saff' >> "$MAP"; fi; "${RUN[@]}" astral -Xmx90G -i "$GT" -a "$MAP" -o "$OUT/japan_origin_global_astral.tree" 2> "$OUT/astral.log"; test -s "$OUT/japan_origin_global_astral.tree"
'''
def accept_script():return '''#!/usr/bin/env bash
#SBATCH --job-name=EAzami-jogv2-accept
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=02:00:00
'''+patch(legacy.common())+'''MODE="${MODE:-bwa}"; TREE="$RESULT_ROOT/tree_$MODE"; TREEFILE="$TREE/concat/japan_origin_global_concat.treefile"; ASTRAL="$TREE/astral/japan_origin_global_astral.tree"; test -s "$TREEFILE"; test -s "$ASTRAL"
python - "$TREEFILE" "$TREE/concat/concat_summary.json" "$TREE/tree_provenance.json" <<'PYSCRIPT'
import hashlib,json,pathlib,sys
tr=pathlib.Path(sys.argv[1]);cs=json.loads(pathlib.Path(sys.argv[2]).read_text());out=pathlib.Path(sys.argv[3])
prov={'tree_sha256':hashlib.sha256(tr.read_bytes()).hexdigest(),'analysis_name':'EAzami 294-tip deduplicated global public Cirsium origin compatibility tree','branch_length_interpretation':'IQ-TREE maximum-likelihood substitutions per site on concatenated Compositae1061-compatible coding-sequence alignment','rooting_definition':'OUTGROUP_lett and OUTGROUP_sunf define the root; OUTGROUP_saff is retained as an optional near Cardueae reference','required_outgroup_tips':['OUTGROUP_lett','OUTGROUP_sunf'],'required_reference_tips':cs['reference_tips'],'support_metric_definition':'IQ-TREE ultrafast bootstrap 1000 plus SH-aLRT 1000; ASTRAL-III species tree is retained as a coalescent sensitivity','source_or_pipeline_provenance':'294 unique public biological samples / 295 unique SRRs from Moreyra 2025 plus deduplicated Chang 2025/2026; original Compositae1061 reference; strict frozen-241 current occupancy >=0.80 and zero-current-paralog admission; HybPiper 2.3.4; MAFFT; IQ-TREE; ASTRAL-III 5.7.8','topology_uncertainty_status':'bootstrap_plus_gene_tree_astral_sensitivity'}
out.write_text(json.dumps(prov,indent=2)+'\n')
PYSCRIPT
"${RUN[@]}" python "$BUNDLE_DIR/helpers/validate_japan_origin_global_tree_v2.py" --tree "$TREEFILE" --manifest "$BUNDLE_DIR/sample_manifest.csv" --provenance "$TREE/tree_provenance.json" --output "$TREE/tree_acceptance.json"
"${RUN[@]}" python "$BUNDLE_DIR/helpers/validate_japan_origin_astral_tree_v2.py" --tree "$ASTRAL" --species-map "$BUNDLE_DIR/astral_species_map.csv" --output "$TREE/astral/tree_acceptance.json"
'''
def submit_tree():return '''#!/usr/bin/env bash
set -euo pipefail
MODE="${MODE:-bwa}"; prep=$(sbatch --parsable --export=ALL,MODE="$MODE" 04_prepare_tree_inputs_slurm.sh); aln=$(sbatch --parsable --dependency=afterok:$prep --export=ALL,MODE="$MODE" 05_align_loci_slurm.sh); gene=$(sbatch --parsable --dependency=afterok:$aln --export=ALL,MODE="$MODE" 06_gene_trees_slurm.sh); con=$(sbatch --parsable --dependency=afterok:$aln --export=ALL,MODE="$MODE" 07_concat_tree_slurm.sh); ast=$(sbatch --parsable --dependency=afterok:$gene --export=ALL,MODE="$MODE" 08_astral_species_tree_slurm.sh); acc=$(sbatch --parsable --dependency=afterok:$con:$ast --export=ALL,MODE="$MODE" 09_accept_trees_slurm.sh); printf 'prep=%s\nalign=%s\ngene=%s\nconcat=%s\nastral=%s\naccept=%s\n' "$prep" "$aln" "$gene" "$con" "$ast" "$acc"
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--panel',type=Path,required=True);p.add_argument('--outdir',type=Path,required=True);a=p.parse_args();rows=read_panel(a.panel);a.outdir.mkdir(parents=True,exist_ok=True);data=sample_manifests(a.outdir,rows);species=species_map(a.outdir,data);helper_sources(a.outdir);write(a.outdir/'env.yml',env_yml())
 scripts={'00_prepare_inputs_slurm.sh':patch(legacy.prep()),'01_fetch_trim_slurm.sh':patch(legacy.fetch()),'02_hybpiper_bwa_slurm.sh':patch(legacy.hyb('bwa')),'02b_hybpiper_blastx_slurm.sh':patch(legacy.hyb('blastx')),'03_retrieve_qc_slurm.sh':patch(legacy.qc()),'04_prepare_tree_inputs_slurm.sh':patch(legacy.treeprep()),'05_align_loci_slurm.sh':patch(legacy.align()),'06_gene_trees_slurm.sh':patch(legacy.gene()),'07_concat_tree_slurm.sh':patch(legacy.concat()),'08_astral_species_tree_slurm.sh':astral_script(),'09_accept_trees_slurm.sh':accept_script(),'submit_bwa_chain.sh':patch(legacy.submit_data('bwa')),'submit_blastx_chain.sh':patch(legacy.submit_data('blastx')),'submit_tree_chain.sh':submit_tree()}
 for n,t in scripts.items():write(a.outdir/n,t,0o755)
 m={'bundle_version':'japan_origin_global_hpc_bundle_v2','biological_samples':EXPECTED_SAMPLES,'public_runs':EXPECTED_RUNS,'source_preserving_taxon_labels':len(species),'cross_paper_read_duplicates_removed':8,'safe_tip_ids':True,'primary_mapping':'bwa','mapping_sensitivity':'blastx','hybpiper_version':'2.3.4','frozen_primary_locus_universe':241,'primary_current_occupancy_gate':0.80,'current_paralog_gate':'zero HybPiper >1-copy warnings across all 294 samples','minimum_primary_loci_to_launch':100,'automatic_filter_relaxation_allowed':False,'tree_products':['294-tip concatenated IQ-TREE ML tree','source-label ASTRAL-III 5.7.8 species tree','per-locus IQ-TREE gene trees'],'tree_completed':False,'japanese_origin_inference_completed':False,'new_china_sampling_freeze_allowed':False};write(a.outdir/'execution_manifest.json',json.dumps(m,indent=2)+'\n');print(json.dumps(m,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
