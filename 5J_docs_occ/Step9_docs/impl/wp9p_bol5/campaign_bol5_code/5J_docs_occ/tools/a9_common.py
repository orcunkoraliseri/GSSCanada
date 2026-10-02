# -*- coding: utf-8 -*-
"""5J Step 9g (Model A) shared code. Speed job only; ES-MAD-BERRUGUETE and IT-BOL-GALVANI2 only; never a UK file.

Reuses (IMPORTS, not copies) from the pilot's tools/speed/s5_common.py: check_features, FEATURE_FORBIDDEN, H, EPW_COLS, COP,
HH_CHANNELS, NB_CHANNELS, WEATHER_CHANNELS, CALENDAR_CHANNELS.  s5_common does `import split_loader` at module level and the
pilot split loader would read PILOT run lists; a stub module is therefore put into sys.modules BEFORE the import, so no pilot
list or pilot run can ever be loaded from here (the stub raises when called).
s5_common.py must sit next to this file (the sbatch copies it unchanged).
Nothing in this file opens a data file; the guard (RunGuard) is the only door to a run folder.
"""
import csv, io, os, sys, types, datetime
sys.dont_write_bytecode = True
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

_stub = types.ModuleType("split_loader")


def _refuse(*a, **k):
    raise PermissionError("a9: the pilot split loader is not available in Model A code")


_stub.load_split = _refuse
sys.modules.setdefault("split_loader", _stub)
import s5_common as s5          # noqa: E402  (pilot code, reused)

H = s5.H
COP = s5.COP
check_features = s5.check_features
FEATURE_FORBIDDEN = s5.FEATURE_FORBIDDEN
EPW_COLS = s5.EPW_COLS
HH_CHANNELS = s5.HH_CHANNELS
NB_CHANNELS = s5.NB_CHANNELS
WEATHER_CHANNELS = s5.WEATHER_CHANNELS
CALENDAR_CHANNELS = s5.CALENDAR_CHANNELS
CLASSES = s5.CLASSES

MA = "/speed-scratch/o_iseri/5J/modelA/"
# the only two districts Model A knows (a district not in this table is refused everywhere)
DISTRICTS = {"ES-MAD-BERRUGUETE": {"cc": "es", "year": 2010}, "IT-BOL-GALVANI2": {"cc": "it", "year": 2014}}
COUNTRIES = ("es", "it")
TARGET_NAMES = ["heating_kwh", "cooling_kwh", "equipment_kwh"]       # the model learns these 3; total = equipment + (h + c) / COP

# ------------------------------------------------------------------------------------------------ static vector (E5)
FLAT_NUMERIC = [("storeys_spanned", "s_storeys_spanned"), ("floor_k", "s_floor_idx"), ("floor_area_m2", "s_floor_area"),
                ("wall_N_m2", "s_wall_n"), ("wall_E_m2", "s_wall_e"), ("wall_S_m2", "s_wall_s"), ("wall_W_m2", "s_wall_w"),
                ("win_N_m2", "s_win_n"), ("win_E_m2", "s_win_e"), ("win_S_m2", "s_win_s"), ("win_W_m2", "s_win_w"),
                ("adiabatic_wall_m2", "s_adiabatic_wall"), ("roof_m2", "s_roof_area"), ("ground_floor_m2", "s_ground_floor_area")]
FLAT_FLAGS = [("top_flag", "s_is_top"), ("ground_flag", "s_is_ground")]
BLD_NUMERIC = [("storeys", "s_storeys"), ("flats", "s_flats"), ("conditioned_area_m2", "s_cond_area"), ("u_wall", "s_u_wall"),
               ("u_roof", "s_u_roof"), ("u_floor", "s_u_floor"), ("u_window", "s_u_window"), ("shgc_window", "s_shgc_window"),
               ("window_share", "s_window_share"), ("n_shading", "s_n_shading")]
BLD_FLAGS = [("no_outdoor_wall", "s_no_outdoor_wall")]


def read_csv_rows(path):
    return list(csv.DictReader(io.open(path, encoding="utf-8", newline="")))


def zone_map(path):
    """{(district, stem): [row dicts in file order]}; refuses any district that is not in DISTRICTS (never keeps one)."""
    out = {}
    for r in read_csv_rows(path):
        if r["district"] not in DISTRICTS:
            raise ValueError("zone map row with district %r is not a Model A district" % r["district"])
        out.setdefault((r["district"], r["stem"]), []).append(r)
    return out


def static_tables(static_dir):
    """(flats {(district, zone): row}, buildings {(district, stem): row}, age_bands sorted list) from the two static tables per
    district: static_dir/flats_<D>.csv, buildings_<D>.csv. Columns are read by name, never by position."""
    flats, blds, bands = {}, {}, set()
    for d in DISTRICTS:
        for r in read_csv_rows(os.path.join(static_dir, "flats_%s.csv" % d)):
            assert r["district"] == d
            flats[(d, r["zone"])] = r
        for r in read_csv_rows(os.path.join(static_dir, "buildings_%s.csv" % d)):
            assert r["district"] == d
            blds[(d, r["stem"])] = r
            bands.add(r["age_band_prepared"])
    return flats, blds, sorted(bands)


def static_names(age_bands):
    """Names of every static input column, in order (all start with s_)."""
    return (["s_ctry_" + c for c in COUNTRIES] + ["s_cls_" + c for c in CLASSES] + ["s_age_" + b.replace(".", "_") for b in age_bands] +
            [n for _, n in BLD_NUMERIC] + [n for _, n in BLD_FLAGS] + [n for _, n in FLAT_NUMERIC] + [n for _, n in FLAT_FLAGS])


def zscored_names():
    """Static columns that are z-scored on development and clipped to the development range (numeric ones); one-hots and flags stay raw."""
    return [n for _, n in BLD_NUMERIC] + [n for _, n in FLAT_NUMERIC]


def all_input_names(age_bands):
    """The full input list of Model A (E3 to E5): household, neighbour, weather, calendar, static."""
    return HH_CHANNELS + NB_CHANNELS + WEATHER_CHANNELS + CALENDAR_CHANNELS + static_names(age_bands)


def calendar_array(year):
    """8760 x 5: hour sin, hour cos, day-of-year sin, day-of-year cos (period 365), day of week (Monday = 0), as s5_store.py:172-178."""
    i = np.arange(H)
    hod, doy = i % 24, i // 24
    dow = (datetime.date(year, 1, 1).weekday() + doy) % 7
    return np.stack([np.sin(2 * np.pi * hod / 24), np.cos(2 * np.pi * hod / 24), np.sin(2 * np.pi * doy / 365),
                     np.cos(2 * np.pi * doy / 365), dow], 1).astype(np.float32)


# ------------------------------------------------------------------------------------------------ the one door (as s5_common.open_run)
class RunGuard(object):
    """allowed = {split: set(run ids)} given by the caller. open_run(run_id, kind, run_dir) returns run_dir only if run_id is in some
    list (PermissionError otherwise, and NOTHING is logged for a refused id); every successful open appends (kind, run_id, path).
    flush(path) appends the lines to a tsv. split_of(run_id) gives the list the id is in (an id in two lists is a ValueError)."""

    def __init__(self, allowed):
        self.allowed = {k: set(v) for k, v in allowed.items()}
        self.log = []
        self.refused = []

    def split_of(self, run_id):
        hit = [k for k, v in self.allowed.items() if run_id in v]
        if len(hit) > 1:
            raise ValueError("run %s is in more than one list: %s" % (run_id, hit))
        return hit[0] if hit else None

    def open_run(self, run_id, kind, run_dir):
        if self.split_of(run_id) is None:
            self.refused.append(run_id)
            raise PermissionError("REFUSED: run %s is not in the allowed lists %s" % (run_id, sorted(self.allowed)))
        self.log.append((kind, run_id, run_dir))
        return run_dir

    def flush(self, path):
        new = not os.path.exists(path)
        with io.open(path, "a", encoding="utf-8") as fh:
            if new:
                fh.write("kind\trun_id\tpath\n")
            for k, rid, p in self.log:
                fh.write("%s\t%s\t%s\n" % (k, rid, p))
        self.log = []
