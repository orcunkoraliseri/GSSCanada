\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 4651
Instance GUID: 4ccb4b5f-79e3-4211-8d20-603f8da416ce
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