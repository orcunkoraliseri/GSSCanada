#!/encs/bin/bash
#SBATCH --job-name=check_eui4
#SBATCH --partition=ps
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:05:00
#SBATCH --output=/speed-scratch/o_iseri/ep_wrappers/check_eui4_%j.out

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python

$PYTHON - <<'PYEOF'
import sqlite3, os, glob

smoke = "/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected/smoke/SingleD__Montreal_6A"
sqls = sorted(glob.glob(os.path.join(smoke, "**", "eplusout.sql"), recursive=True))

for sql_path in sqls:
    hh = sql_path.split("/")[-3]
    con = sqlite3.connect(sql_path)
    # Schema: TabularData(... ReportNameIndex, TableNameIndex, RowNameIndex, ColumnNameIndex, UnitsIndex ... Value TEXT)
    # Strings(StringIndex, StringTypeIndex, Value)

    # List distinct report names
    rnames = con.execute("""
        SELECT DISTINCT s.Value FROM TabularData td
        JOIN Strings s ON s.StringIndex = td.ReportNameIndex
        LIMIT 30
    """).fetchall()
    print(f"\n{hh} ReportNames: {[r[0] for r in rnames]}")

    # Get EUI rows — look for "Energy Per Total Building Area" column
    eui = con.execute("""
        SELECT s_rpt.Value, s_tbl.Value, s_row.Value, s_col.Value, td.Value, s_unit.Value
        FROM TabularData td
        JOIN Strings s_rpt  ON s_rpt.StringIndex  = td.ReportNameIndex
        JOIN Strings s_tbl  ON s_tbl.StringIndex  = td.TableNameIndex
        JOIN Strings s_row  ON s_row.StringIndex  = td.RowNameIndex
        JOIN Strings s_col  ON s_col.StringIndex  = td.ColumnNameIndex
        JOIN Strings s_unit ON s_unit.StringIndex = td.UnitsIndex
        WHERE s_col.Value LIKE '%Per%Building%Area%'
           OR s_col.Value LIKE '%EUI%'
           OR s_row.Value LIKE 'Total Site Energy'
        LIMIT 20
    """).fetchall()
    print(f"  EUI rows:")
    for r in eui:
        print(f"    {r}")

    # Also try: look for "AnnualBuildingUtilityPerformanceSummary"
    bldg = con.execute("""
        SELECT s_row.Value, s_col.Value, td.Value, s_unit.Value
        FROM TabularData td
        JOIN Strings s_rpt  ON s_rpt.StringIndex  = td.ReportNameIndex
        JOIN Strings s_row  ON s_row.StringIndex  = td.RowNameIndex
        JOIN Strings s_col  ON s_col.StringIndex  = td.ColumnNameIndex
        JOIN Strings s_unit ON s_unit.StringIndex = td.UnitsIndex
        WHERE s_rpt.Value LIKE '%AnnualBuilding%' OR s_rpt.Value LIKE '%UtilityPerformance%'
        LIMIT 10
    """).fetchall()
    if bldg:
        print(f"  AnnualBuildingUtility rows: {bldg}")

    con.close()
PYEOF
