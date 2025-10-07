#!/usr/bin/env python3
"""Normalize people pages to use the person layout and clean legacy blocks."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PEOPLE_DIR = ROOT / "peoplepages"

IMAGE_PATTERN = re.compile(r"\]\(/images/(?:optimized/)?People_Images/")
ORCID_PATTERN = re.compile(r"ORCID", re.IGNORECASE)
PUB_INCLUDE_PATTERN = re.compile(r"\{\%\s*include\s+pub_lists/")


def split_front_matter(text: str) -> tuple[str, str]:
  if text.startswith("---\n"):
    end = text.find("\n---\n", 4)
    if end != -1:
      fm = text[4:end]
      body = text[end + 5 :]
      return fm, body
  raise ValueError("Front matter not found")


def normalize_page(path: Path) -> None:
  raw = path.read_text()
  try:
    front_matter, body = split_front_matter(raw)
  except ValueError:
    print(f"Skipping {path} (missing front matter)")
    return

  # Force layout to person
  lines = [line for line in front_matter.splitlines() if not line.startswith("layout:")]
  lines.insert(0, "layout: person")
  front_matter = "\n".join(lines)

  cleaned_lines = []
  headshot_removed = False
  for line in body.splitlines():
    if not headshot_removed and IMAGE_PATTERN.search(line):
      headshot_removed = True
      continue
    if PUB_INCLUDE_PATTERN.search(line):
      continue
    if ORCID_PATTERN.search(line) and line.strip().startswith("**"):
      # drop bold ORCID summary lines
      continue
    if "Papers As" in line or "Schnable Lab Related Papers" in line:
      continue
    cleaned_lines.append(line)

  cleaned_body = "\n".join(cleaned_lines).strip("\n")
  cleaned_body = cleaned_body.lstrip()

  new_text = "---\n" + front_matter + "\n---\n\n" + cleaned_body.strip("\n") + ("\n" if cleaned_body else "")
  path.write_text(new_text)


def main() -> None:
  for page in PEOPLE_DIR.glob("*.md"):
    normalize_page(page)


if __name__ == "__main__":
  main()
