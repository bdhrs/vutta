# Plan: Per-pāda metre identification (mixed-metre verses)

## Phase 1 — Baseline + diagnosis

- [ ] Run the full scan over Dhp + Sn + Thag + Thig + Bv + Cp, save TSV to
      `data/output/baseline_mixed.tsv`.
      → verify: `wc -l data/output/baseline_mixed.tsv` ≥ 4818
- [ ] Filter rows where `metre == "unmatched"` and group by `pada_count`
      and syllable-length pattern (e.g. `[8,8,11,11]`, `[11,11,12,12]`).
      Write the top 20 most common length-patterns to
      `data/output/unmatched_length_patterns.tsv`.
      → verify: file exists; the top entry has count > 50 (sanity)
- [ ] Spot-check 10 random unmatched verses from each of the top 5
      patterns. Confirm by hand that each is a genuine mixed-metre verse.
      Notes go in `notes/unmatched_audit.md` in this thread dir.
      → verify: `notes/unmatched_audit.md` exists and lists ≥50 verses
        with per-pāda metre tags

## Phase 2 — Per-pāda detector

- [ ] Add `vutta/per_pada.py` exposing `identify_pada(weights: str) -> str`
      that returns one of: `Siloka`, `Tuṭṭhubha`, `Jagatī`, `Vetālīya`,
      `Opacchandasaka`, `Āpātalikā`, or `unknown`. Uses the same
      length+cadence checks the family detectors already implement,
      but on a single pāda.
      → verify: unit-test 12 hand-picked pādas (3 per major family);
        all return the expected label.
- [ ] Phase-end verification: `uv run -m vutta.tests.test_golden` exits 0.

## Phase 3 — Mixed-verse detector

- [ ] Add `_detect_mixed` in `match.py` that calls `identify_pada` per
      pāda and returns a name like `Siloka + Tuṭṭhubha mix (8/8/11/11)`
      when at least 2 distinct non-unknown families are present and all
      pādas are individually identified. Cost = 0.5 * (number of mixed
      pādas) so it ranks below homogeneous matches.
      → verify: scan a known mixed verse (Dhp 19 ↔ a Tuṭṭhubha/Siloka mix
        from Sn) — top result reflects the actual structure.
- [ ] Wire `_detect_mixed` into `match()` as a final fallback (after
      Siloka / Tuṭṭhubha / mātrā / fixed-profile attempts but before
      `unmatched`).
      → verify: existing homogeneous tests still pass at cost 0.
- [ ] Phase-end verification: `uv run -m vutta.tests.test_golden` exits 0
      and Dhp Yamakavagga (1-20) all match correctly via
      `uv run -m vutta.scan_book s0502m_mul --out /tmp/y.tsv` then
      `head -25 /tmp/y.tsv | grep -v unmatched | wc -l` ≥ 21.

## Phase 4 — New golden test + corpus regression

- [ ] Add a fourth `CASES` entry to `tests/test_golden.py` for a
      verified mixed-metre verse (pick one from the Phase 1 audit).
      Include both the expected per-pāda weights and the new mixed
      label.
      → verify: `uv run -m vutta.tests.test_golden` reports 4/4 cases ✓.
- [ ] Re-run the corpus scan, save to `data/output/after_mixed.tsv`,
      run `vutta.summarize_tsv` on both baseline and after files,
      compare unmatched counts.
      → verify: unmatched drops from ~1200 to ≤ 700; no homogeneous
        family loses verses (Siloka count unchanged ±5).

## Phase 5 — Pretty output regression

- [ ] Re-render `khuddaka_pre_apadana.md` with the new matcher.
      → verify: file size changes (more verses now have a metre line
        instead of `unmatched`); spot-check 3 previously-unmatched
        verses in Suttanipāta now show the mixed label.
- [ ] Phase-end verification: full test suite green; manual inspection
      of 5 randomly-picked verses confirms display alignment is
      unchanged.
