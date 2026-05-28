# Review

## Thread
- **ID:** 20260528_scan_cst_xml
- **Objective:** Scan every CST XML file containing gāthā tags; write one aligned .md per book to `output/cst/`; replace prosodic symbols; consolidate output paths.

## Files Changed
- `vutta/scan_cst_xml.py` (new) — XML reader + verse extractor + CLI
- `vutta/weight.py` — LIGHT/HEAVY symbols changed to `·`/`–`
- `vutta/_data/metres.py` — metre pattern strings updated to new symbols
- `vutta/match.py` — comments updated; logic unchanged (uses imported LIGHT/HEAVY)
- `vutta/display.py` — docstring updated
- `vutta/_data/exceptions.py` — comment updated
- `vutta/tests/test_golden.py` — expected weight strings updated
- `vutta/scan_book.py` — default output path → `output/tsv/`
- `vutta/scan_book_pretty.py` — default output path → `output/pretty/`
- `vutta/summarize_tsv.py` — default input path → `output/tsv/`
- `.gitignore` — `data/output/` + `data/scratch/` → `output/`
- `README.md` — symbols, example output, layout tree updated
- `kamma/tech.md` — CST path recorded; symbols updated

## Findings
| # | Severity | Location | What | Fix |
|---|----------|----------|------|-----|
| 1 | minor | `weight.py:13` | Docstring said `'−'` (U+2212) for heavy, actual HEAVY is `–` (U+2013) | Fixed |
| 2 | minor | `scan_cst_xml.py:150` | Error label said `metrum:` instead of `metre:` | Fixed |
| 3 | nit | `scan_cst_xml.py:24` | `CST_ROMN_DIR` is an absolute path with username; not portable | Acceptable for personal project |
| 4 | nit | `scan_cst_xml.py:121` | `_book_title` parses XML a second time; minor inefficiency | Acceptable given file sizes |

## Fixes Applied
- Corrected `weight.py` docstring symbol from `−` → `–`
- Corrected `scan_cst_xml.py` error label from `metrum:` → `metre:`
- Updated `README.md` and `kamma/tech.md` stale symbols (˘/¯) found during review

## Test Evidence
- `uv run -m vutta.tests.test_golden` → all 3 cases pass (✓)
- `uv run -m vutta.scan_cst_xml` → 208 files, 82,172 verses, no tracebacks
- `uv run -m vutta.scan "Bahū devā..."` → correct `·`/`–` output, Siloka identified

## Verdict
PASSED
- Review date: 2026-05-28
- Reviewer: kamma (inline)
