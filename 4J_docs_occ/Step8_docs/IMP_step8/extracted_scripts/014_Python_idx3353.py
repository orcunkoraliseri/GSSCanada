\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 3353
Instance GUID: 7facd152-eeea-4515-9c61-695e319f0c01
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

__author__ = "orcun"
__version__ = "2021.09.25"


import rhinoscriptsyntax as rs
a = []
'2 if it is inside'
for i in range(len(x)): 
    if x[i] == 2:
        a.append(i)