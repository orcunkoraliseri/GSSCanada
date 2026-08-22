\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 4753
Instance GUID: f0f222c4-83e3-41ad-9cfe-7c313a4bf63f
Description: Provides a scripting component.

Inputs:
  - x
  - y
  - z

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
__version__ = "2022.03.30"

import rhinoscriptsyntax as rs
if x == 1:
    a = z
else:
    a = y