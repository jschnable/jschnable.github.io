#!/usr/bin/env python3
"""Generate resized copies of site images under images/optimized."""
from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

from PIL import Image, ImageOps

RASTER_EXTENSIONS = {".jpg", ".jpeg", ".jfif", ".png"}

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTENT_GLOB = "*.{md,html,liquid,yml,scss}"
OUTPUT_DIR = REPO_ROOT / "images" / "optimized"
WIDTH_PATTERN = re.compile(r"width\s*[:=]\s*\"?(\d{1,4})(?=\s*(?:px|\"|$))")


@dataclass
class ImageRecord:
  source_web_path: str
  source_file: Path
  dest_file: Path
  width: int
  height: int
  size_bytes: int
  target_scale: float
  display_width: Optional[int]

  @property
  def dest_web_path(self) -> str:
    rel = self.dest_file.relative_to(REPO_ROOT)
    return f"/{str(rel)}".replace("\\", "/")

  def new_dimensions(self) -> tuple[int, int]:
    if self.target_scale >= 1:
      return self.width, self.height
    new_w = max(1, int(round(self.width * self.target_scale)))
    new_h = max(1, int(round(self.height * self.target_scale)))
    return new_w, new_h


def run_rg(args: Iterable[str]) -> str:
  """Run ripgrep with a fixed working directory."""
  full_cmd = ["rg", "--hidden", "--smart-case"] + list(args)
  result = subprocess.run(
    full_cmd,
    cwd=REPO_ROOT,
    check=False,
    capture_output=True,
    text=True,
  )
  if result.returncode not in (0, 1):
    raise RuntimeError(result.stderr)
  return result.stdout


def collect_web_paths() -> List[str]:
  raw = run_rg(["-o", "/images/[^\"') ]+", f"-g{CONTENT_GLOB}", "--no-filename"])
  paths = sorted({line.strip() for line in raw.splitlines() if line.strip()})
  return paths


def detect_display_width(web_path: str) -> Optional[int]:
  args = ["--fixed-strings", "-n", web_path, f"-g{CONTENT_GLOB}", "--no-heading"]
  raw = run_rg(args)
  widths: List[int] = []
  for line in raw.splitlines():
    parts = line.split(":", 2)
    if len(parts) < 3:
      continue
    text = parts[2]
    for match in WIDTH_PATTERN.findall(text):
      try:
        widths.append(int(match))
      except ValueError:
        continue
  return max(widths) if widths else None


def categorize(web_path: str) -> str:
  if "People_Images" in web_path:
    return "people"
  if "News_Images" in web_path:
    return "news"
  if "Front_Page_Images" in web_path:
    return "front"
  if "Science_Images" in web_path:
    return "science"
  return "other"


def compute_scale(web_path: str, width: int, height: int, display_width: Optional[int]) -> float:
  longest = max(width, height)
  category = categorize(web_path)
  if category == "people":
    limit = 800
    return min(1.0, limit / longest)

  if category == "news":
    display = display_width or min(width, 800)
    limit_width = min(max(display * 2, display), 1600)
    scale = min(1.0, limit_width / width)
    limit_longest = 1600
    return min(scale, limit_longest / longest, 1.0)

  if category == "front":
    limit = 1800
    return min(1.0, limit / longest)

  if category == "science":
    limit = 1200
    return min(1.0, limit / longest)

  display = display_width or min(width, 1000)
  limit_width = min(max(display * 2, display), 1800)
  scale = min(1.0, limit_width / width)
  limit_longest = 1800
  return min(scale, limit_longest / longest, 1.0)


def ensure_output_root() -> None:
  if OUTPUT_DIR.exists():
    shutil.rmtree(OUTPUT_DIR)
  OUTPUT_DIR.mkdir(parents=True)


def process_image(record: ImageRecord) -> tuple[int, int]:
  suffix = record.source_file.suffix.lower()
  if suffix in {".jpg", ".jpeg", ".jfif", ".png"}:
    with Image.open(record.source_file) as img:
      img = ImageOps.exif_transpose(img)
      target_w, target_h = record.new_dimensions()
      if target_w == img.width and target_h == img.height:
        record.dest_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(record.source_file, record.dest_file)
        return img.width, img.height
      img = img.resize((target_w, target_h), Image.LANCZOS)
      save_kwargs = {}
      if suffix in {".jpg", ".jpeg", ".jfif"}:
        if img.mode not in ("RGB", "L"):
          img = img.convert("RGB")
        save_kwargs = {"format": "JPEG", "quality": 85, "optimize": True, "progressive": True}
      elif suffix == ".png":
        save_kwargs = {"optimize": True}
      record.dest_file.parent.mkdir(parents=True, exist_ok=True)
      img.save(record.dest_file, **save_kwargs)
      return target_w, target_h
  record.dest_file.parent.mkdir(parents=True, exist_ok=True)
  shutil.copy2(record.source_file, record.dest_file)
  return record.width, record.height


def main() -> None:
  ensure_output_root()
  web_paths = collect_web_paths()
  records: List[ImageRecord] = []
  for web_path in web_paths:
    source_rel = web_path.lstrip("/")
    source_file = (REPO_ROOT / source_rel).resolve()
    if not source_file.exists() or source_file.is_dir():
      continue
    dest_file = OUTPUT_DIR / Path(source_rel).relative_to("images")
    suffix = source_file.suffix.lower()
    display_width = detect_display_width(web_path)

    if suffix in RASTER_EXTENSIONS:
      with Image.open(source_file) as probe:
        probe = ImageOps.exif_transpose(probe)
        width, height = probe.size
      scale = compute_scale(web_path, width, height, display_width)
    else:
      width = height = 0
      scale = 1.0

    record = ImageRecord(
      source_web_path=web_path,
      source_file=source_file,
      dest_file=dest_file,
      width=width,
      height=height,
      size_bytes=source_file.stat().st_size,
      target_scale=scale,
      display_width=display_width,
    )
    records.append(record)

  rows: List[str] = []
  header = "web_path\toriginal_size\toriginal_dims\tnew_size\tnew_dims\tdisplay_width"
  rows.append(header)

  for record in records:
    new_w, new_h = record.new_dimensions()
    process_image(record)
    new_size = record.dest_file.stat().st_size if record.dest_file.exists() else 0
    original_dims = f"{record.width}x{record.height}" if record.width and record.height else ""
    new_dims = f"{new_w}x{new_h}" if new_w and new_h else ""
    row = "\t".join(
      [
        record.dest_web_path,
        str(record.size_bytes),
        original_dims,
        str(new_size),
        new_dims,
        str(record.display_width or ""),
      ]
    )
    rows.append(row)

  inventory_path = REPO_ROOT / "docs" / "image_inventory_optimized.tsv"
  inventory_path.write_text("\n".join(rows))


if __name__ == "__main__":
  main()
