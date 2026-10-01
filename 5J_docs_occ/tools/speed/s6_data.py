# -*- coding: utf-8 -*-
"""5J Step 5 part C: store -> windows and pairs (Speed GPU job only; Spain + Italy only; development / validation only).

Contract: /speed-scratch/o_iseri/5J/train/store/README.md. Rules: Step5_docs/outputs_step5/step5_rules.md R1, R2.
Data class holds ONE split ('development' or 'validation'; any other name is refused) on the GPU and builds windows by index:
  window (row, day d), d in 0..364: driver hours 24d-168 .. 24d+23 (wrap inside the year, 192 h), target hours 24d .. 24d+23.
  x  [B,192,25] dynamic channels (normalised with norm.json): own presence, appl_frac, people, appl_w (4); neighbour mean people,
     mean appl_w, flag for same floor / floor above / floor below (9; a missing neighbour set = 0 and flag 0); 7 weather; 5 calendar.
  st [B,S] static vector: s_* columns standardised (development mean / SD) + c_* climate one-hot (not standardised).
  y  [B,24,3] standardised targets (heating, cooling, equipment); no target is ever an input.
"""
import hashlib, json, os, random, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
import torch
import s5_common as c

STORE = c.TRAIN + "store/"
TEST_STORE = c.FIVE + "test/store/"                                        # Step 6 part A: drivers of the three test lists, no targets
TEST_LISTS = ("test_new_households", "test_new_buildings", "test_both_new")
H = c.H
HIST = 168
WIN = 192
OUTH = 24
NDAY = 365
TNAMES = ["heating", "cooling", "equipment"]
KINDS = ("nb_same", "nb_above", "nb_below")


def dyn_names():
    return c.HH_CHANNELS + c.NB_CHANNELS + c.WEATHER_CHANNELS + c.CALENDAR_CHANNELS


BLIND_COLS = ["hh_index", "nb_same", "nb_above", "nb_below"]


def blind_donors(run_id, flat, country):
    """Rules R8 (control C). For every (run, flat) row of a split the donor is a random row of ANOTHER run of the SAME country in the
    same split table. Draw: rng = random.Random(int(md5("<run_id>|<flat>|blind|20260930").hexdigest(), 16)); candidates = the rows of that
    country in table order (sorted by run id, then flat); j = cand[rng.randrange(len(cand))]; if row j belongs to the own run, draw again
    from the same rng stream (rejection). Returns the donor row index per row (numpy int64)."""
    n = len(run_id)
    donor = np.empty(n, dtype=np.int64)
    cand = {cc: np.flatnonzero(country == cc) for cc in np.unique(country)}
    for i in range(n):
        rng = random.Random(int(hashlib.md5(("%s|%d|blind|20260930" % (run_id[i], int(flat[i]))).encode()).hexdigest(), 16))
        cc = cand[country[i]]
        for _ in range(100000):
            j = int(cc[rng.randrange(len(cc))])
            if run_id[j] != run_id[i]:
                break
        else:
            raise RuntimeError("no donor from another run for %s flat %s" % (run_id[i], flat[i]))
        donor[i] = j
    return donor


def donor_violations(run_id, country, donor):
    """(number of rows whose donor is from the SAME run, number whose donor is from ANOTHER country); both must be 0."""
    return int((run_id == run_id[donor]).sum()), int((country != country[donor]).sum())


def apply_blind(fl):
    """Returns (new flats table with the household and neighbour drivers of the donor rows, info dict). Building, static vector,
    climate, calendar and the targets (not in the table) stay with the own row."""
    donor = blind_donors(fl["run_id"].to_numpy(), fl["flat"].to_numpy(), fl["country"].to_numpy())
    out = fl.copy()
    for col in BLIND_COLS:
        out[col] = fl[col].to_numpy()[donor]
    out["donor_row"] = donor
    same_run, cross_cty = donor_violations(fl["run_id"].to_numpy(), fl["country"].to_numpy(), donor)
    same_hid = float((fl["hid"].to_numpy() == fl["hid"].to_numpy()[donor]).mean())
    return out, {"n_rows": len(fl), "donor_same_run": same_run, "donor_other_country": cross_cty, "share_donor_hid_equals_own_hid": same_hid}


class Data:
    def __init__(self, split, device, stats=None, load_targets=True, drop_climate=False, country=None, blind=False, store=None):
        store = STORE if store is None else store            # Step 6: default = the train store, every Step 5 path unchanged
        if store == STORE:
            if split not in ("development", "validation"):
                raise PermissionError("REFUSED: split %s (Step 5 trains and validates on development / validation only)" % split)
        elif store == TEST_STORE:
            if split not in TEST_LISTS:
                raise PermissionError("REFUSED: the test store holds only %s, got %s" % (TEST_LISTS, split))
            if load_targets:
                raise PermissionError("REFUSED: the test store has no targets (test truth is read only by the frozen scorer)")
        else:
            raise PermissionError("REFUSED: store %s is neither the train store nor the test store" % store)
        self.split, self.dev = split, device
        fl = pd.read_parquet(store + "flats_%s.parquet" % split)
        # --- one-country training (rules R9): rows of one country only, filtered BEFORE stats are computed (AMENDMENT 2)
        self.country = country
        keep = None
        if country is not None:
            if country not in c.COUNTRIES:
                raise ValueError("country must be one of %s" % c.COUNTRIES)
            keep = np.flatnonzero((fl["country"] == country).to_numpy())
            fl = fl.iloc[keep].reset_index(drop=True)
            print("COUNTRY_FILTER split=%s country=%s rows=%d" % (split, country, len(fl)), flush=True)
        # --- blind control (rules R8): household and neighbour drivers replaced by those of a random row of another run
        self.blind = bool(blind)
        self.blind_info = None
        if blind:
            fl, self.blind_info = apply_blind(fl)
            print("BLIND split=%s rows=%d donor_same_run=%d donor_other_country=%d INFO share_donor_hid_equals_own_hid=%.5f" %
                  (split, self.blind_info["n_rows"], self.blind_info["donor_same_run"], self.blind_info["donor_other_country"],
                   self.blind_info["share_donor_hid_equals_own_hid"]), flush=True)
            if self.blind_info["donor_same_run"] > 0 or self.blind_info["donor_other_country"] > 0:
                raise SystemExit("BLIND FAIL: a donor is from the same run or from another country")
        self.flats = fl
        n = len(fl)
        sc = json.load(open(store + "static_cols.json"))
        self.s_cols, self.c_cols = sc["static"], sc["climate_onehot"]
        self.norm = json.load(open(store + "norm.json"))
        nch = self.norm["channels"]
        # --- households (both countries stacked; es first)
        parts, off, tot = [], {}, 0
        for cc in c.COUNTRIES:
            z = np.load(store + "hh_%s.npz" % cc)
            a = np.stack([z[nm] for nm in c.HH_CHANNELS], 0).astype(np.float32)          # [4, n_hh, 8760]
            off[cc] = tot
            tot += a.shape[1]
            parts.append(a)
        hh = np.concatenate(parts, 1)
        for i, nm in enumerate(c.HH_CHANNELS):
            hh[i] = (hh[i] - nch[nm]["mean"]) / nch[nm]["sd"]
        self.HHT = torch.from_numpy(hh).to(device)
        offs = fl["country"].map(off).to_numpy(dtype=np.int64)
        self.hh_row = torch.from_numpy(fl["hh_index"].to_numpy(dtype=np.int64) + offs).to(device)
        # --- neighbours [n, 3, M] (-1 padded)
        lists = []
        for k in KINDS:
            col = fl[k].fillna("").astype(str).tolist()
            lists.append([[int(t) + int(o) for t in s.split(";")] if s != "" else [] for s, o in zip(col, offs)])
        M = max(1, max(len(x) for L in lists for x in L))
        nb = np.full((n, 3, M), -1, dtype=np.int64)
        for k in range(3):
            for i, x in enumerate(lists[k]):
                if x:
                    nb[i, k, :len(x)] = x
        self.M = M
        self.nb = torch.from_numpy(nb).to(device)
        # --- weather and calendar
        clims = [x[2:] for x in self.c_cols]
        w = np.stack([np.load(store + "weather_%s.npy" % cid).astype(np.float32) for cid in clims], 0)    # [6,8760,7]
        for i, nm in enumerate(c.WEATHER_CHANNELS):
            w[:, :, i] = (w[:, :, i] - nch[nm]["mean"]) / nch[nm]["sd"]
        self.W = torch.from_numpy(w).to(device)
        cal = np.stack([np.load(store + "calendar_%s.npy" % cc).astype(np.float32) for cc in c.COUNTRIES], 0)   # [2,8760,5]
        for i, nm in enumerate(c.CALENDAR_CHANNELS):
            cal[:, :, i] = (cal[:, :, i] - nch[nm]["mean"]) / nch[nm]["sd"]
        self.CAL = torch.from_numpy(cal).to(device)
        cmap = {cid: i for i, cid in enumerate(clims)}
        self.cl_idx = torch.from_numpy(fl["climate_id"].map(cmap).to_numpy(dtype=np.int64)).to(device)
        self.cal_idx = torch.from_numpy(fl["country"].map({cc: i for i, cc in enumerate(c.COUNTRIES)}).to_numpy(dtype=np.int64)).to(device)
        # --- static vector
        s = fl[self.s_cols].to_numpy(dtype=np.float64)
        dev_build = stats is None
        if stats is None:
            sd = s.std(0)
            stats = {"mean": s.mean(0).tolist(), "sd": np.where(sd > 0, sd, 1.0).tolist()}
        self.stats = stats
        s = (s - np.array(stats["mean"])) / np.array(stats["sd"])
        if "zmin" not in stats or "zmax" not in stats:
            if not dev_build:
                raise KeyError("static_stats without zmin/zmax (rules AMENDMENT 2): refusing to load unclipped")
            stats["zmin"] = s.min(0).tolist()
            stats["zmax"] = s.max(0).tolist()
        zmin, zmax = np.array(stats["zmin"]), np.array(stats["zmax"])
        outside = (s < zmin) | (s > zmax)
        ncol = outside.sum(0)
        s = np.clip(s, zmin, zmax)
        print("STATIC_CLIP split=%s rows=%d values_clipped=%d columns_clipped=%s" %
              (split, n, int(outside.sum()), ",".join(nm for nm, k in zip(self.s_cols, ncol) if k > 0)), flush=True)
        self.clip_info = {"values_clipped": int(outside.sum()), "columns_clipped": {nm: int(k) for nm, k in zip(self.s_cols, ncol) if k > 0}}
        parts = [s]
        self.static_names = list(self.s_cols)
        if not drop_climate:
            parts.append(fl[self.c_cols].to_numpy(dtype=np.float64))
            self.static_names += list(self.c_cols)
        if drop_climate:
            print("STATIC_COLS split=%s before_drop=%d after_drop=%d (climate one-hot dropped: %d columns)" %
                  (split, len(self.s_cols) + len(self.c_cols), len(self.static_names), len(self.c_cols)), flush=True)
        self.static = torch.from_numpy(np.concatenate(parts, 1).astype(np.float32)).to(device)
        self.S = self.static.shape[1]
        self.dyn_names = dyn_names()
        self.n_dyn = len(self.dyn_names)
        # --- targets
        self.T = None
        self.tmu = torch.tensor([self.norm["targets"][t]["mean"] for t in TNAMES], dtype=torch.float32, device=device)
        self.tsd = torch.tensor([self.norm["targets"][t]["sd"] for t in TNAMES], dtype=torch.float32, device=device)
        if load_targets:
            if keep is None:
                self.T = torch.from_numpy(np.load(store + "targets_%s.npy" % split)).to(device)       # [n,8760,3] float32 raw kWh
            else:
                self.T = torch.from_numpy(np.ascontiguousarray(np.load(store + "targets_%s.npy" % split, mmap_mode="r")[keep])).to(device)
            assert self.T.shape == (n, H, 3), self.T.shape
        # --- pairs
        pp = store + "pairs_%s.parquet" % split
        pr = pd.DataFrame({"row_a": np.zeros(0, dtype=np.int64), "row_b": np.zeros(0, dtype=np.int64)}) if store == TEST_STORE else pd.read_parquet(pp)   # Step 6: no pairs table for the test lists (scored by the scorer)
        if keep is not None and store != TEST_STORE:
            newi = np.full(int(keep.max()) + 1 if len(keep) else 1, -1, dtype=np.int64)
            newi[keep] = np.arange(len(keep))
            ra, rb = pr["row_a"].to_numpy(dtype=np.int64), pr["row_b"].to_numpy(dtype=np.int64)
            ok = (ra <= keep.max()) & (rb <= keep.max())
            ok[ok] = (newi[ra[ok]] >= 0) & (newi[rb[ok]] >= 0)
            pr = pd.DataFrame({"row_a": newi[ra[ok]], "row_b": newi[rb[ok]]})
            print("PAIRS_FILTER split=%s country=%s pairs=%d" % (split, country, len(pr)), flush=True)
        self.pa = torch.from_numpy(pr["row_a"].to_numpy(dtype=np.int64)).to(device)
        self.pb = torch.from_numpy(pr["row_b"].to_numpy(dtype=np.int64)).to(device)
        self.ar_win = torch.arange(WIN, device=device)
        self.ar_out = torch.arange(OUTH, device=device)
        self.lo = (-self.tmu / self.tsd)           # standardised value of 0 kWh = the clip floor (outputs are clipped at 0 kWh)

    def n_rows(self):
        return len(self.flats)

    @torch.no_grad()
    def windows(self, rows, days, with_y=True):
        """rows, days: long tensors [B] on the device. Returns x [B,192,25], st [B,S], y [B,24,3] or None."""
        hrs = (24 * days[:, None] - HIST + self.ar_win[None, :]) % H                          # [B,192]
        own = self.HHT[:, self.hh_row[rows][:, None], hrs]                                     # [4,B,192]
        chans = [own[i] for i in range(4)]
        idx = self.nb[rows]                                                                    # [B,3,M]
        for k in range(3):
            ik = idx[:, k]
            valid = ik >= 0
            cnt = valid.sum(1)
            has = (cnt > 0).float()
            ikc = ik.clamp(min=0)
            for ch in (2, 3):                                                                  # people, appl_w
                g = self.HHT[ch][ikc[:, :, None], hrs[:, None, :]]                             # [B,M,192]
                m = (g * valid[:, :, None]).sum(1) / cnt.clamp(min=1)[:, None]
                chans.append(m * has[:, None])
            chans.append(has[:, None].expand(-1, WIN))
        # order must equal c.NB_CHANNELS: same_people, same_appl_w, same_flag, above_*, below_*  (done above in that order)
        wx = self.W[self.cl_idx[rows][:, None], hrs]                                           # [B,192,7]
        cx = self.CAL[self.cal_idx[rows][:, None], hrs]                                        # [B,192,5]
        x = torch.cat([torch.stack(chans, 2), wx, cx], 2)
        st = self.static[rows]
        y = None
        if with_y and self.T is not None:
            y = (self.T[rows[:, None], 24 * days[:, None] + self.ar_out[None, :]] - self.tmu) / self.tsd
        return x, st, y


def validation_draws(n_pairs, n_draws=20000, seed=20260930):
    """The fixed validation set: (pair index, day) draws, seed 20260930 (same for every configuration)."""
    g = np.random.default_rng(seed)
    return g.integers(0, n_pairs, n_draws), g.integers(0, NDAY, n_draws)
