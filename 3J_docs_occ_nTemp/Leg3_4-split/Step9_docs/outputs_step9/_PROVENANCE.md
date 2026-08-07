# 🔴 SUPERSEDED — do not read numbers or figures out of this directory

**This is `outputs_step9/`, the 2026-07-31 11:42 scorecard run. It is NOT the arm the paper reports.**

The arm the paper reports is the sibling directory
**`outputs_step9_deliverable/`** (frozen 2026-08-06 00:05), registered in
`improvements/v2/V2-G1_FROZEN_DELIVERABLE.md`.

---

## Why this file exists

On 2026-08-06, four consecutive v4 tasks were computed from **this** directory instead of the frozen
one. Office and retail differ by only ~0.1 % between the two, so nothing looked wrong — but **the
hotel channel INVERTS**: 28 cells *below the floor* here versus 28 cells *above the ceiling* in the
frozen arm. On that basis a master document that was correct got "corrected" in three places, and two
pre-registered sub-verdicts came out backwards (`V4-A1`).

> 🔴 **Both directories report "28 of 56".** Every check that compares counts or band values passes
> straight through the inversion. Only a check that looks at *which file was opened* — or at file
> content — can catch this.

---

## The collision surface, measured 2026-08-06

**11 filenames exist in both directories. 10 of them differ. One does not.**

| file | this dir (superseded) | `_deliverable/` (frozen) | |
|---|---|---|---|
| `figures/fig_diurnal_4ch.png` | `5117cfab` | `5117cfab` | ⚠️ **IDENTICAL** |
| `figures/fig_eui_4ch.png` | `1f7c9eda` | `b17ca5e2` | different |
| `figures/fig_longitudinal_4ch.png` | `a04d5640` | `4e32389f` | different |
| `figures/fig_peakhour_4ch.png` | `37a05fe2` | `83ebb7de` | different |
| `figures/fig_scenario_4ch.png` | `26744fbf` | `6e94a233` | different |
| `step9_eui_by_channel.csv` | `ce030239` | `9f2367dd` | different |
| `step9_gates.json` | `6ba5317d` | `e5ea569e` | different |
| `step9_loadshape_peaks.csv` | `ad663afd` | `7722369e` | different |
| `step9_longitudinal.csv` | `a43dbd1c` | `735f19a9` | different |
| `step9_report.html` | `d4347988` | `259b104a` | different |
| `step9_scenario_response.csv` | `1d3c8834` | `8e927778` | different |

> ⚠️ **`fig_diurnal_4ch.png` being byte-identical is the dangerous part, not the harmless part.**
> Spot-checking one figure, finding it identical, and concluding "the two directories agree" licenses
> copying the other four — which do not agree. It also means **no content check can establish which
> directory that one figure came from.** Its origin has to be recorded at copy time; it cannot be
> recovered afterwards.

---

## Why this directory is kept and must not be deleted or renamed

It holds **8 files that exist nowhere else**, so it is not a stale duplicate — it is the only copy of
its own evidence:

| file | size | what it is |
|---|---|---|
| `step9_envelope_exposure.csv` | 33,403 B | envelope-exposure table, cited by `improvements/v1/3rdJ_L3_improvements_step9.md` |
| `retail_rewire_before.json` | 1,050 B | pre-rewire retail state |
| `finding9_verify/Default_NECB__Tall__MTL/injected.idf` (+ `.provenance.txt`) | 6.2 MB | the **uninjected control** IDF behind the office band-applicability finding |
| `finding9_verify/Y2022__Tall__MTL/injected.idf` (+ `.provenance.txt`) | 7.1 MB | its treated counterpart |
| `finding9_verify/falsify_injected.idf` (+ `.provenance.txt`) | 7.1 MB | the falsifier fixture |

**That is the root of the trap:** the directory is legitimately needed for one table and three IDFs,
so it cannot be removed, and its name is a prefix of the frozen one, so it is easy to reach by
accident. The resolution is provenance and checking, not deletion.

---

## Rules

1. **Numbers, gate verdicts, and figures for the paper come from `outputs_step9_deliverable/`.**
2. Reading *this* directory on purpose is fine — annotate the line with
   `# FROZEN-INPUT-OK: <reason>` so `improvements/v5/f1_frozen_input_check.py` records it as
   deliberate rather than flagging it.
3. Anything copied out of here into `writing/` will be caught by
   `improvements/v5/f3_asset_provenance_check.py`, **except `fig_diurnal_4ch.png`**, which is
   indistinguishable by content.

Companion file: `../outputs_step9_deliverable/_PROVENANCE.md`.
