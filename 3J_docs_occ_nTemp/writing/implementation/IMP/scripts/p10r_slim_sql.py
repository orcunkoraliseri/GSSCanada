#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""p10r_slim_sql.py -- shrink <cell_dir>/run/eplusout.sql to only what the Step-8E aggregator
(`Leg3_4-split/Step8_docs/3rdJ_08E_aggregate_4split.py`) reads from it, so a P10R cell can be kept
on the tight local C: budget instead of carrying the full ~160 MB EnergyPlus SQLite output.

WHAT THE AGGREGATOR ACTUALLY READS (grep of the file; only two functions touch sql, nothing in
eSim_bem_utils reads it during aggregate_cell()):
  parse_channel_areas() ~:135  "SELECT ZoneName, FloorArea, Multiplier, IsPartOfTotalArea
                                 FROM Zones"
  read_calendar()       ~:336  "SELECT tm.TimeIndex, tm.Month, tm.Day, tm.Hour, tm.DayType
                                 FROM Time tm JOIN EnvironmentPeriods ep
                                   ON tm.EnvironmentPeriodIndex = ep.EnvironmentPeriodIndex
                                 WHERE ep.EnvironmentType = 3 AND tm.TimeIndex IN (
                                   SELECT DISTINCT rd.TimeIndex FROM ReportData rd
                                   JOIN ReportDataDictionary rdd
                                     ON rd.ReportDataDictionaryIndex = rdd.ReportDataDictionaryIndex
                                   WHERE rdd.Name = 'Electricity:Facility'
                                     AND (rdd.ReportingFrequency = 'Hourly'
                                          OR rdd.ReportingFrequency = 3))"
So the five tables that matter are Zones, Time, EnvironmentPeriods, ReportDataDictionary (all
kept whole -- each is small) and ReportData (the huge table, ~99% of the 160 MB; kept ONLY for
the rows whose ReportDataDictionaryIndex names 'Electricity:Facility', a strict superset of every
row either query can ever touch).

METHOD: ATTACH the source db, `CREATE TABLE ... AS SELECT * FROM src.<table> [WHERE ...]` (copies
schema+data without hand-listing E+-version-specific columns), add the two indices the queries
actually use, VACUUM, then os.replace() the finished tmp file onto eplusout.sql (atomic on the
same filesystem -- the original is untouched until the swap, so a crash mid-build never corrupts
the cell).

USAGE
  py -3 p10r_slim_sql.py <cell_dir> [--keep-name eplusout.sql] [--no-verify]
      slims <cell_dir>/run/<keep-name> in place, prints before/after size.
  py -3 p10r_slim_sql.py --self-test <full_sql_path> <scratch_dir>
      builds a slim copy AND a deliberately-broken copy (ReportDataDictionary dropped) into
      <scratch_dir>, for the control/negative-control check. Does not touch <full_sql_path>.
"""
from __future__ import annotations

import argparse
import os
import shutil
import sqlite3
import sys

FULL_COPY_TABLES = ["Zones", "EnvironmentPeriods", "Time", "ReportDataDictionary"]


def _build_slim(src_sql: str, dst_sql: str, drop_table: str | None = None) -> None:
    """Builds dst_sql (must not exist) as the slim copy of src_sql. If drop_table is given, that
    table is skipped -- used only to manufacture the negative control."""
    if os.path.exists(dst_sql):
        os.remove(dst_sql)
    conn = sqlite3.connect(dst_sql)
    try:
        conn.execute("ATTACH DATABASE ? AS src", (src_sql,))
        for tbl in FULL_COPY_TABLES:
            if tbl == drop_table:
                continue
            conn.execute(f"CREATE TABLE {tbl} AS SELECT * FROM src.{tbl}")
        if drop_table != "ReportData":
            conn.execute(
                "CREATE TABLE ReportData AS SELECT * FROM src.ReportData WHERE "
                "ReportDataDictionaryIndex IN (SELECT ReportDataDictionaryIndex FROM "
                "src.ReportDataDictionary WHERE Name = 'Electricity:Facility')"
            )
        if "ReportData" in _existing_tables(conn):
            conn.execute("CREATE INDEX idx_rd_rddi ON ReportData(ReportDataDictionaryIndex)")
            conn.execute("CREATE INDEX idx_rd_ti ON ReportData(TimeIndex)")
        if "Time" in _existing_tables(conn):
            conn.execute("CREATE INDEX idx_time_env ON Time(EnvironmentPeriodIndex)")
        conn.commit()
        conn.execute("DETACH DATABASE src")
        conn.commit()
    finally:
        conn.close()
    # VACUUM needs its own connection (cannot run inside the ATTACH transaction on some sqlite
    # builds) -- separate, matches "create, copy, VACUUM" as three distinct steps.
    conn = sqlite3.connect(dst_sql)
    try:
        conn.execute("VACUUM")
    finally:
        conn.close()


def _existing_tables(conn) -> set:
    return {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'").fetchall()}


def _verify(sql_path: str) -> tuple[bool, str]:
    """Runs the exact two aggregator queries against sql_path. Returns (ok, message)."""
    try:
        conn = sqlite3.connect(f"file:{sql_path}?mode=ro", uri=True)
        try:
            z = conn.execute(
                "SELECT ZoneName, FloorArea, Multiplier, IsPartOfTotalArea FROM Zones").fetchall()
            if not z:
                return False, "Zones query returned 0 rows"
            t = conn.execute(
                "SELECT tm.TimeIndex, tm.Month, tm.Day, tm.Hour, tm.DayType FROM Time tm "
                "JOIN EnvironmentPeriods ep ON tm.EnvironmentPeriodIndex = ep.EnvironmentPeriodIndex "
                "WHERE ep.EnvironmentType = 3 AND tm.TimeIndex IN ("
                "  SELECT DISTINCT rd.TimeIndex FROM ReportData rd "
                "  JOIN ReportDataDictionary rdd "
                "    ON rd.ReportDataDictionaryIndex = rdd.ReportDataDictionaryIndex "
                "  WHERE rdd.Name = 'Electricity:Facility' "
                "    AND (rdd.ReportingFrequency = 'Hourly' OR rdd.ReportingFrequency = 3)) "
                "ORDER BY tm.TimeIndex ASC").fetchall()
            if len(t) != 8760:
                return False, f"calendar query returned {len(t)} rows, expected 8760"
        finally:
            conn.close()
        return True, f"ok: Zones {len(z)} rows, calendar {len(t)} rows"
    except sqlite3.Error as e:
        return False, f"sqlite3.Error: {e}"


def slim_cell(cell_dir: str, keep_name: str = "eplusout.sql", verify: bool = True) -> tuple[int, int]:
    run_dir = os.path.join(cell_dir, "run")
    src = os.path.join(run_dir, keep_name)
    if not os.path.isfile(src):
        raise SystemExit(f"[slim] no {src}")
    before = os.path.getsize(src)
    tmp = os.path.join(run_dir, keep_name + ".slim_tmp")
    _build_slim(src, tmp)
    if verify:
        ok, msg = _verify(tmp)
        if not ok:
            os.remove(tmp)
            raise SystemExit(f"[slim] FAIL verify on {tmp} before swap: {msg}")
    os.replace(tmp, src)  # atomic on the same volume; src is untouched until this line succeeds
    after = os.path.getsize(src)
    print(f"[slim] {os.path.basename(cell_dir)}: {before/1e6:.1f} MB -> {after/1e6:.1f} MB "
          f"({100*(1-after/max(before,1)):.1f}% smaller)")
    return before, after


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cell_dir", nargs="?")
    ap.add_argument("--keep-name", default="eplusout.sql")
    ap.add_argument("--no-verify", action="store_true")
    ap.add_argument("--self-test", nargs=2, metavar=("FULL_SQL", "SCRATCH_DIR"))
    a = ap.parse_args()

    if a.self_test:
        full_sql, scratch = a.self_test
        os.makedirs(scratch, exist_ok=True)
        slim_path = os.path.join(scratch, "slim.sql")
        broken_path = os.path.join(scratch, "broken_missing_rdd.sql")
        _build_slim(full_sql, slim_path)
        ok, msg = _verify(slim_path)
        before = os.path.getsize(full_sql)
        after = os.path.getsize(slim_path)
        print(f"[self-test] slim: {before/1e6:.1f} MB -> {after/1e6:.1f} MB; verify: {ok} ({msg})")
        _build_slim(full_sql, broken_path, drop_table="ReportDataDictionary")
        ok2, msg2 = _verify(broken_path)
        print(f"[self-test] negative control (ReportDataDictionary dropped): verify: {ok2} ({msg2})")
        if ok and not ok2:
            print("[self-test] PASS: slim verifies clean, broken slim fails verify")
            sys.exit(0)
        print("[self-test] FAIL: expected slim ok / broken not-ok")
        sys.exit(1)

    if not a.cell_dir:
        ap.error("cell_dir required unless --self-test")
    slim_cell(a.cell_dir, keep_name=a.keep_name, verify=not a.no_verify)


if __name__ == "__main__":
    main()
