\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 4438
Instance GUID: 9a87dd96-5ad2-4cba-9e79-127790e3e695
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

__author__ = "Siser"
__version__ = "2022.03.07"

import rhinoscriptsyntax as rs
if x>0:
    a=y
else:
    a=100