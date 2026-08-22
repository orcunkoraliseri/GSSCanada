\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 5604
Instance GUID: d5e114e8-e394-4dba-9b83-862ebf89b008
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
__version__ = "2022.03.08"

import rhinoscriptsyntax as rs
from itertools import groupby
a = [sum(1 for _ in group) for _, group in groupby(x)]