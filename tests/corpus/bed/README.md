# BED corpus

100 BED fixtures synthesized from real-world bug reports across public issue
trackers (bedtools, pybedtools, htslib, deepTools, bedops) and the
Niu, Denisko, Hoffman 2022 BED-tool survey. Each fixture is minimal (avg ~540
bytes), cites its source URL inline via `# Source:`, and describes the pathology
it exhibits via `# Symptom:`. Personal identifiers from the original reports
have been replaced by synthetic equivalents.

## Buckets

Bucketed by validator behavior under the two `--spec` modes:

- **`universal_bad/`** (48): validator rejects in both `--spec ucsc` and `--spec hts`.
  Universal malformations: block invariants, non-integer coords, mixed line
  separators, trailing-tab phantom columns, etc.
- **`hts_only_bad/`** (22): passes `--spec ucsc`, rejects `--spec hts`.
  Spec deviations hts-specs prohibits but UCSC tolerates or is silent on
  (RefSeq accession chrom names, score outside 0-1000, browser/track header
  lines, etc.).
- **`good/`** (30): passes in both modes. Includes spec-legal edge cases
  (zero-length features, dot strand, BED N+M with custom columns) and
  fixtures downstream tools reject but the spec permits (Ensembl no-chr
  prefix, mixed chr/non-chr prefix, out-of-order records, etc.).

## Browsing

```
ls universal_bad/                              # list pathologies
head -3 universal_bad/<file>.bed               # source + symptom + first data line
```
