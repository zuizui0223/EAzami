#!/usr/bin/env python3
"""Directionally validate Azami image-orientation medians against authority states.

Uses an exact group-label permutation of the difference in group medians. This is
an external construct-validity check, not a calibration from image vertical to
true gravitational orientation and not an evolutionary analysis.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

UP = "upward_or_erect"
DOWN = "downward_or_nodding"


def build(frame: pd.DataFrame) -> dict:
    required={"taxon_name","n_detector_positive_observations","image_orientation_median_degrees","authority_orientation_state"}
    if required.difference(frame.columns): raise ValueError("Validation table incomplete")
    data=frame.loc[frame["authority_orientation_state"].isin([UP,DOWN])].copy()
    data["image_orientation_median_degrees"]=pd.to_numeric(data["image_orientation_median_degrees"],errors="raise")
    if data["taxon_name"].duplicated().any(): raise ValueError("Duplicate taxon")
    up=data.loc[data["authority_orientation_state"].eq(UP),"image_orientation_median_degrees"].to_numpy(float)
    down=data.loc[data["authority_orientation_state"].eq(DOWN),"image_orientation_median_degrees"].to_numpy(float)
    if len(up)<2 or len(down)<2: raise ValueError("Need at least two taxa per group")
    observed=float(np.median(down)-np.median(up))
    values=data["image_orientation_median_degrees"].to_numpy(float)
    n_down=len(down)
    diffs=[]
    for indices in itertools.combinations(range(len(values)),n_down):
        chosen=set(indices)
        d=np.array([values[i] for i in range(len(values)) if i in chosen],dtype=float)
        u=np.array([values[i] for i in range(len(values)) if i not in chosen],dtype=float)
        diffs.append(float(np.median(d)-np.median(u)))
    positive_p=float(sum(value>=observed-1e-15 for value in diffs)/len(diffs))
    two_sided_p=float(sum(abs(value)>=abs(observed)-1e-15 for value in diffs)/len(diffs))
    return {
        "contract_version":"japan38_image_authority_orientation_validation_v1",
        "n_taxa":int(len(data)),
        "n_upward_authority_taxa":int(len(up)),
        "n_downward_authority_taxa":int(len(down)),
        "upward_group_image_angle_median":float(np.median(up)),
        "downward_group_image_angle_median":float(np.median(down)),
        "down_minus_up_median_angle_difference":observed,
        "exact_label_permutations":int(len(diffs)),
        "directional_positive_permutation_p":positive_p,
        "two_sided_permutation_p":two_sided_p,
        "descriptive_result":(
            "The Azami image-orientation proxy is directionally consistent with the authority categories in this "
            "small overlap set: authority-downward taxa have a larger median image angle than authority-upward taxa."
        ),
        "claim_boundary":(
            "The overlap contains only eight taxa and the exact permutation test is not significant at 0.05. "
            "Image vertical remains a proxy rather than gravity, authority categories can contain population "
            "variation, and this check does not calibrate individual measurements or validate ancestral states."
        ),
    }


def main():
    p=argparse.ArgumentParser(); p.add_argument("--input",required=True); p.add_argument("--out",required=True)
    a=p.parse_args(); result=build(pd.read_csv(a.input)); out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8"); print(json.dumps(result,indent=2,ensure_ascii=False))

if __name__=="__main__": main()
