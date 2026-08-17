# COP packing measurement (six binary flags)

Manager decision 2026-08-16: COP is now six binary flags (was five; the sixth is
"with a parent"). Question: which packing of the six bits into the serialised
episode tuple costs the fewest tokens, measured in situ (never as a bare string).

## Tokenizer and job

- Tokenizer / vocabulary: OLMo / dolma2 BPE.
- Model id actually loaded: `allenai/OLMo-2-0425-1B`. This is a **stand-in**, not
  the paper's backbone (`allenai/Olmo-3-1025-7B`) — it carries an identical
  vocabulary and is far smaller to download, as instructed.
- vocab_size reported by the tokenizer: 100278. transformers version 5.15.0.
- Speed job ID: **1252633** (`sbatch -p ps --mem=16G -t 7-00:00:00`, COMPLETED,
  elapsed 00:00:42, exit 0:0). Reused the existing venv
  `/speed-scratch/o_iseri/envs/4j_tok` (symlinked to `envs/step4`'s python, per
  `tools/4thJ_tok_setup_and_run.sh`'s pattern) — `envs/step4` itself was not
  touched. Script run: `/speed-scratch/o_iseri/4thJ_cop_measure.py`, a copy of
  `tools/4thJ_cop_measure.py` in this repo.

## Method

Every candidate was measured **inside** an episode tuple `DUR,ACT,LOC,<COP>;` and
inside a full 25-episode diary — never as a bare fragment. The 25-episode diary
skeleton (shared across all five candidates, only the COP field changes):

- DUR (multiples of 10, sum = 1440): `[480, 240, 30, 20, 10, 40, 30, 60, 20, 10, 90, 30, 20, 10, 50, 30, 20, 10, 60, 30, 20, 10, 40, 30, 50]`
- ACT (3-digit): `['311','411','111','911','311','121','411','211','511','311','111','621','411','811','311','911','121','821','411','211','311','511','111','911','311']`
- LOC (includes 41, above 39): `['11','31','11','91','11','11','31','11','11','11','11','41','31','11','11','91','11','21','31','11','11','11','11','91','11']`
- per-episode COP integer v (0-63), one per episode, `v_i = (7i+3) mod 64`:
  `[3,10,17,24,31,38,45,52,59,2,9,16,23,30,37,44,51,58,1,8,15,22,29,36,43]`

The representative single episode uses `DUR=30, ACT=311, LOC=11, v=22` (the same
v=22 used in the manager's own worked examples: binary `010110`, octal `26`, hex
`16`, bits `0,1,0,1,1,0`).

For the worst-case sweep, all 64 values of v (0-63) were substituted into that
same representative episode slot (`30,311,11,<enc(v)>;`) and each was tokenized;
the table reports the maximum token count and every v that reaches it.

## Results

| # | Candidate | Representative episode string | Episode tokens (v=22) | Diary tokens (25 ep.) | Worst-case tokens (sweep v=0..63) | v achieving worst case |
|---|---|---|---|---|---|---|
| 1 | decimal integer 0-63 | `30,311,11,22;` | 8 | 200 | **8** | all 64 values |
| 2 | six chars, e.g. `010110` | `30,311,11,010110;` | 9 | 225 | **9** | all 64 values |
| 3 | two octal digits, e.g. `26` | `30,311,11,26;` | 8 | 200 | **8** | all 64 values |
| 4 | two hex chars, e.g. `16` | `30,311,11,16;` | 8 | 210 | **9** | v in {10-15, 26-31, 42-47, 58-63} (hex digits containing a-f) |
| 5 | baseline, six comma-separated digits, e.g. `0,1,0,1,1,0` | `30,311,11,0,1,0,1,1,0;` | 18 | 450 | **18** | all 64 values |

Reference point: the earlier measurement on this vocabulary (Speed jobs
1234177/1234199/1234216) found a 25-episode diary with the old single-digit
(0-3) COP field costs 200 tokens (8 tokens/episode). Candidates 1 and 3
reproduce that exact cost with six bits packed in; candidate 5 (baseline) more
than doubles it.

### Exact strings measured

Representative episode strings — listed in the table above, verbatim (`repr()`
values from the run log, no escaping needed since all are plain ASCII).

Full 25-episode diary strings (one per candidate, exact, semicolon-terminated,
no separator between episodes):

- **1 (decimal):** `480,311,11,3;240,411,31,10;30,111,11,17;20,911,91,24;10,311,11,31;40,121,11,38;30,411,31,45;60,211,11,52;20,511,11,59;10,311,11,2;90,111,11,9;30,621,41,16;20,411,31,23;10,811,11,30;50,311,11,37;30,911,91,44;20,121,11,51;10,821,21,58;60,411,31,1;30,211,11,8;20,311,11,15;10,511,11,22;40,111,11,29;30,911,91,36;50,311,11,43;`
- **2 (six chars):** `480,311,11,000011;240,411,31,001010;30,111,11,010001;20,911,91,011000;10,311,11,011111;40,121,11,100110;30,411,31,101101;60,211,11,110100;20,511,11,111011;10,311,11,000010;90,111,11,001001;30,621,41,010000;20,411,31,010111;10,811,11,011110;50,311,11,100101;30,911,91,101100;20,121,11,110011;10,821,21,111010;60,411,31,000001;30,211,11,001000;20,311,11,001111;10,511,11,010110;40,111,11,011101;30,911,91,100100;50,311,11,101011;`
- **3 (two octal digits):** `480,311,11,03;240,411,31,12;30,111,11,21;20,911,91,30;10,311,11,37;40,121,11,46;30,411,31,55;60,211,11,64;20,511,11,73;10,311,11,02;90,111,11,11;30,621,41,20;20,411,31,27;10,811,11,36;50,311,11,45;30,911,91,54;20,121,11,63;10,821,21,72;60,411,31,01;30,211,11,10;20,311,11,17;10,511,11,26;40,111,11,35;30,911,91,44;50,311,11,53;`
- **4 (two hex chars):** `480,311,11,03;240,411,31,0a;30,111,11,11;20,911,91,18;10,311,11,1f;40,121,11,26;30,411,31,2d;60,211,11,34;20,511,11,3b;10,311,11,02;90,111,11,09;30,621,41,10;20,411,31,17;10,811,11,1e;50,311,11,25;30,911,91,2c;20,121,11,33;10,821,21,3a;60,411,31,01;30,211,11,08;20,311,11,0f;10,511,11,16;40,111,11,1d;30,911,91,24;50,311,11,2b;`
- **5 (baseline, csv bits):** `480,311,11,0,0,0,0,1,1;240,411,31,0,0,1,0,1,0;30,111,11,0,1,0,0,0,1;20,911,91,0,1,1,0,0,0;10,311,11,0,1,1,1,1,1;40,121,11,1,0,0,1,1,0;30,411,31,1,0,1,1,0,1;60,211,11,1,1,0,1,0,0;20,511,11,1,1,1,0,1,1;10,311,11,0,0,0,0,1,0;90,111,11,0,0,1,0,0,1;30,621,41,0,1,0,0,0,0;20,411,31,0,1,0,1,1,1;10,811,11,0,1,1,1,1,0;50,311,11,1,0,0,1,0,1;30,911,91,1,0,1,1,0,0;20,121,11,1,1,0,0,1,1;10,821,21,1,1,1,0,1,0;60,411,31,0,0,0,0,0,1;30,211,11,0,0,1,0,0,0;20,311,11,0,0,1,1,1,1;10,511,11,0,1,0,1,1,0;40,111,11,0,1,1,1,0,1;30,911,91,1,0,0,1,0,0;50,311,11,1,0,1,0,1,1;`

## RECOMMENDATION

**Candidate 1, a single decimal integer 0-63.** It ties candidate 3 (two octal
digits) for the lowest worst-case cost (8 tokens/episode, identical to today's
single-digit COP field, across all 64 values with no exception) but needs no
octal-to-binary translation step for anyone reading the raw corpus.

This is a recommendation only; the manager decides.
