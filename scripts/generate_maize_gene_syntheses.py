#!/usr/bin/env python3
"""Generate static maize gene synthesis assets for the website tool."""

from __future__ import annotations

import argparse
import json
import sqlite3
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_GENEANNOTATION = Path(__file__).resolve().parents[2] / "GeneAnnotation"
DEFAULT_SYNTHESIS_DB = (
    DEFAULT_GENEANNOTATION
    / "data/processed/direct_evidence_syntheses/direct_synthesis.sqlite"
)
DEFAULT_EVIDENCE_DB = (
    DEFAULT_GENEANNOTATION / "data/processed/evidence/evidence.sqlite"
)
DEFAULT_OUTPUT_DIR = (
    Path(__file__).resolve().parents[1] / "assets/data/maize-gene-syntheses"
)


def normalize_query(value: str) -> str:
    return " ".join(value.strip().lower().split())


def shard_for_gene(gene_id: str) -> str:
    prefix = "Zm00001eb"
    if gene_id.startswith(prefix) and len(gene_id) >= len(prefix) + 2:
        return gene_id[len(prefix) : len(prefix) + 2]
    return "other"


def load_syntheses(db_path: Path) -> dict[str, list[str]]:
    with sqlite3.connect(db_path) as con:
        rows = con.execute(
            """
            SELECT gene_id, function_phrase, function_sentence, annotation_abstract
            FROM direct_gene_syntheses
            WHERE species = 'zea_mays'
            ORDER BY gene_id
            """
        ).fetchall()

    return {
        gene_id: [function_phrase or "", function_sentence or "", annotation_abstract or ""]
        for gene_id, function_phrase, function_sentence, annotation_abstract in rows
    }


def load_lookup(
    db_path: Path, valid_gene_ids: set[str]
) -> tuple[dict[str, list[str]], int]:
    query = """
        SELECT synonym_norm, synonym, gene_id, synonym_type, query_priority
        FROM maize_gene_synonyms
        WHERE is_ambiguous = 0
          AND (is_gene_model_id = 1 OR include_in_pubmed_query = 1)
        ORDER BY synonym_norm, query_priority, synonym_type, synonym
    """
    lookup: dict[str, list[str]] = {}
    skipped = 0
    with sqlite3.connect(db_path) as con:
        for synonym_norm, synonym, gene_id, synonym_type, priority in con.execute(query):
            if gene_id not in valid_gene_ids:
                skipped += 1
                continue
            key = normalize_query(synonym_norm or synonym)
            if not key:
                continue
            lookup.setdefault(
                key,
                [
                    gene_id,
                    synonym,
                    synonym_type,
                    shard_for_gene(gene_id),
                ],
            )
    return lookup, skipped


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--synthesis-db", type=Path, default=DEFAULT_SYNTHESIS_DB)
    parser.add_argument("--evidence-db", type=Path, default=DEFAULT_EVIDENCE_DB)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    syntheses = load_syntheses(args.synthesis_db)
    lookup, skipped_synonyms = load_lookup(args.evidence_db, set(syntheses))

    if args.output_dir.exists():
        for old_file in args.output_dir.glob("*.json"):
            old_file.unlink()
        shard_dir = args.output_dir / "shards"
        if shard_dir.exists():
            for old_file in shard_dir.glob("*.json"):
                old_file.unlink()

    shards: dict[str, dict[str, list[str]]] = defaultdict(dict)
    for gene_id, record in syntheses.items():
        shards[shard_for_gene(gene_id)][gene_id] = record

    write_json(args.output_dir / "lookup.json", lookup)
    for shard, records in sorted(shards.items()):
        write_json(args.output_dir / "shards" / f"{shard}.json", records)

    metadata = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "species": "zea_mays",
        "synthesis_source": "direct_gene_syntheses",
        "synonym_source": "maize_gene_synonyms",
        "gene_count": len(syntheses),
        "lookup_count": len(lookup),
        "skipped_synonyms_without_synthesis": skipped_synonyms,
        "shard_count": len(shards),
    }
    write_json(args.output_dir / "metadata.json", metadata)

    print(
        f"Wrote {metadata['gene_count']} syntheses, "
        f"{metadata['lookup_count']} lookup terms, and "
        f"{metadata['shard_count']} shards to {args.output_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
