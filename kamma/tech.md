# Tech Notes

## Tools & Platforms

- **Python 3.11+** (project targets 3.11, develops on 3.13).
- **`uv`** for environment + script running (`uv run -m vutta.<module>`).
- **SQLite** for the canonical text source (`tipitaka-translation-data.db`
  from the sibling `dpd-db` project — read-only).
- **Linux** is the primary platform. macOS should work; Windows untested.
- No web framework, no network calls, no daemons. Pure CPU; everything
  runs in seconds for the entire Pāḷi canon.

## Who This Is For

Pāḷi students, Indologists, and monastic / lay practitioners reading verse
texts. Assumes basic familiarity with:

- IAST diacritics (`ā`, `ī`, `ū`, `ṃ`, `ṅ`, `ñ`, `ṭ`, `ḍ`, `ṇ`, `ḷ`).
- The concept of *garu* / *lahu* (heavy / light syllables) and the gaṇa system
  — though the algorithm encodes these rules so the user doesn't have to
  apply them manually.
- Markdown for reading the pretty output.

## Constraints

1. **Canon DB is read-only.** The tool depends on `dpd-db`'s SQLite of the
   CST Tipiṭaka but never writes to it. Path is configured via
   `VUTTA_CANON_DB` in `.env` (or `VICAYA_CANON_DB` as fallback).
2. **Output must align in monospace fonts.** Symbols are chosen so the scan
   line aligns perfectly with the verse line in any monospace context —
   terminal, Obsidian, VS Code, GitHub. Specifically: `·` (U+00B7 MIDDLE DOT)
   for light and `–` (U+2013 EN DASH) for heavy — both mid-cell height,
   single-width in all common monospace fonts.
3. **No external network access** at runtime. Everything ships in-repo
   (digraph table, metre profiles, sarabhatti wordlist, non-position
   conjunct stems).
4. **Pāḷi orthography is preserved** in the displayed verse line. Prosody
   substitutions (sarabhatti, br-exception) are applied only for the
   metrical scansion, with a position map that lets the scan marks land on
   the correct original-spelling columns.

## Resources

- **dpd-db** (sibling repo): canonical text SQLite, book-code lookup,
  potentially a compound table for future pādayuga-seam handling.
- **Ven. Ānandajoti Bhikkhu's prosody corpus** (in the user's Calibre
  library): *Vuttodaya — The Composition of Metre*, *Pāli Prosody: Texts
  and Studies*, *Main Metres in the Pali Canon*, *Metre Tables*, *Studies
  in Buddhadatta's Prosody*. Primary reference for algorithm design.
- **A.K. Warder, *Pali Metre*** (PTS): classical academic study; Ānandajoti
  improves on it where they differ.
- **Vicaya** (sibling research workflow): companion project for research
  notes; the `pali-prosody-study-guide.md` note in the Vicaya vault is the
  pedagogical reference for what algorithms *should* implement.
- **CST XML source** (raw Tipiṭaka TEI/XML):
  `/home/bodhirasa/MyFiles/3_Active/dpd-db/resources/dpd_submodules/cst/romn/`
  217 UTF-16-encoded XML files covering the full Tipiṭaka. Verse paragraphs
  use `rend="gatha1|gatha2|gatha3|gathalast"`. Scanned by `vutta.scan_cst_xml`.

## What the Output Looks Like

### Single-verse CLI

```
· –  – –  · –  –  –
bahū devā manussā ca
–  · – ·  ·–  · –
maṅgalāni acintayuṃ
––  ·  – –  –  –  –
ākaṅkhamānā sotthānaṃ
 – ·  –  · · –   · –
brūhi maṅgalam uttamaṃ
metre: Siloka [pathyā / mavipulā]
```

### Book-wide TSV

`data/output/<file>.tsv` with columns
`book_code, paranum, vagga, metre, cost, pada_count, scansion, pali`.

### Aligned Markdown

`data/output/<file>.md` — every verse wrapped in a fenced code block so the
monospace alignment is preserved in any markdown viewer (Obsidian, VS Code,
GitHub).
