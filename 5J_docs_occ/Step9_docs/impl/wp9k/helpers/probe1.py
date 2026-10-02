import sys; sys.path.insert(0,'.')
from degen_lib import *
B="C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11/ES-MAD-BERRUGUETE_win_2026-10-03/idfs/%s.idf"
for stem in ["1271cddbf6bd1e8a","7307694dddf93fb6"]:
    s=read_surfaces(B%stem)
    print(stem,len(s), "nverts counts", {n:sum(1 for x in s if len(x[4])==n) for n in set(len(x[4]) for x in s)})
    for td,tc in [(0.001,0.001),(0.01,0.01),(0.001,0.01),(0.01,0.001),(0.0,0.0)]:
        print(" tol",td,tc, sum(degenerate(x[4],td,tc) for x in s))
s=read_surfaces(B%"1271cddbf6bd1e8a")
import math
tri=[x for x in s if len(x[4])==3]
print(len(tri))
for x in tri[:14]: 
    v=x[4]; print(x[1],x[3],[round(d(v[i],v[(i+1)%3]),4) for i in range(3)])
