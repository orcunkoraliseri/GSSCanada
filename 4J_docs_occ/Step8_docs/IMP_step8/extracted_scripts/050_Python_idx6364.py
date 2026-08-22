\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 6364
Instance GUID: 676bea4f-e636-4883-b090-1d3da5bc37e2
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