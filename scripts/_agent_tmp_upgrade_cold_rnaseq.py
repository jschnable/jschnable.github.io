#!/usr/bin/env python3
from pathlib import Path
path = Path("_data/publications.yml")
text = path.read_text()
old = """  status: accepted
  type: article
  journal: BMC Research Notes
  notes:
  - Research Square: 10.21203/rs.3.rs-9620448/v1
  first_author_is_lab_member: true
  lab_author_count: 5
  tags:
  - sorghum
  - millets
  - transcriptomics
  - stress-tolerance
  - data-release
- id: 2026-m-hyperspectral-phenotyping-senescence"""
new = """  status: published
  type: article
  journal: BMC Research Notes
  doi: 10.1186/s13104-026-08007-x
  url: https://doi.org/10.1186/s13104-026-08007-x
  notes:
  - Research Square: 10.21203/rs.3.rs-9620448/v1
  first_author_is_lab_member: true
  lab_author_count: 5
  tags:
  - sorghum
  - millets
  - transcriptomics
  - stress-tolerance
  - data-release
- id: 2026-m-hyperspectral-phenotyping-senescence"""
# Anchor to cold RNA-seq entry to avoid accidental matches
marker = "2026-h-rnaseq-resource-cold-responses"
idx = text.find(marker)
if idx < 0:
    raise SystemExit("Cold RNA-seq entry id not found")
# Find old block after marker
rel = text.find(old, idx)
if rel < 0:
    raise SystemExit("OLD YML status block not found after cold RNA-seq id")
# Ensure this is the cold entry (hyperspectral follows)
if text.count(old) != 1:
    raise SystemExit(f"Expected 1 YML match, found {text.count(old)}")
text = text[:rel] + new + text[rel+len(old):]
path.write_text(text)
chunk = text[idx:idx+800]
print(chunk)
if "status: published" not in chunk:
    raise SystemExit("status not published")
if "10.1186/s13104-026-08007-x" not in chunk:
    raise SystemExit("publisher DOI missing from entry")
# Primary doi field present (not only in notes)
if "doi: 10.1186/s13104-026-08007-x" not in chunk:
    raise SystemExit("doi field missing")
print("OK size=", path.stat().st_size)
