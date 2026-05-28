# Plan: Scan every CST XML file with gāthā tags

## Architecture Decisions
- New module `vutta/scan_cst_xml.py`. Source is XML, not SQLite — keep
  separate from `scan_book*`.
- UTF-16 decode → `xml.etree.ElementTree.fromstring`. Use ET's tree walk
  (not regex) so chapter/hangnum/gatha state is unambiguous.
- Reuse `vutta.scan.scan` per verse. On any exception emit raw text +
  `metre: unknown` line.
- Output filename = source basename with `.xml` replaced by `.md`. No
  friendly-name mapping — 102+ files would need an unmaintainable lookup.
- Export `CST_ROMN_DIR` constant from the module for future XML tools.

## Phase 1 — XML reading + verse extraction
- [x] Add `CST_ROMN_DIR` constant and `discover_xml_files()` listing every
      `*.xml` under it.
      → verified: 217 paths discovered.
- [x] `read_xml(path) -> str`: read bytes, decode UTF-16.
      → verified: gatha1 present in Dhp.
- [x] `iter_verses(xml_str) -> Iterator[(vagga, paranum, text)]` walking
      the ET tree, tracking chapter + hangnum, joining gatha1/2/3/last.
      Strip `<note>` content and `<pb/>`.
      → verified: first verse paranum=="1", text starts "Manopubbaṅgamā".

## Phase 2 — Rendering + CLI
- [x] `render_file(path) -> str | None`: build markdown; return None if
      no verses found. Title H1 from `<head rend="book">`, chapter H1,
      `## v.N` per verse, fenced block with `scan(text)` result; on
      exception, raw text + `metre: unknown`.
      → verified: Dhp v.1 renders correctly.
- [x] CLI `vutta.scan_cst_xml`:
      - No args → process every file under CST_ROMN_DIR.
      - Positional args → process just those (paths or basenames).
      - `--out-dir` defaults to `output/cst/`.
      → verified: single-file run writes s0502m.mul.md with 423 verses.

## Phase 3 — Full run + tech.md note
- [x] Run across all 217 files.
      → verified: 102 files written, 58,586 verses total, no tracebacks.
      115 files had no gāthās and were skipped.
- [x] Add `CST_ROMN_DIR` path to `kamma/tech.md` under Resources.
      → verified: grep confirms path present.
