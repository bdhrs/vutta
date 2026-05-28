# Spec: Per-pāda metre identification (mixed-metre verses)

## Overview

The matcher currently expects every pāda in a verse to share one metre.
In reality, many canonical Pāḷi verses mix metres — most commonly Siloka
opening + Tuṭṭhubha cadence, or Siloka odd lines followed by Vetālīya
even lines. These verses currently come back as `unmatched`. A
sample scan over Dhp + Sn + Thag + Thig + Bv + Cp shows ~1,200 unmatched
verses (~25%), of which a large fraction are genuinely mixed-metre.

## What it should do

1. Identify the metre of each pāda **independently**: Siloka, Tuṭṭhubha,
   Jagatī, Vetālīya, Opacchandasaka, Āpātalikā, or unknown.
2. When all pādas agree, report the homogeneous metre as today.
3. When pādas disagree, report the mix as a list, e.g.
   `Siloka + Tuṭṭhubha (8/8/11/11)`.
4. Preserve current behaviour and cost values for homogeneous verses
   — no regression in the existing test suite or the Dhp Yamakavagga
   (20/20 must still pass).

## Assumptions & uncertainties

- We assume per-pāda metre is well-defined by syllable count + terminal
  cadence; this holds for Siloka, Tuṭṭhubha, Jagatī, and the mātrā
  metres. Edge cases (resolution making a pāda look shorter, e.g. an
  11-syllable line scanned as 10) are handled by the existing per-pāda
  flexibility (±1 syllable).
- Uncertain: whether a mixed verse like Siloka + Vetālīya (8+8+14+16)
  occurs frequently enough to justify a special case. Verify against the
  current 1,200-verse unmatched sample before generalising.

## Constraints

- Must not regress the golden tests (`vutta/tests/test_golden.py`).
- Must not regress Dhammapada Yamakavagga (vv. 1-20 all correctly
  identified, including 6-pāda Silokas and resolution cases).
- Must keep the cost-based ranking so homogeneous verses still beat
  near-misses that happen to mix metres accidentally.

## How we'll know it's done

- The unmatched count on Dhp + Sn + Thag + Thig + Bv + Cp drops from
  ~1,200 (≈25%) to no more than ~700 (≈14%) — a roughly halving.
- `Tuṭṭhubha/Jagatī mix` cases remain identified as such (this is
  already supported and must not regress).
- A new family label appears for genuine mixed verses, e.g.
  `Siloka + Tuṭṭhubha mix` — recognisable in the summary.
- The pretty output (`scan_book_pretty`) shows the new label.
- A new golden test case (a verifiable mixed verse from a known source)
  is added and passes.

## What's not included

- Pādayuga-seam compound detection (separate thread).
- Bar metres / Ariyā / Gīti (separate thread).
- Heavy resolution / replacement in early-canonical Pāḷi beyond what's
  already implemented.
- Changes to the display format.
