#!/usr/bin/env python1
# -*- coding: utf-8 -*-

'''
  Bymur Software computes Risk and Multi-Risk associated to Natural Hazards.
  In particular this tool aims to provide a final working application for
  the city of Naples, considering three natural phenomena, i.e earthquakes,
  volcanic eruptions and tsunamis.
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
# import sys

# third-party modules
import wx
import numpy as np
import matplotlib as mlib
mlib.use('WX')
# from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as figcv
# from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as navtb

# from matplotlib.patches import Circle, Wedge, Rectangle
# from matplotlib.collections import PatchCollection
# from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import matplotlib.pyplot as plt

# sys.path.append('src')
import globalFunctions as gf
import dbFunctions as db
import getGMapsImg as gmaps
import plotLibs
# JACOPO 10/6/13
import scientLibs
import math
# import re
# END JACOPO 10/6/13


class BymurFrame(wx.Frame):

    """
    Main window frame of ByMuR software.
    """

    srcdir = os.path.dirname(os.path.realpath(__file__))
    # default values for some global variables
    pt_sel = 0           # selected point
    haz_sel = 0          # selected hazard phenomenon
    single_haz = True    # selected
    # JACOPO 10/06/13
    RP = 4975             # selected Return Period
    intTh = 3.0            # selected intensity threshold
    # END JACOPO 10/06/13
    tw = 0               # selected time window

    # defining some input
    hazards = ["Volcanic", "Seismic", "Tsunami"]           # hazard phenomena
    perc = range(1, 100)                                   # percentiles
    # dtime = ["1", "5", "10", "50"]                             # time windows
    # limits of image map
    limits = [375.300, 508.500, 4449.200, 4569.800]
    imgpath = os.path.join(srcdir, "data", "naples.png")   # image map path
    gridpath = os.path.join(
        srcdir, "data", "naples-grid.txt")  # image map path

    nhaz = len(hazards)
    nperc = len(perc)
    # nt = len(dtime)

    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition)
    #     self.SetIcon(wx.Icon("icons/", wx.BITMAP_TYPE_ANY))

        # menubar
        self.menuBar = wx.MenuBar()
        self.fileMenu = wx.Menu()
        self.dbMenu = wx.Menu()
        self.plotMenu = wx.Menu()

        load_db_item = wx.MenuItem(self.fileMenu, 102, '&Load DataBase')
        # quit_item.SetBitmap(wx.Bitmap('icons/exit.png'))
        self.fileMenu.AppendItem(load_db_item)
        self.Bind(wx.EVT_MENU, self.openLoadDB, id=102)
        self.fileMenu.AppendSeparator()

        load_bymurDBitem = wx.MenuItem(self.fileMenu, 103,
                                       '&Load remote ByMuR DB')
        # quit_item.SetBitmap(wx.Bitmap('icons/exit.png'))
        self.fileMenu.AppendItem(load_bymurDBitem)
        self.Bind(wx.EVT_MENU, self.loadBymurDB, id=103)
        self.fileMenu.AppendSeparator()

        # load_in_item = wx.MenuItem(self.fileMenu, 103, '&Load Input Files')
        # self.fileMenu.AppendItem(load_in_item)
        # self.Bind(wx.EVT_MENU, self.loadInputfiles, id=103)
        # self.fileMenu.AppendSeparator()

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

    # JACOPO 4/6/13
        self.analysisMenu = wx.Menu()
    # ROBERTO 13/06/2013
        # ensemble_item = wx.MenuItem(self.analysisMenu, 211,
        # 'Create &Ensemble hazard')
        self.ensemble_item = wx.MenuItem(self.analysisMenu, 211,
                                         'Create &Ensemble hazard')
        self.analysisMenu.AppendItem(self.ensemble_item)
        # self.analysisMenu.AppendItem(ensemble_item)
    # END ROBERTO 13/06/2013
        self.menuBar.Append(self.analysisMenu, '&Analysis')

    # ROBERTO 13/06/2013
        # self.Bind(wx.EVT_MENU, self.ensemble_do, id=211)
        self.Bind(wx.EVT_MENU, self.openEnsembleFr, id=211)
        self.ensemble_item.Enable(False)
    # END ROBERTO 13/06/2013
    # END JACOPO 4/6/13

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

        # self.rb1 = wx.RadioButton(self.pnl_lt, wx.ID_ANY, "Volcanic",
        # style=wx.RB_GROUP)
        # self.rb2 = wx.RadioButton(self.pnl_lt, wx.ID_ANY, "Seismic")
        # self.rb3 = wx.RadioButton(self.pnl_lt, wx.ID_ANY, "Tsunami")
        # self.rb1.SetValue(True)

        # self.Bind(wx.EVT_RADIOBUTTON, self.selHazard, self.rb1)
        # self.Bind(wx.EVT_RADIOBUTTON, self.selHazard, self.rb2)
        # self.Bind(wx.EVT_RADIOBUTTON, self.selHazard, self.rb3)

        # self.vbox_haz_rt.Add(self.rb1, 0, wx.TOP, 10)
        # self.vbox_haz_rt.Add(self.rb2, 0, wx.TOP, 10)
        # self.vbox_haz_rt.Add(self.rb3, 0, wx.TOP, 10)

        hbox_haz.Add(self.vbox_haz_lt, 0, wx.EXPAND | wx.ALL, 10)
        hbox_haz.Add(self.vbox_haz_rt, 0, wx.EXPAND | wx.ALL, 10)

    # ROBERTO 27/06/2013
    #    hbox_vul = wx.StaticBoxSizer(wx.StaticBox(self.pnl_lt, wx.ID_ANY,
    #                                 'Vulnerability'), orient=wx.HORIZONTAL)
    #    self.b_bld_tab = wx.Button(self.pnl_lt, wx.ID_ANY, 'Buildings Table')
    #    self.Bind(wx.EVT_BUTTON, self.show_bld_tab, self.b_bld_tab)
    #    hbox_vul.Add(self.b_bld_tab, 0, wx.ALIGN_BOTTOM|wx.TOP|wx.LEFT, 5)
    #    self.b_bld_tab.Disable()
    #
    #    hbox_exp = wx.StaticBoxSizer(wx.StaticBox(self.pnl_lt, wx.ID_ANY,
    #                                 'Exposure'), orient=wx.HORIZONTAL)
    #
    #    hbox_risk = wx.StaticBoxSizer(wx.StaticBox(self.pnl_lt, wx.ID_ANY,
    #                                  'Risk'), orient=wx.HORIZONTAL)
    # END ROBERTO 27/06/2013

        vbox_lt.Add(hbox_haz, 0, wx.EXPAND | wx.ALL, 5)
    # ROBERTO 27/06/2013
    #    vbox_lt.Add(hbox_vul, 0, wx.EXPAND|wx.ALL, 5)
    #    vbox_lt.Add(hbox_exp, 0, wx.EXPAND|wx.ALL, 5)
    #    vbox_lt.Add(hbox_risk, 0, wx.EXPAND|wx.ALL, 5)
    # END ROBERTO 27/06/2013

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
        # self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.on_tab_changed)
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

    # ROBERTO 26/09/2013
    def loadBymurDB(self, event):
        """
        """
        server = "***REMOVED***"
        user = "bymurUser"
        pwd = "bymurPwd"
        dbname = "bymurDB"
        self.con, self.cur = db.dbConnection(server, user, pwd, dbname)
        self.loadDB()

    # ROBERTO 26/09/2013

    # ROBERTO 27/06/2013
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

    # END ROBERTO 27/06/2013

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
    # JACOPO 3/5/13
    #        self.pn2.hazardCurve(self.hc, self.haz_sel, self.tw, self.hazards,
    #                             self.dtime, self.pt_sel, self.perc, self.iml,
    #                             self.imt)
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
    # FINE JACOPO 3/5/13
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
            # self.Layout()

        elif (sel == 2):
            self.nb.ChangeSelection(old)
            msg = ("WARNING:\nThis feature has not been implemented yet")
            gf.showWarningMessage(self, msg, "WARNING")
            return
            # self.Layout()

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
    # JACOPO 7/6/13
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
    # END JACOPO 7/6/13

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
    # JACOPO 3/6/13
    #    self.pn2.hazardCurve(self.hc, self.haz_sel, self.tw, self.hazards,
    #                         self.dtime, self.pt_sel, self.perc, self.iml,
    #                         self.imt)
        self.pn2.hazardCurve(self.hc, self.haz_sel, self.tw, self.hazards,
                             self.dtime, self.pt_sel, self.perc, self.iml,
                             self.imt, self.th, self.hc_perc, self.intTh)
        print '------------------------------'
    # FINE JACOPO 3/6/13

        # if (self.rb1.GetValue()):
        # self.haz_sel = 0
        # self.pn2.hazardCurve(self.hc, self.haz_sel, self.tw, self.hazards,
        # self.dtime, self.pt_sel, self.perc, self.iml,
        # self.imt)

        # elif (self.rb2.GetValue()):
        # self.haz_sel = 1
        # self.pn2.hazardCurve(self.hc, self.haz_sel, self.tw, self.hazards,
        # self.dtime, self.pt_sel, self.perc, self.iml,
        # self.imt)

        # elif (self.rb3.GetValue()):
        # self.haz_sel = 2
        # self.pn2.hazardCurve(self.hc, self.haz_sel, self.tw, self.hazards,
        # self.dtime, self.pt_sel, self.perc, self.iml,
        # self.imt)
        # else:
        # msg = ("ERROR\nHazard selection gave an unexpected error")
        # gf.showErrorMessage(self, msg, "ERROR")
        # self.fr.Raise()
        # return

    def selTimeWindow(self, event):
        """
        """
        self.tw = int(self.ctw.GetSelection())

    # JACOPO 10/6/13
        print '----------selTimeWindow-------------'
        self.th = scientLibs.prob_thr(self.RP,
                                      self.dtime[self.haz_sel][self.tw])
        print 'time:', self.dtime[self.haz_sel][self.tw]
        ntry = int(math.floor(self.npts * 0.5))
        tmp2 = self.hc[self.haz_sel][self.tw][0][ntry]
        tmp = sum([float(j) for j in tmp2.split()])
    #    if not tmp:
    #      print 'Model not available!!'
    #    else:
        if (tmp == 0):
            busydlg = wx.BusyInfo("...Reading hazard from DB")
            wx.Yield()
            db.dbReadHC(self.haz_sel, self.tw, self.dtime, self.cur, self.hc,
                        self.hc_perc)
            busydlg = None
    # END JACOPO 10/6/13

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

    # JACOPO 3/6/13
    #    self.pn2.hazardCurve(self.hc, self.haz_sel, self.tw, self.hazards,
    #                         self.dtime, self.pt_sel, self.perc, self.iml,
    #                         self.imt)
        self.pn2.hazardCurve(self.hc, self.haz_sel, self.tw, self.hazards,
                             self.dtime, self.pt_sel, self.perc, self.iml,
                             self.imt, self.th, self.hc_perc, self.intTh)
        print '------------------------------'
    # FINE JACOPO 3/6/13

    # ROBERTO 26.09.2013
    def selReturnPeriod(self, event):
        """
        """
    # JACOPO 10/6/13
        print '---------selReturnPeriod--------------'
        self.RP = float(self.cpth.GetValue())
        self.th = scientLibs.prob_thr(self.RP,
                                      self.dtime[self.haz_sel][self.tw])
    #    self.th = float(self.cth.GetValue())
    # FINE JACOPO 10/6/13

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
    # JACOPO 10/6/13
        self.pn2.hazardCurve(self.hc, self.haz_sel, self.tw, self.hazards,
                             self.dtime, self.pt_sel, self.perc, self.iml,
                             self.imt, self.th, self.hc_perc, self.intTh)
    # FINE JACOPO 10/6/13
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
    # END ROBERTO 26.09.2013

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
        # self.gridfile.SetValue("(Grid file path)")
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
        # self.hazpath.SetValue("(Directory path)")
        hbox_h1.Add(self.hazpath, 0, wx.TOP, 2)
        self.bsel = wx.Button(self.fr, wx.ID_ANY, "Select Path", size=(-1, 26))
        self.Bind(wx.EVT_BUTTON, self.selHazPath, self.bsel)
        hbox_h1.Add(self.bsel, 0, wx.LEFT, 5)
        self.vbox_haz.Add(hbox_h1)

        # hbox_h2 = wx.BoxSizer(orient=wx.HORIZONTAL)
        # hbox_h2.Add(wx.StaticText(self.fr, wx.ID_ANY,
        # label="Number of hazard models:",
        # size=(200,24)), 0, wx.TOP|wx.ALIGN_BOTTOM, 12)
        # self.nhazmod = wx.ComboBox(self.fr, wx.ID_ANY, pos=(-1, -1), size=(95, -1),
        # choices=["1", "2", "3", "4", "5"],
        # style=wx.CB_DROPDOWN)
        # self.Bind(wx.EVT_COMBOBOX, self.defineModels, self.nhazmod)
        # self.nhazmod = wx.SpinCtrl(self.fr, wx.ID_ANY, "1", min=1, max=120,
        # size=(60,26))
        # self.Bind(wx.EVT_SPINCTRL, self.spinModels, self.nhazmod)
        # hbox_h2.Add(self.nhazmod, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        # self.vbox_haz.Add(hbox_h2)

        # self.vbox_models = wx.BoxSizer(orient=wx.VERTICAL)
        # self.vbox_haz.Add(self.vbox_models)

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

        # hbox_vul = wx.StaticBoxSizer(wx.StaticBox(self.fr, wx.ID_ANY,
        # 'Vulnerability'), orient=wx.HORIZONTAL)

        # hbox_exp = wx.StaticBoxSizer(wx.StaticBox(self.fr, wx.ID_ANY,
        # 'Exposure'), orient=wx.HORIZONTAL)

        vbox1.Add(vbox_geo, 0, wx.EXPAND | wx.ALL, 5)
        vbox1.Add(vbox_map, 0, wx.EXPAND | wx.ALL, 5)
        vbox1.Add(vbox_con, 1, wx.EXPAND | wx.ALL, 5)
        vbox2.Add(self.vbox_haz, 0, wx.EXPAND | wx.ALL, 5)
        # vbox2.Add(hbox_vul, 1, wx.EXPAND|wx.ALL, 5)
        # vbox2.Add(hbox_exp, 1, wx.EXPAND|wx.ALL, 5)

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
    # ROBERTO 25/09/2013
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

    #          print 'tmp-->',tmp
    #          for itmp in range(len(tmp)):
    #             tmp2 = tmp[itmp]
    #             tmp3 = re.findall('\d+',tmp2)
    #             itmp3 = tmp3[0]
    #             tmp4 = str(itmp3).zfill(3)
    #             self.dtime[itmp] = tmp4
    #
    #          print 'dtime-->',self.dtime

    #          self.dtime = os.listdir(os.path.join(hpath,haz,mod))
    # JACOPO 18.06.2013
    # END ROBERTO 25/09/2013

    # ROBERTO 04.06.2013
        # self.nt = len(self.dtime)
        self.nt = max([len(self.dtime[i]) for i in range(len(self. dtime))])
    # END ROBERTO 04.06.2013
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

    # ROBERTO 04.06.2013
        self.nperc = len(self.perc)
    # END ROBERTO 04.06.2013

        # database data connection
        server = self.server.GetValue()
        user = self.user.GetValue()
        pwd = self.pwd.GetValue()
        dbname = self.dbname.GetValue()
        self.fr.Destroy()
        self.con, self.cur = db.dbConnection(server, user, pwd, dbname)
    # JACOPO 10/06/13
    #    self.cur = cur
    #    self.con = con
    # END JACOPO 10/06/13

        # opening pop-up frame
        busydlg = wx.BusyInfo("Task has been processing.. please wait",
                              parent=self)
        wx.Yield()

        # comment the following two lines if DB tables exist and are populated
        db.dbCreateTables(self.con, self.cur, self.perc, self.hazards,
                          self.models)
        db.dbGenInfoPop(self.con, self.cur, self.imgpath, self.limits)
        self.npts = db.dbSpatDataPop(self.con, self.cur, gridpath)
    # JACOPO 18/06/13
    #    db.dbHazTabPop(con, cur, self.perc, self.hazards, self.models, self.dtime,
    #                   hpath, self.npts)
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
    # FINE JACOPO 18/06/13

        busydlg = None    # closing waiting pop-up frame
    #    self.sb.SetStatusText("Bymur Database successfully created")
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
    #    self.user = wx.TextCtrl(self.conFr, wx.ID_ANY, "bymurUser", size=(120,-1))
    #    hbox2.Add(self.user, 0, wx.ALIGN_BOTTOM|wx.LEFT|wx.TOP, 0)
        self.user = wx.TextCtrl(
            self.conFr, wx.ID_ANY, "V1User", size=(120, -1))
        hbox2.Add(self.user, 0, wx.ALIGN_BOTTOM | wx.LEFT | wx.TOP, 0)

        hbox3 = wx.BoxSizer(orient=wx.HORIZONTAL)
        hbox3.Add(wx.StaticText(self.conFr, wx.ID_ANY, label="Password:",
                                size=(120, -1), style=wx.ALIGN_LEFT),
                  0, wx.ALIGN_BOTTOM | wx.LEFT | wx.TOP, 0)
    #    self.pwd = wx.TextCtrl(self.conFr, wx.ID_ANY, "bymurPwd",
    #                           size=(120,-1), style=wx.TE_PASSWORD)
        self.pwd = wx.TextCtrl(self.conFr, wx.ID_ANY, "V1Pwd",
                               size=(120, -1), style=wx.TE_PASSWORD)
        hbox3.Add(self.pwd, 0, wx.ALIGN_BOTTOM | wx.LEFT | wx.TOP, 0)

        hbox4 = wx.BoxSizer(orient=wx.HORIZONTAL)
        hbox4.Add(wx.StaticText(self.conFr, wx.ID_ANY, label="Database Name:",
                                size=(120, -1), style=wx.ALIGN_LEFT),
                  0, wx.ALIGN_BOTTOM | wx.LEFT | wx.TOP, 0)
    #    self.dbname = wx.TextCtrl(self.conFr, wx.ID_ANY, "bymurDB", size=(120,-1))
    #    hbox4.Add(self.dbname, 0, wx.ALIGN_BOTTOM|wx.LEFT|wx.TOP, 0)
        self.dbname = wx.TextCtrl(self.conFr, wx.ID_ANY, "DPC-V1-DB",
                                  size=(120, -1))
        hbox4.Add(self.dbname, 0, wx.ALIGN_BOTTOM | wx.LEFT | wx.TOP, 0)

        hbox5 = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.conDB = wx.Button(self.conFr, wx.ID_ANY, "Connect", size=(-1, 26))
    #    self.Bind(wx.EVT_BUTTON, self.loadDB, self.conDB)
        self.Bind(wx.EVT_BUTTON, self.getServerData, self.conDB)
        hbox5.Add(self.conDB, 0, wx.TOP, 10)

        vbox.Add(hbox1, 0, wx.ALL, 3)
        vbox.Add(hbox2, 0, wx.ALL, 3)
        vbox.Add(hbox3, 0, wx.ALL, 3)
        vbox.Add(hbox4, 0, wx.ALL, 3)
        vbox.Add(hbox5, 0, wx.ALL | wx.ALIGN_RIGHT, 3)

        # self.fr.Bind(wx.EVT_CLOSE, self.closeInputFr)
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

    #    server = self.server.GetValue()
    #    user = self.user.GetValue()
    #    pwd = self.pwd.GetValue()
    #    dbname = self.dbname.GetValue()
    #    self.conFr.Destroy()
    #    con, cur = db.dbConnection(server, user, pwd, dbname)
    # JACOPO 10/06/13
    #    self.cur = cur
    #    self.con = con
    # END JACOPO 10/06/13

        self.pn1.Enable(True)
        self.pnl_curves.Enable(True)

        # opening waiting pop-up frame
        busydlg = wx.BusyInfo(
            "Task has been processing.. please wait", parent=self)
        wx.Yield()

        # all data stored in DB are loaded in numpy arrays
        # tmp = db.dbReadTable(con, cur, "map_info")
        # self.imgpath = str(tmp[0][1])
        # self.limits = [float(tmp[0][i]) for i in [2,3,4,5]]

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

    # ROBERTO 25/09/2013
        self.dtime = []
        for k in range(self.nhaz):
            hazmodtb = "hazard" + str(k + 1)
            tmp = db.dbSelectDtime(self.con, self.cur, hazmodtb)
            dtlist = [str(tmp[i][0]) for i in range(len(tmp))]
            self.dtime.append(dtlist)
        print "dtime = ", self.dtime
        self.nt = max([len(self.dtime[i]) for i in range(len(self.dtime))])

    # END ROBERTO 25/09/2013

        for k in range(self.nhaz):
            if (len(self.iml[k]) < niml):
                for i in range(niml - len(self.iml[k])):
                    self.iml[k].append(0)

        # self.hc = np.zeros((self.nhaz, self.nt, self.nperc+1, self.npts, niml))
        self.hc = [[[['0' for i in range(self.npts)] for j in range(100)]
                    for k in range(self.nt)] for h in range(self.nhaz)]

    # JACOPO 11/6/13
        print 'niml=', niml
        self.hc_perc = list()
        for k in range(self.nhaz):
            self.hc_perc.append(0)
    # JACOPO 11/6/13

    # ROBERTO 11/09/2013
        self.perc_flag = []
        for i in range(self.nhaz):
            haznametb = "hazard" + str(i + 1)
            self.perc_flag.append(db.dbAssignFlagPerc(self.con,
                                                      self.cur, haznametb))

        print("FLAGS PERCENTILES = {0}".format(self.perc_flag))
    # END ROBERTO 11/09/2013

    # ROBERTO 19/09/2013
        if (gf.verifyInternetConn()):
            srcdir = os.path.dirname(os.path.realpath(__file__))
            savepath = os.path.join(srcdir, "data", "naples_gmaps.png")
            utm_zone = "33N"
            self.imgpath = gmaps.getUrlGMaps(375300, 4449200,
                                             508500, 4569800,
                                             utm_zone, savepath)
    #      self.imgpath = gmaps.getUrlGMaps(min(self.lon)*1000, min(self.lat)*1000,
    #                                       max(self.lon)*1000, max(self.lat)*1000,
    #                                       utm_zone, savepath)
    # END ROBERTO 19/09/2013

        self.th = scientLibs.prob_thr(self.RP,
                                      self.dtime[self.haz_sel][self.tw])
        self.hc = db.dbReadHC(self.haz_sel, self.tw, self.dtime, self.cur,
                              self.hc, self.hc_perc)
    #    print self.npts
    #    tbname = "hazard" + str(1)
    #    cmd = "SELECT stat FROM " + tbname + " WHERE dtime = 'dt" \
    #       + self.dtime[0] + "' AND stat != 'Average' AND id_points = 1"
    #    cur.execute(cmd)
    #    percall = cur.fetchall()
    # percsel = range(1,100) #[10,50,90]
    # hc[hsel][tw][perc][pt_sel][:]
    #    cmd = "SELECT id_points,curve FROM " + tbname + " WHERE dtime = 'dt" \
    #         + self.dtime[0] + "' AND stat = 'Average'"
    #    cur.execute(cmd)
    #    rows = cur.fetchall()
    #    for row in rows:
    #       ipoint = row[0]
    #       curvetmp = row[1].split()
    #       self.hc[0][0][0][ipoint-1] = curvetmp
    #
    #    for ipercsel in range(len(percsel)):
    #      perctmp=percsel[ipercsel]
    # print "Selected percentile:" + str(perctmp)
    #      cmd = "SELECT id_points,curve FROM " + tbname + " WHERE dtime = 'dt" \
    #         + self.dtime[0] + "' AND stat = 'Perc" + str(perctmp) + "'"
    #      cur.execute(cmd)
    #      rows = cur.fetchall()
    #      for row in rows:
    #         ipoint = row[0]
    #         curvetmp = row[1].split()
    #         self.hc[0][0][perctmp][ipoint-1] = curvetmp
    # TESTO PRECEDENTE:
    #    for h in range(self.nhaz):
    #      tbname = "hazard" + str(h+1)
    #      tmp = db.dbReadTable(con, cur, tbname)
    #      hcTmp1 = [[float(j) for j in tmp[i][5].split()] for i in range(len(tmp))]
    #      for k in range(self.nt*(self.nperc+1)*self.npts):
    #        if (len(hcTmp1[k]) < niml):
    #          for i in range(niml-len(hcTmp1[k])):
    #            hcTmp1[k].append(0)
    #
    #      hcTmp2 = np.array(hcTmp1)
    #      print self.nt, self.nperc+1, self.npts, niml, np.shape(hcTmp2)
    #      hcTmp3 = np.reshape(hcTmp2,(self.nt, self.nperc+1, self.npts, niml))
    #      self.hc[h] = hcTmp3
    #
    #    print np.shape(self.hc)
    # FINE JACOPO 5/5/13

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
    # JACOPO 3/5/13
    #    self.pn2.hazardCurve(self.hc, self.haz_sel, self.tw, self.hazards,
    #                         self.dtime, self.pt_sel, self.perc, self.iml,
    #                         self.imt)
        self.pn2.hazardCurve(self.hc, self.haz_sel, self.tw, self.hazards,
                             self.dtime, self.pt_sel, self.perc, self.iml,
                             self.imt, self.th, self.hc_perc, self.intTh)
    # FINE JACOPO 3/5/13

    # ROBERTO 27/06/2013
        self.map_export_gis.Enable(True)
    # END ROBERTO 27/06/2013
        # self.map_menu_ch.Enable(True)

        self.chaz.Clear()
        for i in range(self.nhaz):
            #  item = self.hz_name[i] + " - " + self.model[i]
            item = self.model[i]
            self.chaz.Append(item)

        self.chaz.SetSelection(0)

        self.pnl_lt.Enable(True)
    # ROBERTO 13/06/2013
        self.ensemble_item.Enable(True)
    # END ROBERTO 13/06/2013
    #    self.sb.SetStatusText("Bymur Database successfully loaded")
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
            # self.imgpath = dlg.GetPath()
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

        self.Destroy()

    # ROBERTO 28/06/2013
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
    # END ROBERTO 28/06/2013

    # JACOPO 4/6/13
    def ensemble_do(self, event):
        # selection of models and weights

        # ROBERTO 28/06/2013
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

    #    dtsel = self.dt_sel.GetValue()
    #    self.twsel = []
    #    for i in range(self.nhaz):
    #      tmp = self.dtime[i].index(dtsel)
    #      self.twsel.append(tmp)
    #      print self.dtime[i][self.twsel[i]]
    #    print "index dt sel = ", self.twsel

    #    for i in range(len(self.selected)):
    #      print self.selected[i], self.weights[i]

    # END ROBERTO 28/06/2013

        print self.hc_perc
        # self.twsel = [self.tw]
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
        # tmpmodel = tmpmodel + "_W:"
        # for i in range(nmod_comb):
        #   tmpmodel = tmpmodel + str(self.weights[i]) + ";"
        tmpmodel = tmpmodel + "_T:"
        tmpmodel = tmpmodel + str(self.dtime[self.
                                             selected[0]][self.twsel[0]]) + ";"
        tmpimt = self.imt[self.selected[0]]
        tmp = self.iml[self.selected[0]]
        tmpiml = ' '.join(map(str, tmp[:]))
        # print 'Thresholds:',tmpiml
        sql = """
              INSERT INTO hazard_phenomena (id_haz,name,model,imt,iml,
              id_map_info, id_spatial_data, vd_ID)
              VALUES('{0}','{1}','{2}','{3}','{4}',1, 1, 0)
              """
        # print sql.format(tmpid,tmpname,tmpmodel,tmpimt,tmpiml[:])
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
        # self.hc = np.concatenate((self.hc, hccomb))
        # print hccomb.shape
        hctmp = self.hc
        niml = len(self.iml[self.selected[0]])
        # self.hc = np.zeros((self.nhaz, self.nt, self.nperc+1, self.npts, niml))
        self.hc = [[[['0' for i in range(self.npts)] for j in range(100)]
                    for k in range(self.nt)] for h in range(self.nhaz)]
        for ihz in range(self.nhaz - 1):
            self.hc[ihz] = hctmp[ihz]
        self.hc[-1][0] = hccomb[0]
        # print self.hc.shape

        # print 'prima-->',self.hc_perc
        # self.hc_perc.insert(self.nhaz,np.asarray(self.percsel))
        self.hc_perc.append(np.asarray(self.percsel))
        # print 'dopo-->',self.hc_perc

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
            #      k = self.twsel[iii]
            # k = 0
            #      dt = str(dtimetmp[k]).zfill(3)
            dt = self.dtime[self.selected[0]][self.twsel[0]]
            print 'dT= ', dt, ' yr'
            for i in range(npts):
                idc = idc + 1
                sql = """
                  INSERT INTO {0} (id, id_haz, id_points, stat,
                  dtime, curve) VALUES ( {1}, {2}, {3}, '{4}', '{5}', '{6}' )
                  """
                # tmp = ' '.join(map(str,hccomb[0,0,i][:]))
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
                    # tmp = ' '.join(map(str,hccomb[0,self.percsel[p],i][:]))
                    # or just p, as in dbFunctions.py???
                    # print 'tmp--> ',tmp
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

    # ROBERTO 11/09/2013 -- update true/false flag for percentiles in new
    # hazard tab
        self.perc_flag.append(db.dbAssignFlagPerc(self.con, self.cur, tbname))
        print("UPDATE FLAGS PERCENTILES = {0}".format(self.perc_flag))
    # END ROBERTO 11/09/2013

        # update visualization (CHIEDERE ROB!!)
        item = tmpmodel
        # item = tmpname + " - " + tmpmodel
        self.chaz.Append(item)
    #    self.chaz.SetSelection(self.nhaz)
    #    self.haz_sel = int(self.chaz.GetSelection())
    #    print 'self.haz_sel:',self.haz_sel
    #    self.pn1.hazardMap(self.hc, self.lon, self.lat, self.id_area,
    #                       self.nareas, self.npts, self.hazards, self.dtime,
    #                       self.haz_sel, self.tw, self.th, self.perc, self.imgpath,
    #                       self.limits, self.iml, self.imt)
    #    self.pn2.hazardCurve(self.hc, self.haz_sel, self.tw, self.hazards,
    #                         self.dtime, self.pt_sel, self.perc, self.iml,
    #                         self.imt,self.th,self.hc_perc,self.intTh)

    # FINE
        busydlg = None    # closing waiting pop-up frame
        self.sb.SetStatusText("... ensemble model evaluated")

        print 'Task completed!!'
        print '------------------------------'
    # END JACOPO 4/6/13


class BymurGui(wx.App):

    """
    Instance of the main class BymurFrame
    """

    def OnInit(self):
        # frame = BymurFrame(None, -1, "BYMUR - BaYesian MUlti-Risk")
        frame = BymurFrame(None, -1, "V1 - BYMUR")
        frame.Show(True)
        self.SetTopWindow(frame)
        frame.Centre()
        return True


# starting the main gui
if __name__ == "__main__":
    app = BymurGui(0)
    app.MainLoop()
