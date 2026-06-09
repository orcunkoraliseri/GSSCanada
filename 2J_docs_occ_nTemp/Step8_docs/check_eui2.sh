#!/encs/bin/bash
#SBATCH --job-name=check_eui2
#SBATCH --partition=ps
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:05:00
#SBATCH --output=/speed-scratch/o_iseri/ep_wrappers/check_eui2_%j.out

PYTHON=/speed-scratch/o_iseri/envs/step4/bin/python

$PYTHON - <<'PYEOF'
import sqlite3, os, glob

smoke = "/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected/smoke/SingleD__Montreal_6A"
sql_path = glob.glob(os.path.join(smoke, "**", "eplusout.sql"), recursive=True)[0]
hh = sql_path.split("/")[-3]
print(f"Inspecting: {hh}")
print(f"SQL file: {sql_path}")
print(f"SQL size: {os.path.getsize(sql_path)/1024:.1f} KB")

con = sqlite3.connect(sql_path)

# List all tables
tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print(f"\nTables ({len(tables)}): {tables}")

# Check TabularDataWithStrings
for tbl in tables:
    try:
        cnt = con.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
        print(f"  {tbl}: {cnt} rows")
    except Exception as e:
        print(f"  {tbl}: ERROR {e}")

# If TabularDataWithStrings has rows, show distinct ReportNames
if "TabularDataWithStrings" in tables:
    rnames = con.execute("SELECT DISTINCT ReportName FROM TabularDataWithStrings LIMIT 20").fetchall()
    print(f"\nReportNames in TabularDataWithStrings: {[r[0] for r in rnames]}")

# Try Time series approach — annual from ReportMeterData
if "ReportMeterData" in tables:
    # Check meters
    mnames = con.execute("SELECT DISTINCT ReportMeterDataDictionaryIndex FROM ReportMeterData LIMIT 5").fetchall()
    print(f"\nReportMeterData indexes (sample): {mnames}")
    # Try ReportMeterDataDictionary
    if "ReportMeterDataDictionary" in tables:
        meters = con.execute("SELECT * FROM ReportMeterDataDictionary LIMIT 20").fetchall()
        print(f"\nMeters in dictionary:")
        for m in meters:
            print(f"  {m}")

# Check if there is a Time table for annual data
if "Time" in tables:
    time_sample = con.execute("SELECT * FROM Time LIMIT 3").fetchall()
    print(f"\nTime table sample: {time_sample}")

con.close()
PYEOF
