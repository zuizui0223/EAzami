#!/usr/bin/env python3
"""Directional public palaeoclimate sensitivity for the 0.79-0.47 Ma U->D event.

Uses the regional-series reader from the primary paleohydric workflow. The key
estimand is young-end minus old-end climate value: positive BIO12/BIO15 means
rain amount/seasonality increased toward the descendant D clade; negative BIO1
means cooling toward the descendant D clade. Percentiles are relative to all
same-duration 320-kyr windows across the 5-Myr public PALEO-PGEM series.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
from run_chapter2_taiwan_orientation_paleohydric_window_v1 import regional_series

YOUNG, OLD, WIDTH = 470.0, 790.0, 320.0


def delta(df, young, old):
    w=df[(df.age_ka>=young)&(df.age_ka<=old)].sort_values('age_ka')
    if len(w)<50: raise ValueError('insufficient time points')
    y=float(w.iloc[0]['median'])   # younger end
    o=float(w.iloc[-1]['median'])  # older end
    return {'young_value':y,'old_value':o,'young_minus_old':y-o,'abs_change':abs(y-o)}


def analyze(path):
    df=regional_series(path)
    obs=delta(df,YOUNG,OLD)
    starts=np.arange(0.0,min(5000.0,float(df.age_ka.max()))-WIDTH+1e-9,10.0)
    vals=np.array([delta(df,float(s),float(s+WIDTH))['young_minus_old'] for s in starts])
    obs['signed_percentile']=float((np.sum(vals<=obs['young_minus_old'])+0.5)/(len(vals)+1.0))
    obs['two_sided_extremeness']=float(2*min(obs['signed_percentile'],1-obs['signed_percentile']))
    obs['n_matched_windows']=int(len(vals))
    return obs


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--bio12',type=Path,required=True)
    ap.add_argument('--bio15',type=Path,required=True)
    ap.add_argument('--bio1',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    out={
      'contract_version':'chapter2_taiwan_orientation_directional_sensitivity_v1',
      'event':'minimum U->D orientation transition on Taiwan-trio stem',
      'event_window_ma':[0.47,0.79],
      'estimand':'young endpoint minus old endpoint across the 320-kyr admissible transition branch',
      'expected_if_present_niche_direction_tracks_history':{
        'BIO12':'positive is compatible with Azami higher-rainfall -> larger/downward angle sorting',
        'BIO15':'positive is compatible with EAzami D taxa occupying higher precipitation-seasonality niches',
        'BIO1':'negative is compatible with EAzami D taxa occupying lower-temperature niches'
      },
      'BIO12':analyze(a.bio12), 'BIO15':analyze(a.bio15), 'BIO1':analyze(a.bio1),
      'claim_boundary':'Local published-age sensitivity only; endpoint direction does not identify the exact transition date, selection, adaptation, or all Japan38 events.'
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__': main()
