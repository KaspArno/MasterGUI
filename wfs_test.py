import urllib2
import urllib
from xml.etree import ElementTree
import re
from PyQt4.QtNetwork import QHttp
import random
from PyQt4 import QtCore, QtGui
import os
import tempfile
from osgeo import gdal
from osgeo import ogr
import logging
import string
#from featuretype import FeatureType
from master_dialog import MasterDialog

class FeatureType(object):

    def __init__(self, name):
        self.__name__ = name
        self.__title = ""
        self.__abstract = ""
        self.__namespace = ""
        self.__namespace_prefix = ""
        self.__metadata_url = ""

        self.__wgs84bbox_east = 0
        self.__wgs84bbox_south = 0
        self.__wgs84bbox_west = 0
        self.__wgs84bbox_north = 0

    def getName(self):
        return self.__name__

    def getTitle(self):
        return self.__title

    def setTitle(self, title):
        self.__title = title

    def getAbstract(self):
        return self.__abstract

    def setAbstract(self, abstract):
        self.__abstract = abstract

    def getNamespace(self):
        return self.__namespace.encode('utf8')

    def setNamespace(self, namespace):
        self.__namespace = namespace.decode('utf8')

    def getNamespacePrefix(self):
        return self.__namespace_prefix

    def setNamespacePrefix(self, namespace_prefix):
        self.__namespace_prefix = namespace_prefix

    def getMetadataUrl(self):
        return self.__metadata_url

    def setMetadataUrl(self, metadata_url):
        self.__metadata_url = metadata_url


    def getWgs84BoundingBoxEast(self):        
        return self.__wgs84bbox_east

    def setWgs84BoundingBoxEast(self, east):
        self.__wgs84bbox_east = east

    def getWgs84BoundingBoxSouth(self):        
        return self.__wgs84bbox_south

    def setWgs84BoundingBoxSouth(self, south):
        self.__wgs84bbox_south = south

    def getWgs84BoundingBoxWest(self):        
        return self.__wgs84bbox_west

    def setWgs84BoundingBoxWest(self, west):
        self.__wgs84bbox_west = west

    def getWgs84BoundingBoxNorth(self):        
        return self.__wgs84bbox_north

    def setWgs84BoundingBoxNorth(self, north):
        self.__wgs84bbox_north = north


class wfs_test(QtGui.QDialog):
    i = 0
    def __init__(self, iface):
        QtGui.QDialog.__init__(self)
        self.iface = iface
        self.onlineresource = "https://wfs.geonorge.no/skwms1/wfs.tilgjengelighettettsted?"
        self.vendorparameters = ""
        self.feature_type = []
        self.featuretypes = {}

        self.logger = logging.getLogger('WFS 2.0 Client')
        self.vlayer = None
        self.dlg = MasterDialog()

    def get_namespace_map(self, xml):
        nsmap = {}
        for i in [m.start() for m in re.finditer('xmlns:', xml)]:
            j = i + 6
            prefix = xml[j:xml.find("=", j)]
            k = xml.find("\"", j)
            uri = xml[k + 1:xml.find("\"", k + 1)]

            prefix = prefix.strip()
            # uri = uri.replace("\"","")
            uri = uri.strip()
            # text+= prefix + " " + uri + "\n"

            nsmap[prefix] = uri
        return nsmap

    def get_temppath(self, filename):
        tmpdir = os.path.join(tempfile.gettempdir(),'MasterGUI')
        if not os.path.exists(tmpdir):
            os.makedirs(tmpdir)
        tmpfile= os.path.join(tmpdir, filename)
        return tmpfile


    def getCapabilities(self):

        print "resources + " + self.onlineresource
        request = "{0}{1}".format(self.onlineresource, "{0}service=WFS&acceptversions=2.0.0&request=GetCapabilities".format("&"))

        response = urllib2.urlopen(request, None, 10)

        buf = response.read()

        root = ElementTree.fromstring(buf)


        nswfs = "{http://www.opengis.net/wfs/2.0}"
        nsxlink = "{http://www.w3.org/1999/xlink}"
        nsows = "{http://www.opengis.net/ows/1.1}"


        for target in root.findall("{0}OperationsMetadata/{0}Operation".format(nsows)):
            if target.get("name") == "GetFeature":
                ##print "GETFEATURE"
                for subtarget in target.findall("{0}DCP/{0}HTTP/{0}Get".format(nsows)):
                    ##print "SUBTARGET"
                    getfeatureurl = subtarget.get("{0}href".format(nsxlink))
                    ##print getfeatureurl
                    if not "?" in getfeatureurl:
                        self.onlineresource = getfeatureurl
                        ##print "NOT ? !!!"
                    else:
                        ##print "IS ? !!!"
                        self.onlineresource = getfeatureurl[:getfeatureurl.find("?")]
                        self.vendorparameters = getfeatureurl[getfeatureurl.find("?"):].replace("?", "&")
                        ##print "onlineresource: " + self.onlineresource
                        ##print "vendorparameters: " + self.vendorparameters
        for target in root.findall("{0}FeatureTypeList/{0}FeatureType".format(nswfs)):
            ##print "target"
            for name in target.findall("{0}Name".format(nswfs)):
                ##print "name"
                self.feature_type.append(name.text) #endringer fra orginal koden #self.ui.cmbFeatureType.addItem(name.text,name.text)
                featuretype = FeatureType(name.text)
                ##print name.text
                if ":" in name.text:
                    nsmap = self.get_namespace_map(buf)
                    ##print nsmap
                    for prefix in nsmap:
                        ##print prefix
                        if prefix == name.text[:name.text.find(":")]:
                            ##print name.text[:name.text.find(":")]
                            featuretype.setNamespace(nsmap[prefix])
                            featuretype.setNamespacePrefix(prefix)
                            break
                for title in target.findall("{0}Title".format(nswfs)):
                    ##print "title"
                    featuretype.setTitle(title.text)
                for abstract in target.findall("{0}Abstract".format(nswfs)):
                    featuretype.setAbstract(abstract.text)
                for metadata_url in target.findall("{0}MetadataURL".format(nswfs)):
                    featuretype.setMetadataUrl(metadata_url.get("{0}href".format(nsxlink)))
                for bbox in target.findall("{0}WGS84BoundingBox".format(nsows)):
                    ##print "bbox"
                    for lowercorner in bbox.findall("{0}LowerCorner".format(nsows)):
                        ##print "lowercorner"
                        featuretype.setWgs84BoundingBoxEast(lowercorner.text.split(' ')[0])
                        featuretype.setWgs84BoundingBoxSouth(lowercorner.text.split(' ')[1])
                    for uppercorner in bbox.findall("{0}UpperCorner".format(nsows)):
                        featuretype.setWgs84BoundingBoxWest(uppercorner.text.split(' ')[0])
                        featuretype.setWgs84BoundingBoxNorth(uppercorner.text.split(' ')[1])
                self.featuretypes[name.text] = featuretype
                querytype="adhocquery"
                ##print name.text
        
        ##print self.featuretypes["app:TettstedInngangBygg"]        
        #for f in self.featuretypes:
            ##print f
            ##print "?"


    ### Get features ###
    def getFeature(self):
        wfs_test.i += 1 #debug feauture
        print "wfs i :" + str(wfs_test.i)
        #query_string = "?service=WFS&request=GetFeature&version=2.0.0&STOREDQUERY_ID={0}".format(self.feature_type[1]) # endret format(self.ui.cmbFeatureType.currentText())
        print "GetFeature"
        featuretype = self.featuretypes[self.feature_type[1]] #self.featuretypes[self.ui.cmbFeatureType.currentText()]
        
        typeNames= urllib.quote(self.feature_type[1].encode('utf8')) #urllib.quote(self.ui.cmbFeatureType.currentText().encode('utf8'))

        query_string = "?service=WFS&request=GetFeature&version=2.0.0&srsName={0}&typeNames={1}".format( "urn:ogc:def:crs:EPSG::{0}".format(str(self.iface.mapCanvas().mapRenderer().destinationCrs().postgisSrid())).strip(), typeNames)
        query_string += "&namespaces=xmlns({0},{1})".format(featuretype.getNamespacePrefix(), urllib.quote(featuretype.getNamespace(),""))
        query_string+= "&count={0}".format("1000")
        query_string+=self.vendorparameters

        self.httpGetId = 0
        self.httpRequestAborted = False

        #self.setup_qhttp()
        self.http = QHttp(self)
        print self.http
        self.http.requestFinished.connect(self.httpRequestFinished)
        #self.http.dataReadProgress.connect(self.updateDataReadProgress)
        self.http.responseHeaderReceived.connect(self.readResponseHeader)
        #self.http.authenticationRequired.connect(self.authenticationRequired)
        self.http.sslErrors.connect(self.sslErrors)

        layername="wfs{0}".format(''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(6)))
        ##print layername
        return self.downloadFile(self.onlineresource, query_string, self.get_temppath("{0}.gml".format(layername)))
    
    #Download File
    # QHttp Slot
    def downloadFile(self, onlineResource, queryString, fileName):
        print "DownloadFile"
        print "onlineResource: " + onlineResource
        #print "queryString: " + queryString
        print "fileName: " + fileName
        #self.lock_ui()
        #print "onlineResource: " + onlineResource
        #print "queryString: " + queryString
        #print "fileName: " + fileName
        url = QtCore.QUrl(onlineResource)
        #print url
        if QtCore.QFile.exists(fileName):
            print "File Exists"
            QtCore.QFile.remove(fileName)

        self.outFile = QtCore.QFile(fileName)
        print "1:"
        print self.outFile
        #print self.outFile
        if not self.outFile.open(QtCore .QIODevice.WriteOnly):
            print "not self.outFile.open(QtCore .QIODevice.WriteOnly)"
            QtGui.QMessageBox.information(self, 'Error', 'Unable to save the file %s: %s.' % (fileName, self.outFile.errorString()))
            self.outFile = None
            return

        port = url.port()
        print port
        if port == -1:
            #print "port is -1"
            port = 0
            #print "port = 0"
        #print "2: "
        #print self.outFile
        if onlineResource.startswith("https"):
            #print "httpS"
            #print "3"
            #print self.outFile
            #print url.host()
            print QHttp.ConnectionModeHttps
            self.http.setHost(url.host(), QHttp.ConnectionModeHttps, port)
            print QHttp.ConnectionModeHttps
            #print "4"
            #print self.outFile
        else:
            print "http"
            self.http.setHost(url.host(), QHttp.ConnectionModeHttp, port)
        #print "5: "
        #print self.outFile
        self.httpRequestAborted = False
        #print "6: "
        #print self.outFile
        #self.ui.progressBar.setVisible(True)
        self.httpGetId = self.http.get(url.path() + queryString, self.outFile)
        print "httpGetId (downloadFile):"
        print self.httpGetId
        print "XXX"
        #print self.httpGetId
        #fileName = self.get_temppath("{0}.gml".format(layername))


    # Setup Qhttp (Proxy)
    def setup_qhttp(self):
        self.http = QHttp(self)
        #if not self.getProxy() == "":
        #    self.http.setProxy(QgsNetworkAccessManager.instance().fallbackProxy()) # Proxy

    # QHttp Slot
    def httpRequestFinished(self, requestId, error):
        print "httpRequestFinished XxX"
        if requestId != self.httpGetId:
            print "requestId != httpGetId"
            #print "requestId: "
            #print requestId
            print "httpGetId (httpRequestFinished):"
            print self.httpGetId
            return

        if self.httpRequestAborted:
            print "Request Aborted"
            if self.outFile is not None:
                print "outfile not none"
                self.outFile.close()
                self.outFile.remove()
                self.outFile = None
            return

        self.outFile.close()

        #self.ui.progressBar.setMaximum(1)
        #self.ui.progressBar.setValue(1)

        if error:
            self.outFile.remove()
            QtGui.QMessageBox.critical(self, "Error", "Download failed: %s." % self.http.errorString())
        else:
            # Parse and check only small files
            if os.path.getsize(str(self.outFile.fileName())) < 5000:
                root = ElementTree.parse(str(self.outFile.fileName())).getroot()
                if not self.is_exception(root):
                    if not self.is_empty_response(root):
                        self.load_vector_layer(str(self.outFile.fileName()), self.feature_type[1])
                    else:
                        QtGui.QMessageBox.information(self, "Information", "0 Features returned!")
                        #self.ui.lblMessage.setText("")
            else:
                self.load_vector_layer(str(self.outFile.fileName()), self.feature_type[1])

        #self.ui.progressBar.setMaximum(1)
        #self.ui.progressBar.setValue(0)
        #self.unlock_ui()

    # QHttp Slot
        # Check for genuine error conditions.Gz
    

    def readResponseHeader(self, responseHeader):
        if responseHeader.statusCode() not in (200, 300, 301, 302, 303, 307):
            QtGui.QMessageBox.critical(self, 'Error',
                    'Download failed: %s.' % responseHeader.reasonPhrase())
            #self.ui.lblMessage.setText("")
            self.httpRequestAborted = True
            self.http.abort()
    def sslErrors(self, errors):
        errorString = ""
        for error in errors:
            errorString+=error.errorString() + "\n"
        # QtGui.QMessageBox.critical(self, "Error", errorString)

        self.http.ignoreSslErrors()

    def readResponseHeader(self, responseHeader):
        if responseHeader.statusCode() not in (200, 300, 301, 302, 303, 307):
            QtGui.QMessageBox.critical(self, 'Error',
                    'Download failed: %s.' % responseHeader.reasonPhrase())
            #self.ui.lblMessage.setText("")
            self.httpRequestAborted = True
            self.http.abort()

    def updateDataReadProgress(self, bytesRead, totalBytes):
        print "updateDataReadProgress"
        if self.httpRequestAborted:
            return
        self.dlg.progressBar.setMaximum(totalBytes)
        self.dlg.progressBar.setValue(bytesRead)
        self.dlg.lblMessage.setText("Please wait while downloading - {0} Bytes downloaded!".format(str(bytesRead)))

    # WFS 2.0 UTILS

    # check for OWS-Exception
    def is_exception(self, root):
        for namespace in ["{http://www.opengis.net/ows}", "{http://www.opengis.net/ows/1.1}"]:
        # check correct Rootelement
            if root.tag == "{0}ExceptionReport".format(namespace):
                for exception in root.findall("{0}Exception".format(namespace)):
                    for exception_text in exception.findall("{0}ExceptionText".format(namespace)):
                        QtGui.QMessageBox.critical(self, "OWS Exception", "OWS Exception returned from the WFS:<br>"+ str(exception_text.text))
                        self.ui.lblMessage.setText("")
                return True
        return False

    # Check for empty GetFeature result
    def is_empty_response(self, root):
        # deegree 3.2: numberMatched="unknown" does return numberReturned="0" instead of numberReturned="unknown"
        # https://portal.opengeospatial.org/files?artifact_id=43925
        if not root.get("numberMatched") == "unknown":
            # no Features returned?
            if root.get("numberReturned") == "0":
                return True
        return False

    def load_vector_layer(self, filename, layername):
        print "load vector layer"
        #print "filename: " + filename
        #print "layername: " + layername
        #self.ui.lblMessage.setText("Loading GML - Please wait!")
        self.logger.debug("### LOADING GML ###")

        # Configure OGR/GDAL GML-Driver
        resolvexlinkhref = False #self.settings.value("/Wfs20Client/resolveXpathHref")
        attributestofields = False #self.settings.value("/Wfs20Client/attributesToFields")
        disablenasdetection = True #self.settings.value("/Wfs20Client/disableNasDetection")

        gdaltimeout = "5"
        self.logger.debug("GDAL_HTTP_TIMEOUT " + gdaltimeout)
        gdal.SetConfigOption("GDAL_HTTP_TIMEOUT", gdaltimeout)
        if resolvexlinkhref and resolvexlinkhref == "true":
            gdal.SetConfigOption('GML_SKIP_RESOLVE_ELEMS', 'NONE')
            self.logger.debug("resolveXpathHref " + resolvexlinkhref)
        else:
            gdal.SetConfigOption('GML_SKIP_RESOLVE_ELEMS', 'ALL')

        if attributestofields and attributestofields == "true":
            gdal.SetConfigOption('GML_ATTRIBUTES_TO_OGR_FIELDS', 'YES')
            self.logger.debug("attributesToFields " + attributestofields)
        else:
            gdal.SetConfigOption('GML_ATTRIBUTES_TO_OGR_FIELDS', 'NO')

        nasdetectionstring = "NAS-Operationen.xsd;NAS-Operationen_optional.xsd;AAA-Fachschema.xsd"
        if not disablenasdetection or disablenasdetection == "true":
            nasdetectionstring = 'asdf/asdf/asdf'
        #print "nasdetectionstring: " + nasdetectionstring
        self.logger.debug("Using 'NAS_INDICATOR': " + nasdetectionstring)
        gdal.SetConfigOption('NAS_INDICATOR', nasdetectionstring)

        # Analyse GML-File
        ogrdriver = ogr.GetDriverByName("GML")
        self.logger.debug("OGR Datasource: " + filename)
        ogrdatasource = ogrdriver.Open(filename)
        self.logger.debug("... loaded")

        if ogrdatasource is None:
            #print "ogrdatasource is None"
            QtGui.QMessageBox.critical(self, "Error", "Response is not a valid QGIS-Layer!")
            #self.ui.lblMessage.setText("")

        else:
            # Determine the LayerCount
            #print "ogrdatasource is some"
            ogrlayercount = ogrdatasource.GetLayerCount()
            #print ogrlayercount
            self.logger.debug("OGR LayerCount: " + str(ogrlayercount))

            hasfeatures = False


            # Load every Layer
            for i in range(0, ogrlayercount):
                #print i
                j = ogrlayercount -1 - i # Reverse Order?
                ogrlayer = ogrdatasource.GetLayerByIndex(j)
                #print ogrlayer
                ogrlayername = ogrlayer.GetName()
                #print ogrlayername
                self.logger.debug("OGR LayerName: " + ogrlayername)

                ogrgeometrytype = ogrlayer.GetGeomType()
                #print ogrgeometrytype
                self.logger.debug("OGR GeometryType: " + ogr.GeometryTypeToName(ogrgeometrytype))

                geomtypeids = []

                # Abstract Geometry
                if ogrgeometrytype==0:
                    #print "ogrgeometrytype==0"
                    self.logger.debug("AbstractGeometry-Strategy ...")
                    geomtypeids = ["1", "2", "3", "100"]

                # One GeometryType
                else:
                    #print "ogrgeometrytype!=0"
                    self.logger.debug("DefaultGeometry-Strategy ...")
                    geomtypeids = [str(ogrgeometrytype)]
                    #print geomtypeids


                # Create a Layer for each GeometryType
                for geomtypeid in geomtypeids:
                    #print geomtypeids

                    qgislayername = ogrlayername # + "#" + filename
                    uri = filename + "|layerid=" + str(j)
                    #print "uri: " + uri

                    if len(geomtypeids) > 1:
                        #print "len(geomtypeids) > 1"
                        uri += "|subset=" + self.getsubset(geomtypeid)

                    self.logger.debug("Loading QgsVectorLayer: " + uri)
                    vlayer = QgsVectorLayer(uri, qgislayername, "ogr")
                    vlayer.setProviderEncoding("UTF-8") #Ignore System Encoding --> TODO: Use XML-Header

                    if not vlayer.isValid():
                        print "vlayer not valid"
                        QtGui.QMessageBox.critical(self, "Error", "Response is not a valid QGIS-Layer!")
                        #self.ui.lblMessage.setText("")
                    else:
                        featurecount = vlayer.featureCount()
                        if featurecount > 0:
                            hasfeatures = True
                            #print "hasfeatures = True"
                            QgsMapLayerRegistry.instance().addMapLayers([vlayer])
                            self.logger.debug("... added Layer! QgsFeatureCount: " + str(featurecount))
                            #self.parent.iface.mapCanvas().zoomToFullExtent()


            if hasfeatures == False:
                QtGui.QMessageBox.information(self, "Information", "No Features returned!")

        self.vlayer = vlayer
        print "current layer set"
            #for f in layer.getFeatures():
            #    #print f["dortype"]

    def getsubset(self, geomcode):

        if      geomcode == "1":    return "OGR_GEOMETRY='POINT' OR OGR_GEOMETRY='MultiPoint'"
        elif    geomcode == "2":    return "OGR_GEOMETRY='LineString' OR OGR_GEOMETRY='MultiLineString'"
        elif    geomcode == "3":    return "OGR_GEOMETRY='Polygon' OR OGR_GEOMETRY='MultiPolygon'"
        elif    geomcode == "100":  return "OGR_GEOMETRY='None'"
        else:                       return "OGR_GEOMETRY='Unknown'"

    def addMap(self):
        if self.vlayer:
            QgsMapLayerRegistry.instance().addMapLayers([self.vlayer])
        else:
            self.show_message("Ingen lag tilgjengeligl", "Advarsel", msg_type=QtGui.QMessageBox.Warning)


    def getLayer(slef):
        return self.vlayer



    def show_message(self, msg_text, msg_title=None, msg_info=None, msg_details=None, msg_type=None):
        msg = QtGui.QMessageBox()
        
        msg.setText(self.to_unicode(msg_text))

        if msg_title is not None:
            msg.setWindowTitle(msg_title)

        if msg_info is not None:
            msg.setInformativeText(msg_info)
        
        if msg_details is not None:
            msg.setDetailedText(msg_details)
        
        if msg_type is not None:
            msg.setIcon(msg_type)

        msg.setStandardButtons(QtGui.QMessageBox.Ok)

        #msg.buttonClicked.connect()

        retval = msg.exec_()
        print ("value of pressed message box button:", retval)


    def to_unicode(self, in_string):
        if isinstance(in_string,str):
            out_string = in_string.decode('utf-8')
        elif isinstance(in_string,unicode):
            out_string = in_string
        else:
            raise TypeError('not stringy')
        return out_string

        
# test = wfs_test(iface)
# test.getCapabilities()
# test.getFeature()
#test.addMap()

