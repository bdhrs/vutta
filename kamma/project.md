# Project: Vutta

A Pāḷi metrical analyzer. Reads a Pāḷi verse, scans each syllable as light
(`˘`) or heavy (`¯`) per the rules of the *Vuttodaya*, splits the verse into
pādas, and identifies the metre (Siloka, Tuṭṭhubha, Jagatī, Vetālīya,
Opacchandasaka, Āpātalikā, and the principal fixed metres).

## What it is and why

A standalone Python package + CLI for Pāḷi metrical analysis. Built because
the canonical rules of scansion (Saṅgharakkhita's *Vuttodaya*) and the modern
descriptive work (Ven. Ānandajoti's *Outline of the Metres in the Pāḷi
Canon*) are mature and well-documented, but no open-source tool implements
them end-to-end. The intent is to make scansion of any Pāḷi verse a one-line
command, and to produce printed reference material in the format Ānandajoti
uses in his books — scan marks aligned above the first letter of each
syllable, with metre identification.

## Who it's for

- The author (a Pāḷi student) as a learning aid alongside the *Vuttodaya*
  study guide.
- Other Pāḷi students and Indologists who want quick scansion of canonical
  verse without manual counting.
- Eventually: anyone studying Sanskrit / Indian prosody who wants a
  machine-readable scansion of the Pāḷi corpus.

## One-off or ongoing

**Ongoing.** v1 covers ~93% of canonical Siloka and ~70% of the broader
canonical corpus correctly. Known limits (mixed-metre verses, heavy
resolution, pādayuga-seam compounds, bar metres) are open work.

## What it will produce

1. A Python package `vutta` importable as a library.
2. CLI entry points:
   - `vutta.scan` — scan a single verse from the command line.
   - `vutta.scan_book` — scan every verse in a canon book → TSV.
   - `vutta.scan_book_pretty` — scan every verse → aligned `.md` (Ānandajoti
     style, ready to read in Obsidian or any markdown viewer).
   - `vutta.summarize_tsv` — per-book stats and family distribution.
3. Pre-rendered output files of canonical verse with scansion + metre tags
   (e.g. `data/output/khuddaka_pre_apadana.md`).

## How we'll know it worked

- Golden tests pass against Ven. Ānandajoti's published scansions (currently
  Maṅgalasutta v.1, Jinacarita v.1, Dhammapada 183d).
- On the Yamakavagga (Dhammapada 1–20), 20/20 verses are correctly
  identified.
- On a 4,818-verse sample (Dhp + Sn + Thag + Thig + Bv + Cp), at least 70%
  exact match and 88%+ cleanly identified at cost ≤ 1.0.
- Output is visually correct in standard monospace fonts (Obsidian, VS Code,
  terminal) — scan marks align above syllable-start letters with no font
  fallback surprises.
