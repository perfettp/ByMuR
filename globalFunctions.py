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

def fire_event(target_id, event_type):
    wx.PostEvent(target_id, BymurUpdateEvent(event_type,1))


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




class HazardModel(object):

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


def verifyInternetConn():
    try:
        response = urllib2.urlopen('http://maps.google.com/maps', timeout=3)
        return True
    except urllib2.URLError as err:
        pass
    return False
