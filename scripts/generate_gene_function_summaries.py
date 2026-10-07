#!/usr/bin/env python3
"""Generate static gene function summary assets for the website tool (GeneAnnotation v2).

Reads the GeneAnnotation_v2 database (active summaries, gene names, key papers, Dias et al. 2025
syntenic orthologs) and the key-paper author cache, and writes gzipped JSON under
assets/data/gene-function-summaries/:

  metadata.json                            plain JSON: version, counts, bucket/shard counts
  <species>/lookup/NN.json.gz              name index, LOOKUP_BUCKETS buckets
  <species>/genes/NNN.json.gz              gene records, GENE_SHARDS shards
  <species>/region/<chromosome>.json.gz    genes on one chromosome sorted by start (region search):
                                           [[gene_id, start, end, name, phrase], ...]

Buckets and shards are chosen with 32-bit FNV-1a (UTF-8) modulo the count, mirrored in
assets/js/gene-function-summaries.js. A lookup bucket holds
  {"n": {exact lowercase name: [[gene_id, label, type], ...]},
   "c": {punctuation-free name: [[gene_id, label, type], ...]}}
where "c" only lists keys that differ from an exact key. A name with several genes is kept as a list
(the page offers a choice). A gene record is
  {"n": preferred name, "p": phrase, "s": sentence, "a": abstract,
   "e": evidence basis (lit | inferred | none | te | npc), "l": [chromosome, start, end, strand],
   "k": [[authors, year, title, journal, doi, pmid, category, reason], ...],
   "o": {species key: [[gene_id, name, phrase], ...]}}
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import re
import shutil
import sqlite3
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

FORMAT_VERSION = 2
LOOKUP_BUCKETS = 64
GENE_SHARDS = 128
DEFAULT_V2 = Path(__file__).resolve().parents[2] / "GeneAnnotation_v2"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "assets/data/gene-function-summaries"
NAME_LINE = re.compile(r"^- Name to use in summaries: `([^`]+)`", re.M)
ORTHOLOG_SOURCE = "Dias et al. 2025 PGSGS synteny"


@dataclass(frozen=True)
class SpeciesConfig:
    key: str
    label: str
    species: str
    assembly: str


SPECIES = (
    SpeciesConfig("maize", "Maize", "zea_mays", "B73 RefGen_v5 (Zm-B73-REFERENCE-NAM-5.0)"),
    SpeciesConfig("sorghum", "Sorghum", "sorghum_bicolor", "BTx623 v5.1 (Phytozome)"),
    SpeciesConfig("rice", "Rice", "oryza_sativa", "IRGSP-1.0"),
)
# Region search covers assembled chromosomes; unplaced scaffolds are left out.
CHROMOSOME = re.compile(r"^(chr)?0*(\d+)$", re.I)
# Template prompt families -> evidence basis; model-written summaries split on direct literature.
TEMPLATE_EVIDENCE = {"no_evidence_template": "none", "transposable_element_template": "te",
                     "non_protein_coding_template": "npc"}
KEY_OF = {c.species: c.key for c in SPECIES}

# Lower rank wins when one name reaches the same gene through several sources.
TYPE_RANK = {"gene model ID": 0, "other gene model ID": 1, "transcript ID": 2, "preferred name": 3,
             "gene symbol": 4, "synonym": 5, "literature name": 6, "NCBI gene ID": 7, "UniProt accession": 8,
             "RefSeq accession": 9, "identifier": 10}
ALIAS_TYPES = {"gene_symbol": "gene symbol", "maizegdb_locus_synonym": "synonym",
               "literature_mined_name": "literature name"}
NAMESPACE_TYPES = [
    (re.compile(r"^(B73_RefGen_v\d|B73_v5_pre_ab_gene_model|Zea_mays_B73_v5|Sorghum_bicolor_v[\d_]+|MSU_ID|MSU_locus|"
                r"RAP_locus|ancestor_identifier|curated_source_gene_model)$"), "other gene model ID"),
    (re.compile(r"^(canonical_transcript|RAP_transcript)$"), "transcript ID"),
    (re.compile(r"^(EntrezGene|locus_tag)$"), "NCBI gene ID"),
    (re.compile(r"^(UniProt|Uniprot/)"), "UniProt accession"),
    (re.compile(r"^RefSeq"), "RefSeq accession"),
    (re.compile(r"^(gene_symbol|locus_symbol)$"), "gene symbol"),
    (re.compile(r"^(locus_name|MaizeGDB_locus_name|gene_name|NCBI_gene_synonym|Uniprot_gn_trans_name|"
                r"EntrezGene_trans_name)$"), "synonym"),
]


def namespace_type(namespace: str) -> str:
    for pattern, typ in NAMESPACE_TYPES:
        if pattern.search(namespace or ""):
            return typ
    return "identifier"


def clean(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def norm_key(value: str) -> str:
    return clean(value).lower()


def compact_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def fnv1a(value: str) -> int:
    h = 0x811C9DC5
    for b in value.encode("utf-8"):
        h ^= b
        h = (h * 0x01000193) & 0xFFFFFFFF
    return h


def write_gz(path: Path, payload: object) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    data = gzip.compress(raw, compresslevel=9, mtime=0)  # mtime=0: byte-stable output
    path.write_bytes(data)
    return len(data)


def load_genes(conn: sqlite3.Connection, root: Path, species: str) -> dict[str, dict]:
    with_literature = {r[0] for r in conn.execute(
        "select distinct gene_id from paper_function_statements where species=? and active=1 and gene_id<>''",
        (species,))}
    genes = {}
    for gid, phrase, sentence, abstract, profile, chrom, start, end, strand in conn.execute(
            "select s.gene_id, s.function_phrase, s.function_sentence, s.annotation_abstract, s.synthesis_profile, "
            "g.chromosome, g.start, g.end, g.strand "
            "from gene_syntheses s join genes g on g.species=s.species and g.gene_id=s.gene_id "
            "where s.species=? and s.active=1 and coalesce(s.function_phrase,'')<>'' order by s.gene_id",
            (species,)):
        if gid in genes:
            raise SystemExit(f"more than one active summary for {species} {gid}")
        if profile in TEMPLATE_EVIDENCE:
            evidence = TEMPLATE_EVIDENCE[profile]
        elif profile == "direct_evidence_packet":
            evidence = "lit" if gid in with_literature else "inferred"
        else:
            raise SystemExit(f"unknown synthesis profile {profile!r} for {species} {gid}")
        genes[gid] = {"n": "", "p": clean(phrase), "s": clean(sentence), "a": (abstract or "").strip(),
                      "e": evidence}
        if chrom and start is not None and end is not None:
            genes[gid]["l"] = [str(chrom), int(start), int(end), strand or ""]
    for gid, path in conn.execute("select gene_id, packet_path from evidence_packets where species=?", (species,)):
        if gid not in genes or not path:
            continue
        p = Path(path) if Path(path).is_absolute() else root / path
        m = NAME_LINE.search(p.read_text(encoding="utf-8")[:4000]) if p.exists() else None
        if m and m.group(1).lower() != gid.lower():
            genes[gid]["n"] = m.group(1)
    return genes


def load_names(conn: sqlite3.Connection, species: str, genes: dict[str, dict]) -> dict[str, dict[str, tuple]]:
    """norm name -> {gene_id: (label, type)}; QC-rejected/ambiguous names never resolve (as the export)."""
    qc: dict[str, set[str] | None] = {}
    for name_norm, decision, accepted in conn.execute(
            "select name_norm, decision, accepted_gene_ids_json from gene_mapping_qc_decisions where species=?",
            (species,)):
        qc[norm_key(name_norm)] = set(json.loads(accepted or "[]")) if decision == "accepted_alias" else None

    def allowed(name: str, gid: str) -> bool:
        k = norm_key(name)
        return k not in qc or (qc[k] is not None and gid in qc[k])

    raw: list[tuple[str, str, str]] = []
    for gid, g in genes.items():
        raw.append((gid, gid, "gene model ID"))
        if g["n"]:
            raw.append((g["n"], gid, "preferred name"))
    for gid, ident, ns in conn.execute("select gene_id, identifier, namespace from gene_identifiers where species=? "
                                       "and coalesce(identifier,'')<>''", (species,)):
        raw.append((ident, gid, namespace_type(ns)))
    for to_gid, from_gid, ns in conn.execute("select to_gene_id, from_gene_id, from_namespace from gene_model_mappings "
                                             "where species=? and active=1 and coalesce(from_gene_id,'')<>''",
                                             (species,)):
        raw.append((from_gid, to_gid, namespace_type(ns)))
    for gid, alias, atype in conn.execute("select gene_id, alias, alias_type from gene_aliases where species=?",
                                          (species,)):
        if allowed(alias, gid):
            raw.append((alias, gid, ALIAS_TYPES.get(atype, "synonym")))
    for gid, name in conn.execute("select gene_id, name from gene_name_mappings where species=? and active=1 "
                                  "and mapping_status='unique' and coalesce(gene_id,'')<>''", (species,)):
        if allowed(name, gid):
            raw.append((name, gid, "literature name"))

    names: dict[str, dict[str, tuple]] = defaultdict(dict)
    for label, gid, typ in raw:
        label = clean(label)
        if gid not in genes or not label or not compact_key(label):
            continue
        k = norm_key(label)
        prev = names[k].get(gid)
        cand = (label, typ)
        if prev is None or (TYPE_RANK[typ], len(label), label) < (TYPE_RANK[prev[1]], len(prev[0]), prev[0]):
            names[k][gid] = cand
    return names


def load_key_papers(conn: sqlite3.Connection, species: str, authors: dict[str, dict]) -> dict[str, list]:
    out: dict[str, list] = defaultdict(list)
    for gid, pid, pmid, method, category, reason, title, year, journal, doi in conn.execute(
            "select k.gene_id, k.paper_id, k.pmid, k.method, k.category, k.reason, p.title, p.publication_year, "
            "p.journal, p.doi from gene_key_papers k left join papers p on p.paper_id=k.paper_id "
            "where k.species=? order by k.gene_id, k.rank", (species,)):
        a = authors.get(pid) or {}
        n = int(a.get("n_authors") or 0)
        if n == 1:
            who = a["first_author"]
        elif n == 2 and a.get("second_author"):
            who = f"{a['first_author']} and {a['second_author']}"
        elif n >= 2:
            who = f"{a['first_author']} et al."
        else:
            who = ""
        out[gid].append([who, year or "", clean(title).rstrip("."), clean(journal), clean(doi),
                         str(pmid or ""), category or "", clean(reason) if method == "luna" else ""])
    return out


def load_orthologs(conn: sqlite3.Connection, all_genes: dict[str, dict[str, dict]]) -> dict[tuple, dict]:
    out: dict[tuple, dict] = defaultdict(lambda: defaultdict(list))
    for src_sp, src, tgt_sp, tgt in conn.execute(
            "select source_species, source_gene_id, target_species, target_gene_id from gene_orthology_edges "
            "where relationship_type='syntenic_ortholog' and source=? order by 1,2,3,4", (ORTHOLOG_SOURCE,)):
        if src_sp not in KEY_OF or tgt_sp not in KEY_OF or src_sp == tgt_sp:
            continue
        if src not in all_genes[src_sp] or tgt not in all_genes[tgt_sp]:
            continue
        t = all_genes[tgt_sp][tgt]
        entry = [tgt, t["n"], t["p"]]
        if entry not in out[(src_sp, src)][KEY_OF[tgt_sp]]:
            out[(src_sp, src)][KEY_OF[tgt_sp]].append(entry)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--v2-root", type=Path, default=DEFAULT_V2)
    ap.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = ap.parse_args()
    root = args.v2_root.resolve()
    conn = sqlite3.connect(f"file:{root / 'data/processed/geneannot_v2.sqlite'}?mode=ro", uri=True, timeout=60)
    with (root / "data/processed/paper_authors/key_paper_authors.tsv").open() as fh:
        authors = {r["paper_id"]: r for r in csv.DictReader(fh, delimiter="\t")}
    run = conn.execute("select run_id, applied_at from gene_key_paper_runs order by applied_at desc limit 1").fetchone()

    all_genes = {c.species: load_genes(conn, root, c.species) for c in SPECIES}
    orthologs = load_orthologs(conn, all_genes)

    out = args.output_dir
    if out.exists():
        shutil.rmtree(out)
    meta_species = []
    for c in SPECIES:
        genes = all_genes[c.species]
        papers = load_key_papers(conn, c.species, authors)
        for gid, g in genes.items():
            if papers.get(gid):
                g["k"] = papers[gid]
            if (c.species, gid) in orthologs:
                g["o"] = dict(orthologs[(c.species, gid)])
        shards: dict[int, dict] = defaultdict(dict)
        for gid, g in genes.items():
            shards[fnv1a(gid.lower()) % GENE_SHARDS][gid] = {k: v for k, v in g.items() if v}
        gene_bytes = sum(write_gz(out / c.key / "genes" / f"{i:03d}.json.gz", recs) for i, recs in shards.items())

        names = load_names(conn, c.species, genes)
        by_compact: dict[str, dict[str, tuple]] = defaultdict(dict)
        for k, gmap in names.items():
            for gid, v in gmap.items():
                by_compact[compact_key(k)].setdefault(gid, v)
        buckets: dict[int, dict] = defaultdict(lambda: {"n": {}, "c": {}})
        for k, gmap in names.items():
            buckets[fnv1a(compact_key(k)) % LOOKUP_BUCKETS]["n"][k] = sorted([gid, *v] for gid, v in gmap.items())
        for ck, gmap in by_compact.items():
            if ck not in names or set(names[ck]) != set(gmap):
                buckets[fnv1a(ck) % LOOKUP_BUCKETS]["c"][ck] = sorted([gid, *v] for gid, v in gmap.items())
        lookup_bytes = sum(write_gz(out / c.key / "lookup" / f"{i:02d}.json.gz", b) for i, b in buckets.items())

        by_chrom: dict[str, list] = defaultdict(list)
        for gid, g in genes.items():
            if g.get("l") and CHROMOSOME.match(g["l"][0]):
                chrom, start, end, _ = g["l"]
                by_chrom[chrom].append([gid, start, end, g["n"], g["p"]])
        chromosomes = []
        region_bytes = 0
        for chrom in sorted(by_chrom, key=lambda x: int(CHROMOSOME.match(x).group(2))):
            rows = sorted(by_chrom[chrom], key=lambda r: (r[1], r[2], r[0]))
            region_bytes += write_gz(out / c.key / "region" / f"{chrom}.json.gz", rows)
            chromosomes.append({"name": chrom, "label": f"Chr{int(CHROMOSOME.match(chrom).group(2)):02d}",
                                "genes": len(rows), "max_end": max(r[2] for r in rows)})
        ambiguous = sum(1 for g in names.values() if len(g) > 1)
        meta = {"key": c.key, "label": c.label, "species": c.species, "gene_count": len(genes),
                "lookup_count": len(names), "ambiguous_names": ambiguous,
                "genes_with_key_papers": sum(1 for g in genes.values() if g.get("k")),
                "genes_with_orthologs": sum(1 for g in genes.values() if g.get("o")),
                "gene_shards": len(shards), "lookup_buckets": len(buckets), "assembly": c.assembly,
                "chromosomes": chromosomes, "genes_without_chromosome_position":
                    sum(1 for g in genes.values() if not (g.get("l") and CHROMOSOME.match(g["l"][0]))),
                "gene_bytes": gene_bytes, "lookup_bytes": lookup_bytes, "region_bytes": region_bytes}
        meta_species.append(meta)
        print(f"{c.label}: {meta['gene_count']} genes, {meta['lookup_count']} names ({ambiguous} ambiguous), "
              f"{meta['genes_with_key_papers']} with key papers, {meta['genes_with_orthologs']} with orthologs; "
              f"{len(chromosomes)} chromosomes ({meta['genes_without_chromosome_position']} genes unplaced); "
              f"{(gene_bytes + lookup_bytes + region_bytes) / 1e6:.1f} MB gz")
    metadata = {"format_version": FORMAT_VERSION, "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "source": "GeneAnnotation v2", "key_paper_run": run[0] if run else None,
                "ortholog_source": ORTHOLOG_SOURCE, "lookup_buckets": LOOKUP_BUCKETS, "gene_shards": GENE_SHARDS,
                "species": meta_species}
    (out / "metadata.json").write_text(json.dumps(metadata, indent=1) + "\n")
    total = sum(m["gene_bytes"] + m["lookup_bytes"] + m["region_bytes"] for m in meta_species)
    print(f"total {total / 1e6:.1f} MB in {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
