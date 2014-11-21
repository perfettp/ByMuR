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


_basedir = os.path.dirname(__file__)
_hazardschemafile = os.path.join(_basedir, 'schema/bymur_schema.xsd')

class InventoryClass(object):
    def __init__(self, type='', name='', label=''):
        self._name = name
        self._label = label
        self._type = type
        pass

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, data):
        self._name = data
        
    @property
    def label(self):
        return self._label
    @label.setter
    def label(self, data):
        self._label = data

    @property
    def type(self):
        return self._type
    @type.setter
    def type(self, data):
        self._type = data

class InventoryGeneralClass(InventoryClass):
    pass

class InventoryAgeClass(InventoryClass):
    pass

class InventoryHouseClass(InventoryClass):
    pass

class InventoryPhenClass(InventoryClass):
    def __init__(self, name='', phenomenon = None, **kwargs):
        self._phenomenon = phenomenon
        super(InventoryPhenClass, self).__init__(**kwargs)
        pass

    @property
    def phenomenon(self):
        return self._phenomenon
    @phenomenon.setter
    def phenomenon(self, data):
        self._phenomenon = data
    pass

class InventoryFragilityClass(InventoryPhenClass):
    pass

class InventoryCostClass(InventoryPhenClass):
    pass

class InventoryFragilityClass(InventoryPhenClass):
    pass


class InventoryAsset(object):
    def __init__(self):
        self._total = None
        self._type = None
        self._counts = dict()
        self._frag_class_prob = dict()
        self._cost_class_prob = dict()
        self._counts = dict()
        pass

    def dump(self):
        print "Total: %s" % self.total
        print "Type: %s" % self.type
        for k in self.counts.keys():
            print "Count[%s]: %s" %(k, self.counts[k])
        print "Fragility class Probability: %s " % self.frag_class_prob
        print "Cost class Probability: %s " % self.cost_class_prob

    @property
    def total(self):
        return self._total
    @total.setter
    def total(self, data):
        self._total = data

    @property
    def type(self):
        return self._type
    @type.setter
    def type(self, data):
        self._type = data

    @property
    def counts(self):
        return self._counts
    @counts.setter
    def counts(self, data):
        self._counts = data

    @property
    def frag_class_prob(self):
        return self._frag_class_prob
    @frag_class_prob.setter
    def frag_class_prob(self, data):
        self._frag_class_prob = data

    @property
    def cost_class_prob(self):
        return self._cost_class_prob
    @cost_class_prob.setter
    def cost_class_prob(self, data):
        self._cost_class_prob = data

class InventorySection(object):
    def __init__(self):
        self._geometry = None
        self._centroid = None
        self._areaID = None
        self._sectionID = None
        self._asset = None
        pass

    def dump(self):
        print "AreaID: %s" % self.areaID
        print "SectionID: %s" % self.sectionID
        print "Centroid: %s" % self.centroid
        print "Geometry: %s" % self.geometry
        if self.asset is not None:
            self.asset.dump()

    @property
    def geometry(self):
        return self._geometry

    @geometry.setter
    def geometry(self, data):
        self._geometry = data

    @property
    def centroid(self):
        return self._centroid

    @centroid.setter
    def centroid(self, data):
        self._centroid = data

    @property
    def areaID(self):
        return self._areaID

    @areaID.setter
    def areaID(self, data):
        self._areaID = data

    @property
    def sectionID(self):
        return self._sectionID

    @sectionID.setter
    def sectionID(self, data):
        self._sectionID = data

    @property
    def asset(self):
        return self._asset

    @asset.setter
    def asset(self, data):
        self._asset = data


class  InventoryXML(object):
    def __init__(self):
        self._sections = []
        self._classes = dict()
        pass

    def dump(self):
        for sec in self.sections:
            sec.dump()

    @property
    def sections(self):
        return self._sections

    @sections.setter
    def sections(self, data):
        self._sections = data

    @property
    def classes(self):
        return self._classes

    @classes.setter
    def classes(self, data):
        self._classes = data

class HazardModelXML(object):
    def __init__(self, phenomenon):
        self._volcano = ''
        self._filename = ''
        self._model_name = ''
        self._hazard_model_name = ''
        self._iml_thresholds = []
        self._iml_imt = ''
        self._exp_time = ''
        self._statistic = ''
        self._percentile_value = '0'
        self._points_values= []
        self._points_coords = []
        self._phenomenon = phenomenon.upper()

    def tostring(self):
        xml_root = etree.Element("hazardResult")
        if self.phenomenon == "VULCANIC":
            tmp_child = etree.Element("volcano")
            tmp_child.text = "VULCANO"
            xml_root.append(tmp_child)
        elif self.phenomenon == "SEISMIC":
            pass
        elif self.phenomenon == "TSUNAMIC":
            pass

        if self.model_name != '':
            tmp_child = etree.Element("hazardModel", Model = self.model_name)
        else:
            tmp_child = etree.Element("hazardModel")
        tmp_child.text = self.hazard_model_name
        xml_root.append(tmp_child)
        tmp_child = etree.Element("timeterm",
                                  deltaT = str(int(self.exp_time)) + "yr")
        xml_root.append(tmp_child)
        if self.statistic == "mean":
            haz_curve_tmp = etree.Element("hazardCurveField",
                                        statistics = "mean")
        else:
            haz_curve_tmp = etree.Element("hazardCurveField",
                                        statistics = "percentile",
                                        percentileValue = self.percentile_value)
        tmp_child = etree.Element("IML",  IMT = self.iml_imt)
        tmp_child.text = " ".join([str(thresh) for thresh in
                                   self.iml_thresholds])
        haz_curve_tmp.append(tmp_child)

        for p_index in range(len(self.points_coords)):
            tmp_hcnode = etree.Element("HCNode")
            tmp_site = etree.Element("site")
            tmp_point = etree.Element("gmlPoint")
            tmp_pos = etree.Element("gmlpos")
            tmp_pos.text = str(self.points_coords[p_index]['northing']) + " " +\
                           str(self.points_coords[p_index]['easting'])
            tmp_point.append(tmp_pos)
            tmp_site.append(tmp_point)
            tmp_hcnode.append(tmp_site)

            tmp_hc = etree.Element("hazardCurve")
            tmp_poe = etree.Element("poE")
            tmp_poe.text = self.points_values[p_index]
            tmp_hc.append(tmp_poe)

            tmp_hcnode.append(tmp_hc)

            haz_curve_tmp.append(tmp_hcnode)

        xml_root.append(haz_curve_tmp)

        return etree.tostring(xml_root, pretty_print=True,
                              xml_declaration=True, encoding='UTF-8')

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, data):
        self._filename = data

    @property
    def volcano(self):
        return self._volcano
    @volcano.setter
    def volcano(self, data):
        self._volcano = data

    @property
    def model_name(self):
        return self._model_name
    @model_name.setter
    def model_name(self, data):
        self._model_name = data

    @property
    def hazard_model_name(self):
        return self._hazard_model_name
    @hazard_model_name.setter
    def hazard_model_name(self, data):
        self._hazard_model_name = data

    @property
    def iml_thresholds(self):
        return self._iml_thresholds
    @iml_thresholds.setter
    def iml_thresholds(self, data):
        self._iml_thresholds = data

    @property
    def iml_imt(self):
        return self._iml_imt
    @iml_imt.setter
    def iml_imt(self, data):
        self._iml_imt = data

    @property
    def exp_time(self):
        return self._exp_time
    @exp_time.setter
    def exp_time(self, data):
        self._exp_time = data

    @property
    def statistic(self):
        return self._statistic
    @statistic.setter
    def statistic(self, data):
        self._statistic = data

    @property
    def percentile_value(self):
        return self._percentile_value
    @percentile_value.setter
    def percentile_value(self, data):
        self._percentile_value = data

    @property
    def points_values(self):
        return self._points_values
    @points_values.setter
    def points_values(self, data):
        self._points_values = data

    @property
    def points_coords(self):
        return self._points_coords
    @points_coords.setter
    def points_coords(self, data):
        self._points_coords = data

    @property
    def phenomenon(self):
        return self._phenomenon
    @phenomenon.setter
    def phenomenon(self, data):
        self._phenomenon = data

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


def read_db_hazard(filename, phenomenon, xsd_file=_hazardschemafile,
          utm_zone_number=33, utm_zone_letter='T'):
    pass

def parse_xml_inventory(filename):
    print "Parsing Inventory: %s" % (filename)
    inventory_xml = InventoryXML()
    try:
        context = etree.iterparse(filename, events=("start", "end"))
        for event, element in context:
            if event == "start":
                if element.tag == 'sezione':
                    section_model = InventorySection()
                    section_model.areaID = element.get('areaID')
                    section_model.sectionID = element.get('sezioneID')
                elif element.tag == 'classes':
                    classes = dict()
                    class_list = []
                    class_type = element.get('type')
                elif element.tag == 'generalClasses':
                    class_obj_type = 'InventoryGeneralClass'
                elif element.tag == 'ageClasses':
                    class_obj_type = 'InventoryAgeClass'
                elif element.tag == 'houseClasses':
                    class_obj_type = 'InventoryHouseClass'
                elif element.tag == 'fragilityClasses':
                    class_obj_type = 'InventoryFragilityClass'
                    class_obj_phen = element.get('phenomenon')
                elif element.tag == 'costClasses':
                    class_obj_type = 'InventoryCostClass'
                    class_obj_phen = element.get('phenomenon')
                elif element.tag == 'class':
                    new_class = eval(class_obj_type)(name = element.get('name'),
                                                label = element.get('label'))
                    if issubclass(eval(class_obj_type), InventoryPhenClass):
                        new_class.phenomenon = class_obj_phen
                    class_list.append(new_class)
                elif element.tag == 'asset':
                    asset_model = InventoryAsset()
                    asset_model.total = element.get('total')
                    asset_model.type = element.get('type')
                elif element.tag == 'fragClassProb':
                    class_prob_dict = dict()
                    class_prob_phen = element.get('phenomenon')
                elif element.tag == 'costClassProb':
                    class_prob_dict = dict()
                    class_prob_phen = element.get('phenomenon')
            else:
                if element.tag == 'geometry':
                    section_model.geometry = element.text.strip().split(",")
                    element.clear()
                elif element.tag == 'centroid':
                    section_model.centroid = element.text.strip().split(" ")
                    element.clear()
                elif element.tag == 'asset':
                    section_model.asset = asset_model
                    asset_model = None
                    element.clear()
                elif element.tag == 'genClassCount':
                    asset_model.counts['genClassCount'] =\
                        element.text.strip().split(" ")
                elif element.tag == 'ageClassCount':
                    asset_model.counts['ageClassCount'] =\
                        element.text.strip().split(" ")
                elif element.tag == 'houseClassCount':
                    asset_model.counts['houseClassCount'] =\
                        element.text.strip().split(" ")
                elif element.tag == 'fragClassProb':
                    asset_model.frag_class_prob.update(
                        {class_prob_phen: class_prob_dict})
                    class_prob_phen = ''
                    class_prob_dict = dict()
                    element.clear()
                elif element.tag == 'costClassProb':
                    asset_model.cost_class_prob.update(
                        {class_prob_phen: class_prob_dict})
                    class_prob_phen = ''
                    class_prob_dict = dict()
                    element.clear()
                elif element.tag == 'fnt':
                    class_prob_dict['fnt'] = element.text.strip().split(" ")
                    element.clear()
                elif element.tag == 'fntGivenGeneralClass':
                    class_prob_dict['fntGivenGeneralClass'] = \
                        [[e for e in cs.strip().split(" ") if e is not '']
                         for cs in element.text.strip().split(",")]
                    element.clear()
                elif element.tag == 'fnc':
                    class_prob_dict['fnc'] = element.text.strip().split(" ")
                    element.clear()
                elif element.tag == 'generalClasses':
                    classes['generalClasses'] = class_list
                    class_list = []
                    element.clear()
                elif element.tag == 'ageClasses':
                    classes['ageClasses'] = class_list
                    class_list = []
                    element.clear()
                elif element.tag == 'houseClasses':
                    classes['houseClasses'] = class_list
                    class_list = []
                    element.clear()
                elif element.tag == 'fragilityClasses':
                    if 'fragilityClasses' not in classes.keys():
                            classes['fragilityClasses'] = dict()
                    classes['fragilityClasses'][class_obj_phen] = class_list
                    class_list = []
                    element.clear()
                elif element.tag == 'costClasses':
                    if 'costClasses' not in classes.keys():
                            classes['costClasses'] = dict()
                    classes['costClasses'][class_obj_phen] = class_list
                    class_list = []
                    element.clear()
                elif element.tag == 'classes':
                    inventory_xml.classes.update(classes)
                    class_list = None
                    element.clear()
                elif element.tag == 'sezione':
                    inventory_xml.sections.append(section_model)
                    section_model = None
                    element.clear()

    except Exception as e:
        print "Error parsing file " + \
              filename +  " : " + str(e)
        raise Exception(str(e))
    return inventory_xml


def parse_xml_hazard(filename, phenomenon, xsd_file=_hazardschemafile,
                     utm_zone_number=33, utm_zone_letter='T'):
    hazard_xml_model = HazardModelXML(phenomenon)
    print "Parsing file to Hazard XML: %s" % (filename)
    print "Schema path %s" % xsd_file
    try:
        xml_schema = etree.XMLSchema(file = xsd_file)
        xmlparser = etree.XMLParser(schema=xml_schema)
        print "Loaded schema: %s " % xsd_file
    except Exception as e:
        print "%s is not a valid XSD file" % xsd_file
        raise Exception(str(e))

    # TODO: check why this test fail here and not in the validator
    # try:
    #     with open(filename, 'r') as f:
    #         etree.fromstring(f.read(), xmlparser)
    # except Exception as e:
    #     print "%s is not a valid XML file" % filename
    #     raise Exception(str(e))
    try:
        context = etree.iterparse(filename, events=("start", "end"))
        for event, element in context:
            if event == "start":
                if element.tag == 'hazardCurveField':
                    hazard_xml_model.statistic = element.get('statistics')
                    if hazard_xml_model.statistic == 'percentile':
                        hazard_xml_model.percentile_value = element.get(
                            'percentileValue')
                    else:
                        hazard_xml_model.percentile_value = '0'
                    # print "statistic: %s" % hazard_xml_model.statistic
                    # print "percentile: %s" % hazard_xml_model.percentile_value

            else:
                if element.tag == 'volcano':
                    hazard_xml_model.volcano = element.get('volcanoName')
                    element.clear()
                    # print "volcano: %s" % hazard_xml_model.volcano
                elif element.tag == 'hazardModel':
                    hazard_xml_model.model_name = element.get('Model')
                    hazard_xml_model.hazard_model_name = element.text.strip()
                    element.clear()
                elif element.tag == 'timeterm':
                    hazard_xml_model.exp_time = float(element.get('deltaT').strip('yr'))
                    element.clear()
                elif element.tag == 'IML':
                    hazard_xml_model.iml_imt = element.get('IMT')
                    # print "imt: %s" % hazard_xml_model.iml_imt
                    hazard_xml_model.iml_thresholds = element.text.strip()
                    # print "iml_thresholds: %s" % hazard_xml_model.iml_thresholds
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
                    hazard_xml_model.points_coords.append(point_pos)
                    hazard_xml_model.points_values.append(point_val)
                    element.clear()
                elif element.tag == 'hazardCurveField':
                    element.clear()
    except Exception as e:
        print "Error parsing file " + \
              filename +  " : " + str(e)
        raise Exception(str(e))
    return hazard_xml_model

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


