import os

from PyQt4 import QtCore, QtGui, uic


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/testDock.ui'))

class testDockDialog(QtGui.QDockWidget, FORM_CLASS):
    def __init__(self, parent=None):
    	super(testDockDialog, self).__init__(parent)
        #QtGui.QDockWidget.__init__(self)
        #self.ui = testDock()
        self.setupUi(self)



# class MasterDialog(QtGui.QDialog, FORM_CLASS):
#     def __init__(self, parent=None):
#         """Constructor."""
#         super(MasterDialog, self).__init__(parent)
#         # Set up the user interface from Designer.
#         # After setupUI you can access any designer object by doing
#         # self.<objectname>, and you can use autoconnect slots - see
#         # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
#         # #widgets-and-dialogs-with-auto-connect
#         self.setupUi(self)