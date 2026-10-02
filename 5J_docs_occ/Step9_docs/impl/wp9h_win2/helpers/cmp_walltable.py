import csv,collections
a=list(csv.DictReader(open("2026-10-01_wp9c_wall_table_win.csv",encoding="utf-8")))
b=list(csv.DictReader(open("2026-10-01_wp9c_wall_table_win2.csv",encoding="utf-8")))
print(len(a),len(b),[x["stem"] for x in a]==[x["stem"] for x in b])
dc=collections.Counter(); ex={}
for x,y in zip(a,b):
    for k in x:
        if x[k]!=y[k]:
            dc[k]+=1; ex.setdefault(k,[]).append((x["stem"],x[k],y[k]))
print(dc)
for k,v in ex.items(): print(k,v[:3])
mx=0
for x,y in zip(a,b):
    for k in ("eligible_wall_area_m2","window_area_m2_idf"):
        if x[k]!=y[k]: mx=max(mx,abs(float(x[k])-float(y[k])))
print("max abs diff in the two area columns",mx)
