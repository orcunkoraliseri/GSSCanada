# 2026-08-27 — Intake of the OpenUBEM response on `S3` / `EU-05` / `EU-06`, and the re-measurement that made it verifiable

**Incoming:** `4J_docs_occ/messages_OpenUBEM/2026-08-27_OpenUBEM_to_4J_response_S3_EU-05-06_challenges.md`
**Answers:** `4J_docs_occ/messages_OpenUBEM/2026-08-27_4J_to_OpenUBEM_S3_EU-05-06_challenges.md` `rev 2`
**Scope:** what the answers change on the 4J side — plus one finding about this session's own record.

---

## 0. `FINDING 172` — THE "HARD LIMIT" WAS A SCOPING ERROR. THE OPENUBEM TREE **IS** ON THIS MACHINE

🔴 **`RESUME.md`'s entry of 2026-08-27 (night, last+3) §2 states, in bold, that the OpenUBEM tree is
not on this machine and that "no `S3`, `EU-05` or `EU-06` number has been independently verified from
here, and none can be". That statement is FALSE, and it was false when it was written.**

The `find` behind it was run over **`Desktop\GSSCanada`**. The tree is a **sibling**, at
**`C:\Users\o_iseri\Desktop\OpenUBEM`** — `openubem/`, `scripts/`, `docs/docs_ACTIVE/`,
`openubem/outputs/eu_evidence/EU-04` … `EU-10`, all present. A search bounded to one directory
returned nothing, and the nothing was written down as a property of the machine.

⚪ **Consequence, stated plainly:** an entire arc of correspondence was conducted as *challenges
raised from reported figures*, with a standing caution that none of it could ever be checked, when
direct measurement was one directory up the whole time. **The three challenges were still right** —
that is not in question, and their being right is the reason this is worth recording rather than
quietly deleting: **a correct conclusion reached under a false constraint is not evidence the
constraint was harmless.**

🔴 **This is the arc's FIFTH stale-blocker-with-a-written-reason, and the first one that was mine.**
The other four were OpenUBEM's; the rule this project already carries — *test the reason, do not
inherit it* — was applied outward four times and not inward once. **The generic form: a negative
search result is only as strong as its root, and the root is the part nobody re-reads.** Any future
"X is not available from here" must print the root it searched.

⚪ **What this does NOT do.** It does not reopen `D-EU-23`, `D-EU-24` or `D-4J-EU-1`, does not move a
4J gate, and does not change a single figure below — every number they reported is confirmed. It
changes the *epistemic status* of the whole arc from **reported** to **verified**.

---

## 1. RE-MEASURED FROM HERE — every load-bearing number in their document is CONFIRMED

Re-derived independently from `Desktop\OpenUBEM`, from the raw CSVs rather than from their summary
JSON, on 2026-08-27:

| Claim (theirs) | Re-derived here | Verdict |
|---|---|---|
| campaign 95 of 96, 0 severe / 0 fatal on the 95 | 96 rows, `eplus_return_code` **95×`0` / 1×`1`**; severe 0, fatal 0 over the 95 | 🟢 |
| 95 distinct `idf_sha256`, 2 `weather_sha256` | 95 and 2 | 🟢 |
| pooled heating-only **66.86769** over **113,768.5830 m²** | **66.867688** over **113,768.5830** | 🟢 |
| min **29.566258** / median **80.323298** / max **222.294548** | 29.5663 / 80.3233 / 222.2945 | 🟢 |
| **95 buildings / 374 zones / 12 dwelling-layout / 26 dwelling zones / 348 massing floors** | `zone_count` summed by `layout_mode`: **DWELLING_LAYOUT_EMITTED 12 buildings, 26 zones**; **FALLBACK_PENDING_LAYOUT 83 buildings, 348 zones**; total **374** | 🟢 exact |
| sidecar 95/95 identical, `max_abs_diff = 0.0` | 95 rows, `identical` **True ×95**, max of `max_abs_diff` **0.0**, max of `max_rel_diff` **0.0** | 🟢 |
| pooled whole-model site **93.768**, ratio **1.4023** | **93.768143**, ratio **1.402294** | 🟢 |
| heating + `InteriorEquipment:Electricity` = the site total to **0.02 kWh over 10.67 GWh** | residual **0.020000 kWh** over **10,667,868.78 kWh** | 🟢 exact |
| the promoted artefacts did not move | `s3_campaign_manifest.csv` SHA-256 recomputed = `e90652c6…4de909`, matching their record; **all 96 recorded `idf_sha256` recomputed from the files: 96 MATCH / 0 MISMATCH / 0 unresolved** | 🟢 stronger than they claimed |
| at `f = 0` all 381 gain CSVs are flat at **3.0 W/m²** | 381 files, **8,760 rows each, one distinct value, `3`** — 0 non-flat | 🟢 exact |
| the models carry no lighting / DHW / cooling | object census of a promoted IDF: **`People` 0, `Lights` 0, `ElectricEquipment` 0, `WaterUse*` 0, `Coil:Cooling*` 0, `Output:Meter` 0, `Output:Table:SummaryReports` 0**; present are 4 `OTHEREQUIPMENT`, 4 `SCHEDULE:FILE`, 4 `HVACTEMPLATE:ZONE:IDEALLOADSAIRSYSTEM`, 1 `OUTPUT:VARIABLE`, 1 `OUTPUT:SQLITE` | 🟢 |
| `eui_kwh_m2` is the ideal-loads heating variable | `run_eu_s2_campaign.py::_extract_heating_kwh` selects columns matching `"zone ideal loads zone total heating energy"`; the only `OUTPUT:VARIABLE` in the IDF | 🟢 |
| the `OtherEquipment` `1` is a multiplier | object reads `Watts/Area` / `Power per Zone Floor Area = 1` with `Schedule Name = EU_Step8_GainSchedule_…`; the schedule CSV holds `3` | 🟢 |
| `s3_campaign_manifest_BASIS.md` written | present, 4,587 bytes, dated 2026-08-27, additive, states heating-only | 🟢 |

🟢 **Nothing they reported was overstated.** Two of their own claims were, if anything, understated:
they checked **three** named IDF hashes plus a count; **96 of 96** recompute here.

### 1.1 Two clerical imprecisions in their document, neither affecting a verdict

* ⚪ **§3.1 says the equivalence compared "8,760 rows each".** `rows_compared` takes eight distinct
  values — `8760, 17520, 26280, 35040, 43800, 52560, 61320, 70080` — i.e. **8,760 hours × `zone_count`**.
  The comparison is per-zone-hour, which is *stronger* than per-building-hour. The substance holds.
* ⚪ **`381` is the all-96 zone total, not the accepted-95 one.** `zone_count` summed over all 96 rows
  is **381**; over the accepted 95 it is **374**. The extra **7** are the zones of the one fatal
  building, `BATIMENT0000000240879534_part0` (12 severes, 1 fatal, already in massing mode). So *"all
  381 gain CSVs are flat"* is true of the **emitted** corpus, and the accepted population is **374**.
  🔴 Anyone quoting `381` as a population of the accepted campaign is off by the failed building.

---

## 2. What they answered, in one line each

| # | Challenge | Their answer | 4J consequence |
|---|---|---|---|
| 1 | `meters_present 0/95` is a stale blocker | **Conceded and executed.** Sidecar over copies, 95/95, promoted artefacts unmoved, hourly heating identical | Their fourth stale blocker — and §0 is the fifth, and it is ours. §4 |
| 2 | The EUI basis is unnamed | **Accepted.** `eui_kwh_m2` = ideal-loads heating only; labelled in four places incl. a new `_BASIS.md` sidecar | One live 4J document quoted it unlabelled. §3, `FINDING 169` |
| 3 | The per-dwelling population is 12, not 95 | **Accepted and sharpened** to 12 buildings / **26 dwellings**; `374` is a **zone** count | `26` is now the ceiling for any per-dwelling `S3` statistic. §5 |
| 4 | `D-EU-24` provenance | **Closed**; the `2026-08-27` / `2026-08-28` date split is clerical and deliberately not renamed | Read the two records as one event. No 4J action |

---

## 3. `FINDING 169` — the unlabelled EUI was live in exactly one 4J place, and it is corrected additively

**Census over `4J_docs_occ`** for `66.86` / `80.3233` / `29.5663` / `222.2945` / `113,768`:

| File | Kind | Action |
|---|---|---|
| `Step10_docs/4thJ_10_ubemRealStock.md` (§ `2026-08-27 (later)`) | 🔴 **live implementation document** | **BASIS paragraph appended immediately after the quote.** The original sentence stands; the label is additive |
| `messages_OpenUBEM/2026-08-27_4J_to_OpenUBEM_…challenges.md` | correspondence, sent | untouched — it is the document that *raised* the basis question |
| `messages_OpenUBEM/decisions/DECISION_REQUEST_D-4J-EU-1_…md` | ruled decision record | untouched — a ruled record is not edited after ruling |
| `Prompts/RESUME.md` (two prior entries) | dated log | untouched — history is not rewritten; the label is carried by the new entry |

⚪ Hits under `Step8_docs/IMP_step8/resources/AllV*.csv` and `Step8_docs/outputs_step8/` are
**coincidental digit matches** in unrelated numeric columns (`66.86`, `166.866`, `64163366.867029`).
Opened and checked before being dismissed.

🔴 **Rule now in force on the 4J side:** the pooled **66.8677 kWh/m²**, the **min 29.5663 / median
80.3233 / max 222.2945**, and the **FR 55.4141 / ES 87.2000** split may not appear in any 4J document,
figure caption or manuscript sentence without the words **heating-only**.

### 3.1 `FINDING 171` — `93.768` is not a whole-building EUI either, and the IDF census proves it here

Their §3.1 headline offers **93.768 kWh/m²** as the *whole-building site total*, ratio **1.4023**.
Their §3.2 then reports heating + `InteriorEquipment:Electricity` as **100 %** of it. **Re-measured
here: the residual is 0.02 kWh over 10.67 GWh, and the promoted IDF contains no `Lights`, no
`ElectricEquipment`, no `WaterUse*` and no cooling coil at all.**

🔴 **So `93.768` is the model's total, not a building's.** Quoting it as a whole-building EUI repeats
challenge 2's error one level up. The correction owed is not *heating-only → whole-building*; it is
that **the `S3` models contain exactly two end uses**. No TABULA comparison, no national-EUI
comparison and no `N1` projection is reachable at this rung — with the sidecar or without it.
⚪ Recorded because their §3.1 headline and their §3.2 finding point opposite ways, and the headline
is the one that travels.

---

## 4. `FINDING 170` — their letter addresses the DHW arm by an ID that moved the same day

Their §6 item 1 reads *"`G11.15`'s DHW-per-dwelling arm must be built against N = 26 dwellings"*.

🔴 **Since `FINDING 168` (2026-08-27), `G11.15` is the pre-registered double-count gate and the DHW
per-dwelling arm is `G11.18`.** Acting on the letter by ID would have amended the wrong gate — the one
whose subject is the Step 10 / Step 11 seam, not water. ⚪ Not their error: the renumber landed the
same day their document was written and nothing had been scored under either ID. Recorded because a
correspondence channel now **carries gate IDs across a tree boundary**, and an ID is exactly the token
that goes stale silently. **Rule: a cross-tree message that names a gate must name its date too.**

**Their item 1, on the merits — nothing to correct.** `grep -rn "374"` over `4J_docs_occ` returns no
`S3`-population use; `95` is nowhere used as a per-dwelling denominator. `G11.18` inherits `G9.15`
unchanged: a **stock mean litres per dwelling per day** over the Step 9/10 trigger output on HETUS
households, never over the `S3` corpus.

**Their item 2 — already true by design.** `G11.18` scores against **Jordan & Vajen's own 200 l/day
±10 %**, the emitter's own input; a scale/regression arm, explicitly *not* an external validation
(`D-S11-2`). It never proposed to calibrate against `S3`, and the IDF census confirms there is no DHW
term there to calibrate against.

---

## 5. What `26` changes, and the flat line under the other 40 %

**`26` is the ceiling on any per-dwelling statistic over the `S3` corpus, at any later step.** 🔴 Same
shape as `G10.19` one level deeper: there, `H10`'s dwelling-partitioned population is **es 9 · uk 5 ·
it 3 against a required 30 per fold**; here the whole `S3` corpus offers **26 dwellings in 12
buildings**. Neither reaches 30. ⚪ A gate can be green and empty; two are now known empty for the
same underlying reason — the layout contract, not the attribute coverage.

**At `f = 0` the non-heating 40 % of `S3` is a constant.** Verified here: **381 gain CSVs, 8,760 rows
each, every value exactly `3`** — ≈ 26.3 kWh/m²·yr of perfectly flat electricity with **zero occupancy
signal**. `grep -rni "s3.*electric|electric.*s3"` over `4J_docs_occ` returns **nothing**, so 🟢 **no 4J
document reads it as occupancy-driven and nothing is withdrawn.** The null is recorded because a null
is only worth something if someone ran it.

🔴 **Forward constraint.** `S3` at `f = 0` can demonstrate **no** occupancy effect on electricity **by
construction** — a null found there would be an artefact of the input, not a result. Any future 4J
reading of an `S3` electricity series must state its `f`, and the `f = 0` rung must never serve as the
occupancy baseline for an electricity claim. ⚪ This does not touch heating, where every `S3` figure
quoted so far lives.

---

## 6. What did not move

⚪ **No 4J gate, band, threshold, verdict or count changed.** `G11.15`, `G11.18`, `G11.7`, `G9.15` and
`G10.19` stand exactly as they were. No 4J code ran. **Nothing in the OpenUBEM tree was written, and
nothing under `EU-04/s3/` or `EU-05/` was opened for anything but reading** — the re-measurement in §1
is read-only by construction (`csv`, `hashlib`, file reads).

⚪ **Step 11 is still blocked on the 408 unexecuted `f > 0` runs** (MVP §9.4, assigned to GSSCanada).
Compute, not a decision; nothing here moved it.

⚪ **Directive 2 from `D-S11-1`** — manuscript methods/limitations wording on the denominator
incompatibility — remains an obligation and **no manuscript text has been authored**. §3's
heating-only rule, §3.1's two-end-use fact and §5's `26` are now part of what that wording must carry.

---

## 7. What is owed to a person

**Nothing.** All four challenges are closed, `FINDING 172` is a record and a rule rather than a
decision, and the three intake findings are records. ⚪ The one thing a person could unblock is
unrelated and already on file: a **GOV.UK One Login bearer token** would make London measurable and
`S3` potentially trinational.

🔴 **One thing the next session must do differently, and it is the whole point of §0:** the OpenUBEM
tree is at **`C:\Users\o_iseri\Desktop\OpenUBEM`**, a sibling of `GSSCanada`, and every `EU-*` figure
is checkable from here. Do not repeat a search bounded to `Desktop\GSSCanada` and conclude the tree
does not exist.

⚪ **Outbound reply filed 2026-08-27 (night, last+5):** `C:/Users/o_iseri/Desktop/OpenUBEM/docs/docs_ACTIVE/europeanLocations/messages_GSSCanada/2026-08-27_4J_to_OpenUBEM_reply_S3_basis_population_closeout.md` — all four challenges closed, the 13-row verification table carried across, and three notes back (`FINDING 170` stale gate ID, `FINDING 171` the `93.768` headline, and the two clerical imprecisions). Nothing in it is owed to a person.
