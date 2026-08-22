\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 4815
Instance GUID: f75e7b90-a1ba-407f-ade7-2320e6149aea
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
__version__ = "2022.04.06"

import rhinoscriptsyntax as rs
if x == True:
    a = 0
else:
    a=1
