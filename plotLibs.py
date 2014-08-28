#!/usr/bin/env python
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

import numpy as np
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as figcv
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as navtb

from matplotlib.patches import Circle, Wedge, Rectangle
from matplotlib.collections import PatchCollection
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import matplotlib as mpl
import globalFunctions as gf


# some global plotting settings
mpl.rcParams['xtick.direction'] = 'out'
mpl.rcParams['ytick.direction'] = 'out'
mpl.rcParams['axes.labelsize'] = '10'
mpl.rcParams['xtick.labelsize'] = '10'
mpl.rcParams['ytick.labelsize'] = '10'
mpl.rcParams['legend.fontsize'] = '10'
mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['font.sans-serif'] = 'Times'



# TODO: refactor completely this object.
# Which fields have to be initialized in
#  __init__, which in other methods? What is really required? etc
class MapFigure():
    """
    Graphical object containing matplot canvas. This is the main graph where
    hazard map is plotted and where is possible to click to select for which
    point visualize hazard's curves.
    """
    
    _haz_array = []

    def __init__(self, parent, controller):

        self._parent  = parent
        self._controller = controller
        self.fig = plt.figure()
        self.canvas = figcv(self._parent, -1, self.fig)
        self.toolbar = navtb(self.canvas)
        self.fig.clf()
        self.fig.subplots_adjust(left=None, bottom=None, right=None, top=None,
                                 wspace=None, hspace=0.3)
        self.fig.hold(True)
        self.canvas.SetSize(self._parent.GetSize())
        self.fig.canvas.mpl_connect(
            'button_press_event', self._controller.onMapClick)
        self.canvas.draw()


    def hazardMap(self, **kwargs):
        """
        Main method to draw updated map.
        It accept a dictionary as argument, that must contains following keys
            and data:
                hc:
                lon:
                lat:
                ...
        """

        hc = kwargs.get('hc')            # volcanic hazard
        self.xx = kwargs.get('lon')       # x coord of each point
        self.yy = kwargs.get('lat')       # y coord of each point
        aa = kwargs.get('id_area')            # id area for each point
        na = kwargs.get('nareas')            # nareas
        npt = kwargs.get('npts')           # n. point
        hazard = kwargs.get('hazards')        # hazard phenomena
        dtime = kwargs.get('dtime')         # time windows
        hsel = kwargs.get('haz_mod')          # hazard phenomenon
        tw = kwargs.get('tw')            # time window
        pth = kwargs.get('th')          # probability threshold
        ith = kwargs.get('int_thres')      # intensity threshold
        perc = kwargs.get('perc')         # n. percentiles
        imgfile = kwargs.get('imgpath')
        xmap1, xmap2, ymap1, ymap2 = kwargs.get('limits')
        iml = kwargs.get('iml')
        imt = kwargs.get('imt')


        nperc = len(perc)


        nx = 100
        ny = 100
        self.xmin = min(self.xx)
        self.xmax = max(self.xx)
        self.ymin = min(self.yy)
        self.ymax = max(self.yy)
        print iml[hsel]
        nperc = len(hc[:][:][:])
        self._haz_array = [0] * npt
        zp = [0] * npt
        for i in range(npt):
            tmp = hc[hsel][tw][0][i]
            curve = [float(j) for j in tmp.split()]

            if (pth < curve[0] and pth > curve[-1]):
                for j in range(len(curve)):
                    if (curve[j] < pth):
                        interp = - \
                            (pth - curve[j]) * (iml[hsel][j] - iml[hsel][j - 1]) / (curve[j - 1] - curve[j])
                        self._haz_array[i] = iml[hsel][j] + interp
                        break
            elif (pth >= curve[0]):
                self._haz_array[i] = iml[hsel][0]
            elif (pth <= curve[-1]):
                self._haz_array[i] = iml[hsel][-1]
            else:
                pass

            if (ith < iml[hsel][-1] and ith > iml[hsel][0]):
                for j in range(len(iml)):
                    if (iml[hsel][j] < ith):
                        interp = - \
                            (ith - iml[hsel][j]) * (curve[j] - curve[j - 1]) / (iml[hsel][j - 1] - iml[hsel][j])
                        zp[i] = curve[j] + interp
                        break
            elif (ith >= iml[hsel][-1]):
                zp[i] = curve[-1]
            elif (ith <= iml[hsel][0]):
                zp[i] = curve[0]
            else:
                pass


        xv = np.linspace(self.xmin, self.xmax, nx)
        yv = np.linspace(self.ymin, self.ymax, ny)
        xg, yg = np.meshgrid(xv, yv)
        zg = mlab.griddata(self.xx, self.yy, self._haz_array, xg, yg)
        zgp = mlab.griddata(self.xx, self.yy, zp, xg, yg)

        cmap = plt.cm.RdYlGn_r
        cmaplist = [cmap(i) for i in range(cmap.N)]
        dcmap = cmap.from_list('Custom cmap', cmaplist, cmap.N)

        # JACOPO 26/09/13
        maxint = 10
        maxz = np.ceil(max(self._haz_array)) + 1
        minz = 0
        print 'maxz-->', maxz
        if maxz < 10:
            inter = 1.
            maxz = max(maxz, 3.)
        else:
            order = np.floor(np.log10(maxz - minz)) - 1
            inter = 1. * 10 ** (order)
        print 'range-->', minz, maxz, inter

        chk = len(np.arange(minz, maxz, inter))
        itmp = 1
        while chk > maxint:
            itmp = itmp + 1
            inter = inter * itmp
            bounds = range(int(minz), int(maxz), int(inter))
            chk = len(bounds)
        maxz = minz + chk * inter
        bounds = np.linspace(minz, maxz, chk + 1)


        norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

        self.fig.clf()
        self.fig.subplots_adjust(left=0.1, bottom=0.1, right=0.96,
                                 top=0.92, wspace=0.35, hspace=0.2)
        self.fig.hold(True)
        self.ax1 = self.fig.add_subplot(1, 2, 1)

        img = plt.imread(imgfile)
        self.ax1.imshow(
            img,
            origin="upper",
            extent=(
                xmap1,
                xmap2,
                ymap1,
                ymap2))


        self.map1 = self.ax1.contourf(xg, yg, zg, bounds, origin="lower",
                                      cmap=plt.cm.RdYlGn_r, alpha=0.5)
        self.map2 = self.ax1.contour(
            xg,
            yg,
            zg,
            bounds,
            origin="lower",
            aspect="equal",
            cmap=plt.cm.RdYlGn_r,
            linewidths=2,
            alpha=1)

        self.cb1 = self.fig.colorbar(
            self.map1,
            shrink=0.9,
            norm=norm,
            ticks=bounds,
            boundaries=bounds,
            format='%.3f')
        self.cb1.set_alpha(1)
        self.cb1.set_label(imt[hsel])
        self.cb1.draw_all()

        self.ax1.set_title("Hazard Map\n", fontsize=9)
        self.ax1.set_xlabel("Easting (km)")
        self.ax1.set_ylabel("Northing (km)")
        self.ax1.axis([xmap1, xmap2, ymap1, ymap2])

        self.ax2 = self.fig.add_subplot(1, 2, 2)
        self.ax2.imshow(
            img,
            origin="upper",
            extent=(
                xmap1,
                xmap2,
                ymap1,
                ymap2))
        self.map3 = self.ax2.contourf(xg, yg, zgp, 10, origin="lower",
                                      cmap=plt.cm.RdYlGn_r, alpha=0.5)
        self.map4 = self.ax2.contour(
            xg,
            yg,
            zgp,
            10,
            origin="lower",
            aspect="equal",
            cmap=plt.cm.RdYlGn_r,
            linewidths=2,
            alpha=1)

        self.cb2 = self.fig.colorbar(
            self.map3,
            shrink=0.9,
            orientation='vertical')

        # self.cb2.set_label("P", rotation=90)
        self.cb2.set_alpha(1)
        self.cb2.draw_all()
        self.ax2.axis([xmap1, xmap2, ymap1, ymap2])

        self.ax2.set_title("Probability Map\n", fontsize=9)
        self.ax2.set_xlabel("Easting (km)")
        # self.ax2.set_ylabel("Northing (km)")
        # self.ax2.set_ylabel(ylab)

        self.canvas.draw()
        self.canvas.mpl_connect('motion_notify_event', self.updateMouseSel)


    def updateMouseSel(self, event):

        if (event.inaxes != self.ax1):
            return
        else:
            xsel, ysel = event.xdata, event.ydata
            if (xsel >= self.xmin and xsel <= self.xmax and
                    ysel >= self.ymin and ysel <= self.ymax):
                dist = np.sqrt((self.xx - xsel) ** 2 + (self.yy - ysel) ** 2)
                i = np.argmin(dist) + 1
                x = self.xx[i]
                y = self.yy[i]
                tt = "Hazard Map\nPoint n. %s, Lon = %8.3f km, Lat = %8.3f km" % (
                    i, x, y)

                self.canvas.draw()
            else:
                tt = "Hazard Map\nOut of data points bounds"
                self.canvas.draw()

    @property
    def hazArray(self):
        return self._haz_array


class HazFigure():
    _perc_lbl = ['10', '50', '90']

    def __init__(self, parent, controller):

        self._parent = parent
        self.fig = plt.figure()
        self.canvas = figcv(self._parent, -1, self.fig)
        self.toolbar = navtb(self.canvas)
        self.fig.clf()
        self.fig.subplots_adjust(left=None, bottom=None, right=None, top=None,
                                 wspace=None, hspace=0.3)
        self.fig.hold(True)
        self.canvas.SetSize(self._parent.GetSize())
        self.canvas.draw()

    def hazardCurve(self, **kwargs):
        """
        It plots hazard curves.

        """

        hc = kwargs.get('hc')            # volcanic hazard
        self.xx = kwargs.get('lon')       # x coord of each point
        self.yy = kwargs.get('lat')       # y coord of each point
        aa = kwargs.get('id_area')            # id area for each point
        na = kwargs.get('nareas')            # nareas
        npt = kwargs.get('npts')           # n. point
        hazard = kwargs.get('hazards')        # hazard phenomena
        dtime = kwargs.get('dtime')         # time windows
        hsel = kwargs.get('haz_mod')          # hazard phenomenon
        tw = kwargs.get('tw')            # time window
        pth = kwargs.get('th')          # probability threshold
        ith = kwargs.get('int_thres')      # intensity threshold
        perc = kwargs.get('perc')         # n. percentiles
        imgfile = kwargs.get('imgpath')
        xmap1, xmap2, ymap1, ymap2 = kwargs.get('limits')
        iml = kwargs.get('iml')
        imt = kwargs.get('imt')
        pt_sel = kwargs.get('pt_sel')


        # hc = kargs[0]             # hazard curves
        # hsel = kargs[1]           # selected hazard phenomenon
        # tw = kargs[2]             # selected time window
        # hazard = kargs[3]         # hazard phenomena
        # dtime = kargs[4]          # time windows
        # pt_sel = kargs[5]         # selected point
        # perc = kargs[6]           # percentiles
        # iml = kargs[7]            # intensity
        # imt = kargs[8]            # intensity unit
        # pth = kargs[9]             # threshold hazard map
        # hc_perc = kargs[10]       # percentiles in hc
        # ith = kargs[11]          # intensity threshold


        self.fig.clf()
        self.axes = self.fig.add_axes([0.15, 0.15, 0.75, 0.75])
        self.fig.subplots_adjust(left=None, bottom=None, right=None, top=None,
                                 wspace=None, hspace=0.3)
        self.fig.hold(True)
        self.axes.grid(True)

        nperc = len(perc)

        index = [10, 50, 90]
        print 'index of percentiles--->', index

        pmin = 1000
        for p in range(3):
            ll = self._perc_lbl[p] + "th Percentile"
            tmp = hc[hsel][tw][index[p]][pt_sel]
            curve = [float(j) for j in tmp.split()]
            self.pt, = self.axes.plot(iml[hsel], curve,
                                      linewidth=1, alpha=1, label=ll)

        tmp = hc[hsel][tw][0][pt_sel][:]
        ave = [float(j) for j in tmp.split()]
        self.pt, = self.axes.plot(iml[hsel], ave, color="#000000",
                                  linewidth=1, alpha=1, label="Average")

        self.axes.axhline(
            y=pth,
            linestyle='--',
            color="#000000",
            linewidth=1,
            alpha=1,
            label="Threshold in Probability")

        self.axes.legend()
        tt = ("Point n." + str(pt_sel + 1) +
              " - Time window = " + dtime[hsel][tw] + " years")

        self.axes.set_title(tt, fontsize=10)
        self.axes.set_xlabel(imt[hsel])
        self.axes.set_ylabel("Probability of Exceedance")
        self.axes.set_yscale("log")
        # self.axes.axis([0,1,0,1])
        self.canvas.draw()



class VulnFigure():

    def __init__(self, parent, controller):

        self._parent  = parent
        self.fig = plt.figure()
        self.canvas = figcv(self._parent, -1, self.fig)
        self.toolbar = navtb(self.canvas)
        self.fig.clf()
        self.fig.subplots_adjust(left=None, bottom=None, right=None, top=None,
                                 wspace=None, hspace=0.3)
        self.fig.hold(True)
        self.canvas.SetSize(self._parent.GetSize())
        self.canvas.draw()


class RiskFigure():

    def __init__(self, parent, controller):

        self._parent  = parent
        self.fig = plt.figure()
        self.canvas = figcv(self._parent, -1, self.fig)
        self.toolbar = navtb(self.canvas)
        self.fig.clf()
        self.fig.subplots_adjust(left=None, bottom=None, right=None, top=None,
                                 wspace=None, hspace=0.3)
        self.fig.hold(True)
        self.canvas.SetSize(self._parent.GetSize())
        self.canvas.draw()


