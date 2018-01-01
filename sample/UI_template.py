import os
from maya import OpenMayaUI, cmds, mel
import pymel.core as pm
import uiStyle
import logging
from functools import partial
try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide import QtCore, QtGui
    QtWidgets = QtGui

reload(uiStyle)
# ------------------------------------------------------------------------------

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)

# ------------------------------------------------------------------------------

SIGNAL = QtCore.SIGNAL
SLOT = QtCore.SLOT

# ------------------------------------------------------------------------------   

def mayaWindow():
    """
    Get Maya's main window.
    
    :rtype: QMainWindow
    """
    # window = OpenMayaUI.MQtUtil.mainWindow()
    # window = shiboken.wrapInstance(long(window), QMainWindow)
    window = pm.ui.Window('MayaWindow').asQtObject()
    return window

# ------------------------------------------------------------------------------
__windowName__ = "PipelineTools"
__windowTitle__ = "Pipeline Tools"
__statusMessage__ = "All UI"
__version__ = "v01.0"
__author__ = "Nguyen Phi Hung"
__date__ = "20171231"
# ------------------------------------------------------------------------------
class main(QtWidgets.QMainWindow):
    '''
    Qt UI to rename Object in Scene
    '''
    def __init__(self, parent=None):
        super(main, self).__init__()
        try:
            pm.deleteUI(__windowName__)
        except:
            pass
        if parent:
            assert isinstance(parent, QtWidgets.QMainWindow), \
                'Parent is not of type QMainWindow'
            self.setParent(parent)
        else:
            self.setParent(mayaWindow())
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle(__windowTitle__)
        self.setObjectName(self._name)
        self.setStyleSheet(uiStyle.styleSheet)

    def _initUIValue(self):
        pass

    def _initMainUI(self):
        self._initUIValue()
        # create Widget
        self.topFiller = QtWidgets.QWidget(self)
        self.topFiller.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.bottomFiller = QtWidgets.QWidget(self)
        self.bottomFiller.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.mainCtner = QtWidgets.QWidget(self)
        # Create Layout
        self.mainLayout = QtWidgets.QVBoxLayout(self.mainCtner)
        # Add widget
        self.mainLayout.addWidget(self.topFiller)
        self.createMainWidgets()
        self.mainLayout.addWidget(self.bottomFiller)
        # Set Layout
        self.mainCtner.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainCtner)
        self.setStyleSheet(uiStyle.styleSheet)
        self.createMenuBar()
        self.createStatusBar()
        self._connectFunction()

    def createMainWidgets(self):
        pass

    def createMenuBar(self):
        # create Action
        def menuItem(name, func , parent=None):
            newAction = QtWidgets.QAction(name, self)
            newAction.triggered.connect(func)
            if parent:
                parent.addAction(newAction)
            return newAction
        self.reset_action = QtWidgets.QAction('Reset', self)
        self.reset_action.setToolTip('Reset UI To Default Value')
        self.reset_action.setStatusTip('Reset UI To Default Value')
        self.reset_action.triggered.connect(self.resetUI)
        # create Menu
        self.menubar = self.menuBar()
        self.optionmenu = self.menubar.addMenu('Option')
        self.optionmenu.addAction(self.reset_action)

    def createStatusBar(self):
        self.statusbar = self.statusBar()
        self.statusbar.showMessage('__statusMessage__')
    # UI Changed Action
    def createScriptJob(self,callbackEvent='SelectionChanged'):
        self.updateUIJob = pm.scriptJob(
            e= [callbackEvent,self.autoUpdateUI],
            parent = __windowName__,
            rp=True)

    def removeScriptJob(self):
        if hasattr(self, 'updateUIJob'):
            if pm.scriptJob(exists=self.updateUIJob):
                pm.scriptJob(k=self.updateUIJob)

    def showEvent(self, event):
        self._initMainUI()
        self.show()

    def closeEvent(self, event):
        self.close()

    def autoUpdateUI(self):
        pass

    def resetUI(self):
        self._initMainUI()
        self.show()

    def _connectFunction(self):
        pass

def show():
    win = main()
    win.show()
    return win

if __name__ =='__main__':
    try:
        app = QtWidgets.QApplication([])
    except:
        raise
    show()
    if app in globals():
        app.exec_()