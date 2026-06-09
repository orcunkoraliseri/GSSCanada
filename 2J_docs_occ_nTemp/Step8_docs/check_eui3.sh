#!/encs/bin/bash
#SBATCH --job-name=check_eui3
#SBATCH --partition=ps
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:05:00
#SBATCH --output=/speed-scratch/o_iseri/ep_wrappers/check_eui3_%j.out

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python

$PYTHON - <<'PYEOF'
import sqlite3, os, glob

smoke = "/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected/smoke/SingleD__Montreal_6A"
sqls = sorted(glob.glob(os.path.join(smoke, "**", "eplusout.sql"), recursive=True))

for sql_path in sqls:
    hh = sql_path.split("/")[-3]
    con = sqlite3.connect(sql_path)

    # Schema: TabularData(TabularDataIndex, ReportType, ReportNumber, TableName,
    #         RowName, ColumnName, Units, Value) — all stored as text IDs in Strings
    # Check if Value is direct or via Strings
    sample = con.execute("SELECT * FROM TabularData LIMIT 3").fetchall()
    print(f"\n{hh} TabularData schema sample: {sample[0]}")

    # Try direct value access (newer E+ versions store values inline)
    try:
        # Get column names
        cols = [d[0] for d in con.execute("SELECT * FROM TabularData LIMIT 1").description]
        print(f"  Columns: {cols}")
    except: pass

    # Approach: join TabularData with Strings to decode string IDs
    # Strings table: (StringIndex, StringTypeIndex, Value)
    # TabularData refs StringIndex for ReportName, TableName, RowName, ColName, Value
    try:
        # Look for energy-per-area type rows — search across all text via Strings join
        # First get distinct report names to identify the right table
        rnames = con.execute("""
            SELECT DISTINCT s.Value
            FROM TabularData td
            JOIN Strings s ON s.StringIndex = td.ReportType
            LIMIT 30
        """).fetchall()
        print(f"  ReportTypes: {[r[0] for r in rnames]}")
    except Exception as e:
        print(f"  ReportType query failed: {e}")
        # Try without join
        rnames2 = con.execute("SELECT DISTINCT ReportType FROM TabularData LIMIT 10").fetchall()
        print(f"  Raw ReportType values: {rnames2}")

    # Try to get EUI rows directly
    try:
        eui_rows = con.execute("""
            SELECT s_rpt.Value, s_tbl.Value, s_row.Value, s_col.Value, s_val.Value, s_unit.Value
            FROM TabularData td
            JOIN Strings s_rpt  ON s_rpt.StringIndex  = td.ReportType
            JOIN Strings s_tbl  ON s_tbl.StringIndex  = td.TableName
            JOIN Strings s_row  ON s_row.StringIndex  = td.RowName
            JOIN Strings s_col  ON s_col.StringIndex  = td.ColumnName
            JOIN Strings s_val  ON s_val.StringIndex  = td.Value
            JOIN Strings s_unit ON s_unit.StringIndex = td.Units
            WHERE s_col.Value LIKE '%Area%' OR s_row.Value LIKE '%Total%Energy%'
            LIMIT 20
        """).fetchall()
        print(f"  EUI/Area rows:")
        for r in eui_rows:
            print(f"    {r}")
    except Exception as e:
        print(f"  EUI query failed: {e}")

    con.close()
PYEOF
