#!/encs/bin/bash
#SBATCH --job-name=check_eui
#SBATCH --partition=ps
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:05:00
#SBATCH --output=/speed-scratch/o_iseri/ep_wrappers/check_eui_%j.out

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python
SMOKE=/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected/smoke/SingleD__Montreal_6A

$PYTHON - <<'PYEOF'
import sqlite3, os, glob

smoke = "/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected/smoke/SingleD__Montreal_6A"
FLOOR_AREA_M2 = 144.0  # approximate SingleD floor area

sqls = glob.glob(os.path.join(smoke, "**", "eplusout.sql"), recursive=True)
print(f"Found {len(sqls)} SQL files")
for sql_path in sorted(sqls):
    hh = sql_path.split("/")[-3]
    try:
        con = sqlite3.connect(sql_path)
        # Query annual site energy from TabularDataWithStrings
        cur = con.execute("""
            SELECT Value, Units FROM TabularDataWithStrings
            WHERE ReportName='AnnualBuildingUtilityPerformanceSummary'
              AND TableName='Site:EnergyUse'
              AND RowName='Total Site Energy'
              AND ColumnName='Energy Per Total Building Area'
        """)
        row = cur.fetchone()
        if row:
            print(f"  {hh}: EUI={row[0]} {row[1]}")
        else:
            # Try alternative query
            cur2 = con.execute("""
                SELECT Value, Units FROM TabularDataWithStrings
                WHERE TableName='Site:EnergyUse'
                  AND ColumnName='Energy Per Total Building Area'
                LIMIT 5
            """)
            rows2 = cur2.fetchall()
            print(f"  {hh}: alt query -> {rows2[:3]}")
        con.close()
    except Exception as e:
        print(f"  {hh}: ERROR {e}")
PYEOF
