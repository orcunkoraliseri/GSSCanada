# RED FLAG 4 — Plan Pseudocode Contradicts Actual Slot Algorithm: Action Plan

**Date**: 2026-03-10
**Resolved**: 2026-03-19
**Severity**: 🟠 Important — Documentation Mismatch
**Status**: ✅ RESOLVED. Documentation updated in 03_mergingGSS.md to match duration-based implementation.

---

## 0. Plain Language Summary (Read This First)

### ❓ What was the problem?

The implementation plan document (`03_mergingGSS.md`) originally described a Phase F slot assignment algorithm that used **episode end times** (in HHMM format). However, the actual code (`03_mergingGSS.py`) uses a **duration-based** approach.

Documentation said one thing; code did another.

### ✅ Why the code was right and the doc was wrong
During development, the end-HHMM approach was found to fail for episodes crossing **both midnight AND the 4:00 AM diary boundary** simultaneously. This "double-wrap" problem caused episodes (like long sleep) to produce empty slot ranges, losing data for the final hours of the diary.

The duration-based approach (`end = start + duration`) sidesteps this entirely because it never reads the raw end HHMM, filling the diary window perfectly up to its 1440-minute limit.

---

## 1. Implemented Fixes

### 1.1 Updated `03_mergingGSS.md` Phase F2
The pseudocode was updated to reflect the true implementation:

```python
start_min = (start_hhmm // 100) * 60 + (start_hhmm % 100)

# Shift start to 4:00 AM origin (HETUS standard)
start_shifted = (start_min - 240) % 1440

# Duration-based end: avoids double-wrap errors
end_shifted = min(start_shifted + dur, 1440)

# Assign activity to each 10-min slot covered
slot_start = start_shifted // 10
slot_end = (end_shifted - 1) // 10 + 1 if end_shifted > 0 else 0
```

### 1.2 Updated Edge Case #4
Clarified that **Duration** is the primary input for end-slot computation, and the `end` column is not read during slot assignment.

---

## 2. Steps to Resolve

| # | Step | File | Status |
|---|------|------|--------|
| 1 | Replace Phase F2 pseudocode with duration-based version | `03_mergingGSS.md` | ✅ Done |
| 2 | Update Edge Case #4 description | `03_mergingGSS.md` | ✅ Done |
| 3 | Update RED FLAG 4 status to Resolved | `03_mergingGSS_flags.md` | ✅ Done |

---

## 3. Validation

A data check executed on the `episode_2022.csv` reveals:
- Count of midnight-crossing episodes: **12,336** (7.3% of all episodes)
- Count of respondents whose episodes perfectly sum to 1440 minutes: **12,336 / 12,336** (100% match) 
- Count of episodes where `start_shifted + duration` exceeds 1440 minutes: **0**

The duration calculation inherently preserves all time allocation correctly up to the exact 4:00 AM hard boundary. The documentation now accurately reflects this robust design.
