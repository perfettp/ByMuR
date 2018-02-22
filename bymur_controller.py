#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
  Bymur Software computes Risk and Multi-Risk associated to Natural Hazards.
  In particular this tool aims to provide a final working application for
  the city of Naples, considering three natural phenomena, i.e earthquakes,
  volcanic eruptions and tsunamis.
  The tool is the final product of BYMUR, an Italian project funded by the
  Italian Ministry of Education (MIUR) in the frame of 2008 FIRB, Futuro in
  Ricerca funding program.

  Copyright(C) 2012-2015 Paolo Perfetti, Roberto Tonini and Jacopo Selva

  This file is part of BYMUR software.

  BYMUR is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  BYMUR is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with BYMUR. If not, see <http://www.gnu.org/licenses/>.

"""


import os
import bymur_functions as bf


class BymurController(object):
    """BymurController is in charge of application logic.
    Update both the core and the graphical interface to reflect the current
    application state and exchange data.
    """

    _exception_debug = False
    _basedir = os.getcwd()
    _dbDetails = dict(db_host='localhost', db_port='3306',
                      db_user='bymurTEST', db_password='bymurTEST',
                      db_name='bymurTEST')

    _addDBDataDetails = dict()

    _createDBDetails = dict(db_host='localhost', db_port='3306',
                            db_user='bymurTEST', db_password='bymurTEST',
                            db_name='bymurTEST')

    def __init__(self, core):
        """
        Initialize BymurController object

        :param core: bymur_core.BymurCore
        :raise: Exception
        """
        self._ctrls_data = dict()
        self._wxframe = None
        self._wxapp = None
        if core is None:
            raise Exception("core cannot be None")
        self._core = core
        self._hazard_options = dict()

    def connect_db(self):
        """ Connect ByMur to a database containing data."""

        if self._core.db:
            msg = "Close connected database?"
            confirmation = bf.showMessage(parent=self.get_gui(),
                                          message=msg,
                                          kind="BYMUR_CONFIRM",
                                          caption="Please confirm this action")
            if confirmation:
                self.close_db()
            else:
                return

        dialogResult = self._wxframe.showModalDlg("BymurDBLoadDlg",
                                             **self._dbDetails)
        if dialogResult:
            self._dbDetails.update(dialogResult)
            try:
                bf.SpawnThread(self.get_gui(),
                               bf.wxBYMUR_DB_CONNECTED,
                               self._core.load_db,
                               self._dbDetails,
                               callback=self._set_ctrls_data,
                               wait_msg="Loading database...")
            except Exception as e:
                bf.showMessage(parent=self.get_gui(),
                               debug=self._exception_debug,
                               message=str(e),
                               kind="BYMUR_ERROR",
                               caption="Error")


    def create_db(self):
        """Create a new ByMuR database."""

        if self._core.db:
            msg = "Close connected database?"
            confirmation = bf.showMessage(parent=self.get_gui(),
                                          message=msg,
                                          kind="BYMUR_CONFIRM",
                                          caption="Please confirm this action")
            if confirmation:
                self.close_db()
            else:
                return
        dialogResult = self._wxframe.showModalDlg("BymurDBCreateDlg",
                                             **self._createDBDetails)
        if dialogResult:
            self._createDBDetails.update(dialogResult)
            self.get_gui().busymsg = "Creating DB..."
            self.get_gui().busy = True
            try:
                bf.SpawnThread(self.get_gui(),
                               bf.wxBYMUR_DB_CONNECTED,
                               self._core.create_db,
                               self._createDBDetails,
                               self._set_ctrls_data,
                               wait_msg="Creating database...")
            except Exception as e:
                bf.showMessage(parent=self.get_gui(),
                               message=str(e),
                               debug=self._exception_debug,
                               kind="BYMUR_ERROR",
                               caption="Error")

    def close_db(self):
        """Close current database connection."""

        self._core.close_db()
        self._ctrls_data = dict()
        self._hazard_options = dict()
        bf.fire_event(self.get_gui(), bf.wxBYMUR_DB_CLOSED)

    def quit(self):
        """Close connections, windows  and quit."""

        print "Close"
        self._core.close_db()
        self.get_gui().Close()

    def load_grid(self):
        """Load new grid into currently open ByMuR database."""

        print "loadGrid"
        gridData = dict(basedir=self._basedir, filepath='')
        dialogResult = self._wxframe.showModalDlg("BymurLoadGridDlg", **gridData)
        if dialogResult:
            gridData.update(dialogResult)
            try:
                bf.SpawnThread(self.get_gui(),
                               bf.wxBYMUR_UPDATE_DIALOG,
                               self._core.load_grid,
                               gridData,
                               self._set_ctrls_data,
                               wait_msg="Adding grid to database...")
            except Exception as e:
                bf.showMessage(parent=self.get_gui(),
                               message=str(e),
                               debug=self._exception_debug,
                               kind="BYMUR_ERROR",
                               caption="Error")


    def add_data(self):
        """Add new data to currently open ByMuR database."""

        print "addDBData"
        print "_addDBDetails %s" % self._addDBDataDetails
        _localDBDataDetails = self._addDBDataDetails.copy()
        _localDBDataDetails['grid_list'] = [d['datagrid_name']
                                               for d in
                                               self._core.db.get_datagrids_list()]
        _localDBDataDetails['phenomena_list'] = [p['phenomenon_name'] for p
                                                    in
                                                    self._core.db.get_phenomena_list()]
        dialogResult = self._wxframe.showModalDlg("BymurAddDBDataDlg",
                                                       **_localDBDataDetails)
        if dialogResult:
            _localDBDataDetails.update(dialogResult)
            try:
                bf.SpawnThread(self.get_gui(),
                               bf.wxBYMUR_UPDATE_DIALOG,
                               self._core.add_data,
                               _localDBDataDetails,
                               self._set_ctrls_data,
                               wait_msg="Adding data to database...")
            except Exception as e:
                bf.showMessage(parent=self.get_gui(),
                               message=str(e),
                               debug=self._exception_debug,
                               kind="BYMUR_ERROR",
                               caption="Error")


    def drop_tables(self):
        """ Drop all tables from currently open ByMur database."""

        print "dropDBTables"
        if self._core.db:
            msg = "Are you really sure you want to delete all tables in the " \
                  "database?"
            confirmation = bf.showMessage(parent=self.get_gui(),
                                          message=msg,
                                          kind="BYMUR_CONFIRM",
                                          caption="Please confirm this action")
            if confirmation:
                try:
                    bf.SpawnThread(self.get_gui(),
                                   bf.wxBYMUR_DB_CLOSED,
                                   self._core.drop_tables,
                                   dict(),
                                   self.close_db,
                                   wait_msg="Dropping tables...")
                except Exception as e:
                    bf.showMessage(parent=self.get_gui(),
                                   message=str(e),
                                   debug=self._exception_debug,
                                   kind="BYMUR_ERROR",
                                   caption="Error")
            else:
                return

    def create_ensemble(self):
        """Define a new ensemble model combining available hazard models."""

        print "openEnsemble"
        dialogResult = self._wxframe.showModalDlg("BymurEnsembleDlg",
                                             **{'data': self._core.ctrls_data})
        if dialogResult:
            try:
                dialogResult['ensIMLThresh'] = [float(thresh) for thresh in
                                        dialogResult['ensIMLThresh'].split()]
                bf.SpawnThread(self.get_gui(),
                               bf.wxBYMUR_UPDATE_DIALOG,
                               self._core.defEnsembleHaz,
                               dialogResult,
                               self._set_ctrls_data,
                               wait_msg="Creating ensemble hazard...")
                # self._core.defEnsembleHaz(**dialogResult)
            except Exception as e:
                bf.showMessage(parent=self.get_gui(),
                               message=str(e),
                               debug=self._exception_debug,
                               kind="BYMUR_ERROR",
                               caption="Ensemble hazard definition")

            finally:
                self.get_gui().busy = False

    def compare_risks_act(self, ev):
        risks = self._core.get_risks(self._core.hazard_options['exp_time'])
        dialogResult, dialogStrings = self._wxframe.selectRisksDlg(
            self._core.risk, self._core.compare_risks, risks)
        if dialogResult >= 0:
            self._core.set_cmp_risks(dialogStrings,
                                     self._core.hazard_options['exp_time'])
            areaID_list=[a['areaID'] for a in self._core.selected_areas]
            bf.SpawnThread(self.get_gui(),
                           bf.wxBYMUR_UPDATE_MAP,
                           self._core.set_areas_by_ID,
                           dict(areaID_list=areaID_list),
                           callback=self._update_areas_data,
                           wait_msg="Loading data..."
            )


    def export_hazard(self):
        """Export hazard model to XMLs file"""

        print "export Hazard"
        dialogResult = self._wxframe.showModalDlg("BymurExportHazDlg",
                                             **{'data': self._core.ctrls_data})
        if dialogResult:
            try:
                bf.SpawnThread(self.get_gui(),
                               bf.wxBYMUR_UPDATE_DIALOG,
                               self._core.exportHaz,
                               dialogResult,
                               self._set_ctrls_data,
                               wait_msg="Exporting hazard XMLs...")
            except Exception as e:
                bf.showMessage(parent=self.get_gui(),
                               message=str(e),
                               debug=self._exception_debug,
                               kind="BYMUR_ERROR",
                               caption="Export XML files")

            finally:
                self.get_gui().busy = False

    def update_hazard_options(self, event):
        """Update hazard options from parameters from GUI.

        :param event: wx.Event
        """

        try:
            data = self.get_gui().ctrlsPanel.hazard_options
            print "Setting hazard_options data: %s" % data
            if (data['ret_per'] is None) or (data['int_thresh'] is None) or \
                    (data['hazard_name'] is None) or (data['exp_time'] is None):
                raise StandardError("Hazard options are not complete")
            tmp = dict()
            tmp['hazard_name'] = data['hazard_name']
            tmp['risk_model_name'] = data['risk_model_name']
            tmp['ret_per'] = float(data['ret_per'])
            tmp['int_thresh'] = float(data['int_thresh'])
            tmp['exp_time'] = float(data['exp_time'])
            self._hazard_options = tmp
            bf.SpawnThread(self.get_gui(),
                           bf.wxBYMUR_UPDATE_ALL,
                           self._core.updateModel,
                           self._hazard_options,
                           callback=self._update_hazard_data,
                           wait_msg="Updating maps...")
        except Exception as e:
            bf.showMessage(parent=self.get_gui(),
                           debug=self._exception_debug,
                           message="Error setting hazard_options!\n" + str(e),
                           kind="BYMUR_ERROR",
                           caption="Error")

    def exportASCII(self):
        self.get_gui().saveFile(self._basedir, self._core.exportRawPoints)

    def showPoints(self):
        print "showPoints"

    def nbTabChanged(self, event):
        self.get_gui().rightPanel.curvesPanel.updateView()

    def get_areas_data(self, index, areas=[]):
        if self._core.set_point_by_index(index):
            bf.SpawnThread(self.get_gui(),
                           bf.wxBYMUR_UPDATE_POINT,
                           self.areas_selection,
                           dict(areas=areas),
                           wait_msg="Loading data..."
            )


    def areas_selection(self, areas=[]):
        # if self._core.set_point_by_index(index):
        self._core.set_areas_by_list(areas)
        self._set_selected_point()
        self._set_selected_areas()
            # bf.fire_event(self.get_gui(), bf.wxBYMUR_UPDATE_POINT)

    def pick_point_by_index(self, index, pathID=None):
        """
        Select by index a point of which plot data in curve graph.

        :param index: bigint
        """

        if pathID is not None:
            self._core.set_areas_by_ID([pathID+1])
            self._set_selected_areas()
        if self._core.set_point_by_index(index):
            self._set_selected_point()
            bf.fire_event(self.get_gui(), bf.wxBYMUR_UPDATE_POINT)


    def pick_point_by_coordinates(self, easting, northing):
        """
        Select point by coordinates of which plot data in curve graph .

        :param easting: bigint
        :param northing: bigint
        """

        if self._core.set_point_by_coordinates(easting, northing):
            self._set_selected_point()
            bf.fire_event(self.get_gui(), bf.wxBYMUR_UPDATE_POINT)

    def set_gui(self, frame):
        """
        Set main GUI window element.

        :type frame: bymur.BymurWxView
        """
        
        print "Setting frame"
        self._wxframe = frame

    def get_gui(self):
        """
        Get main GUI window element.

        :return wx.Frame
        """

        return self._wxframe

    @property
    def basedir(self):
        return self._basedir

    def _update_hazard_data(self):
        self._set_hazard()
        self._set_hazard_data()
        self._set_hazard_options()
        self._set_selected_point()
        self._set_inventory()
        self._set_fragility()
        self._set_loss()
        self._set_risk()
        self._set_compare_risks()
        # self._set_selected_area()
        self._set_selected_areas()

    def _update_areas_data(self):
        self._set_compare_risks()
        self._set_selected_areas()

    def _set_ctrls_data(self):
        self.get_gui().ctrls_data = self._core.ctrls_data

    def _set_hazard(self):
        self.get_gui().hazard = self._core.hazard

    def _set_hazard_options(self):
        self.get_gui().hazard_options = self._core.hazard_options

    def _set_hazard_data(self):
        self.get_gui().hazard_data = self._core.hazard_data

    def _set_selected_point(self):
        self.get_gui().selected_point = self._core.selected_point

    def _set_inventory(self):
        self.get_gui().inventory = self._core.inventory
        
    def _set_fragility(self):
        self.get_gui().fragility = self._core.fragility
        
    def _set_loss(self):
        self.get_gui().loss = self._core.loss

    def _set_risk(self):
        self.get_gui().risk = self._core.risk

    # def _set_inventory_sections(self):
    #     print "Set inventory_sections"
    #     self.get_gui().inventory_sections = self._core.inventory_sections

    # def _set_selected_area(self):
    #     self.get_gui().selected_area = self._core.selected_area

    def _set_selected_areas(self):
        self.get_gui().selected_areas = self._core.selected_areas
        
    def _set_compare_risks(self):
        print "set_compare_risks"
        print self._core.compare_risks
        self.get_gui().compare_risks = self._core.compare_risks
        print self.get_gui().compare_risks
