---
layout: page
title: Software
---

The Schnable Lab publishes software that supports high-throughput phenotyping, comparative genomics, and data wrangling for large-scale field experiments. Most active development lives in GitHub repositories under the lab and collaborator accounts; this page curates the projects we rely on everyday and points you toward install and contribution resources.

## Phenotyping & Field Automation

- **SLHTP – Schnable Lab High Throughput Phenotyping**  
  GitHub: [alejandropages/SLHTP](https://github.com/alejandropages/SLHTP)  
  Python toolkit that powers our bean, ear, and kernel image pipelines. The repo bundles the `beanpheno`, `earpheno`, and `kernelpheno` modules, along with notebooks for reproducing the analyses described in our phenotyping publications.
- **PhytoMorph integrations**  
  Internal notebooks and scripts that wrap [PhytoMorph](https://www.biorxiv.org/content/10.1101/384974v1) for automated ear feature extraction. Reach out to the phenotyping subgroup for access or to collaborate on new trait extractors.

## Comparative Genomics Utilities

- **Pan-grass synteny workflows**  
  Supporting scripts for the [pan-grass syntenic gene sets](https://doi.org/10.6084/m9.figshare.7926674.v1) consolidate LastZ alignments, QuotaAlign blocks, and polishing notebooks. The current production notebooks are in the lab’s internal `synteny-tools` repo; contact James for access while we prep the public release.
- **Paleopolyploidy map tools**  
  Lightweight scripts that generate the plant paleopolyploidy visualisations published on CoGePedia. These live in the `paleopolyploidy-maps` repo and depend on standard R tidyverse packages.

## Getting Started & Contributing

1. Clone the target repository and follow the README to install Python/R dependencies. Most projects expect `conda` environments; phenotyping code additionally requires OpenCV and PyTorch.
2. Open issues for bugs or feature requests before submitting a pull request. We follow the same review expectations outlined in [AGENTS.md](/AGENTS.md).
3. Document new scripts with example commands and add small sample data under a `tests/` or `examples/` directory so other lab members can reproduce your results quickly.

Looking for published datasets, imagery, or derived gene lists? Browse the [Published Datasets and Code Repositories](/data/) page for DOI-linked archives that complement these tools.
