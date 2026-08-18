# `act2` coverage — three countries, two bases, never mixed

Work item 3.2-bis. This file closes the "Italy is not yet measured" gap and adds the post-filter
(`harmonised.parquet`) accounting the item also requires. It does **not** decide whether `ACT2` is
serialised — that is `outputs_step3/act2_tuple_measurement.md` plus the author's ruling.

Every rate below states its numerator, its denominator, and the table it was read from. No rate is
ever quoted against a base it was not measured on.

---

## 1. Episode-level share, Step 1's accepted run

Source: `Step1_docs/outputs_step1/run_20260816-2210/gate_report_step1_{spain,uk,italy}.txt`, the
`G1.4` line's `act2_raw states` (`recorded_with_value`), against `episodes loaded` from the same file.
This is the **pre-Step-2-filter** population (raw episodes as read, before the age-11 floor and the
diary-origin split).

| Country | recorded_with_value | total episodes | share | vs. task doc's pre-measured figure |
|---|---:|---:|---:|---|
| ES | 80,800 | 430,754 | **18.76 %** | quoted 18.8 % — re-derived, **matches** |
| UK | 163,105 | 587,632 | **27.75 %** | quoted 27.75 % — re-derived, **matches** |
| IT | 257,998 | 1,077,657 | **23.94 %** | **not previously measured — new** |

🔴 UK note: at this same baseline, `G1.4` **FAILs** for the UK, but not because of `act2` coverage
itself — the failure is one out-of-list code, `act2_raw='4276'`, appearing once with no label anywhere
in the delivered UK dictionary (`F-UK-9`, already recorded in Step 1). It does not change the coverage
rate above (that code is still counted inside `recorded_with_value`), but it means one UK secondary-code
value has no known meaning. Flagged, not resolved here — Step 1's own document owns it.

---

## 2. Slot-level share — **Spain only**

Source: Spain's `G1.11` line, "for reference only, never a gate input": *"340,269 of 2,778,480 raw
slots are non-blank ASECU — a different, slot-level quantity."*

| Country | non-blank slots | total slots | share |
|---|---:|---:|---:|
| ES | 340,269 | 2,778,480 | **12.24 %** (quoted 12.2 % — matches) |

🔴 **The UK and Italy ship episodes natively and have no slot base at all.** Confirmed directly from
`Step1_docs/4thJ_01_corpusAcquisition.md`: the UK reader "reconstructs nothing, the opposite of the
Spanish reader's slot-collapsing" (§1.3, UK); Italy's diary is delivered "with explicit
`oraini`/`minini`/`orafin`/`minfin`. No slot reconstruction" (§1.3, Italy). For these two countries
**the episode share in §1 is the only rate that exists**, and it is never to be compared to Spain's
slot share above — the two differ by a factor that depends on episode length, i.e. instrument design,
not respondent behaviour.

---

## 3. Post-filter, `harmonised.parquet` base — episode share, own column

The corpus is built on the **post-filter** population (age ≥ 11, diary-origin split applied), not on
Step 1's raw read. Source: `Step2_docs/outputs_step2/filter_report_{es,uk,it}.md`, regenerated
2026-08-17 12:39 as part of the D-S2-18/D-S2-19 additive round — these are the harmonisation run's own
per-country logs, read directly, no parquet scan needed for this number.

| Country | `act2_raw` recorded_with_value | output episodes | **post-filter episode share** |
|---|---:|---:|---:|
| ES | 80,494 | 446,547 | **18.03 %** |
| UK | 159,302 | 567,381 | **28.08 %** |
| IT | 242,281 | 1,010,140 | **23.99 %** |

These three numbers sum to the accepted `harmonised.parquet`'s 2,024,068 rows exactly
(446,547 + 567,381 + 1,010,140), confirming this is the same table Task B would build against.

🔴 **This is `act2_raw`, not `act2`.** The tuple, if ever serialised, would read the *mapped* target
column `act2` (2-digit, D-S2-7), not the raw carrier. The two differ by the "unmapped" defect recorded
in the same `filter_report_*.md` files: a non-null, non-blank `act2_raw` that failed to map to a target
code leaves `act2` **null**, which collapses into the *same* null state that "not recorded" would use
(`D-S2-12` says null means "not recorded"; in this delivery it always means "unmapped", since the
literal not-recorded state never occurs for any country — `not_recorded(null)=0` everywhere).

| Country | unmapped-with-value episodes (`act2` null despite a raw value) | `act2` recorded_with_value | mapped share |
|---|---:|---:|---:|
| ES | 57 | 80,437 | 18.02 % |
| UK | 530 | 158,772 | 27.98 % |
| IT | 0 | 242,281 | 23.99 % |

The gap is small (57 and 530 episodes) but real, and it means the field actually usable in a tuple is
very slightly narrower than the raw-carrier coverage rate above. Recorded here because a later reader
of this file could otherwise quote the `act2_raw` row as if it were what the encoder would emit.

---

## 4. Mixing within an episode (first-of-run aggregation)

Task doc: *"Spain has 11,216 episodes mixing blank and non-blank `ASECU` and 13,009 carrying more than
one distinct value ... measure the same two counts for Italy and the UK."*

| Country | mixed blank/non-blank | multi-value | basis |
|---|---:|---:|---|
| ES | **11,216** | **13,009** | as given in `4thJ_03_serialisation.md`, from Step 1's Spain gate re-run |
| UK | **N/A — structurally 0** | **N/A — structurally 0** | native episodes, see below |
| IT | **N/A — structurally 0** | **N/A — structurally 0** | native episodes, see below |

🔴 **This is not a measured zero — it is a structural one, and the difference matters.** Spain's two
counts exist because Spain's episodes are *reconstructed*: several raw 10-minute slots, each carrying
its own `ASECU` value, are collapsed under a first-of-run rule into one episode, so a run can legitimately
mix blank and non-blank, or several distinct codes, across the slots it absorbs. **The UK and Italy ship
one raw diary row per episode already** — confirmed above in §2 — so there is nothing to mix: each
episode's `act2_raw` comes from exactly one raw record, never several. The two counts are inapplicable
by construction, not zero-by-coincidence. Not independently re-derived by a fresh script against
`episodes_uk.parquet` / `episodes_italy.parquet` (see the implementation doc's WHAT I DID NOT VERIFY) —
the argument rests on Step 1's own reader documentation, which states this explicitly for both countries.

Consequence for the aggregation-rule question 3.2-bis raises ("if this field is ever serialised,
first-of-run is a decision that has to be taken deliberately"): **the question only exists for Spain.**
The UK and Italy have no first-of-run rule to defend or replace, because they never aggregate slots into
episodes in the first place.

---

## Summary table (all rates, one place)

| Country | Step 1 episode share | Step 1 slot share | Post-filter episode share (`act2_raw`) | Post-filter episode share (`act2`, mapped) |
|---|---:|---:|---:|---:|
| ES | 18.76 % (80,800/430,754) | 12.24 % (340,269/2,778,480) | 18.03 % (80,494/446,547) | 18.02 % (80,437/446,547) |
| UK | 27.75 % (163,105/587,632) | no slot base | 28.08 % (159,302/567,381) | 27.98 % (158,772/567,381) |
| IT | 23.94 % (257,998/1,077,657) | no slot base | 23.99 % (242,281/1,010,140) | 23.99 % (242,281/1,010,140) |

**This file is now complete for all three countries.** It does not decide serialisation — that is
`act2_tuple_measurement.md`'s token-cost result plus the author's ruling.
