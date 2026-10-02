# -*- coding: utf-8 -*-
"""Step 9p items 4-6: additive edits of the Model A tools for Bologna on `_win_2026-10-05` (country switch MODELA_COUNTRY=IT).
Every edit is a one-spot replacement that must match exactly once; prints one `PATCH <file> <name> OK` line per edit.
A second run stops (the old text no longer matches). The old values (win_2026-10-01/02/03) and the Madrid `win_2026-10-05` behaviour must not
change (proved by re-running them in a scratch copy of the tools, see the state file)."""
import io, sys, os
TOOLS = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "tools"))


def patch(path, edits):
    t = io.open(path, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in t else "\n"      # the tool files use CRLF: keep their line ends
    edits = [(nm, o.replace("\n", nl), w.replace("\n", nl)) for nm, o, w in edits]
    for name, old, new in edits:
        n = t.count(old)
        if n != 1:
            sys.exit("STOP: %s edit %s matches %d times (nothing written)" % (path, name, n))
        t = t.replace(old, new)
    io.open(path, "w", encoding="utf-8", newline="").write(t)
    for name, old, new in edits:
        print("PATCH %s %s OK" % (os.path.basename(path), name))


Q = '"'
# ---------------------------------------------------------------------------------------------- static
S = os.path.join(TOOLS, "5thJ_modelA_static.py")
patch(S, [
    ("static_a_country_switch",
     'WIN2 = _VINTAGE in ("win_2026-10-02", "win_2026-10-03", "win_2026-10-05")   # fixed bases: the "outward" check replaces the "inverted" check\n',
     'WIN2 = _VINTAGE in ("win_2026-10-02", "win_2026-10-03", "win_2026-10-05")   # fixed bases: the "outward" check replaces the "inverted" check\n'
     '# step 9p (additive): MODELA_COUNTRY=IT with win_2026-10-05 = Bologna only, own names `_bol5` (cannot collide with the Madrid `_win5` files); unset = unchanged\n'
     '_COUNTRY = os.environ.get("MODELA_COUNTRY", "")\n'
     'if _COUNTRY not in ("", "IT") or (_COUNTRY and _VINTAGE != "win_2026-10-05"):\n'
     '    raise SystemExit("MODELA_COUNTRY must be empty or IT, and IT only with win_2026-10-05, got %r with %r" % (_COUNTRY, _VINTAGE))\n'
     '_BOL5 = (_COUNTRY == "IT")\n'),
    ("static_b_out",
     'OUT = os.path.join(IMPL, {"win": "static", "win2": "static_win2", "win3": "static_win3", "win5": "static_win5"}[_SUFFIX[_VINTAGE]])\n',
     'OUT = os.path.join(IMPL, {"win": "static", "win2": "static_win2", "win3": "static_win3", "win5": "static_win5"}[_SUFFIX[_VINTAGE]])\n'
     'if _BOL5:\n'
     '    OUT = os.path.join(IMPL, "static_bol5")\n'),
    ("static_c_districts",
     'ZONES_CSV = os.path.join(IMPL, "2026-10-01_wp9c_zone_map_%s.csv" % _SUFFIX[_VINTAGE])\n',
     'ZONES_CSV = os.path.join(IMPL, "2026-10-01_wp9c_zone_map_%s.csv" % _SUFFIX[_VINTAGE])\n'
     'if _BOL5:\n'
     '    _DISTRICTS = ("IT-BOL-GALVANI2",)\n'
     '    WALLS_CSV = os.path.join(IMPL, "2026-10-01_wp9c_wall_table_bol5.csv")\n'
     '    ZONES_CSV = os.path.join(IMPL, "2026-10-01_wp9c_zone_map_bol5.csv")\n'),
    ("static_d_planted_district",
     '    d = "ES-MAD-BERRUGUETE"\n    fl_rows, b_rows, chk, per_b, wrows, wcsv = results[d]\n',
     '    d = "IT-BOL-GALVANI2" if _BOL5 else "ES-MAD-BERRUGUETE"   # step 9p: the planted window-U fault runs on the district that is built\n    fl_rows, b_rows, chk, per_b, wrows, wcsv = results[d]\n'),
])

# ---------------------------------------------------------------------------------------------- buildsplit
B = os.path.join(TOOLS, "5thJ_modelA_buildsplit.py")
patch(B, [
    ("buildsplit_a_country",
     'if _SUF == "win5":\n    DISTRICTS = ("ES-MAD-BERRUGUETE",)\n',
     '_CTRY = os.environ.get("MODELA_COUNTRY", "")   # step 9p (additive): IT with win_2026-10-05 = Bologna, own names `_bol5`\n'
     'if _CTRY not in ("", "IT") or (_CTRY and _SUF != "win5"):\n'
     '    sys.exit("MODELA_COUNTRY must be empty or IT, and IT only with win_2026-10-05")\n'
     '_BOL5 = (_CTRY == "IT")\n'
     'if _BOL5:\n'
     '    WALL = os.path.join(STEP9, "impl", "2026-10-01_wp9c_wall_table_bol5.csv")\n'
     '    OUT = os.path.join(STEP9, "impl", "buildsplit_bol5")\n'
     'if _SUF == "win5":\n    DISTRICTS = ("ES-MAD-BERRUGUETE",)\n'),
    ("buildsplit_b_expect",
     '    EXPECT = {"ES-MAD-BERRUGUETE": 1164}',
     '    if _BOL5:\n'
     '        DISTRICTS = ("IT-BOL-GALVANI2",)\n'
     '        EXPECT = {"IT-BOL-GALVANI2": 1167}   # step 9p: measured independently in item 1 (1,179 stems minus 12 buildings with one `_whole` zone per floor)\n'
     '    else:\n'
     '        EXPECT = {"ES-MAD-BERRUGUETE": 1164}'),
    ("buildsplit_c_planted_district",
     '    victim = res["ES-MAD-BERRUGUETE"]["test"][0]\n'
     '    copy_planted["ES-MAD-BERRUGUETE"]["dev"] = copy_planted["ES-MAD-BERRUGUETE"]["dev"] + [victim]\n'
     '    ovp = overlap(copy_planted)\n'
     '    named = {d: v for d, v in ovp.items() if v}\n'
     '    planted_fired = (named == {"ES-MAD-BERRUGUETE": {victim["stem"]}})\n',
     '    PD = DISTRICTS[0]   # step 9p: the planted stem comes from the first district of the run (Madrid for every old value: unchanged)\n'
     '    victim = res[PD]["test"][0]\n'
     '    copy_planted[PD]["dev"] = copy_planted[PD]["dev"] + [victim]\n'
     '    ovp = overlap(copy_planted)\n'
     '    named = {d: v for d, v in ovp.items() if v}\n'
     '    planted_fired = (named == {PD: {victim["stem"]}})\n'),
])
print("done")
