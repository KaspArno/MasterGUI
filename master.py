# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Master
                                 A QGIS plugin
 My master assignment
                              -------------------
        begin                : 2017-08-21
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Kasper Skjeggestad
        email                : kasper.skjeggestad@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import sys
import os.path
import io

from qgis.core import QgsDataSourceURI, QgsMapLayerRegistry, QgsVectorLayer, QgsExpression, QgsFeatureRequest, QgsVectorFileWriter, QgsLayerTreeLayer, QgsLayerTreeGroup, QgsMapLayer, QgsProject
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QPyNullVariant, QDateTime, QThread, pyqtSignal, Qt
from PyQt4.QtGui import QAction, QIcon, QDockWidget, QGridLayout, QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox, QApplication, QHBoxLayout, QVBoxLayout, QAbstractItemView, QListWidgetItem, QAbstractItemView, QFileDialog

# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from master_dialog import MasterDialog

#from ObjectWindow.ObjectWindow import ObjectWindow

from tabledialog import TableDialog
from infoWidgetDialog import infoWidgetDialog


from exportlayerdialog import exportLayerDialog
from GuiAttribute import GuiAttribute

import urllib2
import urllib
from xml.etree import ElementTree
from PyQt4.QtNetwork import QHttp
import random
import os
import tempfile
from PyQt4 import QtCore, QtGui
from osgeo import gdal
from osgeo import ogr
import string
from featuretype import FeatureType
from SavedSearch import SavedSearch

#For selection
from identifyGeometry import IdentifyGeometry

import datetime
import time

from functools import partial



class Master:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Master_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Master')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Master')
        self.toolbar.setObjectName(u'Master')

        #Globale Variabler
        #Combobox filling
        self.uspesifisert = "" #For tomme comboboxser og lineEdtis
        self.mer = ">" #for combobokser linket til mer eller mindre enn iteratsjoner
        self.mindre = "<"
        self.mer_eller_lik = ">="
        self.mindre_eller_lik = "<="

        #layers and search
        self.layers = [] #gather all layers
        self.layername = [] #gather all layer name (dict?)

        self.current_seartch_layer = None #The last searched layer
        self.search_history = {} #history of all search

        #to hide layers
        self.ltv = self.iface.layerTreeView()
        self.model = self.ltv.model()
        self.root = QgsProject.instance().layerTreeRoot()



        #self.layer_inngang = None


        

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Master', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = MasterDialog() #main dialig

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/Master/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'UU Tilgjengelighet'),
            callback=self.run,
            parent=self.iface.mainWindow())


        #main window
        self.dlg.tabWidget_main.currentChanged.connect(self.change_search_name) #change search name based on tab
        self.dlg.tabWidget_friluft.currentChanged.connect(self.change_search_name)
        self.dlg.tabWidget_tettsted.currentChanged.connect(self.change_search_name)

        self.dlg.pushButton_reset.clicked.connect(self.reset) #resett all choses

        #table window
        self.dock = TableDialog(self.iface.mainWindow())
        self.dock.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows) #select entire row in table
        self.dock.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers) #Making table unediteble

        self.dock.tableWidget.itemClicked.connect(self.table_item_clicked) #what happens when an item is clicked in table

        #info window
        self.infoWidget = infoWidgetDialog(self.iface.mainWindow())
        self.infoWidget.pushButton_Select_Object.setCheckable(True)
        self.infoWidget.pushButton_Select_Object.toggled.connect(self.toolButtonSelect)
        self.infoWidget.pushButton_exporter.clicked.connect(self.open_export_layer_dialog)
        self.infoWidget.pushButton_filtrer.clicked.connect(lambda x: self.dlg.show()) #open main window
        self.infoWidget.pushButton_filtre_tidligere.clicked.connect(self.get_previus_search) #open main window with prev search options

        self.sourceMapTool = IdentifyGeometry(self.canvas, self.infoWidget, pickMode='selection')

        #Export window
        self.export_layer = exportLayerDialog()
        self.export_layer.pushButton_bla.clicked.connect(self.OpenBrowse)
        self.export_layer.pushButton_lagre.clicked.connect(self.lagre_lag)
        self.export_layer.pushButton_lagre.clicked.connect(lambda x: self.export_layer.close()) #close winwo when you have saved layer
        self.export_layer.pushButton_avbryt.clicked.connect(lambda x: self.export_layer.close())
        

        #set combobox functions
        self.dlg.comboBox_fylker.currentIndexChanged.connect(self.fylke_valgt) #Filling cityes from county
        self.dlg.comboBox_fylker.currentIndexChanged.connect(self.change_search_name) #setting search name based on fylke
        self.dlg.comboBox_komuner.currentIndexChanged.connect(self.change_search_name) #setting search name based on komune

        self.fylker = GuiAttribute("fylker")
        self.fylker.setComboBox(self.dlg.comboBox_fylker)
        self.kommuner = GuiAttribute("komune")
        self.kommuner.setComboBox(self.dlg.comboBox_komuner)


        #Create attributes object
        self.assign_combobox_inngang()
        self.assign_combobox_vei()
        self.assign_combobox_hc_parkering()
        self.assign_combobox_parkeringsomraade()

        self.dlg.pushButton_filtrer.clicked.connect(self.filtrer)

        

    def assign_combobox_inngang(self):
        
        self.avstandHC = GuiAttribute("avstandHC", self.dlg.comboBox_avstand_hc, self.dlg.lineEdit_avstand_hc)
        self.ank_stigning = GuiAttribute("stigningAdkomstvei", self.dlg.comboBox_ank_stigning, self.dlg.lineEdit_ank_stigning)
        self.byggningstype = GuiAttribute("funksjon", self.dlg.comboBox_byggningstype)
        self.rampe = GuiAttribute("rampe", self.dlg.comboBox_rampe, comboBoxText={"" : "", "Ja" : "1", "Nei" : "0"})
        self.dortype = GuiAttribute(u'd\xf8rtype', self.dlg.comboBox_dortype)
        self.dorapner = GuiAttribute(u'd\xf8r\xe5pner', self.dlg.comboBox_dorapner)
        self.man_hoyde = GuiAttribute(u'man\xe5verknappH\xf8yde', self.dlg.comboBox_man_hoyde, self.dlg.lineEdit_man_hoyde)
        self.dorbredde = GuiAttribute("InngangBredde", self.dlg.comboBox_dorbredde, self.dlg.lineEdit_dorbredde)
        self.terskel = GuiAttribute(u'terskelH\xf8yde', self.dlg.comboBox_terskel, self.dlg.lineEdit_terskel)
        self.kontrast = GuiAttribute("kontrast", self.dlg.comboBox_kontrast)
        self.rampe_stigning = GuiAttribute("rampeStigning", self.dlg.comboBox_rmp_stigning, self.dlg.lineEdit_rmp_stigning)
        self.rampe_bredde = GuiAttribute("rampeBredde", self.dlg.comboBox_rmp_bredde, self.dlg.lineEdit_rmp_bredde)
        self.handlist = GuiAttribute(u'h\xe5ndlist', self.dlg.comboBox_handliste)
        self.handlist1 = GuiAttribute(u'h\xe5ndlistH\xf8yde1', self.dlg.comboBox_hand1, self.dlg.lineEdit_hand1)
        self.handlist2 = GuiAttribute(u'h\xe5ndlistH\xf8yde2', self.dlg.comboBox_hand2, self.dlg.lineEdit_hand2)
        self.rmp_tilgjengelig = GuiAttribute("rampeTilgjengelig", self.dlg.comboBox_rmp_tilgjengelig)
        self.manuellRullestol = GuiAttribute("tilgjengvurderingRullestol", self.dlg.comboBox_manuell_rullestol)
        self.elektriskRullestol = GuiAttribute("tilgjengvurderingElRull", self.dlg.comboBox_el_rullestol)
        self.synshemmet = GuiAttribute("tilgjengvurderingSyn", self.dlg.comboBox_syn)

        self.attributes_inngang = [self.avstandHC, self.ank_stigning, self.byggningstype, self.rampe, self.dortype, self.dorapner, self.man_hoyde, self.dorbredde, self.terskel, self.kontrast, self.rampe_stigning, self.rampe_bredde, self.handlist, self.handlist1, self.handlist2, self.rmp_tilgjengelig, self.manuellRullestol, self.elektriskRullestol, self.synshemmet]
        self.attributes_inngang_gui = [self.byggningstype, self.dortype, self.dorapner, self.kontrast, self.handlist, self.rmp_tilgjengelig, self.manuellRullestol, self.elektriskRullestol, self.synshemmet]
        self.attributes_inngang_mer_mindre = [self.avstandHC, self.ank_stigning, self.man_hoyde, self.dorbredde, self.terskel, self.rampe_stigning, self.rampe_bredde, self.handlist1, self.handlist2]


        #selection test
        #self.sourceMapTool = IdentifyGeometry(self.canvas, self.infoWidget, pickMode='selection')

        #hide gui options test
        self.dlg.label_rampe_boxs.setVisible(False)

        self.dlg.lineEdit_rmp_stigning.setVisible(False)
        self.dlg.comboBox_rmp_stigning.setVisible(False)
        self.dlg.label_rmp_stigning.setVisible(False)

        self.dlg.lineEdit_rmp_bredde.setVisible(False)
        self.dlg.comboBox_rmp_bredde.setVisible(False)
        self.dlg.label_rmp_bredde.setVisible(False)

        self.dlg.comboBox_handliste.setVisible(False)
        self.dlg.label_handliste.setVisible(False)

        self.dlg.lineEdit_hand1.setVisible(False)
        self.dlg.comboBox_hand1.setVisible(False)
        self.dlg.label_hand1.setVisible(False)

        self.dlg.lineEdit_hand2.setVisible(False)
        self.dlg.comboBox_hand2.setVisible(False)
        self.dlg.label_hand2.setVisible(False)

        self.dlg.comboBox_rmp_tilgjengelig.setVisible(False)
        self.dlg.label_rmp_tilgjengelig.setVisible(False)

        self.dlg.line_4.setVisible(False)
        self.dlg.line.setVisible(False)

        self.dlg.comboBox_rampe.currentIndexChanged.connect(self.hide_show_rampe)

    def assign_combobox_vei(self):
        self.gatetype = GuiAttribute("gatetype")
        self.gatetype.setComboBox(self.dlg.comboBox_gatetype)

        self.nedsenkning1 = GuiAttribute("nedsenk1")
        self.nedsenkning1.setComboBox(self.dlg.comboBox_nedsenkning1)
        self.nedsenkning1.setLineEdit(self.dlg.lineEdit_nedsenkning1)

        self.nedsenkning2 = GuiAttribute("nedsenk2")
        self.nedsenkning2.setComboBox(self.dlg.comboBox_nedsenkning2)
        self.nedsenkning2.setLineEdit(self.dlg.lineEdit_nedsenkning2)

        self.dekke_vei_tettsted = GuiAttribute("dekke")
        self.dekke_vei_tettsted.setComboBox(self.dlg.comboBox_dekke_vei_tettsted)

        self.dekkeTilstand_vei_tettsted = GuiAttribute("dekkeTilstand")
        self.dekkeTilstand_vei_tettsted.setComboBox(self.dlg.comboBox_dekkeTilstand_vei_tettsted)

        self.bredde = GuiAttribute("bredde")
        self.bredde.setComboBox(self.dlg.comboBox_bredde)
        self.bredde.setLineEdit(self.dlg.lineEdit_bredde)

        self.stigning = GuiAttribute("stigning")
        self.stigning.setComboBox(self.dlg.comboBox_stigning)
        self.stigning.setLineEdit(self.dlg.lineEdit_stigning)

        self.tverfall = GuiAttribute("tverfall")
        self.tverfall.setComboBox(self.dlg.comboBox_tverfall)
        self.tverfall.setLineEdit(self.dlg.lineEdit_tverfall)

        self.ledelinje = GuiAttribute("ledelinje")
        self.ledelinje.setComboBox(self.dlg.comboBox_ledelinje)
        self.nedsenkning1.setLineEdit(self.dlg.lineEdit_nedsenkning1)

        self.ledelinjeKontrast = GuiAttribute("ledelinjeKontrast")
        self.ledelinjeKontrast.setComboBox(self.dlg.comboBox_ledelinjeKontrast)

        self.manuell_rullestol_vei = GuiAttribute("tilgjengvurderingRullestol")
        self.manuell_rullestol_vei.setComboBox(self.dlg.comboBox_manuell_rullestol_vei)

        self.electrisk_rullestol_vei = GuiAttribute("tilgjengvurderingElRull")
        self.electrisk_rullestol_vei.setComboBox(self.dlg.comboBox_electrisk_rullestol_vei)
        
        self.syn_vei = GuiAttribute("tilgjengvurderingSyn")
        self.syn_vei.setComboBox(self.dlg.comboBox_syn_vei)

        self.attributes_vei = [self.gatetype, self.nedsenkning1, self.nedsenkning2, self.dekke_vei_tettsted, self.dekkeTilstand_vei_tettsted, self.bredde, self.stigning, self.tverfall, self.ledelinje, self.ledelinjeKontrast, self.manuell_rullestol_vei, self.electrisk_rullestol_vei, self.syn_vei]
        self.attributes_vei_gui = [self.gatetype, self.dekke_vei_tettsted, self.dekkeTilstand_vei_tettsted, self.ledelinje, self.ledelinjeKontrast, self.manuell_rullestol_vei, self.electrisk_rullestol_vei, self.syn_vei]
        self.attributes_vei_mer_mindre = [self.nedsenkning1,self.nedsenkning2,self.bredde,self.stigning,self.tverfall]

        self.dlg.comboBox_nedsenkning1.setVisible(False)
        self.dlg.lineEdit_nedsenkning1.setVisible(False)
        self.dlg.label_nedsenkning1.setVisible(False)
        self.dlg.comboBox_nedsenkning2.setVisible(False)
        self.dlg.lineEdit_nedsenkning2.setVisible(False)
        self.dlg.label_nedsenkning2.setVisible(False)

        self.dlg.comboBox_gatetype.currentIndexChanged.connect(self.hide_show_nedsenkning)

    def assign_combobox_hc_parkering(self):
        self.avstandServicebygg = GuiAttribute("avstandServicebygg")
        self.avstandServicebygg.setComboBox(self.dlg.comboBox_avstandServicebygg)
        self.avstandServicebygg.setLineEdit(self.dlg.lineEdit_avstandServicebygg)

        self.overbygg = GuiAttribute("overbygg")
        self.overbygg.setComboBox(self.dlg.comboBox_overbygg)

        self.skiltet = GuiAttribute("skiltet")
        self.skiltet.setComboBox(self.dlg.comboBox_skiltet)

        self.merket = GuiAttribute("merket")
        self.merket.setComboBox(self.dlg.comboBox_merket)

        self.bredde_vei = GuiAttribute("bredde")
        self.bredde_vei.setComboBox(self.dlg.comboBox_bredde_vei)
        self.bredde_vei.setLineEdit(self.dlg.lineEdit_bredde_vei)

        self.lengde_vei = GuiAttribute("lengde")
        self.lengde_vei.setComboBox(self.dlg.comboBox_lengde_vei)
        self.lengde_vei.setLineEdit(self.dlg.lineEdit_lengde_vei)

        self.manuell_rullestol_hcparkering = GuiAttribute("tilgjengvurderingRullestol")
        self.manuell_rullestol_hcparkering.setComboBox(self.dlg.comboBox_manuell_rullestol_hcparkering)

        self.elektrisk_rullestol_hcparkering = GuiAttribute("tilgjengvurderingElRull")
        self.elektrisk_rullestol_hcparkering.setComboBox(self.dlg.comboBox_elektrisk_rullestol_hcparkering)

        #self.syn_hcparkering = GuiAttribute("tilgjengvurderingSyn")
        #self.syn_hcparkering.setComboBox(self.dlg.comboBox_syn_hcparkering)

        self.attributes_hcparkering = [self.avstandServicebygg, self.overbygg, self.skiltet, self.merket, self.bredde_vei, self.lengde_vei, self.manuell_rullestol_hcparkering, self.elektrisk_rullestol_hcparkering]
        self.attributes_hcparkering_gui = [self.manuell_rullestol_hcparkering, self.elektrisk_rullestol_hcparkering]
        self.attributes_hcparkering_mer_mindre = [self.avstandServicebygg, self.bredde_vei, self.lengde_vei]

        self.dlg.label_bredde_vei.setVisible(False)
        self.dlg.comboBox_bredde_vei.setVisible(False)
        self.dlg.lineEdit_bredde_vei.setVisible(False)
        self.dlg.label_lengde_vei.setVisible(False)
        self.dlg.comboBox_lengde_vei.setVisible(False)
        self.dlg.lineEdit_lengde_vei.setVisible(False)

        self.dlg.comboBox_merket.currentIndexChanged.connect(self.hide_show_merket)

    def assign_combobox_parkeringsomraade(self):
        self.overbygg_pomrade = GuiAttribute("overbygg")
        self.overbygg_pomrade.setComboBox(self.dlg.comboBox_overbygg_pomrade)

        self.kapasitetPersonbiler = GuiAttribute("kapasitetPersonbiler")
        self.kapasitetPersonbiler.setComboBox(self.dlg.comboBox_kapasitetPersonbiler)
        self.kapasitetPersonbiler.setLineEdit(self.dlg.lineEdit_kapasitetPersonbiler)

        self.kapasitetUU = GuiAttribute("kapasitetUU")
        self.kapasitetUU.setComboBox(self.dlg.comboBox_kapasitetUU)
        self.kapasitetUU.setLineEdit(self.dlg.lineEdit_kapasitetUU)

        self.dekke_pomrade = GuiAttribute("dekke")
        self.dekke_pomrade.setComboBox(self.dlg.comboBox_dekke_pomrade)

        self.dekkeTilstand_pomrade = GuiAttribute("dekkeTilstand")
        self.dekkeTilstand_pomrade.setComboBox(self.dlg.comboBox_dekkeTilstand_pomrade)

        self.manuell_rullestol_pomrade = GuiAttribute("tilgjengvurderingRullestol")
        self.manuell_rullestol_pomrade.setComboBox(self.dlg.comboBox_manuell_rullestol_pomrade)

        self.attributes_pomrade = [self.overbygg_pomrade, self.kapasitetPersonbiler, self.kapasitetUU, self.dekke_pomrade, self.dekkeTilstand_pomrade, self.manuell_rullestol_pomrade]
        self.attributes_pomrade_gui = [self.dekke_pomrade, self.dekkeTilstand_pomrade, self.manuell_rullestol_pomrade]
        self.attributes_pomrade_mer_mindre = [self.kapasitetPersonbiler, self.kapasitetUU]


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Master'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def get_temppath(self, filename):
        tmpdir = os.path.join(tempfile.gettempdir(),'masterGUI')
        if not os.path.exists(tmpdir):
            os.makedirs(tmpdir)
        tmpfile= os.path.join(tmpdir, filename)
        return tmpfile


    def to_unicode(self, in_string):
        if isinstance(in_string,str):
            out_string = in_string.decode('utf-8')
        elif isinstance(in_string,unicode):
            out_string = in_string
        else:
            raise TypeError('not stringy')
        return out_string


    def updateDataReadProgress(self, bytesRead, totalBytes):
        self.dlg.label_Progress.setText("Laster inn data: " + self.featuretype.getFeatureType())

    def httpRequestStartet(self):
        print("The Request has started!")


    def httpRequestFinished(self, requestId, error):
        print("The Request is finished!")
        #print(requestId, self.httpGetId)
        if requestId != self.httpGetId:
            print("requesrtd Id != httpGetId")
            return
        
        self.outFile.close()
        
        if error:
            print("error in requestFinished")
            print(self.http.errorString())
            print(type(error))
            self.outFile.remove()
        else:
            print("here i am")
            gdaltimeout = "5"
            gdal.SetConfigOption("GDAL_HTTP_TIMEOUT", gdaltimeout)
            gdal.SetConfigOption('GML_SKIP_RESOLVE_ELEMS', 'ALL')
            gdal.SetConfigOption('GML_ATTRIBUTES_TO_OGR_FIELDS', 'NO')
            nasdetectionstring = 'asdf/asdf/asdf'
            gdal.SetConfigOption('NAS_INDICATOR', nasdetectionstring)
            
            ogrdriver = ogr.GetDriverByName("GML")
            ogrdatasource = ogrdriver.Open(self.outFile.fileName())
            
            if ogrdatasource is None:
                print("ogrdatasource is None")
            else: # Determine the LayerCount
                #print("ogrdatasource is some")
                ogrlayercount = ogrdatasource.GetLayerCount()
                for i in range(0, ogrlayercount):
                    j = ogrlayercount -1 - i
                    ogrlayer = ogrdatasource.GetLayerByIndex(j)
                    ogrlayername = ogrlayer.GetName()
                    ogrgeometrytype = ogrlayer.GetGeomType()
                    geomtypeids = []
                    
                    if ogrgeometrytype==0:
                        #print("is it ever abstract geometry?")
                        geomtypeids = ["1", "2", "3", "100"]
                    else:
                        geomtypeids = [str(ogrgeometrytype)]
                        #print(geomtypeids)
                    
                    for geomtypeid in geomtypeids:
                        qgislayername = ogrlayername
                        #print("qgislayername: ", qgislayername)
                        uri = self.outFile.fileName() + "|layerid=" + str(j)
                        if len(geomtypeids) > 1:
                            uri += "|subset=" + self.getsubset(geomtypeid)
                        
                        self.layers.append(QgsVectorLayer(uri, qgislayername, "ogr"))
                        self.layername.append(qgislayername)
                        self.layers[-1].setProviderEncoding("UTF-8")
                        #self.vlayer = QgsVectorLayer(uri, qgislayername, "ogr")
                        #self.layers[qgislayername : self.vlayer]
                        #self.layers[qgislayername].setProviderEncoding("UTF-8")
                        #self.vlayer.setProviderEncoding("UTF-8")
                        
                        #if not self.vlayer.isValid():
                        if not self.layers[-1].isValid():
                            print("self.vlayer not valid")
                        else:
                            #featurecount = self.vlayer.featureCount()
                            featurecount = self.layers[-1].featureCount()
                            if featurecount > 0:
                                #QgsMapLayerRegistry.instance().addMapLayers([self.vlayer])
                                #QgsMapLayerRegistry.instance().addMapLayers([self.layers[-1]])
                                pass
                            #Remove this bit
                            #prov = self.vlayer.dataProvider()
                            prov = self.layers[-1].dataProvider()
                            #for f in self.vlayer.getFeatures():
                            #for f in self.layers[qgislayername].getFeatures():
                            #for f in self.layers[-1].getFeatures():
                                #print("")
                                #for i in range(0, len(prov.fields())):
                                    #print(prov.fields().field(i).name(), ": ", f[i])
                                    #pass
                                #break
                            #Flytt denne bolken til ege metode    
                            #inngangbygg = self.layers[0]
                            #print(self.layers[-1].name())
                            #fill comboboxes
                            #print(self.layers[-1].name())
                            if self.layers[-1].name() == "TettstedInngangBygg":
                                self.fill_fylker()
                                for att in self.attributes_inngang_gui:
                                    self.fill_combobox(self.layers[-1], att.getAttribute(), att.getComboBox())
                                for att in self.attributes_inngang_mer_mindre:
                                    self.fill_combobox_mer_mindre(att.getComboBox())
                            elif self.layers[-1].name() == "TettstedVei":
                                for att in self.attributes_vei_gui:
                                    self.fill_combobox(self.layers[-1], att.getAttribute(), att.getComboBox())
                                for att in self.attributes_vei_mer_mindre:
                                    self.fill_combobox_mer_mindre(att.getComboBox())
                            elif self.layers[-1].name() == "TettstedHCparkering":
                                for att in self.attributes_hcparkering_gui:
                                    self.fill_combobox(self.layers[-1], att.getAttribute(), att.getComboBox())
                                for att in self.attributes_hcparkering_mer_mindre:
                                    self.fill_combobox_mer_mindre(att.getComboBox())
                            elif self.to_unicode(self.layers[-1].name()) == self.to_unicode("TettstedParkeringsomrÃ¥de"):
                                for att in self.attributes_pomrade_gui:
                                    self.fill_combobox(self.layers[-1], att.getAttribute(), att.getComboBox())
                                for att in self.attributes_pomrade_mer_mindre:
                                    self.fill_combobox_mer_mindre(att.getComboBox())

                            self.featuretype.next()
                            if self.featuretype.getFeatureType():
                                self.getFeatures()
                            else:
                                #print("self.layers: ", len(self.layers))
                                #print(dir(self.dlg.label_Progress))
                                #self.dlg.label_Progress_Inngang.setVisible(False)
                                #self.dlg.label_Progress_Vei.setVisible(False)
                                self.dlg.label_Progress.setVisible(False)
                                #print(self.dlg.progressBar.value())
                                for baselayer in self.layers:
                                    QgsMapLayerRegistry.instance().addMapLayer(baselayer)
                                    self.hideLayer(baselayer)
                                    self.iface.legendInterface().setLayerVisible(baselayer, False)

                                print("doen")


    def getFeatures(self):
        namespace = "http://skjema.geonorge.no/SOSI/produktspesifikasjon/TilgjengelighetTettsted/4.5"
        namespace_prefix = "app"
        online_resource = "https://wfs.geonorge.no/skwms1/wfs.tilgjengelighettettsted"

        #typeNames= urllib.quote(feature_type[1].encode('utf8'))
        typeNames= urllib.quote(self.featuretype.getFeatureType().encode('utf8'))
        #print("typeNames", typeNames)
        query_string = "?service=WFS&request=GetFeature&version=2.0.0&srsName={0}&typeNames={1}".format( "urn:ogc:def:crs:EPSG::{0}".format(str(self.iface.mapCanvas().mapRenderer().destinationCrs().postgisSrid())).strip(), typeNames)
        query_string += "&namespaces=xmlns({0},{1})".format(namespace_prefix, urllib.quote(namespace,""))
        #query_string+= "&count={0}".format("1000")
        query_string+= "&"
        #print("query_string: ", query_string)

        self.httpGetId = 0
        #print("httpGatId", self.httpGetId)
        self.http = QHttp()

        self.http.requestStarted.connect(self.httpRequestStartet)
        self.http.requestFinished.connect(self.httpRequestFinished)
        self.http.dataReadProgress.connect(self.updateDataReadProgress)


        layername="wfs{0}".format(''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(6)))
        fileName = self.get_temppath("{0}.gml".format(layername))

        #downloadFile

        url = QtCore.QUrl(online_resource)
        print("online_resource: ", online_resource)
        if QtCore.QFile.exists(fileName):
                    print("File  Exists")
                    QtCore.QFile.remove(fileName)

        self.outFile = QtCore.QFile(fileName)

        port = url.port()
        if port == -1:
            port = 0
        
        self.http.setHost(url.host(), QHttp.ConnectionModeHttps, port) #starting request
        #print("url.path: ", url.path())
        self.httpGetId = self.http.get(url.path() + query_string, self.outFile)
        #print("httpGetId", self.httpGetId)
        

    def toolButtonSelect(self, checked):
        print("toolButtonSelect Activated")
        # If the toolButton is checked
        if checked:
            print("checked")
            self.oldMapTool = self.canvas.mapTool()
            self.canvas.setMapTool(self.sourceMapTool)

        else:
            self.oldMapTool = self.canvas.mapTool()


    def toolButtonAction(self, layer, feature):
        if isinstance(layer, QgsVectorLayer) and isinstance(feature, QgsFeature):
            self.featIdentTool.doWhatEver(feature)


    def hideNode( self, node, bHide=True ):
        if type( node ) in ( QgsLayerTreeLayer, QgsLayerTreeGroup ):
            index = self.model.node2index( node )
            self.ltv.setRowHidden( index.row(), index.parent(), bHide )
            node.setCustomProperty( 'nodeHidden', 'true' if bHide else 'false' )
            self.ltv.setCurrentIndex( self.model.node2index( self.root ) )

    def hideLayer( self, mapLayer ):
        if isinstance( mapLayer, QgsMapLayer ):
            self.hideNode( self.root.findLayer( mapLayer.id() ) )


    def hide_show_rampe(self):
        if self.dlg.comboBox_rampe.currentText() == "Ja":
            self.dlg.label_rampe_boxs.setVisible(True)

            self.dlg.lineEdit_rmp_stigning.setVisible(True)
            self.dlg.comboBox_rmp_stigning.setVisible(True)
            self.dlg.label_rmp_stigning.setVisible(True)

            self.dlg.lineEdit_rmp_bredde.setVisible(True)
            self.dlg.comboBox_rmp_bredde.setVisible(True)
            self.dlg.label_rmp_bredde.setVisible(True)

            self.dlg.comboBox_handliste.setVisible(True)
            self.dlg.label_handliste.setVisible(True)

            self.dlg.lineEdit_hand1.setVisible(True)
            self.dlg.comboBox_hand1.setVisible(True)
            self.dlg.label_hand1.setVisible(True)

            self.dlg.lineEdit_hand2.setVisible(True)
            self.dlg.comboBox_hand2.setVisible(True)
            self.dlg.label_hand2.setVisible(True)

            self.dlg.comboBox_rmp_tilgjengelig.setVisible(True)
            self.dlg.label_rmp_tilgjengelig.setVisible(True)

            self.dlg.line_4.setVisible(True)
            self.dlg.line.setVisible(True)
        else:
            self.dlg.label_rampe_boxs.setVisible(False)

            self.dlg.lineEdit_rmp_stigning.setVisible(False)
            self.dlg.comboBox_rmp_stigning.setVisible(False)
            self.dlg.label_rmp_stigning.setVisible(False)

            self.dlg.lineEdit_rmp_bredde.setVisible(False)
            self.dlg.comboBox_rmp_bredde.setVisible(False)
            self.dlg.label_rmp_bredde.setVisible(False)

            self.dlg.comboBox_handliste.setVisible(False)
            self.dlg.label_handliste.setVisible(False)

            self.dlg.lineEdit_hand1.setVisible(False)
            self.dlg.comboBox_hand1.setVisible(False)
            self.dlg.label_hand1.setVisible(False)

            self.dlg.lineEdit_hand2.setVisible(False)
            self.dlg.comboBox_hand2.setVisible(False)
            self.dlg.label_hand2.setVisible(False)

            self.dlg.comboBox_rmp_tilgjengelig.setVisible(False)
            self.dlg.label_rmp_tilgjengelig.setVisible(False)


            self.dlg.line_4.setVisible(False)
            self.dlg.line.setVisible(False)

    def hide_show_nedsenkning(self):
        if self.dlg.comboBox_gatetype.currentText() != self.uspesifisert:
            self.dlg.comboBox_nedsenkning1.setVisible(True)
            self.dlg.lineEdit_nedsenkning1.setVisible(True)
            self.dlg.label_nedsenkning1.setVisible(True)
            self.dlg.comboBox_nedsenkning2.setVisible(True)
            self.dlg.lineEdit_nedsenkning2.setVisible(True)
            self.dlg.label_nedsenkning2.setVisible(True)
        else:
            self.dlg.comboBox_nedsenkning1.setVisible(False)
            self.dlg.lineEdit_nedsenkning1.setVisible(False)
            self.dlg.label_nedsenkning1.setVisible(False)
            self.dlg.comboBox_nedsenkning2.setVisible(False)
            self.dlg.lineEdit_nedsenkning2.setVisible(False)
            self.dlg.label_nedsenkning2.setVisible(False)

    def hide_show_merket(self):
        if self.dlg.comboBox_merket.currentText() == "Ja":
            self.dlg.label_bredde_vei.setVisible(True)
            self.dlg.comboBox_bredde_vei.setVisible(True)
            self.dlg.lineEdit_bredde_vei.setVisible(True)
            self.dlg.label_lengde_vei.setVisible(True)
            self.dlg.comboBox_lengde_vei.setVisible(True)
            self.dlg.lineEdit_lengde_vei.setVisible(True)
        else:
            self.dlg.label_bredde_vei.setVisible(False)
            self.dlg.comboBox_bredde_vei.setVisible(False)
            self.dlg.lineEdit_bredde_vei.setVisible(False)
            self.dlg.label_lengde_vei.setVisible(False)
            self.dlg.comboBox_lengde_vei.setVisible(False)
            self.dlg.lineEdit_lengde_vei.setVisible(False)


    def get_previus_search(self):
        layer_name = self.infoWidget.comboBox_search_history.currentText()
        if layer_name != "":
            try:
                pre_search = self.search_history[layer_name]
                for key, value in pre_search.attributes.iteritems():
                    key.getComboBox().setCurrentIndex(int(value[0]))
                    if value[1]:
                        key.getLineEdit().setText(value[1])
                self.dlg.tabWidget_main.setCurrentIndex(pre_search.tabIndex_main)
                self.dlg.tabWidget_friluft.setCurrentIndex(pre_search.tabIndex_friluft)
                self.dlg.tabWidget_tettsted.setCurrentIndex(pre_search.tabIndex_tettsted)
                pre_search.lineEdit_seach.setText(pre_search.search_name)
                self.dlg.show()

            except KeyError:
                raise
        else:
            self.dlg.show()



    def table_item_clicked(self):
        print("test called")
        self.current_seartch_layer.setSelectedFeatures([])
        #print(dir(self.dock.tableWidget.selectionModel().selectedRows().index()))
        #self.layer_inngang.setSelectedFeatures([self.feature_id[int(self.dock.tableWidget.item(index.row(), i).text())]])
        #infoWidget_label_list = [self.infoWidget.label_avstand_hc_text, self.infoWidget.label_byggningstype_text, self.infoWidget.label_ank_vei_stigning_text, self.infoWidget.label_dortype_text, self.infoWidget.label_dorapner_text, self.infoWidget.label_ringeklokke_text, self.infoWidget.label_ringeklokke_hoyde_text, self.infoWidget.label_terskelhoyde_text, self.infoWidget.label_inngang_bredde_text, self.infoWidget.label_kontrast_text, self.infoWidget.label_rampe_text]
        indexes = self.dock.tableWidget.selectionModel().selectedRows()
        if self.current_seartch_layer is not None:
            print("Layer is not None")
            for index in sorted(indexes):
                #print("index:", index)
                #print(self.dock.tableWidget.item(index.row(), 29))
                #self.layer_inngang.setSelectedFeatures([self.feature_id[int(self.dock.tableWidget.item(index.row(), 0).text())]])
                self.current_seartch_layer.setSelectedFeatures([self.feature_id[self.dock.tableWidget.item(index.row(), 0).text()]])
                #print("self.feature_id[self.dock.tableWidget.item(index.row(), 0).text()]: ", self.feature_id[self.dock.tableWidget.item(index.row(), 0).text()])
                #print("self.dock.tableWidget.item(index.row(), 0).text(): ", self.dock.tableWidget.item(index.row(), 0).text())
                #self.layer_inngang.setSelectedFeatures([self.feature_id[int(self.dock.tableWidget.item(index.row(), 0).text()[23:len(self.dock.tableWidget.item(index.row(), 0).text())])]])
                selection = self.current_seartch_layer.selectedFeatures()
                #print("self.layer_inngang.selectedFeatures(): ", self.layer_inngang.selectedFeatures())
                #print("selection", selection)
                # for feature in selection:
                #     #print("feature", feature)
                #     for i in range(0, len(infoWidget_label_list)):
                #         #print("i: ", i)
                #         try:
                #             if isinstance(feature[self.to_unicode(self.attributes_inngang[i].getAttribute())], (int, float, long)): #isinstance(feature[self.to_unicode(self.att_info_list[i])], (int, float, long)):
                #                 self.attributes_inngang
                #                 #print("int, float, ling", feature[self.to_unicode(self.att_info_list[i])])
                #                 infoWidget_label_list[i].setText((str(feature[self.to_unicode(self.attributes_inngang[i].getAttribute())])))
                #             elif isinstance(feature[self.to_unicode(self.attributes_inngang[i].getAttribute())], (QPyNullVariant)):
                #                 #print("NULL", feature[self.to_unicode(self.att_info_list[i])])
                #                 infoWidget_label_list[i].setText("-")
                #             else:
                #                 #print("else", feature[self.to_unicode(self.att_info_list[i])])
                #                 infoWidget_label_list[i].setText(feature[self.to_unicode(self.attributes_inngang[i].getAttribute())])
                #         except Exception, e:
                #             #print("Exception", feature[self.to_unicode(self.att_info_list[i])])
                #             infoWidget_label_list[i].setText("-")
                #             #print(str(e))
                #             raise


    def fill_combobox(self, layer, feat_name, combobox):
        combobox.clear()
        combobox.addItem(self.uspesifisert)
        
        feat_name = self.to_unicode(feat_name)
        #print("feat_name: ", feat_name)
        for feature in layer.getFeatures(): #Sett inn error catchment her
            try:
                name = feature[feat_name]
                #print(feat_name, ": ", name)
            except KeyError:
                print("Layer does not contain given key")
                return
            if isinstance(name, int):
                name = str(name)
            if not isinstance(name, QPyNullVariant) and combobox.findText(name) < 0:
                combobox.addItem(name)

    def fill_combobox_mer_mindre(self, combobox):
        combobox.clear()
        combobox.addItem(self.mer)
        combobox.addItem(self.mindre)
        combobox.addItem(self.mer_eller_lik)
        combobox.addItem(self.mindre_eller_lik)
        
        

    def showResults(self, layer):
        #reset table
        self.dock.tableWidget.setRowCount(0)
        self.dock.tableWidget.setColumnCount(0)

        #Create data providers
        prov = layer.dataProvider()
        feat = layer.getFeatures()
        
        #Create colums
        self.nrColumn = len(prov.fields())
        self.dock.tableWidget.setColumnCount(len(prov.fields())) #creating colums

        for i in range(0, len(prov.fields())): #creating header in table         
            self.dock.tableWidget.setHorizontalHeaderItem(i,QTableWidgetItem(prov.fields().field(i).name()))

        # creating rows
        nr_objects  = 0
        for f in feat:
            nr_objects = nr_objects + 1
        self.dock.tableWidget.setRowCount(nr_objects)
        
        # filling table values
        current_object = 0
        self.feature_id = {}
        feat = layer.getFeatures() #resetting iterator
        for f in feat:
            self.feature_id[f['gml_id']] = f.id()
            for i in range(0,len(prov.fields())):
                if isinstance(f[i], QDateTime):
                    if f[i].isNull:
                        self.dock.tableWidget.setItem(current_object,i,QTableWidgetItem("NULL"))
                    else:
                        self.dock.tableWidget.setItem(current_object,i,QTableWidgetItem(f[i].toString('dd.MM.yy')))
                elif hasattr(f[i], 'toString'):
                    self.dock.tableWidget.setItem(current_object,i,QTableWidgetItem(f[i].toString()))
                elif isinstance(f[i], (int, float, long)):
                    self.dock.tableWidget.setItem(current_object,i,QTableWidgetItem(str(f[i])))
                elif isinstance(f[i], QPyNullVariant):
                    self.dock.tableWidget.setItem(current_object,i,QTableWidgetItem("NULL"))
                else:
                    self.dock.tableWidget.setItem(current_object,i,QTableWidgetItem(f[i]))

            current_object = current_object + 1
        self.dock.tableWidget.setSortingEnabled(True) #enabeling sorting
        self.iface.addDockWidget( Qt.BottomDockWidgetArea , self.dock ) #adding seartch result Widget


    def fill_fylker(self):
        self.dlg.comboBox_fylker.clear()
        self.dlg.comboBox_fylker.addItem("Norge")

        filename = self.plugin_dir + "\komm.txt"
        self.komm_dict_nr = {}
        self.komm_dict_nm = {}
        self.fylke_dict = {}

        with io.open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                komm_nr, komune, fylke = line.rstrip('\n').split(("\t"))
                komm_nr = self.to_unicode(komm_nr)
                komune = self.to_unicode(komune)
                fylke = self.to_unicode(fylke)

                self.komm_dict_nr[komm_nr] = komune
                self.komm_dict_nm[komune] = komm_nr
                if not fylke in self.fylke_dict:
                    self.fylke_dict[fylke] = []
                    self.dlg.comboBox_fylker.addItem(fylke)

                self.fylke_dict[fylke].append(komm_nr)


    def fylke_valgt(self):
        fylke = self.dlg.comboBox_fylker.currentText()
        self.dlg.comboBox_komuner.clear()
        self.dlg.comboBox_komuner.addItem(self.uspesifisert)
        if fylke != "Norge":
            try:
                for komune_nr in self.fylke_dict[fylke]:
                    self.dlg.comboBox_komuner.addItem(self.komm_dict_nr[komune_nr])
            except Exception as e:
                print(str(e))

    def komune_valgt(self):
        if self.dlg.comboBox_komuner.currentText() != "":
            self.dlg.lineEdit_navn_paa_sok.setText(self.dlg.lineEdit_navn_paa_sok.text() + ": " + self.dlg.comboBox_komuner.currentText())
        else:
            self.dlg.lineEdit_navn_paa_sok.setText(self.dlg.lineEdit_navn_paa_sok.text() + ": " + self.dlg.comboBox_fylker.currentText())


    def change_search_name(self):
        self.dlg.lineEdit_navn_paa_sok.setText(self.dlg.tabWidget_main.tabText(self.dlg.tabWidget_main.currentIndex()))
        if self.dlg.tabWidget_main.currentIndex() == 0:
            self.dlg.lineEdit_navn_paa_sok.setText(self.dlg.lineEdit_navn_paa_sok.text() + " " + self.dlg.tabWidget_friluft.tabText(self.dlg.tabWidget_friluft.currentIndex()))
        else:
            self.dlg.lineEdit_navn_paa_sok.setText(self.dlg.lineEdit_navn_paa_sok.text() + " " + self.dlg.tabWidget_tettsted.tabText(self.dlg.tabWidget_tettsted.currentIndex()))
        if self.dlg.comboBox_fylker.currentText() != "Norge":
            if self.dlg.comboBox_komuner.currentText() != "":
                self.dlg.lineEdit_navn_paa_sok.setText(self.dlg.lineEdit_navn_paa_sok.text() + ": " + self.dlg.comboBox_komuner.currentText())
            else:
                self.dlg.lineEdit_navn_paa_sok.setText(self.dlg.lineEdit_navn_paa_sok.text() + ": " + self.dlg.comboBox_fylker.currentText())


    def create_expr_statement(self, attribute, expr_string):
        if attribute.getLineEdit() is None:
            if attribute.getComboBoxCurrentText() != self.uspesifisert:
                if len(expr_string) == 0:
                    expr_string = "\"%s\"=\'%s\' " % (attribute.getAttribute(), attribute.getComboBoxCurrentText())
                else:
                    expr_string =  expr_string + " AND " + "\"%s\"=\'%s\' " % (attribute.getAttribute(), attribute.getComboBoxCurrentText())
        else:
            if attribute.getLineEditText() != self.uspesifisert:
                if len(expr_string) == 0:
                    expr_string = "\"%s\"%s\'%s\' " % (attribute.getAttribute(), attribute.getComboBoxCurrentText(), attribute.getLineEditText())
                else:
                    expr_string = expr_string + " AND " + "\"%s\"%s\'%s\' " % (attribute.getAttribute(), attribute.getComboBoxCurrentText(), attribute.getLineEditText())
        return expr_string

    def create_where_statement(self,attribute, where):
        onde_atributter = ["dørtype", "terskelHøyde", "håndlist", "håndlistHøyde1", "håndlistHøyde2"]
        one_att_dict = {"dørtype" : "d_rtype", "terskelHøyde" : "terskelH_yde", "håndlist" : "h_ndlist", "håndlistHøyde1" : "h_ndlistH_yde1", "håndlistHøyde2" : "h_ndlistH_yde2"}
        if attribute.getLineEdit() is None:
            if attribute.getComboBoxCurrentText() != self.uspesifisert:
                if len(where) == 0:
                    where = "WHERE %s = '%s'" % (attribute.getAttribute(), attribute.getComboBoxCurrentText())
                else:
                    where =  where + " AND " + "%s = '%s'" % (attribute.getAttribute(), attribute.getComboBoxCurrentText())
        else:
            if attribute.getLineEditText() != self.uspesifisert:
                if len(where) == 0:
                    where = "WHERE %s %s '%s'" % (attribute.getAttribute(), attribute.getComboBoxCurrentText(), attribute.getLineEditText())
                else:
                    where = where + " AND " +  "%s %s '%s'" % (attribute.getAttribute(), attribute.getComboBoxCurrentText(), attribute.getLineEditText())

        return where

    def create_where_statement2(self,attribute, where):
        onde_atributter = ["dørtype", "terskelHøyde", "håndlist", "håndlistHøyde1", "håndlistHøyde2"]
        one_att_dict = {"dørtype" : "d_rtype", "terskelHøyde" : "terskelH_yde", "håndlist" : "h_ndlist", "håndlistHøyde1" : "h_ndlistH_yde1", "håndlistHøyde2" : "h_ndlistH_yde2"}
        if attribute.getLineEdit() is None:
            if attribute.getComboBoxCurrentText() != self.uspesifisert:
                if len(where) == 0:
                    where = "\"%s\" = '%s'" % (attribute.getAttribute(), attribute.getComboBoxCurrentText())
                else:
                    where =  where + " AND " + "\"%s\" = '%s'" % (attribute.getAttribute(), attribute.getComboBoxCurrentText())
        else:
            if attribute.getLineEditText() != self.uspesifisert:
                if len(where) == 0:
                    where = "\"%s\" %s '%s'" % (attribute.getAttribute(), attribute.getComboBoxCurrentText(), attribute.getLineEditText())
                else:
                    where = where + " AND " +  "\"%s\" %s '%s'" % (attribute.getAttribute(), attribute.getComboBoxCurrentText(), attribute.getLineEditText())

        return where



    def filtrer(self, attributes):
        print("Filtering Start")
    
        sok_metode = self.dlg.comboBox_sok_metode.currentText() #henter hvilke metode som benyttes(virtuelt eller memory)
        layer_name = self.dlg.lineEdit_navn_paa_sok #setter navn på laget
        search_type = self.dlg.tabWidget_tettsted.tabText(self.dlg.tabWidget_tettsted.currentIndex()) #henter hvilke søk som blir gjort (må spesifisere esenere for tettsted eller friluft)
        search_type_pomrade = self.dlg.tabWidget_tettsted.tabText(3) #setter egen for pområde pga problemer med norske bokstaver

        #setter baselayre basert på søketypen
        if search_type == "Vei":
            baselayer = QgsMapLayerRegistry.instance().mapLayersByName('TettstedVei')[0]
            attributes = self.attributes_vei
        elif search_type == "Inngang":
            baselayer = QgsMapLayerRegistry.instance().mapLayersByName('TettstedInngangBygg')[0]
            attributes = self.attributes_inngang
        elif search_type == "HC-Parkering":
            baselayer = QgsMapLayerRegistry.instance().mapLayersByName('TettstedHCparkering')[0]
            attributes = self.attributes_hcparkering
        elif search_type == search_type_pomrade:
            baselayer = QgsMapLayerRegistry.instance().mapLayersByName('TettstedParkeringsomr\xc3\xa5de')[0]
            attributes = self.attributes_pomrade

        fylke = self.dlg.comboBox_fylker.currentText()
        komune = self.dlg.comboBox_komuner.currentText()

        #genererer express string og where spørringer med komuner
        expr_string = ""
        if fylke != "Norge":
            if komune == self.uspesifisert:
                expr_string = expr_string + " (\"kommune\"={0}".format(self.fylke_dict[fylke][0])
                for komune_nr in range(1, len(self.fylke_dict[fylke])-1):
                    expr_string = expr_string + " OR \"kommune\"={0}".format(self.fylke_dict[fylke][komune_nr])
                expr_string = expr_string + ")"
            else:
                expr_string = expr_string + " \"kommune\"={0}".format(self.komm_dict_nm[komune])
        where = "WHERE lokalId > 0"
        if fylke != "Norge":
            if komune == self.uspesifisert:
                where = where + " AND " + "(kommune = '{0}'".format(self.fylke_dict[fylke][0])
                for komune_nr in range(1, len(self.fylke_dict[fylke])-1):
                    where = where + " OR kommune = '{0}'".format(self.fylke_dict[fylke][komune_nr])
                where = where + ")"
            else:
                where = where + " AND " + "kommune = '{0}'".format(self.komm_dict_nm[komune])

        #genererer express string og where spørringer basert på tilstndte attributter
        for attribute in attributes:
            where = self.create_where_statement(attribute, where)
            expr_string = self.create_where_statement2(attribute, expr_string)

        #Genererer lag basert på virtuell metode eller memory metode
        if sok_metode == "virtual":
            
            layer_name_text = layer_name.text() + "Virtual"
            base_layer_name = baselayer.name()
            query = "SELECT * FROM " + base_layer_name + " " + where
            self.current_seartch_layer = QgsVectorLayer("?query=%s" % (query), layer_name_text, "virtual" )

            if self.current_seartch_layer.featureCount() > 0: #Lager lag hvis noen objecter er funnet
                if len(QgsMapLayerRegistry.instance().mapLayersByName(layer_name_text)) > 0:
                    try:
                        QgsMapLayerRegistry.instance().removeMapLayer( QgsMapLayerRegistry.instance().mapLayersByName(layer_name_text)[0].id() ) #Fjerner lag med samme navn, for å ungå duplicates
                    except (RuntimeError, AttributeError) as e:
                        print(str(e))

                QgsMapLayerRegistry.instance().addMapLayer(self.current_seartch_layer) #Legger inn nytt lag
                self.canvas.setExtent(self.current_seartch_layer.extent()) #zoomer inn på nytt lag
                self.iface.addDockWidget( Qt.LeftDockWidgetArea , self.infoWidget ) #legger inn infowidget
                self.showResults(self.current_seartch_layer) #Legger inn tabell
                self.sourceMapTool.setLayer(self.current_seartch_layer) #setter nytt lag til å være mål for verktøy

                self.search_history[layer_name_text] = SavedSearch(layer_name_text, self.current_seartch_layer, layer_name, self.dlg.tabWidget_main.currentIndex(), self.dlg.tabWidget_friluft.currentIndex(), self.dlg.tabWidget_tettsted.currentIndex()) #lagerer søkets tab indes, lagnavn og lag referanse
                for attribute in attributes: #lagrer valg av attributter
                    self.search_history[layer_name_text].add_attribute(attribute, int(attribute.getComboBox().currentIndex()), attribute.getLineEditText())

                self.search_history[layer_name_text].add_attribute(self.fylker, int(self.fylker.getComboBox().currentIndex()), None) #lagerer valg og fylter og komuner
                self.search_history[layer_name_text].add_attribute(self.kommuner, int(self.kommuner.getComboBox().currentIndex()), None)
                if self.infoWidget.comboBox_search_history.findText(layer_name_text) == -1: #Legger til ikke existerende søk i søk historien
                	self.infoWidget.comboBox_search_history.addItem(layer_name_text)
                self.dlg.close() #lukker hovedvindu for enklere se resultater
                
            else:
                self.show_message("Søket fullførte uten at noen objecter ble funnet", "ingen Objecter funnet", msg_info=None, msg_details=None, msg_type=None) #Melding som vises om søket feilet
        
        if sok_metode == "memory": #self.dlg.comboBox_sok_metode.currentText() == "memory":
            try:
                QgsMapLayerRegistry.instance().removeMapLayer( tempLayer )
            except (RuntimeError, AttributeError, UnboundLocalError):
                pass
            if len(expr_string) == 0:
                tempLayer = baselayer
            else:
                print(datetime.datetime.now().time())
                expr = QgsExpression(expr_string)
                print(datetime.datetime.now().time())
                it = baselayer.getFeatures( QgsFeatureRequest( expr ) )
                ids = [i.id() for i in it]
                baselayer.setSelectedFeatures( ids )
                print(datetime.datetime.now().time())
                selectedFeatures = baselayer.selectedFeatures()
                print(datetime.datetime.now().time())
                #selectedFeatures = []
                #WFSlayer = QgsVectorLayer(uri, "layerName", "WFS")
                #features1 = self.layers[-1].selectedFeatures() # this layer is the layer the user or code selects in the map
                print(datetime.datetime.now().time())
                #for WFSfeature in WFSlayer.getFeatures():
                #  for f in features1:
                #    if WFSfeature.geometry().intersects(f.geometry()):
                #      selectedFeatures.append(WFSfeature)
                # create temp layer, eg use LineString geometry
                if search_type == "vei_tettsted":
                    tempLayer = QgsVectorLayer("LineString?crs=epsg:4326", layer_name + "Memory", "memory")
                elif search_type == "parkeringsomrade":
                    tempLayer = QgsVectorLayer("Polygon?crs=epsg:4326", layer_name + "Memory", "memory")
                else:
                    tempLayer = QgsVectorLayer("Point?crs=epsg:4326", layer_name + "Memory", "memory")
                print(datetime.datetime.now().time())
                #QgsMapLayerRegistry.instance().addMapLayer(tempLayer)
                print(datetime.datetime.now().time())
                temp_data = tempLayer.dataProvider()
                print(datetime.datetime.now().time())
                attr = baselayer.dataProvider().fields().toList()
                print(datetime.datetime.now().time())
                temp_data.addAttributes(attr)
                print(datetime.datetime.now().time())
                tempLayer.updateFields()
                print(datetime.datetime.now().time())
                temp_data.addFeatures(selectedFeatures)
                print(datetime.datetime.now().time())
            if tempLayer.featureCount() > 0:
                # try:
                #     QgsMapLayerRegistry.instance().removeMapLayer( self.layer_inngang )
                # except (RuntimeError, AttributeError):
                #     pass
                self.filtering_layer = tempLayer
                QgsMapLayerRegistry.instance().addMapLayer(self.filtering_layer)
                #self.showResults(self.layer_inngang)
                self.canvas.setExtent(self.filtering_layer.extent())
                self.canvas.refresh()
                tempLayer.triggerRepaint()
                self.iface.addDockWidget( Qt.LeftDockWidgetArea , self.infoWidget )
                self.sourceMapTool.setLayer(self.filtering_layer)
                self.showResults(self.filtering_layer) #rampeverdi ikke med i tabell
                self.dock.tabWidget_main.setCurrentIndex(1) #for tettsted
                self.dock.tabWidget_tettsted.setCurrentIndex(1) #for inngangbygg
                self.infoWidget.tabWidget.setCurrentIndex(1)
                self.current_seartch_layer = self.filtering_layer

            else:
                self.show_message("Søket fullførte uten at noen objecter ble funnet", "ingen Objecter funnet", msg_info=None, msg_details=None, msg_type=None)
                QgsMapLayerRegistry.instance().removeMapLayer( tempLayer.id() )
            
        
        print("Filtering End")
        

    def show_message(self, msg_text, msg_title=None, msg_info=None, msg_details=None, msg_type=None):
        msg = QMessageBox()
        
        msg.setText(self.to_unicode(msg_text))

        if msg_title is not None:
            msg.setWindowTitle(msg_title)

        if msg_info is not None:
            msg.setInformativeText(msg_info)
        
        if msg_details is not None:
            msg.setDetailedText(msg_details)
        
        if msg_type is not None:
            msg.setIcon(msg_type)

        msg.setStandardButtons(QMessageBox.Ok)

        #msg.buttonClicked.connect()

        retval = msg.exec_()
        print(("value of pressed message box button:", retval))


    def open_export_layer_dialog(self):
        self.export_layer.show()

    def OpenBrowse(self):        
        filename1 = QFileDialog.getSaveFileName()
        self.export_layer.lineEdit.setText(filename1)

    def lagre_lag(self):
        QgsVectorFileWriter.writeAsVectorFormat(self.iface.activeLayer(), self.export_layer.lineEdit.text(), "utf-8", None, self.export_layer.comboBox.currentText())


    def reset(self): #unfinished
        comboBoxes = [self.dlg.comboBox_fylker, self.dlg.comboBox_komuner, self.dlg.comboBox_avstand_hc, self.dlg.comboBox_ank_stigning, self.dlg.comboBox_byggningstype, self.dlg.comboBox_rampe, self.dlg.comboBox_dortype, self.dlg.comboBox_dorbredde, self.dlg.comboBox_terskel, self.dlg.comboBox_kontrast, self.dlg.comboBox_rmp_stigning, self.dlg.comboBox_rmp_bredde, self.dlg.comboBox_handliste, self.dlg.comboBox_hand1, self.dlg.comboBox_hand2, self.dlg.comboBox_manuell_rullestol, self.dlg.comboBox_el_rullestol, self.dlg.comboBox_syn]
        for cmb in comboBoxes:
            cmb.setCurrentIndex(0)

        lineEdits = [self.dlg.lineEdit_avstand_hc, self.dlg.lineEdit_ank_stigning, self.dlg.lineEdit_dorbredde, self.dlg.lineEdit_terskel, self.dlg.lineEdit_rmp_stigning, self.dlg.lineEdit_rmp_bredde, self.dlg.lineEdit_hand1, self.dlg.lineEdit_hand2, self.dlg.lineEdit_navn_paa_sok]
        for le in lineEdits:
            le.setText("")

  



    def run(self):
        """Run method that performs all the real work"""


        # show the dialog
        self.dlg.show()
        self.featuretype = FeatureType()
        if self.featuretype:
            self.getFeatures()
        

        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
