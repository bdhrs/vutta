# Spec: Scan every CST XML file with gāthā tags

## Overview
Add a CLI that walks every XML file in the CST romn directory, extracts all
verses (gāthā), and writes one Ānandajoti-style aligned .md per source file
to `output/cst/`. Files with no gāthā tags are skipped.

## CST XML source location
`/home/bodhirasa/MyFiles/3_Active/dpd-db/resources/dpd_submodules/cst/romn/`

Recorded in `kamma/tech.md` (Resources section).

## What it should do
- Iterate every `*.xml` in the CST romn directory.
- For each file:
  - Read bytes, decode as UTF-16 (with BOM).
  - Parse with ElementTree.
  - Track chapter (`<head rend="chapter">`) and verse number
    (`<p rend="hangnum" n="N">`).
  - Collect text from consecutive `<p rend="gatha1|gatha2|gatha3|gathalast">`
    paragraphs. Strip `<pb .../>`, `<note>...</note>`, other inline markup.
  - If the file contains no gāthā paragraphs, skip it (no output file).
  - Otherwise run `vutta.scan` on each verse and write an Ānandajoti-style
    markdown.
  - On per-verse scan errors: emit the raw text and `metre: unknown`.
- Output: `output/cst/<basename-without-.xml>.md` — e.g.
  `output/cst/s0502m.mul.md`.

## Assumptions & uncertainties
- Verse tags are exactly `gatha1`, `gatha2`, `gatha3`, `gathalast` across
  all files (verified on Dhp; assumed uniform across the CST set).
- All files are UTF-16-encoded with BOM.
- ~208 files contain gāthā tags (preliminary count). Final number may
  shift slightly depending on parse success.
- Commentaries and ṭīkās contain embedded gāthās too; user wants those
  scanned alongside the mūla — the same scansion engine applies.

## Constraints
- Pure offline; reuse `vutta.scan`. No fork of scansion logic.
- Do not mutate CST source files.
- One `.md` per source XML, basename mirrors source.

## How we'll know it's done
- Running the CLI with no args writes ~208 .md files under `output/cst/`.
- Spot-check Dhammapada: `output/cst/s0502m.mul.md` first verse matches
  existing `scan_book_pretty s0502m_mul` output for v.1.
- No tracebacks; per-verse failures appear as `metre: unknown`.

## What's not included
- Aggregate/summary file across books.
- Re-scanning via the SQLite DB.
