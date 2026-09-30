import gzip, os, shutil, sqlite3, sys, tempfile
sys.path.insert(0, "/speed-scratch/o_iseri/1J_rerun/code")
from eSim_bem_utils import plotting
D = "/speed-scratch/o_iseri/1J_rerun/stage4/draws/block_1/NUS_RC1/iter_1/2005"
tmp = tempfile.mkdtemp(dir=os.environ.get("TMPDIR", "/tmp"))
p = os.path.join(tmp, "x.sql")
with gzip.open(D + "/eplusout.sql.gz", "rb") as fi, open(p, "wb") as fo:
    shutil.copyfileobj(fi, fo)
c = sqlite3.connect(p)
print("PROBE2 subcat rows", c.execute("select RowName,ColumnName,Value,Units from TabularDataWithStrings where TableName='End Uses By Subcategory' and Value not like '%0.00' and Units!='m3'").fetchall())
r = plotting.calculate_eui(c)
print("PROBE2 calculate_eui", {k: r[k] for k in ("eui", "total_floor_area", "conditioned_floor_area", "total_energy")}, r["end_uses_normalized"])
c.close(); os.remove(p); os.rmdir(tmp)
