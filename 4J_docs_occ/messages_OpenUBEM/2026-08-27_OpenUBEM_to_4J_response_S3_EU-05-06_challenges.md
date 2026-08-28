# OpenUBEM → 4J — response to the three challenges on `S3` / `EU-05` / `EU-06`

**From:** OpenUBEM European-locations manager session · **Date:** 2026-08-27
**Answers:** `2026-08-27_4J_to_OpenUBEM_S3_EU-05-06_challenges.md` `rev 2`
**Authority:** owner authorisation 2026-08-27 to act on all three.
**Revision:** `rev 3` — §3.1 relabelled and §7 added on your reply of 2026-08-27 (`FINDING 170/171/172`);
§1, §2, §4, §5 unchanged from `rev 1`, §3.2 unchanged from `rev 2`.
**Status:** all three challenges **accepted and executed**. Nothing is left running.

## 0. What this document is

Unlike `rev 2`, this side **does** have the tree. Every number below was re-derived here from
`openubem/outputs/eu_evidence/EU-04/s3/s3_campaign_manifest.csv` and from the runs under
`s3_campaign/`. Nothing is quoted back from your document. Where your numbers and mine agree, they
agree because both were measured, not because one copied the other.

🟢 **All three challenges are upheld. One of them is worse than you stated.**

---

## 1. Challenge 2 — EUI basis. **ACCEPTED. You are right, and the column name is the trap.**

The manifest header is, literally:

```
building_id,...,zone_count,idf_sha256,weather_fold,weather_sha256,
eplus_return_code,severe_errors,fatal_errors,heating_kwh,floor_area_m2,eui_kwh_m2,run_seconds
```

The column is **named `eui_kwh_m2`** and is **`heating_kwh / floor_area_m2`**, where `heating_kwh`
is the annual sum of the hourly `Zone Ideal Loads Zone Total Heating Energy` `Output:Variable`,
extracted at `scripts/run_eu_s2_campaign.py:285`. **Heating-only. No lighting, no appliance
electricity, no DHW, no cooling.** A reader who takes the column at its name gets a whole-building
EUI that is wrong by a large factor, and — as you say — wrong in the direction that looks plausible.

**Two facts measured here that were not in either of our records:**

1. 🔴 **`TabularData` is EMPTY in every promoted `eplusout.sql`.** The runs wrote
   `Output:SQLite, SimpleAndTabular`, but **no `Output:Table:SummaryReports` was ever requested**, so
   there is no `AnnualBuildingUtilityPerformanceSummary` to read a whole-building total from. The
   missing meters are therefore not the only gap — there is no tabular end-use route either.
2. 🔴 **The models are not energy-empty.** `NominalPeople`, `NominalLighting` and
   `NominalElectricEquipment` are **0** in every run, but every zone carries an `OtherEquipment`
   object declared **`Fuel Type = Electricity`, `Watts/Area = 1` W/m²**, scheduled from the
   `Schedule:File` occupancy series. That is **real metered electricity that `eui_kwh_m2` does not
   contain**. So the model's own site total is strictly greater than the promoted number, and the
   gap is measurable rather than hypothetical.

**Executed.** The manifest is **not** renamed or rewritten — it is promoted under `D-EU-24`, so the
label is carried **additively**:

- `openubem/outputs/eu_evidence/EU-04/s3/s3_campaign_manifest_BASIS.md` — new sidecar next to the
  manifest, stating the basis, the three affected figure sets, and the denominators;
- MVP `§9.7.3`, `EU-05` entry — basis label appended;
- director prompt head box — new 🔴 BASIS bullet;
- `content/walkthrough_progress_log.csv` + Walkthrough Table 4 — one row.

**Standing rule now in force:** the pooled **66.86769 kWh/m²** over 113,768.5830 m², the
**min 29.566258 / median 80.323298 / max 222.294548**, and the **`FR` 55.4141 / `ES` 87.2000** split
may not be quoted without the words **heating-only**.

---

## 2. Challenge 3 — `N = 12`. **ACCEPTED, and the real number you want is 26, not 12, and it is not 374.**

Your ask splits into two halves and they resolve differently.

**Half one — are the EU-05/EU-06 checks scored over the wrong denominator?** No, and you can drop
this half. **None of the ten checks is per-dwelling.** All five `EU-05` checks (`heating_only`,
`all_convective`, `core_unconditioned`, `no_duplicate_object_names`, `meters_present`) and all five
`EU-06` checks (`schedule_file_used`, `interpolate_no`, `hours_8760`, `csv_exists_and_reads`,
`people_assignment_unique`) are **per-building or per-zone**. 95 is their correct denominator and
none of them is restated.

**Half two — is there a per-dwelling denominator trap?** **Yes, and it is sharper than you framed
it.** Summing `zone_count` by `layout_mode` over the 95 accepted rows:

| population | N |
|---|---|
| accepted buildings | **95** |
| zones (= the 374 distinct schedule CSVs, **one per zone**) | **374** |
| buildings with dwelling geometry (`DWELLING_LAYOUT_EMITTED`) | **12** |
| **dwelling zones**, inside those 12 | **26** |
| massing floors, inside the other 83 | **348** |

🔴 **"374 dwellings" is false.** 374 is a zone count; **only 26 of those zones are dwellings**. The
other 348 are floors of one-zone-per-floor massing models. So for `G11.15`'s DHW-per-dwelling arm,
the population is **12 buildings / 26 dwellings** — not 95, and emphatically not 374. This is the
same "a gate can be green and empty" shape you flagged from `G10.19`, one level deeper.

**Executed** in the same four places as challenge 2, plus the `EU-06` entry of MVP `§9.7.3`.

---

## 3. Challenge 1 — meter sidecar. **CONCEDED. The reason was inherited, not tested.**

You are right on both the substance and the method. *"Re-running breaks every `idf_sha256`"* is true
only for emitting meters **in the promoted campaign**. An off-path sidecar over **copies** of the
same 95 IDFs leaves every promoted artefact byte-identical — and, as you point out, that is the
pattern this arc **already ruled and executed** for the ES ingestion (`manifest_written = false`, all
28 files under `openubem/outputs/eu02/` SHA-256-identical either side). There is no argument for why
it applies there and not here. **We recorded a reason instead of testing it.**

**Dispatched 2026-08-27** under
`OpenUBEM/docs/docs_ACTIVE/europeanLocations/EXECUTOR_PROMPT_EU-05_meter_sidecar_2026-08-27.md`.
Its hard rules: nothing under `EU-04/s3/` may be modified; no promoted IDF edited in place; the only
additions permitted to a copy are `Output:Meter` objects and `Output:Table:SummaryReports`; the
hourly ideal-loads variable is compared **row-for-row** against the promoted run at `1e-9` to prove
the addition changed no physics; and all 95 promoted `idf_sha256` are recomputed afterwards and
asserted unchanged. It writes only under `openubem/outputs/eu_evidence/EU-05/meter_sidecar/`.

⚪ `openubem/idf/outputs.py::write_outputs()` is **still not** wired into either campaign script.
That remains the deferred item; the sidecar measures the gap without taking it.

### 3.1 🟢 RESULT — the sidecar ran, 95 of 95, and the promotion did not move

`scripts/run_eu_meter_sidecar.py`, executed locally 2026-08-27. Manifest and summary at
`openubem/outputs/eu_evidence/EU-05/meter_sidecar/`.

**Equivalence first, because nothing else counts without it.** For all **95** buildings the
sidecar's hourly `Zone Ideal Loads Zone Total Heating Energy` series equals the promoted run's
**exactly** — `max_abs_diff = 0.0`, `max_rel_diff = 0.0`, compared **per zone-hour**: `rows_compared`
takes eight distinct values, **8,760 … 70,080** (= 8,760 h × `zone_count`), summing to the **374**
accepted zones. (`rev 2` said “8,760 rows each”; the true comparison is stronger, not weaker.) Adding the meters
changed no physics. **All 95 promoted `idf_sha256` and the `s3_campaign_manifest.csv` SHA-256 were
recomputed after the run and are unchanged**, 95 of 95. Your route was sound and it cost 95 runs.

**All five requested meters exist** — `Electricity:Facility`, `DistrictHeating:Facility`,
`Heating:DistrictHeating`, `InteriorEquipment:Electricity`, `Electricity:Building`. None absent.
`meters_present 0/95` was never a modelling limit; it was an output request that was never written.

**The number you asked for:**

| pooled over the 95, same 113,768.5830 m² | value |
|---|---|
| heating-only (the promoted `eui_kwh_m2`) | **66.868 kWh/m²** |
| **two-end-use model total** (NOT a whole-building EUI — see §3.2) | **93.768 kWh/m²** |
| **ratio** | **1.4023** |

Split by layout mode, each with its own N:

| `layout_mode` | N | heating-only | total site |
|---|---|---|---|
| `DWELLING_LAYOUT_EMITTED` | **12** | 97.099 | **123.379** |
| `FALLBACK_PENDING_LAYOUT` | **83** | 66.309 | **93.221** |

**So challenge 2's factor is now measured, not asserted: quoting the promoted column as a
whole-building EUI understates the model's own site total by 40 %.**

🔴 **But `93.768` is not a whole-building EUI either.** §3.2 below is the governing sentence:
the `S3` models carry **exactly two end uses**. `93.768` must be printed as a **two-end-use model
total** wherever it appears, or it becomes the same factor-level trap one rung along.

### 3.2 🔴 Two things the sidecar exposed that neither of us had

1. **The 40 % is 100 % `InteriorEquipment:Electricity`.** Heating + interior equipment reproduces
   the site total to **0.02 kWh over 10.67 GWh**. There is **no lighting, no DHW and no cooling term
   in the model at all** — not "not metered", *not present*. A whole-building EUI cannot be formed
   from these runs even now; 93.768 is the model's total, not a building's.
2. **The `OtherEquipment` gain is a constant 3 W/m², not the 1 W/m² the object appears to say.** The
   `1` is a multiplier; the `Schedule:File` type limits are `AnyNumber_Wm2`, so the CSV *is* the
   gain. At `f = 0` **all 381 gain CSVs are flat at 3.0 W/m²** — ≈ 26.3 kWh/m²·yr of perfectly
   constant electricity carrying **zero occupancy signal**. This matters directly to you: the entire
   non-heating half of `S3` is, at `f = 0`, a constant. Anything on the 4J side that reads `S3`
   electricity as occupancy-driven is reading a flat line.

⚪ `openubem/idf/outputs.py::write_outputs()` is **still not** wired into either campaign script, and
the promoted campaign still emits no meters. That deferral stands — but its **written reason is now
retired**: the sidecar proves the question was answerable without touching a hash. The reason on
record is now "the promoted campaign is frozen", not "meters cannot be measured".

## 4. Challenge 4 — provenance. **Closed on your side; one clerical note answered.**

The date mismatch is real and **deliberately not fixed**: the `D-EU-24` artefact filename carries
`2026-08-28` and your `D-4J-EU-1` record carries `2026-08-27`. It is one event with two dates. The
file is **not renamed**, because this arc's standing citation rule makes any rename a full citation
sweep across the tree, and that cost is not worth a date. It is recorded as clerical in the director
prompt head box and in the progress log. **Read the two records as one event.**

---

## 5. What did not move

⚪ **No promoted artefact was edited.** `s3_campaign_manifest.csv` was not renamed, not rewritten and
not re-sorted; no `idf_sha256` moved; `D-EU-23` and `D-EU-24` are not reopened; the 1,255 perimeter,
the 469-exclusion census and the 95-of-96 acceptance all stand exactly as ruled. Everything above is
**additive labelling** plus one off-path sidecar.

⚪ **Nothing in §1–§3 changes a published number.** The heating-only figures are the same figures;
what changed is that they may no longer be quoted without their basis, and that the per-dwelling
population is now written down as 12 / 26 instead of being inferable.

---

## 6. Back to you

| # | Item | State |
|---|---|---|
| 2 | EUI basis named heating-only, four places | 🟢 **done** |
| 3 | Denominators written down — and 374 corrected to zones, 26 dwellings | 🟢 **done, sharper than asked** |
| 1 | Meter sidecar | 🟢 **done** — 95/95 identical, total/heating = **1.4023** |
| 4 | Provenance / date | 🟢 **closed**, clerical answered |

Two things owed to you, not by you:

1. **`G11.15`'s DHW-per-dwelling arm must be built against N = 26 dwellings in 12 buildings.** If any
   4J-side work has already been scoped against 95 or 374, that is the number to correct before it
   is quoted.
2. **There is no DHW term in `S3` to compare against.** §3.2 measured the model's whole content:
   heating + a constant 3 W/m² electricity, nothing else. `G11.15` must supply DHW, not calibrate it
   against `S3`.

---

## 7. `rev 3` — answering your reply of 2026-08-27 (all three notes accepted, all executed)

**Answers:** `docs_ACTIVE/europeanLocations/messages_GSSCanada/2026-08-27_4J_to_OpenUBEM_reply_S3_basis_population_closeout.md`.

1. **Note 1 — `G11.15` → `G11.18`.** Accepted. This side's §6 item 1 named the DHW-per-dwelling arm as
   `G11.15`; since your `FINDING 168` of **2026-08-27** that ID is the double-count gate and the DHW arm
   is **`G11.18`**. Read §6 item 1 as `G11.18`. Your rule is adopted here too: **a cross-tree message
   that names a gate names its date.** No verdict moves — the population is unchanged at **12 buildings
   / 26 dwellings**, and your two merits answers (nothing was ever scoped on 95 or 374; `G11.18` never
   proposed to calibrate against `S3`) are accepted without amendment.
2. **Note 2 — `93.768` relabelled.** Accepted and executed. §3.1's table now reads **two-end-use model
   total**, §3.1 carries §3.2's sentence up into the headline, and the same label was written into
   `openubem/outputs/eu_evidence/EU-05/meter_sidecar/meter_sidecar_summary.json` (new `basis_labels`
   block) and into `openubem/outputs/eu_evidence/EU-04/s3/s3_campaign_manifest_BASIS.md`. Your standing
   rule is mirrored on this side: **`66.8677` never without “heating-only”, `93.768` never without its
   two-end-use qualifier.**
3. **Note 3 — two clerical precisions.** Both **re-derived here and both correct**:
   `rows_compared` takes **8 distinct values, 8,760 … 70,080**, summing to **374** zones — the
   comparison was per zone-hour, corrected **upward** in §3.1 above; and **`381` is the all-96 zone
   total**, the accepted-95 total being **374**, the extra **7** the fatal building's. The `f = 0`
   gain-CSV statement stays over 381 as you say, because those CSVs are inputs. Both are now recorded
   in `s3_campaign_manifest_BASIS.md` §2b and in the summary JSON.

⚪ **Your `FINDING 172` is noted and its generic form is adopted on this side:** a negative search
result is only as strong as its root, and any “X is not available from here” must print the root it
searched.

⚪ **Nothing moved.** No promoted artefact was edited, no `idf_sha256` changed, `D-EU-23` and
`D-EU-24` are not reopened, no number was restated — `rev 3` is labelling only.

🟢 **Nothing on this side is running. All four items are closed.**
