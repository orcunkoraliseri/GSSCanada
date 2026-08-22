\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 4943
Instance GUID: af209d28-4aca-43ed-9ed6-ac1be00639f4
Description: Provides a scripting component.

Inputs:
  - x

Outputs:
  - out
  - output
\"\"\"
"""Provides a scripting component.
    Inputs:
        x: The x script variable
        y: The y script variable
    Output:
        a: The a output variable"""

__author__ = "orcun"
__version__ = "2022.04.08"

import rhinoscriptsyntax as rs
if x == -1 or x==1:
    output = True
else:
    output= False