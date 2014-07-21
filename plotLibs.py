

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

import random
import wx
import numpy as np
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as figcv
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as navtb

from matplotlib.patches import Circle, Wedge, Rectangle
from matplotlib.collections import PatchCollection
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import matplotlib as mpl
#ROBERTO 18/09/2013
## JACOPO, 05/06/13
#import math
## END JACOPO, 05/06/13

import globalFunctions as gf


# some global plotting settings
mpl.rcParams['xtick.direction']='out'
mpl.rcParams['ytick.direction']='out'
mpl.rcParams['axes.labelsize']='10'
mpl.rcParams['xtick.labelsize']='10'
mpl.rcParams['ytick.labelsize']='10'
mpl.rcParams['legend.fontsize']='10'
mpl.rcParams['font.family']='serif'
mpl.rcParams['font.sans-serif']='Times'

class pn1Canvas(wx.Panel):
  """
  
  """
  
  
  def __init__(self, parent):
    wx.Panel.__init__(self, parent)

    vbox = wx.BoxSizer(orient=wx.VERTICAL)
    #hbox_top = wx.BoxSizer(orient=wx.HORIZONTAL)

    self.fig = plt.figure()
    self.canvas = figcv(self, -1, self.fig)
    self.toolbar = navtb(self.canvas)
    #self.toolbar.Disable()

    self.fig.clf()
    #self.axes = self.fig.add_axes([0.1,0.1,0.85,0.85])


    self.fig.subplots_adjust(left=None, bottom=None, right=None, top=None, 
                             wspace=None, hspace=0.3)
    self.fig.hold(True)

    self.canvas.SetSize(self.GetSize())
    self.canvas.draw()
    
    #self.chpoints = wx.CheckBox(self, -1, 'Show Points', (-1, -1))
    #wx.EVT_CHECKBOX(self, self.chpoints.GetId(), self.show_points)
    #self.chareas = wx.CheckBox(self, -1, 'Show Areas', (-1, -1))
    #wx.EVT_CHECKBOX(self, self.chareas.GetId(), self.show_areas)
    #self.chpoints.Disable()
    #self.chareas.Disable()
    #hbox_top.Add(self.chpoints, 0, wx.ALL, 5)
    #hbox_top.Add(self.chareas, 0, wx.ALL, 5)

    #vbox.Add(hbox_top, 0, wx.EXPAND|wx.ALL, 0)
    vbox.Add(self.canvas, 1, wx.EXPAND|wx.ALL, 0)
    vbox.Add(self.toolbar, 0, wx.EXPAND|wx.ALL, 0)

    self.SetSizer(vbox)



 
  def hazardMap(self, *kargs):
    """
    Loading map ...
    """
    
    hc = kargs[0]            # volcanic hazard
    self.xx = kargs[1]       # x coord of each point
    self.yy = kargs[2]       # y coord of each point
    aa = kargs[3]            # id area for each point
    na = kargs[4]            # nareas
    npt = kargs[5]           # n. point
    hazard = kargs[6]        # hazard phenomena
    dtime = kargs[7]         # time windows
    hsel = kargs[8]          # hazard phenomenon
    tw = kargs[9]            # time window
    pth = kargs[10]          # probability threshold
    ith = kargs[11]          # intensity threshold
    perc = kargs[12]         # n. percentiles
    imgfile = kargs[13]
    xmap1, xmap2, ymap1, ymap2 = kargs[14]
    iml = kargs[15]
    imt = kargs[16]
    
#    print hsel
#    print iml
   
    nperc = len(perc)
#    self.fig.clf()
#    self.axes = self.fig.add_axes([0.0,0.15,0.9,0.75])
#    self.fig.subplots_adjust(left=None, bottom=None, right=None, top=None, 
#                             wspace=None, hspace=0.3)
#    self.fig.hold(True)
    
    nx = 100
    ny = 100
    self.xmin = min(self.xx)
    self.xmax = max(self.xx)
    self.ymin = min(self.yy)
    self.ymax = max(self.yy)
    print iml[hsel]
    nperc = len(hc[:][:][:])
    z = [0]*npt
    zp = [0]*npt
    for i in range(npt):
      tmp = hc[hsel][tw][0][i]
      curve = [float(j) for j in tmp.split()]
      #hc = np.cumsum(vh[nperc/2][i][:])
      #hc = list(1 - hc/hc[0])
      # finding intensity value corresponding to probability threshold (pth)
      if (pth < curve[0] and pth > curve[-1] ):
        for j in range(len(curve)):
          if (curve[j] < pth):
            interp = -(pth-curve[j]) * (iml[hsel][j]-iml[hsel][j-1]) / (curve[j-1]-curve[j])
            z[i] = iml[hsel][j] + interp 
            break
      elif (pth >= curve[0]):
        z[i] = iml[hsel][0]
      elif (pth <= curve[-1]):
        z[i] = iml[hsel][-1]
      else:
        pass
        #print "error"
    
      # finding probability value corresponding to intensity threshold (ith)
      if (ith < iml[hsel][-1] and ith > iml[hsel][0] ):
        for j in range(len(iml)):
          if (iml[hsel][j] < ith):
            interp = -(ith-iml[hsel][j]) * (curve[j]-curve[j-1]) / (iml[hsel][j-1]-iml[hsel][j])
            zp[i] = curve[j] + interp
            break
      elif (ith >= iml[hsel][-1]):
        zp[i] = curve[-1]
      elif (ith <= iml[hsel][0]):
        zp[i] = curve[0]
      else:
        pass
        #print "error"


    #print min(z),max(z)

    xv = np.linspace(self.xmin, self.xmax, nx)
    yv = np.linspace(self.ymin, self.ymax, ny)
    xg, yg = np.meshgrid(xv, yv)
    zg = mlab.griddata(self.xx, self.yy, z, xg, yg)  
    zgp = mlab.griddata(self.xx, self.yy, zp, xg, yg)  

    cmap = plt.cm.RdYlGn_r
    cmaplist = [cmap(i) for i in range(cmap.N)]
    dcmap = cmap.from_list('Custom cmap', cmaplist, cmap.N)

    # JACOPO 26/09/13
    maxint = 10
    maxz = np.ceil(max(z))+1
    minz = 0
    print 'maxz-->',maxz
    if maxz < 10:
       inter = 1.
       maxz = max(maxz,3.)
    else:
       order = np.floor(np.log10(maxz-minz)) - 1
       inter = 1.*10**(order)
    print 'range-->',minz,maxz,inter

    chk = len(np.arange(minz,maxz,inter))
    itmp = 1
    while chk > maxint:
        itmp = itmp + 1
        inter = inter * itmp
        bounds = range(minz,maxz,inter)
        chk = len(bounds)
    maxz = minz + chk*inter
    bounds = np.linspace(minz,maxz,chk+1)
      


    #print 'maxz->',maxz
    #print 'inter->',inter
    #print 'bounds->',bounds
    # END JACOPO 26/09/13

    #bounds = np.linspace(gf.floatFloor(min(z)), gf.floatCeil(max(z)), 11)
    
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

    self.fig.clf()
    self.fig.subplots_adjust(left=0.1, bottom=0.1, right=0.96, 
                             top=0.92, wspace=0.35, hspace=0.2)
    self.fig.hold(True)
    self.ax1 = self.fig.add_subplot(1, 2, 1)

    img = plt.imread(imgfile)
    self.ax1.imshow(img, origin="upper", extent=(xmap1, xmap2, ymap1, ymap2))
    
    #img2 = self.axes.imshow(zg, origin="lower", aspect="equal", vmin=bounds[0], 
                       #    vmax=bounds[-1], cmap=dcmap, alpha=0.75, 
                       #    extent=(self.xmin,self.xmax,self.ymin,self.ymax))

    #img2 = self.axes.scatter(self.xx[::10], self.yy[::10], c=z[::10], 
                       #      s=22, linewidths=0, color="#000000", 
                       #      cmap=plt.cm.RdYlGn_r, vmin=min(z), 
                       #      vmax=max(z), alpha=0.75)

    self.map1 = self.ax1.contourf(xg, yg, zg, bounds, origin="lower",
                                  cmap=plt.cm.RdYlGn_r, alpha=0.5)
    self.map2 = self.ax1.contour(xg, yg, zg, bounds, origin="lower",
                                 aspect="equal", cmap=plt.cm.RdYlGn_r, linewidths=2,
                                 alpha=1)
                            

    self.cb1 = self.fig.colorbar(self.map1, shrink=0.9, norm=norm, ticks=bounds, 
                                 boundaries=bounds, format='%.3f')
    self.cb1.set_alpha(1)
    self.cb1.set_label(imt[hsel])
    self.cb1.draw_all()

    self.ax1.set_title("Hazard Map\n", fontsize=9)
    self.ax1.set_xlabel("Easting (km)")
    self.ax1.set_ylabel("Northing (km)")
    self.ax1.axis([xmap1, xmap2, ymap1, ymap2])

    self.ax2 = self.fig.add_subplot(1, 2, 2)
    self.ax2.imshow(img, origin="upper", extent=(xmap1, xmap2, ymap1, ymap2))
    self.map3 = self.ax2.contourf(xg, yg, zgp, 10, origin="lower",
                                  cmap=plt.cm.RdYlGn_r, alpha=0.5)
    self.map4 = self.ax2.contour(xg, yg, zgp, 10, origin="lower",
                                 aspect="equal", cmap=plt.cm.RdYlGn_r, linewidths=2,
                                 alpha=1)
                            
    self.cb2 = self.fig.colorbar(self.map3, shrink=0.9, orientation='vertical')

    #self.cb2.set_label("P", rotation=90)
    self.cb2.set_alpha(1)
    self.cb2.draw_all()
    self.ax2.axis([xmap1, xmap2, ymap1, ymap2])

    self.ax2.set_title("Probability Map\n", fontsize=9)
    self.ax2.set_xlabel("Easting (km)")
    #self.ax2.set_ylabel("Northing (km)")
    #self.ax2.set_ylabel(ylab)


    self.canvas.draw()
    self.canvas.mpl_connect('motion_notify_event', self.updateMouseSel)
    self.Layout()
    return z


  def updateMouseSel(self, event):

    if (event.inaxes != self.ax1): 
          return
    else:
      xsel, ysel = event.xdata, event.ydata
      if ( xsel >= self.xmin and xsel <= self.xmax and 
           ysel >= self.ymin and ysel <= self.ymax ):
        dist = np.sqrt( (self.xx-xsel)**2 + (self.yy-ysel)**2 )
        i = np.argmin(dist) + 1
        x = self.xx[i]
        y = self.yy[i]
        tt = "Hazard Map\nPoint n. %s, Lon = %8.3f km, Lat = %8.3f km" %(i, x, y)
        #tt = "Point n. {:}, Lon = {:f8.3} km,  Lat = {:f8.3} km".format(i,x,y)
#        self.ax1.set_title(tt, fontsize=9)
        self.canvas.draw()
      else:
        tt = "Hazard Map\nOut of data points bounds"
#        self.ax1.set_title(tt, fontsize=9)
        self.canvas.draw()

#    if (event.inaxes != self.ax2): 
#          return
#    else:
#      xsel, ysel = event.xdata, event.ydata
#      if ( xsel >= self.xmin and xsel <= self.xmax and 
#           ysel >= self.ymin and ysel <= self.ymax ):
#        dist = np.sqrt( (self.xx-xsel)**2 + (self.yy-ysel)**2 )
#        i = np.argmin(dist) + 1
#        x = self.xx[i]
#        y = self.yy[i]
#        tt = "Hazard Map\nPoint n. %s, Lon = %8.3f km, Lat = %8.3f km" %(i, x, y)
#        #tt = "Point n. {:}, Lon = {:f8.3} km,  Lat = {:f8.3} km".format(i,x,y)
#        #self.ax2.set_title(tt, fontsize=9)
#        self.canvas.draw()
#      else:
#        tt = "Hazard Map\nOut of data points bounds"
#        #self.ax2.set_title(tt, fontsize=9)
#        self.canvas.draw()




class pn2Canvas(wx.Panel):
  """
  Bottom canvas.
  It plots hazard curves, fragility curves ...   
  """
  
  
  def __init__(self, parent):
    wx.Panel.__init__(self, parent)

    vbox = wx.BoxSizer(orient=wx.VERTICAL)
    hbox_top = wx.BoxSizer(orient=wx.HORIZONTAL)

    self.fig = plt.figure()
    self.canvas = figcv(self, -1, self.fig)
    self.toolbar = navtb(self.canvas)
    #self.toolbar.Disable()

    self.fig.clf()
    #self.axes = self.fig.add_axes([0.1,0.1,0.85,0.85])

    #cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick)

    self.fig.subplots_adjust(left=None, bottom=None, right=None, top=None, 
                             wspace=None, hspace=0.3)
    self.fig.hold(True)

    self.canvas.SetSize(self.GetSize())
    self.canvas.draw()
    
    vbox.Add(hbox_top, 0, wx.EXPAND|wx.ALL, 0)
    vbox.Add(self.canvas, 1, wx.EXPAND|wx.ALL, 0)
    vbox.Add(self.toolbar, 0, wx.EXPAND|wx.ALL, 0)
 
    self.SetSizer(vbox)


  def hazardCurve(self, *kargs):
    """
    It plots hazard curves.
  
    """
    
    hc = kargs[0]             # hazard curves
    hsel = kargs[1]           # selected hazard phenomenon 
    tw = kargs[2]             # selected time window
    hazard = kargs[3]         # hazard phenomena
    dtime = kargs[4]          # time windows
    pt_sel = kargs[5]         # selected point
    perc = kargs[6]           # percentiles
    iml = kargs[7]            # intensity
    imt = kargs[8]            # intensity unit
# JACOPO, 05/06/13
    th = kargs[9]             # threshold hazard map
    hc_perc = kargs[10]       # percentiles in hc
    ith = kargs[11]          # intensity threshold
# FINE JACOPO, 05/06/13

    self.fig.clf()
    self.axes = self.fig.add_axes([0.15,0.15,0.75,0.75])
    self.fig.subplots_adjust(left=None, bottom=None, right=None, top=None, 
                             wspace=None, hspace=0.3)
    self.fig.hold(True)
    self.axes.grid(True)
    
    nperc = len(perc)
    
# JACOPO 5/5/13  
##    tmp = [perc[0], perc[nperc/2], perc[-1]]
##    index = [1, nperc/2, -1]
##    print 'hc_perc--->',hc_perc
#    percsel=hc_perc[hsel]  
    perc_lbl = ['10', '50', '90']
#    n10=np.where(percsel==10)
#    n50=np.where(percsel==50)
#    n90=np.where(percsel==90)
##    print 'n10--->',n10
##    print 'n50--->',n50
##    print 'n90--->',n90
#
#    index = [n10[0][0]+1,n50[0][0]+1,n90[0][0]+1]
##    index = [percsel.index(10), percsel.index(50), percsel.index(90)]
    index = [10,50,90] 
    print 'index of percentiles--->',index
# END JACOPO 5/5/13      

    pmin = 1000;
    for p in range(3):
      ll = perc_lbl[p] + "th Percentile"
      tmp = hc[hsel][tw][index[p]][pt_sel]
      curve = [float(j) for j in tmp.split()]
      self.pt, = self.axes.plot(iml[hsel], curve, 
                                linewidth=1, alpha=1, label=ll)

    tmp = hc[hsel][tw][0][pt_sel][:]
    ave = [float(j) for j in tmp.split()]
    self.pt, = self.axes.plot(iml[hsel], ave, color="#000000",
                                linewidth=1, alpha=1, label="Average")

# JACOPO, 05/06/13
# AGGIUNGERE LINEA DI SOGLIA IN PROB (th), DA PASSARE NEGLI ARGOMENTI (kargs)
#    thmax = iml[hsel][-1]
#    limi = [0,thmax]
#    valu = [th,th] 
    #self.pt, = self.axes.plot(limi, valu, '--', color="#000000",
                                #linewidth=1, alpha=1, label="Threshold in probability")
    self.axes.axhline(y=th, linestyle='--', color="#000000",
                                linewidth=1, alpha=1, label="Threshold in Probability")

#    ind = -1;
#    curve = hc[hsel][tw][index[0]][pt_sel][:]
#    #print 'curve-->',curve
#    prmin = min([x for x in curve if x >0])
#    order = np.floor(np.log10(prmin))
#    prmin = 10**order
#    prmax = hc[hsel][tw][index[2]][pt_sel][0]
#    order = np.ceil(np.log10(prmax))
#    prmax = 10**order
#    #print 'prmin-->',prmin
#    #print 'prmax-->',prmax
#    #print 'ith-->',ith
#    limi = [ith,ith] 
#    valu = [prmin,prmax]
#    self.pt, = self.axes.plot(limi, valu, '-', color="#000000",
#                                linewidth=1, alpha=1, label="Threshold in Intensity")
    self.axes.axvline(x=ith, linestyle='-', color="#000000",
                                linewidth=1, alpha=1, label="Threshold in Intensity")


# END JACOPO, 05/06/13
    self.axes.legend()
    #print tw
    #print dtime[tw]
    #tt = (hazard[hsel] + " Hazard - Point n." + str(pt_sel+1) + 
         #" - Time window = " + dtime[tw] + " years")
    tt = ("Point n." + str(pt_sel+1) + 
         " - Time window = " + dtime[hsel][tw] + " years")
    
    self.axes.set_title(tt, fontsize=10)  
    self.axes.set_xlabel(imt[hsel])
    self.axes.set_ylabel("Probability of Exceedance")
    self.axes.set_yscale("log")
    #self.axes.axis([0,1,0,1])
    self.canvas.draw()
    self.Layout()




class pn3Canvas(wx.Panel):
  """
  
  """
  
  
  def __init__(self, parent):
    wx.Panel.__init__(self, parent)

    vbox = wx.BoxSizer(orient=wx.VERTICAL)
  
    self.SetSizer(vbox)


class pn4Canvas(wx.Panel):
  """
  
  """
  
  
  def __init__(self, parent):
    wx.Panel.__init__(self, parent)

    vbox = wx.BoxSizer(orient=wx.VERTICAL)
  
    self.SetSizer(vbox)





