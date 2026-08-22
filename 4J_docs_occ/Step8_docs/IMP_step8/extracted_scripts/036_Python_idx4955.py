\"\"\"
Component: Python Script
NickName: Python
Component Index: 4955
Instance GUID: c29050a3-de79-4f9c-98ec-c7c1c8f43e9b
Description: GhPython provides a Python script component

Inputs:
  - x

Outputs:
  - out
  - a
\"\"\"
if x[0] == x[1]:
    a =True
    print("centroids are the same")
else:
    a =False
    print("centroids are not the same")