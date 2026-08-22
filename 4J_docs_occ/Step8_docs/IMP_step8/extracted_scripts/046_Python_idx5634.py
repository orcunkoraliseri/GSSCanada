\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 5634
Instance GUID: b088fa26-8691-49b5-890a-fdb1c1dcce35
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
else:
    a = 1