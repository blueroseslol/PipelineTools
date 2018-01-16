import os
import sys

# from __future__ import print_function, absolute_import, unicode_literals, division

basePath = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), '..'))
print basePath
if basePath not in sys.path:
    sys.path.append(basePath)
import nimble
import PipelineTools as pt
import pymel.core as pm
from nimble import NimbleScriptBase

RenamerUI = pt.main.ui.RenamerUI
conn = nimble.getConnection()
# conn.runPythonClass(RenamerUI.show)
result = conn.runPythonClass(pm.polySphere)
result = conn.runPythonClass(pm.selected)
print result