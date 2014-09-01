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

import math
import os
import urllib2
import xml.etree.ElementTree as xml
import wx


def show_message(self, *kargs):
    """
    It opens a pop-up dialog showing a text message.
    """

    dlg = wx.MessageDialog(
        self,
        kargs[0],
        kargs[1],
        wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()


def showWarningMessage(self, *kargs):
    """
    It opens a pop-up dialog showing a warning message.
    """

    dlg = wx.MessageDialog(self, kargs[0], kargs[1], wx.OK | wx.ICON_WARNING)
    dlg.ShowModal()
    dlg.Destroy()


def showErrorMessage(self, *kargs):
    """
    It opens a pop-up dialog showing an error message.
    """

    dlg = wx.MessageDialog(self, kargs[0], kargs[1], wx.OK | wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()


def showYesnoDialog(self, *kargs):
    """
    It opens a pop-up dialog showing a Yes/No message.
    """

    dlg = wx.MessageDialog(self, kargs[0], kargs[1],
                           wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
    answer = dlg.ShowModal()
    dlg.Destroy()
    return answer


def xmlParsing(*kargs):
    """
    Reading of hazard curves.
    It opens and reads xml files formatted on the basis of the standard
    semantic proposed by the OpenQuake/GEM projects.

    """

    path = kargs[0]

    if os.path.isfile(path):

        tree = xml.parse(path)
        root = tree.getroot()

        pos = []
        poe = []

        for node in tree.iter():
            if ("model" in node.tag):
                mod = node.attrib.get("Model")
            if ("timeterm" in node.tag):
                dtime = node.attrib.get("deltaT")
            if ("IML" in node.tag):
                iml = [float(x) for x in node.text.split()]
                imt = node.attrib.get("IMT")
            if ("gmlpos" in node.tag):
                pos.append([float(x) for x in node.text.split()])
            if ("poE" in node.tag):
                poe.append([float(x) for x in node.text.split()])

        np = len(pos)
        lat = [pos[i][0] for i in range(np)]
        lon = [pos[i][1] for i in range(np)]

        return mod, dtime, imt, iml, lat, lon, poe

    else:
        msg = ("ERROR:\nUploaded file path is wrong")
        showErrorMessage(None, msg, "ERROR")
        return


def selDir(self, event):
    """
    Open a dialog to select a directory path
    """
    dfl_dir = os.path.expanduser("~")
    dlg = wx.DirDialog(self, "Select a directory:", defaultPath=dfl_dir,
                       style=wx.DD_DEFAULT_STYLE
                       # | wx.DD_DIR_MUST_EXIST
                       # | wx.DD_CHANGE_DIR
                       )
    if dlg.ShowModal() == wx.ID_OK:
        path = dlg.GetPath()
    else:
        msg = "WARNING\nYou have NOT selected any directory"
        showWarningMessage(self, msg, "WARNING")
        path = ""

    dlg.Destroy()
    return path


def selFile(self, event, *kargs):
    """
    upload_file
    It opens a file dialog, it opens the selected file and
    it returns the corresponding path
    """

    dfl_dir = os.path.expanduser("~")
    dlg = wx.FileDialog(self, message="Upload File", defaultDir=dfl_dir,
                        defaultFile="", wildcard="*.*",
                        style=wx.FD_OPEN | wx.FD_CHANGE_DIR)

    if (dlg.ShowModal() == wx.ID_OK):
        path = dlg.GetPath()
    else:
        msg = "WARNING\nYou have NOT selected any file"
        showWarningMessage(self, msg, "WARNING")
        path = ""

    dlg.Destroy()
    return path


def verifyInternetConn():
    try:
        response = urllib2.urlopen('http://maps.google.com/maps', timeout=3)
        return True
    except urllib2.URLError as err:
        pass
    return False


def floatCeil(*kargs):

    x = kargs[0]
    if (x < 1):
        y = math.ceil(x * 10.) / 10.
    elif (x < 0.1):
        y = math.ceil(x * 100.) / 100.
    elif (x < 0.01):
        y = math.ceil(x * 1000.) / 1000.
    else:
        y = math.ceil(x)

    return y


def floatFloor(*kargs):

    x = kargs[0]
    if (x < 1):
        y = math.floor(x * 10.) / 10.
    elif (x < 0.1):
        y = math.floor(x * 100.) / 100.
    elif (x < 0.01):
        y = math.floor(x * 1000.) / 1000.
    else:
        y = math.floor(x)

    return y
