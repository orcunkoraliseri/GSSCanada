\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 6360
Instance GUID: 04bb7e4a-e690-4401-b615-e70e4575e0d6
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
__version__ = "2022.05.06"

import rhinoscriptsyntax as rs
#0: masonry
#1: concrete
if x == True:
    a = 0
else:
    a = 1