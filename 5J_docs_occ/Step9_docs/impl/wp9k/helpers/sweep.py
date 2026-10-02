import sys; sys.path.insert(0,'.')
from degen_lib import *
E="C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11/%s_win_2026-10-03/idfs/%s.idf"
ES="ES-MAD-BERRUGUETE"; IT="IT-BOL-GALVANI2"
b=[(ES,"1271cddbf6bd1e8a")]+[(ES,s) for s in ["919761afea1827b3","0275c53572b2ff9f","7307694dddf93fb6"]]+[(IT,s) for s in ["504fa19567bbc2b7","1ef46361a8060ff9","13c60875a803e164","b3f8d90890ff6314"]]
S={x:read_surfaces(E%x) for x in b}
for t in [0.0005,0.001,0.002,0.005,0.0072,0.0075,0.01,0.0127,0.02,0.05]:
    print(t,[sum(degenerate(s[4],t,t) for s in S[x]) for x in b])
