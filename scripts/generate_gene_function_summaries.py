#!/usr/bin/env python3
"""Generate static gene function summary assets for the website tool."""

from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
from collections import defaultdict
from dataclasses import dataclass
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
    Path(__file__).resolve().parents[1] / "assets/data/gene-function-summaries"
)


@dataclass(frozen=True)
class SpeciesConfig:
    key: str
    label: str
    synthesis_species: str
    synonym_table: str
    shard_prefix: str
    shard_chars: int


SPECIES = (
    SpeciesConfig(
        key="maize",
        label="Maize",
        synthesis_species="zea_mays",
        synonym_table="maize_gene_synonyms",
        shard_prefix="Zm00001eb",
        shard_chars=2,
    ),
    SpeciesConfig(
        key="sorghum",
        label="Sorghum",
        synthesis_species="sorghum_bicolor",
        synonym_table="sorghum_gene_synonyms",
        shard_prefix="Sobic.",
        shard_chars=3,
    ),
)


def normalize_query(value: str) -> str:
    return " ".join(value.strip().lower().split())


def shard_for_gene(gene_id: str, config: SpeciesConfig) -> str:
    prefix = config.shard_prefix
    if gene_id.startswith(prefix) and len(gene_id) >= len(prefix) + config.shard_chars:
        return gene_id[len(prefix) : len(prefix) + config.shard_chars].lower()
    return "other"


def load_latest_syntheses(
    db_path: Path, species: str
) -> tuple[dict[str, list[str]], int]:
    with sqlite3.connect(db_path) as con:
        rows = con.execute(
            """
            SELECT gene_id, function_phrase, function_sentence, annotation_abstract
            FROM (
                SELECT
                    gene_id,
                    function_phrase,
                    function_sentence,
                    annotation_abstract,
                    row_number() OVER (
                        PARTITION BY gene_id
                        ORDER BY created_at DESC, batch_id DESC, custom_id DESC
                    ) AS rn
                FROM direct_gene_syntheses
                WHERE species = ?
            )
            WHERE rn = 1
            ORDER BY gene_id
            """,
            (species,),
        ).fetchall()
        total_rows = con.execute(
            "SELECT COUNT(*) FROM direct_gene_syntheses WHERE species = ?",
            (species,),
        ).fetchone()[0]

    return (
        {
            gene_id: [
                function_phrase or "",
                function_sentence or "",
                annotation_abstract or "",
            ]
            for gene_id, function_phrase, function_sentence, annotation_abstract in rows
        },
        total_rows,
    )


def load_lookup(
    db_path: Path, config: SpeciesConfig, valid_gene_ids: set[str]
) -> tuple[dict[str, list[str]], int]:
    query = f"""
        SELECT synonym_norm, synonym, gene_id, synonym_type, query_priority
        FROM {config.synonym_table}
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
                    shard_for_gene(gene_id, config),
                ],
            )
    return lookup, skipped


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True),
        encoding="utf-8",
    )


def generate_species(
    config: SpeciesConfig,
    synthesis_db: Path,
    evidence_db: Path,
    output_dir: Path,
) -> dict[str, object]:
    syntheses, synthesis_row_count = load_latest_syntheses(
        synthesis_db, config.synthesis_species
    )
    lookup, skipped_synonyms = load_lookup(evidence_db, config, set(syntheses))

    species_dir = output_dir / config.key
    shards_dir = species_dir / "shards"
    shards: dict[str, dict[str, list[str]]] = defaultdict(dict)
    for gene_id, record in syntheses.items():
        shards[shard_for_gene(gene_id, config)][gene_id] = record

    write_json(species_dir / "lookup.json", lookup)
    for shard, records in sorted(shards.items()):
        write_json(shards_dir / f"{shard}.json", records)

    return {
        "key": config.key,
        "label": config.label,
        "species": config.synthesis_species,
        "synthesis_source": "direct_gene_syntheses",
        "synonym_source": config.synonym_table,
        "synthesis_row_count": synthesis_row_count,
        "gene_count": len(syntheses),
        "lookup_count": len(lookup),
        "skipped_synonyms_without_synthesis": skipped_synonyms,
        "shard_count": len(shards),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--synthesis-db", type=Path, default=DEFAULT_SYNTHESIS_DB)
    parser.add_argument("--evidence-db", type=Path, default=DEFAULT_EVIDENCE_DB)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--species",
        choices=[config.key for config in SPECIES],
        nargs="+",
        default=[config.key for config in SPECIES],
    )
    args = parser.parse_args()

    selected = [config for config in SPECIES if config.key in set(args.species)]

    if args.output_dir.exists():
        shutil.rmtree(args.output_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    species_metadata = []
    for config in selected:
        metadata = generate_species(
            config=config,
            synthesis_db=args.synthesis_db,
            evidence_db=args.evidence_db,
            output_dir=args.output_dir,
        )
        species_metadata.append(metadata)
        print(
            f"Wrote {metadata['gene_count']} {config.label.lower()} syntheses, "
            f"{metadata['lookup_count']} lookup terms, and "
            f"{metadata['shard_count']} shards"
        )

    metadata = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "species": species_metadata,
    }
    write_json(args.output_dir / "metadata.json", metadata)
    print(f"Wrote summary metadata to {args.output_dir / 'metadata.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
