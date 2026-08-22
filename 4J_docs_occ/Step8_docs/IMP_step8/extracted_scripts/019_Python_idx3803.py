\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 3803
Instance GUID: 25edada6-0ed0-4b18-b941-8ece39009213
Description: Provides a scripting component.

Inputs:
  - x

Outputs:
  - out
  - a
\"\"\"
"""Provides a scripting component.
    Inputs:
        x: The x script variable
        y: The y script variable
    Output:
        a: The a output variable"""

__author__ = "Siser"
__version__ = "2022.02.23"

import rhinoscriptsyntax as rs
TrueList=[]
for i in range(len(x)):
    if x[i] == 'True':
        TrueList.append(i)
    else:
        pass
a = TrueList