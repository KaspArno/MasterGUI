from PyQt4.QtCore import pyqtSignal
from qgis.gui import QgsMapToolIdentifyFeature

class FeatureIdentifyTool(QgsMapToolIdentifyFeature):
	geomIdentified = pyqtSignal(object, object)
	
	def __init__(self, iface, layer, x, y):
		QgsMapToolIdentify.__init__(self, iface.mapCanvas())
		self.canvasReleaseEvent(layer,x,y)
		print "FeatureIdentifyTool initialised"
	
	def canvasReleaseEvent(self,layer,x,y):
		results = self.identify(x, y, self.ActiveLayer, [layer], self.VectorLayer)
		print results
		if len(results) > 0:
			self.geomIdentified.emit(results[0].mLayer, results[0].mFeature)

	def doWhatEver(self, feature):
		print "I'm doing what ever i want!"