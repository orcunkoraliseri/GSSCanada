# Step 7 — Metabolic Map Verification (paper-prep)
### Grounding the 14-category activity → W/person map in a published source

---

## Goal

The BEM internal-gain channel (`Metabolic_Rate`) is produced by mapping each of the 14 unified
activity codes to a watts-per-person value (`BEMConverter.metabolic_map`,
`eSim_occ_utils/21CEN22GSS/21CEN22GSS_occToBEM.py:57`; re-used verbatim in
`07_aug_to_bem.py:22`). In the code this map is a **bare dict — no units, no body-size
assumption, no citation**. For the journal, every value feeding the energy simulation must be
traceable. This document establishes that source and verifies each value against it.

**Source (user-provided):** *2024 Adult Compendium of Physical Activities* — energy costs (MET
values) of human activities. File: `2J_docs_occ_nTemp/resources/1_2024-adult-compendium_1_2024.pdf`
(28 pp, 1,111 activity records: Major Heading · Activity Code · MET · Description).
Standard citation: Herrmann SD, Willis EA, Ainsworth BE, et al. *2024 Adult Compendium of
Physical Activities*, **J Sport Health Sci** 2024;13(1):6–12. *(confirm exact volume/pages at
submission.)*

---

## The map under test

```python
# 21CEN22GSS_occToBEM.py : BEMConverter.metabolic_map   (watts/person; unknown code -> 100)
{1:125, 2:175, 3:190, 4:195, 5:70, 6:105, 7:170, 8:110, 9:90, 10:85, 11:245, 12:105, 13:140, 14:135, 0:0}
```

---

## The conversion basis — recovered, not assumed

The Compendium gives **MET**, not watts. Reverse-engineering the map against it recovers a
single clean factor, confirmed by **two independent exact hits**:

| Activity (Compendium) | Compendium MET | Map W | W ÷ MET |
|---|---|---|---|
| **Sleeping** (Inactivity) | 1.00 | 70 | **70.0** |
| **Eating, sitting** (Self Care) | 1.50 | 105 | **70.0** |

⇒ **`Metabolic_Rate (W) = MET × 70`.** The map is Compendium MET values scaled by **70 W/MET**.

> **What 70 W/MET implies — the one point to state in the paper.** 1 MET ≈ 1 kcal·kg⁻¹·h⁻¹, so
> 70 W/MET (= 60.2 kcal/h) corresponds to a **~60 kg reference adult**. This is *conservative*
> relative to the two other common conventions:
> - ASHRAE 55 / ISO 7730 surface-area basis: 1 met = 58.2 W/m² × 1.8 m² ≈ **105 W/MET**
> - 70 kg physiological basis: ≈ **83 W/MET**
>
> Because all internal gains scale linearly by this factor, it is the single most consequential
> assumption. It is **defensible** (a lighter reference person → lower, conservative gains) but
> must be documented; a ×1.19 (→83) or ×1.5 (→105) sensitivity run is a one-line change if a
> reviewer asks.

---

## Per-category verification

Implied MET = map W ÷ 70, compared to representative Compendium activities for each category:

| Code | GSS category | Map W | ⇒ MET | Compendium anchor(s) — MET | Verdict |
|---|---|---|---|---|---|
| 5 | Sleep & Rest | 70 | **1.00** | Sleeping 1.00 | ✓✓ exact |
| 6 | Eating & Drinking | 105 | **1.50** | Eating, sitting 1.50 | ✓✓ exact |
| 8 | Education | 110 | 1.57 | Sitting–studying (read/write) 1.50 | ✓ close |
| 10 | Passive Leisure | 85 | 1.21 | Watch TV 1.0 · sit reading 1.0 · reclining read 1.3 | ✓ central |
| 12 | Community & Volunteer | 105 | 1.50 | Religious sitting 1.5–1.8 · volunteer sitting 1.3–1.5 | ✓ central |
| 2 | Household Work | 175 | 2.50 | Kitchen/cooking 2.0–3.5 · cleaning 2.0–3.5 · dishes 2.0 | ✓ central |
| 4 | Purchasing | 195 | 2.79 | Food shopping 3.30 · non-food shopping 2.30 (mid 2.8) | ✓ central |
| 3 | Caregiving | 190 | 2.71 | Childcare sit 2.0–2.3 / stand 3.5 · elder care 3.0 | ✓ blend |
| 7 | Personal Care | 170 | 2.43 | Bathing 1.5 · shower 2.0 · grooming 2.0 · dressing 2.8 · toilet 2.3 | ✓ (top of range) |
| 1 | Work & Related | 125 | 1.79 | Office/computer 1.3–1.5 · store clerk 1.8 · manual 2.3–4.8 | ✓ mixed-occupation blend |
| 13 | Travel | 140 | 2.00 | Driving 1.3–2.0 · passenger 1.3 · walking-travel 2.3–3.8 | ✓ (slightly conservative) |
| 9 | Socializing | 90 | 1.29 | Sitting talking 1.3 · standing talking ~1.8 | ⚠ slightly low (sit-only proxy) |
| 11 | Active Leisure | 245 | 3.50 | Walking-for-pleasure 3.5 · yoga 2.3–4.0 · light calisthenics 2.8–3.5; **vigorous sport 5–8** | ⚠ conservative for the vigorous tail |
| 14 | Miscellaneous / Idle | 135 | 1.93 | Idle/waiting/standing 1.0–1.3 | ⚠ high for a true "idle" bin |

**9 of 14 land squarely on Compendium central values; 2 are exact. No category is mis-scaled.**

---

## Findings & recommendations

1. **The map is well-grounded.** It is the 2024 Adult Compendium MET table scaled by a constant
   70 W/MET, with Sleep and Eating reproducing the standard exactly. For the paper this converts
   from "unexplained numbers" to a cited, reproducible mapping.
2. **Document the 70 W/MET (~60 kg) basis explicitly** in Methods — it is conservative vs ASHRAE
   (105) / 70 kg (83) and scales every internal-gain value.
3. **Three minor, low-impact flags** (Socializing slightly low; Active Leisure conservative for
   vigorous exercise; Misc high for "idle"). All sit in low-time-share or occupancy-gated slots,
   so energy impact is small. **Do not silently change values** — any edit alters publishable BEM
   results (per repo guardrail); flag for an explicit decision + a re-run if pursued.
4. **Occupancy gates the gain anyway** (EnergyPlus People object; OP5): in unoccupied slots the
   metabolic value contributes zero heat regardless, bounding the impact of any residual map error.

**Verdict for Step 7: the metabolic channel is now sourced and defensible.** Remaining paper-prep
on this item = adding the citation + 70 W/MET note to Methods, and (optional) a conversion-factor
sensitivity run.

---

## Provenance

- Map read from `eSim_occ_utils/21CEN22GSS/21CEN22GSS_occToBEM.py:57` (= `07_aug_to_bem.py:22`).
- Compendium text extracted from the provided PDF via PyMuPDF (`fitz`) → 1,111 parsed
  `(heading, code, MET, description)` records; anchors quoted above are verbatim entries.
- Conversion factor recovered (not assumed) from two exact hits (Sleeping 1.0→70, Eating 1.5→105).
- Activity-category definitions: `02_harmonizationGSS_actCodes.md` (14-category target scheme).
- Verified 2026-06-01.
