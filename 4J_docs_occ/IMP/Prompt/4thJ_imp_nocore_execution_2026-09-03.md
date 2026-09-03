# Session task — execute the no-core review, IMP §12 boxes 2 to 8, after the author's rulings

**Written** 2026-09-03 (last+33, same session that filed the review) · **For** the next session, opened with this file's path and "continue".
**Governing document** `4J_docs_occ/IMP/docs/2026-09-03_nocore-pipeline-review-improvements.md` — read its **§0, §11, §12 and §13 first**; do not re-derive them. Everything below is the run-book for its §12.
**Also binding** `4J_docs_occ/Prompts/RESUME.md` — the last+33 lead block (§0–§2) and the last+32 block **§1–§5** (the five rules, the Step 10 state, the EU 149 state, the never-quote list, where things live). Read them before touching anything.
**Memory** `~/.claude/projects/C--Users-o-iseri-Desktop-GSSCanada/memory/` — `project_4j_hetus_llm.md` (the END is latest; read the last two entries), `feedback_board_live_artifact_is_master.md`, `feedback_gates_must_be_seen_failing.md`.

**Role: executor.** You apply what the author has ruled, additively, in the order §12 gives, and you see each check felled by its perturbation before you tick its box. You do not design gates for a step that is not ruled, you do not choose thresholds, and 🔴 **you never move a threshold, re-score a closed gate, retrofit a manifest, or run a cell.** A check that does not fall when it should is a result: write `SEEN NOT FAILING` and stop on that item.

---

## 0. WHERE THINGS STAND WHEN THIS SESSION OPENS

The owner ruled the **no-core regime** on the OpenUBEM side (`D-EU-79`/`80`/`81` on 2026-09-02, `D-EU-82`–`D-EU-88` on 2026-09-03): a floor plate divides into **dwellings only**, no core, corridor, access band or unconditioned zone; every square metre belongs to a flat; nothing narrower than 2 m; one flat = one zone. The engine `openubem/geometry/european_residential.py` is **still core-era** (carry-in "identified, not ordered"); only the rule-bench `scripts/eu21/07_nocore_tests.py` implements no-core; `D-EU-84` and `D-EU-87` are open; `D-EU-55` forbids any EnergyPlus run without the owner's own sentence.

The 4J review of Steps 0–11 is **filed** in the governing document: nine items I-1…I-9, **three decisions waiting on the author** (§11), **nothing applied** except §12 box 1 (`FINDING 195`/`196` logged in Step 10, master-plan entry, RESUME lead block, board merged and republished — `FINDING 197`). Commit `3ef7c393` on `main` of `GSSCanada-main` carries all of it.

| decision | question | recommended |
|---|---|---|
| `D-IMP-1` | dated no-core header on the `IMP_step8` core/corridor plan, SUPERSEDED markers, "no circulation zone" limitation | **(a)** |
| `D-IMP-2` | register the no-core real-stock campaign as **Step 12 / `G12.x`**, own prereg, spec now, compute only after the OpenUBEM blockers clear | **(a)** |
| `D-IMP-3` | one independent series per drawn flat, emission sized per district, all drawn storeys eligible | **(a)** |

---

## 1. FIRST ACTION — FIND THE RULINGS, OR ASK

1. Look for the author's rulings in this order: the message that opened this session; a docket in `IMP/docs/DONE/` named for `D-IMP-1/2/3`; a dated note appended to the governing document's §11.
2. **If ruled:** write the rulings **verbatim** into a docket `IMP/docs/DONE/<today>_D-IMP-1_D-IMP-2_D-IMP-3_nocore-review-rulings.md` (the 2026-08-22 dockets in that folder are the shape), then execute §2 below in order.
3. **If not ruled:** ask in **one line** — `Waiting on you: D-IMP-1, D-IMP-2, D-IMP-3 --- recommend (a) on all three.` — and **stop**. Do not start any box on a guess. Do not do the "no decision needed" boxes first to look busy; box 3 (I-9) is the only one that may run without a ruling, and only if the author says so in the opening message.
4. A ruling other than (a) is executed as ruled. **(c) of `D-IMP-1` is "delete the core plan"** — if ruled, back up first and record what was removed in the docket; (b) of `D-IMP-2` (amend Step 10 in place) contradicts the Overview's own rule at `Overview.md:683` and must be flagged **once**, then executed if reaffirmed.

---

## 2. ORDER OF WORK — §12 BOXES 2 TO 8, WITH THE CHECK THAT CLOSES EACH

Tick a §12 box **only** when the item is applied **and** its perturbation has been seen felling the check it guards. Append one `§13` ledger row per box. Every edit is additive; every file gets a backup first (`cp X X.bak_nocore_exec`) and the backup is verified non-empty (`[ -s "$BK" ]`) before anything is written.

### Box 2 — I-1, on `D-IMP-1`(a)

* **Target** `Step8_docs/IMP_step8/4thJ_08_bemSimulation_IMP.md`. Add a **dated no-core regime header** above the title (the device the OpenUBEM tree used on 2026-09-02: a boxed block, date, the ruling quoted, "everything below that names a core, corridor or `b_u` is SUPERSEDED by `D-EU-79`; kept as the record of what was considered").
* Mark **SUPERSEDED by `D-EU-79`** at: `:44` (layoutGenerator line), `:129` (table row "Multi-Dwelling + Unheated Stair"), `:153-181` (§4 MFH/AB grids, corridor spine, 8 % core, `b_u`, the `units_corridor` diagram), `:196-197` (§5.2). Re-anchor by grep before editing; line numbers shift.
* One paragraph under the `DR01`–`DR04` links (`:11` onward): the core recommendation was **considered and retired by the owner's ruling**, quotation included.
* Same marker on `IMP_step8/outputs/step8_master_results_dossier.md:217` ("First Watertight Multi-Dwelling Procedural UBEM") and on `outputs/floor_layout_generation_report.md:44-51, 290-299, 313-330`.
* Limitation paragraph into `writing/4thJ_writeup_notes.md` (new dated section, append): *no circulation zone is modelled; every square metre is conditioned dwelling; consequence stated, literature range 6–12 % cited to `DR02`/`DR03` as literature, never as a district number.*
* **Check** `grep -n -i "corridor\|circulation\|stair\|core\b\|b_u" 4thJ_08_bemSimulation_IMP.md` returns hits **only** inside marked sections or the header. **Perturbation:** un-mark one section in a scratch copy → the grep must show an unmarked hit. Seen felling → tick.

### Box 3 — I-9 housekeeping (no ruling needed, but see §1 item 3)

* **Master plan** `4thJ_00_HETUS_LLM_Pipeline.md` — the doc's own rule (`:2278-2279`) says **edit the entry**, not append a contradiction: `:649` "four countries" → three, dated; the KEY DESIGN DECISIONS block (🔴 the `:2069` anchor did **not** resolve on 2026-09-03 — `grep -n -i "four" ` and locate it; if no "four countries" survives there, record "already three" and move on); status lines `:849` (Step 2), `:1557` (Step 7), `:1644` (Step 8), `:1704` (Step 9), `:1814` (Step 10) get a dated status (closed 2026-08-14/18, 2026-08-25, 2026-08-25/26, 2026-08-25/27, 2026-08-28); Step 10D `:1873-1889` — the 18/297, 256/297 and 1/12 figures carry *"measured under the parked layout regime"*.
* **Overview** `4thJ_00_HETUS_LLM_Pipeline_Overview.md:307-484` — one dated line above the status box; the box itself stays.
* **510 vs 88** — `IMP_step8/4thJ_08_bemSimulation_IMP.md:27` and `outputs/step8_master_results_dossier.md:137`: "510-cell / 102 archetypes" = the **OpenUBEM archetype campaign** (`EU-08`); the 4J Step 8 campaign is **88 × 5 f × 10 diaries** (`4thJ_08_bemSimulation.md:796-799`). One bracketed clarification each.
* **Step 7 IMP** `Step7_docs/4thJ_07_schedules_and_chaining_IMP.md:706-708` — dated note: `G7.18`'s blocker text is stale since `D-S8-2` (2026-08-21/24) and the 9,000-run sweep (2026-08-25).
* **Board** — three cards: flip `10.11` (the only stale card, the rotation-origin fix is OpenUBEM's — read what the live card says before deciding done/blocked), set the no-core review card from in progress to done **only at box 8**, add the Step 12 card if `D-IMP-2`(a). 🔴 **Read the live artefact in full and diff it against the local file per step before any edit** (`feedback_board_live_artifact_is_master.md`, `FINDING 197`); `node --check` on the extracted script **and** the DOM-shim smoke must pass; publish with the existing `url` (`9e07da64-8e57-4e01-9c89-3fffd2a0ceaf`), keep the favicon, prepend to the stamp, copy the published HTML back over the local file. The one-in-progress rule holds.
* **Check** re-run the four greps of §9 (four countries, `Status: OPEN`, `510-cell`, `blocked behind an IDF`) → each hit now sits beside a dated note. **Perturbation:** none needed beyond the grep; record the before/after hit counts.

### Box 4 — I-4, on `D-IMP-2`(a)

* **Create** `Step12_docs/4thJ_12_nocoreRealStock.md` (implementation: STATUS, AIM, what is carried from Step 10 unchanged, the population change, work items, Progress Log) and `Step12_docs/4thJ_12_nocoreRealStock_val.md` (gate table **`G12.x`**, one row per gate, **inheritance from `G10.x` stated on each row** — the Step 10/11 convention — perturbation column, vacuity guards `V12.x`). Population = the four districts (Madrid, Lyon, London, Bologna; France a physical baseline, **never** in a 4J denominator, `G10.11` intact). Arm F redefined (check-FAIL or unusable footprint → one box per floor), `G10.22` LOWER BOUND wording kept, `G10.19`'s floor stated as reachable on census arithmetic only.
* **Prereg draft** `Step12_docs/prereg_step12_DRAFT.md` — marked DRAFT, **not frozen**, no md5 sidecar yet. 🔴 `Step6_docs/outputs_step6/prereg.md` (md5 `e4243e07cdd80c9c846b91f40e3e8c45`) is never opened for writing.
* **Preflight guard** `tools/4thJ_step12_preflight.py` — read-only; asserts from a manifest `scheme == "nocore_equal_area"`, `status == "direct"`, the check verdict present, and the sha256 of `european_residential.py` against a pinned no-core digest (pin = `TBD_by_owner`, so the digest check fails by construction until carry-in). Local interpreter `C:/Users/o_iseri/Desktop/OpenUBEM/.venv/Scripts/python.exe`; **no EnergyPlus, no network, no cluster**.
* **Check — the guard must be seen FAILING today** on any of the 410 retained manifests in `Step10_docs/outputs_step10/realstock_campaign/manifests/` and on the engine as it is (core-era). Record the exact failure lines in `Step12_docs/impl/<today>_preflight-seen-failing.md`. `V10.i` applies: re-measure the engine digest, do not copy the "core-era" claim from the review.

### Box 5 — I-3, I-6, I-7 into the Step 12 spec (with box 4)

* **I-3** — `N_u := k × storeys`, `k = max(1, round(dwellings_total / storeys))`; the deficit `N_u − observed_dwellings` per building **reported, never gated**; the spec names which N_u every gate means. Source table `IMP/docs/2026-09-03_nocore_projection_41.csv` (41 buildings; 332 / 312 / 230 are census arithmetic, never a result).
* **I-6** — required manifest fields, all of them: `weather_sha256`, `energyplus_build_hash`, `energyplus_version` (measured, not literal — `FINDING 187`), `openubem_version`, `openubem_git_commit`, measured `platform`, `rotated_to_midnight`, `diary_origin_hour`, `completed`, `completion_status`, `scheme`, `status`, `k`, `observed_dwellings`, `dwelling_deficit`. The `G12` twin of `G10.14` **fails** on one blanked field. **Check:** blank one field in a scratch manifest → seen felling.
* **I-7** — replicate arm: a named subset re-run R times on one host; re-run tolerance is the **quotation rule** (inside → quotable with the tolerance; outside → barred, named); `.err` marker census (`PsyPsatFnTemp` / `PsyTwbFnTdbWPb`, `FINDING 182`/`193`) as an INFO column. **Check:** a scratch replicate set with one cell beyond tolerance → the quotation rule must bar it, seen felling. No compute.

### Box 6 — I-5, on `D-IMP-3`(a)

* Binding rule into the Step 12 spec: every drawn flat gets its **own independent series** (Case B semantics) by rank order from a per-fold emission **sized to the district's dwelling count** (emission is CPU, `tools/4thJ_step7_schedules.py`, selftest 61/61 — **do not emit anything now**, size it on paper from the census `k × storeys`, labelled "projected, not measured"); all drawn storeys eligible; non-residential ground floors a declared limitation. Case A stays the paired control. `G10.8` (content-located fold) and `G10.20` (Case A/B distinct) carry over as `G12` rows.
* **Check:** two dwellings of one building sharing a series in Case B must FAIL the binding gate (sha256 collision per building); a series of the wrong fold must FAIL the fold check (the `G10.8` mutation). Both seen felling on scratch fixtures.

### Box 7 — I-8, Step 11 notes (no ruling needed, but only after box 4 so the pointer exists)

* `Step11_docs/4thJ_11_stockEndUseLoads.md` **§2.1** (`:222`) — dated amendment: Arm F = check-FAIL or unusable footprint, one box per floor, no longer a convexity refusal; `G11.17` unchanged. **Item 11.7** (`:273`) — input re-pointed to the `D-EU-88` district-viewer output once it exists (geometry only, no EUI on the page); `G11.13` stays. Mirror one line in `_val.md`. Nothing built.

### Box 8 — close

* Tick §12 box 8 in the governing document; final `§13` row; its header **Status** line gains a dated *"APPLIED except …"* sentence (additive, the original line stays).
* 🔴 **Three-artefact closure ritual:** Progress-Log entries (Step 8 IMP if box 2, master plan, Step 11 if box 7, Step 12 if box 4), the validation-doc entries, and the **lead block of `Prompts/RESUME.md` rewritten at the head** (backup `RESUME.md.bak_next34`, header "last+34"); board republished (box 3 rules); memory `project_4j_hetus_llm.md` appended + `MEMORY.md` 4J line extended by one sentence.
* Step 12 exists **on paper only**; it waits on the OpenUBEM blockers of §4 (engine carry-in, `D-EU-84`, `D-EU-87`, `FINDING 221`, `D-EU-88`) and on `D-EU-55`. **Step 10 and Step 11 do not re-open.**

---

## 3. 🔴 WHAT NEVER HAPPENS IN THIS SESSION

* No EnergyPlus, no Speed job, no local run, no emission of schedules, no plate cut. `D-EU-55` binds the OpenUBEM side and nothing on the 4J side is authorised. If a box seems to need a run, it does not — write the spec line and the perturbation on a scratch fixture.
* No re-scoring of the closed Step 10 board (18 PASS / 2 FAIL / 1 INFO / 1 OPEN_INHERITED / 2 NOT_EVALUABLE); no retrofit of any of the 410 manifests; `G10.1`–`G10.4` stay on 40 paired cells (`es` 30 / `it` 10 / `uk` 0) and that naming travels with every mention.
* Never re-propose option (c) of `D-S10-1` or Option B of `D-EU-31`; the 149 stay barred at cell level.
* No edit to a promoted artefact, a frozen spec, or an existing log entry — dated additions only.
* No images. No deep research (author the prompt if one is needed; the 7-step vetting applies).
* Nothing unrequested: the boxes above are the whole scope. A defect found on the way is a dated `FINDING` in the nearest Progress Log, not a fix.

## 4. 🔴 THE NEVER-QUOTE LIST (verbatim from RESUME last+32 §4)

**395** - **249** - **"136 clean"** - any raw `completed` count - any pre-2026-08-28 `idf_sha256` - any `uk` fold-level or nationally representative heating figure - **any `es` result at any level** - the **191** as a reporting perimeter - `FINDING 186`'s OR of **4.12** - the `it` cell range **45.08-156.70** - the `it` cell median **113.09** - the all-perimeter **99.79 kWh/m²** - any per-cell number from the 149 - the 15 per-pair `f_sweep` values - and never *"108.25 was re-measured"*. Added 2026-09-03: no stock EUI from Arm D was ever quotable (`FINDING 196`), and the six affected buildings' `eui_heating_kwh_m2` are **lower bounds**.

## 5. WORKING RULES THAT HAVE COST THE PROJECT BEFORE

* **Reply in English**, ~80 words: headline, 3–5 bullets, `Evidence:` (paths, `path:line`), `Next:` (3–4 word noun phrase). One decision per reply: `Waiting on you: D-XX --- recommend (a).` No tables in replies.
* **No parking:** state goes to disk as it happens (the §12 boxes and §13 ledger of the governing document are the state); one agent, one task, one turn; end the turn with the state written.
* **Delegate scanning** to cheap agents (sonnet/haiku); never delegate a gate design or a decision.
* **Gates must be seen failing** — read `feedback_gates_must_be_seen_failing.md` before designing any `G12.x` row; `feedback_read_the_gates_own_doc.md` — basis change = band change, never as a fix.
* **Verify Progress-Log claims** against the artefact before repeating them; **re-check recorded blockers** (`V10.i`).
* **Shell:** Git Bash; bare `python` hits the Store shim — use `C:/Users/o_iseri/AppData/Local/Programs/Python/Python313/python.exe` or the OpenUBEM venv; `PYTHONIOENCODING=utf-8` for any print; count lines with `wc -l`, never PowerShell; long scripts by the Write tool and run by path, never nested heredocs.
* **Backups:** `BK=X.bak_nocore_exec; cp X "$BK"; [ -s "$BK" ] || exit 1` before every in-place edit.
* **Board:** live artefact is master (`FINDING 197`); `node --check` + DOM-shim smoke before every publish; `const DATA` array of `{n, title, note, items:[{t, s, risk, note}]}`; commas between items.
* **Git:** commit only if the author asks; if asked, `[docs]:` prefix, trailer `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`; the author's own staged rename of the 2026-08-21 IMP doc is left as they staged it.

## 6. WHERE THINGS LIVE

* Governing document and its CSVs: `4J_docs_occ/IMP/docs/2026-09-03_*` · tool `4J_docs_occ/tools/4thJ_imp_nocore_void_census.py` (read-only over `_local_runs/step10_realstock_speed410/` and the 410 manifests).
* Owner's ruling: `C:/Users/o_iseri/Desktop/OpenUBEM/docs/docs_ACTIVE/europeanLocations/` — `STATE_european_locations_v5.md:170-183` (`D-EU-79`–`D-EU-88`), `rules/RULES_dwelling_layout_groups_nocore_2026-09-02.html` + two companions, `implementation/PLAN_eu21-nocore-2026-09-02.md`, `implementation/PLAN_eu21-district-viewer-2026-09-03.md`, `messages_GSSCanada/DONE/`. Read-only on that tree; decisions there are the owner's.
* Step 10: `Step10_docs/4thJ_10_ubemRealStock.md` (Progress Log, append-only; 2026-09-03 entry = `FINDING 195`/`196`), `_val.md`, `impl/2026-08-28_step10-validation-suite-scored.md` §9 (the closure), `outputs_step10/realstock_campaign/` (scored, untouched).
* Step 11: `Step11_docs/4thJ_11_stockEndUseLoads.md` + `_val.md` (11.3–11.7 unbuilt). Step 12: does not exist yet.
* Board: `4J_docs_occ/4thJ_CHECKLIST.html` = the published page (139 cards, 130 / 1 / 8 on 2026-09-03) → `https://claude.ai/code/artifact/9e07da64-8e57-4e01-9c89-3fffd2a0ceaf`. Backups `.bak_nocore` and earlier.
* Handoff: `4J_docs_occ/Prompts/RESUME.md` (lead block rewritten at the head every closure; backups `RESUME.md.bak_nextNN`).
