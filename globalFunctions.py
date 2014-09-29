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

import os
import urllib2
from lxml import etree
import wx
import linecache
import sys
import threading
import utm
import numpy as np

import matplotlib as mpl
import matplotlib.mlab as mlab
import matplotlib.pyplot as pyplot
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg



wxBYMUR_UPDATE_CURVE = wx.NewEventType()
wxBYMUR_UPDATE_MAP = wx.NewEventType()
wxBYMUR_UPDATE_DIALOG = wx.NewEventType()
wxBYMUR_UPDATE_CTRLS = wx.NewEventType()
wxBYMUR_UPDATE_ALL = wx.NewEventType()
wxBYMUR_THREAD_CLOSED = wx.NewEventType()
wxBYMUR_DB_CONNECTED = wx.NewEventType()
BYMUR_UPDATE_CURVE = wx.PyEventBinder(wxBYMUR_UPDATE_CURVE)
BYMUR_UPDATE_MAP = wx.PyEventBinder(wxBYMUR_UPDATE_MAP)
BYMUR_UPDATE_DIALOG = wx.PyEventBinder(wxBYMUR_UPDATE_DIALOG)
BYMUR_UPDATE_CTRLS = wx.PyEventBinder(wxBYMUR_UPDATE_CTRLS)
BYMUR_UPDATE_ALL = wx.PyEventBinder(wxBYMUR_UPDATE_ALL)
BYMUR_THREAD_CLOSED = wx.PyEventBinder(wxBYMUR_THREAD_CLOSED)
BYMUR_DB_CONNECTED = wx.PyEventBinder(wxBYMUR_DB_CONNECTED)


def SpawnThread(target, event_type, function, function_args, callback=None,
                    wait_msg='Wait please...'):
        """
        """
        threadId = wx.NewId()
        target.wait(wait_msg=wait_msg)
        worker = BymurThread(target, event_type, function, function_args,
                             callback)
        worker.start()


class BymurUpdateEvent(wx.PyCommandEvent):

    def __init__(self, eventType, id):
        self._callback_fun = None
        self._callback_args = None
        super(BymurUpdateEvent, self).__init__(eventType, id)
        print "id = %s " % id

    def SetCallback(self, callback, **kwargs):
        self._callback_fun = callback
        self._callback_kwargs = kwargs

    def GetCallbackFun(self):
        return self._callback_fun

    def GetCallbackKwargs(self):
        return self._callback_kwargs

class BymurThread(threading.Thread):
    def __init__(self, targetid, event_type, function, function_args, callback):
        self._targetid = targetid
        self._function = function
        self._function_args = function_args
        self._callback = callback
        self._event = BymurUpdateEvent(event_type, 1)
        super(BymurThread, self).__init__()

    def run(self):
        print "Load..."
        self._function(**self._function_args)
        print "target: %s " % self._targetid
        evt_id = self._event.GetEventType()
        print evt_id
        if self._callback:
            print "callback"
            self._callback()
        print "Fire!"
        wx.PostEvent(self._targetid, self._event)


class HazardXMLModel(object):

    def __init__(self, filename, phenomenon,
                 xsd="/hades/dev/bymur/schema/bymur_schema.xsd"):
        self._xsd_file = xsd
        print "%s > itializing file: %s " % (self.__class__.__name__,
                                             filename)
        try:
            xml_schema = etree.XMLSchema(file = self._xsd_file)
            # xmlparser = etree.XMLParser(schema=xml_schema)
            print "Loaded schema: %s " % self._xsd_file
        except Exception as e:
            print "%s is not a valid XSD file" % self._xsd_file
            raise Exception(str(e))

        try:
            xml_schema.assertValid(etree.parse(filename))
            print "%s is a valid XML file" % filename
        except Exception as e:
            print "%s is not a valid XML file" % filename
            raise Exception(str(e))

        self._filename = filename
        self._volcano = ''
        self._model_name = ''
        self._iml_thresholds = []
        self._iml_imt = ''
        self._dtime = ''
        self._statistic = ''
        self._percentile_value = 0
        self._points_values= []
        self._points_coords = []
        self._phenomenon = phenomenon.upper()

        print "Parsing %s" % self._filename
        try:
            self.parse()
        except Exception as e:
            print self.__class__.__name__ + ", error parsing file " + \
                  self._filename +  " : " + str(e)
            raise Exception(str(e))

    def parse(self):
        context = etree.iterparse(self._filename, events=("start", "end"))
        for event, element in context:
            if event == "start":
                if element.tag == 'hazardCurveField':
                    self._statistic = element.get('statistics')
                    if self.statistic == 'percentile':
                        self._percentile_value = float(element.get(
                            'percentileValue', '0'))
                    else:
                        self._percentile_value = 0
                    # print "statistic: %s" % self._statistic
                    # print "percentile: %s" % self._percentile_value

            else:
                if element.tag == 'volcano':
                    self._volcano = element.get('volcanoName')
                    element.clear()
                    # print "volcano: %s" % self._volcano
                elif element.tag == 'model':
                    self._model_name = element.get('Model')
                    # print "model: %s" % self._model_name
                    element.clear()
                elif element.tag == 'timeterm':
                    self._dtime = float(element.get('deltaT').strip('yr'))
                    # print "dtime: %s" % self._dtime
                    element.clear()
                elif element.tag == 'IML':
                    self._iml_imt = element.get('IMT')
                    # print "imt: %s" % self._iml_imt
                    self._iml_thresholds = list(element.text.strip().split())
                    # print "iml_thresholds: %s" % self._iml_thresholds
                    element.clear()
                elif element.tag == 'HCNode':
                    point_pos = {}
                    gml_pos = element.find('.//gmlpos').text.split()
                    point_pos['northing'] = float(gml_pos[0])
                    point_pos['easting']  = float(gml_pos[1])
                    point_val = [float(x) for x in
                                 element.find( './/poE').text.split()]
                    # print "point: %s" % point
                    self._points_coords.append(point_pos)
                    self._points_values.append(point_val)
                    element.clear()
                elif element.tag == 'hazardCurveField':
                    element.clear()
        return True

    @property
    def hazard_schema(self):
        return self.hazard_schema

    @property
    def filename(self):
        return self._filename

    @property
    def volcano(self):
        return self._volcano

    @property
    def model_name(self):
        return self._model_name

    @property
    def iml_thresholds(self):
        return self._iml_thresholds

    @property
    def iml_imt(self):
        return self._iml_imt

    @property
    def dtime(self):
        return self._dtime

    @property
    def statistic(self):
        return self._statistic

    @property
    def percentile_value(self):
        return self._percentile_value

    @property
    def points_values(self):
        return self._points_values

    @property
    def points_coords(self):
        return self._points_coords

    @property
    def phenomenon(self):
        return self._phenomenon


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


class HazardCurve(BymurPlot):
    def __init__(self, *args, **kwargs):
        super(HazardCurve, self).__init__(*args, **kwargs)
        # self._parent = parent
        # self._figure = pyplot.figure()
        # self.canvas = FigureCanvasWxAgg(self._parent, -1, self._figure)
        # self._toolbar = NavigationToolbar2WxAgg(self._canvas)
        # self._figure.clf()
        # self._figure.subplots_adjust(left=None, bottom=None, right=None,
        #                             top=None, wspace=None, hspace=0.3)
        # self.fig.hold(True)
        # self.canvas.SetSize(self._parent.GetSize())
        # self.canvas.draw()

    def plot(self, points_data):
        pass

class HazardGraph(BymurPlot):
    def __init__(self, *args, **kwargs):
        super(HazardGraph, self).__init__(*args, **kwargs)
        # TODO: imgfile should be a parameter, but maybe in plot
        self._imgfile = "/hades/dev/bymur/data/naples_gmaps.png"

    def plot(self, points_data):

        # TODO: to transform in a parameter

        print "points_data: %s" % points_data
        # Prepare matplotlib grid and data
        grid_points_number = 100
        points_utm = points_to_utm([p['point'] for p in points_data])
        x_points = [p['easting'] for p in points_utm]

        # TODO: fix these points
        x_points = [x/1000 for x in x_points]
        y_points = [p['northing'] for p in points_utm]
        y_points = [x/1000 for x in y_points]
        x_vector = np.linspace(min(x_points), max(x_points), grid_points_number)
        y_vector = np.linspace(min(y_points), max(y_points), grid_points_number)
        x_mesh, y_mesh = np.meshgrid(x_vector, y_vector)



        self._figure.clf()
        self._figure.subplots_adjust(left=0.1, bottom=0.1, right=0.96,
                                     top=0.92, wspace=0.35, hspace=0.2)
        self._figure.hold(True)
        map_limits = [375.300, 508.500, 4449.200, 4569.800]
        self.plot_hazard_map(x_points, y_points, x_mesh, y_mesh,
                             [p['haz_value'] for p in points_data],
                             map_limits)
        
        self.plot_probability_map(x_points, y_points, x_mesh, y_mesh,
                                  [p['prob_value'] for p in points_data],
                                  map_limits)

        self._canvas.draw()

    def plot_hazard_map(self, x_points, y_points, x_mesh, y_mesh, z_points,
                 map_limits):
        xmap1, xmap2, ymap1, ymap2 = map_limits
        haz_bar_label = "Etichetta barra"
        # TODO: install natgrid to use natural neighbor interpolation
        z_mesh = mlab.griddata(x_points, y_points, z_points, x_mesh, y_mesh,
                               interp='linear')

        # Define colors mapping and levels
        z_boundaries = self.levels_boundaries(z_points)
        print "plot> z_boundaries: %s" % z_boundaries
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
        haz_subplot.axis([425.000,448.000, 4510.000,
                                      4533.000])

    def plot_probability_map(self, x_points, y_points, x_mesh, y_mesh, z_points,
                 map_limits):

        xmap1, xmap2, ymap1, ymap2 = map_limits
        z_mesh = mlab.griddata(x_points, y_points, z_points, x_mesh, y_mesh,
                               interp='linear')

        # Define colors mapping and levels
        z_boundaries = self.levels_boundaries(z_points)
        print "plot> z_boundaries: %s" % z_boundaries
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

        
    def levels_boundaries(self, z_array):
        max_intervals = 5
        maxz = np.ceil(max(z_array))
        minz = np.floor(min(z_array))
        print "maxz %s" %maxz
        print "minz %s" %minz

        if (maxz - minz) < 4:
            inter = 0.2
        elif maxz < 10:
            inter = 1.
            maxz = max(maxz, 3.)
        else:
            order = np.floor(np.log10(maxz - minz)) - 1
            inter = 1. * 10 ** (order)
        print 'range-->', minz, maxz, inter

        chk = len(np.arange(minz, maxz, inter))
        itmp = 1
        while chk > max_intervals:
            itmp = itmp + 1
            inter = inter * itmp
            bounds = range(int(minz), int(maxz), int(inter))
            chk = len(bounds)
        maxz = minz + chk * inter
        # bounds = np.linspace(minz, maxz, chk + 1)
        bounds = np.linspace(min(z_array), max(z_array), max_intervals)
        return bounds



def verifyInternetConn():
    try:
        response = urllib2.urlopen('http://maps.google.com/maps', timeout=3)
        return True
    except urllib2.URLError as err:
        pass
    return False


def fire_event(target_id, event_type):
    wx.PostEvent(target_id, BymurUpdateEvent(event_type,1))

def points_to_latlon(points, utm_zone_number=33,
                     utm_zone_letter='T', decimals=5):
    res = []
    for p in points:
        lat,lon = utm.to_latlon(float(p['easting']),
                                float(p['northing']),
                                utm_zone_number,
                                utm_zone_letter)
        res.append({'latitude': round(lat, decimals),
                    'longitude':round(lon, decimals)})
    return res

def points_to_utm(points, decimals=5):
    res = []
    for p in points:
        easting, northing, zone_number, zone_letter = \
            utm.from_latlon(p['latitude'],
                            p['longitude'])
        res.append({'easting': round(easting, decimals),
                    'northing':round(northing, decimals),
                    'zone_number': zone_number,
                    'zone_letter': zone_letter})
    return res

def get_gridpoints_from_file(filepath, utm_coords=True, utm_zone_number=33,
                             utm_zone_letter='T', decimals=5):
        gridfile = open(filepath, 'r')
        points = []
        if utm_coords:
            for line in gridfile:
                line_arr = line.strip().split()
                lat, lon = utm.to_latlon(float(line_arr[0]),
                                         float(line_arr[1]),
                                         utm_zone_number,
                                         utm_zone_letter)
                points.append({'latitude': round(lat, decimals) ,
                               'longitude':round(lon, decimals)
                })
            return points
        else:
            return False

def showMessage(**kwargs):
        debug = kwargs.pop('debug', False)
        style = kwargs.pop('style', 0)
        kind = kwargs.pop('kind', '')
        style |= wx.CENTRE | wx.STAY_ON_TOP
        if ( kind == 'BYMUR_ERROR'):
            style |= wx.ICON_ERROR | wx.OK
        elif (kind == 'BYMUR_CONFIRM'):
            style |= wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION
            print style
        else:
            style |= wx.ICON_INFORMATION | wx.OK
            print style

        if debug:
            exc_type, exc_obj, tb = sys.exc_info()
            f = tb.tb_frame
            lineno = tb.tb_lineno
            filename = os.path.split(f.f_code.co_filename)[1]
            linecache.checkcache(filename)
            line = linecache.getline(filename, lineno, f.f_globals)
            message = 'Exception in %s\nLine %s : "%s")\n%s' % \
                    ( filename, str(lineno),
                      str(line.strip()), str(exc_obj))
        else:
            message=kwargs.pop('message', '')

        msgDialog = wx.MessageDialog( parent = kwargs.pop('parent'),
                                      message = message,
                                      caption=kwargs.pop('caption', ''),
                                      style=style)
        answer = msgDialog.ShowModal()
        return (answer == wx.ID_OK) or (answer == wx.ID_YES)

