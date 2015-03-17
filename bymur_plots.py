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


from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import bymur_functions as bf
import matplotlib as mpl
import matplotlib.mlab as mlab
import matplotlib.pyplot as pyplot
import matplotlib.collections as mcoll
from matplotlib.widgets import RectangleSelector
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

show_areas = True


class BymurPlot(object):
    _stat_to_plot = ['mean', 'quantile10', 'quantile50', 'quantile90']
    _stat_colors = ['k', 'g', 'b', 'r']
    def __init__(self, *args, **kwargs):
        self.x_points = None
        self.y_points = None
        self._parent = kwargs.get('parent', None)
        self._figure = pyplot.figure()
        self._canvas = FigureCanvasWxAgg(self._parent, -1, self._figure)
        self._toolbar = NavigationToolbar2WxAgg(self._canvas)
        self._figure.clf()
        # self._figure.subplots_adjust(left=None, bottom=None, right=None,
        #                             top=None, wspace=None, hspace=0.3)
        self._cmap = pyplot.cm.RdYlGn_r
        self._figure.hold(True)
        self._canvas.SetSize(self._parent.GetSize())
        self._canvas.draw()

    def clear(self):
        self._figure.clf()
        self._canvas.draw()


class HazardGraph(BymurPlot):
    def __init__(self, *args, **kwargs):
        self._imgfile = kwargs.get('imgfile',"naples_gmaps.png")
        self._click_callback = kwargs.get('click_callback', None)
        self._selection_callback = kwargs.get('selection_callback', None)
        self._map_limits = [425.000,448.000, 4510.000, 4533.000]
        self.haz_point = None
        self.prob_point = None
        self._selector = None
        self._areas = None
        self.area_patch_coll = []
        self._sel_minspan = 0.4

        super(HazardGraph, self).__init__(*args, **kwargs)

        self._figure.canvas.mpl_connect('button_press_event',
                                        self.on_press)
        if show_areas:
            self._figure.canvas.mpl_connect('button_release_event',
                                        self.on_release)
        else:
            self._figure.canvas.mpl_connect('pick_event',
                                        self.on_pick)
        self._points_data = None
        self._selected_point = None
        self._selected_areas = []
        self._old_selected_areas = []

    def draw_point(self, x, y):
        self.haz_point.set_data(x, y)
        self.haz_point.set_visible(True)
        self.prob_point.set_data(x, y)
        self.prob_point.set_visible(True)
        self._canvas.draw()

    def clear(self):
        self._figure.clf()
        self._canvas.draw()

    def plot(self, hazard,  hazard_data, inventory):
        # Prepare matplotlib grid and data
        grid_points_number = 256
        points_utm = [p['point'] for p in hazard_data]
        self.x_points = [p['easting']*1e-3 for p in points_utm]
        self.y_points = [p['northing']*1e-3 for p in points_utm]
        x_vector = np.linspace(min(self.x_points), max(self.x_points), grid_points_number)
        y_vector = np.linspace(min(self.y_points), max(self.y_points), grid_points_number)
        x_mesh, y_mesh = np.meshgrid(x_vector, y_vector)

        self._figure.clf()
        # self._figure.subplots_adjust(left=0.1, bottom=0.1, right=0.96,
        #                              top=0.92, wspace=0.35, hspace=0.2)
        self._figure.hold(True)
        gridspec = pyplot.GridSpec(1, 2)
        gridspec.update(wspace=0.4, left=0.07, right=.93)
        subplot_spec = gridspec.new_subplotspec((0, 0))
        subplot = self._figure.add_subplot(subplot_spec)
        self.haz_map = self.plot_hazard_map(subplot,
                             [p['haz_value'] for p in hazard_data],
                             hazard, inventory)

        self.haz_point,  = self.haz_map.plot([self.x_points[0]],
                                                  [self.y_points[0]],
                                                  'o', ms=8,
                                                  alpha=0.8,
                                                  color='m',
                                                  visible=False,
                                                  zorder=10)


        subplot_spec = gridspec.new_subplotspec((0, 1))
        subplot = self._figure.add_subplot(subplot_spec)
        self.prob_map = self.plot_probability_map(subplot,
                                  [p['prob_value'] for p in hazard_data])

        self.prob_point,  = self.prob_map.plot([self.x_points[0]],
                                                  [self.y_points[0]],
                                                  'o', ms=8,
                                                  alpha=0.8,
                                                  color='m',
                                                  visible=False,
                                                  zorder=5)

        self._canvas.draw()



    def plot_hazard_map(self, subplot, z_points,
                 hazard, inventory):
        # Define colors mapping and levels
        z_boundaries = self.levels_boundaries(z_points)
        cmap_norm_index = mpl.colors.BoundaryNorm(z_boundaries,
                                                  self._cmap.N)
        # Add hazard map subfigure
        haz_subplot = subplot
        # haz_subplot = self._figure.add_subplot(1, 2, 1)

        self._selector = RectangleSelector(haz_subplot, self.on_select,
                                     drawtype='box',
                                     minspanx=self._sel_minspan,
                                     minspany=self._sel_minspan,
                                     rectprops=dict(alpha=0.5,
                                                      facecolor='c',
                                                      zorder = 10),
                                     button=1,
                                     spancoords='data')

        # haz_subplot.add_artist(self._sel_rect)

        # TODO: tmp image plot
        img = pyplot.imread(self._imgfile)
        haz_subplot.imshow(
            img,
            zorder=0,
            origin="upper",
            extent=self._map_limits)


        # Add inventory areas to subplot
        if show_areas:
            self._areas= []
            for sec in inventory.sections:
                _area_tmp=dict(patch = None,
                                section = None)
                geometry_array =  np.array([[float(coord)*1e-3
                                    for coord in v]
                                        for v in sec.geometry])
                _area_tmp['patch'] = mpl.patches.PathPatch(mpl.path.Path(
                    geometry_array,closed=True), facecolor='c',
                                              linewidth=0.1,
                                              zorder = 5,
                                              alpha = 0.4)
                _area_tmp['inventory'] = sec
                self._areas.append(_area_tmp)

            self.area_patch_coll = mcoll.PatchCollection(
                [a['patch'] for a in self._areas],
                facecolor='none',
                color = 'w',
                linewidths=0.2,
                zorder=5,
                alpha=0.8)
            haz_subplot.add_collection(self.area_patch_coll)

        # Plot hazard map
        haz_scatter = haz_subplot.scatter(self.x_points, self.y_points, marker='.',
                                          c = z_points,
                                          cmap=self._cmap,
                                          alpha=0.7,
                                          zorder=4,
                                          picker=5,
                                          linewidths=0)

        # Plot hazard bar
        divider = make_axes_locatable(haz_subplot)
        cax = divider.append_axes("right", size="5%", pad=0.3)
        hazard_bar = self._figure.colorbar(
            haz_scatter,
            cax=cax,
            norm=cmap_norm_index,
            ticks=z_boundaries,
            boundaries=z_boundaries,
            format='%.3f')

        hazard_bar.set_alpha(1)
        hazard_bar.set_label(hazard.imt, labelpad=-60)
        hazard_bar.draw_all()

        haz_subplot.set_title("Hazard Map\n", fontsize=12)
        haz_subplot.set_xlabel("Easting (km)")
        haz_subplot.set_ylabel("Northing (km)")
        haz_subplot.axis(self._map_limits)
        return haz_subplot

    def plot_probability_map(self, subplot, z_points):

        # Define colors mapping and levels
        z_boundaries = self.levels_boundaries(z_points)
        cmap_norm_index = mpl.colors.BoundaryNorm(z_boundaries,
                                                  self._cmap.N)

        prob_subplot = subplot
        # prob_subplot = self._figure.add_subplot(1, 2, 2)
        img = pyplot.imread(self._imgfile)
        prob_subplot.imshow(
            img,
            origin="upper",
            extent=self._map_limits)
        
        prob_scatter = prob_subplot.scatter(self.x_points, self.y_points,
                                            marker='.', c = z_points,
                                            cmap=self._cmap,
                                            alpha=0.7,
                                            zorder=2,
                                            picker=5,
                                            linewidths = 0)

        divider = make_axes_locatable(prob_subplot)
        cax = divider.append_axes("right", size="5%", pad=0.3)
        probability_bar = self._figure.colorbar(
            prob_scatter,
            cax=cax,
            orientation='vertical')

        probability_bar.set_alpha(1)
        probability_bar.set_label("Probability", labelpad=-60)
        prob_subplot.set_title("Probability Map\n", fontsize=12)
        prob_subplot.set_xlabel("Easting (km)")
        probability_bar.draw_all()
        prob_subplot.axis(self._map_limits)
        return prob_subplot

    def on_pick(self, event):
        x = event.mouseevent.xdata
        y = event.mouseevent.ydata
        ind = bf.nearest_point_index(x, y, self.x_points, self.y_points)
        self._click_callback(ind)

    def on_press(self, event):
        self.x0 = event.xdata
        self.y0 = event.ydata

    def on_release(self, event):
        x = event.xdata
        y = event.ydata
        if (abs(x-self.x0) < self._sel_minspan) and \
            (abs(x-self.x0) < self._sel_minspan):
                # self._sel_rect.set_visible(False)
                ind = bf.nearest_point_index(x, y, self.x_points, self.y_points)
                for path_index in range(len(self.area_patch_coll.get_paths())):
                        if self.area_patch_coll.get_paths()[path_index].\
                                contains_point((x, y)):
                            self._click_callback(ind, pathID=path_index)

    def on_select(self, eclick, erelease):
        'eclick and erelease are matplotlib events at press and release'
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        x_min = min(x1, x2)
        y_min = min(y1, y2)
        x_max = max(x1, x2)
        y_max = max(y1, y2)
        self._canvas.draw()
        _points = [(self.x_points[i],self.y_points[i])
                  for i in range(len(self.x_points)) ]
        _sel_points = [p for p in _points
                       if (x_min<=p[0]<=x_max) and (y_min<=p[1]<=y_max)]
        ind = bf.nearest_point_index(x_min+(x_max-x_min)/2,
                                     y_min+(y_max-y_min)/2,
                                     self.x_points,
                                     self.y_points)
        _nearest_centroid_index = bf.nearest_point_index(x_min+(x_max-x_min)/2,
                                                         y_min+(y_max-y_min)/2,
                                     [a['inventory'].centroid[0]*1e-3 for a in
                                        self._areas],
                                     [a['inventory'].centroid[1]*1e-3 for a in
                                        self._areas])
        print "index %s" % ind
        print "nearest_centroid_index %s" % _nearest_centroid_index
        # Select an area if at least one of the selected point is inside it
        # Doing this areas with no point are never selected
        # if len(_sel_points) <= 0:
        #     _sel_points = [(self.x_points[ind], self.y_points[ind])]
        # _areas_list = [i_p for i_p in range(len(self._areas))
        #          if self._areas[i_p]['patch'].get_path().
        #             contains_points(_sel_points).any()]

        if len(_sel_points) <= 0:
            _sel_points = [(self.x_points[ind], self.y_points[ind])]
        _areas_list = []
        for i_p in range(len(self._areas)):
            cent_x = self._areas[i_p]['inventory'].centroid[0]*1e-3
            cent_y = self._areas[i_p]['inventory'].centroid[1]*1e-3
            if (x_min<=cent_x<=x_max) and (y_min<=cent_y<=y_max):
                if i_p == _nearest_centroid_index:
                    _areas_list.insert(0,self._areas[i_p])
                    print "nearest , index = %s, areaID %s " % \
                          (i_p, self._areas[i_p]['inventory'].areaID)
                else:
                    _areas_list.append(self._areas[i_p])
        print "first index %s" % _areas_list[0]['inventory'].areaID
        self._selection_callback(ind, _areas_list)



        
    def levels_boundaries(self, z_array):
        max_intervals = 5
        maxz = np.ceil(max(z_array))
        minz = np.floor(min(z_array))
        # print "z_array max: %s" % maxz
        # print "z_array min: %s" % minz

        if (maxz - minz) < 4:
            inter = 0.2
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

    def update_selection(self):
        self.draw_point(self.selected_point[0],
                        self.selected_point[1])
        for i_a in range(len(self._areas)):
            if i_a in [a['areaID']-1 for a in self._old_selected_areas]:
                try:
                    self._areas[i_a]['patch'].remove()
                except:
                    pass
            if i_a in [a['areaID']-1 for a in self.selected_areas]:
                self.haz_map.add_artist(self._areas[i_a]['patch'])
        self._canvas.draw()


    @property
    def selected_point(self):
        return self._selected_point

    @selected_point.setter
    def selected_point(self, coords):
        self._selected_point = coords


    @property
    def selected_areas(self):
        return self._selected_areas

    @selected_areas.setter
    def selected_areas(self, areas):
        self._old_selected_areas = self.selected_areas
        self._selected_areas = areas


class HazardCurve(BymurPlot):
    def __init__(self, *args, **kwargs):
        super(HazardCurve, self).__init__(*args, **kwargs)

    def plot(self, hazard, hazard_options,
             selected_point):
        perc_to_plot = ["10", "50", "90"]

        self._figure.clf()
        if (selected_point is None) or (hazard is None):
            return
        # self._axes = self._figure.add_axes([0.15, 0.15, 0.75, 0.75])
        gridspec = pyplot.GridSpec(1, 1)
        gridspec.update(bottom=0.15)
        subplot_spec = gridspec.new_subplotspec((0,0))
        self._axes = self._figure.add_subplot(subplot_spec)
        self._figure.hold(True)
        self._axes.grid(True)

        if len(hazard.iml) <10:
            xticks = hazard.iml + [0]
        else:
            xticks = [0] + [hazard.iml[i]
                            for i in range(len(hazard.iml))
                            if i%2==0]

        self._axes.set_xlabel(hazard.imt)
        self._axes.set_xticks(xticks)
        self._axes.tick_params(axis='x', labelsize=8)
        self._axes.set_xlim(left=0,
                            right= hazard.iml[len(hazard.iml)-1])

        for perc in perc_to_plot:
            perc_key = "percentile"+perc
            if selected_point.curves[perc_key] is not None:
                perc_label =  perc + "th Percentile"
                self._axes.plot(hazard.iml,
                                [float(y) for  y in
                                 selected_point.curves[
                                     perc_key].split(',')],
                                linewidth=1,
                                alpha=1,
                                label=perc_label)


        if selected_point.curves["mean"] is not None:
                self._axes.plot(hazard.iml,
                                [float(y) for  y in
                                 selected_point.curves["mean"].split(','
                                                                           '')],
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
        #TODO: forse dovrei aggiungere un id del punto?
        title = ("Point index: " + str(selected_point.index) +
               " - Time window = " + str(hazard_options['exp_time']) + " "
                                                                        "years")
        self._axes.set_title(title, fontsize=12)
        self._axes.set_ylabel("Probability of Exceedance")
        self._axes.set_yscale("log")
        # self.axes.axis([0,1,0,1])
        self._canvas.draw()

class FragCurve(BymurPlot):

    def __init__(self, *args, **kwargs):
        super(FragCurve, self).__init__(*args, **kwargs)

    def plot(self, **kwargs ):
        self._hazard = kwargs.pop('hazard', None)
        self._fragility = kwargs.pop('fragility', None)
        self._inventory = kwargs.pop('inventory', None)
        self._areas= kwargs.pop('areas', None)

        self._figure.clf()

        if len(self._areas) == 0:
            print "Warning: no area selected"
        elif len(self._areas) > 1:
            print "Warning: multiple areas selected, plotting data just for " \
                  "area %s " % self._areas[0]['areaID']
            self._area = self._areas[0]
        else:
            self._area = self._areas[0]

        if (self._inventory is None) or (self._fragility is None) or \
                (self._area['inventory'] is None) or \
                (self._area['fragility'] is None) or \
                (self._area['inventory'].asset.total == 0):
            self._canvas.draw()
            return

        # here order of classes is important!
        area_class_set = set([af['general_class'] for af in
                              self._area['fragility']])
        area_general_classes = [c.name for c in self._inventory.classes[
                                            'generalClasses']
                              if c.name in  area_class_set]

        row_num = len(self._fragility.limit_states)
        col_num = len(area_general_classes)
        gridspec = pyplot.GridSpec(row_num, col_num)
        gridspec.update(hspace = 0.6)
        for i_row in range(row_num):
            for i_col in range(col_num):

                subplot_spec = gridspec.new_subplotspec((i_row, i_col))
                subplot_tmp = self._figure.add_subplot(subplot_spec)


                for c in self._area['fragility']:
                    if (c['limit_state'] == self._fragility.limit_states[i_row]) \
                            and (c['general_class'] ==
                                     area_general_classes[i_col]):
                        # print "dentro if: %s, %s" % (c['limit_state'],
                        #                              c['general_class'])
                        # subplot_tmp.plot([1, 2])

                        if c['statistic'] in self._stat_to_plot:
                            # print "%s: %s " % (c['statistic'], [float(y) for
                            #                                     y in
                            #                  c['fragility_curve'].split(" ")])
                            subplot_tmp.plot(self._fragility.iml,
                                            [float(y) for  y in
                                             c['fragility_curve'].split(" ")],
                                            linewidth=1,
                                            alpha=1,
                                            label = c['statistic'],
                                            color = self._stat_colors[
                                                self._stat_to_plot.index(c[
                                                    'statistic'])])
                        subplot_tmp.tick_params(axis='x', labelsize=8)
                        subplot_tmp.tick_params(axis='y', labelsize=8)
                        subplot_tmp.set_xlabel(self._hazard.imt, fontsize=9,
                                               labelpad=-2)
                        subplot_tmp.set_ylabel("Exceedance pobability",
                                               fontsize=9)
                        subplot_tmp.set_ylim((0,1.05))
                        # print subplot_tmp
                        subplot_tmp.set_title("Prob. of " + c['limit_state'] +
                                              " for " + c['general_class'],
                                                  fontsize=9)
                subplot_tmp.legend(loc=2, prop={'size':6})
        # gridspec.tight_layout(self._figure)
        self._canvas.draw()


class LossCurve(BymurPlot):

    def __init__(self, *args, **kwargs):
        super(LossCurve, self).__init__(*args, **kwargs)

    def plot(self, **kwargs):
        self._hazard = kwargs.pop('hazard', None)
        self._inventory = kwargs.pop('inventory', None)
        self._fragility = kwargs.pop('fragility', None)
        self._loss = kwargs.pop('loss', None)
        self._areas = kwargs.pop('areas', None)
        self._figure.clf()

        if len(self._areas) == 0:
            print "Warning: no area selected"
        elif len(self._areas) > 1:
            print "Warning: multiple areas selected, plotting data just for " \
                  "area %s " % self._areas[0]['areaID']
            self._area = self._areas[0]
        else:
            self._area = self._areas[0]

        if (self._inventory is None) or (self._fragility is None) or \
                (self._loss is None) or \
                (self._area['inventory'] is None) or \
                (self._area['fragility'] is None) or \
                (self._area['loss'] is None) or \
                (self._area['inventory'].asset.total == 0):
            self._canvas.draw()
            return

        row_num = len(self._fragility.limit_states)
        gridspec = pyplot.GridSpec(row_num, 1)
        gridspec.update(hspace = 0.6)
        subplot_list = []
        for i_row in range(row_num):
            subplot_spec = gridspec.new_subplotspec((i_row, 0))
            subplot_tmp = self._figure.add_subplot(subplot_spec)
            for c in self._area['loss']:
                if c['limit_state'] == self._fragility.limit_states[i_row]:
                    if c['statistic'] in self._stat_to_plot:
                        loss_x_values = [float(p.split(" ")[0]) for p in
                                          c['loss_function'].split(",")]
                        loss_y_values = [float(p.split(" ")[1]) for p in
                                          c['loss_function'].split(",")]
                        subplot_tmp.plot(loss_x_values,
                                         loss_y_values,
                                         linewidth=1,
                                         alpha=1,
                                         label = c['statistic'],
                                         color = self._stat_colors[
                                             self._stat_to_plot.index(c[
                                                 'statistic'])])
                    subplot_tmp.tick_params(axis='x', labelsize=8)
                    subplot_tmp.set_xlabel(self._loss.unit, fontsize=9,
                                           labelpad=-2)
                    subplot_tmp.tick_params(axis='y', labelsize=8)
                    subplot_tmp.set_ylabel("Exceedance probability", fontsize=9)
                    subplot_tmp.set_ylim((0, 1.05))
                    # print subplot_tmp
                    subplot_tmp.set_title("Prob. of loss given " + c[
                        'limit_state'], fontsize=10)
            subplot_tmp.legend(loc=1, prop={'size':6})
            subplot_list.append(subplot_tmp)
        # gridspec.tight_layout(self._figure)
        self._canvas.draw()


class RiskCurve(BymurPlot):
    risk_colors = ['r', 'c', 'g', 'y']
    risk_linestyles = ['-', '-.', '--', ':']

    def __init__(self, *args, **kwargs):
        super(RiskCurve, self).__init__(*args, **kwargs)

    def plot(self, **kwargs):
        self._hazard = kwargs.pop('hazard', None)
        self._inventory = kwargs.pop('inventory', None)
        self._fragility = kwargs.pop('fragility', None)
        self._loss = kwargs.pop('loss', None)
        self._risk = kwargs.pop('risk', None)
        self._compare_risks = kwargs.pop('compare_risks', None)
        self._areas = kwargs.pop('areas', None)
        self._figure.clf()

        if len(self._areas) == 0:
            print "Warning: no area selected"
        elif len(self._areas) == 1:
            self._area = self._areas[0]


            print "compare risks: %s" % [r.model_name for r in self._compare_risks]
            if (self._inventory is None) or (self._fragility is None) or \
                    (self._loss is None) or (self._risk is None) or \
                    (self._area['inventory'] is None) or \
                    (self._area['fragility'] is None) or \
                    (self._area['loss'] is None) or \
                    (self._area['risk'] is None) or \
                    (self._area['inventory'].asset.total == 0):
                self._canvas.draw()
                return

            gridspec = pyplot.GridSpec(1, 2)
            gridspec.update(wspace = 0.4, bottom=0.15)
            # Plot risk curve
            subplot_spec = gridspec.new_subplotspec((0, 0))
            subplot_tmp = self._figure.add_subplot(subplot_spec)
            r_handles = []
            for c in self._area['risk']:
                if c['statistic'] in self._stat_to_plot:
                    risk_x_values = [float(p.split(" ")[0]) for p in
                                      c['risk_function'].split(",")]
                    risk_y_values = [float(p.split(" ")[1]) for p in
                                      c['risk_function'].split(",")]
                    subplot_tmp.plot(risk_x_values,
                                     risk_y_values,
                                     linewidth=1,
                                     alpha=1,
                                     linestyle=self.risk_linestyles[
                                         self._stat_to_plot.index(c[
                                             'statistic'])],
                                     color='k')
                    l, = pyplot.plot([], label=c['statistic'],
                                     linestyle=self.risk_linestyles[
                                         self._stat_to_plot.index(c[
                                             'statistic'])],
                                     color='k')
                    r_handles.append(l)

            cr_handles = []
            for i_r in range(len(self._area['compare_risks'])):
                for c in self._area['compare_risks'][i_r]:
                    if c['statistic'] in self._stat_to_plot:
                        risk_x_values = [float(p.split(" ")[0]) for p in
                                          c['risk_function'].split(",")]
                        risk_y_values = [float(p.split(" ")[1]) for p in
                                          c['risk_function'].split(",")]
                        subplot_tmp.plot(risk_x_values,
                                         risk_y_values,
                                         linewidth=1,
                                         alpha=1,
                                         linestyle=self.risk_linestyles[
                                             self._stat_to_plot.index(c[
                                                 'statistic'])],
                                         color=self.risk_colors[i_r])
                l, = pyplot.plot([], label=self._compare_risks[i_r].model_name,
                                 color=self.risk_colors[i_r])
                cr_handles.append(l)

            if len(cr_handles) > 0:
                l, = pyplot.plot([], label=self._risk.model_name,
                                 color = 'k')
                cr_handles.append(l)
                cr_legend = pyplot.legend(handles=cr_handles, loc=1,
                                          prop={'size':6})
                # Add the legend manually to the current Axes.
                ax = pyplot.gca().add_artist(cr_legend)

            # subplot_tmp.legend(handles=r_handles, loc=1, prop={'size':6})
            subplot_tmp.legend(handles=r_handles, prop={'size':6},
                               bbox_to_anchor=(0., 1, 1.,.10), loc=3,
                        ncol=len(r_handles), mode="expand", borderaxespad=0.)
            subplot_tmp.set_yscale('log')
            subplot_tmp.set_xlabel("Loss("+self._loss.unit+")")
            subplot_tmp.set_ylabel("Exceedance probability")
            subplot_tmp.tick_params(axis='x', labelsize=8)
            subplot_tmp.tick_params(axis='y', labelsize=8)
            subplot_tmp.set_title("Risk curve", y=1.05, fontsize=12)

            # Plot risk index
            subplot_spec = gridspec.new_subplotspec((0, 1))
            subplot_tmp = self._figure.add_subplot(subplot_spec)
            values = []
            r_handles = []
            for c in self._area['risk']:
                if c['statistic'] == 'mean':
                    subplot_tmp.axvline(
                        x=float(c['average_risk']),
                        color='k',
                        linewidth=1,
                        alpha=1)
                    l, = pyplot.plot([], label="Mean",
                                 color='k')
                    r_handles.append(l)
                else:
                    values.append((c['average_risk'],
                                   float(c['statistic'][len("quantile"):])/100))

            values = sorted(values, key = lambda val: val[0])
            subplot_tmp.plot([v[0] for v in values],
                             [v[1] for v in values],
                             linewidth=1,
                             linestyle='-.',
                             alpha=1,
                             color = 'k')
            l, = pyplot.plot([], label="Percentiles",
                                 color = 'k',linestyle='-.' )
            r_handles.append(l)

            # plot other risks for comparison
            print "compare risks len %s " % len(self._area['compare_risks'])
            cr_handles = []
            for i_r in range(len(self._area['compare_risks'])):
                values = []
                for c in self._area['compare_risks'][i_r]:
                    if c['statistic'] == 'mean':
                        subplot_tmp.axvline(
                            x=float(c['average_risk']),
                            color=self.risk_colors[i_r],
                            linewidth=1,
                            alpha=1)
                    else:
                        values.append((c['average_risk'],
                                       float(c['statistic'][len("quantile"):])/100))

                values = sorted(values, key = lambda val: val[0])
                subplot_tmp.plot([v[0] for v in values],
                                 [v[1] for v in values],
                                 linewidth=1,
                                 linestyle='-.',
                                 alpha=1,
                                 color=self.risk_colors[i_r])
                l, = pyplot.plot([], label=self._compare_risks[i_r].model_name,
                                 color = self.risk_colors[i_r])
                cr_handles.append(l)
            subplot_tmp.set_title("Risk index", y=1.05, fontsize=12)
            if len(cr_handles) > 0:
                l, = pyplot.plot([], label=self._risk.model_name,
                                 color = 'k')
                cr_handles.append(l)
                cr_legend = pyplot.legend(handles=cr_handles, loc=4,
                                          prop={'size':6})
                # Add the legend manually to the current Axes.
                ax = pyplot.gca().add_artist(cr_legend)

            subplot_tmp.legend(handles=r_handles, prop={'size':6},
                                   bbox_to_anchor=(0., 1, 1.,.10), loc=3,
                            ncol=len(r_handles), mode="expand", borderaxespad=0.)
            subplot_tmp.set_ylim((0,1))
            subplot_tmp.set_xscale("log")
            subplot_tmp.set_xlabel("Loss("+self._loss.unit+")")
            subplot_tmp.set_ylabel("Percentile")
            subplot_tmp.tick_params(axis='x', labelsize=8)
            subplot_tmp.tick_params(axis='y', labelsize=8)

        elif len(self._areas) > 1: # multiple areas selected
            print "Multiple areas selected, plotting just risk index "
            self._ind_area = bf.aggregated_indipendent(self._areas)
            self._corr_area = bf.aggregated_correlated(self._areas)
            gridspec = pyplot.GridSpec(1, 1)
            gridspec.update(wspace = 0.4, bottom=0.15)
            subplot_spec = gridspec.new_subplotspec((0, 0))
            subplot_tmp = self._figure.add_subplot(subplot_spec)
            values = []
            r_handles = []
            for c in self._ind_area['risk']:
                if c['statistic'] == 'mean':
                    subplot_tmp.axvline(
                        x=float(c['average_risk']),
                        color='k',
                        linewidth=1,
                        alpha=1)
                    l, = pyplot.plot([], label="Indipendent mean",
                                 color = 'k')
                    r_handles.append(l)
                else:
                    values.append((c['average_risk'],
                                   float(c['statistic'][len("quantile"):])/100))

            values = sorted(values, key = lambda val: val[0])
            subplot_tmp.plot([v[0] for v in values],
                             [v[1] for v in values],
                             linewidth=1,
                             linestyle='-.',
                             alpha=1,
                             color = 'k')
            l, = pyplot.plot([], label="Indipendent percentiles",
                                 color = 'k',linestyle='-.' )
            r_handles.append(l)

            values=[]
            for c in self._corr_area['risk']:
                if c['statistic'] == 'mean':
                    if c['statistic'] == 'mean':
                        subplot_tmp.axvline(
                            x=float(c['average_risk']),
                            color='k',
                            linestyle='--',
                            linewidth=1,
                            alpha=1)
                        l, = pyplot.plot([], label="Correlated mean",
                                     linestyle='--', color='k')
                        r_handles.append(l)
                else:
                    values.append((c['average_risk'],
                                   float(c['statistic'][len("quantile"):])/100))
            values = sorted(values, key = lambda val: val[0])
            subplot_tmp.plot([v[0] for v in values],
                             [v[1] for v in values],
                             linewidth=1,
                             linestyle=':',
                             alpha=1,
                             color = 'k')
            l, = pyplot.plot([], label="Correlated perc.",
                               color='k', linestyle=':')
            r_handles.append(l)

            # plot other risks for comparison
            print "compare risks len %s " % len(self._ind_area['compare_risks'])
            cr_handles = []
            for i_r in range(len(self._ind_area['compare_risks'])):
                values = []
                for c in self._ind_area['compare_risks'][i_r]:
                    if c['statistic'] == 'mean':
                        subplot_tmp.axvline(
                            x=float(c['average_risk']),
                            color=self.risk_colors[i_r],
                            linewidth=1,
                            alpha=1)
                    else:
                        values.append((c['average_risk'],
                                       float(c['statistic'][len("quantile"):])/100))

                values = sorted(values, key = lambda val: val[0])
                subplot_tmp.plot([v[0] for v in values],
                                 [v[1] for v in values],
                                 linewidth=1,
                                 linestyle='-.',
                                 alpha=1,
                                 color=self.risk_colors[i_r])
                l, = pyplot.plot([], label=self._compare_risks[i_r].model_name,
                                   linestyle='-.', color=self.risk_colors[i_r])
                cr_handles.append(l)

                values = []
                for c in self._corr_area['compare_risks'][i_r]:
                    if c['statistic'] == 'mean':
                        subplot_tmp.axvline(
                            x=float(c['average_risk']),
                            color=self.risk_colors[i_r],
                            linestyle='--',
                            linewidth=1,
                            alpha=1)
                    else:
                        values.append((c['average_risk'],
                                       float(c['statistic'][len("quantile"):])/100))

                values = sorted(values, key = lambda val: val[0])
                subplot_tmp.plot([v[0] for v in values],
                                 [v[1] for v in values],
                                 linewidth=1,
                                 linestyle=':',
                                 alpha=1,
                                 color=self.risk_colors[i_r])

            subplot_tmp.set_title("Aggregated risk index", y=1.05,
                                  fontsize=12)

            if len(cr_handles) > 0:
                l, = pyplot.plot([], label=self._risk.model_name,
                                 color = 'k')
                cr_handles.append(l)
                cr_legend = pyplot.legend(handles=cr_handles, loc=4,
                                          prop={'size':6})
                # Add the legend manually to the current Axes.
                ax = pyplot.gca().add_artist(cr_legend)

            subplot_tmp.legend(handles=r_handles, prop={'size':6},
                                   bbox_to_anchor=(0., 1, 1.,.10), loc=3,
                            ncol=len(r_handles), mode="expand", borderaxespad=0.)
            subplot_tmp.set_ylim((0,1))
            subplot_tmp.set_xscale("log")
            subplot_tmp.set_xlabel("Loss("+self._loss.unit+")")
            subplot_tmp.set_ylabel("Percentile")
            subplot_tmp.tick_params(axis='x', labelsize=8)
            subplot_tmp.tick_params(axis='y', labelsize=8)


        self._canvas.draw()


class InvCurve(BymurPlot):

    _colors = ['#fff7ec', '#fee8c8', '#fdd49e', '#fdbb84', '#fc8d59',
               '#ef6548', '#d7301f', '#b30000', '#7f0000']
    # _bar_colors = ['#762a83', '#af8dc3', '#e7d4e8', '#d9f0d3',
    #                '#7fbf7b','#1b7837']
    _bar_colors = ['#1b9e77', '#d95f02', '#7570b3', '#e7298a', '#66a61e',
                   '#e6ab02']

    def __init__(self, *args, **kwargs):
        super(InvCurve, self).__init__(*args, **kwargs)

    def plot(self, **kwargs):
        self._hazard = kwargs.pop('hazard', None)
        self._inventory = kwargs.pop('inventory', None)
        self._areas = kwargs.pop('areas', None)
        self._figure.clf()

        if len(self._areas) == 0:
            print "Warning: no area selected"
            self._canvas.draw()
            return
        elif len(self._areas) > 1:
            print "Warning: multiple areas selected, plotting data just for " \
                  "area %s " % self._areas[0]['areaID']
            self._area = self._areas[0]
        else:
            self._area = self._areas[0]

        if (self._inventory is None) or \
                (self._area['inventory'] is None) or \
                (self._area['inventory'].asset.total <= 0):
            print "Inventory exiting"
            self._canvas.draw()
            return

        subplot_arr = []
        #if there area any builging, plot fragility and cost classes probability

        # Fragility class probabilities
        gridspec = pyplot.GridSpec(2, 2)
        gridspec.update(hspace = 0.4)
        subplot_spec = gridspec.new_subplotspec((0, 0))
        subplot_tmp = self._figure.add_subplot(subplot_spec)
        width=0.2
        subplot_tmp.set_xlim((0, width*len(self._inventory.classes[
            'fragilityClasses'][self._hazard.phenomenon_name.lower()])))
        ticks = np.arange(0,width*len(self._inventory.classes[
            'fragilityClasses'][self._hazard.phenomenon_name.lower()]),
                  width) + (width/2)
        subplot_tmp.set_title("Fragility class probability", fontsize=12)
        subplot_tmp.set_xticks(ticks)
        subplot_tmp.set_xticklabels([cl.label for cl in
                                self._inventory.classes['fragilityClasses'][
                                    self._hazard.phenomenon_name.lower()]])
        subplot_tmp.set_ylim((0,1))

        for i_class in range(len(self._inventory.classes['fragilityClasses'][
            self._hazard.phenomenon_name.lower()])):
            subplot_tmp.bar(i_class*width,
                np.float(self._area['inventory'].asset.frag_class_prob[
                    self._hazard.phenomenon_name.lower()]['fnt'][i_class]),
                width, color=self._colors[i_class],
                label=self._inventory.classes['fragilityClasses'][
                    self._hazard.phenomenon_name.lower()][i_class].label)
        subplot_arr.append(subplot_tmp)

        # Cost class probabilities
        subplot_spec = gridspec.new_subplotspec((0, 1))
        subplot_tmp = self._figure.add_subplot(subplot_spec)
        subplot_tmp.set_ylim((0,1))
        subplot_tmp.set_xlim((0,
            width*len(self._inventory.classes['costClasses'][
            self._hazard.phenomenon_name.lower()])))
        ticks = np.arange(0,width*len(self._inventory.classes[
        'costClasses'][self._hazard.phenomenon_name.lower()]),
              width) + (width/2)
        subplot_tmp.set_title("Cost class probability", fontsize=12)
        subplot_tmp.set_xticks(ticks)
        subplot_tmp.set_xticklabels([cl.label for cl in
                            self._inventory.classes['costClasses'][
                                self._hazard.phenomenon_name.lower()]])
        for i_class in range(len(self._inventory.classes['costClasses'][
            self._hazard.phenomenon_name.lower()])):
            subplot_tmp.bar(i_class*width,
                np.float(self._area['inventory'].asset.cost_class_prob[
                    self._hazard.phenomenon_name.lower()]['fnc'][i_class]),
                width, color=self._colors[i_class],
                label=self._inventory.classes['costClasses'][
                    self._hazard.phenomenon_name.lower()][i_class].name)
        subplot_arr.append(subplot_tmp)

        # Plot the probability to be in a specific fragility class given
        # a certain generic class (plotted with the same color accross
        # differents target fragility class ==> same bar color sum == 1)
        subplot_spec = gridspec.new_subplotspec((1, 0), colspan=2)
        subplot_tmp = self._figure.add_subplot(subplot_spec)
        subplot_tmp.set_title("Fragility given class", fontsize=12)
        ticks = np.arange(0,width*len(self._inventory.classes[
            'fragilityClasses'][self._hazard.phenomenon_name.lower()]),
                  width) + (width/2)

        subplot_tmp.set_xticks(ticks)
        subplot_tmp.set_xticklabels([cl.label for cl in
                                self._inventory.classes['fragilityClasses'][
                                    self._hazard.phenomenon_name.lower()]])
        subplot_tmp.set_ylim((0,1))
        bar_width=0.05

        if (len(self._inventory.classes['generalClasses'])%2 != 0 ):
            bar_offset = bar_width/2
        else:
            bar_offset = 0
        for i_class in range(len(self._inventory.classes['fragilityClasses'][
            self._hazard.phenomenon_name.lower()])):
            sub_probs = [float(x) for x  in self._area['inventory'].asset.frag_class_prob[
                self._hazard.phenomenon_name.lower()][
                'fntGivenGeneralClass'][i_class]]
            for i_p in range(len(sub_probs)):
                subplot_tmp.bar(i_class*width+bar_width*i_p+bar_offset,
                    sub_probs[i_p], bar_width, color=self._bar_colors[
                        i_p] )

        # Build legend for graph
        legend_handles = []
        for i_leg in \
            range(len(self._inventory.classes['generalClasses'])):
            lh_tmp = mpl.patches.Patch(color=self._bar_colors[i_leg],
                               label= self._inventory.classes[
                                   'generalClasses'][i_leg].name)
            legend_handles.append(lh_tmp)
        subplot_tmp.legend(handles=legend_handles, prop={'size': 9},
                           frameon = False, labelspacing=0.2,
                           borderaxespad=0.)
        subplot_arr.append(subplot_tmp)
        self._canvas.draw()
