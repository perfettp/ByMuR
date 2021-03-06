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

  Copyright(C) 2012-2016, 2018 Paolo Perfetti, Roberto Tonini and Jacopo Selva

  This file is part of BYMUR software.

  BYMUR is free software: you can redistribute it and/or modify it under the 
  terms of the GNU Affero General Public License as published by the 
  Free Software Foundation, either version 3 of the License, or (at your 
  option) any later version.

  BYMUR is distributed in the hope that it will be useful, but WITHOUT ANY 
  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS 
  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for 
  more details.

  You should have received a copy of the GNU Affero General Public License
  along with BYMUR. If not, see <http://www.gnu.org/licenses/>.

"""


import wx
from wx.lib.agw.flatnotebook import FNB_NO_NAV_BUTTONS, FNB_NO_X_BUTTON
import bymur_plots
import os
import bymur_core
import bymur_controller
import bymur_functions as bf
import wx.lib.agw.flatnotebook as FlatNB
import sys
import argparse


class BymurBusyDlg(wx.BusyInfo):
    """
    """

    def __init__(self, *args, **kwargs):
        super(BymurBusyDlg, self).__init__(*args, **kwargs)


class BymurStaticBoxSizer(wx.StaticBoxSizer):
    def __init__(self, *args, **kwargs):
        self._parent = kwargs.pop('parent', None)
        self._label = kwargs.pop('label', "")
        self._box = wx.StaticBox(self._parent, label=self._label)
        super(BymurStaticBoxSizer, self).__init__(self._box,
                                                  *args,
                                                  **kwargs)


class BymurDBBoxSizer(BymurStaticBoxSizer):
    _textSize = (300, -1)

    def __init__(self, *args, **kwargs):
        self._dbDetails = {'db_host': kwargs.pop('db_host', ''),
                           'db_port': kwargs.pop('db_port', ''),
                           'db_user': kwargs.pop('db_user', ''),
                           'db_password': kwargs.pop('db_password', ''),
                           'db_name': kwargs.pop('db_name', '')
        }
        super(BymurDBBoxSizer, self).__init__(*args, **kwargs)

        self._dbSizer = wx.GridBagSizer(hgap=5, vgap=5)
        self.Add(self._dbSizer)

        row = 0
        self._dbHost = wx.StaticText(self._parent, wx.ID_ANY,
                                     'Server hostname: ')
        self._dbSizer.Add(self._dbHost, pos=(row, 0))
        self._dbHostText = wx.TextCtrl(self._parent, wx.ID_ANY,
                                       size=self._textSize)
        self._dbHostText.SetValue(self._dbDetails['db_host'])
        self._dbSizer.Add(self._dbHostText, pos=(row, 1))
        row += 1
        self._dbPort = wx.StaticText(self._parent, wx.ID_ANY, 'Server Port: ')
        self._dbSizer.Add(self._dbPort, pos=(row, 0))
        self._dbPortText = wx.TextCtrl(self._parent, wx.ID_ANY,
                                       size=self._textSize)
        self._dbPortText.SetValue(self._dbDetails['db_port'])
        self._dbSizer.Add(self._dbPortText, pos=(row, 1))
        row += 1
        self._dbUser = wx.StaticText(self._parent, wx.ID_ANY, 'User: ')
        self._dbSizer.Add(self._dbUser, pos=(row, 0))
        self._dbUserText = wx.TextCtrl(self._parent, wx.ID_ANY,
                                       size=self._textSize)
        self._dbUserText.SetValue(self._dbDetails['db_user'])
        self._dbSizer.Add(self._dbUserText, pos=(row, 1))
        row += 1
        self._dbPassword = wx.StaticText(self._parent, wx.ID_ANY, 'Password: ')
        self._dbSizer.Add(self._dbPassword, pos=(row, 0))
        self._dbPasswordText = wx.TextCtrl(self._parent, wx.ID_ANY,
                                           size=self._textSize,
                                           style=wx.TE_PASSWORD)
        self._dbPasswordText.SetValue(self._dbDetails['db_password'])
        self._dbSizer.Add(self._dbPasswordText, pos=(row, 1))
        row += 1
        self._dbName = wx.StaticText(self._parent, wx.ID_ANY, 'Database name: ')
        self._dbSizer.Add(self._dbName, pos=(row, 0))
        self._dbNameText = wx.TextCtrl(self._parent, wx.ID_ANY,
                                       size=self._textSize)
        self._dbNameText.SetValue(self._dbDetails['db_name'])
        self._dbSizer.Add(self._dbNameText, pos=(row, 1))

    @property
    def dbHost(self):
        return self._dbHostText.GetValue()

    @property
    def dbPort(self):
        return self._dbPortText.GetValue()

    @property
    def dbUser(self):
        return self._dbUserText.GetValue()

    @property
    def dbPassword(self):
        return self._dbPasswordText.GetValue()

    @property
    def dbName(self):
        return self._dbNameText.GetValue()


class BymurLoadGridBoxSizer(BymurStaticBoxSizer):
    _gridText = "Load a 2-column ascii file having easting\n" \
               "(1st col) and northing (2nd col) of each spatial\n" \
               "point."

    def __init__(self, *args, **kwargs):
        self._basedir = kwargs.pop('basedir', '')
        self._filepath = kwargs.pop('filepath', '')

        super(BymurLoadGridBoxSizer, self).__init__(*args, **kwargs)

        self._gridBoxGrid = wx.GridBagSizer(hgap=5, vgap=5)
        self.Add(self._gridBoxGrid)
        self._gridBoxGrid.Add(wx.StaticText(self._parent, id=wx.ID_ANY,
                                           style=wx.EXPAND,
                                           label=self._gridText),
                             flag=wx.EXPAND, pos=(0, 0), span=(1, 6))
        self._gridFileText = wx.TextCtrl(self._parent, wx.ID_ANY)
        self._gridBoxGrid.Add(self._gridFileText, flag=wx.EXPAND,
                             pos=(1, 0), span=(1, 5))
        self._gridFileText.SetValue(self._basedir)
        self._gridFileButton = wx.Button(self._parent, id=wx.ID_ANY,
                                        label="Select File")
        self._gridFileButton.Bind(event=wx.EVT_BUTTON, handler=self.selGridFile)
        self._gridBoxGrid.Add(self._gridFileButton, flag=wx.EXPAND,
                             pos=(1, 5), span=(1, 1))

    def selGridFile(self, event):
        dir = os.path.dirname(self._gridFileText.GetValue())
        if (not os.path.isdir(dir)):
            dir = self._basedir
        dlg = wx.FileDialog(self._parent, message="Upload File", defaultDir=dir,
                            defaultFile="", wildcard="*.*",
                            style=wx.FD_OPEN | wx.FD_CHANGE_DIR)

        if (dlg.ShowModal() == wx.ID_OK):
            self._gridFileText.SetValue(dlg.GetPath())
        dlg.Destroy()

    @property
    def gridPath(self):
        return self._gridFileText.GetValue()
    
    
class BymurSelectGridBoxSizer(BymurStaticBoxSizer):
    _gridText = "Select a grid from database:"

    def __init__(self, *args, **kwargs):
        self.grid_list= kwargs.pop('grid_list', [])

        super(BymurSelectGridBoxSizer, self).__init__(*args, **kwargs)

        self._gridBoxGrid = wx.GridBagSizer(hgap=5, vgap=5)
        self.Add(self._gridBoxGrid)
        self._gridBoxGrid.Add(wx.StaticText(self._parent, id=wx.ID_ANY,
                                           style=wx.EXPAND,
                                           label=self._gridText),
                             flag=wx.EXPAND, pos=(0, 0), span=(1, 6))
        self._gridCB = wx.ComboBox(self._parent, wx.ID_ANY)
        self._gridCB.AppendItems(self.grid_list)

        self._gridBoxGrid.Add(self._gridCB, flag=wx.EXPAND,
                             pos=(1, 0), span=(1, 6))

    @property
    def gridName(self):
       return self._gridCB.GetValue()

class BymurEnsBoxSizer(BymurStaticBoxSizer):
    _hazText = "Chose among the list of possible hazard models \n" \
               "here below the ones you would like to use to \n" \
               "calculate the ensable hazard."

    _intText = "Choose time interval"

    _haz_array = []
    _haz_dict = {}

    def __init__(self, *args, **kwargs):
        self.ctrls_data = kwargs.pop('data', {})
        # print self.ctrls_data
        self._available_haz_list = []
        super(BymurEnsBoxSizer, self).__init__(*args, **kwargs)
        self._ensBoxGrid = wx.GridBagSizer(hgap=5, vgap=5)
        self.Add(self._ensBoxGrid)
        self._hazLabel = wx.StaticText(self._parent, id=wx.ID_ANY,
                                       style=wx.EXPAND,
                                       label=self._hazText)
        grid_row = 0
        self._ensBoxGrid.Add(self._hazLabel, flag=wx.EXPAND,
                             pos=(grid_row, 0), span=(2, 6))

        grid_row += 3
        self._ensPhenLabel = wx.StaticText(self._parent, id=wx.ID_ANY,
                                           style=wx.EXPAND,
                                           label="Choose phenomena")
        self._ensBoxGrid.Add(self._ensPhenLabel, flag=wx.EXPAND,
                             pos=(grid_row, 0), span=(1, 2))
        self._ensPhenCB = wx.ComboBox(self._parent,wx.ID_ANY,
                                      style=wx.CB_READONLY)
        self._ensPhenCB.AppendItems(list(set([haz['phenomenon_name']
                                              for haz in
                                              self.ctrls_data['hazard_models']])))
        self._ensPhenCB.Enable(True)
        self._ensPhenCB.Bind(wx.EVT_COMBOBOX, self.updateEnsemble)
        self._ensBoxGrid.Add(self._ensPhenCB, flag=wx.EXPAND,
                             pos=(grid_row, 2), span=(1, 4))


        grid_row += 1
        self._ensGridLabel = wx.StaticText(self._parent, id=wx.ID_ANY,
                                           style=wx.EXPAND,
                                           label="Choose grid")
        self._ensBoxGrid.Add(self._ensGridLabel, flag=wx.EXPAND,
                             pos=(grid_row, 0), span=(1, 2))
        self._ensGridCB = wx.ComboBox(self._parent,wx.ID_ANY,
                                      style=wx.CB_READONLY)
        self._ensGridCB.Enable(False)
        self._ensGridCB.Bind(wx.EVT_COMBOBOX, self.updateEnsemble)
        self._ensBoxGrid.Add(self._ensGridCB, flag=wx.EXPAND,
                             pos=(grid_row, 2), span=(1, 4))

        grid_row += 1
        self._ensExpTimeLabel = wx.StaticText(self._parent, id=wx.ID_ANY,
                                           style=wx.EXPAND,
                                           label="Choose exposure time")
        self._ensBoxGrid.Add(self._ensExpTimeLabel, flag=wx.EXPAND,
                             pos=(grid_row, 0), span=(1, 2))
        self._ensExpTimeCB = wx.ComboBox(self._parent,wx.ID_ANY,
                                      style=wx.CB_READONLY)
        self._ensExpTimeCB.Enable(False)
        self._ensExpTimeCB.Bind(wx.EVT_COMBOBOX, self.updateEnsemble)
        self._ensBoxGrid.Add(self._ensExpTimeCB, flag=wx.EXPAND,
                             pos=(grid_row, 2), span=(1, 4))


        self._ensHaz = []
        for i in range(1, 5):
            grid_row += 1
            hazEntry = {}
            hazEntry['checkbox'] = wx.CheckBox(self._parent,  wx.ID_ANY)
            hazEntry['checkbox'].Bind(wx.EVT_CHECKBOX, self.checkItem)
            self._ensBoxGrid.Add(hazEntry['checkbox'], flag=wx.EXPAND,
                                 pos=(grid_row, 0), span=(1, 1))
            hazEntry['combobox'] = wx.ComboBox(self._parent,wx.ID_ANY,
                                               style=wx.CB_READONLY)
            hazEntry['combobox'].Enable(False)
            hazEntry['combobox'].Bind(wx.EVT_COMBOBOX, self.updateEnsemble)
            self._ensBoxGrid.Add(hazEntry['combobox'], flag=wx.EXPAND,
                             pos=(grid_row, 1), span=(1, 4))
            hazEntry['textctrl'] = wx.TextCtrl(self._parent, wx.ID_ANY,
                                               style=wx.TE_PROCESS_ENTER)
            hazEntry['textctrl'].Enable(False)
            self._ensBoxGrid.Add(hazEntry['textctrl'], flag=wx.EXPAND,
                             pos=(grid_row, 5), span=(1, 1))
            self._ensHaz.append(hazEntry)

        grid_row += 1
        self._ensIMLThreshLabel = wx.StaticText(self._parent, id=wx.ID_ANY,
                                           style=wx.EXPAND,
                                           label="Choose thresholds list")
        self._ensBoxGrid.Add(self._ensIMLThreshLabel, flag=wx.EXPAND,
                             pos=(grid_row, 0), span=(1, 2))
        self._ensIMLThreshCB = wx.ComboBox(self._parent,wx.ID_ANY,
                                      style=wx.CB_READONLY)
        self._ensIMLThreshCBDefaults = ['Choose thresholds list...']
        self._ensIMLThreshCB.SetItems(self._ensIMLThreshCBDefaults)
        self._ensIMLThreshCB.SetSelection(0)
        self._ensIMLThreshCB.Enable(False)
        self._ensIMLThreshCB.Bind(wx.EVT_COMBOBOX, self.updateEnsemble)
        self._ensBoxGrid.Add(self._ensIMLThreshCB, flag=wx.EXPAND,
                             pos=(grid_row, 2), span=(1, 4))

        grid_row += 1
        self._ensNameLabel = wx.StaticText(self._parent, id=wx.ID_ANY,
                                           style=wx.EXPAND,
                                           label="Choose ensemble "
                                                 "hazard name")
        self._ensBoxGrid.Add(self._ensNameLabel, flag=wx.EXPAND,
                             pos=(grid_row, 0), span=(1, 3))
        self._ensNameText = wx.TextCtrl(self._parent, wx.ID_ANY,
                                  style=wx.TE_PROCESS_ENTER)
        self._ensBoxGrid.Add(self._ensNameText, flag=wx.EXPAND,
                             pos=(grid_row, 3), span=(1, 3))

    def updateEnsemble(self, ev=None):
        if (ev is None):  # First data load
            pass
        elif ev.GetEventType() == wx.wxEVT_COMMAND_COMBOBOX_SELECTED:
            _phen_name = self._ensPhenCB.GetStringSelection()
            _exptime_sel = self._ensExpTimeCB.GetValue()
            _grid_sel = self._ensGridCB.GetValue()
            if ev.GetEventObject() == self._ensPhenCB:
                _glist = [haz for haz in  self.ctrls_data['hazard_models']
                          if haz['phenomenon_name'] == _phen_name]
                self._ensGridCB.Clear()
                self._ensGridCB.SetValue('')
                self._ensGridCB.AppendItems(list(set([haz['grid_name']
                                          for haz in _glist])))
                self._ensGridCB.Enable(True)
                if len(self._ensGridCB.Items) > 0:
                    self._ensGridCB.SetSelection(0)
                _grid_sel = self._ensGridCB.GetValue()
                _exptimelist = [str(haz['exposure_time']) for haz in
                                    self.ctrls_data['hazard_models']
                                    if (haz['phenomenon_name'] == _phen_name and
                                haz['grid_name'] == _grid_sel)]

                self._ensExpTimeCB.Clear()
                self._ensExpTimeCB.SetValue('')
                self._ensExpTimeCB.AppendItems(list(set(_exptimelist)))
                if len(self._ensExpTimeCB.Items) > 0:
                    self._ensExpTimeCB.SetSelection(0)
                self._ensExpTimeCB.Enable(True)
            elif ev.GetEventObject() == self._ensGridCB:
                _exptimelist = [str(haz['exposure_time']) for haz in
                                    self.ctrls_data['hazard_models']
                                    if (haz['phenomenon_name'] == _phen_name and
                                haz['grid_name'] == _grid_sel)]

                self._ensExpTimeCB.Clear()
                self._ensExpTimeCB.SetValue('')
                self._ensExpTimeCB.AppendItems(list(set(_exptimelist)))
                if len(self._ensExpTimeCB.Items) > 0:
                    self._ensExpTimeCB.SetSelection(0)
                self._ensExpTimeCB.Enable(True)
            elif ev.GetEventObject() == self._ensExpTimeCB:
                pass
            _phen_name = self._ensPhenCB.GetStringSelection()
            _exptime_sel = self._ensExpTimeCB.GetValue()
            _grid_sel = self._ensGridCB.GetValue()
            self._available_haz_list = [haz['hazard_name'] for haz in
                                self.ctrls_data['hazard_models']
                                if (haz['phenomenon_name'] == _phen_name
                                    and haz['grid_name'] == _grid_sel
                                    and haz['exposure_time'] ==_exptime_sel)]
            for ensHaz in self._ensHaz:
                if (ensHaz['combobox'].GetStringSelection()
                    not in self._available_haz_list) :
                    ensHaz['combobox'].Clear()
                    ensHaz['combobox'].SetValue('')
                    ensHaz['combobox'].Enable(False)
                    ensHaz['checkbox'].SetValue(False)
                    ensHaz['textctrl'].SetValue('')
                    ensHaz['textctrl'].Enable(False)
                ensHaz['combobox'].AppendItems(self._available_haz_list)

            self._update_thresh_list(_phen_name, _grid_sel, _exptime_sel)


    def checkItem(self, event):
        _phen_name = self._ensPhenCB.GetStringSelection()
        _exptime_sel = self._ensExpTimeCB.GetValue()
        _grid_sel = self._ensGridCB.GetValue()
        for hazEntry in self._ensHaz:
            if hazEntry['checkbox'].GetId() == event.GetId():
                if event.IsChecked():
                    hazEntry['combobox'].Enable(True)
                    hazEntry['textctrl'].Enable(True)
                    hazEntry['textctrl'].SetValue('1.0')
                else:
                    hazEntry['combobox'].Enable(False)
                    hazEntry['combobox'].SetSelection(0)
                    hazEntry['textctrl'].Enable(False)
                    hazEntry['textctrl'].SetValue('')
        self._update_thresh_list(_phen_name, _grid_sel, _exptime_sel)

    def _update_thresh_list(self, phen_name, grid_sel, exptime_sel):
        self._available_thresh_list = list(set([haz['iml'] for haz in
                        self.ctrls_data['hazard_models']
                            if ( haz['hazard_name'] in
                                [ensHaz['combobox'].GetStringSelection()
                                 for ensHaz in self._ensHaz
                                if ensHaz['combobox'].IsEnabled()]
                                and haz['phenomenon_name'] == phen_name
                                and haz['grid_name'] == grid_sel
                                and haz['exposure_time'] == exptime_sel)]))

        _iml_sel = self._ensIMLThreshCB.GetStringSelection()
        self._ensIMLThreshCB.SetItems(self._ensIMLThreshCBDefaults)
        self._ensIMLThreshCB.AppendItems(self._available_thresh_list)
        if _iml_sel in self._available_thresh_list:
            self._ensIMLThreshCB.SetStringSelection(_iml_sel)
        else:
            self._ensIMLThreshCB.SetSelection(0)
        self._ensIMLThreshCB.Enable(True)

    @property
    def ensPhen(self):
        return self._ensPhenCB.GetStringSelection()

    @property
    def ensGrid(self):
        return self._ensGridCB.GetValue()

    @property
    def ensExpTime(self):
        return self._ensExpTimeCB.GetValue()

    @property
    def ensHaz(self):
        res = []
        for hazEntry in self._ensHaz:
            if hazEntry['checkbox'].IsChecked():
                haz_tmp = {'hazard_name':
                               hazEntry['combobox'].GetStringSelection(),
                           'weight': float(hazEntry['textctrl'].GetValue())}
                res.append(haz_tmp)
                # for haz in self.ctrls_data['hazard_models']:
                #     if haz['hazard_name'] == hazEntry[
                #         'combobox'].GetStringSelection():

        return res

    @property
    def ensIMLThresh(self):
        if self._ensIMLThreshCB.GetSelection() > 0:
            return self._ensIMLThreshCB.GetStringSelection()
        else:
            return None

    @property
    def ensName(self):
        return self._ensNameText.GetValue()


class BymurExpHazBoxSizer(BymurStaticBoxSizer):

    def __init__(self, *args, **kwargs):
        self.ctrls_data = kwargs.pop('data', {})
        # print self.ctrls_data
        self._available_haz_list = []
        super(BymurExpHazBoxSizer, self).__init__(*args, **kwargs)
        self._expHazGrid = wx.GridBagSizer(hgap=5, vgap=5)
        self.Add(self._expHazGrid)
    
        grid_row = 0
        self._expHazPhenLabel = wx.StaticText(self._parent, id=wx.ID_ANY,
                                           style=wx.EXPAND,
                                           label="Choose phenomena")
        self._expHazGrid.Add(self._expHazPhenLabel, flag=wx.EXPAND,
                             pos=(grid_row, 0), span=(1, 2))
        self._expHazPhenCB = wx.ComboBox(self._parent,wx.ID_ANY,
                                      style=wx.CB_READONLY)
        self._expHazPhenCB.AppendItems(list(set([haz['phenomenon_name']
                                              for haz in
                                              self.ctrls_data['hazard_models']])))
        self._expHazPhenCB.Enable(True)
        self._expHazPhenCB.Bind(wx.EVT_COMBOBOX, self.update)
        self._expHazGrid.Add(self._expHazPhenCB, flag=wx.EXPAND,
                             pos=(grid_row, 2), span=(1, 4))


        grid_row += 1
        self._expHazGridLabel = wx.StaticText(self._parent, id=wx.ID_ANY,
                                           style=wx.EXPAND,
                                           label="Choose grid")
        self._expHazGrid.Add(self._expHazGridLabel, flag=wx.EXPAND,
                             pos=(grid_row, 0), span=(1, 2))
        self._expHazGridCB = wx.ComboBox(self._parent,wx.ID_ANY,
                                      style=wx.CB_READONLY)
        self._expHazGridCB.Enable(False)
        self._expHazGridCB.Bind(wx.EVT_COMBOBOX, self.update)
        self._expHazGrid.Add(self._expHazGridCB, flag=wx.EXPAND,
                             pos=(grid_row, 2), span=(1, 4))

        grid_row += 1
        self._expHazExpTimeLabel = wx.StaticText(self._parent, id=wx.ID_ANY,
                                           style=wx.EXPAND,
                                           label="Choose exposure time")
        self._expHazGrid.Add(self._expHazExpTimeLabel, flag=wx.EXPAND,
                             pos=(grid_row, 0), span=(1, 2))
        self._expHazExpTimeCB = wx.ComboBox(self._parent,wx.ID_ANY,
                                      style=wx.CB_READONLY)
        self._expHazExpTimeCB.Enable(False)
        self._expHazExpTimeCB.Bind(wx.EVT_COMBOBOX, self.update)
        self._expHazGrid.Add(self._expHazExpTimeCB, flag=wx.EXPAND,
                             pos=(grid_row, 2), span=(1, 4))

        grid_row += 1
        self._expHazModelLabel = wx.StaticText(self._parent, id=wx.ID_ANY,
                                           style=wx.EXPAND,
                                           label="Choose hazard model")
        self._expHazGrid.Add(self._expHazModelLabel, flag=wx.EXPAND,
                             pos=(grid_row, 0), span=(1, 2))
        self._expHazModelCB = wx.ComboBox(self._parent,wx.ID_ANY,
                                               style=wx.CB_READONLY)
        self._expHazModelCB.Enable(False)
        # self._expHazModelCB.Bind(wx.EVT_COMBOBOX, self.update)
        self._expHazGrid.Add(self._expHazModelCB, flag=wx.EXPAND,
                             pos=(grid_row, 2), span=(1, 4))

        grid_row += 1
        self._expHazDirButton = wx.Button(self._parent, id=wx.ID_ANY,
                                       style=wx.EXPAND,
                                       label="Select directory to save to")
        self._expHazDirButton.Bind(event=wx.EVT_BUTTON,
                                   handler=self.selExpHazDir)
        self._expHazGrid.Add(self._expHazDirButton, flag=wx.EXPAND,
                             pos=(grid_row, 0), span=(1, 2))
        self._expHazDirTC = wx.TextCtrl(self._parent, id=wx.ID_ANY,
                                       style=wx.EXPAND|wx.TE_READONLY)
        self._expHazGrid.Add(self._expHazDirTC, flag=wx.EXPAND,
                             pos=(grid_row, 2), span=(1, 4))

    def update(self, ev=None):
        if (ev is None):  # First data load
            pass
        elif ev.GetEventType() == wx.wxEVT_COMMAND_COMBOBOX_SELECTED:
            _phen_name = self._expHazPhenCB.GetStringSelection()
            _exptime_sel = self._expHazExpTimeCB.GetValue()
            _grid_sel = self._expHazGridCB.GetValue()
            if ev.GetEventObject() == self._expHazPhenCB:
                _glist = [haz for haz in  self.ctrls_data['hazard_models']
                          if haz['phenomenon_name'] == _phen_name]
                self._expHazGridCB.Clear()
                self._expHazGridCB.SetValue('')
                self._expHazGridCB.AppendItems(list(set([haz['grid_name']
                                          for haz in _glist])))
                self._expHazGridCB.Enable(True)
                if len(self._expHazGridCB.Items) > 0:
                    self._expHazGridCB.SetSelection(0)
                _grid_sel = self._expHazGridCB.GetValue()
                _exptimelist = [str(haz['exposure_time']) for haz in
                                    self.ctrls_data['hazard_models']
                                    if (haz['phenomenon_name'] == _phen_name and
                                haz['grid_name'] == _grid_sel)]

                self._expHazExpTimeCB.Clear()
                self._expHazExpTimeCB.SetValue('')
                self._expHazExpTimeCB.AppendItems(list(set(_exptimelist)))
                if len(self._expHazExpTimeCB.Items) > 0:
                    self._expHazExpTimeCB.SetSelection(0)
                self._expHazExpTimeCB.Enable(True)
            elif ev.GetEventObject() == self._expHazGridCB:
                _exptimelist = [str(haz['exposure_time']) for haz in
                                    self.ctrls_data['hazard_models']
                                    if (haz['phenomenon_name'] == _phen_name and
                                haz['grid_name'] == _grid_sel)]

                self._expHazExpTimeCB.Clear()
                self._expHazExpTimeCB.SetValue('')
                self._expHazExpTimeCB.AppendItems(list(set(_exptimelist)))
                if len(self._expHazExpTimeCB.Items) > 0:
                    self._expHazExpTimeCB.SetSelection(0)
                self._expHazExpTimeCB.Enable(True)
            elif ev.GetEventObject() == self._expHazExpTimeCB:
                pass
            _phen_name = self._expHazPhenCB.GetStringSelection()
            _exptime_sel = self._expHazExpTimeCB.GetValue()
            _grid_sel = self._expHazGridCB.GetValue()
            self._available_haz_list = [haz['hazard_name'] for haz in
                                self.ctrls_data['hazard_models']
                                if (haz['phenomenon_name'] == _phen_name
                                    and haz['grid_name'] == _grid_sel
                                    and haz['exposure_time'] ==_exptime_sel)]

            self._expHazModelCB.Clear()
            self._expHazModelCB.SetValue('')
            self._expHazModelCB.Enable(True)
            self._expHazModelCB.AppendItems(self._available_haz_list)

    def selExpHazDir(self, event):
        dir = os.path.expanduser("~")

        dlg = wx.DirDialog(self._parent, "Select a directory:", defaultPath=dir,
                           style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            self._rootdir = dlg.GetPath()
            self._expHazDirTC.SetValue(self._rootdir)
        dlg.Destroy()

    @property
    def expHazPhen(self):
        return self._expHazPhenCB.GetStringSelection()

    @property
    def expHazGrid(self):
        return self._expHazGridCB.GetValue()

    @property
    def expHazExpTime(self):
        return self._expHazExpTimeCB.GetValue()

    @property
    def expHazModel(self):
        return self._expHazModelCB.GetStringSelection()

    @property
    def expHazExpDir(self):
        return self._expHazDirTC.GetValue()

class BymurMapBoxSizer(BymurStaticBoxSizer):
    def __init__(self, *args, **kwargs):
        self._latMin = kwargs.pop('northing_min', '')
        self._latMax = kwargs.pop('northing_max', '')
        self._lonMin = kwargs.pop('easting_min', '')
        self._lonMax = kwargs.pop('easting_max', '')
        self._mapPath = kwargs.pop('map_path', '')
        super(BymurMapBoxSizer, self).__init__(*args, **kwargs)

        self._mapBoxGrid = wx.GridBagSizer(hgap=5, vgap=5)
        self.Add(self._mapBoxGrid)

        self._mapLatMinLabel = wx.StaticText(self._parent, id=wx.ID_ANY,
                                             style=wx.EXPAND,
                                             label="Latitude Min (m)")
        self._mapLatMinText = wx.TextCtrl(self._parent, wx.ID_ANY)
        self._mapLatMinText.SetValue(str(self._latMin))
        self._mapBoxGrid.Add(self._mapLatMinLabel, flag=wx.EXPAND,
                             pos=(0, 0), span=(1, 4))
        self._mapBoxGrid.Add(self._mapLatMinText, flag=wx.EXPAND,
                             pos=(0, 4), span=(1, 1))

        self._mapLatMaxLabel = wx.StaticText(self._parent, id=wx.ID_ANY,
                                             style=wx.EXPAND,
                                             label="Latitude Max (m)")
        self._mapLatMaxText = wx.TextCtrl(self._parent, wx.ID_ANY)
        self._mapLatMaxText.SetValue(str(self._latMax))
        self._mapBoxGrid.Add(self._mapLatMaxLabel, flag=wx.EXPAND,
                             pos=(1, 0), span=(1, 4))
        self._mapBoxGrid.Add(self._mapLatMaxText, flag=wx.EXPAND,
                             pos=(1, 4), span=(1, 1))

        self._mapLonMinLabel = wx.StaticText(self._parent, id=wx.ID_ANY,
                                             style=wx.EXPAND,
                                             label="Longitude Min (m)")
        self._mapLonMinText = wx.TextCtrl(self._parent, wx.ID_ANY)
        self._mapLonMinText.SetValue(str(self._lonMin))
        self._mapBoxGrid.Add(self._mapLonMinLabel, flag=wx.EXPAND,
                             pos=(2, 0), span=(1, 4))
        self._mapBoxGrid.Add(self._mapLonMinText, flag=wx.EXPAND,
                             pos=(2, 4), span=(1, 1))

        self._mapLonMaxLabel = wx.StaticText(self._parent, id=wx.ID_ANY,
                                             style=wx.EXPAND,
                                             label="Longitude Max (m)")
        self._mapLonMaxText = wx.TextCtrl(self._parent, wx.ID_ANY)
        self._mapLonMaxText.SetValue(str(self._lonMax))
        self._mapBoxGrid.Add(self._mapLonMaxLabel, flag=wx.EXPAND,
                             pos=(3, 0), span=(1, 4))
        self._mapBoxGrid.Add(self._mapLonMaxText, flag=wx.EXPAND,
                             pos=(3, 4), span=(1, 1))

        self._mapButton = wx.Button(self._parent, id=wx.ID_ANY,
                                    label="Upload map")
        self._mapButton.Bind(event=wx.EVT_BUTTON, handler=self.selMap)
        self._mapBoxGrid.Add(self._mapButton, flag=wx.EXPAND,
                             pos=(0, 5), span=(4, 1))

    def selMap(self, event):
        dir = os.getcwd()
        if (not os.path.isdir(dir)):
            dir = os.path.expanduser("~")
        dlg = wx.FileDialog(self._parent, message="Upload Map", defaultDir=dir,
                            defaultFile="", wildcard="*.png", style=wx.OPEN)
        if (dlg.ShowModal() == wx.ID_OK):
            self._mapPath = str(dlg.GetPath())

            if (self._mapPath):
                ext = self._mapPath[-3:]

                if (ext != "png"):
                    msg = ("ERROR:\nYou can upload .png file "
                           "format only.")
                    bf.showMessage(parent=self._parent,
                                   kind="BYMUR_ERROR", caption="Error!",
                                   message="You can upload .png file format only")
                    dlg.Destroy()
                    return
                print "Map uploaded"
            else:
                bf.showMessage(parent=self._parent, kind="BYMUR_ERROR",
                               caption="Error!",
                               message="Image path is wrong.")
        dlg.Destroy()

    @property
    def latMin(self):
        return int(self._mapLatMinText.GetValue())

    @property
    def latMax(self):
        return int(self._mapLatMaxText.GetValue())

    @property
    def lonMin(self):
        return int(self._mapLonMinText.GetValue())

    @property
    def lonMax(self):
        return int(self._mapLonMaxText.GetValue())

    @property
    def mapPath(self):
        return self._mapPath


class BymurHazBoxSizer(BymurStaticBoxSizer):
    _hazRecLabel = "Add all xml files recursively"
    _phenText = "Select phenomenon: "

    def __init__(self, *args, **kwargs):
        self._hazPath = kwargs.pop('haz_path', '')
        self.phenomena_list = kwargs.pop('phenomena_list', '')
        super(BymurHazBoxSizer, self).__init__(*args, **kwargs)

        self._hazBoxGrid = wx.GridBagSizer(hgap=5, vgap=5)
        self.Add(self._hazBoxGrid)
        self._hazDirButton = wx.Button(self._parent, id=wx.ID_ANY,
                                       style=wx.EXPAND,
                                       label="Select directory to scan")
        vpos = 0
        self._hazDirButton.Bind(event=wx.EVT_BUTTON, handler=self.selHazPath)
        self._hazBoxGrid.Add(self._hazDirButton, flag=wx.EXPAND,
                             pos=(vpos, 0), span=(1,6))

        vpos += 1
        self._hazDirLabel = wx.StaticText(self._parent, id=wx.ID_ANY,
                                       style=wx.EXPAND, label = "Root dir")
        self._hazBoxGrid.Add(self._hazDirLabel, flag=wx.EXPAND, pos=(vpos, 0),
                             span=(1, 1))
        self._hazDirTC = wx.TextCtrl(self._parent, id=wx.ID_ANY,
                                       style=wx.EXPAND|wx.TE_READONLY)
        self._hazBoxGrid.Add(self._hazDirTC, flag=wx.EXPAND, pos=(vpos, 1),
                             span=(1, 5))

        vpos += 1
        self._hazFilesAllCB = wx.CheckBox(self._parent, id=wx.ID_ANY,
                                            style=wx.EXPAND, label="Select "
                                                                   "all files")
        self._hazFilesAllCB.Bind(wx.EVT_CHECKBOX, self._select_all)
        self._hazBoxGrid.Add(self._hazFilesAllCB, flag=wx.EXPAND,
                             pos=(vpos, 0), span=(1, 6))
        self._hazFilesCLB = wx.CheckListBox(self._parent, id=wx.ID_ANY,
                                            style=wx.EXPAND)

        vpos += 1
        self._hazBoxGrid.Add(self._hazFilesCLB, flag=wx.EXPAND,
                             pos=(vpos, 0), span=(7, 6))

        # vpos += 7
        # self._hazBoxGrid.Add(wx.StaticText(self._parent, id=wx.ID_ANY,
        #                                    style=wx.EXPAND,
        #                                    label=self._phenText),
        #                      flag=wx.EXPAND, pos=(vpos, 0), span=(1, 6))
        # vpos += 1
        # self._phenCB = wx.ComboBox(self._parent, wx.ID_ANY)
        # self._phenCB.AppendItems(self.phenomena_list)
        # self._hazBoxGrid.Add(self._phenCB, flag=wx.EXPAND,
        #                      pos=(vpos, 0), span=(1, 6))



    def _select_all(self, ev):
        if self._hazFilesAllCB.IsChecked():
            self._hazFilesCLB.SetChecked(range(len(self._hazFilesCLB.GetItems())))
        else:
            for i in range(len(self._hazFilesCLB.GetItems())):
                self._hazFilesCLB.Check(i, check=False)

    def _list_header(self, list):
        list.SetFirstItemStr("Select all files")
        list.SetItemBackgroundColour(1, wx.RED)
        f = list.GetFont()
        f.SetWeight(wx.BOLD)
        list.SetItemFont(1,f)

    def selHazPath(self, event):
        dir = os.path.dirname(self._hazPath)
        if (not os.path.isdir(dir)):
            dir = os.path.expanduser("~")

        dlg = wx.DirDialog(self._parent, "Select a directory:", defaultPath=dir,
                           style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            self._rootdir = dlg.GetPath()
            self._hazFilesCLB.Clear()
            self._hazDirTC.SetValue(self._rootdir)
            self._hazFilesCLB.AppendItems(bf.find_xml_files(self._rootdir))
        dlg.Destroy()

    @property
    def hazFilesList(self):
        return [os.path.join(self._rootdir, p) for p in
                list(self._hazFilesCLB.GetCheckedStrings())]

    # @property
    # def phenomenon(self):
    #     return self._phenCB.GetStringSelection()


class BymurLoadGridDlg(wx.Dialog):
    def __init__(self, *args, **kwargs):
        self._title = "Load grid file to DB"
        self._style = kwargs.pop('style', 0)
        self._style |= wx.OK | wx.CANCEL
        self._localGridDefaults = {'basedir': kwargs.pop('basedir', ''),
                                   'filepath': kwargs.pop('filepath', '')}
        self._localData = {}
        super(BymurLoadGridDlg, self).__init__(style=self._style, *args,
                                               **kwargs)
        self.SetTitle(self._title)
        self._sizer = wx.BoxSizer(orient=wx.VERTICAL)
        self._gridSizer = wx.GridBagSizer(hgap=10, vgap=10)
        self._sizer.Add(self._gridSizer)

        self._gridBoxSizer = BymurLoadGridBoxSizer(parent=self,
                                             label="Geographical grid "
                                                   "data",
                                             **self._localGridDefaults)
        self._gridSizer.Add(self._gridBoxSizer, flag=wx.EXPAND,
                            pos=(0, 0), span=(1, 1))

        self._sizer.Add(self.CreateButtonSizer(flags=wx.OK | wx.CANCEL),
                        flag=wx.ALL | wx.ALIGN_CENTER, border=10)
        self.SetSizerAndFit(self._sizer)

    def ShowModal(self, *args, **kwargs):
        result = super(BymurLoadGridDlg, self).ShowModal(*args, **kwargs)
        if (result == wx.ID_OK):
            result = 1
            self._localData['filepath'] = self._gridBoxSizer.gridPath
        elif (result == wx.ID_CANCEL):
            result = 0
        else:
            result = -1
        return (result, self._localData)


class BymurDBCreateDlg(wx.Dialog):
    def __init__(self, *args, **kwargs):
        self._title = "Create ByMuR database"
        print "Create ByMuR database, kwargs: %s " % kwargs
        self._style = kwargs.pop('style', 0)
        self._style |= wx.OK | wx.CANCEL
        self._localData = {'db_host': kwargs.pop('db_host', ''),
                           'db_port': kwargs.pop('db_port', ''),
                           'db_user': kwargs.pop('db_user', ''),
                           'db_password': kwargs.pop('db_password', ''),
                           'db_name': kwargs.pop('db_name', '')}
        self._localGeoDefaults = {'grid_path': kwargs.pop('grid_path', '')}
        self._localMapDefaults = {'northing_min': kwargs.pop('northing_min', 0),
                                  'northing_max': kwargs.pop('northing_max', 0),
                                  'easting_min': kwargs.pop('easting_min', 0),
                                  'easting_max': kwargs.pop('easting_max', 0),
                                  'map_path': kwargs.pop('map_path', '')}
        # self._localHazDefaults = {'haz_path': kwargs.pop('haz_path', ''),
        #                           'haz_perc': kwargs.pop('haz_perc', '')}
        self._localHazDefaults = {'haz_path': kwargs.pop('haz_path', '')}

        super(BymurDBCreateDlg, self).__init__(style=self._style, *args,
                                               **kwargs)
        self.SetTitle(self._title)
        self._sizer = wx.BoxSizer(orient=wx.VERTICAL)
        self._gridSizer = wx.GridBagSizer(hgap=10, vgap=10)
        self._sizer.Add(self._gridSizer)

        self._dbBoxSizer = BymurDBBoxSizer(parent=self,
                                           label="Database details",
                                           **self._localData)
        self._gridSizer.Add(self._dbBoxSizer, flag=wx.EXPAND,
                            pos=(0, 0), span=(1, 1))

        self._sizer.Add(self.CreateButtonSizer(flags=wx.OK | wx.CANCEL),
                        flag=wx.ALL | wx.ALIGN_CENTER, border=10)
        self.SetSizerAndFit(self._sizer)

    def ShowModal(self, *args, **kwargs):
        result = super(BymurDBCreateDlg, self).ShowModal(*args, **kwargs)
        if (result == wx.ID_OK):
            result = 1
            self._localData['db_host'] = self._dbBoxSizer.dbHost
            self._localData['db_port'] = self._dbBoxSizer.dbPort
            self._localData['db_user'] = self._dbBoxSizer.dbUser
            self._localData['db_password'] = self._dbBoxSizer.dbPassword
            self._localData['db_name'] = self._dbBoxSizer.dbName
        elif (result == wx.ID_CANCEL):
            result = 0
        else:
            result = -1
        return (result, self._localData)

class BymurAddDBDataDlg(wx.Dialog):
    def __init__(self, *args, **kwargs):
        self._title = 'Add data to database'
        self._style = kwargs.pop('style', 0)
        self._style |= wx.OK | wx.CANCEL
        self._localHazData = {'haz_path': kwargs.pop('haz_path', ''),
                              'phenomena_list': kwargs.pop('phenomena_list', '')
                              }
        self._localGeoDefaults = {'grid_path': kwargs.pop('grid_path', '')}
        self._localGridData = {'grid_list': kwargs.pop('grid_list', []) }
        super(BymurAddDBDataDlg, self).__init__(style=self._style, *args,
                                               **kwargs)
        self.SetTitle(self._title)
        self._sizer = wx.BoxSizer(orient=wx.VERTICAL)
        self._gridSizer = wx.GridBagSizer(hgap=10, vgap=10)
        self._sizer.Add(self._gridSizer)

        self._gridSelectBoxSizer = BymurSelectGridBoxSizer(parent=self,
                                                           label="Grid",
                                        **self._localGridData)
        self._gridSizer.Add(self._gridSelectBoxSizer, flag=wx.EXPAND,
                            pos=(0, 0), span=(1, 1))

        self._hazBoxSizer = BymurHazBoxSizer(parent=self,
                                             label="XML files",
                                             **self._localHazData)
        self._gridSizer.Add(self._hazBoxSizer, flag=wx.EXPAND,
                            pos=(1, 0), span=(1, 1))
        self._sizer.Add(self.CreateButtonSizer(flags=wx.OK | wx.CANCEL),
                        flag=wx.ALL | wx.ALIGN_CENTER, border=10)
        self.SetSizerAndFit(self._sizer)

    def ShowModal(self, *args, **kwargs):
        result = super(BymurAddDBDataDlg, self).ShowModal(*args, **kwargs)
        if (result == wx.ID_OK):
            self._localHazData['haz_files'] = self._hazBoxSizer.hazFilesList
            # self._localHazData['phenomenon'] = self._hazBoxSizer.phenomenon
            self._localHazData['datagrid_name'] = \
                self._gridSelectBoxSizer.gridName
            if self._localHazData['datagrid_name'] == '':
                    result = -1
            elif self._localHazData['haz_files'] == []:
                    result = -1
            else:
                result = 1
        elif (result == wx.ID_CANCEL):
            result = 0
        else:
            result = -1
        return (result, self._localHazData)

class BymurDBLoadDlg(wx.Dialog):
    _textSize = (300, -1)


    def __init__(self, *args, **kwargs):
        self._title = 'Load ByMuR database'
        self._style = kwargs.pop('style', 0)
        self._style |= wx.OK | wx.CANCEL
        self._dbDetails = {'db_host': kwargs.pop('db_host', ''),
                           'db_port': kwargs.pop('db_port', ''),
                           'db_user': kwargs.pop('db_user', ''),
                           'db_password': kwargs.pop('db_password', ''),
                           'db_name': kwargs.pop('db_name', '')
        }
        super(BymurDBLoadDlg, self).__init__(style=self._style, *args, **kwargs)
        self.SetTitle(self._title)
        self._sizer = wx.BoxSizer(orient=wx.VERTICAL)

        self._dbBoxSizer = BymurDBBoxSizer(parent=self,
                                           label="Connection details",
                                           orient=wx.VERTICAL,
                                           **self._dbDetails)

        self._dbBoxSizer.Add(self.CreateButtonSizer(flags=wx.OK | wx.CANCEL))

        self._sizer.Add(self._dbBoxSizer)
        self.SetSizerAndFit(self._sizer)

    def ShowModal(self, *args, **kwargs):
        result = super(BymurDBLoadDlg, self).ShowModal(*args, **kwargs)
        if (result == wx.ID_OK):
            result = 1
            self._dbDetails['db_host'] = self._dbBoxSizer.dbHost
            self._dbDetails['db_port'] = self._dbBoxSizer.dbPort
            self._dbDetails['db_user'] = self._dbBoxSizer.dbUser
            self._dbDetails['db_password'] = self._dbBoxSizer.dbPassword
            self._dbDetails['db_name'] = self._dbBoxSizer.dbName

        elif (result == wx.ID_CANCEL):
            result = 0
        else:
            result = -1
        return (result, self._dbDetails)


class BymurEnsembleDlg(wx.Dialog):


    def __init__(self, *args, **kwargs):
        self._ensBoxSizer = None
        self._title = kwargs.pop('title', '')
        self._style = kwargs.pop('style', 0)
        self._style |= wx.OK | wx.CANCEL
        self._localData = kwargs.pop('data', {})
        # print "data %s " % self._localData
        super(BymurEnsembleDlg, self).__init__(style=self._style, *args,
                                               **kwargs)

        self._sizer = wx.BoxSizer(orient=wx.VERTICAL)

        self._ensBoxSizer = BymurEnsBoxSizer(parent=self,
                                             label="Ensemble hazard definition",
                                             orient=wx.VERTICAL,
                                             data=self._localData)

        self._ensBoxSizer.Add(self.CreateButtonSizer(flags=wx.OK | wx.CANCEL),
                              flag=wx.ALL | wx.ALIGN_CENTER, border=10)

        self._sizer.Add(self._ensBoxSizer)
        self.SetSizerAndFit(self._sizer)

        self.SetTitle(self._title)

    def ShowModal(self, **kwargs):
        result = super(BymurEnsembleDlg, self).ShowModal(**kwargs)
        if (result == wx.ID_OK):
            result = 1
            self._localData = { 'ensHaz': self._ensBoxSizer.ensHaz,
                                'ensPhen': self._ensBoxSizer.ensPhen,
                                'ensGrid': self._ensBoxSizer.ensGrid,
                                'ensExpTime': self._ensBoxSizer.ensExpTime,
                                'ensIMLThresh': self._ensBoxSizer.ensIMLThresh,
                                'ensName': self._ensBoxSizer.ensName,
            }
            if self._localData['ensIMLThresh'] is None:
                result = -1
            if self._localData['ensName'] is '':
                result = -1
            print "Ensemble parameters %s" % self._localData
        elif (result == wx.ID_CANCEL):
            result = 0
        else:
            result = -1
        return (result, self._localData)

class BymurExportHazDlg(wx.Dialog):


    def __init__(self, *args, **kwargs):
        self._ensBoxSizer = None
        self._title = kwargs.pop('title', '')
        self._style = kwargs.pop('style', 0)
        self._style |= wx.OK | wx.CANCEL
        self._localData = kwargs.pop('data', {})
        super(BymurExportHazDlg, self).__init__(style=self._style, *args,
                                               **kwargs)

        self._sizer = wx.BoxSizer(orient=wx.VERTICAL)

        self._expHazBoxSizer = BymurExpHazBoxSizer(parent=self,
                                             label="Export hazard XMLs",
                                             orient=wx.VERTICAL,
                                             data=self._localData)

        self._expHazBoxSizer.Add(self.CreateButtonSizer(flags=wx.OK | wx.CANCEL),
                              flag=wx.ALL | wx.ALIGN_CENTER, border=10)

        self._sizer.Add(self._expHazBoxSizer)
        self.SetSizerAndFit(self._sizer)

        self.SetTitle(self._title)

    def ShowModal(self, **kwargs):
        result = super(BymurExportHazDlg, self).ShowModal(**kwargs)
        if (result == wx.ID_OK):
            result = 1
            self._localData = { 'expHazModel': self._expHazBoxSizer.expHazModel,
                                'expHazPhen': self._expHazBoxSizer.expHazPhen,
                                'expHazGrid': self._expHazBoxSizer.expHazGrid,
                                'expHazExpTime': self._expHazBoxSizer.expHazExpTime,
                                'expHazDir': self._expHazBoxSizer.expHazExpDir,
            }
            print "Export hazard to XMLs %s" % self._localData
        elif (result == wx.ID_CANCEL):
            result = 0
        else:
            result = -1
        return (result, self._localData)

class BymurCmpRiskBoxSizer(BymurStaticBoxSizer):

    def __init__(self, *args, **kwargs):
        self._data = kwargs.pop('data', {})
        super(BymurCmpRiskBoxSizer, self).__init__(*args, **kwargs)
        self._map = bymur_plots.CompareRisk(parent=self._parent)
        self.Add(self._map._canvas, flag=wx.EXPAND)
        self.Add(self._map._toolbar, flag=wx.EXPAND)


class BymurCmpRiskDlg(wx.MultiChoiceDialog):
    def __init__(self, *args, **kwargs):
        self._riskBoxSizer = None
        self._title = kwargs.pop('title', '')
        self._style = kwargs.pop('style', 0)
        self._style |= wx.OK | wx.CANCEL
        self._localData = dict()
        self._localData['risks'] = kwargs.pop('risks', [])
        self._localData['area'] = kwargs.pop('area', [])
        super(BymurCmpRiskDlg, self).__init__(style=self._style, *args,
                                               **kwargs)

        self._sizer = wx.BoxSizer(orient=wx.VERTICAL)

        self._riskBoxSizer = BymurCmpRiskBoxSizer(parent=self,
                                             label="Compare risks",
                                             orient=wx.VERTICAL,
                                             data=self._localData)

        self._riskBoxSizer.Add(self.CreateButtonSizer(flags=wx.OK),
                              flag=wx.ALL | wx.ALIGN_CENTER, border=10)

        self._sizer.Add(self._riskBoxSizer)
        self.SetSizerAndFit(self._sizer)

        self.SetTitle(self._title)

class BymurWxPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        self._map = None
        self._bymur_label = kwargs.pop('label', "")
        self._controller = kwargs.pop('controller', None)
        super(BymurWxPanel, self).__init__(*args, **kwargs)
        self.Enable(False)

    def updateView(self, **kwargs):
        self.Enable(False)
        for panel in self.GetChildren():
            if isinstance(panel, BymurWxPanel):
                panel.updateView(**kwargs)
        self.Enable(True)

    def clear(self):
        if self._map is not None:
            self._map.clear()

class BymurWxCurvesPanel(BymurWxPanel):
    def __init__(self, *args, **kwargs):
        super(BymurWxCurvesPanel, self).__init__(*args, **kwargs)

        self._sizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.SetSizer(self._sizer)
        self._nb = FlatNB.FlatNotebook(self, agwStyle=FNB_NO_X_BUTTON)

        self._curvesNBHaz = BymurWxNBHazPage(parent=self._nb,
                                             controller=self._controller,
                                             label="NBHazPage")
        self._curvesNBInv = BymurWxNBInvPage(parent=self._nb,
                                               controller=self._controller,
                                               label="NBInvPage")
        self._curvesNBFrag = BymurWxNBFragPage(parent=self._nb,
                                               controller=self._controller,
                                               label="NBFragPage")
        self._curvesNBLoss = BymurWxNBLossPage(parent=self._nb,
                                               controller=self._controller,
                                               label="NBLossPage")
        self._curvesNBRisk = BymurWxNBRiskPage(parent=self._nb,
                                               controller=self._controller,
                                               label="NBRiskPage")

        self._nb.AddPage(self._curvesNBHaz, self._curvesNBHaz.title)
        self._nb.AddPage(self._curvesNBInv, self._curvesNBInv.title)
        self._nb.AddPage(self._curvesNBFrag, self._curvesNBFrag.title)
        self._nb.AddPage(self._curvesNBLoss, self._curvesNBLoss.title)
        self._nb.AddPage(self._curvesNBRisk, self._curvesNBRisk.title)

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._controller.nbTabChanged)
        self._sizer.Add(self._nb, 1, wx.EXPAND | wx.ALL, 10)

        self.SetSize((-1, 100))

    def updateView(self, **kwargs):
        super(BymurWxCurvesPanel, self).updateView(**kwargs)
        self._nb.GetCurrentPage().updateView(**kwargs)
        self.Enable(True)

    def updatePages(self):
        all_pages_enable = self.GetTopLevelParent()._hazard is not None
        risk_pages_enable = self.GetTopLevelParent()._risk is not None
        multiple_areas = len(self.GetTopLevelParent()._selected_areas) > 1

        self._nb.EnableTab(self._nb.GetPageIndex(self._curvesNBHaz),
                           (all_pages_enable and not multiple_areas))
        self._nb.EnableTab(self._nb.GetPageIndex(self._curvesNBInv),
                           (all_pages_enable and not multiple_areas))
        self._nb.EnableTab(self._nb.GetPageIndex(self._curvesNBFrag),
                           (risk_pages_enable and not multiple_areas))
        self._nb.EnableTab(self._nb.GetPageIndex(self._curvesNBLoss),
                           (risk_pages_enable and not multiple_areas))
        self._nb.EnableTab(self._nb.GetPageIndex(self._curvesNBRisk),
                           risk_pages_enable)

        if (risk_pages_enable and multiple_areas):
            self._nb.SetSelection(self._nb.GetPageIndex(self._curvesNBRisk))
        elif (not self._nb.GetEnabled(self._nb.GetSelection())):
            self._nb.SetSelection(self._nb.GetPageIndex(self._curvesNBHaz))


    def clear(self):
        for i_p in range(self._nb.GetPageCount()):
            self._nb.GetPage(i_p).clear()



class BymurWxMapPanel(BymurWxPanel):
    def __init__(self, *args, **kwargs):
        self._title = kwargs.pop('title', "Map")
        super(BymurWxMapPanel, self).__init__(*args, **kwargs)
        self._sizer = wx.BoxSizer(orient=wx.VERTICAL)
        _imgfile =  os.path.join(wx.GetTopLevelParent(self).basedir,
                                     "./data/naples_gsatellite.png")
        self._map = bymur_plots.HazardGraph(parent=self,
                            click_callback=self._controller.pick_point_by_index,
                            # selection_callback=self._controller.areas_selection,
                            selection_callback=self._controller.get_areas_data,
                            imgfile = _imgfile)
        # TODO: fix these references
        self._sizer.Add(self._map._canvas, 1, wx.EXPAND | wx.ALL, 0)
        self._sizer.Add(self._map._toolbar, 0, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(self._sizer)

    def updateView(self, **kwargs):
        super(BymurWxMapPanel, self).updateView(**kwargs)
        self._map.plot(wx.GetTopLevelParent(self).hazard,
                       wx.GetTopLevelParent(self).hazard_data,
                       wx.GetTopLevelParent(self).inventory)
        self.Enable(True)

    # def clear(self):
    #     self._map.clear()

    def updatePoint(self, **kwargs):
        if wx.GetTopLevelParent(self).selected_point is not None:
            self._map.selected_point = (wx.GetTopLevelParent(self).
                                        selected_point.easting * 1e-3,
                                        wx.GetTopLevelParent(self).
                                        selected_point.northing * 1e-3)
            self._map.selected_areas = wx.GetTopLevelParent(self).selected_areas
            # print [s.keys() for s in self._map.selected_areas]
            self._map.update_selection()

    @property
    def title(self):
        """Get the current page title."""
        return self._title

    @property
    def map(self):
        """Get the current page title."""
        return self._map

class BymurWxNBInvPage(BymurWxPanel):
    def __init__(self, *args, **kwargs):
        self._title = kwargs.pop('title', "Inventory")
        super(BymurWxNBInvPage, self).__init__(*args, **kwargs)
        self._sizer = wx.BoxSizer(orient=wx.VERTICAL)
        self._map = bymur_plots.InvCurve(parent=self)
        self._sizer.Add(self._map._canvas, 1, wx.EXPAND | wx.ALL, 0)
        self._sizer.Add(self._map._toolbar, 0, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(self._sizer)

    def updateView(self, **kwargs):
        super(BymurWxNBInvPage, self).updateView(**kwargs)
        self._map.plot(hazard=wx.GetTopLevelParent(self).hazard,
                       inventory=wx.GetTopLevelParent(self).inventory,
                       areas=wx.GetTopLevelParent(self).selected_areas)
        self.Enable(True)

    @property
    def title(self):
        """Get the current page title."""
        return self._title

class BymurWxNBFragPage(BymurWxPanel):
    def __init__(self, *args, **kwargs):
        self._title = kwargs.pop('title', "Fragility")
        super(BymurWxNBFragPage, self).__init__(*args, **kwargs)
        self._sizer = wx.BoxSizer(orient=wx.VERTICAL)
        self._map = bymur_plots.FragCurve(parent=self)
        self._sizer.Add(self._map._canvas, 1, wx.EXPAND | wx.ALL, 0)
        self._sizer.Add(self._map._toolbar, 0, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(self._sizer)

    def updateView(self, **kwargs):
        super(BymurWxNBFragPage, self).updateView(**kwargs)
        self._map.plot(hazard=wx.GetTopLevelParent(self).hazard,
                       fragility=wx.GetTopLevelParent(self).fragility,
                       inventory=wx.GetTopLevelParent(self).inventory,
                       areas=wx.GetTopLevelParent(self).selected_areas)
        self.Enable(True)

    @property
    def title(self):
        """Get the current page title."""
        return self._title

class BymurWxNBHazPage(BymurWxPanel):
    def __init__(self, *args, **kwargs):
        self._title = kwargs.pop('title', "Hazard")
        super(BymurWxNBHazPage, self).__init__(*args, **kwargs)
        self._sizer = wx.BoxSizer(orient=wx.VERTICAL)
        self._map = bymur_plots.HazardCurve(parent=self)
        # TODO: fix these references
        self._sizer.Add(self._map._canvas, 1, wx.EXPAND | wx.ALL, 0)
        self._sizer.Add(self._map._toolbar, 0, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(self._sizer)

    def updateView(self, **kwargs):
        super(BymurWxNBHazPage, self).updateView(**kwargs)
        self._map.plot(wx.GetTopLevelParent(self).hazard,
                       wx.GetTopLevelParent(self).hazard_options,
                       wx.GetTopLevelParent(self).selected_point)
        self.Enable(True)

    @property
    def title(self):
        """Get the current page title."""
        return self._title


class BymurWxNBLossPage(BymurWxPanel):
    def __init__(self, *args, **kwargs):
        self._title = kwargs.pop('title', "Loss")
        super(BymurWxNBLossPage, self).__init__(*args, **kwargs)
        self._sizer = wx.BoxSizer(orient=wx.VERTICAL)
        self._map = bymur_plots.LossCurve(parent=self)
        self._sizer.Add(self._map._canvas, 1, wx.EXPAND | wx.ALL, 0)
        self._sizer.Add(self._map._toolbar, 0, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(self._sizer)

    def updateView(self, **kwargs):
        super(BymurWxNBLossPage, self).updateView(**kwargs)
        self._map.plot(hazard=wx.GetTopLevelParent(self).hazard,
                       inventory=wx.GetTopLevelParent(self).inventory,
                       fragility=wx.GetTopLevelParent(self).fragility,
                       loss=wx.GetTopLevelParent(self).loss,
                       areas=wx.GetTopLevelParent(self).selected_areas)
        self.Enable(True)

    @property
    def title(self):
        """Get the current page title."""
        return self._title



class BymurWxNBRiskPage(BymurWxPanel):
    def __init__(self, *args, **kwargs):
        self._title = kwargs.pop('title', "Risk")
        super(BymurWxNBRiskPage, self).__init__(*args, **kwargs)
        self._sizer = wx.BoxSizer(orient=wx.VERTICAL)
        self._map = bymur_plots.RiskCurve(parent=self)
        # self._cmpPanel = BymurWxRiskPanel(parent=self,
        #                                   controller=self._controller,
        #                                   title="Compare Risks",
        #                                   label="CmpRisk")
        self._cmpButton = wx.Button(self, wx.ID_ANY | wx.EXPAND,
                                       'Compare Risks',
                                       size=(-1, -1))
        self.Bind(wx.EVT_BUTTON, self._controller.compare_risks_act,
                  self._cmpButton)
        self._sizer.Add(self._cmpButton, flag=wx.EXPAND)

        self._sizer.Add(self._map._canvas, 1, wx.EXPAND | wx.ALL, 0)
        self._sizer.Add(self._map._toolbar, 0, wx.EXPAND | wx.ALL, 0)
        self._sizer.Add(self._cmpButton, 0, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(self._sizer)

    def updateView(self, **kwargs):
        super(BymurWxNBRiskPage, self).updateView(**kwargs)
        self._map.plot(hazard=wx.GetTopLevelParent(self).hazard,
                       inventory=wx.GetTopLevelParent(self).inventory,
                       fragility=wx.GetTopLevelParent(self).fragility,
                       loss=wx.GetTopLevelParent(self).loss,
                       risk=wx.GetTopLevelParent(self).risk,
                       compare_risks=wx.GetTopLevelParent(self).compare_risks,
                       areas=wx.GetTopLevelParent(self).selected_areas)
        self.Enable(True)

    @property
    def title(self):
        """Get the current page title."""
        return self._title


class BymurWxRightPanel(BymurWxPanel):
    def __init__(self, *args, **kwargs):
        super(BymurWxRightPanel, self).__init__(*args, **kwargs)
        self._sizer = wx.BoxSizer(orient=wx.VERTICAL)
        self._mapPanel = BymurWxMapPanel(parent=self,
                                         controller=self._controller,
                                         label="MapPanel")
        self._mapBox = wx.StaticBox(self, wx.ID_ANY, self._mapPanel.title)
        self._mapBoxSizer = wx.StaticBoxSizer(self._mapBox,
                                              orient=wx.HORIZONTAL)
        self._mapBoxSizer.Add(self._mapPanel, 1, wx.EXPAND | wx.ALL, 0)
        self._mapPanel.Enable(False)
        self._sizer.Add(self._mapBoxSizer, 1, wx.EXPAND | wx.ALL, 5)

        self._curvesPanel = BymurWxCurvesPanel(self, id=wx.ID_ANY,
                                               controller=self._controller,
                                               label="CurvesPanel")

        self._curvesPanel.Enable(False)
        self._sizer.Add(self._curvesPanel, 1, wx.EXPAND | wx.ALL, 0)

        self.Centre()
        self.SetSizer(self._sizer)

    def updateView(self, **kwargs):
        super(BymurWxRightPanel, self).updateView(**kwargs)
        # self.Layout()

    @property
    def curvesPanel(self):
        return self._curvesPanel

    @property
    def mapPanel(self):
        return self._mapPanel

# class BymurWxRiskPanel(BymurWxPanel):
#     def __init__(self, *args, **kwargs):
#         self._title = kwargs.pop('title', "Compare risks")
#         super(BymurWxRiskPanel, self).__init__(*args, **kwargs)
#         self._topWindow = wx.GetTopLevelParent(self)
#         self._sizer = wx.BoxSizer(orient=wx.VERTICAL)
#         self._cmpButton = wx.Button(self, wx.ID_ANY | wx.EXPAND,
#                                        'Compare Risks',
#                                        size=(-1, -1))
#         self.Bind(wx.EVT_BUTTON, self._controller.compare_risks,
#                   self._cmpButton)
#         self._sizer.Add(self._cmpButton, flag=wx.EXPAND)
#         self.SetSizer(self._sizer)


class BymurWxDataPanel(BymurWxPanel):
    def __init__(self, *args, **kwargs):
        self._dataBoxTitle = kwargs.pop('title', "Data")
        super(BymurWxDataPanel, self).__init__(*args, **kwargs)
        self._topWindow = wx.GetTopLevelParent(self)
        self._sizer = wx.BoxSizer(orient=wx.VERTICAL)

        ## Nearest data point coordinates and values
        self._dataBox = wx.StaticBox(
            self,
            wx.ID_ANY,
            "Selected point and area")
        self._dataBoxSizer = wx.StaticBoxSizer(
            self._dataBox,
            orient=wx.VERTICAL)

        self._dataSizer = wx.FlexGridSizer(5, 2, hgap=5, vgap=5)
        self._dataBoxSizer.Add(self._dataSizer)

        vpos = 0
        self._dataHazLabel = wx.StaticText(self, wx.ID_ANY, 'Hazard ')
        self._dataHazTC = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_READONLY)
        self._dataSizer.Add(self._dataHazLabel,
                              flag=wx.ALIGN_BOTTOM)
        self._dataSizer.Add(self._dataHazTC)

        self._dataProbLabel = wx.StaticText(self, wx.ID_ANY, 'Probability ')
        self._dataProbTC = wx.TextCtrl(self, wx.ID_ANY,
                                       style=wx.TE_READONLY)
        self._dataSizer.Add(self._dataProbLabel,
                              flag=wx.ALIGN_BOTTOM)
        self._dataSizer.Add(self._dataProbTC)

        ## Area Inventory details
        # self._invBox = wx.StaticBox(
        #     self,
        #     wx.ID_ANY,
        #     "Selected area")
        # self._invBoxSizer = wx.StaticBoxSizer(
        #     self._invBox,
        #     orient=wx.VERTICAL)
        # self._invSizer = wx.FlexGridSizer(5, 2, hgap=5, vgap=5)
        # self._invBoxSizer.Add(self._invSizer)

        self._invAreaIDLabel = wx.StaticText(self, wx.ID_ANY,
                                    "Area ID")
        self._invAreaIDTC = wx.TextCtrl(self, wx.ID_ANY,
                                        style=wx.TE_READONLY)
        self._dataSizer.Add(self._invAreaIDLabel,
                             flag=wx.EXPAND)
        self._dataSizer.Add(self._invAreaIDTC, flag=wx.EXPAND)

        self._invSecIDLabel = wx.StaticText(self, wx.ID_ANY,
                                    "Section ID")
        self._invSecIDTC = wx.TextCtrl(self, wx.ID_ANY,
                                      style=wx.TE_READONLY)
        self._dataSizer.Add(self._invSecIDLabel,
                             flag=wx.EXPAND)
        self._dataSizer.Add(self._invSecIDTC, flag=wx.EXPAND)

        self._invCentroidLabelX = wx.StaticText(self, wx.ID_ANY,
                                    "Centroid X")
        self._invCentroidXTC = wx.TextCtrl(self, wx.ID_ANY,
                                           style=wx.TE_READONLY)
        self._invCentroidLabelY = wx.StaticText(self, wx.ID_ANY,
                                    "Centroid Y")
        self._invCentroidYTC = wx.TextCtrl(self, wx.ID_ANY,
                                           style=wx.TE_READONLY)
        self._dataSizer.Add(self._invCentroidLabelX,
                             flag=wx.EXPAND)
        self._dataSizer.Add(self._invCentroidXTC, flag=wx.EXPAND)
        self._dataSizer.Add(self._invCentroidLabelY, flag=wx.EXPAND)
        self._dataSizer.Add(self._invCentroidYTC, flag=wx.EXPAND)

        self._invTotalLabel = wx.StaticText(self, wx.ID_ANY,
                                    "Total buildings number")
        self._invTotalTC = wx.TextCtrl(self, wx.ID_ANY,
                                      style=wx.TE_READONLY)
        self._dataSizer.Add(self._invTotalLabel,
                             flag=wx.EXPAND)
        self._dataSizer.Add(self._invTotalTC, flag=wx.EXPAND)

        self._classBox = wx.StaticBox(
            self,
            wx.ID_ANY,
            "Classes")
        self._classBoxSizer = wx.StaticBoxSizer(
            self._classBox,
            orient=wx.HORIZONTAL)
        self._classSizer = wx.GridBagSizer()
        self._classBoxSizer.Add(self._classSizer)

        # General Classes
        self._genClassBox = wx.StaticBox(
            self,
            wx.ID_ANY,
            "General")
        self._genClassBoxSizer = wx.StaticBoxSizer(
            self._genClassBox,
            orient=wx.VERTICAL)
        self._genClassSizer = wx.GridBagSizer(hgap=5, vgap=5)
        self._genClassBoxSizer.Add(self._genClassSizer)
        self._genClasses = []
        self._classBoxSizer.Add(self._genClassBoxSizer, flag=wx.EXPAND)

        # Age Classes
        self._ageClassBox = wx.StaticBox(
            self,
            wx.ID_ANY,
            "Ages")
        self._ageClassBoxSizer = wx.StaticBoxSizer(
            self._ageClassBox,
            orient=wx.VERTICAL)
        self._ageClassSizer = wx.GridBagSizer(hgap=5, vgap=5)
        self._ageClassBoxSizer.Add(self._ageClassSizer)
        self._ageClasses = []
        self._classBoxSizer.Add(self._ageClassBoxSizer, flag=wx.EXPAND)

        # House Classes
        self._houseClassBox = wx.StaticBox(
            self,
            wx.ID_ANY,
            "Houses")
        self._houseClassBoxSizer = wx.StaticBoxSizer(
            self._houseClassBox,
            orient=wx.VERTICAL)
        self._houseClassSizer = wx.GridBagSizer(hgap=5, vgap=5)
        self._houseClassBoxSizer.Add(self._houseClassSizer)
        self._houseClasses = []
        self._classBoxSizer.Add(self._houseClassBoxSizer, flag=wx.EXPAND)

        self._sizer.Add(self._dataBoxSizer, flag=wx.ALL|wx.EXPAND)
        self._sizer.Add(self._classBoxSizer, flag=wx.ALL|wx.EXPAND)
        self.SetSizer(self._sizer)

    def updateInventory(self):
        vpos = 0
        self._genClasses = []
        self._genClassSizer.Clear()
        self._genClassSizer.Layout()
        for gen_class in self._topWindow.inventory.classes['generalClasses']:
            _genclassrow = dict()
            _genclassrow['label'] = wx.StaticText(self, wx.ID_ANY,
                                                  gen_class.name)
            _genclassrow['value'] = wx.TextCtrl(self, wx.ID_ANY,
                                                style=wx.TE_READONLY,
                                                size=(40,20))
            self._genClassSizer.Add(_genclassrow['label'],
                             flag=wx.EXPAND, pos=(vpos, 0), span=(1, 1))

            self._genClassSizer.Add(_genclassrow['value'],
                                    flag=wx.EXPAND, pos=(vpos, 1), span=(1, 1))
            self._genClasses.append(_genclassrow)
            vpos +=1


        vpos = 0
        self._ageClasses = []
        self._ageClassSizer.Clear()
        self._ageClassSizer.Layout()
        for age_class in self._topWindow.inventory.classes['ageClasses']:
            _ageclassrow = dict()
            _ageclassrow['label'] = wx.StaticText(self, wx.ID_ANY,
                                                  age_class.name)
            _ageclassrow['value'] = wx.TextCtrl(self, wx.ID_ANY,
                                                style=wx.TE_READONLY,
                                                size=(40,20))
            self._ageClassSizer.Add(_ageclassrow['label'],
                             flag=wx.EXPAND, pos=(vpos, 0), span=(1, 1))

            self._ageClassSizer.Add(_ageclassrow['value'],
                                    flag=wx.EXPAND, pos=(vpos, 1), span=(1, 1))
            self._ageClasses.append(_ageclassrow)
            vpos +=1


        vpos = 0
        self._houseClasses = []
        self._houseClassSizer.Clear()
        self._houseClassSizer.Layout()
        for house_class in self._topWindow.inventory.classes['houseClasses']:
            _houseclassrow = dict()
            _houseclassrow['label'] = wx.StaticText(self, wx.ID_ANY,
                                                  house_class.name)
            _houseclassrow['value'] = wx.TextCtrl(self, wx.ID_ANY,
                                                style=wx.TE_READONLY,
                                                size=(40,20))
            self._houseClassSizer.Add(_houseclassrow['label'],
                             flag=wx.EXPAND, pos=(vpos, 0), span=(1, 1))

            self._houseClassSizer.Add(_houseclassrow['value'],
                                    flag=wx.EXPAND, pos=(vpos, 1), span=(1, 1))
            self._houseClasses.append(_houseclassrow)
            vpos +=1


        self.Layout()
        self.GetParent().Layout()



    def updateView(self, **kwargs):
        super(BymurWxDataPanel, self).updateView(**kwargs)

    def clearPoint(self):
        self._dataHazTC.SetValue('')
        self._dataProbTC.SetValue('')
        self._invAreaIDTC.SetValue('')
        self._invSecIDTC.SetValue('')
        self._invCentroidXTC.SetValue('')
        self._invCentroidYTC.SetValue('')
        self._invTotalTC.SetValue('')

    def updatePointData(self):
        if self._topWindow.selected_point.haz_value:
            self._dataHazTC.SetValue(
                str(self._topWindow.selected_point.haz_value))
        else:
            self._dataHazTC.SetValue("")

        if self._topWindow.selected_point.prob_value:
            self._dataProbTC.SetValue(
                str(self._topWindow.selected_point.prob_value))
        else:
            self._dataProbTC.SetValue("")

        grand_total = 0
        for a in self._topWindow.selected_areas:
            try:
                grand_total += a['inventory'].asset.total
            except AttributeError:
                pass

        area_inventory = self._topWindow.selected_areas[0]['inventory']

        try:
            self._invAreaIDTC.SetValue(str(area_inventory.areaID))
        except AttributeError:
            self._invAreaIDTC.SetValue('')

        try:
            self._invSecIDTC.SetValue(str(area_inventory.sectionID))
        except AttributeError:
            self._invSecIDTC.SetValue('')

        try:
            self._invCentroidXTC.SetValue(str(area_inventory.centroid[0]))
            self._invCentroidYTC.SetValue(str(area_inventory.centroid[1]))
        except AttributeError:
            self._invCentroidXTC.SetValue('')
            self._invCentroidYTC.SetValue('')


        self._invTotalTC.SetValue(str(grand_total))


        if isinstance(self._topWindow.inventory.classes, dict):
            if self._topWindow.inventory.classes['generalClasses']:
                for i_class in range(len(self._topWindow.inventory.
                        classes['generalClasses'])):
                    grand_total = 0
                    for a in self._topWindow.selected_areas:
                        try:
                            grand_total += a['inventory'].asset.\
                                        counts['genClassCount'][i_class]
                        except KeyError:
                            pass
                    self._genClasses[i_class]['value'].SetValue(str(
                        grand_total))
            else:
                for i_class in range(len(self._genClasses)):
                    self._genClasses[i_class]['value'].SetValue('0')

            if self._topWindow.inventory.classes['ageClasses']:
                for i_class in range(len(self._topWindow.inventory.
                        classes['ageClasses'])):
                    grand_total = 0
                    for a in self._topWindow.selected_areas:
                        try:
                            grand_total += a['inventory'].asset.\
                                        counts['ageClassCount'][i_class]
                        except KeyError:
                            pass
                    self._ageClasses[i_class]['value'].SetValue(str(
                        grand_total))
            else:
                for i_class in range(len(self._ageClasses)):
                    self._ageClasses[i_class]['value'].SetValue('0')

            if self._topWindow.inventory.classes['houseClasses']:
                for i_class in range(len(self._topWindow.inventory.
                        classes['houseClasses'])):
                    grand_total = 0
                    for a in self._topWindow.selected_areas:
                        try:
                            grand_total += a['inventory'].asset.\
                                        counts['houseClassCount'][i_class]
                        except KeyError:
                            pass
                    self._houseClasses[i_class]['value'].SetValue(str(
                        grand_total))
            else:
                for i_class in range(len(self._houseClasses)):
                    self._houseClasses[i_class]['value'].SetValue('0')

            self.Enable(True)


class BymurWxCtrlsPanel(BymurWxPanel):
    def __init__(self, *args, **kwargs):
        self._ctrlsBoxTitle = kwargs.pop('title', "Controls")
        super(BymurWxCtrlsPanel, self).__init__(*args, **kwargs)
        self._topWindow = wx.GetTopLevelParent(self)
        self._sizer = wx.BoxSizer(orient=wx.VERTICAL)

        self._ctrlsBox = wx.StaticBox(
            self,
            wx.ID_ANY,
            self.ctrlsBoxTitle)
        self._ctrlsBoxSizer = wx.StaticBoxSizer(
            self._ctrlsBox,
            orient=wx.VERTICAL)

        self._ctrlsSizer = wx.GridBagSizer(hgap=5, vgap=5)
        self._ctrlsBoxSizer.Add(self._ctrlsSizer)

        vpos = 0
        self._phenLabel = wx.StaticText(self, wx.ID_ANY,
                                        'Phenomeon type')
        self._phenCB = wx.ComboBox(self, wx.ID_ANY, choices=[],
                                   style=wx.CB_READONLY, size=(200, -1))

        self._phenCB.Bind(wx.EVT_COMBOBOX, self.updateCtrls)
        self._ctrlsSizer.Add(self._phenLabel, pos=(vpos, 0), span=(1, 2),
                             flag=wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT)
        self._ctrlsSizer.Add(self._phenCB, pos=(vpos, 2), span=(1, 2))

        vpos += 1
        self._hazModLabel = wx.StaticText(self, wx.ID_ANY,
                                          'Hazard Model')
        self._hazModCB = wx.ComboBox(self, wx.ID_ANY, choices=[],
                                     style=wx.CB_READONLY, size=(200, -1))
        self._hazModCB.Bind(wx.EVT_COMBOBOX, self.updateCtrls)
        self._ctrlsSizer.Add(self._hazModLabel, pos=(vpos, 0), span=(1, 2),
                             flag=wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT)
        self._ctrlsSizer.Add(self._hazModCB, pos=(vpos, 2), span=(1, 2))

        # expTime
        vpos += 1
        self._expTimeLabel = wx.StaticText(self, wx.ID_ANY, 'Exposure Time')
        self._expTimeCB = wx.ComboBox(self, wx.ID_ANY, choices=[],
                                      style=wx.CB_READONLY, size=(120, -1))
        self._expTimeLabelBis = wx.StaticText(self, wx.ID_ANY, '[years]')
        self._expTimeCB.Bind(wx.EVT_COMBOBOX, self.updateCtrls)
        self._ctrlsSizer.Add(self._expTimeLabel, pos=(vpos, 0), span=(1, 2),
                             flag=wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT)
        self._ctrlsSizer.Add(self._expTimeCB, pos=(vpos, 2), span=(1, 1))
        self._ctrlsSizer.Add(self._expTimeLabelBis, pos=(vpos, 3), span=(1, 1),
                             flag=wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM)
        # riskModel
        vpos += 1
        self._riskModLabel = wx.StaticText(self, wx.ID_ANY,
                                          'Risk Model')
        self._riskModCB = wx.ComboBox(self, wx.ID_ANY, choices=[],
                                     style=wx.CB_READONLY, size=(200, -1))
        self._riskModCB.Bind(wx.EVT_COMBOBOX, self.updateCtrls)
        self._ctrlsSizer.Add(self._riskModLabel, pos=(vpos, 0), span=(1, 2),
                             flag=wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT)
        self._ctrlsSizer.Add(self._riskModCB, pos=(vpos, 2), span=(1, 2))

        # returnPeriod
        vpos += 1
        self._retPerLabel = wx.StaticText(self, wx.ID_ANY, 'Return Period')
        self._retPerText = wx.TextCtrl(self, wx.ID_ANY, size=(120, -1),
                                       style=wx.TE_PROCESS_ENTER)
        self._retPerText.Enable(False)
        self.Bind(wx.EVT_TEXT_ENTER, self._controller.update_hazard_options,
                  self._retPerText)
        self._retPerLabelBis = wx.StaticText(self, wx.ID_ANY, '[years]')
        self._ctrlsSizer.Add(self._retPerLabel, pos=(vpos, 0), span=(1, 2),
                             flag=wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT)
        self._ctrlsSizer.Add(self._retPerText, pos=(vpos, 2), span=(1, 1))
        self._ctrlsSizer.Add(self._retPerLabelBis, pos=(vpos, 3), span=(1, 2),
                             flag=wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM)

        # intensityThres
        vpos += 1
        self._intThresLabel = wx.StaticText(self, wx.ID_ANY, 'Intensity '
                                                             'Threshold')
        self._intThresText = wx.TextCtrl(self, wx.ID_ANY, size=(120, -1),
                                         style=wx.TE_PROCESS_ENTER)
        self._intThresText.Enable(False)
        self.Bind(wx.EVT_TEXT_ENTER, self._controller.update_hazard_options,
                  self._intThresText)
        # self._intThresLabelBis = wx.StaticText(self, wx.ID_ANY, '')
        self._ctrlsSizer.Add(self._intThresLabel, pos=(vpos, 0), span=(1, 2),
                             flag=wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT)
        self._ctrlsSizer.Add(self._intThresText, pos=(vpos, 2), span=(1, 1))
        # self._ctrlsSizer.Add(self._intThresLabelBis, pos=(vpos, 3), span=(1, 1),
        #                      flag=wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM)


        vpos += 1
        self._updateButton = wx.Button(self, wx.ID_ANY | wx.EXPAND,
                                       'Update Map',
                                       size=(-1, -1))
        self.Bind(wx.EVT_BUTTON, self._controller.update_hazard_options,
                  self._updateButton)
        self._ctrlsSizer.Add(self._updateButton, flag=wx.EXPAND, pos=(vpos, 0),
                             span=(3, 4))

        vpos = 0
        self._pointBox = wx.StaticBox(
            self,
            wx.ID_ANY,
            "Point selection",
            style=wx.EXPAND)
        self._pointBoxSizer = wx.StaticBoxSizer(
            self._pointBox,
            orient=wx.VERTICAL)
        self._pointSizer = wx.GridBagSizer(hgap=5, vgap=5)
        self._pointBoxSizer.Add(self._pointSizer, flag=wx.EXPAND)

        self._pointText = wx.StaticText(self, id=wx.ID_ANY,
                                           style=wx.EXPAND,
                                           label="Select a point by "
                                                 "UTM coordinates")
        self._pointSizer.Add(self._pointText, flag=wx.EXPAND, pos=(vpos, 0),
                             span=(1, 4))
        vpos += 1
        self._pointEastLabel = wx.StaticText(self, wx.ID_ANY| wx.EXPAND, 'Easting ')
        self._pointEastSC = wx.SpinCtrl(self, wx.ID_ANY| wx.EXPAND)
        self._pointSizer.Add(self._pointEastLabel, pos=(vpos, 0), span=(1, 1),
                              flag=wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.EXPAND)
        self._pointSizer.Add(self._pointEastSC, pos=(vpos, 1), span=(1, 1), flag=wx.EXPAND)

        self._pointNortLabel = wx.StaticText(self, wx.ID_ANY| wx.EXPAND, 'Northing ')
        self._pointNortSC = wx.SpinCtrl(self, wx.ID_ANY| wx.EXPAND)
        self._pointSizer.Add(self._pointNortLabel, pos=(vpos, 2), span=(1, 1),
                              flag=wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.EXPAND)
        self._pointSizer.Add(self._pointNortSC, pos=(vpos, 3), span=(1, 1), flag=wx.EXPAND)

        vpos += 1
        self._pointButton = wx.Button(self, wx.ID_ANY | wx.EXPAND,
                                        'Update Curve',
                                        size=(-1, -1))
        self.Bind(wx.EVT_BUTTON, self.pointCoordsSel,
                   self._pointButton)
        self._pointSizer.Add(self._pointButton, flag=wx.EXPAND, pos=(vpos, 0),
                              span=(2, 4))

        self._sizer.Add(self._ctrlsBoxSizer, flag=wx.EXPAND)
        self._sizer.Add(self._pointBoxSizer, flag=wx.EXPAND)
        self.SetSizer(self._sizer)
        # self.Enable(False)

    def pointCoordsSel(self, ev):
        self._controller.pick_point_by_coordinates(self._pointEastSC.GetValue(),
                                                   self._pointNortSC.GetValue())

    def clearPoint(self):
        self._pointEastSC.SetValueString('')
        self._pointNortSC.SetValueString('')

    def updatePointSel(self, ev=None, easting='', northing=''):
        self._pointEastSC.SetValueString(easting)
        self._pointNortSC.SetValueString(northing)

    def updatePointData(self):
        try:
            self._pointEastSC.SetValueString(
                str(self._topWindow.selected_point.easting))
        except AttributeError as e:
            self._pointEastSC.SetValueString("")
        try:
            self._pointNortSC.SetValueString(
                str(self._topWindow.selected_point.northing))
        except AttributeError as e:
            self._pointNortSC.SetValueString("")

    def updateCtrls(self, ev=None):
        ctrls_data = wx.GetTopLevelParent(self).ctrls_data
        if (ev is None):  # First data load
            self._phenCB.Clear()
            self._phenCB.AppendItems([haz['phenomenon_name']
                                      for haz in ctrls_data['phenomena']])
            self._phenCB.Enable(True)
            self.Enable(True)
        elif ev.GetEventType() == wx.wxEVT_COMMAND_COMBOBOX_SELECTED:
            if ev.GetEventObject() == self._phenCB:
                _phen_name = self._phenCB.GetStringSelection()
                _hlist = [haz for haz in ctrls_data['hazard_models']
                          if haz['phenomenon_name'] == _phen_name]
                self._hazModCB.Clear()
                self._hazModCB.SetValue('')
                self._hazModCB.AppendItems((list(set([haz['hazard_name']
                                            for haz in _hlist]))))
                self._hazModCB.Enable(True)
                if len(self._hazModCB.Items) > 0:
                    self._hazModCB.SetSelection(0)
                _haz_sel = self._hazModCB.GetValue()
                self._retPerText.SetValue(
                    str(ctrls_data[_phen_name]['ret_per']))
                self._intThresText.SetValue(
                    str(ctrls_data[_phen_name]['int_thresh']))
                self._retPerText.Enable(True)
                self._intThresText.Enable(True)
                _exptimelist = [str(haz['exposure_time']) for haz in
                                    ctrls_data['hazard_models']
                                    if (haz['hazard_name'] == _haz_sel and
                                haz['phenomenon_name'] == _phen_name)]
                self._expTimeCB.Clear()
                self._expTimeCB.SetValue('')
                self._expTimeCB.AppendItems(list(set(_exptimelist)))
                if len(self._expTimeCB.Items) > 0:
                    self._expTimeCB.SetSelection(0)
                self._expTimeCB.Enable(True)
                _exp_time_sel = self._expTimeCB.GetValue()
                if _exp_time_sel != '':
                    _exp_time_sel = float(_exp_time_sel)
                _risklist = [str(haz['risk_model_name']) for haz in
                                    ctrls_data['hazard_models']
                                    if (haz['hazard_name'] == _haz_sel and
                                haz['exposure_time'] == _exp_time_sel and
                                        (haz['risk_model_name'] is not None))]
                self._riskModCB.Clear()
                self._riskModCB.SetValue('')
                self._riskModCB.AppendItems(list(set(_risklist)))
                if len(self._riskModCB.Items) > 0:
                    self._riskModCB.SetSelection(0)
                    self._riskModCB.Enable(True)
                else:
                    self._riskModCB.Enable(False)
            elif ev.GetEventObject() == self._hazModCB:
                _phen_name = self._phenCB.GetStringSelection()
                _haz_sel = self._hazModCB.GetValue()
                _exptimelist = [str(haz['exposure_time']) for haz in
                                    ctrls_data['hazard_models']
                                    if (haz['hazard_name'] == _haz_sel and
                                haz['phenomenon_name'] == _phen_name)]
                self._expTimeCB.Clear()
                self._expTimeCB.SetValue('')
                self._expTimeCB.AppendItems(list(set(_exptimelist)))
                if len(self._expTimeCB.Items) > 0:
                    self._expTimeCB.SetSelection(0)
                self._expTimeCB.Enable(True)
                _exp_time_sel = self._expTimeCB.GetValue()
                if _exp_time_sel != '':
                    _exp_time_sel = float(_exp_time_sel)
                _risklist = [str(haz['risk_model_name']) for haz in
                                    ctrls_data['hazard_models']
                                    if (haz['hazard_name'] == _haz_sel and
                                haz['exposure_time'] == _exp_time_sel and
                                        haz['risk_model_name'] is not
                                         None)]
                self._riskModCB.Clear()
                self._riskModCB.SetValue('')
                self._riskModCB.AppendItems(list(set(_risklist)))
                if len(self._riskModCB.Items) > 0:
                    self._riskModCB.SetSelection(0)
                    self._riskModCB.Enable(True)
                else:
                    self._riskModCB.Enable(False)
            elif ev.GetEventObject() == self._expTimeCB:
                _haz_sel = self._hazModCB.GetValue()
                _exp_time_sel = self._expTimeCB.GetValue()
                if _exp_time_sel != '':
                    _exp_time_sel = float(_exp_time_sel)
                _risklist = [str(haz['risk_model_name']) for haz in
                                    ctrls_data['hazard_models']
                                    if (haz['hazard_name'] == _haz_sel and
                                haz['exposure_time'] == _exp_time_sel and
                                        haz['risk_model_name'] is not None)]
                self._riskModCB.Clear()
                self._riskModCB.SetValue('')
                self._riskModCB.AppendItems(list(set(_risklist)))
                if len(self._riskModCB.Items) > 0:
                    self._riskModCB.SetSelection(0)
                    self._riskModCB.Enable(True)
                else:
                    self._riskModCB.Enable(False)
            elif ev.GetEventType() == bf.wxBYMUR_UPDATE_ALL:
                pass

    def updateView(self, **kwargs):
        super(BymurWxCtrlsPanel, self).updateView(**kwargs)

    def updatePointInterval(self):
        self._pointEastSC.SetRange(
            minVal=wx.GetTopLevelParent(self).hazard.grid_limits['east_min'],
            maxVal=wx.GetTopLevelParent(self).hazard.grid_limits['east_max']
            )
        self._pointNortSC.SetRange(
            minVal=wx.GetTopLevelParent(self).hazard.grid_limits['north_min'],
            maxVal=wx.GetTopLevelParent(self).hazard.grid_limits['north_max']
            )

    def clearCtrls(self):
        self._phenCB.Clear()
        self._phenCB.SetItems([])
        self._phenCB.SetValue('')
        self._phenCB.Enable(False)

        self._hazModCB.Clear()
        self._hazModCB.SetItems([])
        self._hazModCB.SetValue('')
        self._hazModCB.Enable(False)

        self._expTimeCB.Clear()
        self._expTimeCB.SetItems([])
        self._expTimeCB.SetValue('')
        self._expTimeCB.Enable(False)

        self._riskModCB.Clear()
        self._riskModCB.SetValue('')
        self._riskModCB.SetItems([])
        self._riskModCB.Enable(False)
        
        self._retPerText.SetValue('')
        self._retPerText.Enable(False)

        self._intThresText.SetValue('')
        self._intThresText.Enable(False)

        

    @property
    def ctrlsBoxTitle(self):
        """Get the current ctrlsBoxTitle."""
        return self._ctrlsBoxTitle

    @ctrlsBoxTitle.setter
    def ctrlsBoxTitle(self, value):
        self._ctrlsBoxTitle = value
        self._ctrlsBox.SetLabel(self._ctrlsBoxTitle)

    @property
    def hazard_options(self):
        """Get the current ctrlsBox parameters"""
        values = {}
        values['hazard_name'] = self._hazModCB.GetStringSelection()
        values['risk_model_name'] = self._riskModCB.GetStringSelection()
        values['ret_per'] = self._retPerText.GetValue()
        values['int_thresh'] = self._intThresText.GetValue()
        values['exp_time'] = self._expTimeCB.GetStringSelection()
        return values



class BymurWxMenu(wx.MenuBar):
    """
    This class provides all program menus
    """
    _menu_actions = {}
    _db_actions = []
    _map_actions = []

    def __init__(self, *args, **kwargs):
        self._controller = kwargs.pop('controller', None)
        super(BymurWxMenu, self).__init__(*args, **kwargs)

        # File menu and items
        self.menuFile = wx.Menu()
        menuItemTmp = self.menuFile.Append(wx.ID_ANY, '&Connect database')
        self._menu_actions[menuItemTmp.GetId()] = self._controller.connect_db
        menuItemTmp = self.menuFile.Append(wx.ID_ANY, '&Close database '
                                                      'connection')
        self._menu_actions[menuItemTmp.GetId()] = self._controller.close_db
        menuItemTmp.Enable(False)
        self._db_actions.append(menuItemTmp)
        self.menuFile.AppendSeparator()
        self.menuFile.Append(wx.ID_CLOSE, '&Quit')
        self._menu_actions[wx.ID_CLOSE] = self._controller.quit
        self.Append(self.menuFile, '&File')

        # Database menu and items
        self.menuDB = wx.Menu()
        menuItemTmp = self.menuDB.Append(wx.ID_ANY,
                                         '&Create DataBase (DB)')
        self._menu_actions[menuItemTmp.GetId()] = self._controller.create_db
        menuItemTmp = self.menuDB.Append(wx.ID_ANY, '&Add Data to DB')
        self._db_actions.append(menuItemTmp)
        self._menu_actions[
            menuItemTmp.GetId()] = self._controller.add_data
        menuItemTmp.Enable(False)
        self.menuDB.AppendSeparator()
        menuItemTmp = self.menuDB.Append(wx.ID_ANY, '&Drop All DB Tables')
        self._db_actions.append(menuItemTmp)
        menuItemTmp.Enable(False)
        self._menu_actions[
            menuItemTmp.GetId()] = self._controller.drop_tables
        self.Append(self.menuDB, '&DataBase')

        # Grid menu
        self.menuGrid = wx.Menu()
        menuItemTmp = self.menuGrid.Append(wx.ID_ANY,
                                         '&Load grid file')
        menuItemTmp.Enable(False)
        self._db_actions.append(menuItemTmp)
        self._menu_actions[menuItemTmp.GetId()] = self._controller.load_grid
        self.Append(self.menuGrid, '&Grid')

        # Plot menu and items
        self.menuPlot = wx.Menu()
        menuItemTmp = self.menuPlot.Append(wx.ID_ANY,
                                           '&Export Hazard XMLs')
        self._menu_actions[menuItemTmp.GetId()] = self._controller.export_hazard
        self._db_actions.append(menuItemTmp)
        menuItemTmp.Enable(False)

        menuItemTmp = self.menuPlot.Append(wx.ID_ANY,
                                           '&Export Raster ASCII (GIS)')  # original method was exportAsciiGis
        self._menu_actions[menuItemTmp.GetId()] = self._controller.exportASCII
        self._map_actions.append(menuItemTmp)
        menuItemTmp.Enable(False)
        menuItemTmp = self.menuPlot.Append(wx.ID_ANY, '&Show Points',
                                           kind=wx.ITEM_CHECK)  # original method was showPoints
        self._menu_actions[menuItemTmp.GetId()] = self._controller.showPoints
        menuItemTmp.Enable(False)
        self.Append(self.menuPlot, '&Export')

        # Analysis menu and items
        self.menuAnalysis = wx.Menu()
        menuItemTmp = self.menuAnalysis.Append(wx.ID_ANY,
                                               'Create &Ensemble hazard')  # original method was openEnsembleFr
        self._db_actions.append(menuItemTmp)
        self._menu_actions[
            menuItemTmp.GetId()] = self._controller.create_ensemble
        self._map_actions.append(menuItemTmp)
        menuItemTmp.Enable(False)
        self.Append(self.menuAnalysis, '&Analysis')


    def doMenuAction(self, event):
        evt_id = event.GetId()
        action = self._menu_actions.get(evt_id, None)
        if action:
            action()
        else:
            raise Exception, "Menu action not defined!"

    def fireEvent(self):
        print "Fire bf.BYMUR_UPDATE_ALL event!"
        event = bf.BymurUpdateEvent(bf.BYMUR_UPDATE_ALL, 1)
        wx.PostEvent(self, event)

    @property
    def dbControls(self):
        return self._db_actions

    @property
    def mapControls(self):
        return self._map_actions


class BymurWxView(wx.Frame):
    # TODO: lot of methods should be moved to wx.App, not frame
    status_txt_ready = "ByMuR ready"
    _isbusy = False
    _busymsg = "Wait please..."
    _disableAll = None

    # TODO: These should be in controller or core?
    _db_connected = False
    _db_loaded = False

    def __init__(self, *args, **kwargs):
        self._basedir =  kwargs.pop('basedir', None)
        self._controller = kwargs.pop('controller', None)
        self._inventory = kwargs.pop('inventory', None)
        self._title = kwargs.pop('title', '')
        super(BymurWxView, self).__init__(*args, **kwargs)

        self._ctrls_data = {}
        self._hazard = None
        self._hazard_data = None
        self._hazard_options = {}
        self._loss = None
        self._risk = None

        self._selected_point = None
        # self._selected_area = None
        self._selected_areas = None

        self._compare_risks = []


        # TODO: make a list for events
        self.Bind(bf.BYMUR_UPDATE_ALL, self.OnBymurEvent)
        self.Bind(bf.BYMUR_UPDATE_POINT, self.OnBymurEvent)
        self.Bind(bf.BYMUR_UPDATE_CURVE, self.OnBymurEvent)
        self.Bind(bf.BYMUR_UPDATE_MAP, self.OnBymurEvent)
        self.Bind(bf.BYMUR_UPDATE_DIALOG, self.OnBymurEvent)
        self.Bind(bf.BYMUR_UPDATE_CTRLS, self.OnBymurEvent)
        self.Bind(bf.BYMUR_THREAD_CLOSED, self.OnBymurEvent)
        self.Bind(bf.BYMUR_DB_CONNECTED, self.OnBymurEvent)
        self.Bind(bf.BYMUR_DB_CLOSED, self.OnBymurEvent)

        # Menu
        self.menuBar = BymurWxMenu(controller=self._controller)
        self.SetMenuBar(self.menuBar)
        self.Bind(wx.EVT_MENU, self.menuBar.doMenuAction)

        # StatusBar
        self.statusbar = self.CreateStatusBar()
        self.PushStatusText(self.status_txt_ready)

        # Main panel
        self.mainSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        # self._leftSizer = wx.BoxSizer(orient=wx.VERTICAL)
        self._leftSizer = wx.GridBagSizer(5, 4)
        self._ctrlsPanel = BymurWxCtrlsPanel(parent=self,
                                           controller=self._controller,
                                           title="Model",
                                           label="CtrlsPanel")

        self._dataPanel = BymurWxDataPanel(parent=self,
                                           controller=self._controller,
                                           title="Data",
                                           label="DataPanel")

        self._rightPanel = BymurWxRightPanel(parent=self,
                                             controller=self._controller,
                                             label="RightPanel")
        self._leftSizer.Add(self._ctrlsPanel, pos=(0,0))
        self._leftSizer.Add(self._dataPanel, pos=(1,0))
        self.mainSizer.Add(self._leftSizer, 0)
        self.mainSizer.Add(self._rightPanel, 1, wx.EXPAND)
        self.SetSizer(self.mainSizer)
        self.SetSize((1200, 900))

    def reset(self):
        self._ctrls_data = {}
        self._hazard = None
        self._hazard_data = None
        self._hazard_options = {}
        self._selected_point = None

    def refresh(self):
        wx.SafeYield()
        self.Refresh()
        self.Update()


    def updateView(self, **kwargs):
        pass

    def saveFile(self, dfl_dir, get_text):
        ext = '.txt'
        dlg = wx.FileDialog(self, message="Save File as...",
                            defaultDir=dfl_dir, defaultFile="*.txt",
                            wildcard="*.*",
                            style=wx.SAVE | wx.FD_OVERWRITE_PROMPT)
        dlg_result = dlg.ShowModal()
        dlg.Destroy()
        if dlg_result == wx.ID_OK:
            savepath = dlg.GetPath()
            if savepath[-4:] == ext:
                filename = savepath
            else:
                filename = savepath + ext

            try:
                fp = open(filename, "w")
                # TODO: i shloud refactor to avoid calculations in the view!
                fp.writelines(get_text(self.rightPanel.mapPanel.map.hazArray))
                fp.close()
            except Exception as e:
                bf.showMessage(parent=self,
                               message=str(e),
                               kind="BYMUR_ERROR",
                               caption="Error")

    def showModalDlg(self, dialog_type, **kwargs):
        """
        :param dialog_type: class name of the dialog to show
        :param **kwargs: argument to the specific dialog
        :return: dictionary containing dialog data on success, None on failure
        """
        result = -1
        data = {}
        dlg = eval(dialog_type)(parent=self, **kwargs)
        while result < 0:
            result, data = dlg.ShowModal()
        if result > 0:
            return data
        else:
            return None

    def selectRisksDlg(self, current_risk, compare_risks, risks):
        """

        """
        opts = [r['model_name'] for r in risks
                if r['model_name'] != current_risk.model_name]
        dlg = wx.MultiChoiceDialog( self, "Pick some programming languages",
                              "wx.MultiChoiceDialog", opts)
        sel_items = []
        for r in opts:
            if r in [cr.model_name for cr in compare_risks]:
                sel_items.append(opts.index(r))
        dlg.SetSelections(sel_items)
        r_strings = []
        if (dlg.ShowModal() == wx.ID_OK):
            selections = dlg.GetSelections()
            r_strings = [opts[x] for x in selections]
            return (len(r_strings), r_strings)
        else:
            return (-1, r_strings)


    def GetBusy(self):
        """
        Is the application busy?
        :return: Boolean
        """
        return self._isbusy

    def SetBusy(self, state, **kwargs):
        """
        Setting the application busy
        :param state: Boolean
        """
        self._isbusy = state
        wait_msg = kwargs.pop('wait_msg', self._busymsg)
        if self._isbusy:
            # self._old_style = self.GetWindowStyle()
            # self.Hide()
            # self.SetWindowStyle(self._old_style | wx.STAY_ON_TOP)
            self.PushStatusText(wait_msg)
            self.Disable()
            self._busydlg = BymurBusyDlg(wait_msg, parent=self)


        else:
            self.PopStatusText()
            # self.Show()
            self._busydlg.Destroy()
            self.Enable()
            del self._busydlg
            # del self._disableAll
            # self.SetWindowStyle(self._old_style)


    def wait(self, **kwargs):
        self.SetBusy(True, **kwargs)


    def OnBymurEvent(self, event):
        if event.GetEventType() == bf.wxBYMUR_DB_CONNECTED:
            print "bf.wxBYMUR_DB_CONNECTED"
            self.dbConnected = True
            self.ctrlsPanel.updateCtrls()
        elif event.GetEventType() == bf.wxBYMUR_DB_CLOSED:
            print "bf.wxBYMUR_DB_CLOSED"
            self.dbConnected = False
            self.reset()
            self.ctrlsPanel.clearCtrls()
            self.ctrlsPanel.clearPoint()
            self.dataPanel.clearPoint()
            self.rightPanel.curvesPanel.clear()
            self.rightPanel.mapPanel.clear()
        elif event.GetEventType() == bf.wxBYMUR_UPDATE_CTRLS:
            print "bf.wxBYMUR_UPDATE_CTRLS"
            self.ctrlsPanel.updateCtrls()
        elif event.GetEventType() == bf.wxBYMUR_UPDATE_DIALOG:
            print "bf.wxBYMUR_UPDATE_DIALOG"
            self.ctrlsPanel.updateCtrls()
        elif event.GetEventType() == bf.wxBYMUR_UPDATE_ALL:
            print "bf.wxBYMUR_UPDATE_ALL"
            self.ctrlsPanel.updateCtrls(event)
            self.dataPanel.updateInventory()
            self.ctrlsPanel.updatePointInterval()
            self.ctrlsPanel.clearPoint()
            self.dataPanel.clearPoint()
            self.rightPanel.curvesPanel.clear()
            self.rightPanel.curvesPanel.updatePages()
            self.rightPanel.curvesPanel.updateView()
            self.rightPanel.mapPanel.clear()
            self.rightPanel.mapPanel.updateView()
            self.rightPanel.Enable(True)
        elif event.GetEventType() == bf.wxBYMUR_UPDATE_POINT:
            print "bf.wxBYMUR_UPDATE_POINT"
            self.ctrlsPanel.updatePointData()
            self.dataPanel.updatePointData()
            self.rightPanel.mapPanel.updatePoint()
            self.rightPanel.curvesPanel.updatePages()
            self.rightPanel.curvesPanel.updateView()
        elif event.GetEventType() == bf.wxBYMUR_UPDATE_MAP:
            print "bf.wxBYMUR_UPDATE_MAP"
            self.rightPanel.curvesPanel.updateView()

        if self.GetBusy():
            self.SetBusy(False)

    @property
    def rightPanel(self):
        return self._rightPanel

    @property
    def ctrlsPanel(self):
        return self._ctrlsPanel

    @property
    def dataPanel(self):
        return self._dataPanel

    @property
    def hazard_options(self):
        return self._ctrlsPanel.hazard_options

    @property
    def busymsg(self):
        """
        """
        return self._busymsg

    @busymsg.setter
    def busymsg(self, msg):
        self._busymsg = msg

    @property
    def dbConnected(self):
        return self._db_connected

    @dbConnected.setter
    def dbConnected(self, value):
        self._db_connected = value
        for item in self.menuBar.dbControls:
            self.menuBar.Enable(item.GetId(), value)

    @property
    def dbLoaded(self):
        return self._db_loaded

    @dbLoaded.setter
    def dbLoaded(self, value):
        self.dbConnected = value
        self._db_loaded = value
        for item in self.menuBar.mapControls:
            self.menuBar.Enable(item.GetId(), value)

    @property
    def basedir(self):
        return self._basedir

    @basedir.setter
    def basedir(self, dir):
        self._basedir = dir

    @property
    def ctrls_data(self):
        return self._ctrls_data

    @ctrls_data.setter
    def ctrls_data(self, data):
        self._ctrls_data = data

    @property
    def hazard(self):
        return self._hazard

    @hazard.setter
    def hazard(self, haz):
        self._hazard = haz

    @property
    def hazard_data(self):
        return self._hazard_data

    @hazard_data.setter
    def hazard_data(self, data):
        self._hazard_data = data

    @property
    def hazard_options(self):
        return self._hazard_options

    @hazard_options.setter
    def hazard_options(self, data):
        self._hazard_options = data

    @property
    def selected_point(self):
        return self._selected_point

    @selected_point.setter
    def selected_point(self, data):
        self._selected_point = data
        
    @property
    def inventory(self):
        return self._inventory

    @inventory.setter
    def inventory(self, data):
        self._inventory = data
        
    @property
    def fragility(self):
        return self._fragility

    @fragility.setter
    def fragility(self, data):
        self._fragility = data
        
    @property
    def loss(self):
        return self._loss

    @loss.setter
    def loss(self, data):
        self._loss = data
    
    @property
    def risk(self):
        return self._risk

    @risk.setter
    def risk(self, data):
        self._risk = data

    # @property
    # def inventory_sections(self):
    #     return self._inventory_sections
    #
    # @inventory_sections.setter
    # def inventory_sections(self, data):
    #     self._inventory_sections = data
        
    # @property
    # def selected_area(self):
    #     return self._selected_area
    # @selected_area.setter
    # def selected_area(self, data):
    #     self._selected_area = data

    @property
    def selected_areas(self):
        return self._selected_areas
    @selected_areas.setter
    def selected_areas(self, data):
        self._selected_areas = data
        
    @property
    def compare_risks(self):
        return self._compare_risks
    @compare_risks.setter
    def compare_risks(self, data):
        self._compare_risks = data

class BymurWxApp(wx.App):
    def __init__(self, *args, **kwargs):
        self._controller = kwargs.pop('controller', None)
        self._basedir =  kwargs.pop('basedir', None)
        self._inventory = kwargs.pop('inventory', None)
        self._hazard_schema = bf.HazardSchema()
        # self._hazard_schema.validate_xml('/hades/dev/bymur-data/test/seis_test.xml')
        # print bf.validate_xml('/hades/dev/bymur-data/test/seis_test.xml',
        #         '/hades/dev/bymur/schemas/bymur_hazard_result.xsd')
        super(BymurWxApp, self).__init__(*args, **kwargs)
        # print bf.validate_xml('/hades/dev/bymur-data/test/seis_test.xml',
        #         '/hades/dev/bymur/schemas/bymur_hazard_result.xsd')
        # self._hazard_schema.validate_xml('/hades/dev/bymur-data/test/seis_test.xml')


    def OnInit(self):
        frame = BymurWxView(parent=None, controller=self._controller,
                            basedir = self._basedir,
                            inventory = self._inventory,
                            title="ByMuR - Refactoring")

        self._controller.set_gui(frame)

        # self._controller._wxframe = frame

        frame.Show(True)
        return True


def build_parser():
    parser = argparse.ArgumentParser(description="ByMuR tool")
    parser.add_argument('-b', '--batch', action="store_true",
                        help='Run ByMuR in batch mode')
    parser.add_argument('-g', '--grid', required=False, help='Grid file to use')
    actions_args = parser.add_mutually_exclusive_group(required=False)
    actions_args.add_argument('-a','--add', action="store_true",
                        help='Load data on database')
    parser.add_argument('files', nargs='*', help='file list')

    return parser


if __name__ == "__main__":
    _batch_mode = False

    opts=vars(build_parser().parse_args(sys.argv[1:]))
    _batch_mode = opts['batch']
    if _batch_mode:
        print "Batch mode!"
        if not opts['grid']:
            raise argparse.ArgumentError(opts["grid"], "Grid file is required!")

        core = bymur_core.BymurCore(batch = _batch_mode)
        core.connect_db(db_host="localhost", db_port="3306",
        db_user="bymurTEST", db_password = "bymurTEST",
        db_name="bymurTEST")
        _grid_name = core.db.load_grid(opts['grid'])
        for f in opts['files']:
            if os.path.isdir(f):
                _haz_files = bf.find_xml_files(f, path=True)
            elif os.path.isfile(f):
                _haz_files = [f]
            _addDataDetails = dict(datagrid_name=_grid_name,
                               haz_files=_haz_files )
            print "addDataDetails %s " % _addDataDetails
            core.add_data(**_addDataDetails)
        exit
    else:
        print "GUI mode!"
        core = bymur_core.BymurCore()
        control = bymur_controller.BymurController(core)
        app = BymurWxApp(redirect=False, controller=control,
                     basedir = control.basedir, inventory = core.inventory)
        app.MainLoop()
