"""Rebuild the three 2030 hotel schedule products after the recovery-level switch (author, 2026-09-25).

The author approved replacing the unsourced 2030 recovery levels (AB 0.615, QC 0.635) with the observed
2023-2025 means (AB 0.597 from the Government of Alberta CBRE series, QC 0.610 from ISQ); evidence in
writing/implementation/IMP/author_checks_2026-09-25/item2_hotel_recovery_levels.md section 8.

Uses the P10R Step-7 module's own build_hotel_product / _resolve_hotel_2030_rates, so the product format
is the one the campaign already reads.

  --control   build from the CURRENT forecast into a temp dir and compare with the frozen md5s.
              Run it BEFORE editing the anchors: it must print CONTROL PASS (builder reproduces the
              frozen files byte for byte). After the anchor edit it must print CONTROL FAIL.
  --write     build into outputs_step7_P10R (atomic_write keeps a _BAK_ copy) and print new md5s.
"""
import argparse
import hashlib
import importlib.util
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve()
LEG3 = HERE.parents[4] / "Leg3_4-split"
S7 = LEG3 / "Step7_docs"

FROZEN = {
    "cons": "d6e834bab96d26c1830617064dec707d",
    "central": "4b3d3a4603cc0cccc6a1bf42139d69ee",
    "opt": "e0ab6c86fbe3c0ea2475f8cada6d1bd6",
}


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def load_p10r():
    sys.path.insert(0, str(S7))
    spec = importlib.util.spec_from_file_location("s7p10r", S7 / "3rdJ_07_aug_to_bem_4split_P10R.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def build(m, outdir):
    got = {}
    for blabel in ("cons", "central", "opt"):
        band = m.BUNDLE_MAP[blabel]["hotel_band"]
        rates = m._resolve_hotel_2030_rates(band)
        df = m.build_hotel_product(rates, f"2030/{blabel}")
        m.run_hotel_gates(df, label=f"2030/{blabel} (hotel_obs)")
        out = Path(outdir) / f"hotel_schedule_multiplier_2030_{blabel}.csv"
        m.atomic_write(df, out, "%.6f")
        got[blabel] = md5(out)
        rate = rates.groupby("PR")["occupancy_rate"].mean().round(4).to_dict()
        print(f"[hotel_obs] {blabel:8s} band={band:8s} mean rate {rate} md5 {got[blabel]}", flush=True)
    return got


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--control", action="store_true")
    g.add_argument("--write", action="store_true")
    a = ap.parse_args()
    m = load_p10r()
    if a.control:
        with tempfile.TemporaryDirectory() as td:
            got = build(m, td)
        same = {b: got[b] == FROZEN[b] for b in FROZEN}
        print(f"[hotel_obs] control match per band: {same}")
        print("CONTROL PASS" if all(same.values()) else "CONTROL FAIL")
    else:
        got = build(m, m.OUT_DIR)
        moved = {b: got[b] != FROZEN[b] for b in FROZEN}
        print(f"[hotel_obs] changed vs frozen per band: {moved}")
        print("WRITE DONE (all three changed)" if all(moved.values()) else "WRITE DONE BUT SOME BAND UNCHANGED")


if __name__ == "__main__":
    main()
