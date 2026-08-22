\"\"\"
Component: Python Script
NickName: Python
Component Index: 1211
Instance GUID: d5539b94-335c-4ef3-87c6-e3eacbfae9e8
Description: GhPython provides a Python script component

Inputs:
  - InList

Outputs:
  - TrueList
  - FalseList
\"\"\"
TrueList = []
FalseList = []
for id,value in enumerate(InList):
    if value == "True":
        TrueList.append(id)
    else:
        FalseList.append(id)