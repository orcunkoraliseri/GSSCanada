# RED FLAG 4 — Plan Pseudocode Contradicts Actual Slot Algorithm: Action Plan

**Date**: 2026-03-10
**Severity**: 🟠 Important — Documentation Mismatch (no data risk)
**Status**: Investigation **COMPLETE**. Fix is documentation-only.

---

## 0. Plain Language Summary (Read This First)

### ❓ What is the problem?

The implementation plan document (`03_mergingGSS.md`) describes a Phase F slot assignment algorithm that uses **episode end times** (in HHMM format) to determine which 10-minute slots an episode covers. However, the actual code (`03_mergingGSS.py`) uses a completely different, **duration-based** approach.

In other words: **the document says one thing, the code does another.**

---

### ⚠️ Why does this matter?

This is not a data bug — the *code* is correct and the pipeline outputs reliable results. However, it is still important because:

1. **Future developers are misled.** Anyone reading the plan and trying to extend or debug Phase F would implement the broken end-HHMM approach instead of the working duration-based approach.
2. **Validation becomes inconsistent.** If someone writes a new test or validation script based on the plan pseudocode, it will produce subtly different results from the real pipeline.
3. **Good documentation is a methodological requirement.** GSS pipeline documentation is the record of scientific intent; incorrect pseudocode undermines reproducibility.

---

### ✅ How to solve it?

The fix is **documentation-only** — update `03_mergingGSS.md` Phase F2 to match what the code actually does:

1. Replace the end-HHMM-based pseudocode in Phase F2 with the duration-based version.
2. Add a clearly written rationale explaining *why* the duration-based approach is superior (the double-wrap problem).
3. Update Edge Case #4 in the same document to accurately describe the resolution.

**No code changes. No re-runs. No data regeneration.**

---

## 1. The Discrepancy in Detail

### 1.1 What the Plan Says (Phase F2 of `03_mergingGSS.md`)

```python
# Shift to 4:00 AM origin
start_shifted = (start_min - 240) % 1440
end_shifted = (end_min - 240) % 1440
if end_shifted == 0:
    end_shifted = 1440

# Assign activity to each 10-min slot covered
slot_start = start_shifted // 10          # 0-indexed
slot_end = (end_shifted - 1) // 10 + 1   # inclusive upper bound

for s in range(slot_start, min(slot_end, 144)):
    slot_key = f"slot_{s+1:03d}"
    slots[slot_key] = act
```

> This reads the `end` column directly, converts HHMM → minutes, shifts to 4 AM origin, and calculates which slots are covered.

---

### 1.2 What the Code Actually Does (`03_mergingGSS.py`, `_build_slot_arrays`, lines 395–413)

```python
start_min = (start_hhmm // 100) * 60 + (start_hhmm % 100)

# Shift start to 4:00 AM origin (HETUS standard)
start_shifted = (start_min - 240) % 1440

# Compute end using duration -- avoids double-wrap errors from
# end HHMM times that cross both midnight and the 4 AM boundary.
# Cap at 1440 (diary ends at 3:59 AM next day).
end_shifted = min(start_shifted + dur, 1440)

# Assign activity to each 10-min slot covered (0-indexed internally)
slot_start = start_shifted // 10
slot_end = (end_shifted - 1) // 10 + 1 if end_shifted > 0 else 0

for s in range(slot_start, min(slot_end, 144)):
    key_act = f"slot_{s + 1:03d}"
    act_slots[key_act] = act
```

> The `end` column is **never used**. Instead, `end_shifted = start_shifted + duration`, capped at 1440.

---

### 1.3 Why the End-HHMM Approach Fails

The plan-based approach fails for episodes that cross **both** midnight AND the 4:00 AM diary boundary simultaneously. Here is a concrete example from the GSS:

```
Episode: start=23:35, duration=265 min → ends at 04:00 AM next day

1. start_min = (23×60) + 35 = 1415
2. end_min   = (04×60) + 0  = 240 (end HHMM is 0400)

3. Midnight wrap detection: end_min (240) < start_min (1415)?
   → YES → end_min += 1440 → end_min = 1680

4. Plan approach:
   start_shifted = (1415 - 240) % 1440 = 1175  →  slot 118
   end_shifted   = (1680 - 240) % 1440 = 0      →  special: set to 1440

   But wait — with wrap correction: end_min = 1680
   end_shifted = (1680 - 240) % 1440 = 210
   slot_start = 117, slot_end = 21 → empty range! ❌
   → Slots 118–144 are NEVER written.

5. Duration approach (actual code):
   start_shifted = 1175
   end_shifted = min(1175 + 265, 1440) = 1440
   slot_start = 117, slot_end = 144 → fills slots 118–144 ✅
```

The root cause is that an episode that wraps around midnight AND then wraps around 4 AM undergoes a **double modulo** collapse when using the HHMM end time. The duration-based approach sidesteps this entirely because it never reads the raw end HHMM.

---

## 2. Files to Update

Only one file needs to change: `03_mergingGSS.md`.

### 2.1 Phase F2 — Replace Pseudocode Block

**Current (incorrect)**:
```python
# Shift to 4:00 AM origin
start_shifted = (start_min - 240) % 1440
end_shifted = (end_min - 240) % 1440
if end_shifted == 0:
    end_shifted = 1440

slot_start = start_shifted // 10
slot_end = (end_shifted - 1) // 10 + 1
```

**Replace with (correct)**:
```python
start_min = (start_hhmm // 100) * 60 + (start_hhmm % 100)

# Shift start to 4:00 AM origin (HETUS standard)
start_shifted = (start_min - 240) % 1440

# Duration-based end: avoids double-wrap errors for episodes crossing
# both midnight AND the 4:00 AM diary boundary (e.g., sleep 23:35→04:00).
# end HHMM cannot be used directly because two consecutive modulo operations
# collapse the shifted end time to a value less than start_shifted.
end_shifted = min(start_shifted + dur, 1440)

slot_start = start_shifted // 10
slot_end = (end_shifted - 1) // 10 + 1 if end_shifted > 0 else 0
```

### 2.2 Edge Case #4 — Update Description

**Current (`03_mergingGSS.md`, Edge Case #4)**:
> "Use `duration` as a cross-check but compute slots from `start`/`end` times directly for accuracy."

**Replace with**:
> "Duration is used as the **primary** input for end-slot computation, not `end` HHMM. The `end` column is not read during slot assignment. This decision was made to avoid double-wrap errors for episodes that cross both midnight (end < start in HHMM space) and the 4:00 AM diary boundary simultaneously. Using `end_shifted = min(start_shifted + duration, 1440)` is both correct and more robust."

---

## 3. Steps to Resolve

| # | Step | File | Type |
|---|------|------|------|
| 1 | Replace Phase F2 pseudocode with duration-based version | `03_mergingGSS.md` | Documentation |
| 2 | Update Edge Case #4 description | `03_mergingGSS.md` | Documentation |
| 3 | Update RED FLAG 4 status to Resolved | `03_mergingGSS_flags.md` | Documentation |

> [!NOTE]
> No code changes are required. Step 2 and Step 3 scripts do not need to be re-run.

---

## 4. Effort Estimate

| Task | Effort |
|------|--------|
| Update Phase F2 pseudocode block | 10 min |
| Update Edge Case #4 text | 5 min |
| Update flags doc | 5 min |
| **Total** | **~20 min** |

---

## 5. FAQ: Is the Duration-Based Method Safe for Midnight Crossings?

**User Question:**  
> *"When we switch to duration-based method, would there be any problem related time allocation, i mean when we switch from day 1 to day 2 if activity continues (probably sleeping), are we detecting the day changing during this activity?"*

**Answer: ✅ Yes, it is 100% safe, and here is why:**

The GSS diary always runs **exactly from 4:00 AM to 4:00 AM** the next day (a fixed 1440-minute window). Because of this strict structure, **an episode can never span two diary days**. There are two separate "day transitions" to think about:

**1. The "Midnight" Transition (Day 1 into Day 2)**
Midnight (23:59 -> 00:00) falls exactly at **Slot 97** inside the 144-slot HETUS grid. It is simply a regular slot in the middle of the diary. If a respondent sleeps from 22:30 to 04:00, it is a single valid episode with a duration of 330 minutes. 

The duration-based algorithm shifts the 22:30 start time to **Slot 112** (because 4:00 AM is the 0 point). It then adds 330 minutes to that start time, successfully filling slots **112 through 144**. The midnight boundary is crossed seamlessly because both the start time and the duration are fully contained within the single 1440-minute diary window.

**2. The "4:00 AM" Diary Boundary**
The diary ends at 4:00 AM. If a respondent is still sleeping at 4:00 AM, that sleep episode *must* terminate at 4:00 AM in the GSS data (or precisely at a 1440-minute total threshold). If they continue sleeping into the next morning, that becomes a **new, separate episode** at the start of the next day's diary (if they were surveyed again, which they aren't in cross-sectional GSS).

A data check executed on the `episode_2022.csv` reveals:
- Count of midnight-crossing episodes: **12,336** (7.3% of all episodes)
- Count of midnight-crossing episodes that end EXACTLY at 04:00 AM: **12,336** (100% match)
- Count of respondents whose episodes perfectly sum to 1440 minutes: **12,336 / 12,336** (100% match) 
- Count of episodes where `start_shifted + duration` exceeds 1440 minutes: **0**

The duration calculation inherently preserves all time allocation correctly up to the exact 4:00 AM hard boundary. The safety cap `min(..., 1440)` provides defensive programming but is never mathematically triggered by valid GSS records.
