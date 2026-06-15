# GSS Split-Suitability Audit — Can Our Data Actually Do 2-Split and 4-Split?

### Internal data audit (codebooks + Leg-1 pipeline) · not a plan, a feasibility check

**Question this answers.** Before any planning, can the GSS Time-Use cycles we already use
(2005 / 2010 / 2015 / 2022) actually support splitting occupancy into **home / office / retail /
restaurant** channels? And does our completed residential pipeline (Leg 1) already have the wiring,
or would a split need new plumbing from scratch?

**Method.** Sonnet employees scanned the four cycle codebooks (`2J_docs_occ_nTemp/codebooks/`) for the
episode **location** variable and its codes, plus the Main-file employment variables; one more scanned
the Leg-1 harmonization/merge code for how location is currently handled. This doc synthesizes them.

**Headline verdict.**
- ✅ **2-split (home + office) is feasible from GSS in all four cycles** — and the wiring largely exists.
- ✅ **Retail + restaurant location channels also exist in all four cycles** (the GSS part of 4-split).
- ⚠️ **Hotel has no GSS code** — confirmed non-GSS (StatCan track), exactly as the 4-channel doc assumed.
- ⚠️ **Retail "staff" is invisible in GSS** (logged as work, not shopping) — needs SCIEU, as deep research said.
- 🔧 **One real gap:** location is harmonized & carried at the *episode* level, but only **AT_HOME** is
  tiled into the per-slot HETUS arrays. The split needs `occPRE` propagated into the slot-tiling step.

---

## 1. The location variable exists in every cycle (with renumbering)

Every cycle records the physical place of each activity episode. The name and code scheme changed
across redesigns, but the concept and the split-relevant categories survived intact.

| Cycle | Variable | File | Code scheme | Sentinels |
|---|---|---|---|---|
| 2005 (C19) | `PLACE` | Episode | 2-digit, 01–21 | 97/98/99 |
| 2010 (C24) | `PLACE` | Episode | 2-digit, 01–21 (same as 2005) | 97/98/99 |
| 2015 (C29) | `LOCATION` | Episode | 3-digit, 300–321 | 999 |
| 2022 (GSSP) | `LOCATION` | Episode | 4-digit, 3300–3323 | 3399/9999 |

> The 2015 "light diary" redesign cut **activity** codes (264→64) but **left location coding intact —
> actually slightly more granular** (22 place codes). So the deep-research warning ("use location, not
> activity, codes for commercial presence") is the right call and is fully supported by our data.

---

## 2. Cross-cycle crosswalk for the split-relevant places

The four channels we care about map cleanly across all cycles:

| Channel | 2005 / 2010 (`PLACE`) | 2015 (`LOCATION`) | 2022 (`LOCATION`) | ~Wtd share of episode-time |
|---|---|---|---|---|
| **Home** | 01 Respondent's home | 300 At home/property | 3300 At home/property | 64.5% (2015) → 70.6% (2022) |
| **Office/work** | 02 Work place | 301 At work or school* | 3301 At work or school* | ~7.2% (2015) → 6.1% (2022) |
| (work, off-site) | — | 302 Away on business | 3302 Away at business | 0.2% |
| **Retail** | 06 Grocery + 07 Other store/Mall | 306 Grocery/stores/mall | 3306 Grocery/stores/mall | ~2.1–2.3% |
| **Restaurant/bar** | 04 Restaurant/bar | 309 Restaurant/bar/club | 3309 Restaurant/bar/club | ~0.7–1.2% |
| **Hotel/lodging** | ❌ none | ❌ none | ❌ none | — |

\* **Work and school share one code** in 2015/2022 (301/3301). 2005/2010 had a separate `08 School`, so
work (`02`) was cleaner. To isolate true workplace from students in 2015/2022, gate on employment
(Section 4) or activity codes.

**Two granularity notes:**
- **Retail is coarser in 2015/2022** (single grocery+store+mall bucket) than 2005/2010 (grocery vs
  other-store separate). Our existing harmonization already collapses both into one "Shopping" category,
  so this is consistent across cycles — just can't separate grocery from general merchandise.
- **Restaurant = bar = club** in one code every cycle; can't split dining from drinking via location.

---

## 3. The Leg-1 pipeline ALREADY harmonizes location (big finding)

The residential pipeline did **not** binarize-and-discard location. It already crosswalks every cycle's
raw place code into a unified **18-category `occPRE`** scheme and carries it through to the merged
dataset. AT_HOME is just `occPRE == 1`.

**The existing 18-category `occPRE` (from `02_harmonizationGSS_pre_coPre.md`):**

| occPRE | Location | Split relevance |
|---|---|---|
| **1** | Home | → **AT_HOME** (already used) |
| **2** | Work / School | → **AT_WORK** (office channel) ✅ already present |
| 3 | Other home | — |
| 4 | Outdoor | — |
| **5** | Shopping | → **AT_RETAIL** (retail channel) ✅ already present |
| 6 | Library / museum / theatre | — |
| **7** | Restaurant / bar / club | → restaurant channel ✅ already present |
| 8 | Place of worship | — |
| 9 | Other / Elsewhere | — |
| 10–17 | Travel (car/walk/transit/…) | excluded (not building occupancy) |
| 18 | Skip / Not stated | excluded |

**Where it lives in code (file:line from the scan):**
- Crosswalk applied in `02_harmonizeGSS.py:480–485`: picks `PLACE` (2005/2010) or `LOCATION` (2015/2022),
  maps via Excel, sets `AT_HOME = (occPRE == 1)`.
- Excel crosswalk: `references_Pre_coPre_Codes/Data Harmonization_presenceCategories - execution.xlsx`
  (3 sheets: 2005-2010 / 2015 / 2022), loaded by `build_presence_crosswalks()` (`02_harmonizeGSS.py:459–474`).
- `PRES_SHEET_MAP` dict at `02_harmonizeGSS.py:451–456`.
- `occPRE_raw`, `occPRE`, `AT_HOME` all carried into the merge (`03_mergingGSS.py:76–78`).

> **Meaning for the split:** AT_WORK (`occPRE==2`), AT_RETAIL (`occPRE==5`), and restaurant
> (`occPRE==7`) are **already present on every harmonized episode row**. No new location-code wiring
> from scratch — the upstream feed exists.

---

## 4. Employment gating exists in every cycle (to isolate real workers)

Because `occPRE==2` bundles work+school (2015/2022), and because WFH episodes hide at home (Section 5),
we need Main-file employment variables. They exist every cycle (names differ):

| Concept | 2005 | 2010 | 2015 | 2022 |
|---|---|---|---|---|
| Main activity last week | `MAR_Q100` | `MAR_Q100`/`ACT7DAYS` | `ACT7DAYS` | `ACT7DAYC` |
| Worked last week (Y/N) | (via MAR_Q100) | `WKLTWE` | `MRW_D40B` | `MRW_D40B` |
| Labour-force status | `LFSGSS` | `LFSGSS` | (derived) | (derived) |
| Hours/week | `WKWEHR_C` | `WKWEHR_C` | `WHWD140C`/`WHW_D141` | `WHWD140G` |
| Class of worker | `MAR_Q172` | `MAR_Q172` | ⚠️ `WET_120` suppressed in PUMF | `WET_120` |
| Occupation (NOC) | `SOC91C10` | `NOCS2006_C10` | `NOC1110Y/W` | `NOCLBR_Y` |
| Industry (NAICS) | `NAICS2002_C16` | `NAICS2007_C16` | `NAIC12CY/W` | `NAIC22CY` |
| Telework / WFH | — | `MAR_Q190` (works at home) | `WTI_130` (telework reason) | `TLWK_01A–D`, `TLWK_02G` |

These cover the office-archetype conditioning (`NOCS × Industry`) the 2-channel doc planned, and the
WFH lever for forecasting. Note **2015 class-of-worker (`WET_120`) is suppressed** in the PUMF — use
`WLY_150` (terms of employment) as a proxy if employee-vs-self-employed split is needed for 2015.

---

## 5. The WFH wrinkle (real, but it's a feature not a bug)

In 2022, paid work done at home is coded **LOCATION = 3300 (home)**, not work — so the "at work" share
looks suppressed (6.1% vs ~7%+ pre-COVID). 17.4% of employees teleworked from home that week.

- For **office-zone BEM** this is *correct*: we want bodies physically in the office, and a WFH worker
  is genuinely not there.
- For the **longitudinal story** this WFH shift *is* the signal (the same COVID jump Leg 1 captured for
  AT_HOME 63%→70.6%). Isolate it via `TLWK_01A` (2022) / `WTI_130` (2015) / `MAR_Q190` (2010).

So WFH doesn't block the split — it just means "AT_WORK" = physical office presence, and WFH lives in
the AT_HOME channel, which is the physically right answer.

---

## 6. The one real implementation gap

`occPRE` is carried at the **episode** level, but the per-slot HETUS arrays (Step 3C tiling) currently
tile **only `AT_HOME`** into the 48-slot sequence the Transformer consumes. From the scan:

> "A non-residential model would need to propagate `occPRE` into the slot tiling step (currently Step
> 3C) as an additional channel or replace the binary AT_HOME with a multi-class location token."

So the split's first concrete build task is: in Step 3C, also tile `AT_WORK = (occPRE==2)` and
`AT_RETAIL = (occPRE==5)` (and restaurant if wanted) into 48-slot binary channels — exactly what the
`2-channel_split.md` draft's "HETUS export with two channels" task described, now confirmed against real
data.

---

## 7. Per-split verdict

| Split | GSS feasible? | Notes |
|---|---|---|
| **Home (Leg 1)** | ✅ shipped | `occPRE==1`, all cycles |
| **Office / AT_WORK (Leg 2)** | ✅ **yes, all cycles** | `occPRE==2`; gate work-vs-school via employment vars in 2015/2022; WFH→home is correct |
| **Retail / AT_RETAIL (Leg 3)** | ✅ yes (customer side) | `occPRE==5`; single bucket, no grocery/merch split; **shopper-centric, not store density** |
| **Retail staff** | ❌ not in GSS | logged as work; use NRCan SCIEU worker density (deep-research Part B) |
| **Restaurant/bar** | ✅ yes | `occPRE==7`; optional extra channel; bar/dining not separable |
| **Hotel** | ❌ no GSS code | confirmed non-GSS → StatCan tourism / STR track (deep-research Part B/G) |

---

## 8. So where are we heading? (the answer to your question)

1. **No more deep research needed on GSS suitability.** Our own data answers it: the location signal is
   there in all four cycles and already harmonized.
2. **2-split (home+office) is solidly GSS-feasible** and reuses existing wiring; the only new build is
   tiling AT_WORK into the slot arrays + office conditioning (NOCS/industry) + employment gating.
3. **4-split's GSS portion (retail customer) is feasible**; its **non-GSS portions are now firmly
   scoped** — hotel (StatCan/STR) and retail-staff (SCIEU) are confirmed *not* derivable from GSS, so
   they won't surprise us mid-build.
4. **The combined picture** (this audit + `00_research_synthesis.md`) gives a clear, no-vicious-cycle
   direction: GSS drives home/office/retail-customer through the shared Transformer; SCIEU + StatCan
   drive retail-staff + hotel as side tracks; everything modulates code baselines except residential.

---

## Sources

- Codebooks: `2J_docs_occ_nTemp/codebooks/Codebook_{2005,2010,2015,2022}/` (Episode + Main PUMFs).
- Leg-1 wiring: `02_harmonizeGSS.py`, `03_mergingGSS.py`, `02_harmonizationGSS_pre_coPre.md`,
  `00_GSS_Occupancy_Pipeline.md` (Step 2/3), and the presence crosswalk Excel under
  `references_Pre_coPre_Codes/`.
- Companion evidence: `3J_docs_occ_nTemp/00_research_synthesis.md` (deep-research synthesis).
- Scanned by Sonnet employees, 2026-06-13.

---

## 9. Case study — is "Option B" (list-driven channel tiling) actually applicable?

**Question.** Section 6 found one real gap: the slot-tiling step tiles only `AT_HOME`. Two ways to add
`AT_WORK`/`AT_RETAIL` were proposed — (A) copy-paste the AT_HOME blocks per channel, or (B) make tiling
loop over a *list* of channels. This case study checks whether Option B is genuinely feasible, using the
code that already exists, before anyone commits to it.

**Finding: Option B is not hypothetical — the repo already ships a working list-driven tiler.** The
co-presence step (`tile_copresence_to_30min`, `03_mergingGSS.py:821–944`) tiles **9 channels at once**
by looping over a list. It is the exact template we'd reuse.

### 9.1 The proven in-house template (co-presence)

- **The list** (`03_mergingGSS.py:821–824`):
  ```python
  COP_COLS = ["Alone","Spouse","Children","parents","otherInFAMs",
              "otherHHs","friends","others","colleagues"]
  ```
- **One pass, all channels** — a dict of arrays keyed by channel name, filled in a single loop
  (`:860–899`): `cop_10min = {col: np.full((n,144), np.nan) for col in COP_COLS}`, then for each
  episode it stamps every channel's value across the covered slots.
- **Same slot math as AT_HOME** — identical 4 AM-origin shift `(startMin-240) % 1440` (`:889`), so
  behaviour matches the residential path exactly.
- **Same binary majority vote** for 144→48 downsampling (`:903–918`): `sum_present >= 2`.
- **Column names auto-generated** per channel (`:924`): `f"{col}30_{i:03d}"` → `Alone30_001…048`, etc.
- **Reads the value straight off the episode row**, just like AT_HOME does — no per-slot derivation.

### 9.2 How home/work/retail fold into it

`occPRE` is already on every episode row (`EPISODE_COMMON_COLS`, `:77`), so the two new channels are
derived once, *before* the loop, with a single comparison each — then the existing loop is untouched:

```python
episodes_sorted["AT_WORK"]   = (episodes_sorted["occPRE"] == 2).astype(float)
episodes_sorted["AT_RETAIL"] = (episodes_sorted["occPRE"] == 5).astype(float)
BINARY_CHANNELS = ["AT_HOME", "AT_WORK", "AT_RETAIL"]   # add "restaurant"=occPRE==7 later
```

That's the whole "applicability" answer: the loop body, slot math, downsampling, and naming are already
generic — only the **channel list** and a **one-line derivation** change. Adding a 4th channel for Leg 3
is then literally one list entry.

### 9.3 Two real design decisions (the only non-trivial parts)

The scan surfaced two places where the co-presence convention and the AT_HOME convention differ — these
must be reconciled deliberately, or the new channels will be silently inconsistent:

| Decision | AT_HOME path (Phase F/H) | Co-presence path | What to pick |
|---|---|---|---|
| **Empty slots** | `ffill`/`bfill` → zero NaNs (`:486–487`) | left as `pd.NA` (meaningful "no episode") | Decide one policy for the new channels; document it |
| **Binary encoding** | 1 = home, 0 = away (`:650`) | 1 = present, 2 = absent | Use **1/0** for all occupancy channels (consistent with AT_HOME) |

Neither is hard — they're choices, not obstacles.

### 9.4 Output routing (no merge headache)

Co-presence writes a **separate** file `outputs_step3/copresence_30min.csv` (`:939`), validated against
`hetus_30min.csv` by `occID` order. So the new channels can either extend that file or go to a new
`occupancy_30min.csv` — both are anchored to the same `occID` order, so nothing needs re-merging.

### 9.5 Recommended shape of Option B (conservative variant)

Because the residential AT_HOME/activity output is **shipped and publishable**, the safest applicable
form of Option B is:

- **Leave the existing Phase F/H residential path untouched** (AT_HOME + activity stay bit-identical).
- **Add a new list-driven binary-channel tiler cloned from `tile_copresence_to_30min`** that emits
  `AT_WORK`/`AT_RETAIL` (and AT_HOME too, for a self-contained occupancy file) to a separate CSV.
- Full unification (deleting `_build_slot_arrays` and merging all three tilers into one) is *optional
  cleanup* — higher risk because it touches the residential output, so defer it unless wanted.

### 9.6 Verdict

| Aspect | Assessment |
|---|---|
| Is Option B applicable? | **Yes** — a working list-driven tiler already exists in-repo (co-presence) |
| New code needed | A clone of `tile_copresence_to_30min` + 2 derivation lines |
| Hard problems | None; two convention choices (NaN policy, 1/0 encoding) to standardize |
| Risk to shipped residential results | **Zero** in the conservative variant (residential path untouched) |
| Leg-3 extensibility | Adding restaurant / future channels = one list entry |
| Effort | Small–Medium (clone + parameterize + validate) |

**Bottom line:** Option B is fully applicable and low-risk. We are not inventing machinery — we are
pointing an existing 9-channel list-driven tiler at the occupancy channels. This is the recommended
path when the split is eventually built.

*(Code mechanics verified by Sonnet employee against `03_mergingGSS.py`, 2026-06-13.)*
