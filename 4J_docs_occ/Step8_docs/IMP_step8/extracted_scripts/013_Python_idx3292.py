\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 3292
Instance GUID: 6e9cd69e-20dd-4360-9e57-2ef2665cb317
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
__version__ = "2022.02.03"

import rhinoscriptsyntax as rs
if x == 0:
    a = 0
else:
    a = 1