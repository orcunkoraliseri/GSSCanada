\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 4654
Instance GUID: 9401225e-b280-4f3b-b410-6496e2c57707
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
__version__ = "2022.03.23"

import rhinoscriptsyntax as rs
if x == 1:
    a = 1
else:
    a = 0