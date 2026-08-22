import json
import sys
from pathlib import Path
import pandas as pd

path = Path(sys.argv[1])
book = pd.ExcelFile(path)
summary = {"sheets": book.sheet_names, "sheet_summaries": {}}
for sheet in book.sheet_names:
    df = pd.read_excel(path, sheet_name=sheet)
    info = {
        "rows": int(len(df)),
        "columns": [str(c) for c in df.columns],
        "sample_rows": df.head(3).fillna("").astype(str).to_dict(orient="records"),
    }
    # Print compact unique values for low-cardinality columns to discover coding.
    low = {}
    for c in df.columns:
        vals = df[c].dropna().astype(str).unique()
        if 1 <= len(vals) <= 30:
            low[str(c)] = sorted(vals.tolist())[:30]
    info["low_cardinality_values"] = low
    summary["sheet_summaries"][sheet] = info

out = Path("results/caruso2019_dryad_schema.json")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary, indent=2))
