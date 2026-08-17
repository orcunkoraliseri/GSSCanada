## Progress Log fragment — COP packing measurement (2026-08-16)

- Ran a new script, `tools/4thJ_cop_measure.py`, on Speed as job **1252633**
  (`sbatch -p ps --mem=16G -t 7-00:00:00`, COMPLETED, elapsed 00:00:42, exit
  0:0), reusing the venv/module pattern of `tools/4thJ_tok_setup_and_run.sh`
  (`/speed-scratch/o_iseri/envs/4j_tok`, symlinked to `envs/step4`'s python;
  `envs/step4` itself was not touched or modified).
- Measured five candidate packings of the six COP binary flags (decimal 0-63,
  six binary chars, two octal digits, two hex chars, and the six
  comma-separated-digit baseline), each **in situ** inside a
  `DUR,ACT,LOC,<COP>;` episode tuple and inside a full 25-episode diary built
  from plausible values (durations multiples of 10 summing to 1440, 3-digit
  activity codes, a location code of 41 above 39), using
  `allenai/OLMo-2-0425-1B` (stated stand-in for the OLMo/dolma2 vocabulary of
  the actual backbone `allenai/Olmo-3-1025-7B`).
- Also swept all 64 possible COP values (0-63) through the representative
  episode slot for each candidate, to get a genuine worst case rather than one
  lucky example. Result: decimal and octal both hold at 8 tokens/episode for
  every one of the 64 values (matching the current single-digit COP cost);
  six-char binary is a flat 9; two hex chars is 8 for most values but 9 for
  any value whose hex digits include a-f; the six-comma-digit baseline is a
  flat 18. Full table and exact strings are in
  `Step3_docs/outputs_step3/cop_packing_measurement.md`.
- Recommended (not decided) candidate 1, decimal integer 0-63, tied with
  candidate 3 on worst-case token cost but simpler to read/decode.

### What was NOT independently verified

- Did **not** verify that `allenai/OLMo-2-0425-1B` and `allenai/Olmo-3-1025-7B`
  actually share an identical vocabulary — that equivalence was given as a
  premise in the task and was not re-derived or checked against the 7B
  tokenizer files here.
- Did **not** re-run or cross-check the earlier reference numbers from jobs
  1234177/1234199/1234216 (the "311=1 token, 45=1 token, one episode=8 tokens,
  25-episode diary=200 tokens" baseline) — they were only quoted as a
  reference point that this run's decimal/octal candidates happened to match.
- Did **not** check how these five candidates interact with the rest of the
  serialisation schema, the val split, or any downstream parser — only raw
  tokenizer output was measured.
- Did **not** edit `4thJ_03_serialisation.md` or `4thJ_03_serialisation_val.md`
  — left for the manager to merge.
