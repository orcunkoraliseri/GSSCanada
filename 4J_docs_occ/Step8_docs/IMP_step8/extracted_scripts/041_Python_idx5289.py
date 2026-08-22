\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 5289
Instance GUID: 506bcc8c-dee5-4c1a-a4f0-88b56bfe462e
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

__author__ = "Siser"
__version__ = "2022.03.16"

import rhinoscriptsyntax as rs
if x >0:
    a = 1
else:
    a = 0