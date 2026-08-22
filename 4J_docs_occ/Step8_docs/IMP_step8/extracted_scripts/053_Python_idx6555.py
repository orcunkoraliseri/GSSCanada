\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 6555
Instance GUID: d02dfe30-d336-4eff-b54a-fa95f8c78976
Description: Provides a scripting component.

Inputs:
  - x
  - y

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
__version__ = "2022.05.09"

import rhinoscriptsyntax as rs
if y == 1:
    a = 'Null'
else:
    a = x