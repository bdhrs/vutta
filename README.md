# Vutta — a Pāḷi metrical analyzer

Reads a Pāḷi verse, scans its syllables into light (`˘`) and heavy (`¯`)
weights, splits it into pādas, and identifies the metre. Built on the rules of
the [*Vuttodaya*](https://tipitaka.org/romn/#2681) ([Ānandajoti's edition](https://www.ancient-buddhist-texts.net/Textual-Studies/Vuttodaya/index.htm)) and Ven. Ānandajoti Bhikkhu's [*Outline of the Metres in the
Pāḷi Canon*](https://www.ancient-buddhist-texts.net/Textual-Studies/Outline/index.htm).

## Quick start

```bash
# one-off scan from the CLI
uv run -m vutta.scan "Bahū devā manussā ca, maṅgalāni acintayuṃ, Ākaṅkhamānā sotthānaṃ, brūhi maṅgalam-uttamaṃ."

# scan every verse in a canon book and write an aligned .md file
cp .env.example .env       # then edit VUTTA_CANON_DB to point at your CST SQLite db
uv run -m vutta.scan_book_pretty s0502m_mul --out output/pretty/dhammapada.md

# scan every Khuddaka book up to (not including) the Apadānas
uv run -m vutta.scan_book_pretty \
    s0501m_mul s0502m_mul s0503m_mul s0504m_mul s0505m_mul \
    s0506m_mul s0507m_mul s0508m_mul s0509m_mul \
    --out output/pretty/khuddaka_pre_apadana.md
```

## Output format

For each verse, two lines per pāda followed by an analysis line:

```
˘ ¯  ¯ ¯  ˘ ¯  ¯  ¯
bahū devā manussā ca
¯  ˘ ¯ ˘  ˘¯  ˘ ¯
maṅgalāni acintayuṃ
¯¯  ˘  ¯ ¯  ¯  ¯  ¯
ākaṅkhamānā sotthānaṃ
 ¯ ˘  ¯  ˘ ˘ ¯   ˘ ¯
brūhi maṅgalam uttamaṃ
metre: Siloka [pathyā / mavipulā]
```

The `˘` (U+02D8 BREVE) and `¯` (U+00AF MACRON) symbols sit at the same vertical
level — they're the standard prosodic marks used in Latin/Greek/Sanskrit
scholarly typography and are widely supported in monospace fonts.

Note: dropped characters (the `b` of *brāhmaṇ-*, the medial `i` of *cariya*,
etc.) get a blank column above them — visually showing they don't participate
in scansion.

## Pipeline

```
raw text → normalize → pāda split → syllabify → weight → match → display
```

1. **normalize.py** — Two layers: `clean()` (lowercase, NFC, strip punctuation,
   preserve word spacing) and `metrical()` (apply sarabhatti + br/dv/tv
   substitutions, return both the substituted form and a position map).
2. **pada_split.py** — Split on explicit punctuation, line breaks, or a
   syllable-count heuristic (16 → halve into 8-syllable Silokas; 22 → halve
   into 11-syllable Tuṭṭhubha lines; etc.).
3. **syllabify.py** — Token-list algorithm: tokenise into vowels, consonants
   (digraphs as one atom), and niggahīta. For each VCCV cluster, the first
   consonant closes the previous syllable; the rest open the next.
4. **weight.py** — Apply *Vuttodaya* v. 7's five rules.
5. **match.py** — Three family-level detectors (Siloka with per-pāda vipulā
   identification + resolution; Tuṭṭhubha/Jagatī by terminal cadence; mātrā
   metres by total + cadence) plus a fixed-profile scorer for the rest.
6. **display.py** — Render scan marks above the verse, aligned to the first
   letter of each syllable in the original spelling.

## Realistic accuracy

On a 4,818-verse sample (Dhp + Sn + Thag + Thig + Bv + Cp):

- 70% exact match (cost 0)
- 18% near-match within cost 0.5 (resolution / replacement)
- 4–5% within cost 1.0
- 7–8% unmatched or high-cost (mostly: mixed-metre verses, heavy
  resolution in early-canonical Pāḷi, pādayuga-seam compounds, and verses
  with manuscript-variant pādas)

## Known limits

- **Mixed-metre verses** where some pādas are Siloka and others Tuṭṭhubha —
  the detector currently expects one metre per verse.
- **Aggressive resolution / replacement** in early-canonical text (Suttanipāta
  Aṭṭhakavagga, Pārāyanavagga).
- **Pādayuga-seam compounds** — last syllable of an odd pāda is treated heavy
  by default; for compounds spanning the seam the natural weight should be
  preserved. Detecting this needs a compound lookup (e.g. DPD).
- **Bar metres** (Ariyā / Gīti / Uggīti / Upagīti) — needs 4-mātrā gaṇa
  structure detection, not just terminal cadence. Implemented as a placeholder.

## Layout

```
vutta/
├── README.md
├── pyproject.toml
├── .env.example
├── vutta/
│   ├── __init__.py
│   ├── _data/
│   │   ├── digraphs.py        # the 18 aspirated digraphs, vowel classes
│   │   ├── env.py             # env / .env / VUTTA_CANON_DB resolution
│   │   ├── exceptions.py      # sarabhatti words, br-/dv-/tv- non-position stems
│   │   └── metres.py          # metre profiles (Siloka, Tuṭṭhubha, ...)
│   ├── normalize.py
│   ├── pada_split.py
│   ├── syllabify.py
│   ├── weight.py
│   ├── match.py
│   ├── display.py
│   ├── scan.py                # CLI: scan a single verse
│   ├── scan_book.py           # scan a canon book → TSV
│   ├── scan_book_pretty.py    # scan a canon book → aligned .md
│   ├── scan_cst_xml.py        # scan all CST XML files → aligned .md
│   ├── summarize_tsv.py       # stats from a scansion TSV
│   └── tests/
│       └── test_golden.py
└── output/
    ├── tsv/                   # generated TSVs (gitignored)
    ├── pretty/                # aligned .md from DB (gitignored)
    └── cst/                   # aligned .md from CST XML (gitignored)
```

## Sources

- Saṅgharakkhita, *Vuttodaya — The Composition of Metre*, ed./tr. Ānandajoti
  Bhikkhu, 2016. ([Pāḷi text](https://tipitaka.org/romn/#2681) · [Ānandajoti's edition](https://www.ancient-buddhist-texts.net/Textual-Studies/Vuttodaya/index.htm))
- Ānandajoti Bhikkhu, *Pāḷi Prosody: Texts and Studies* (contains *An Outline of
  the Metres in the Pāḷi Canon*).
- Ānandajoti Bhikkhu, *Main Metres in the Pāli Canon*, *Metre Tables*.
- A.K. Warder, *Pali Metre*, PTS.

Both Ānandajoti's online project ([ancient-buddhist-texts.net](https://www.ancient-buddhist-texts.net/Textual-Studies/Outline/index.htm))
and Warder's monograph informed the algorithms here.
