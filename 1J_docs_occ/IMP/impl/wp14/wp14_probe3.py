import gzip, os, shutil, sqlite3, tempfile
D = "/speed-scratch/o_iseri/1J_rerun/stage4/draws/block_1/NUS_RC1/iter_1/2005"
tmp = tempfile.mkdtemp(dir=os.environ.get("TMPDIR", "/tmp"))
p = os.path.join(tmp, "x.sql")
with gzip.open(D + "/eplusout.sql.gz", "rb") as fi, open(p, "wb") as fo:
    shutil.copyfileobj(fi, fo)
c = sqlite3.connect(p)
rows = c.execute("select Name,ReportingFrequency,IsMeter,count(*) from ReportDataDictionary group by Name,ReportingFrequency,IsMeter order by IsMeter desc,Name").fetchall()
print("PROBE3 ReportDataDictionary distinct (Name,freq,IsMeter,n):", len(rows))
for r in rows[:60]:
    print("PROBE3", r)
c.close(); os.remove(p); os.rmdir(tmp)
