import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
from qgis.core import *
 
class testDock(QObject):
    """This class controls all plugin-related GUI elements."""
 
    def __init__ (self,iface):
        """initialize the GUI control"""
        QObject.__init__(self)
        self.iface = iface
 
        # load the form
        path = os.path.dirname( os.path.abspath( __file__ ) )
        self.dock = uic.loadUi( os.path.join( path, "mywidget.ui" ) )
        self.iface.addDockWidget( Qt.RightDockWidgetArea, self.dock )