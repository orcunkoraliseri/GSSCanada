\"\"\"
Component: Python Script
NickName: Python
Component Index: 2118
Instance GUID: a73fe794-a0a4-4a80-bc5b-f3766616ed82
Description: GhPython provides a Python script component

Inputs:
  - s
  - swapUV
  - reverseU
  - reverseV

Outputs:
  - out
  - anchor
  - uVec
  - vVec
  - revSrf
\"\"\"

import Rhino

if reverseU:
    uS,uE = s.Domain(0)
    inter0 = Rhino.Geometry.Interval(-uE, -uS)
    s.SetDomain(0,inter0)
    s = s.Reverse(0)

if reverseV:
    vS,vE = s.Domain(1)
    inter1 = Rhino.Geometry.Interval(-vE, -vS)
    s.SetDomain(1,inter1)
    s = s.Reverse(1)

if swapUV:
    s = s.Transpose()

anchor = s.PointAt(0,0)
uend = s.PointAt(0.5,0)
vend = s.PointAt(0,0.5)
uVec = uend - anchor
vVec = vend - anchor

revSrf = s