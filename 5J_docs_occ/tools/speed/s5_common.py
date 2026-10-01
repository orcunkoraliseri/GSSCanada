# -*- coding: utf-8 -*-
"""5J Step 5 shared code (Speed job only; Spain + Italy only; never a UK file; never a test run).

Rules: Step5_docs/outputs_step5/step5_rules.md (R1 no test data, R2 inputs).
  allowed_ids()      = development U validation U b0_dev U b0_val, read ONLY through split_loader.load_split.
  open_run()         refuses (PermissionError) any run id outside allowed_ids(); appends (kind, run_id, path) to a list `log`;
                     flush_log(log, tag) appends the lines to /speed-scratch/o_iseri/5J/train/openlog_<tag>.tsv.
  FEATURE_FORBIDDEN  EnergyPlus output names; check_features(names) -> (ok, bad)  (validation gate 1.2).
split_loader.py is the copy of /speed-scratch/o_iseri/5J/freeze/split_loader.py placed next to this file by the sbatch.
"""
import csv, io, os, re, sys
sys.dont_write_bytecode = True
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import split_loader as sl

FIVE = "/speed-scratch/o_iseri/5J/"
CAMP = FIVE + "campaign/"
TRAIN = FIVE + "train/"
TRUTH = CAMP + "extracted/"
HHROOT = FIVE + "households/inputs/"
REPO = CAMP + "repo/"
SPLITS = ("development", "validation", "b0_dev", "b0_val")
COUNTRIES = ("es", "it")
H = 8760
TARGETS = ["heating_kwh", "cooling_kwh", "equipment_kwh", "total_elec_kwh"]     # file columns; the model learns the first 3
CAL_YEAR = {"es": 2010, "it": 2014}
COP = 3.0

_ALLOWED = None
_LISTS = {}
_RUNS = None


# ------------------------------------------------------------------------------------------------ allowed runs
def lists():
    """The four lists, each through load_split (never any other name)."""
    if not _LISTS:
        for nm in SPLITS:
            _LISTS[nm] = sl.load_split(nm)
    return _LISTS


def allowed_ids():
    global _ALLOWED
    if _ALLOWED is None:
        _ALLOWED = set()
        for nm, ids in lists().items():
            _ALLOWED |= set(ids)
    return _ALLOWED


def runs():
    """Raw rows of the two run tables, run_id -> dict (placement is NOT parsed here; see placement())."""
    global _RUNS
    if _RUNS is None:
        _RUNS = {}
        for cc in COUNTRIES:
            for r in csv.DictReader(io.open(CAMP + "in/campaign_runs_%s.csv" % cc, encoding="utf-8")):
                assert r["country"] == cc and r["run_id"].startswith(cc + "_"), r["run_id"]
                _RUNS[r["run_id"]] = r
    return _RUNS


def placement(run_id):
    """{flat: token} of an ALLOWED run (refuses any other id)."""
    if run_id not in allowed_ids():
        raise PermissionError("REFUSED: run %s is not in development, validation, b0_dev or b0_val" % run_id)
    d = {}
    for item in runs()[run_id]["placement"].split(";"):
        j, t = item.split(":", 1)
        d[int(j)] = t
    return d


# ------------------------------------------------------------------------------------------------ the one reader
def open_run(run_id, kind, log, root=None):
    """Returns the file path of the run's csv.gz under `root` (default: the campaign truth folder) after the allowed-list
    check; logs (kind, run_id, path). The caller opens the returned path. Raises PermissionError for any other id."""
    if run_id not in allowed_ids():
        raise PermissionError("REFUSED: run %s is not in development, validation, b0_dev or b0_val" % run_id)
    r = runs()[run_id]
    p = "%s%s/%s.csv.gz" % (root or TRUTH, r["climate_id"], run_id)
    log.append((kind, run_id, p))
    return p


def flush_log(log, tag):
    p = TRAIN + "openlog_%s.tsv" % tag
    new = not os.path.exists(p)
    with io.open(p, "a", encoding="utf-8") as fh:
        if new:
            fh.write("kind\trun_id\tpath\n")
        for k, rid, pth in log:
            fh.write("%s\t%s\t%s\n" % (k, rid, pth))


def read_truth(run_id, nd, log, kind="truth", root=None):
    """[nd, 8760, 4] float64 (heating, cooling, equipment, total_elec) of one run, checked like the scorer's reader."""
    p = open_run(run_id, kind, log, root)
    df = pd.read_csv(p, comment="#", compression="gzip", usecols=["dwelling", "hour"] + TARGETS)
    if len(df) != nd * H:
        raise RuntimeError("%s: rows %d != %d" % (run_id, len(df), nd * H))
    df = df.sort_values(["dwelling", "hour"], kind="stable")
    if not (np.array_equal(df["dwelling"].to_numpy(), np.repeat(np.arange(nd), H)) and
            np.array_equal(df["hour"].to_numpy(), np.tile(np.arange(1, H + 1), nd))):
        raise RuntimeError("%s: dwelling or hour index wrong" % run_id)
    arr = df[TARGETS].to_numpy(dtype=float).reshape(nd, H, 4)
    if not np.isfinite(arr).all():
        raise RuntimeError("%s: non-finite values" % run_id)
    return arr


# ------------------------------------------------------------------------------------------------ leakage guard (val 1.2)
FEATURE_FORBIDDEN_EXACT = {
    "heating_kwh", "cooling_kwh", "equipment_kwh", "total_elec_kwh", "heating_sens_kwh", "heating_lat_kwh", "cooling_sens_kwh",
    "cooling_lat_kwh", "zoneside_heating_kwh", "zoneside_cooling_kwh", "people_heat_kwh", "infil_gain_kwh", "infil_loss_kwh",
    "win_gain_kwh", "win_loss_kwh", "win_solar_kwh", "unmet_heat_zone_h", "unmet_cool_zone_h", "t_air_c", "t_op_c", "rh_pct",
}
FEATURE_FORBIDDEN_SUBSTR = ("heating", "cooling", "equipment_kwh", "total_elec", "temperature", "zone", "load")
FEATURE_FORBIDDEN = {"exact": sorted(FEATURE_FORBIDDEN_EXACT), "substring": list(FEATURE_FORBIDDEN_SUBSTR)}


def check_features(names):
    """(ok, bad): ok is False when any name equals an EnergyPlus output name or contains a forbidden word."""
    bad = [n for n in names if n.lower() in FEATURE_FORBIDDEN_EXACT or any(s in n.lower() for s in FEATURE_FORBIDDEN_SUBSTR)]
    return (not bad), bad


# ------------------------------------------------------------------------------------------------ input names (R2)
HH_CHANNELS = ["presence", "appl_frac", "people", "appl_w"]
NB_CHANNELS = ["nb_same_people", "nb_same_appl_w", "nb_same_flag", "nb_above_people", "nb_above_appl_w", "nb_above_flag",
               "nb_below_people", "nb_below_appl_w", "nb_below_flag"]
WEATHER_CHANNELS = ["dry_bulb_c", "dew_point_c", "rel_humidity_pct", "ghi_wh_m2", "dni_wh_m2", "dhi_wh_m2", "wind_speed_ms"]
EPW_COLS = [6, 7, 8, 13, 14, 15, 21]       # 0-based EPW data columns: dry bulb, dew point, RH, GHI, DNI, DHI, wind speed
CALENDAR_CHANNELS = ["hour_sin", "hour_cos", "doy_sin", "doy_cos", "dow"]
CLASSES = ["SFH", "TH", "MFH", "AB"]
STATIC_FIXED = ["s_cls_" + c for c in CLASSES] + ["s_infil_ach", "s_north_sin", "s_north_cos", "s_n_floors", "s_k", "s_n_dwellings",
                                                  "s_floor_idx", "s_is_top", "s_is_ground", "s_area_m2"]


def archetype_rows(cc):
    """Rows of archetype_parameters_<cc>.csv (3 leading '#' lines dropped, as 4thJ_step8_idf.load_rows)."""
    path = CAMP + "in/archetype_parameters_%s.csv" % cc
    raw = [r for r in csv.reader(io.open(path, encoding="utf-8")) if len(r) > 1]
    hdr = raw[0]
    return [dict(zip(hdr, r)) for r in raw[1:]], hdr


def archetype_numeric_columns():
    """Columns of the archetype table that are numeric in every row of both countries (blank counts as numeric 0),
    minus the text 'Code_*' columns and the counter Number_BuildingVariant. Returns (cols, skipped)."""
    rows, hdr = {}, {}
    for cc in COUNTRIES:
        rows[cc], hdr[cc] = archetype_rows(cc)
    assert hdr["es"] == hdr["it"], "archetype headers differ between es and it"
    cols, skipped = [], []
    for c in hdr["es"]:
        ok = True
        for cc in COUNTRIES:
            for r in rows[cc]:
                v = r[c].strip()
                if v == "":
                    continue
                try:
                    float(v)
                except ValueError:
                    ok = False
        if c.startswith("Code_") or c == "Number_BuildingVariant" or not ok:
            skipped.append(c)
        else:
            cols.append(c)
    return cols, skipped


def climates():
    return [r["climate_id"] for r in csv.DictReader(io.open(CAMP + "in/climates_es_it.csv", encoding="utf-8"))]


def static_names():
    cols, _ = archetype_numeric_columns()
    return STATIC_FIXED + ["s_" + c.lower() for c in cols]


def all_input_names():
    """The full list of model input names (R2): household, neighbour, weather, calendar, static, climate one-hot."""
    return (HH_CHANNELS + NB_CHANNELS + WEATHER_CHANNELS + CALENDAR_CHANNELS + static_names() +
            ["c_" + c for c in climates()])
