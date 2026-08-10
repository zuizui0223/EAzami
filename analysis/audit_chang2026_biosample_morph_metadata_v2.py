#!/usr/bin/env python3
"""Run the Chang BioSample morph audit with collector-number reconciliation.

NCBI PRJNA1311153 runinfo stores the six var. takaoense samples as values such
as ``Cirsium japonicum var. takaoense-3559`` in ``SampleName``. Supplementary
Table S1 stores the same collector as ``ccy3559``. This wrapper adds that direct,
taxon-qualified collector-number match while preserving every conservative
colour-assignment rule from ``audit_chang2026_biosample_morph_metadata``.

Collector number is used only to link provenance. It never assigns W or BP.
"""

from __future__ import annotations

import re
from typing import Mapping

import audit_chang2026_biosample_morph_metadata as base


def collector_number(value: object) -> str:
    """Return the terminal numeric collector identifier, if present."""
    match = re.search(r"(\d+)$", str(value or "").strip())
    return match.group(1) if match else ""


def score_seed_run(
    seed: Mapping[str, str], run: Mapping[str, str]
) -> tuple[int, str]:
    """Prefer exact voucher text, then taxon-qualified collector number."""
    score, basis = base.score_seed_run(seed, run)
    if score >= 100:
        return score, basis

    number = collector_number(seed.get("voucher", ""))
    sample_name = base.compact(run.get("SampleName", ""))
    if number and re.search(r"\btakaoense\s*[-_ ]\s*" + re.escape(number) + r"\b", sample_name, re.I):
        return 95, "exact_takaoense_collector_number_in_sample_name"

    # BioSample isolate values are not part of runinfo in every export, but when
    # present they are also a direct collector-number identifier. Require the
    # run to carry the takaoense taxon name elsewhere before accepting it.
    isolate = base.compact(run.get("isolate", ""))
    run_text = base.run_search_text(run)
    if (
        number
        and isolate == number
        and re.search(r"\btakaoense\b", run_text, re.I)
    ):
        return 90, "exact_takaoense_collector_number_in_isolate"

    return score, basis


def main() -> int:
    # base.match_runs_to_seeds resolves this global at call time, so patching the
    # module function applies the stricter reconciliation without duplicating the
    # audited network and output code.
    base.score_seed_run = score_seed_run
    return base.main()


if __name__ == "__main__":
    raise SystemExit(main())
