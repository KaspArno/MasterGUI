import os

from PyQt4.uic import loadUiType
from PyQt4.QtGui import QDialog, QDialogButtonBox, QFileDialog

FORM_CLASS, _ = loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/AllObjectWidget.ui'))

class AllObjectWidget(QDialog, FORM_CLASS):
    '''Widget showing all objects found'''

    def __init__(self, lltools, iface, parent):
        super(AllObjectWidget, self).__init__(parent)
        self.setupUi(self)
        self.lltools = lltools
        self.iface = iface
        self.canvas = iface.mapCanvas()
        
        #self.buttonBox.button(QDialogButtonBox.RestoreDefaults).clicked.connect(self.restoreDefaults)