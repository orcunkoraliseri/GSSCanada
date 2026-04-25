Use the **reviewer** agent in **MODE B** (execution review).

Read each task document for this loop, including the Progress Log chapter the reporter just appended. Read `.claude/progress.md`. Read every modified source file listed in the progress entries.

For each completed task, verify per the `@code-review` skill execution-mode checklist:
- Code matches the stated Expected Result.
- Test Method passes (or skip is documented).
- No regressions or broken imports.
- EnergyPlus schedule arrays are length 8760 (or 17520 / 105120).
- Every eppy IDF mutation is followed by `idf.save()`.
- No hardcoded GSS/Census/IDF/EnergyPlus paths.
- No raw microdata rows in any output or log.
- `0_Occupancy/DataSources_*` and protected ML files untouched.
- Pandas merges have no silent index misalignment.
- Concurrency uses joblib loky.

Output to terminal only. Per-task line:
`<TASK_ID> | PASS | NEEDS_FIX | FAIL — <file:line — concrete defect>`

End with overall:
`VERDICT: APPROVED | NEEDS_REVISION | BLOCKED`