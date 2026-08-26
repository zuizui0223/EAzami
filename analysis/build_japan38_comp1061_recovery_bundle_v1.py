#!/usr/bin/env python3
"""Build the thin GitHub/Slurm recovery bundle for the 39-sample Japan-38 subset."""
from __future__ import annotations
import argparse,importlib.util,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('jogp',ROOT/'analysis/japan_origin_global_hpc_primitives.py');assert SPEC and SPEC.loader
P=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(P)
NS='japan38_comp1061_v1'

def write(path,text,mode=0o644):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8');path.chmod(mode)
def main():
    p=argparse.ArgumentParser();p.add_argument('--subset-dir',type=Path,required=True);p.add_argument('--outdir',type=Path,required=True);a=p.parse_args();a.outdir.mkdir(parents=True,exist_ok=True)
    for fn in ('sample_manifest.csv','sample_manifest.tsv','concept_map.csv','summary.json'):
        src=a.subset_dir/fn
        if not src.is_file():raise ValueError(f'missing subset file {src}')
        shutil.copy2(src,a.outdir/fn)
    write(a.outdir/'env.yml',P.env_yml())
    write(a.outdir/'00_prepare_inputs_slurm.sh',P.prep(NS),0o755)
    write(a.outdir/'01_fetch_trim_slurm.sh',P.fetch(NS,38,max_parallel=4),0o755)
    print(f'Japan38 recovery bundle ready: {a.outdir}')
if __name__=='__main__':main()
