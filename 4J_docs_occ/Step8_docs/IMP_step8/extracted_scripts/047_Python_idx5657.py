\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 5657
Instance GUID: 068b84c2-dfc9-424a-bfb3-9365e44eb36c
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
__version__ = "2022.04.06"

import rhinoscriptsyntax as rs
if x == 1 and y!=0:
    a = 1
else:
    a=0
