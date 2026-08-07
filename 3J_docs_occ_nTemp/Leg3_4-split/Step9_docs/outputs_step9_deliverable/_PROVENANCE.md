# ✅ CANONICAL — this is the arm the paper reports

**`outputs_step9_deliverable/`, frozen 2026-08-06 00:05.**
Registered in `improvements/v2/V2-G1_FROZEN_DELIVERABLE.md` — read that document for the full
identity block (arm definition, `INPUTS_HASH`, EnergyPlus build, aggregate-table md5s, scorecard).

Every number, gate verdict, and figure in the 3rd-journal manuscript comes from **here**.

---

## Identity, in brief

| field | value |
|---|---|
| arm | base + V2-D9 (retail `NECB-C`) + V2-D10 (per-object DHW resize) |
| cells | **56 / 56** |
| scorecard | `{'PASS': 17, 'INFO': 10, 'FAIL': 3}` over 30 gates |
| failing gates | `S9-EUI-office`, `S9-EUI-retail`, `S9-EUI-hotel` — **all three left failing on purpose** |
| hotel channel | median 260.5411 kWh/m²·yr, range 203.3295–318.4200, n = 56; **28 above the 300 ceiling, 0 below the 180 floor** |
| platform | `win32`, EnergyPlus 24.2.0 build `94a887817b` |

---

## Canonical figure manifest (md5)

| file | md5 |
|---|---|
| `figures/fig_diurnal_4ch.png` | `5117cfabf0a252738d36a9cd00c68ba4` |
| `figures/fig_eui_4ch.png` | `b17ca5e2c65331ee624d1f52213bf5f0` |
| `figures/fig_longitudinal_4ch.png` | `4e32389ff3ac42ac551e01d52558a76c` |
| `figures/fig_peakhour_4ch.png` | `83ebb7de79398205c9df088d729dfdc0` |
| `figures/fig_scenario_4ch.png` | `6e94a2332d67e505f30283dcbf86bcf2` |

## Canonical table manifest (md5)

| file | md5 |
|---|---|
| `step9_eui_by_channel.csv` | `9f2367ddda83ca5351a3fb077b3d9994` |
| `step9_gates.json` | `e5ea569e7f072b700bc771dda9870757` |
| `step9_loadshape_peaks.csv` | `7722369e3de7493036a70ff880524ff8` |
| `step9_longitudinal.csv` | `735f19a98982228616bece8af06d7658` |
| `step9_report.html` | `259b104aa0f6e87b8d3ee0607500d407` |
| `step9_scenario_response.csv` | `8e927778362ed50885f8f9a4db5de810` |

---

## 🔴 The sibling directory, and the one thing this manifest cannot check

The sibling **`../outputs_step9/`** (2026-07-31 11:42) carries **the same 11 filenames**. Ten differ;
**`fig_diurnal_4ch.png` is byte-identical in both**.

Consequence, stated plainly so the coverage is not overclaimed: a content check can prove the origin
of **four** of the five figures and **all six** tables. It **cannot** prove the origin of
`fig_diurnal_4ch.png` — for that one file, both directories are correct answers, and the copy
provenance has to be written down at copy time.

The sibling is **not** deletable: it holds `step9_envelope_exposure.csv` and the three
`finding9_verify/` IDFs, which exist nowhere else. See `../outputs_step9/_PROVENANCE.md`.

---

## Checks that enforce this

| check | what it catches | what it cannot catch |
|---|---|---|
| `improvements/v5/f1_frozen_input_check.py` | a **script** that names or assembles a superseded path | a file already copied and renamed |
| `improvements/v5/f3_asset_provenance_check.py` | a **copied asset** whose bytes came from the superseded arm | `fig_diurnal_4ch.png` (identical in both) |

Companion file: `../outputs_step9/_PROVENANCE.md`.
