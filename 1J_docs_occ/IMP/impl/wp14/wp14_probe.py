import gzip, os, shutil, sqlite3, sys, tempfile
D = "/speed-scratch/o_iseri/1J_rerun/stage4/draws/block_1/NUS_RC1/iter_1/2005"
tmp = tempfile.mkdtemp(dir=os.environ.get("TMPDIR", "/tmp"))
p = os.path.join(tmp, "x.sql")
with gzip.open(D + "/eplusout.sql.gz", "rb") as fi, open(p, "wb") as fo:
    shutil.copyfileobj(fi, fo)
c = sqlite3.connect(p)
q = lambda s, a=(): c.execute(s, a).fetchall()
print("PROBE building area", q("select RowName,Value,Units from TabularDataWithStrings where TableName='Building Area'"))
print("PROBE end uses heat/cool/equip", q("select RowName,ColumnName,Value,Units from TabularDataWithStrings where TableName='End Uses' and RowName in ('Heating','Cooling','Interior Equipment','Interior Lighting') and Value not like '%0.00'"))
print("PROBE meters in sql dict", q("select distinct KeyValue,Name,ReportingFrequency,Units,IsMeter from ReportDataDictionary where IsMeter=1 and ReportingFrequency in ('Hourly','Zone Timestep') limit 40"))
print("PROBE simulations", q("select * from Simulations"))
print("PROBE time rows", q("select count(*), min(Year), max(Year) from Time where Interval=60"))
c.close(); os.remove(p); os.rmdir(tmp)
