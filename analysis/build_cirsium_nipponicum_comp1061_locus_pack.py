#!/usr/bin/env python3
"""Build a strict Compositae1061 CDS pack from the public Ulleung C. nipponicum genome.

Expected upstream steps:
1. gffread extracts CDS and translated proteins from the public genome + GFF3;
2. DIAMOND blastx maps the original Compositae1061 DNA targets to those proteins;
3. this script admits only unambiguous, well-covered homologs in the frozen
   conservative-241 locus universe.

The resulting locus pack is an augmentation input. It does not alter the accepted
294-tip primary tree until a downstream cross-data-type placement comparison passes.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from typing import Iterable, Mapping, Sequence

REF_PREFIXES = ("lett", "saff", "sunf")
STANDARD_CODE = {
    "TTT":"F","TTC":"F","TTA":"L","TTG":"L","TCT":"S","TCC":"S","TCA":"S","TCG":"S",
    "TAT":"Y","TAC":"Y","TAA":"*","TAG":"*","TGT":"C","TGC":"C","TGA":"*","TGG":"W",
    "CTT":"L","CTC":"L","CTA":"L","CTG":"L","CCT":"P","CCC":"P","CCA":"P","CCG":"P",
    "CAT":"H","CAC":"H","CAA":"Q","CAG":"Q","CGT":"R","CGC":"R","CGA":"R","CGG":"R",
    "ATT":"I","ATC":"I","ATA":"I","ATG":"M","ACT":"T","ACC":"T","ACA":"T","ACG":"T",
    "AAT":"N","AAC":"N","AAA":"K","AAG":"K","AGT":"S","AGC":"S","AGA":"R","AGG":"R",
    "GTT":"V","GTC":"V","GTA":"V","GTG":"V","GCT":"A","GCC":"A","GCA":"A","GCG":"A",
    "GAT":"D","GAC":"D","GAA":"E","GAG":"E","GGT":"G","GGC":"G","GGA":"G","GGG":"G",
}


def clean(value: object) -> str:
    return str(value or "").strip()


def read_fasta(path: Path) -> list[tuple[str, str]]:
    records: list[tuple[str, str]] = []
    name: str | None = None
    seq: list[str] = []
    with path.open(encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line:
                continue
            if line.startswith(">"):
                if name is not None:
                    records.append((name, "".join(seq).upper()))
                name = line[1:].split()[0]
                seq = []
            else:
                seq.append(line)
    if name is not None:
        records.append((name, "".join(seq).upper()))
    if not records:
        raise ValueError(f"{path}: no FASTA records")
    return records


def fasta_dict(path: Path) -> dict[str, str]:
    rows = read_fasta(path)
    out: dict[str, str] = {}
    for name, seq in rows:
        if name in out:
            raise ValueError(f"{path}: duplicate FASTA id {name}")
        out[name] = seq
    return out


def write_fasta(path: Path, records: Iterable[tuple[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for name, seq in records:
            handle.write(f">{name}\n")
            for start in range(0, len(seq), 80):
                handle.write(seq[start:start + 80] + "\n")


def locus_from_target_id(query: str) -> str | None:
    for prefix in REF_PREFIXES:
        token = prefix + "-"
        if query.startswith(token):
            return query[len(token):]
    return None


def read_locus_list(path: Path) -> list[str]:
    loci = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(loci) != 241 or len(set(loci)) != 241:
        raise ValueError(f"expected exactly 241 unique frozen loci, found {len(loci)} / {len(set(loci))}")
    return loci


def target_queries(path: Path) -> dict[str, set[str]]:
    out: dict[str, set[str]] = defaultdict(set)
    for name, _ in read_fasta(path):
        locus = locus_from_target_id(name)
        if locus:
            out[locus].add(name)
    if len(out) != 1061:
        raise ValueError(f"target reference should contain 1061 loci, found {len(out)}")
    return out


def translate_cds(seq: str) -> str:
    seq = seq.upper().replace("U", "T")
    if len(seq) % 3:
        return ""
    aa: list[str] = []
    for i in range(0, len(seq), 3):
        codon = seq[i:i + 3]
        if set(codon) - set("ACGT"):
            aa.append("X")
        else:
            aa.append(STANDARD_CODE[codon])
    return "".join(aa)


def norm_aa(seq: str) -> str:
    return seq.upper().rstrip("*")


def read_hits(path: Path, wanted: set[str]) -> dict[str, dict[str, dict[str, dict[str, float]]]]:
    """locus -> subject -> query -> best hit metrics."""
    out: dict[str, dict[str, dict[str, dict[str, float]]]] = defaultdict(lambda: defaultdict(dict))
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        for row in reader:
            if not row:
                continue
            if len(row) != 7:
                raise ValueError(f"DIAMOND row should have 7 fields, found {len(row)}: {row[:3]}")
            qseqid, sseqid, pident, length, evalue, bitscore, qcovhsp = row
            locus = locus_from_target_id(qseqid)
            if not locus or locus not in wanted:
                continue
            hit = {
                "pident": float(pident),
                "length": float(length),
                "evalue": float(evalue),
                "bitscore": float(bitscore),
                "qcovhsp": float(qcovhsp),
            }
            prev = out[locus][sseqid].get(qseqid)
            if prev is None or hit["bitscore"] > prev["bitscore"]:
                out[locus][sseqid][qseqid] = hit
    return out


def candidate_stats(query_hits: Mapping[str, Mapping[str, float]]) -> dict[str, float | int]:
    hits = list(query_hits.values())
    return {
        "reference_query_count": len(query_hits),
        "score": sum(float(hit["bitscore"]) for hit in hits),
        "median_qcov": median(float(hit["qcovhsp"]) for hit in hits),
        "minimum_qcov": min(float(hit["qcovhsp"]) for hit in hits),
        "maximum_evalue": max(float(hit["evalue"]) for hit in hits),
        "median_pident": median(float(hit["pident"]) for hit in hits),
    }


def build(
    target: Path,
    locus_list: Path,
    gff_protein: Path,
    gff_cds: Path,
    published_protein: Path,
    hits: Path,
    outdir: Path,
    min_reference_queries: int = 2,
    max_second_ratio: float = 0.90,
    min_qcov: float = 50.0,
) -> dict[str, object]:
    loci = read_locus_list(locus_list)
    wanted = set(loci)
    queries = target_queries(target)
    proteins = fasta_dict(gff_protein)
    cds = fasta_dict(gff_cds)
    published_sequences = {norm_aa(seq) for _, seq in read_fasta(published_protein)}
    hitmap = read_hits(hits, wanted)

    rows: list[dict[str, object]] = []
    provisional_subjects: list[str] = []
    for locus in loci:
        subject_rows: list[tuple[str, dict[str, float | int]]] = []
        for subject, query_hits in hitmap.get(locus, {}).items():
            subject_rows.append((subject, candidate_stats(query_hits)))
        subject_rows.sort(key=lambda item: (-float(item[1]["score"]), item[0]))

        best_subject = subject_rows[0][0] if subject_rows else ""
        best = subject_rows[0][1] if subject_rows else {}
        second_subject = subject_rows[1][0] if len(subject_rows) > 1 else ""
        second_score = float(subject_rows[1][1]["score"]) if len(subject_rows) > 1 else 0.0
        best_score = float(best.get("score", 0.0))
        ratio = second_score / best_score if best_score else math.nan
        aa = proteins.get(best_subject, "")
        dna = cds.get(best_subject, "")
        translated = translate_cds(dna) if dna else ""
        translation_match = bool(aa and translated and norm_aa(aa) == norm_aa(translated))
        published_match = bool(aa and norm_aa(aa) in published_sequences)

        reasons: list[str] = []
        if not subject_rows:
            reasons.append("no_diamond_hit")
        if int(best.get("reference_query_count", 0)) < min_reference_queries:
            reasons.append("fewer_than_two_reference_queries")
        if float(best.get("minimum_qcov", 0.0)) < min_qcov:
            reasons.append("query_coverage_below_threshold")
        if second_subject and ratio > max_second_ratio:
            reasons.append("near_tie_second_subject")
        if best_subject not in proteins:
            reasons.append("best_subject_missing_gffread_protein")
        if best_subject not in cds:
            reasons.append("best_subject_missing_gffread_cds")
        if dna and len(dna) % 3:
            reasons.append("cds_not_divisible_by_three")
        if dna and not translation_match:
            reasons.append("gffread_cds_translation_mismatch")
        if aa and not published_match:
            reasons.append("gffread_protein_not_exactly_in_published_proteome")
        if best_subject and not reasons:
            provisional_subjects.append(best_subject)

        rows.append({
            "locus": locus,
            "target_reference_query_count": len(queries.get(locus, set())),
            "diamond_subject_count": len(subject_rows),
            "best_subject": best_subject,
            "best_reference_query_count": int(best.get("reference_query_count", 0)),
            "best_score": best_score,
            "best_minimum_qcov": float(best.get("minimum_qcov", 0.0)),
            "best_median_qcov": float(best.get("median_qcov", 0.0)),
            "best_median_pident": float(best.get("median_pident", 0.0)),
            "best_maximum_evalue": float(best.get("maximum_evalue", math.nan)),
            "second_subject": second_subject,
            "second_score": second_score,
            "second_to_best_score_ratio": ratio,
            "cds_length": len(dna),
            "protein_length": len(aa),
            "translation_matches_gffread_protein": translation_match,
            "gffread_protein_matches_published_proteome": published_match,
            "cross_locus_subject_collision": False,
            "strict_eligible": not reasons,
            "reason": "eligible" if not reasons else "|".join(reasons),
        })

    collisions = {subject for subject, count in Counter(provisional_subjects).items() if count > 1}
    for row in rows:
        subject = clean(row["best_subject"])
        if subject and subject in collisions and bool(row["strict_eligible"]):
            row["cross_locus_subject_collision"] = True
            row["strict_eligible"] = False
            row["reason"] = "cross_locus_subject_collision"

    strict = [row for row in rows if bool(row["strict_eligible"])]
    outdir.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0])
    with (outdir / "cirsium_nipponicum_comp1061_locus_audit.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    strict_loci = [clean(row["locus"]) for row in strict]
    (outdir / "strict_recovered_loci.txt").write_text(
        "".join(f"{locus}\n" for locus in strict_loci), encoding="utf-8"
    )
    locus_dir = outdir / "loci"
    for row in strict:
        locus = clean(row["locus"])
        subject = clean(row["best_subject"])
        write_fasta(locus_dir / f"{locus}.fasta", [("AUG_ULLEUNG_CNIP2024", cds[subject])])

    reason_counts = Counter(clean(row["reason"]) for row in rows)
    summary: dict[str, object] = {
        "contract_version": "cirsium_nipponicum_comp1061_locus_pack_v1",
        "frozen_candidate_loci": len(loci),
        "strict_recovered_loci": len(strict),
        "strict_recovered_fraction": len(strict) / len(loci),
        "minimum_strict_loci_for_augmentation": 100,
        "augmentation_locus_pack_ready": len(strict) >= 100,
        "tip_id": "AUG_ULLEUNG_CNIP2024",
        "minimum_reference_queries": min_reference_queries,
        "maximum_second_to_best_score_ratio": max_second_ratio,
        "minimum_query_coverage_percent": min_qcov,
        "cross_locus_subject_collisions": len(collisions),
        "reason_counts": dict(sorted(reason_counts.items())),
        "published_proteome_unique_sequence_count": len(published_sequences),
        "gffread_protein_record_count": len(proteins),
        "gffread_cds_record_count": len(cds),
        "tree_tip_promotion_allowed": False,
        "claim_limit": (
            "A ready locus pack permits a predeclared 295-tip genome-augmentation tree. "
            "It does not modify the accepted 294-tip primary tree until placement is stable "
            "under cross-data-type sensitivity."
        ),
    }
    (outdir / "cirsium_nipponicum_comp1061_locus_pack_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if not summary["augmentation_locus_pack_ready"]:
        raise ValueError(
            f"Only {len(strict)} strict Ulleung loci recovered; augmentation requires >=100."
        )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--locus-list", type=Path, required=True)
    parser.add_argument("--gff-protein", type=Path, required=True)
    parser.add_argument("--gff-cds", type=Path, required=True)
    parser.add_argument("--published-protein", type=Path, required=True)
    parser.add_argument("--diamond-hits", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--min-reference-queries", type=int, default=2)
    parser.add_argument("--max-second-ratio", type=float, default=0.90)
    parser.add_argument("--min-qcov", type=float, default=50.0)
    args = parser.parse_args()
    build(
        args.target,
        args.locus_list,
        args.gff_protein,
        args.gff_cds,
        args.published_protein,
        args.diamond_hits,
        args.outdir,
        args.min_reference_queries,
        args.max_second_ratio,
        args.min_qcov,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
