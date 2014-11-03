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
import numpy as np


wxBYMUR_UPDATE_CURVE = wx.NewEventType()
wxBYMUR_UPDATE_MAP = wx.NewEventType()
wxBYMUR_UPDATE_DIALOG = wx.NewEventType()
wxBYMUR_UPDATE_CTRLS = wx.NewEventType()
wxBYMUR_UPDATE_ALL = wx.NewEventType()
wxBYMUR_UPDATE_POINT = wx.NewEventType()
wxBYMUR_THREAD_CLOSED = wx.NewEventType()
wxBYMUR_DB_CONNECTED = wx.NewEventType()
wxBYMUR_DB_CLOSED = wx.NewEventType()
BYMUR_UPDATE_CURVE = wx.PyEventBinder(wxBYMUR_UPDATE_CURVE)
BYMUR_UPDATE_MAP = wx.PyEventBinder(wxBYMUR_UPDATE_MAP)
BYMUR_UPDATE_DIALOG = wx.PyEventBinder(wxBYMUR_UPDATE_DIALOG)
BYMUR_UPDATE_CTRLS = wx.PyEventBinder(wxBYMUR_UPDATE_CTRLS)
BYMUR_UPDATE_ALL = wx.PyEventBinder(wxBYMUR_UPDATE_ALL)
BYMUR_UPDATE_POINT = wx.PyEventBinder(wxBYMUR_UPDATE_POINT)
BYMUR_THREAD_CLOSED = wx.PyEventBinder(wxBYMUR_THREAD_CLOSED)
BYMUR_DB_CONNECTED = wx.PyEventBinder(wxBYMUR_DB_CONNECTED)
BYMUR_DB_CLOSED = wx.PyEventBinder(wxBYMUR_DB_CLOSED)


class BymurUpdateEvent(wx.PyCommandEvent):

    def __init__(self, eventType, id):
        self._callback_fun = None
        self._callback_args = None
        super(BymurUpdateEvent, self).__init__(eventType, id)

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
        # try:
        self._function(**self._function_args)
        evt_id = self._event.GetEventType()
        print evt_id
        if self._callback:
            self._callback()
        # except Exception as e:
        #     showMessage(parent=self._targetid,
        #                 message="Error in backgroud thread\n "+str(e),
        #                 kind="BYMUR_ERROR",
        #                 caption="Error")
        # finally:
        wx.PostEvent(self._targetid, self._event)


class HazardXMLModel(object):
    _basedir = os.path.dirname(__file__)
    _schemafile = os.path.join(_basedir, 'schema/bymur_schema.xsd')

    def __init__(self, filename, phenomenon, xsd=_schemafile):
        self._xsd_file = xsd
        print "schema path %s" % self._xsd_file
        print "%s > itializing file: %s " % (self.__class__.__name__,
                                             filename)
        try:
            xml_schema = etree.XMLSchema(file = self._xsd_file)
            xmlparser = etree.XMLParser(schema=xml_schema)
            print "Loaded schema: %s " % self._xsd_file
        except Exception as e:
            print "%s is not a valid XSD file" % self._xsd_file
            raise Exception(str(e))

        # TODO: check why this test fail here and not in the validator
        # try:
        #     with open(filename, 'r') as f:
        #         etree.fromstring(f.read(), xmlparser)
        # except Exception as e:
        #     print "%s is not a valid XML file" % filename
        #     raise Exception(str(e))

        self._filename = filename
        self._volcano = ''
        self._model_name = ''
        self._iml_thresholds = []
        self._iml_imt = ''
        self._exp_time = ''
        self._statistic = ''
        self._percentile_value = '0'
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


    def parse(self, utm_zone_number=33, utm_zone_letter='T'):
        context = etree.iterparse(self._filename, events=("start", "end"))
        for event, element in context:
            if event == "start":
                if element.tag == 'hazardCurveField':
                    self._statistic = element.get('statistics')
                    if self.statistic == 'percentile':
                        self._percentile_value = element.get(
                            'percentileValue')
                    else:
                        self._percentile_value = '0'
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
                    self._exp_time = float(element.get('deltaT').strip('yr'))
                    element.clear()
                elif element.tag == 'IML':
                    self._iml_imt = element.get('IMT')
                    # print "imt: %s" % self._iml_imt
                    self._iml_thresholds = element.text.strip()
                    # print "iml_thresholds: %s" % self._iml_thresholds
                    element.clear()
                elif element.tag == 'HCNode':
                    point_pos = {}
                    gml_pos = element.find('.//gmlpos').text.split()
                    point_pos['northing'] = int(round(float(gml_pos[0])))
                    point_pos['easting']  = int(round(float(gml_pos[1])))
                    point_pos['zone_number'] = utm_zone_number
                    point_pos['zone_letter'] = utm_zone_letter
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
    def exp_time(self):
        return self._exp_time

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


def SpawnThread(target, event_type, function, function_args, callback=None,
                    wait_msg='Wait please...'):
        """
        """
        threadId = wx.NewId()
        target.wait(wait_msg=wait_msg)
        worker = BymurThread(target, event_type, function, function_args,
                             callback)
        worker.start()

def verifyInternetConn():
    try:
        response = urllib2.urlopen('http://maps.google.com/maps', timeout=3)
        return True
    except urllib2.URLError as err:
        pass
    return False

def get_gridpoints_from_file(filepath, utm_coords=True, utm_zone_number=33,
                             utm_zone_letter='T', decimals=5):
        gridfile = open(filepath, 'r')
        points = []
        if utm_coords:
            for line in gridfile:
                line_arr = line.strip().split()
                points.append({'easting': int(round(float(line_arr[0]))),
                               'northing':  int(round(float(line_arr[1]))),
                               'zone_number': utm_zone_number,
                               'zone_letter': utm_zone_letter}
                )
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

def nearest_point_index(x,y,x_points,y_points):
    distances = np.hypot(x-x_points,
                             y-y_points)

    indmin = distances.argmin()
    return indmin

def fire_event(target_id, event_type):
    wx.PostEvent(target_id, BymurUpdateEvent(event_type,1))
    return True

def find_xml_files(rootdir):
    files_array=[]
    for root, dirs, files in os.walk(rootdir):
        for file in files:
            if file.endswith(".xml"):
                 files_array.append(os.path.relpath(os.path.join(root,file),
                                                 rootdir))
    return files_array


