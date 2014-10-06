#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
  Bymur Software computes Risk and Multi-Risk associated to Natural Hazards.
  In particular this tool aims to provide a final working application for
  the city of Naples, considering three natural phenomena, i.e earthquakes,
  volcanic eruptions and tsunamis.1
  The tool is the final product of BYMUR, an Italian project funded by the
  Italian Ministry of Education (MIUR) in the frame of 2008 FIRB, Futuro in
  Ricerca funding program.

  Copyright(C) 2012 Roberto Tonini and Jacopo Selva

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

'''

import os

# third-party modules
import wx
import numpy as np
import matplotlib as mlib
mlib.use('WX')

import matplotlib.pyplot as plt

import globalFunctions as gf
import dbFunctions as db
import getGMapsImg as gmaps
import plotLibs
import scientLibs
import math



class BymurFrame(wx.Frame):

    """
    Main window frame of ByMuR software.
    """

    srcdir = os.path.dirname(os.path.realpath(__file__))
    # default values for some global variables
    pt_sel = 0           # selected point
    haz_sel = 0          # selected hazard phenomenon
    single_haz = True    # selected
    RP = 4975            # selected Return Period
    intTh = 3.0          # selected intensity threshold
    tw = 0               # selected time window

    # defining some input
    hazards = ["Volcanic", "Seismic", "Tsunami"]           # hazard phenomena
    perc = range(1, 100)                                   # percentiles

    # limits of image map
    limits = [375.300, 508.500, 4449.200, 4569.800]
    imgpath = os.path.join(srcdir, "data", "naples.png")   # image map path
    gridpath = os.path.join(srcdir, "data",
                            "naples-grid.txt")  # image map path

    nhaz = len(hazards)
    nperc = len(perc)

    def __init__(self, parent, id, title):
        """
        """
        wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition)

        # menubar
        self.menuBar = wx.MenuBar()
        self.fileMenu = wx.Menu()
        self.dbMenu = wx.Menu()
        self.plotMenu = wx.Menu()

        load_db_item = wx.MenuItem(self.fileMenu, 102, '&Load DataBase')
        self.fileMenu.AppendItem(load_db_item)
        self.Bind(wx.EVT_MENU, self.openLoadDB, id=102)
        self.fileMenu.AppendSeparator()

        load_bymurDBitem = wx.MenuItem(self.fileMenu, 103,
                                       '&Load remote ByMuR DB')
        self.fileMenu.AppendItem(load_bymurDBitem)
        self.Bind(wx.EVT_MENU, self.loadBymurDB, id=103)
        self.fileMenu.AppendSeparator()

        quitItem = wx.MenuItem(self.fileMenu, 105, '&Quit')
        self.fileMenu.AppendItem(quitItem)
        self.Bind(wx.EVT_MENU, self.on_quit, id=105)

        self.menuBar.Append(self.fileMenu, '&File')

        creadbItem = wx.MenuItem(self.dbMenu, 111, '&Create DataBase (DB)')
        self.dbMenu.AppendItem(creadbItem)
        self.Bind(wx.EVT_MENU, self.openCreateDB, id=111)

        addItem = wx.MenuItem(self.dbMenu, 112, '&Add Data to DB')
        self.dbMenu.AppendItem(addItem)
        self.Bind(wx.EVT_MENU, self.openAddDB, id=112)
        addItem.Enable(False)

        dropTabs = wx.MenuItem(self.dbMenu, 116, '&Drop All DB Tables')
        self.dbMenu.AppendItem(dropTabs)
        self.Bind(wx.EVT_MENU, self.dropAllTabs, id=116)
        self.dbMenu.AppendSeparator()

        self.menuBar.Append(self.dbMenu, '&DataBase')

        self.map_export_gis = wx.MenuItem(self.plotMenu, 121,
                                          '&Export Raster ASCII (GIS)')
        self.Bind(wx.EVT_MENU, self.exportAsciiGis, id=121)
        self.plotMenu.AppendItem(self.map_export_gis)
        self.map_menu_ch = wx.MenuItem(self.plotMenu, 131, '&Show Points',
                                       kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.showPoints, id=131)
        self.plotMenu.AppendItem(self.map_menu_ch)
        self.menuBar.Append(self.plotMenu, '&Map')
        self.map_export_gis.Enable(False)
        self.map_menu_ch.Enable(False)

        self.analysisMenu = wx.Menu()

        self.ensemble_item = wx.MenuItem(self.analysisMenu, 211,
                                         'Create &Ensemble hazard')
        self.analysisMenu.AppendItem(self.ensemble_item)

        self.menuBar.Append(self.analysisMenu, '&Analysis')

        self.Bind(wx.EVT_MENU, self.openEnsembleFr, id=211)
        self.ensemble_item.Enable(False)

        self.SetMenuBar(self.menuBar)





        # main sizer
        hbox = wx.BoxSizer(orient=wx.HORIZONTAL)

        # left panel
        self.pnl_lt = wx.Panel(self, wx.ID_ANY)
        vbox_lt = wx.BoxSizer(orient=wx.VERTICAL)

        hbox_haz = wx.StaticBoxSizer(
            wx.StaticBox(
                self.pnl_lt,
                wx.ID_ANY,
                'Hazard'),
            orient=wx.HORIZONTAL)

        self.vbox_haz_lt = wx.BoxSizer(orient=wx.VERTICAL)
        self.vbox_haz_rt = wx.BoxSizer(orient=wx.VERTICAL)

        self.hlbl = wx.StaticText(self.pnl_lt, wx.ID_ANY,
                                  "Select Hazard Model:")
        self.vbox_haz_lt.Add(self.hlbl, 0, wx.TOP, 10)
        self.chaz = wx.ComboBox(self.pnl_lt, wx.ID_ANY, choices=[""],
                                style=wx.CB_READONLY, size=(-1, -1))
        self.vbox_haz_lt.Add(self.chaz, 0, wx.TOP, 4)
        self.Bind(wx.EVT_COMBOBOX, self.selHazard, self.chaz)

        self.vbox_haz_lt.Add(
            wx.StaticText(
                self.pnl_lt,
                wx.ID_ANY,
                "Select Return Period (yr):"),
            0,
            wx.TOP,
            6)
        self.hbox_pth = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.cpth = wx.TextCtrl(self.pnl_lt, wx.ID_ANY, size=(80, -1))
        self.cpth.SetValue(str(self.RP))
        self.hbox_pth.Add(self.cpth, 0, wx.ALIGN_BOTTOM | wx.TOP, 2)
        self.bpth = wx.Button(self.pnl_lt, wx.ID_ANY, 'Update Map',
                              size=(-1, 26))
        self.Bind(wx.EVT_BUTTON, self.selReturnPeriod, self.bpth)
        self.hbox_pth.Add(self.bpth, 0, wx.ALIGN_BOTTOM | wx.LEFT, 5)
        self.vbox_haz_lt.Add(self.hbox_pth)

        self.vbox_haz_lt.Add(
            wx.StaticText(
                self.pnl_lt,
                wx.ID_ANY,
                "Select Intesity Threshold (0-1):"),
            0,
            wx.TOP,
            6)
        self.hbox_ith = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.cith = wx.TextCtrl(self.pnl_lt, wx.ID_ANY, size=(80, -1))
        self.cith.SetValue(str(self.intTh))
        self.hbox_ith.Add(self.cith, 0, wx.ALIGN_BOTTOM | wx.TOP, 2)
        self.bith = wx.Button(self.pnl_lt, wx.ID_ANY, 'Update Map',
                              size=(-1, 26))
        self.Bind(wx.EVT_BUTTON, self.selIntensityTh, self.bith)
        self.hbox_ith.Add(self.bith, 0, wx.ALIGN_BOTTOM | wx.LEFT, 5)
        self.vbox_haz_lt.Add(self.hbox_ith)

        self.twlbl = wx.StaticText(self.pnl_lt, wx.ID_ANY,
                                   "Select Exposure Time (Years):")
        self.vbox_haz_lt.Add(self.twlbl, 0, wx.TOP, 10)
        self.ctw = wx.ComboBox(self.pnl_lt, wx.ID_ANY, choices=[],
                               style=wx.CB_READONLY, size=(80, -1))
        self.ctw.SetSelection(0)
        self.vbox_haz_lt.Add(self.ctw, 0, wx.TOP, 4)
        self.Bind(wx.EVT_COMBOBOX, self.selTimeWindow, self.ctw)

        hbox_haz.Add(self.vbox_haz_lt, 0, wx.EXPAND | wx.ALL, 10)
        hbox_haz.Add(self.vbox_haz_rt, 0, wx.EXPAND | wx.ALL, 10)

        vbox_lt.Add(hbox_haz, 0, wx.EXPAND | wx.ALL, 5)

        self.pnl_lt.SetSizer(vbox_lt)
        self.pnl_lt.Enable(False)
        hbox.Add(self.pnl_lt, 0, wx.EXPAND | wx.ALL, 5)




        # right panel
        vbox_rt = wx.BoxSizer(orient=wx.VERTICAL)
        hbox_map = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, 'Map'),
                                     orient=wx.HORIZONTAL)
        self.pn1 = plotLibs.pn1Canvas(self)
        hbox_map.Add(self.pn1, 1, wx.EXPAND | wx.ALL, 0)
        vbox_rt.Add(hbox_map, 1, wx.EXPAND | wx.ALL, 5)

        self.pnl_curves = wx.Panel(self, wx.ID_ANY)
        self.nb = wx.Notebook(self.pnl_curves)
        self.pn2 = plotLibs.pn2Canvas(self.nb)
        self.pn3 = plotLibs.pn3Canvas(self.nb)
        self.pn4 = plotLibs.pn4Canvas(self.nb)

        self.nb.AddPage(self.pn2, "Hazard")
        self.nb.AddPage(self.pn3, "Vulnerability")
        self.nb.AddPage(self.pn4, "Risk")

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onTabChanged)
        box_nb = wx.BoxSizer(orient=wx.VERTICAL)
        box_nb.Add(self.nb, 1, wx.EXPAND | wx.ALL, 10)
        self.pnl_curves.SetSizer(box_nb)

        self.pn1.Enable(False)
        self.pnl_curves.Enable(False)

        vbox_rt.Add(self.pnl_curves, 1, wx.EXPAND | wx.ALL, 0)
        hbox.Add(vbox_rt, 1, wx.EXPAND | wx.ALL, 5)

        cid = self.pn1.fig.canvas.mpl_connect(
            'button_press_event', self.onClick)
        self.Bind(wx.EVT_CLOSE, self.on_quit)
        self.sb = self.CreateStatusBar()
        self.sb.SetStatusText("... load DB")
        self.SetSizer(hbox)
        self.SetSize((950, 750))
        self.pnl_curves.SetSize((-1, 100))
        self.Centre()

    def loadBymurDB(self, event):
        """
        """
        server = "***REMOVED***"
        user = "bymurUser"
        pwd = "bymurPwd"
        dbname = "bymurDB"
        self.con, self.cur = db.dbConnection(server, user, pwd, dbname)
        self.loadDB()

    def exportAsciiGis(self, event):
        """
        """
        ext = ".txt"
        dfl_dir = os.path.expanduser("~")
        dlg = wx.FileDialog(self, message="Save File as...",
                            defaultDir=dfl_dir, defaultFile="*.txt",
                            wildcard="*.*",
                            style=wx.SAVE | wx.FD_OVERWRITE_PROMPT)

        if (dlg.ShowModal() == wx.ID_OK):
            savepath = dlg.GetPath()

            if (savepath[-4:] == ext):
                filename = savepath
            else:
                filename = savepath + ext

            fp = open(filename, "w")

            for i in range(self.npts):
                fp.write(
                    "%f %f %f\n" %
                    (self.lon[i] *
                     1000,
                     self.lat[i] *
                        1000,
                        self.zmap[i]))

            fp.close()

        dlg.Destroy()

    def dropAllTabs(self, event):
        """
        """
        msg = ("WARNING\nYou are going to delete all tables in you database.\n"
               "Do you want to continue?")
        answer = gf.showYesnoDialog(self, msg, "WARNING")
        if (answer == wx.ID_YES):
            con, cur = db.dbConnection("localhost", "V1User",
                                       "V1Pwd", "DPC-V1-DB")
            db.dbDropAllTabs(con, cur)
        else:
            return

    def onClick(self, event):
        """
        1) Finding the closest point in the data grid to the point clicked
           by the mouse on the map at the top canvas.
        2) Updating the hazard curve plot in the bottom canvas to the
           selected point.
        """

        if (self.pn1.toolbar.mode == ""):

            if (event.inaxes != self.pn1.ax1):
                return
            else:
                lon1 = min(self.lon)
                lon2 = max(self.lon)
                lat1 = min(self.lat)
                lat2 = max(self.lat)
                xsel, ysel = event.xdata, event.ydata
                if (xsel >= lon1 and xsel <= lon2 and
                        ysel >= lat1 and ysel <= lat2):
                    dist = np.sqrt((self.lon - xsel) ** 2 +
                                   (self.lat - ysel) ** 2)
                    self.pt_sel = np.argmin(dist)

                    self.pn2.hazardCurve(
                        self.hc,
                        self.haz_sel,
                        self.tw,
                        self.hazards,
                        self.dtime,
                        self.pt_sel,
                        self.perc,
                        self.iml,
                        self.imt,
                        self.th,
                        self.hc_perc,
                        self.intTh)
                else:
                    return

    def showPoints(self, event):
        """
        Switching show/hide points on the map.
        NOTE: Currently it is not used (see show point menu item)
        """

        val = self.map_menu_ch.IsChecked()

        if val:
            self.pn1.pt.set_cmap(plt.cm.RdYlGn_r)
            self.pn1.pt.set_alpha(1)
            self.pn1.canvas.draw()

        else:
            self.pn1.pt.set_alpha(0)
            self.pn1.canvas.draw()

    def onTabChanged(self, event):
        """
        Switching between tabs of bottom canvas
        """

        sel = self.nb.GetSelection()
        old = event.GetOldSelection()

        if (sel == 1):
            self.nb.ChangeSelection(old)
            msg = ("WARNING:\nThis feature has not been implemented yet")
            gf.showWarningMessage(self, msg, "WARNING")
            return

        elif (sel == 2):
            self.nb.ChangeSelection(old)
            msg = ("WARNING:\nThis feature has not been implemented yet")
            gf.showWarningMessage(self, msg, "WARNING")
            return

        else:
            pass

    def selHazard(self, event):

        self.haz_sel = int(self.chaz.GetSelection())

        self.dtime = []
        for k in range(self.nhaz):
            hazmodtb = "hazard" + str(k + 1)
            tmp = db.dbSelectDtime(self.con, self.cur, hazmodtb)
            dtlist = [str(tmp[i][0]) for i in range(len(tmp))]
            self.dtime.append(dtlist)
        print "dtime = ", self.dtime

        self.tw = 0
        self.ctw.Clear()
        print self.dtime[self.haz_sel], self.haz_sel
        for item in self.dtime[self.haz_sel]:
            print item
            self.ctw.Append(item)
        self.ctw.SetSelection(self.tw)
        print '---------selHazard--------------'
        print 'Selected model: ', self.haz_sel
        ntry = int(math.floor(self.npts * 0.5))
        tmp2 = self.hc[self.haz_sel][self.tw][0][ntry]
        print tmp2, type(tmp2)
        tmp = sum([float(j) for j in tmp2.split()])
        if (tmp == 0):
            busydlg = wx.BusyInfo("...Reading hazard from DB")
            wx.Yield()
            db.dbReadHC(self.haz_sel, self.tw, self.dtime, self.cur, self.hc,
                        self.hc_perc)
            busydlg = None

        self.zmap = self.pn1.hazardMap(
            self.hc,
            self.lon,
            self.lat,
            self.id_area,
            self.nareas,
            self.npts,
            self.hazards,
            self.dtime,
            self.haz_sel,
            self.tw,
            self.th,
            self.intTh,
            self.perc,
            self.imgpath,
            self.limits,
            self.iml,
            self.imt)
        self.pn2.hazardCurve(self.hc, self.haz_sel, self.tw, self.hazards,
                             self.dtime, self.pt_sel, self.perc, self.iml,
                             self.imt, self.th, self.hc_perc, self.intTh)
        print '------------------------------'

    def selTimeWindow(self, event):
        """
        """
        self.tw = int(self.ctw.GetSelection())

        print '----------selTimeWindow-------------'
        self.th = scientLibs.prob_thr(self.RP,
                                      self.dtime[self.haz_sel][self.tw])
        print 'time:', self.dtime[self.haz_sel][self.tw]
        ntry = int(math.floor(self.npts * 0.5))
        tmp2 = self.hc[self.haz_sel][self.tw][0][ntry]
        tmp = sum([float(j) for j in tmp2.split()])
        if (tmp == 0):
            busydlg = wx.BusyInfo("...Reading hazard from DB")
            wx.Yield()
            db.dbReadHC(self.haz_sel, self.tw, self.dtime, self.cur, self.hc,
                        self.hc_perc)
            busydlg = None

        self.zmap = self.pn1.hazardMap(
            self.hc,
            self.lon,
            self.lat,
            self.id_area,
            self.nareas,
            self.npts,
            self.hazards,
            self.dtime,
            self.haz_sel,
            self.tw,
            self.th,
            self.intTh,
            self.perc,
            self.imgpath,
            self.limits,
            self.iml,
            self.imt)

        self.pn2.hazardCurve(self.hc, self.haz_sel, self.tw, self.hazards,
                             self.dtime, self.pt_sel, self.perc, self.iml,
                             self.imt, self.th, self.hc_perc, self.intTh)
        print '------------------------------'

    def selReturnPeriod(self, event):
        """
        """
        print '---------selReturnPeriod--------------'
        self.RP = float(self.cpth.GetValue())
        self.th = scientLibs.prob_thr(self.RP,
                                      self.dtime[self.haz_sel][self.tw])

        self.zmap = self.pn1.hazardMap(
            self.hc,
            self.lon,
            self.lat,
            self.id_area,
            self.nareas,
            self.npts,
            self.hazards,
            self.dtime,
            self.haz_sel,
            self.tw,
            self.th,
            self.intTh,
            self.perc,
            self.imgpath,
            self.limits,
            self.iml,
            self.imt)
        self.pn2.hazardCurve(self.hc, self.haz_sel, self.tw, self.hazards,
                             self.dtime, self.pt_sel, self.perc, self.iml,
                             self.imt, self.th, self.hc_perc, self.intTh)
        print '------------------------------'

    def selIntensityTh(self, event):
        """
        """
        print '---------selProbThreshold--------------'
        self.intTh = float(self.cith.GetValue())

        self.zmap = self.pn1.hazardMap(
            self.hc,
            self.lon,
            self.lat,
            self.id_area,
            self.nareas,
            self.npts,
            self.hazards,
            self.dtime,
            self.haz_sel,
            self.tw,
            self.th,
            self.intTh,
            self.perc,
            self.imgpath,
            self.limits,
            self.iml,
            self.imt)
        self.pn2.hazardCurve(self.hc, self.haz_sel, self.tw, self.hazards,
                             self.dtime, self.pt_sel, self.perc, self.iml,
                             self.imt, self.th, self.hc_perc, self.intTh)
        print '------------------------------'

    def openAddDB(self, event):
        """
        Opening a new window frame on top of the main window.
        This frame contains input forms to fill in in order to load data from
        single files. Data files must be prepared with specific rules.
        ...
        ...
        """
        pass

    def openCreateDB(self, event):
        """
        Opening a new window frame on top of the main window.
        This frame contains input forms to fill in in order to load data from
        single files. Data files must be prepared with specific rules.
        ...
        ...
        """

        self.fr = wx.Frame(self, title="DB Creation Input")
        hbox = wx.BoxSizer(orient=wx.HORIZONTAL)

        # left vertical sizer
        vbox1 = wx.BoxSizer(orient=wx.VERTICAL)

        # loading lat, lon, id_area 3-cols ascii file
        vbox_geo = wx.StaticBoxSizer(
            wx.StaticBox(
                self.fr,
                wx.ID_ANY,
                'Geographical grid data'),
            orient=wx.VERTICAL)
        txt = ("Load a 3-column ascii file having latitude\n"
               "(1st col) and longitude (2nd col) of each spatial\n"
               "point and the corresponding ID area (3rd col).")
        vbox_geo.Add(wx.StaticText(self.fr, wx.ID_ANY, label=txt,
                                   size=(-1, -1)), 0, wx.TOP, 5)

        hbox_pt = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.gridfile = wx.TextCtrl(self.fr, wx.ID_ANY, size=(200, 24))
        self.gridfile.SetValue(self.gridpath)
        hbox_pt.Add(self.gridfile, 0, wx.TOP, 4)
        self.ptbut = wx.Button(
            self.fr, wx.ID_ANY, "Select File", size=(-1, 26))
        self.Bind(wx.EVT_BUTTON, self.selGridFile, self.ptbut)
        hbox_pt.Add(self.ptbut, 0, wx.LEFT, 5)

        self.label_ptbut = wx.StaticText(self.fr, wx.ID_ANY, label="",
                                         size=(-1, -1))
        hbox_pt.Add(self.label_ptbut, 0, wx.TOP | wx.LEFT, 10)

        vbox_geo.Add(hbox_pt)

        # loading background map box
        vbox_map = wx.StaticBoxSizer(
            wx.StaticBox(
                self.fr,
                wx.ID_ANY,
                'Background Image Map and Limits (UTM)'),
            orient=wx.VERTICAL)
        hbox1 = wx.BoxSizer(orient=wx.HORIZONTAL)
        hbox1.Add(wx.StaticText(self.fr, wx.ID_ANY, label="Latitude Min (m):",
                                size=(140, -1),
                                style=wx.ALIGN_LEFT | wx.TE_WORDWRAP),
                  0, wx.ALIGN_BOTTOM | wx.LEFT | wx.TOP, 2)
        self.lat_min = wx.TextCtrl(self.fr, wx.ID_ANY, "4449200",
                                   size=(120, -1))
        hbox1.Add(self.lat_min, 0, wx.ALIGN_BOTTOM | wx.LEFT | wx.TOP, 2)

        hbox2 = wx.BoxSizer(orient=wx.HORIZONTAL)
        hbox2.Add(wx.StaticText(self.fr, wx.ID_ANY, label="Latitude Max (m):",
                                size=(140, -1),
                                style=wx.ALIGN_LEFT | wx.TE_WORDWRAP),
                  0, wx.ALIGN_BOTTOM | wx.LEFT | wx.TOP, 2)
        self.lat_max = wx.TextCtrl(self.fr, wx.ID_ANY, "4569800",
                                   size=(120, -1))
        hbox2.Add(self.lat_max, 0, wx.ALIGN_BOTTOM | wx.LEFT | wx.TOP, 2)

        hbox3 = wx.BoxSizer(orient=wx.HORIZONTAL)
        hbox3.Add(wx.StaticText(self.fr, wx.ID_ANY, label="Longitude Min (m):",
                                size=(140, -1),
                                style=wx.ALIGN_LEFT | wx.TE_WORDWRAP),
                  0, wx.ALIGN_BOTTOM | wx.LEFT | wx.TOP, 2)
        self.lon_min = wx.TextCtrl(
            self.fr, wx.ID_ANY, "375300", size=(120, -1))
        hbox3.Add(self.lon_min, 0, wx.ALIGN_BOTTOM | wx.LEFT | wx.TOP, 2)

        hbox4 = wx.BoxSizer(orient=wx.HORIZONTAL)
        hbox4.Add(wx.StaticText(self.fr, wx.ID_ANY, label="Longitude Max (m):",
                                size=(140, -1),
                                style=wx.ALIGN_LEFT | wx.TE_WORDWRAP),
                  0, wx.ALIGN_BOTTOM | wx.LEFT | wx.TOP, 2)
        self.lon_max = wx.TextCtrl(
            self.fr, wx.ID_ANY, "508500", size=(120, -1))
        hbox4.Add(self.lon_max, 0, wx.ALIGN_BOTTOM | wx.LEFT | wx.TOP, 2)

        hbox5 = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.loadmap = wx.Button(self.fr, wx.ID_ANY, "Upload Map",
                                 size=(-1, 28))
        self.Bind(wx.EVT_BUTTON, self.uploadMap, self.loadmap)
        hbox5.Add(self.loadmap, 0, wx.LEFT | wx.ALIGN_BOTTOM, 2)
        self.conf_map = wx.StaticText(self.fr, wx.ID_ANY, label="",
                                      size=(-1, -1))
        hbox5.Add(self.conf_map, 0, wx.ALIGN_CENTER | wx.LEFT, 5)

        vbox_map.Add(hbox1, 0, wx.ALL, 1)
        vbox_map.Add(hbox2, 0, wx.ALL, 1)
        vbox_map.Add(hbox3, 0, wx.ALL, 1)
        vbox_map.Add(hbox4, 0, wx.ALL, 1)
        vbox_map.Add(hbox5, 0, wx.ALL, 1)

        vbox_con = wx.StaticBoxSizer(
            wx.StaticBox(
                self.fr,
                wx.ID_ANY,
                'Database Connection'),
            orient=wx.VERTICAL)

        hbox1 = wx.BoxSizer(orient=wx.HORIZONTAL)
        hbox1.Add(wx.StaticText(self.fr, wx.ID_ANY, label="Server Name:",
                                size=(120, -1), style=wx.ALIGN_LEFT),
                  0, wx.ALIGN_BOTTOM | wx.LEFT | wx.TOP, 0)
        self.server = wx.TextCtrl(self.fr, wx.ID_ANY, "localhost",
                                  size=(120, -1))
        hbox1.Add(self.server, 0, wx.ALIGN_BOTTOM | wx.LEFT | wx.TOP, 0)

        hbox2 = wx.BoxSizer(orient=wx.HORIZONTAL)
        hbox2.Add(wx.StaticText(self.fr, wx.ID_ANY, label="User Name:",
                                size=(120, -1), style=wx.ALIGN_LEFT),
                  0, wx.ALIGN_BOTTOM | wx.LEFT | wx.TOP, 0)
        self.user = wx.TextCtrl(self.fr, wx.ID_ANY, "V1User", size=(120, -1))
        hbox2.Add(self.user, 0, wx.ALIGN_BOTTOM | wx.LEFT | wx.TOP, 0)

        hbox3 = wx.BoxSizer(orient=wx.HORIZONTAL)
        hbox3.Add(wx.StaticText(self.fr, wx.ID_ANY, label="Password:",
                                size=(120, -1), style=wx.ALIGN_LEFT),
                  0, wx.ALIGN_BOTTOM | wx.LEFT | wx.TOP, 0)
        self.pwd = wx.TextCtrl(self.fr, wx.ID_ANY, "V1Pwd",
                               size=(120, -1), style=wx.TE_PASSWORD)
        hbox3.Add(self.pwd, 0, wx.ALIGN_BOTTOM | wx.LEFT | wx.TOP, 0)

        hbox4 = wx.BoxSizer(orient=wx.HORIZONTAL)
        hbox4.Add(wx.StaticText(self.fr, wx.ID_ANY, label="Database Name:",
                                size=(120, -1), style=wx.ALIGN_LEFT),
                  0, wx.ALIGN_BOTTOM | wx.LEFT | wx.TOP, 0)
        self.dbname = wx.TextCtrl(self.fr, wx.ID_ANY, "DPC-V1-DB",
                                  size=(120, -1))
        hbox4.Add(self.dbname, 0, wx.ALIGN_BOTTOM | wx.LEFT | wx.TOP, 0)

        vbox_con.Add(hbox1, 0, wx.ALL, 3)
        vbox_con.Add(hbox2, 0, wx.ALL, 3)
        vbox_con.Add(hbox3, 0, wx.ALL, 3)
        vbox_con.Add(hbox4, 0, wx.ALL, 3)

        # right vertical sizer
        vbox2 = wx.BoxSizer(orient=wx.VERTICAL)

        self.vbox_haz = wx.StaticBoxSizer(
            wx.StaticBox(
                self.fr,
                wx.ID_ANY,
                'Hazard'),
            orient=wx.VERTICAL)

        self.vbox_haz.Add(wx.StaticText(self.fr, wx.ID_ANY,
                                        label="Select hazard files directory:",
                                        size=(-1, -1),
                                        style=wx.ALIGN_LEFT | wx.TE_WORDWRAP),
                          0, wx.TOP, 5)

        hbox_h1 = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.hazpath = wx.TextCtrl(self.fr, wx.ID_ANY, size=(200, 24))
        self.hazpath.SetValue(self.srcdir)
        hbox_h1.Add(self.hazpath, 0, wx.TOP, 2)
        self.bsel = wx.Button(self.fr, wx.ID_ANY, "Select Path", size=(-1, 26))
        self.Bind(wx.EVT_BUTTON, self.selHazPath, self.bsel)
        hbox_h1.Add(self.bsel, 0, wx.LEFT, 5)
        self.vbox_haz.Add(hbox_h1)

        self.vbox_haz.Add(wx.StaticText(self.fr, wx.ID_ANY,
                                        label="Insert percentile single values or ranges:",
                                        size=(-1, -1)), 0, wx.TOP, 5)
        self.percentiles = wx.TextCtrl(self.fr, wx.ID_ANY, size=(300, -1))
        self.percentiles.SetValue("10:90:10")
        self.vbox_haz.Add(self.percentiles, 0, wx.TOP, 2)
        txt_perc = ("Ex: 10,50,90 for single values or 5:100:5\n"
                    "for range from 5 to 100 with a step of 5")
        self.perc_lbl = wx.StaticText(self.fr, wx.ID_ANY, label=txt_perc,
                                      size=(-1, -1))
        self.vbox_haz.Add(self.perc_lbl, 0, wx.TOP, 5)

        vbox1.Add(vbox_geo, 0, wx.EXPAND | wx.ALL, 5)
        vbox1.Add(vbox_map, 0, wx.EXPAND | wx.ALL, 5)
        vbox1.Add(vbox_con, 1, wx.EXPAND | wx.ALL, 5)
        vbox2.Add(self.vbox_haz, 0, wx.EXPAND | wx.ALL, 5)

        hbox_bot = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.canc_button = wx.Button(self.fr, wx.ID_ANY, "Cancel",
                                     size=(-1, 28))
        self.Bind(wx.EVT_BUTTON, self.closeInputFr, self.canc_button)
        hbox_bot.Add(self.canc_button, 0, wx.TOP | wx.ALIGN_CENTRE, 10)
        self.save_button = wx.Button(self.fr, wx.ID_ANY, "Create",
                                     size=(-1, 28))
        self.Bind(wx.EVT_BUTTON, self.createDB, self.save_button)
        hbox_bot.Add(self.save_button, 0, wx.TOP | wx.ALIGN_CENTRE, 10)

        vbox2.Add(hbox_bot, 1, wx.EXPAND | wx.ALL, 5)
        hbox.Add(vbox1, 1, wx.EXPAND | wx.ALL, 5)
        hbox.Add(vbox2, 1, wx.EXPAND | wx.ALL, 5)

        self.fr.Bind(wx.EVT_CLOSE, self.closeInputFr)
        self.fr.SetSizer(hbox)
        self.fr.SetSize((680, 420))
        self.fr.Fit()
        self.fr.Centre()
        self.fr.Show(True)

    def createDB(self, event):
        """
        Using data provided by the input form (see openCreateDB function)
        to create Tables in Bymur DB and populate them.

        NOTA: STO SUPPONENDO CHE L'UTENTE PREPARI UNA STRUTTURA AD ALBERO
        GERARCHICA DEI DATI :

        cartella_hazard/
            |--hazard1/
               |--model1/
                  |--time1/
                  |--time2/
                  |--time3/
               |--model2/
                  |--time1/
                  |--time2/
                  |--time3/
            |--hazard2/
            |--hazard3/

        NB: ogni hazard puo' avere una quantita' diversa di modelli (minimo uno),
            e invece suppongo che i tempi di ricorrenza (time1,time2...) siano
            gli stessi per ogni modello
        """

        gridpath = str(self.gridfile.GetValue())       # grid file path

        # image map limits
        self.limits = [float(self.lon_min.GetValue()) / 1000,
                       float(self.lon_max.GetValue()) / 1000,
                       float(self.lat_min.GetValue()) / 1000,
                       float(self.lat_max.GetValue()) / 1000]

        # getting the hazard directory and subdirectories
        hpath = str(self.hazpath.GetValue())
        self.hazards = os.listdir(hpath)
        self.models = []
        self.dtime = []
        self.dtimefold = []
        for ind, haz in enumerate(self.hazards):
            print 'hpath-->', hpath
            print 'haz-->', haz
            self.models.append(os.listdir(os.path.join(hpath, haz)))
            for mod in self.models[ind]:
                if (os.listdir(os.path.join(hpath, haz, mod))):
                    # JACOPO 18.06.2013
                    tmp = os.listdir(os.path.join(hpath, haz, mod))
                    self.dtimefold.append(tmp)

                    dtime_tmp = [str(tmp[i].replace("dt", "")).zfill(3)
                                 for i in range(len(tmp))]
                    self.dtime.append(dtime_tmp)

        self.nt = max([len(self.dtime[i]) for i in range(len(self. dtime))])
        print self.hazards
        print self.models
        print self.dtime

        percpattern = str(self.percentiles.GetValue())  # selected percentiles

        if (percpattern.find(":") != -1):
            ii, ff, dd = percpattern.split(":")
            self.perc = range(int(ii), int(ff) + int(dd), int(dd))
        elif (percpattern.find(",") != -1):
            val = percpattern.split(",")
            self.perc = [int(val[i]) for i in range(len(val))]
        else:
            msg = ("ERROR\nInput in percentiles field is not correct")
            gf.showErrorMessage(self, msg, "ERROR")
            self.fr.Raise()
            return

        self.nperc = len(self.perc)

        # database data connection
        server = self.server.GetValue()
        user = self.user.GetValue()
        pwd = self.pwd.GetValue()
        dbname = self.dbname.GetValue()
        self.fr.Destroy()
        self.con, self.cur = db.dbConnection(server, user, pwd, dbname)

        # opening pop-up frame
        busydlg = wx.BusyInfo("Task has been processing.. please wait",
                              parent=self)
        wx.Yield()

        # comment the following two lines if DB tables exist and are populated
        db.dbCreateTables(self.con, self.cur, self.perc, self.hazards,
                          self.models)
        db.dbGenInfoPop(self.con, self.cur, self.imgpath, self.limits)
        self.npts = db.dbSpatDataPop(self.con, self.cur, gridpath)
        db.dbHazTabPop(
            self.con,
            self.cur,
            self.perc,
            self.hazards,
            self.models,
            self.dtime,
            hpath,
            self.npts,
            self.dtimefold)

        busydlg = None    # closing waiting pop-up frame
        self.sb.SetStatusText("DPC-V1-DB Database successfully created")

    def openLoadDB(self, event):
        """
        Opening a pop-up form to set the connection to the bymurDB (MySQL).
        By pressing the Connect Button it will be launched the connectDB()
        """

        self.conFr = wx.Frame(self)
        vbox = wx.BoxSizer(orient=wx.VERTICAL)

        hbox1 = wx.BoxSizer(orient=wx.HORIZONTAL)
        hbox1.Add(wx.StaticText(self.conFr, wx.ID_ANY, label="Server Name:",
                                size=(120, -1), style=wx.ALIGN_LEFT),
                  0, wx.ALIGN_BOTTOM | wx.LEFT | wx.TOP, 0)
        self.server = wx.TextCtrl(self.conFr, wx.ID_ANY, "localhost",
                                  size=(120, -1))
        hbox1.Add(self.server, 0, wx.ALIGN_BOTTOM | wx.LEFT | wx.TOP, 0)

        hbox2 = wx.BoxSizer(orient=wx.HORIZONTAL)
        hbox2.Add(wx.StaticText(self.conFr, wx.ID_ANY, label="User Name:",
                                size=(120, -1), style=wx.ALIGN_LEFT),
                  0, wx.ALIGN_BOTTOM | wx.LEFT | wx.TOP, 0)

        self.user = wx.TextCtrl(
            self.conFr, wx.ID_ANY, "V1User", size=(120, -1))
        hbox2.Add(self.user, 0, wx.ALIGN_BOTTOM | wx.LEFT | wx.TOP, 0)

        hbox3 = wx.BoxSizer(orient=wx.HORIZONTAL)
        hbox3.Add(wx.StaticText(self.conFr, wx.ID_ANY, label="Password:",
                                size=(120, -1), style=wx.ALIGN_LEFT),
                  0, wx.ALIGN_BOTTOM | wx.LEFT | wx.TOP, 0)
        self.pwd = wx.TextCtrl(self.conFr, wx.ID_ANY, "V1Pwd",
                               size=(120, -1), style=wx.TE_PASSWORD)
        hbox3.Add(self.pwd, 0, wx.ALIGN_BOTTOM | wx.LEFT | wx.TOP, 0)

        hbox4 = wx.BoxSizer(orient=wx.HORIZONTAL)
        hbox4.Add(wx.StaticText(self.conFr, wx.ID_ANY, label="Database Name:",
                                size=(120, -1), style=wx.ALIGN_LEFT),
                  0, wx.ALIGN_BOTTOM | wx.LEFT | wx.TOP, 0)

        self.dbname = wx.TextCtrl(self.conFr, wx.ID_ANY, "DPC-V1-DB",
                                  size=(120, -1))
        hbox4.Add(self.dbname, 0, wx.ALIGN_BOTTOM | wx.LEFT | wx.TOP, 0)

        hbox5 = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.conDB = wx.Button(self.conFr, wx.ID_ANY, "Connect", size=(-1, 26))
        self.Bind(wx.EVT_BUTTON, self.getServerData, self.conDB)
        hbox5.Add(self.conDB, 0, wx.TOP, 10)

        vbox.Add(hbox1, 0, wx.ALL, 3)
        vbox.Add(hbox2, 0, wx.ALL, 3)
        vbox.Add(hbox3, 0, wx.ALL, 3)
        vbox.Add(hbox4, 0, wx.ALL, 3)
        vbox.Add(hbox5, 0, wx.ALL | wx.ALIGN_RIGHT, 3)

        self.conFr.SetSizer(vbox)
        self.conFr.Fit()
        self.conFr.Center()
        self.conFr.Show(True)

    def getServerData(self, event):
        """
        """
        server = self.server.GetValue()
        user = self.user.GetValue()
        pwd = self.pwd.GetValue()
        dbname = self.dbname.GetValue()
        self.conFr.Destroy()
        self.con, self.cur = db.dbConnection(server, user, pwd, dbname)
        self.loadDB()

    def loadDB(self):
        """
        Opening a pop-up form to set the connection to the bymurDB (MySQL).
        By pressing the Connect Button it will be launched the connectDB()
        """

        self.pn1.Enable(True)
        self.pnl_curves.Enable(True)

        # opening waiting pop-up frame
        busydlg = wx.BusyInfo(
            "Task has been processing.. please wait", parent=self)
        wx.Yield()

        # all data stored in DB are loaded in numpy arrays
        tmp = db.dbReadTable(self.con, self.cur, "spatial_data1")
        self.npts = len(tmp)
        self.id_area = [int(tmp[i][1]) for i in range(self.npts)]
        self.lon = [float(tmp[i][2]) / 1000 for i in range(self.npts)]
        self.lat = [float(tmp[i][3]) / 1000 for i in range(self.npts)]
        self.nareas = len(self.id_area)

        tmp = db.dbReadTable(self.con, self.cur, "hazard_phenomena")
        self.nhaz = len(tmp)
        print 'tmp->', tmp
        self.hz_name = [tmp[i][4] for i in range(self.nhaz)]
        self.model = [tmp[i][5] for i in range(self.nhaz)]
        self.imt = [tmp[i][6] for i in range(self.nhaz)]
        self.iml = [[float(j) for j in tmp[i][7].split()]
                    for i in range(self.nhaz)]

        niml = max([len(self.iml[i]) for i in range(self.nhaz)])

        self.dtime = []
        for k in range(self.nhaz):
            hazmodtb = "hazard" + str(k + 1)
            tmp = db.dbSelectDtime(self.con, self.cur, hazmodtb)
            dtlist = [str(tmp[i][0]) for i in range(len(tmp))]
            self.dtime.append(dtlist)
        print "dtime = ", self.dtime
        self.nt = max([len(self.dtime[i]) for i in range(len(self.dtime))])


        for k in range(self.nhaz):
            if (len(self.iml[k]) < niml):
                for i in range(niml - len(self.iml[k])):
                    self.iml[k].append(0)

        self.hc = [[[['0' for i in range(self.npts)] for j in range(100)]
                    for k in range(self.nt)] for h in range(self.nhaz)]

        print 'niml=', niml
        self.hc_perc = list()
        for k in range(self.nhaz):
            self.hc_perc.append(0)

        self.perc_flag = []
        for i in range(self.nhaz):
            haznametb = "hazard" + str(i + 1)
            self.perc_flag.append(db.dbAssignFlagPerc(self.con,
                                                      self.cur, haznametb))

        print("FLAGS PERCENTILES = {0}".format(self.perc_flag))

        if (gf.verifyInternetConn()):
            srcdir = os.path.dirname(os.path.realpath(__file__))
            savepath = os.path.join(srcdir, "data", "naples_gmaps.png")
            utm_zone = "33N"
            self.imgpath = gmaps.getUrlGMaps(375300, 4449200,
                                             508500, 4569800,
                                             utm_zone, savepath)

        self.th = scientLibs.prob_thr(self.RP,
                                      self.dtime[self.haz_sel][self.tw])
        self.hc = db.dbReadHC(self.haz_sel, self.tw, self.dtime, self.cur,
                              self.hc, self.hc_perc)

        self.zmap = self.pn1.hazardMap(
            self.hc,
            self.lon,
            self.lat,
            self.id_area,
            self.nareas,
            self.npts,
            self.hazards,
            self.dtime,
            self.haz_sel,
            self.tw,
            self.th,
            self.intTh,
            self.perc,
            self.imgpath,
            self.limits,
            self.iml,
            self.imt)

        self.pn2.hazardCurve(self.hc, self.haz_sel, self.tw, self.hazards,
                             self.dtime, self.pt_sel, self.perc, self.iml,
                             self.imt, self.th, self.hc_perc, self.intTh)

        self.map_export_gis.Enable(True)

        self.chaz.Clear()
        for i in range(self.nhaz):
            #  item = self.hz_name[i] + " - " + self.model[i]
            item = self.model[i]
            self.chaz.Append(item)

        self.chaz.SetSelection(0)

        self.pnl_lt.Enable(True)

        self.ensemble_item.Enable(True)

        self.sb.SetStatusText("DPC-V1-DB Database successfully loaded")

    def closeInputFr(self, event):
        self.fr.Destroy()
        msg = ("WARNING\nYou are leaving the input procedure")
        gf.showWarningMessage(self, msg, "WARNING")
        return

    def defineModels(self, event):

        nh = int(event.GetSelection()) + 1

        if (self.vbox_models.GetChildren()):
            for child in self.vbox_models.GetChildren():
                self.vbox_models.Remove(child.Sizer)
                self.fr.Layout()

        for i in range(0, nh):
            hmsizer = wx.BoxSizer(orient=wx.HORIZONTAL)
            self.hmitem = wx.TextCtrl(self.fr, wx.ID_ANY, size=(200, 24))
            self.hmitem.SetValue("Hazard Model " + str(i + 1))
            hmsizer.Add(self.hmitem, 0, wx.TOP, 2)
            self.vbox_models.Add(hmsizer, 0, wx.ALL, 0)
            self.fr.Layout()
            self.fr.Fit()

    def selGridFile(self, event):

        path = gf.selFile(self, event)
        if (path == ""):
            return
        else:
            self.gridfile.SetValue(path)
            self.fr.Raise()

    def selHazPath(self, event):

        path = gf.selDir(self, event)
        if (path == ""):
            return
        else:
            self.hazpath.SetValue(path)
            self.fr.Raise()

    def confAct(self, *kargs):
        """
        Setting an 'OK' label after a successfully action
        """
        msg = kargs[0]
        msg.SetLabel("OK")
        msg.SetForegroundColour((0, 80, 0))
        font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                       wx.FONTWEIGHT_BOLD)
        msg.SetFont(font)

    def uploadMap(self, event, *args):
        """
        Uploading image file used as background image for hazard maps
        At the moment, it works with .png files only
        """

        dfl_dir = os.path.expanduser("~")
        dlg = wx.FileDialog(self, message="Upload Map", defaultDir=dfl_dir,
                            defaultFile="", wildcard="*.*", style=wx.OPEN)

        if (dlg.ShowModal() == wx.ID_OK):
            self.imgpath = str(dlg.GetPath())

            if (self.imgpath):
                ext = self.imgpath[-3:]

                if (ext != "png"):
                    msg = ("ERROR:\nYou can upload .png file "
                           "format only.")
                    gf.showErrorMessage(self, msg, "ERROR")
                    dlg.Destroy()
                    self.fr.Raise()
                    return

                self.confAct(self.conf_map)
                self.Layout()
                dlg.Destroy()

            else:
                msg = ("ERROR:\nImage path is wrong.")
                gf.showErrorMessage(self, msg, "ERROR")
                dlg.Destroy()
                self.fr.Raise()
                return

    def show_bld_tab(self, event):
        self.tab = OpenTable(self, wx.ID_ANY, "Table", self.buildings)
        print self.vh

    def on_quit(self, event):
         # db.dbClose(self.cur)
        self.Destroy()

    def openEnsembleFr(self, event):

        self.fr = wx.Frame(self, title="Ensable Selection")

        vbox = wx.BoxSizer(orient=wx.VERTICAL)
        txt1 = ("Chose among the list of possible hazard models\n"
                "here below the ones you would like to use to\n"
                "calculate the ensable hazard.")
        vbox.Add(wx.StaticText(self.fr, wx.ID_ANY, label=txt1, size=(-1, -1)),
                 0, wx.TOP, 5)

        self.hazname = [""] * self.nhaz
        self.hazweight = [""] * self.nhaz
        self.dtshared = []
        print self.nhaz
        print self.model
        print self.dtime

        for i in range(self.nhaz):

            hbox_haz = wx.BoxSizer(orient=wx.HORIZONTAL)
            self.hazname[i] = wx.CheckBox(self.fr, wx.ID_ANY,
                                          label=self.model[i], size=(-1, -1))
            hbox_haz.Add(self.hazname[i], 0, wx.TOP | wx.LEFT, 4)
            haz_id = self.hazname[i].GetId()
            self.Bind(wx.EVT_CHECKBOX, self.selectModel, self.hazname[i])
            self.hazweight[i] = wx.TextCtrl(self.fr, wx.ID_ANY, size=(80, 24))
            self.hazweight[i].SetValue("1")
            hbox_haz.Add(self.hazweight[i], 0, wx.LEFT, 4)
            vbox.Add(hbox_haz, 1, wx.EXPAND | wx.ALL, 5)
            self.hazweight[i].Enable(False)

        txt2 = ("Chose the time interval:")
        vbox.Add(wx.StaticText(self.fr, wx.ID_ANY, label=txt2, size=(-1, -1)),
                 0, wx.TOP, 5)

        hbox_dt = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.dt_sel = wx.ComboBox(self.fr, wx.ID_ANY, choices=self.dtshared,
                                  style=wx.CB_READONLY, size=(-1, -1))
        hbox_dt.Add(self.dt_sel, 0, wx.TOP | wx.ALIGN_CENTRE, 10)
        # self.Bind(wx.EVT_COMBOBOX, self.boh, self.dt_sel)
        vbox.Add(hbox_dt, 1, wx.EXPAND | wx.ALL, 5)

        hbox_bot = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.canc_button = wx.Button(self.fr, wx.ID_ANY, "Cancel",
                                     size=(-1, 28))
        self.Bind(wx.EVT_BUTTON, self.closeInputFr, self.canc_button)
        hbox_bot.Add(self.canc_button, 0, wx.TOP | wx.ALIGN_CENTRE, 10)
        self.save_button = wx.Button(self.fr, wx.ID_ANY, "Create",
                                     size=(-1, 28))
        self.Bind(wx.EVT_BUTTON, self.ensemble_do, self.save_button)
        hbox_bot.Add(self.save_button, 0, wx.TOP | wx.ALIGN_CENTRE, 10)

        vbox.Add(hbox_bot, 1, wx.EXPAND | wx.ALL, 5)

        self.fr.Bind(wx.EVT_CLOSE, self.closeInputFr)
        self.fr.SetSizer(vbox)
        # self.fr.SetSize((680,420))
        self.fr.Fit()
        self.fr.Centre()
        self.fr.Show(True)

    def selectModel(self, event, *kargs):
        self.dtshared = []
        for i in range(self.nhaz):
            if self.hazname[i].IsChecked():
                self.hazweight[i].Enable(True)
                self.dtshared.append(self.dtime[i])
            else:
                self.hazweight[i].Enable(False)

        nsel = len(self.dtshared)
        if (nsel > 1):
            tmp = list(set(self.dtshared[0]) & set(self.dtshared[1]))
            for j in range(2, nsel):
                tmp = list(set(tmp) & set(self.dtshared[j]))
            print tmp
            self.dt_sel.SetItems(tmp)

    def closeEnsembleFr(self, event):
        self.fr.Destroy()
        msg = ("WARNING\nYou are leaving the ensemble procedure")
        gf.showWarningMessage(self, msg, "WARNING")
        return

    def ensemble_do(self, event):
        # selection of models and weights

        self.fr.Destroy()

        self.selected = []
        self.weights = []

        dtsel = self.dt_sel.GetValue()
        self.twsel = []
        for i in range(self.nhaz):
            if self.hazname[i].IsChecked():
                self.selected.append(int(i))
                self.weights.append(float(self.hazweight[i].GetValue()))
                tmp = self.dtime[i].index(dtsel)
                self.twsel.append(tmp)
            else:
                pass

        print self.selected

        print self.hc_perc
        self.percsel = range(10, 100, 10)

        print "TWSEL", self.tw, self.twsel

        # opening waiting pop-up frame
        busydlg = wx.BusyInfo("Task has been processing.. please wait")
        wx.Yield()

        # update from db
        for i in range(len(self.selected)):
            ntry = int(math.floor(self.npts * 0.5))
            tmp2 = self.hc[self.selected[i]][self.twsel[i]][0][ntry]
            tmp = sum([float(j) for j in tmp2.split()])
            if (tmp == 0):
                busydlg = wx.BusyInfo("...Reading hazard from DB")
                wx.Yield()
                db.dbReadHC(self.selected[i], self.twsel[i], self.dtime,
                            self.cur, self.hc, self.hc_perc)
                busydlg = None

        # do ensemble

        self.sb.SetStatusText("... generating ensemble model")
        tmp = scientLibs.ensemble(self.hc, self.hc_perc, self.tw, self.hazards,
                                  self.dtime, self.selected, self.weights,
                                  self.twsel, self.percsel, self.perc_flag)

        hccomb = [[['0' for i in range(self.npts)] for j in range(100)]
                  for k in range(self.nt)]
        for i in range(self.npts):
            for j in range(100):
                hccomb[0][j][i] = ' '.join(map(str, tmp[0, j, i][:]))

        # update DB, table hazard_phenomena
        self.sb.SetStatusText("... updating DB")
        nmod_comb = len(self.selected)
        ntw = 1
        self.nhaz = self.nhaz + 1
        tmpid = self.nhaz
        tmpname = self.hz_name[self.selected[0]]
        tmpmodel = "EN:"
        for i in range(nmod_comb):
            tmpmodel = tmpmodel + str(self.model[self.selected[i]]) + "("
            tmpmodel = tmpmodel + str(self.weights[i]) + ");"  # ID in DB

        tmpmodel = tmpmodel + "_T:"
        tmpmodel = tmpmodel + str(self.dtime[self.
                                             selected[0]][self.twsel[0]]) + ";"
        tmpimt = self.imt[self.selected[0]]
        tmp = self.iml[self.selected[0]]
        tmpiml = ' '.join(map(str, tmp[:]))

        sql = """
              INSERT INTO hazard_phenomena (id_haz,name,model,imt,iml,
              id_map_info, id_spatial_data, vd_ID)
              VALUES('{0}','{1}','{2}','{3}','{4}',1, 1, 0)
              """
        self.cur.execute(sql.format(tmpid, tmpname, tmpmodel, tmpimt, tmpiml))

        # update variables
        tmp = db.dbReadTable(self.con, self.cur, "hazard_phenomena")
        self.nhaz = len(tmp)
        self.hz_name = [tmp[i][4] for i in range(self.nhaz)]
        self.model = [tmp[i][5] for i in range(self.nhaz)]
        self.imt = [tmp[i][6] for i in range(self.nhaz)]
        self.iml = [[float(j) for j in tmp[i][7].split()]
                    for i in range(self.nhaz)]

        # update array hc & hc_perc
        hctmp = self.hc
        niml = len(self.iml[self.selected[0]])
        self.hc = [[[['0' for i in range(self.npts)] for j in range(100)]
                    for k in range(self.nt)] for h in range(self.nhaz)]
        for ihz in range(self.nhaz - 1):
            self.hc[ihz] = hctmp[ihz]
        self.hc[-1][0] = hccomb[0]

        self.hc_perc.append(np.asarray(self.percsel))

        # update DB, table hazard#
        tbname = "hazard" + str(self.nhaz)
        sql_query = """
                    CREATE TABLE IF NOT EXISTS {0}
                    (id INT UNSIGNED NOT NULL PRIMARY KEY, id_haz INT,
                    id_points INT, stat VARCHAR(20), dtime VARCHAR(20),
                    curve MEDIUMTEXT);
                    """
        self.cur.execute(sql_query.format(tbname))
        idc = 0
        dtimetmp = self.dtime
        nperc = len(self.hc[0][0]) - 1
        npts = len(self.hc[0][0][0])

        for iii in range(ntw):
            dt = self.dtime[self.selected[0]][self.twsel[0]]
            print 'dT= ', dt, ' yr'
            for i in range(npts):
                idc = idc + 1
                sql = """
                  INSERT INTO {0} (id, id_haz, id_points, stat,
                  dtime, curve) VALUES ( {1}, {2}, {3}, '{4}', '{5}', '{6}' )
                  """
                self.cur.execute(sql.format(tbname, idc, tmpid, i + 1,
                                            "Average", dt, hccomb[0][0][i]))
            for p in range(len(self.percsel)):
                pp = str(self.percsel[p])
                print('percsel[p]', self.percsel[p])
                for i in range(npts):
                    idc = idc + 1
                    sql = """
                      INSERT INTO {0} (id, id_haz, id_points, stat,
                      dtime, curve) VALUES
                      ( {1}, {2}, {3}, '{4}', '{5}', '{6}' )
                      """
                    self.cur.execute(
                        sql.format(
                            tbname,
                            idc,
                            tmpid,
                            i + 1,
                            "Perc" + pp,
                            dt,
                            hccomb[0][
                                self.percsel[p]][i]))
        print 'DB populated!!'


    # hazard tab
        self.perc_flag.append(db.dbAssignFlagPerc(self.con, self.cur, tbname))
        print("UPDATE FLAGS PERCENTILES = {0}".format(self.perc_flag))

        item = tmpmodel

        self.chaz.Append(item)

        busydlg = None    # closing waiting pop-up frame
        self.sb.SetStatusText("... ensemble model evaluated")

        print 'Task completed!!'
        print '------------------------------'



class BymurGui(wx.App):

    """
    Instance of the main class BymurFrame
    """

    def OnInit(self):
        frame = BymurFrame(None, -1, "V1 - BYMUR")
        frame.Show(True)
        self.SetTopWindow(frame)
        frame.Centre()
        return True


# starting the main gui
if __name__ == "__main__":
    app = BymurGui(0)
    app.MainLoop()
