\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 4957
Instance GUID: 7a1bcfcb-4aed-4bfe-8336-af168ed4744d
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
__version__ = "2022.04.08"

import rhinoscriptsyntax as rs
#if x == 1 or x == 2:
if x == 1:
    a = 0
elif x ==2:
    a = 2
else:
    a = 1