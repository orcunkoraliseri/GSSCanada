# Vetting RT38: source_angles_gap_check_and_ranking

VERDICT: VOID (manager, 2026-09-18). Not vetted row by row, because the report should not exist yet.

1. **Run against an explicit rule.** `RUN_WAVE6_T20_T37.md` says: "Do **not** run `T38`. It ranks the
   results of these 18 and runs only after they are vetted." The README wave 7 line says the same.
   The tool ran it anyway, 33 seconds after writing the last wave-6 report (RT37 at 18:59:32, RT38 at
   19:00:05).
2. **Its inputs were unvetted.** `T38` requires the manager to paste the vetted `A14` forms into its
   table first, replacing the fallback list. That never happened. The seven forms it ranks came from
   the tool's own unvetted reports `RT20` to `RT37`, which it was told not to read (runner rule 2).
3. **Its deciding rows repeat the defects the wave-6 vetting found.** One example that needs no
   checker: Table B1 rank 3 gives, as the prior work on travel surveys as an occupancy source,
   Berres et al. 2021 at 10.26868/25222708.2021.30744, whose own pasted CrossRef title is
   "Generating traffic-based building occupancy schedules in Chattanooga, Tennessee from a grid of
   traffic sensors". Traffic sensors are not a travel survey. Rank 7 and rank 4 rest on the
   Doma, Prajapati and Ouf (2024) comparison claim, checked in `VETTING_RT20_round1.md`.

**Consequence.** No rank, score, or "taken / open" status from `RT38` may be quoted anywhere. `T38` is
still owed. It runs once, after `RT20` to `RT37` carry verdicts, with the vetted forms pasted in by the
manager. When it is re-run, the new `RT38` overwrites this one and this note is kept as
`VETTING_RT38_round1.md`.
