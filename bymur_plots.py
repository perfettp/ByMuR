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

import matplotlib as mpl
import matplotlib.mlab as mlab
import matplotlib.pyplot as pyplot
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg


# some global plotting settings
mpl.rcParams['xtick.direction'] = 'out'
mpl.rcParams['ytick.direction'] = 'out'
mpl.rcParams['axes.labelsize'] = '10'
mpl.rcParams['xtick.labelsize'] = '10'
mpl.rcParams['ytick.labelsize'] = '10'
mpl.rcParams['legend.fontsize'] = '10'
mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['font.sans-serif'] = 'Times'


class BymurPlot(object):
    def __init__(self, *args, **kwargs):
        self._parent = kwargs.get('parent', None)
        self._figure = pyplot.figure()
        self._canvas = FigureCanvasWxAgg(self._parent, -1, self._figure)
        self._toolbar = NavigationToolbar2WxAgg(self._canvas)
        self._figure.clf()
        self._figure.subplots_adjust(left=None, bottom=None, right=None,
                                    top=None, wspace=None, hspace=0.3)
        self._cmap = pyplot.cm.RdYlGn_r
        self._figure.hold(True)
        self._canvas.SetSize(self._parent.GetSize())
        self._canvas.draw()






class HazardGraph(BymurPlot):
    def __init__(self, *args, **kwargs):
        self._imgfile = kwargs.get('imgfile',"naples_gmaps.png")
        self._click_callback = kwargs.get('click_callback', None)
        super(HazardGraph, self).__init__(*args, **kwargs)
        self._figure.canvas.mpl_connect('button_press_event',
                                        self._click_callback)
        self._points_data = None


    def plot(self, hazard_description, points_utm):


        # Prepare matplotlib grid and data
        grid_points_number = 100
        self._points_utm = points_utm
        x_points = [p['point']['easting'] for p in self._points_utm]

        # TODO: fix these points
        x_points = [x/1000 for x in x_points]
        print "y_points len: %s" % len(x_points)
        y_points = [p['point']['northing'] for p in self._points_utm]
        y_points = [x/1000 for x in y_points]
        print "y_points len: %s" % len(y_points)
        x_vector = np.linspace(min(x_points), max(x_points), grid_points_number)
        y_vector = np.linspace(min(y_points), max(y_points), grid_points_number)
        print "x_vector len: %s" % len(x_vector)
        print "y_vector len: %s" % len(y_vector)
        x_mesh, y_mesh = np.meshgrid(x_vector, y_vector)



        self._figure.clf()
        self._figure.subplots_adjust(left=0.1, bottom=0.1, right=0.96,
                                     top=0.92, wspace=0.35, hspace=0.2)
        self._figure.hold(True)
        map_limits = [375.300, 508.500, 4449.200, 4569.800]
        self.haz_map = self.plot_hazard_map(hazard_description,
                                            x_points, y_points,
                                            x_mesh, y_mesh,
                             [p['haz_value'] for p in self._points_utm],
                             map_limits)

        self.prob_map = self.plot_probability_map(x_points, y_points, x_mesh,
                                              y_mesh,
                                  [p['prob_value'] for p in self._points_utm],
                                  map_limits)

        self._canvas.draw()

    def plot_hazard_map(self, hazard_description, x_points, y_points, x_mesh,
                        y_mesh, z_points,
                 map_limits):
        xmap1, xmap2, ymap1, ymap2 = map_limits
        haz_bar_label = hazard_description['imt']
        # TODO: install natgrid to use natural neighbor interpolation
        z_mesh = mlab.griddata(x_points, y_points, z_points, x_mesh, y_mesh,
                               interp='linear')

        # Define colors mapping and levels
        z_boundaries = self.levels_boundaries(z_points)
        print "hazard_map_plot> z_boundaries: %s" % z_boundaries
        cmap_norm_index = mpl.colors.BoundaryNorm(z_boundaries,
                                                  self._cmap.N)
        # Add hazard map subfigure
        haz_subplot = self._figure.add_subplot(1, 2, 1)
        # TODO: tmp image plot
        img = pyplot.imread(self._imgfile)

        haz_subplot.imshow(
            img,
            zorder=0,
            origin="upper",
            extent=(
                xmap1,
                xmap2,
                ymap1,
                ymap2))


        # Plot hazard map
        haz_contourf = haz_subplot.contourf(x_mesh, y_mesh, z_mesh,
                                            z_boundaries,
                                            origin="lower",
                                            cmap=self._cmap,
                                            alpha=0.5,
                                            zorder=1 )
        haz_contour = haz_subplot.contour(x_mesh, y_mesh, z_mesh,
                                          z_boundaries,
                                          origin="lower",
                                          aspect="equal",
                                          cmap=self._cmap,
                                          linewidths=2,
                                          alpha=1,
                                          zorder=2)

        # Plot hazard bar
        hazard_bar = self._figure.colorbar(
            haz_contourf,
            shrink=0.9,
            norm=cmap_norm_index,
            ticks=z_boundaries,
            boundaries=z_boundaries,
            format='%.3f')
        hazard_bar.set_alpha(1)
        hazard_bar.set_label(haz_bar_label)
        hazard_bar.draw_all()

        haz_subplot.set_title("Hazard Map\n", fontsize=9)
        haz_subplot.set_xlabel("Easting (km)")
        haz_subplot.set_ylabel("Northing (km)")
        # TODO: fix these limits
        haz_subplot.axis([425.000,448.000, 4510.000, 4533.000])
        # haz_subplot.axis([350.000,500.000, 4400.000, 4600.000])
        return haz_subplot

    def plot_probability_map(self, x_points, y_points, x_mesh, y_mesh, z_points,
                 map_limits):

        xmap1, xmap2, ymap1, ymap2 = map_limits
        z_mesh = mlab.griddata(x_points, y_points, z_points, x_mesh, y_mesh,
                               interp='linear')

        # Define colors mapping and levels
        z_boundaries = self.levels_boundaries(z_points)
        print "probability_map_plot> z_boundaries: %s" % z_boundaries
        cmap_norm_index = mpl.colors.BoundaryNorm(z_boundaries,
                                                  self._cmap.N)

        prob_subplot = self._figure.add_subplot(1, 2, 2)
        img = pyplot.imread(self._imgfile)
        prob_subplot.imshow(
            img,
            origin="upper",
            extent=(
                xmap1,
                xmap2,
                ymap1,
                ymap2))
        prob_contourf = prob_subplot.contourf(x_mesh, y_mesh, z_mesh,
                                          z_boundaries, origin="lower",
                                          cmap=self._cmap, alpha=0.5)
        prob_contour = prob_subplot.contour(x_mesh, y_mesh, z_mesh,
                                         z_boundaries,
                                         origin="lower",
                                         aspect="equal",
                                         cmap=self._cmap,
                                         linewidths=2,
                                         alpha=1)

        probability_bar = self._figure.colorbar(
            prob_contourf,
            shrink=0.9,
            orientation='vertical')


        probability_bar.set_alpha(1)
        prob_subplot.set_title("Probability Map\n", fontsize=9)
        prob_subplot.set_xlabel("Easting (km)")
        probability_bar.draw_all()
        # TODO: fix these limits
        prob_subplot.axis([425.000,448.000, 4510.000, 4533.000])
        # prob_subplot.axis([350.000,500.000, 4400.000, 4600.000])
        return prob_subplot

        
    def levels_boundaries(self, z_array):
        max_intervals = 5
        maxz = np.ceil(max(z_array))
        minz = np.floor(min(z_array))
        print "z_array max: %s" % maxz
        print "z_array min: %s" % minz

        if (maxz - minz) < 4:
            inter = 0.2
            print "qui"
        elif maxz < 10:
            inter = 1.
            maxz = max(maxz, 3.)
        else:
            order = np.floor(np.log10(maxz - minz)) - 1
            inter = 1. * 10 ** (order)

        chk = len(np.arange(minz, maxz, inter))
        itmp = 1
        while chk > max_intervals:
            itmp = itmp + 1
            inter = inter * itmp
            if inter < 1:
                inter = 1
            bounds = range(int(minz), int(maxz), int(inter))
            chk = len(bounds)
        maxz = minz + chk * inter
        # bounds = np.linspace(minz, maxz, chk + 1)
        bounds = np.linspace(min(z_array), max(z_array), max_intervals)
        return bounds

class HazardCurve(BymurPlot):
    def __init__(self, *args, **kwargs):
        super(HazardCurve, self).__init__(*args, **kwargs)

    def plot(self, hazard_options, hazard_description, selected_point,
             selected_point_curves):
        perc_to_plot = ["10", "50", "90"]

        self._figure.clf()
        self._axes = self._figure.add_axes([0.15, 0.15, 0.75, 0.75])
        self._figure.hold(True)
        self._axes.grid(True)
        xticks = hazard_description['int_thresh_list'] + [0]
        self._axes.set_xticks(xticks)
        self._axes.set_xlim(left=0,
                            right=hazard_description['int_thresh_list'][
                                len(hazard_description['int_thresh_list'])-1])
        for perc in perc_to_plot:
            perc_key = "percentile"+perc+".0"
            if selected_point_curves[perc_key] is not None:
                perc_label =  perc + "th Percentile"
                self._axes.plot(hazard_description['int_thresh_list'],
                                [float(y) for  y in
                                 selected_point_curves[perc_key].split(',')],
                                linewidth=1,
                                alpha=1,
                                label=perc_label)


        if selected_point_curves["mean"] is not None:
                self._axes.plot(hazard_description['int_thresh_list'],
                                [float(y) for  y in
                                 selected_point_curves["mean"].split(',')],
                                 color="#000000",
                                 linewidth=1,
                                 alpha=1,
                                 label="Average")

        self._axes.axhline(
            y=hazard_options['hazard_threshold'],
            linestyle='--',
            color="#000000",
            linewidth=1,
            alpha=1,
            label="Threshold in Probability")

        self._axes.axvline(
            x=hazard_options['int_thresh'],
            linestyle='-',
            color="#000000",
            linewidth=1,
            alpha=1,
            label="Threshold in Intensity")


        self._axes.legend()
        title = ("Point n." + str(selected_point['index']+ 1) +
               " - Time window = " + str(hazard_options['exp_time']) + " "
                                                                        "years")
        self._axes.set_title(title, fontsize=10)


        self._axes.set_ylabel("Probability of Exceedance")
        self._axes.set_yscale("log")
        # self.axes.axis([0,1,0,1])
        self._canvas.draw()


class VulnCurve(BymurPlot):
    def __init__(self, *args, **kwargs):
        super(VulnCurve, self).__init__(*args, **kwargs)

class RiskCurve(BymurPlot):
    def __init__(self, *args, **kwargs):
        super(RiskCurve, self).__init__(*args, **kwargs)



