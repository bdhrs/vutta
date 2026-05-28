# Lessons: 20260528_scan_cst_xml

## 1 — CST XML has two distinct verse-numbering styles

**What:** 104 of the 208 gāthā-containing files use "hangnum" style (`<p rend="hangnum" n="N">` before each verse). The other 104 use "bodytext" style (`<p rend="bodytext" n="N">` on the prose paragraph; `gatha1` signals a new verse). Original code handled only hangnum — half the corpus produced no output.

**Fix:** Track `last_paranum` and a `paranum_fresh` flag. Both styles update the same slot; `gatha1` consumes it and clears the flag.

**Rule for future XML work:** Always sample files from multiple books before assuming a single numbering scheme. The CST corpus mixes conventions across the three Piṭakas.

---

## 2 — Scan each dvi-pāda independently, not the whole verse joined

**What:** Joining all gatha lines as one string and calling `scan()` once produced ~6% unmatched on Dhammapada because 6-pāda verses don't fit 4-pāda metre profiles. Scanning each gatha element independently (one `scan()` call per gatha line) raised the Dhp match rate to 96.6%.

**Rule:** When CST XML splits a verse into gatha1/2/3/last, treat each element as an independently scannable unit (typically one dvi-pāda). Pass the element text to `scan()` directly; do not join across elements before scanning.

---

## 3 — `gathalast` does not reliably close a verse; add an `in_verse` guard

**What:** Some files have "uddāna" gāthās (mnemonic verse summaries) immediately after the final `gathalast` of a chapter, with no intervening `hangnum` or new `gatha1`. Without an `in_verse` flag, stray `gatha2`/`gatha3`/`gathalast` lines bled into the previous verse's buffer (surfaced as Dhp v.423 appearing twice with two different paragraphs).

**Fix:** Reset `in_verse` on `gathalast`; ignore stray `gatha2/3/last` when `in_verse` is False. A new `gatha1` with `paranum_fresh=False` gets paranum `"?"`, making the orphan visible without corrupting the preceding verse.

---

## 4 — Never hardcode absolute paths with a username

**What:** `CST_ROMN_DIR = Path("/home/bodhirasa/…")` was written as a module-level constant during development. This breaks for any other user and would have been embarrassing to share with Ven. Ānandajoti Bhikkhu.

**Fix:** Replaced with `_cst_romn_dir()` reading `VUTTA_CST_DIR` from the `.env` / environment, with a clear error message if unset. Added to `.env.example` alongside `VUTTA_CANON_DB`.

**Rule:** Any path that points outside the repo must come from an env var. No usernames in code.

---

## 5 — Symbol rendering: verify in every target editor before committing

**What:** `⏑` (U+23D1 METRICAL BREVE) was the initial choice for light syllables. It rendered correctly in the terminal but double-width in Zed (ZedMono has no native glyph; system fallback font is wide), breaking alignment in the output `.md` files.

**Fix:** Switched to `·` (U+00B7 MIDDLE DOT) + `–` (U+2013 EN DASH). Both are in Latin-1 Supplement, present in every monospace font, and render single-width everywhere: terminal, Obsidian, Zed, VS Code, GitHub.

**Rule:** For output symbols that must align in monospace, test in all three of: terminal, Obsidian, Zed. Prefer characters from Latin-1 Supplement (U+0080–U+00FF) over specialised Unicode blocks.

---

## 6 — Global symbol replacement can hit prose as well as code

**What:** When replacing `¯` → `–` across the codebase, the substitute also changed em dashes in prose comments in `match.py` to en dashes, producing minor typography errors (e.g. `"resolution — see below"` became `"resolution – see below"`).

**Rule:** Run symbol replacements on pattern strings only (metres.py, weight.py constants), not repository-wide. Review prose-heavy files manually afterward.
