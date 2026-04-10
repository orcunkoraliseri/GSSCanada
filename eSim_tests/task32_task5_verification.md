# Task 5 Verification Report — Task 32 Step 1

**Date:** 2026-04-09  
**Script:** `eSim_tests/run_task32_task5_verification.py`  
**Batch analysed:** `Neighbourhood_Comparative_1775582790`  

---

## Stage A — Code Inspection

| Option | Lines | Marker |
|--------|-------|--------|
| Option 6 (comparative neighbourhood) | `main.py:1176-1201` | ✅ |
| Option 7 (batch comparative neighbourhood) | `main.py:1993-2017` | ✅ |

Sample (Option 6): `# Per-building SSE matching — same logic as single-building mode (Task 5)`

---

## Stage B — Per-Building HH IDs × 6 Scenarios

**Batch directory:** `C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\BEM_Setup\SimResults_Schedules\Neighbourhood_Comparative_1775582790`  

| Scenario | Building 1 | Building 2 |
| --- | --- | --- |
| 2005 ✅ | HH1631 (sz=1) | HH235 (sz=1) |
| 2010 ✅ | HH1748 (sz=1) | HH2737 (sz=1) |
| 2015 ✅ | HH2531 (sz=1) | HH29773 (sz=1) |
| 2022 ✅ | HH1255 (sz=1) | HH1277 (sz=1) |
| 2025 ✅ | HH29925 (sz=?) | HH3077 (sz=1) |
| Default ✅ | N/A | N/A |

*(sz = hhsize from BEM_Schedules CSV; ✅ = no Severe Error)*

---

## Verification Assertions

**✅ PASS — Per-building HH IDs differ between 2005 and 2022 scenarios**  
2005 IDs=['1631', '235'], 2022 IDs=['1255', '1277'], diff=['1255', '1277', '1631', '235']  

**✅ PASS — All 6 scenarios complete without Severe Error in EnergyPlus log**  
Clean=['2005', '2010', '2015', '2022', '2025', 'Default'], Failed=[], Missing=[]  

**✅ PASS — hhsize_profile preserved across year scenarios**  
Base 2005 sizes=['1', '1']; mismatches=none  

---

## Sign-off Verdict

**Verdict: PASS ✅**  

Per-building SSE matching in Options 6 and 7 is confirmed in production code at `main.py:1176-1201` and `main.py:1993-2017`. The most recent neighbourhood comparative batch shows: (1) different HH IDs selected per scenario (per-scenario re-matching is live); (2) all 6 EnergyPlus scenarios completed without Severe Error; (3) hhsize_profile preserved across all year scenarios.

**Task 5 ✅**
