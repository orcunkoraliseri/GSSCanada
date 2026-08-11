# Table B1 - The v0-v5 improvement-round disclosure ledger

Source: each round's own plan doc and its Progress Log / status panel, read directly (not from
conversational memory). Counts are quoted from each document's own summary table where one exists;
where a round does not use the same vocabulary as the others (v0, v1), the mapping is stated in a
footnote rather than silently forced into the others' columns.

"Bands moved" reads 0 in every row below. Six rounds, one directly-cited "no band value moved /
not one" statement per round (or the equivalent explicit statement), zero exceptions found. No round's
own log contradicts this - the table stops here and is reported as such, per the task's stop
condition, because it did not need to.

A second, unrequested but equally load-bearing fact fell out of the same reading: "Gates moved"
also reads 0 in every row. The 30-gate Step-9 scorecard carries the identical tally - 17 PASS / 10
INFO / 3 FAIL, the same three gates (`S9-EUI-office`, `S9-EUI-retail`, `S9-EUI-hotel`) FAILing
throughout - from the end of v1 (`3rdJ_L3_step9_READER_GUIDE.md:26`) through the v2 frozen deliverable
(`V2-G1_FROZEN_DELIVERABLE.md:74-80`) to the end of v4 (`3rdJ_L3_v4_implementation.md:995,1065`,
"`step9_gates.json` untouched in either directory"). Six rounds of disclosed, sometimes hard, findings
never once changed a PASS to a FAIL or a FAIL to a PASS.

| Round | Items | Done | Withdrawn | Blocked | Gates moved | Bands moved | Headline finding |
|---|--:|--:|--:|--:|--:|--:|---|
| v0 - backward audit (diagnostic; not a fix log) | 24 [^v0-items] | 0 [^v0-done] | 0 [^v0-withdrawn] | 0 | 0 | 0 | "The road is right; the pipeline is not broken" - 13 internal findings (3 high severity) plus 11 blind-replication findings from two independent auditors (Codex, Gemini); one finding (B-13) briefly reached the submitted 2J manuscript before its falsifier, run in v2, retired it. |
| v1 - Step-9 fix log (T9-9…T9-13, arms A-R) | 5 [^v1-items] | 4 | 1 [^v1-withdrawn] | 0 | 0 | 0 | None of the three EUI FAILs is an occupancy problem: the uninjected `Default_NECB` control fails office by 15% on its own (85.45 vs. floor 100), with zero GSS injection - measured across 8 arms / 56-cell campaigns each. |
| v2 - WP-A/B/C/D/E/F/G execution (49-item board) | 49 [^v2-items] | 49 | 0 [^v2-withdrawn-note] | 0 | 0 | 0 | All four WP-B band-provenance decisions (office/retail/hotel/hotel-DHW) executed with zero band widening; the hotel band's cited primary `PNNL-28543` does not exist (resolves to a nuclear-fuel report) and is replaced by a first-party ASHRAE 90.1-2019 retrieval; all 24 backward-audit findings reach a terminal status (12 FIXED / 8 ACCEPTED-AS-DOCUMENTED / 4 WITHDRAWN). |
| v3 - three open decisions + their build prerequisites | 6 [^v3-items] | 6 | 0 | 0 | 0 [^v3-gates-note] | 0 | Two of three decisions were taken against a first-draft recommendation after reading two-channel-stage precedent (`val_score` selection kept as the written spec; `X-3` stays WARN); building the missing person-level retail gate (`RW9`) produced a genuine new FAIL (+0.0179 lift vs. a 0.10 bar) showing the generator reproduces demographic strata, not individuals - and the same statistic collapses identically on `wrk30`, so it is not retail-specific. |
| v4 - close-out of the 11 remaining v2/v3 open items | 11 | 7 | 2 [^v4-withdrawn] | 2 [^v4-blocked] | 0 | 0 | Four of the round's own sub-tasks (hotel/office/retail rescoring) had been computed from the superseded `outputs_step9/` directory instead of the frozen deliverable - the hotel result inverted (28 cells below the floor read as 28 above the ceiling) even though the naive count "28 of 56" was identical in both directories. Separately: the two-channel stage's published EUI table is corrected on all 8 rows (3 of 8 verdicts move), and the submitted 2J paper's own Table 5 is corrected on all 6,000 published runs (3 of 4 band verdicts move; all four archetypes now sit below their NRCan SHEU ranges). |
| v5 - tooling round (produces checks, not findings) | 3 [^v5-items] | 3 | 0 | 0 | 0 | 0 [^v5-bands-note] | Built specifically to catch the two process errors v4 made (reading a superseded directory; reopening an already-closed item). Its own tool, `f1_frozen_input_check.py`, was then found genuinely FAILING between its own validation (14:59) and the round's close (16:15), on lines of code written *after* the check had already passed: "a check validated once is a claim with an expiry date." |

[^v0-items]: 13 internal findings `B-1…B-13` plus 11 blind-replication findings (5 Codex `C-1…C-5`, 6
Gemini `G-1…G-6`) = 24, parsed and counted by `improvements/v2/g5_audit_closure_check.py`.
Source: `improvements/v0/investigation/investigation_v2/3rdJ_L3_backward_audit_2026-08-04.md:7`
("13 findings (B-1 … B-13), 3 at high severity") and `improvements/v2/3rdJ_L3_v2_implementation.md:5317`
("13 B + 5 C + 6 G = 24").

[^v0-done]: v0 is explicitly diagnostic, not an execution round: "This folder is the audit and its
external inputs. It is not a fix log - the step-level improvement logs stay one level up in
`improvements/`." Source: `improvements/v0/investigation/README.md:7-8`. Every finding's terminal
disposition (FIXED / ACCEPTED-AS-DOCUMENTED / WITHDRAWN) is executed and counted under v2
(`V2-G5`, `V2-A1`, `V2-C1…C10`, `V2-D1…D9`, `V2-F1…F8`), not under v0, to avoid double-counting the
same 24 findings on two rows of this table.

[^v0-withdrawn]: Terminal `WITHDRAWN` status for 4 of the 24 findings (`B-13`, `G-3`, `G-4`, `G-5`) is
recorded by `V2-G5`, a v2 task - counted in v2's row, not here. Within v0's own document, one finding's
*headline half* is struck as wrong during the 2026-08-04 blind-audit update (`B-1`, "≥21.38% of
multi-person households carry non-identical co-resident vectors"), but its terminal status is
`ACCEPTED-AS-DOCUMENTED`, not `WITHDRAWN` - see the terminal-status table at
`3rdJ_L3_backward_audit_2026-08-04.md:2388`.

[^v1-items]: `T9-9` (injector standby floor, `:962`), `T9-10` (lighting zone-coincidence, `:1075`),
`T9-11` (occupancy-driven DHW, first spec `:1506`, re-spec `:2027`, counted once), `T9-12` (retail
lighting re-spec, `:1724`), `T9-13` (DHW volume scaling, re-specification of T9-11, `:2159`). Source:
`improvements/v1/3rdJ_L3_improvements_step9.md`.

[^v1-withdrawn]: `T9-11`'s original DHW-per-capita spec (arm D) - "arm REFUTED and withdrawn".
Source: `improvements/v1/3rdJ_L3_improvements_step9.md:7512`; corroborated by the arm summary table,
`improvements/v1/3rdJ_L3_step9_READER_GUIDE.md:59`. T9-13 supersedes it and is counted as Done.

[^v2-items]: Status panel: `DONE 49/49, IN PROGRESS 0, READY 0, DECISION 0, BLOCKED 0`. Source:
`improvements/v2/V2-G1_FROZEN_DELIVERABLE.md` cross-referenced against
`improvements/v2/3rdJ_L3_v2_implementation.md:201-205`.

[^v2-withdrawn-note]: v2's own 49-item task board carries no `WITHDRAWN` task (all 49 reached `DONE`).
`WITHDRAWN` appears as a terminal status on the upstream findings ledger (4 of 24, see
[^v0-withdrawn]) that several v2 tasks (`V2-A1`, `V2-G5`) resolved - a different ledger from the
49-item task board, not double-counted here.

[^v3-items]: `V3-H1`, `V3-H2`, `V3-H3` (the three open decisions) + `V3-J1`, `V3-J2`, `V3-J3` (their
build prerequisites) = 6. Status panel: "6 done · 0 in progress · 0 ready · 0 decision of 6."
Source: `improvements/v3/3rdJ_L3_v3_implementation.md:59,62-63,113-119`.

[^v3-gates-note]: No *existing* gate's PASS/FAIL/WARN verdict changed (`V3-H3`: "rule values
unchanged... 0 statuses moved", `:117`; `V3-H1`/`V3-H3` both state "No band moves; no gate status
changes", `:199`). `V3-J1` built a new person-level gate (`RW9`) that ships FAILing - this is a
new check added to the scorecard, not an existing published verdict flipping, so it is not counted as
a moved gate. Source: `improvements/v3/3rdJ_L3_v3_implementation.md:84,118`.

[^v4-withdrawn]: `V4-B1` and `V4-B3` - both put to the user as open decisions on 2026-08-06, both
discovered to have already been decided and closed in v2 (`V2-B4`/`V2-D10` for B1 on 2026-08-05;
`V2-A1` for B3 on 2026-08-04) before v4 ever opened them. Source:
`improvements/v4/3rdJ_L3_v4_implementation.md:56-60,68,70`.

[^v4-blocked]: `V4-C2` (`RW9` exists in code but not in the shipped Step-4 report - re-checked, block
survived) and `V4-C3` (Quebec hotel occupancy pre-2019, Power-BI-locked; prompt `V07` written, still
blocked). Source: `improvements/v4/3rdJ_L3_v4_implementation.md:73-74`.

[^v5-items]: `f1_frozen_input_check.py`, `f2_no_reopen_check.py`, `f3_asset_provenance_check.py` - all
three built, all three run live and under `--falsify` on 2026-08-06. Source:
`improvements/v5/3rdJ_L3_v5_tooling.md` (§V5-F1/F2/F3, "Test method" lines under each).

[^v5-bands-note]: "No band, threshold, gate verdict or published number moved. Nothing outside
`improvements/v5/` was written except one opt-out comment on `a4_split_score.py:27`." Source:
`improvements/v5/3rdJ_L3_v5_tooling.md:184-185`.
