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

from qgis.core import QgsDataSourceURI, QgsMapLayerRegistry, QgsVectorLayer
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QPyNullVariant, QDateTime, QThread, pyqtSignal, Qt
from PyQt4.QtGui import QAction, QIcon, QDockWidget, QGridLayout, QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox, QApplication, QHBoxLayout, QVBoxLayout, QAbstractItemView, QListWidgetItem, QAbstractItemView
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from master_dialog import MasterDialog

#from ObjectWindow.ObjectWindow import ObjectWindow
from AllObjectWidget import AllObjectWidget
from tabledialog import TableDialog
from infoWidgetDialog import infoWidgetDialog
from mytable import MyTable
from test_table import Table


class SelectThread(QThread):

    data_downloaded = pyqtSignal(object)

    def __init__(self, infoWidget_label_list, att_info_list):
        QThread.__init__(self, )
        #self.layer = layer
        #self.info_widget = info_widget
        self.infoWidget_label_list = infoWidget_label_list
        self.att_info_list = att_info_list

    def run(self):
        while True:
            layer = iface.activeLayer()
            selection = self.layer.selectedFeatures()
            for feature in selection:
                        for i in range(0, len(infoWidget_label_list)):
                            try:
                                if isinstance(feature[self.att_info_list[i]], (int, float)):
                                    infoWidget_label_list[i].setText((str(feature[self.att_info_list[i]])))
                                else:
                                    infoWidget_label_list[i].setText((feature[self.att_info_list[i]]))
                            except IndexError, e:
                                print str(e)
                            except Exception, e:
                                infoWidget_label_list[i].setText("-")
                                print str(e)


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
        self.uspesifisert = ""
        self.mer = ">" #for combobokser linket til mer eller mindre enn iteratsjoner
        self.mindre = "<"
        self.mer_eller_lik = ">="
        self.mindre_eller_lik = "<="

        #Attributter Inngangbygg
        self.att_bygg = "bygg_funksjon"
        self.att_dor = "dortype"
        self.att_hand = "handlist"

        self.att_avst_hc = "avstand_hc_park"
        self.att_ank_stig = "adko_stig_grad"
        self.att_dortype = "dortype"
        self.att_dorbredde = "inngang_bredde"
        self.att_dorapner = "dorapner"
        self.att_ringeklokke = "ringeklokke"
        self.att_ringeklokke_hoyde = "ringekl_hoyde"
        self.att_terslelhoyde = "terskel_hoyde"
        self.att_kontrast = "kontrast"
        self.att_rampe = "rampe"
        self.att_rmp_stigning = "rampe_stigning"
        self.att_rmp_bredde = "rampe_bredde"
        self.att_hand1 = "hand_hoy_1"
        self.att_hand2 = "hand_hoy_2"
        self.att_info_list = [self.att_avst_hc, self.att_bygg, self.att_ank_stig, self.att_dor, self.att_dorapner, self.att_ringeklokke, self.att_ringeklokke_hoyde, self.att_terslelhoyde, self.att_dorbredde, self.att_kontrast, self.att_rampe]

        #Attributter Tilgjengelighet
        self.att_rulle = "t_rulle_auto"
        self.att_el_rulle = "el_ruelle_auto"
        self.att_syn = "t_syn"

        #Annet
        self.feature_id = {}
        self.canvas = self.iface.mapCanvas()
        self.layer_inngang = None
        

        

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
        self.dlg = MasterDialog()

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
            text=self.tr(u''),
            callback=self.run,
            parent=self.iface.mainWindow())

        #Connect and create source layer
        self.uri = self.connect_database()
        inngangbygg = self.add_layers()

        #fill comboboxes
        self.fill_fylker()
        self.fill_combobox(inngangbygg, "bygg_funksjon", self.dlg.comboBox_byggningstype)
        self.fill_combobox(inngangbygg, "dortype", self.dlg.comboBox_dortype)
        self.fill_combobox(inngangbygg, "handlist", self.dlg.comboBox_handliste)
        self.fill_combobox(inngangbygg, "t_rulle", self.dlg.comboBox_manuell_rullestol)
        self.fill_combobox(inngangbygg, "t_el_rulle_auto", self.dlg.comboBox_el_rullestol)
        self.fill_combobox(inngangbygg, "t_syn", self.dlg.comboBox_syn)
        self.fill_combobox(inngangbygg, "kontrast", self.dlg.comboBox_kontrast)
        self.integer_valg_list = [self.dlg.comboBox_avstand_hc, self.dlg.comboBox_ank_stigning, self.dlg.comboBox_dorbredde, self.dlg.comboBox_rmp_stigning, self.dlg.comboBox_rmp_stigning, self.dlg.comboBox_rmp_bredde, self.dlg.comboBox_hand1, self.dlg.comboBox_hand2, self.dlg.comboBox_terskel]
        for cmbBox in self.integer_valg_list:
            self.fill_combobox_mer_mindre(cmbBox)

        # remove source layer
        QgsMapLayerRegistry.instance().removeMapLayer( inngangbygg.id() )

        #Set push functions
        # filtrer_btn_inngang = self.dlg.pushButton_filtrerInngang
        # filtrer_btn_inngang.clicked.connect(self.filtrer_inngang)

        #Creating dock view of second window
        self.dock = TableDialog()
        self.obdockwidget=QDockWidget("Seartch Results" , self.iface.mainWindow() )
        self.obdockwidget.setObjectName("Results")
        self.obdockwidget.setWidget(self.dock)
        self.dock.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows) #select entire row in table
        self.dock.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers) #Making table unediteble

        self.infoWidget = infoWidgetDialog()
        self.obj_info_dockwidget=QDockWidget("Info" , self.iface.mainWindow() )
        self.obj_info_dockwidget.setObjectName("Object Info")
        self.obj_info_dockwidget.setWidget(self.infoWidget)
        
        self.dlg.accepted.connect(self.filtrer_inngang) #OK fillterer foreløpig for inngang, burde endres
        #self.iface.addDockWidget( Qt.BottomDockWidgetArea , self.obdockwidget )

        #Set push functions
        filtrer_btn_inngang = self.dlg.pushButton_filtrerInngang
        filtrer_btn_inngang.clicked.connect(self.filtrer_inngang)
        self.dock.tableWidget.itemClicked.connect(self.test)
        self.dlg.pushButton_reset.clicked.connect(self.reset)

        #set combobox functions
        fylker_cmb_changed = self.dlg.comboBox_fylker
        fylker_cmb_changed.currentIndexChanged.connect(self.fylke_valgt) #Filling cityes from county
        self.dlg.comboBox_komuner.currentIndexChanged.connect(lambda x: self.dlg.lineEdit_navn_paa_sok_inngang.setText(self.dlg.comboBox_komuner.currentText())) #seting name for search to city chosen

        


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Master'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def add_layers(self):
        layerList = QgsMapLayerRegistry.instance().mapLayersByName("inngangbygg")

        try:
            inngangbygg = layerList[0]
            return inngangbygg
        except IndexError:
            print "inngangbygg not a layer"

    def to_unicode(self, in_string):
        if isinstance(in_string,str):
            out_string = in_string.decode('utf-8')
        elif isinstance(in_string,unicode):
            out_string = in_string
        else:
            raise TypeError('not stringy')
        return out_string


    def connect_database(self):
        uri = QgsDataSourceURI()
        uri.setConnection("localhost","5432","tilgjengelig","postgres","postgres")
        #uri.setConnection("46.101.4.130","5432","webinar","webinar","webinar")
        sql = "(select * from tilgjengelighet.t_inngangbygg)"
        #sql = "(select * from kasper_master.t_inngangbygg)"
        uri.setDataSource("",sql,"wkb_geometry","","ogc_fid")
        vlayer = QgsVectorLayer(uri.uri(),"inngangbygg","postgres")
        QgsMapLayerRegistry.instance().addMapLayer(vlayer)

        return uri


    def test(self):
        #print dir(self.dock.tableWidget.selectionModel().selectedRows().index())
        #self.layer_inngang.setSelectedFeatures([self.feature_id[int(self.dock.tableWidget.item(index.row(), i).text())]])
        infoWidget_label_list = [self.infoWidget.label_avstand_hc_text, self.infoWidget.label_byggningstype_text, self.infoWidget.label_ank_vei_stigning_text, self.infoWidget.label_dortype_text, self.infoWidget.label_dorapner_text, self.infoWidget.label_ringeklokke_text, self.infoWidget.label_ringeklokke_hoyde_text, self.infoWidget.label_terskelhoyde_text, self.infoWidget.label_inngang_bredde_text, self.infoWidget.label_kontrast_text, self.infoWidget.label_rampe_text]
        indexes = self.dock.tableWidget.selectionModel().selectedRows()
        if self.layer_inngang is not None:
            for index in sorted(indexes):
                self.layer_inngang.setSelectedFeatures([self.feature_id[int(self.dock.tableWidget.item(index.row(), 29).text())]])
                selection = self.layer_inngang.selectedFeatures()

                for feature in selection:
                    for i in range(0, len(infoWidget_label_list)):
                        try:
                            if isinstance(feature[self.att_info_list[i]], (int, float)):
                                infoWidget_label_list[i].setText((str(feature[self.att_info_list[i]])))
                            else:
                                infoWidget_label_list[i].setText((feature[self.att_info_list[i]]))
                        except IndexError, e:
                            print str(e)
                        except Exception, e:
                            infoWidget_label_list[i].setText("-")
                            print str(e)


    def fill_combobox(self, layer, feat_name, combobox):
        combobox.clear()
        combobox.addItem(self.uspesifisert)

        for feature in layer.getFeatures(): #Sett inn error catchment her
            try:
                name = feature[feat_name]
            except KeyError:
                print "Layer does not contain given key"
                return

            if not isinstance(name, QPyNullVariant) and combobox.findText(name) < 0:
                combobox.addItem(name)

    def fill_combobox_mer_mindre(self, combobox):
        combobox.clear()
        combobox.addItem(self.mer)
        combobox.addItem(self.mindre)
        combobox.addItem(self.mer_eller_lik)
        combobox.addItem(self.mindre_eller_lik)
        
        

    def showResults(self, layer):
        prov = layer.dataProvider()
        feat = layer.getFeatures()
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
            self.feature_id[f['ogc_fid']] = f.id()
            for i in range(0,len(prov.fields())):
                if isinstance(f[i], QDateTime):
                    if f[i].isNull:
                        self.dock.tableWidget.setItem(current_object,i,QTableWidgetItem("NULL"))
                    else:
                        self.dock.tableWidget.setItem(current_object,i,QTableWidgetItem(f[i].toString('dd.MM.yy')))
                elif hasattr(f[i], 'toString'):
                    self.dock.tableWidget.setItem(current_object,i,QTableWidgetItem(f[i].toString()))
                elif isinstance(f[i], (int, float)):
                    self.dock.tableWidget.setItem(current_object,i,QTableWidgetItem(str(f[i])))
                elif isinstance(f[i], QPyNullVariant):
                    self.dock.tableWidget.setItem(current_object,i,QTableWidgetItem("NULL"))
                else:
                    self.dock.tableWidget.setItem(current_object,i,QTableWidgetItem(f[i]))

            current_object = current_object + 1
        self.dock.tableWidget.setSortingEnabled(True) #enabeling sorting
        self.iface.addDockWidget( Qt.BottomDockWidgetArea , self.obdockwidget ) #adding seartch result Widget


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
            for komune_nr in self.fylke_dict[fylke]:
                self.dlg.comboBox_komuner.addItem(self.komm_dict_nr[komune_nr])
        self.dlg.lineEdit_navn_paa_sok_inngang.setText(fylke)

    # def fill_komuner(self):
    #     self.dlg.comboBox_komuner.clear()
    #     self.dlg.comboBox_komuner.addItem(self.uspesifisert)

    #     #filename = 'C:\Users\kaspa_000\.qgis2\python\plugins\MasterGUI\komm.txt'
    #     filename = self.plugin_dir + "\komm.txt"

    #     self.komm_dict = {}
    #     self.fylke_dict = {}
    #     with io.open(filename,'r',encoding='utf-8') as f:
    #         for line in f:
    #             komm_nr, komune, fylke = line.rstrip('\n').split(("\t"))
    #             komm_nr = self.to_unicode(komm_nr)
    #             komune = self.to_unicode(komune)
    #             fylke = self.to_unicode(fylke)
    #             self.komm_dict[komune] = [komm_nr, fylke]
    #             #self.dlg.comboBox_komuner.addItem(komune)
    #             #print komune
    #             if not fylke in self.fylke_dict:
    #                 self.fylke_dict[fylke] = []
    #                 self.dlg.comboBox_komuner.addItem(fylke)
    #             self.fylke_dict[fylke].append(komm_nr)
    #             self.dlg.comboBox_komuner.addItem("    " + komune)
    #     #print self.fylke_dict

    #     #print komm_nr


    # def fylke_valgt(self):
    #     fylke = self.dlg.comboBox_byggningstype.currentText()
    #     for komune in self.fylke_dict[fylke]:
    #         self.dlg.comboBox_komuner.addItem()
        # print "something"


    def create_where_statement(self, attribute, value, opperator, where):
        if value != self.uspesifisert:
            if len(where) == 0:
                where = "where " + attribute + " " + opperator +" '" + value + "'"
            else: 
                where = where + " and " + attribute + " " + opperator +" '" + value + "'"
        return where



    def filtrer_inngang(self):
        print"Filtering Start"

        fylke = self.dlg.comboBox_fylker.currentText()
        komune = self.dlg.comboBox_komuner.currentText()

        byggningstype = self.dlg.comboBox_byggningstype.currentText()
        dortype = self.dlg.comboBox_dortype.currentText()
        handliste = self.dlg.comboBox_handliste.currentText()
        m_rullestol = self.dlg.comboBox_manuell_rullestol.currentText()
        el_rullestol = self.dlg.comboBox_el_rullestol.currentText()
        syn = self.dlg.comboBox_syn.currentText()

        byggningstype = self.to_unicode(byggningstype)
        #byggningstype = byggningstype.decode('iso-8859-1')
        dortype = self.to_unicode(dortype)
        handliste = self.to_unicode(handliste)
        m_rullestol = self.to_unicode(m_rullestol)
        el_rullestol = self.to_unicode(el_rullestol)
        syn = self.to_unicode(syn)

        ing_atr_combobox = {self.att_bygg : byggningstype, self.att_dor :  dortype, self.att_hand :  handliste, self.att_rulle : m_rullestol, self.att_el_rulle : el_rullestol, self.att_syn : syn}

        avstand_hc = self.dlg.lineEdit_avstand_hc.text()
        ank_stigning = self.dlg.lineEdit_ank_stigning.text()
        dorbredde = self.dlg.lineEdit_dorbredde.text()
        rmp_stigning = self.dlg.lineEdit_rmp_stigning.text()
        rmp_bredde = self.dlg.lineEdit_rmp_bredde.text()
        hand1 = self.dlg.lineEdit_hand1.text()
        hand2 = self.dlg.lineEdit_hand2.text()

        ing_atr_lineedit = {self.att_avst_hc : [avstand_hc, self.dlg.comboBox_avstand_hc.currentText()], self.att_ank_stig : [ank_stigning, self.dlg.comboBox_ank_stigning.currentText()], self.att_dorbredde : [dorbredde, self.dlg.comboBox_dorbredde.currentText()], self.att_rmp_stigning : [rmp_stigning, self.dlg.comboBox_rmp_stigning.currentText()], self.att_rmp_bredde : [rmp_bredde, self.dlg.comboBox_rmp_bredde.currentText()], self.att_hand1 : [hand1, self.dlg.comboBox_hand1.currentText()], self.att_hand2 : [hand2, self.dlg.comboBox_hand2.currentText()]}

        sql = "select * from tilgjengelighet.t_inngangbygg"
        #sql = "select * from kasper_master.t_inngangbygg"
        where = "".decode('utf-8')

        if fylke != "Norge":
            if komune == self.uspesifisert:
                where = "where komm = " + self.fylke_dict[fylke][0]
                for komune_nr in range(1, len(self.fylke_dict[fylke])-1):
                    where = where + " or komm = " + self.fylke_dict[fylke][komune_nr]
            else:
                where = "where komm = " + self.komm_dict_nm[komune]

        # if komune != self.uspesifisert:
        #     if komune[0:4] == "    ": #If a city is chosen, and not a county
        #         where = "where komm = " + self.komm_dict[komune[4:len(komune)]][0] + ""
        #     else: #If a county is chosen
        #         where = "where komm = " + self.fylke_dict[komune][0]
        #         for kommnr in range(1,len(self.fylke_dict[komune])-1): #iterate throu the rest of the cityes in the county
        #             where = where + " or komm = " + self.fylke_dict[komune][kommnr]

        for atr, value in ing_atr_combobox.iteritems():
            where = self.create_where_statement(atr, value, "like", where)
            #print where

        for atr, value in ing_atr_lineedit.iteritems():
            opperator = ">"
            if value[1] == self.mindre:
                opperator = "<"
            where = self.create_where_statement(atr, value[0], opperator, where)

        sql = "(" + sql + " " + where + ")"

        #print sql
        
        self.uri.setDataSource("",sql,"wkb_geometry","","ogc_fid")
        try:
            QgsMapLayerRegistry.instance().removeMapLayer(self.layer_inngang.id())
        except Exception, e:
            print str(e)


        #self.layer_inngang = QgsVectorLayer(self.uri.uri(),"inngangbygg_filtrert","postgres")
        if len(self.dlg.lineEdit_navn_paa_sok_inngang.text()) > 0:
            self.layer_inngang = QgsVectorLayer(self.uri.uri(),self.dlg.lineEdit_navn_paa_sok_inngang.text(),"postgres")
        else:
            self.layer_inngang = QgsVectorLayer(self.uri.uri(),"inngangbygg_filtrert","postgres")
        
        #QgsMapLayerRegistry.instance().removeMapLayer( inngangbygg.id() )
        QgsMapLayerRegistry.instance().addMapLayer(self.layer_inngang)


        if not self.layer_inngang.isValid():
            print "layer failed to load"
            self.show_message("søket ga ingen teff", "Advarsel", msg_type=QMessageBox.Warning)
        else:
            print "layer succeeded to load"
            self.showResults(self.layer_inngang)
            self.iface.addDockWidget( Qt.LeftDockWidgetArea , self.obj_info_dockwidget )


        infoWidget_label_list = [self.infoWidget.label_avstand_hc_text, self.infoWidget.label_byggningstype_text, self.infoWidget.label_ank_vei_stigning_text, self.infoWidget.label_dortype_text, self.infoWidget.label_dorapner_text, self.infoWidget.label_ringeklokke_text, self.infoWidget.label_ringeklokke_hoyde_text, self.infoWidget.label_terskelhoyde_text, self.infoWidget.label_inngang_bredde_text, self.infoWidget.label_kontrast_text, self.infoWidget.label_rampe_text]

        # thread = SelectThread(infoWidget_label_list, self.att_info_list)
        # thread.start()
        print "Filtering End"
        

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
        print ("value of pressed message box button:", retval)


    def reset(self): #unfinished
        comboBoxes = [self.dlg.comboBox_fylker, self.dlg.comboBox_komuner, self.dlg.comboBox_avstand_hc, self.dlg.comboBox_ank_stigning, self.dlg.comboBox_byggningstype, self.dlg.comboBox_rampe, self.dlg.comboBox_dortype, self.dlg.comboBox_dorbredde, self.dlg.comboBox_terskel, self.dlg.comboBox_kontrast, self.dlg.comboBox_rmp_stigning, self.dlg.comboBox_rmp_bredde, self.dlg.comboBox_handliste, self.dlg.comboBox_hand1, self.dlg.comboBox_hand2, self.dlg.comboBox_manuell_rullestol, self.dlg.comboBox_el_rullestol, self.dlg.comboBox_syn]
        for cmb in comboBoxes:
            cmb.setCurrentIndex(0)

        lineEdits = [self.dlg.lineEdit_avstand_hc, self.dlg.lineEdit_ank_stigning, self.dlg.lineEdit_dorbredde, self.dlg.lineEdit_terskel, self.dlg.lineEdit_rmp_stigning, self.dlg.lineEdit_rmp_bredde, self.dlg.lineEdit_hand1, self.dlg.lineEdit_hand2, self.dlg.lineEdit_navn_paa_sok_inngang]
        for le in lineEdits:
            le.setText("")


    def run(self):
        """Run method that performs all the real work"""


        # show the dialog
        self.dlg.show()
        
        # indexes = self.dock.tableWidget.selectionModel().selectedRows()
        # for index in sorted(indexes):
        #     print('Row %d is selected' % index.row())

        #byggningstyper = self.add_byggningstyper(inngangbygg = inngangbygg)
        #fyll ut combobosker
        
        #ow = self.testDock()
        #td = testDock(self.iface)
        #td.show()


        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
