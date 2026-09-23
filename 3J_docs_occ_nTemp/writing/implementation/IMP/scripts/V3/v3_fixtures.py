"""V3b fixtures: the CODE (NECB) occupancy schedules of the uninjected Default_NECB cells, written in
the four Step-7 product formats so they can be sent through the injector.

Values are READ from the frozen Default_NECB injected_resized.idf (all four must agree), never typed.
  office  (2 day types, 24 h)      <- NECB-A-Occupancy   (all 6 office Space types run it)
  retail  (3 day types, 48 slots)  <- NECB-C-Occupancy   (the 3 injected retail types run it after V2-D9)
  hotel   (12 months x 2, 48 slots)<- NECB-A-Occupancy   (guest rooms run it)
  residential pool (60 identical households, HHSIZE=K, DTYPE HighRise)
                                   <- NECB-A-Occupancy + NECB-Activity (the apartment carrier runs them)
The 2-day-type formats are exact only if Saturday == Sunday == Holidays in the source; asserted.

Negative control (arm X): office weekday profile rolled +3 h (np.roll), everything else identical.

    py -3 v3_fixtures.py            -> writes fixtures/*.csv and fixtures/fixtures_manifest.json
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v3_lib as L  # noqa: E402

RES_K = 2          # fixture household size (identical households; R uses the same K)
RES_POOL_N = 60    # >= 41 apartment Spaces in SuperTall (no-replacement draw)
SHIFT_H = 3


def parse_compact(txt, name):
    """{day-type token string: [24 hourly values]} for a Schedule:Compact with one Through: 12/31."""
    for m in re.finditer(r"(?im)^Schedule:Compact,\s*(?:!.*)?\n", txt):
        end = txt.find(";", m.end())
        fields = [re.sub(r"!.*", "", l).strip().rstrip(",;").strip()
                  for l in txt[m.end():end + 1].split("\n")]
        fields = [f for f in fields if f]
        if fields[0] != name:
            continue
        blocks, cur, until = {}, None, None
        throughs = [f for f in fields[2:] if f.lower().startswith("through")]
        if throughs != ["Through: 12/31"]:
            raise SystemExit("REFUSING: %s has Through fields %r (expected one 12/31)" % (name, throughs))
        for f in fields[2:]:
            fl = f.lower()
            if fl.startswith("through"):
                continue
            if fl.startswith("for"):
                cur = f.split(":", 1)[1].strip()
                blocks[cur] = []
            elif fl.startswith("until"):
                until = f.split(":", 1)[1].strip()
            else:
                blocks[cur].append((until, float(f)))
        out = {}
        for k, pairs in blocks.items():
            hourly, h0 = [], 0
            for u, v in pairs:
                hh, mm = [int(x) for x in u.split(":")]
                if mm != 0:
                    raise SystemExit("REFUSING: sub-hourly Until in %s/%s" % (name, k))
                hourly += [v] * (hh - h0)
                h0 = hh
            if len(hourly) != 24:
                raise SystemExit("REFUSING: %s/%s expands to %d hours" % (name, k, len(hourly)))
            out[k] = hourly
        return out
    raise SystemExit("REFUSING: schedule %s not found" % name)


def main():
    scheds = None
    for b in ("Tall", "SuperTall"):
        for c in ("MTL", "CLG"):
            txt = open(L.frozen_idf("Default_NECB", b, c), errors="replace").read()
            s = {n: parse_compact(txt, n) for n in ("NECB-A-Occupancy", "NECB-C-Occupancy", "NECB-Activity")}
            if scheds is None:
                scheds = s
            elif s != scheds:
                raise SystemExit("REFUSING: NECB schedules differ between frozen Default_NECB cells")
    A, C, ACT = scheds["NECB-A-Occupancy"], scheds["NECB-C-Occupancy"], scheds["NECB-Activity"]
    print("NECB-A day-type blocks:", list(A))
    print("NECB-C day-type blocks:", list(C))
    print("NECB-Activity blocks:", list(ACT))
    a_wd = A["Weekdays"]
    assert A["Saturday"] == A["Sunday"], "NECB-A Sat != Sun: 2-day-type office/hotel format not exact"
    assert A["WinterDesignDay"] == a_wd and A["SummerDesignDay"] == a_wd
    a_we = A["Saturday"]
    c_wd, c_sat, c_sun = C["Weekdays"], C["Saturday"], C["Sunday Holidays AllOtherDays"]
    act = ACT["AllDays"]
    assert len(set(act)) == 1, "NECB-Activity is not constant"

    os.makedirs(L.FIXTURES, exist_ok=True)

    def w(name, header, rows):
        p = os.path.join(L.FIXTURES, name)
        with open(p, "w", newline="\n") as f:
            f.write(",".join(header) + "\n")
            for r in rows:
                f.write(",".join(str(x) for x in r) + "\n")
        return p

    def office_rows(wd):
        return ([("Office_Knowledge", "observed", "Weekday", h, wd[h]) for h in range(24)] +
                [("Office_Knowledge", "observed", "Weekend", h, a_we[h]) for h in range(24)])
    hdr_o = ["office_archetype", "BAND", "Day_Type", "Hour", "AT_WORK_fraction"]
    p_off = w("v3_office_necb.csv", hdr_o, office_rows(a_wd))
    shifted = a_wd[-SHIFT_H:] + a_wd[:-SHIFT_H]           # np.roll(+3): value at h moves to h+3
    p_offx = w("v3_office_necb_shift3h.csv", hdr_o, office_rows(shifted))

    rows = []
    for pr in ("QC", "AB"):
        for dt, prof in (("Weekday", c_wd), ("Saturday", c_sat), ("Sunday", c_sun)):
            for slot in range(48):
                rows.append((pr, dt, slot, prof[slot // 2], 0))
    p_ret = w("v3_retail_necb.csv", ["PR", "Day_Type", "slot", "multiplier", "staff_shoulder_flag"], rows)

    rows = []
    for pr in ("QC", "AB"):
        for month in range(1, 13):
            for dt, prof in (("Weekday", a_wd), ("Weekend", a_we)):
                for slot in range(48):
                    rows.append((pr, month, dt, slot, prof[slot // 2]))
    p_hot = w("v3_hotel_necb.csv", ["PR", "MONTH", "Day_Type", "slot", "multiplier"], rows)

    rows = []
    for hh in range(1, RES_POOL_N + 1):
        for dt, prof in (("Weekday", a_wd), ("Weekend", a_we)):
            for h in range(24):
                rows.append((hh, dt, h, RES_K, "HighRise", 0, prof[h], act[0]))
    p_res = w("v3_residential_necb.csv", ["SIM_HH_ID", "Day_Type", "Hour", "HHSIZE", "DTYPE", "CONDO",
                                          "Occupancy_Schedule", "Metabolic_Rate"], rows)

    man = {"source": "frozen Default_NECB injected_resized.idf x4 (identical schedules asserted)",
           "RES_K": RES_K, "RES_POOL_N": RES_POOL_N, "SHIFT_H": SHIFT_H,
           "necb_a_weekday": a_wd, "necb_a_weekend": a_we, "necb_c": {"wd": c_wd, "sat": c_sat, "sun": c_sun},
           "necb_activity_W": act[0], "office_shifted_weekday": shifted,
           "files": {os.path.basename(p): L.md5_file(p) for p in (p_off, p_offx, p_ret, p_hot, p_res)}}
    with open(os.path.join(L.FIXTURES, "fixtures_manifest.json"), "w") as f:
        json.dump(man, f, indent=2)
    print(json.dumps(man["files"], indent=2))


if __name__ == "__main__":
    main()
