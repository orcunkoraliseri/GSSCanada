\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 6564
Instance GUID: 4ea46cde-a241-427a-88aa-17bb68f01876
Description: Provides a scripting component.

Inputs:
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
    a = 0
else:
    a = 1