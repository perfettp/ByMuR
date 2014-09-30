import wx
import plotLibs
import os
import bymurcore
import bymurcontroller
import globalFunctions as gf
import time

class BymurBusyDlg(wx.BusyInfo):
    """
    """

    def __init__(self, *args, **kwargs):
        super(BymurBusyDlg, self).__init__(*args, **kwargs)


class BymurStaticBoxSizer(wx.StaticBoxSizer):
    def __init__(self, *args, **kwargs):
        self._parent = kwargs.pop('parent', None)
        self._label = kwargs.pop('label', "")
        self._box = wx.StaticBox(self._parent, label=self._label)
        super(BymurStaticBoxSizer, self).__init__(self._box,
                                                  *args,
                                                  **kwargs)


class BymurDBBoxSizer(BymurStaticBoxSizer):
    _textSize = (300, -1)

    def __init__(self, *args, **kwargs):
        self._dbDetails = {'db_host': kwargs.pop('db_host', ''),
                           'db_port': kwargs.pop('db_port', ''),
                           'db_user': kwargs.pop('db_user', ''),
                           'db_password': kwargs.pop('db_password', ''),
                           'db_name': kwargs.pop('db_name', '')
        }
        super(BymurDBBoxSizer, self).__init__(*args, **kwargs)

        self._dbSizer = wx.GridBagSizer(hgap=5, vgap=5)
        self.Add(self._dbSizer)

        row = 0
        self._dbHost = wx.StaticText(self._parent, wx.ID_ANY,
                                     'Server hostname: ')
        self._dbSizer.Add(self._dbHost, pos=(row, 0))
        self._dbHostText = wx.TextCtrl(self._parent, wx.ID_ANY,
                                       size=self._textSize)
        self._dbHostText.SetValue(self._dbDetails['db_host'])
        self._dbSizer.Add(self._dbHostText, pos=(row, 1))
        row += 1
        self._dbPort = wx.StaticText(self._parent, wx.ID_ANY, 'Server Port: ')
        self._dbSizer.Add(self._dbPort, pos=(row, 0))
        self._dbPortText = wx.TextCtrl(self._parent, wx.ID_ANY,
                                       size=self._textSize)
        self._dbPortText.SetValue(self._dbDetails['db_port'])
        self._dbSizer.Add(self._dbPortText, pos=(row, 1))
        row += 1
        self._dbUser = wx.StaticText(self._parent, wx.ID_ANY, 'User: ')
        self._dbSizer.Add(self._dbUser, pos=(row, 0))
        self._dbUserText = wx.TextCtrl(self._parent, wx.ID_ANY,
                                       size=self._textSize)
        self._dbUserText.SetValue(self._dbDetails['db_user'])
        self._dbSizer.Add(self._dbUserText, pos=(row, 1))
        row += 1
        self._dbPassword = wx.StaticText(self._parent, wx.ID_ANY, 'Password: ')
        self._dbSizer.Add(self._dbPassword, pos=(row, 0))
        self._dbPasswordText = wx.TextCtrl(self._parent, wx.ID_ANY,
                                           size=self._textSize,
                                           style=wx.TE_PASSWORD)
        self._dbPasswordText.SetValue(self._dbDetails['db_password'])
        self._dbSizer.Add(self._dbPasswordText, pos=(row, 1))
        row += 1
        self._dbName = wx.StaticText(self._parent, wx.ID_ANY, 'Database name: ')
        self._dbSizer.Add(self._dbName, pos=(row, 0))
        self._dbNameText = wx.TextCtrl(self._parent, wx.ID_ANY,
                                       size=self._textSize)
        self._dbNameText.SetValue(self._dbDetails['db_name'])
        self._dbSizer.Add(self._dbNameText, pos=(row, 1))

    @property
    def dbHost(self):
        return self._dbHostText.GetValue()

    @property
    def dbPort(self):
        return self._dbPortText.GetValue()

    @property
    def dbUser(self):
        return self._dbUserText.GetValue()

    @property
    def dbPassword(self):
        return self._dbPasswordText.GetValue()

    @property
    def dbName(self):
        return self._dbNameText.GetValue()


class BymurGeoBoxSizer(BymurStaticBoxSizer):
    _geoText = "Load a 3-column ascii file having latitude\n" \
               "(1st col) and longitude (2nd col) of each spatial\n" \
               "point and the corresponding ID area (3rd col)."

    def __init__(self, *args, **kwargs):
        self._gridPath = kwargs.pop('grid_path', '')

        super(BymurGeoBoxSizer, self).__init__(*args, **kwargs)

        self._geoBoxGrid = wx.GridBagSizer(hgap=5, vgap=5)
        self.Add(self._geoBoxGrid)
        self._geoBoxGrid.Add(wx.StaticText(self._parent, id=wx.ID_ANY,
                                           style=wx.EXPAND,
                                           label=self._geoText),
                             flag=wx.EXPAND, pos=(0, 0), span=(1, 6))
        self._geoFileText = wx.TextCtrl(self._parent, wx.ID_ANY)
        self._geoBoxGrid.Add(self._geoFileText, flag=wx.EXPAND,
                             pos=(1, 0), span=(1, 5))
        self._geoFileText.SetValue(self._gridPath)
        self._geoFileButton = wx.Button(self._parent, id=wx.ID_ANY,
                                        label="Select File")
        self._geoFileButton.Bind(event=wx.EVT_BUTTON, handler=self.selGridFile)
        self._geoBoxGrid.Add(self._geoFileButton, flag=wx.EXPAND,
                             pos=(1, 5), span=(1, 1))

    def selGridFile(self, event):
        dir = os.path.dirname(self._geoFileText.GetValue())
        if (not os.path.isdir(dir)):
            dir = os.path.expanduser("~")
        dlg = wx.FileDialog(self._parent, message="Upload File", defaultDir=dir,
                            defaultFile="", wildcard="*.*",
                            style=wx.FD_OPEN | wx.FD_CHANGE_DIR)

        if (dlg.ShowModal() == wx.ID_OK):
            self._geoFileText.SetValue(dlg.GetPath())
        dlg.Destroy()

    @property
    def gridPath(self):
        return self._geoFileText.GetValue()


class BymurEnsBoxSizer(BymurStaticBoxSizer):
    _hazText = "Chose among the list of possible hazard models \n" \
               "here below the ones you would like to use to \n" \
               "calculate the ensable hazard."

    _intText = "Choose time interval"

    _haz_array = []
    _haz_dict = {}

    def __init__(self, *args, **kwargs):
        data = kwargs.pop('data', {})
        super(BymurEnsBoxSizer, self).__init__(*args, **kwargs)
        self._ensBoxGrid = wx.GridBagSizer(hgap=5, vgap=5)
        self.Add(self._ensBoxGrid)
        self._hazLabel = wx.StaticText(self._parent, id=wx.ID_ANY,
                                       style=wx.EXPAND,
                                       label=self._hazText)
        self._ensBoxGrid.Add(self._hazLabel, flag=wx.EXPAND, pos=(0, 0),
                             span=(2, 4))
        grid_row = 2
        for i in range(len(data['model'])):
            haz_item = {'name': data['model'][i],
                        'checkbox': wx.CheckBox(self._parent,
                                                wx.ID_ANY,
                                                label=data['model'][i]),
                        'text': wx.TextCtrl(self._parent, wx.ID_ANY),
                        'dtime': data['dtime'][i],
            }
            print data['dtime'][i]
            haz_item['text'].SetValue("1")
            haz_item['text'].Enable(False)
            haz_item['checkbox'].Bind(wx.EVT_CHECKBOX, self.checkItem)

            self._ensBoxGrid.Add(haz_item['checkbox'],
                                 flag=wx.EXPAND,
                                 pos=(grid_row, 0), span=(1, 3))
            self._ensBoxGrid.Add(haz_item['text'],
                                 flag=wx.EXPAND,
                                 pos=(grid_row, 3), span=(1, 1))

            self._haz_array.append(haz_item)
            self._haz_dict[data['model'][i]] = haz_item
            grid_row += 1

        self._ensBoxGrid.Add(wx.StaticText(self._parent, id=wx.ID_ANY,
                                           style=wx.EXPAND,
                                           label=self._intText),
                             flag=wx.EXPAND, pos=(grid_row, 0), span=(1, 3))
        self._intCB = wx.ComboBox(self._parent, wx.ID_ANY, choices=[],
                                  style=wx.CB_READONLY)
        self._intCB.Enable(False)
        self._ensBoxGrid.Add(self._intCB, flag=wx.EXPAND,
                             pos=(grid_row, 3), span=(1, 1))

    def checkItem(self, event):
        self._haz_dict[event.GetEventObject().GetLabelText()]['text']. \
            Enable(event.IsChecked())
        dtshared = []
        for k in self._haz_dict:
            if self._haz_dict[k]['checkbox'].IsChecked():
                dtshared.append(self._haz_dict[k]['dtime'])
        if len(dtshared) > 1:
            dtime_shared = list(set(dtshared[0]) & set(dtshared[1]))
            for j in range(2, len(dtshared)):
                dtime_shared = list(set(dtime_shared) & set(dtshared[j]))
            self._intCB.SetItems(dtime_shared)
            self._intCB.Enable(True)
        else:
            self._intCB.Enable(False)

    @property
    def hazArray(self):
        return self._haz_array

    @property
    def dtimeShared(self):
        if self._intCB.GetSelection() == wx.NOT_FOUND:
            raise Exception("Time interval is not selected!")
        return self._intCB.GetString(self._intCB.GetSelection())


class BymurMapBoxSizer(BymurStaticBoxSizer):
    def __init__(self, *args, **kwargs):
        self._latMin = kwargs.pop('lat_min', '')
        self._latMax = kwargs.pop('lat_max', '')
        self._lonMin = kwargs.pop('lon_min', '')
        self._lonMax = kwargs.pop('lon_max', '')
        self._mapPath = kwargs.pop('map_path', '')
        super(BymurMapBoxSizer, self).__init__(*args, **kwargs)

        self._mapBoxGrid = wx.GridBagSizer(hgap=5, vgap=5)
        self.Add(self._mapBoxGrid)

        self._mapLatMinLabel = wx.StaticText(self._parent, id=wx.ID_ANY,
                                             style=wx.EXPAND,
                                             label="Latitude Min (m)")
        self._mapLatMinText = wx.TextCtrl(self._parent, wx.ID_ANY)
        self._mapLatMinText.SetValue(str(self._latMin))
        self._mapBoxGrid.Add(self._mapLatMinLabel, flag=wx.EXPAND,
                             pos=(0, 0), span=(1, 4))
        self._mapBoxGrid.Add(self._mapLatMinText, flag=wx.EXPAND,
                             pos=(0, 4), span=(1, 1))

        self._mapLatMaxLabel = wx.StaticText(self._parent, id=wx.ID_ANY,
                                             style=wx.EXPAND,
                                             label="Latitude Max (m)")
        self._mapLatMaxText = wx.TextCtrl(self._parent, wx.ID_ANY)
        self._mapLatMaxText.SetValue(str(self._latMax))
        self._mapBoxGrid.Add(self._mapLatMaxLabel, flag=wx.EXPAND,
                             pos=(1, 0), span=(1, 4))
        self._mapBoxGrid.Add(self._mapLatMaxText, flag=wx.EXPAND,
                             pos=(1, 4), span=(1, 1))

        self._mapLonMinLabel = wx.StaticText(self._parent, id=wx.ID_ANY,
                                             style=wx.EXPAND,
                                             label="Longitude Min (m)")
        self._mapLonMinText = wx.TextCtrl(self._parent, wx.ID_ANY)
        self._mapLonMinText.SetValue(str(self._lonMin))
        self._mapBoxGrid.Add(self._mapLonMinLabel, flag=wx.EXPAND,
                             pos=(2, 0), span=(1, 4))
        self._mapBoxGrid.Add(self._mapLonMinText, flag=wx.EXPAND,
                             pos=(2, 4), span=(1, 1))

        self._mapLonMaxLabel = wx.StaticText(self._parent, id=wx.ID_ANY,
                                             style=wx.EXPAND,
                                             label="Longitude Max (m)")
        self._mapLonMaxText = wx.TextCtrl(self._parent, wx.ID_ANY)
        self._mapLonMaxText.SetValue(str(self._lonMax))
        self._mapBoxGrid.Add(self._mapLonMaxLabel, flag=wx.EXPAND,
                             pos=(3, 0), span=(1, 4))
        self._mapBoxGrid.Add(self._mapLonMaxText, flag=wx.EXPAND,
                             pos=(3, 4), span=(1, 1))

        self._mapButton = wx.Button(self._parent, id=wx.ID_ANY,
                                    label="Upload map")
        self._mapButton.Bind(event=wx.EVT_BUTTON, handler=self.selMap)
        self._mapBoxGrid.Add(self._mapButton, flag=wx.EXPAND,
                             pos=(0, 5), span=(4, 1))

    def selMap(self, event):
        dir = os.getcwd()
        if (not os.path.isdir(dir)):
            dir = os.path.expanduser("~")
        dlg = wx.FileDialog(self._parent, message="Upload Map", defaultDir=dir,
                            defaultFile="", wildcard="*.png", style=wx.OPEN)
        if (dlg.ShowModal() == wx.ID_OK):
            self._mapPath = str(dlg.GetPath())

            if (self._mapPath):
                ext = self._mapPath[-3:]

                if (ext != "png"):
                    msg = ("ERROR:\nYou can upload .png file "
                           "format only.")
                    gf.showMessage(parent=self._parent,
                                   kind="BYMUR_ERROR", caption="Error!",
                                   message="You can upload .png file format only")
                    dlg.Destroy()
                    return
                print "Map uploaded"
                # TODO: what should I do here?
                # self.confAct(self.conf_map)
                #self.Layout()
            else:
                gf.showMessage(parent=self._parent, kind="BYMUR_ERROR",
                               caption="Error!",
                               message="Image path is wrong.")
        dlg.Destroy()

    @property
    def latMin(self):
        return int(self._mapLatMinText.GetValue())

    @property
    def latMax(self):
        return int(self._mapLatMaxText.GetValue())

    @property
    def lonMin(self):
        return int(self._mapLonMinText.GetValue())

    @property
    def lonMax(self):
        return int(self._mapLonMaxText.GetValue())

    @property
    def mapPath(self):
        return self._mapPath


class BymurHazBoxSizer(BymurStaticBoxSizer):
    _hazPercLabel = "Insert percentile single values or ranges"
    _hazPercExample = "Ex: 10,50,90 for single values or 5:100:5\n" \
                      "for range from 5 to 100 with a step of 5"

    def __init__(self, *args, **kwargs):
        self._hazPath = kwargs.pop('haz_path', '')
        self._hazPerc = kwargs.pop('haz_perc', '')
        super(BymurHazBoxSizer, self).__init__(*args, **kwargs)

        self._hazBoxGrid = wx.GridBagSizer(hgap=5, vgap=5)
        self.Add(self._hazBoxGrid)
        self._hazBoxGrid.Add(wx.StaticText(self._parent, id=wx.ID_ANY,
                                           style=wx.EXPAND,
                                           label="Select hazard files "
                                                 "directory"),
                             flag=wx.EXPAND, pos=(0, 0), span=(1, 6))
        self._hazDirText = wx.TextCtrl(self._parent, wx.ID_ANY)
        self._hazDirText.SetValue(self._hazPath)
        self._hazBoxGrid.Add(self._hazDirText, flag=wx.EXPAND,
                             pos=(1, 0), span=(1, 5))
        self._hazDirButton = wx.Button(self._parent, id=wx.ID_ANY,
                                       label="Select path")
        self._hazDirButton.Bind(event=wx.EVT_BUTTON, handler=self.selHazPath)
        self._hazBoxGrid.Add(self._hazDirButton, flag=wx.EXPAND,
                             pos=(1, 5), span=(1, 1))

        self._hazBoxGrid.Add(wx.StaticText(self._parent, id=wx.ID_ANY,
                                           style=wx.EXPAND,
                                           label=self._hazPercLabel),
                             flag=wx.EXPAND, pos=(2, 0), span=(1, 6))

        self._hazPercText = wx.TextCtrl(self._parent, wx.ID_ANY)
        self._hazPercText.SetValue(self._hazPerc);
        self._hazBoxGrid.Add(self._hazPercText, flag=wx.EXPAND,
                             pos=(3, 0), span=(1, 6))

        self._hazBoxGrid.Add(wx.StaticText(self._parent, id=wx.ID_ANY,
                                           style=wx.EXPAND,
                                           label=self._hazPercExample),
                             flag=wx.EXPAND, pos=(4, 0), span=(2, 6))

    def selHazPath(self, event):
        print "selHazPath"
        dir = os.path.dirname(self._hazDirText.GetValue())
        if (not os.path.isdir(dir)):
            dir = os.path.expanduser("~")

        dlg = wx.DirDialog(self._parent, "Select a directory:", defaultPath=dir,
                           style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self._hazDirText.SetValue(dlg.GetPath())
        dlg.Destroy()

    @property
    def hazPath(self):
        return self._hazDirText.GetValue()

    @property
    def hazPerc(self):
        return self._hazPercText.GetValue()


class BymurDBCreateDlg(wx.Dialog):
    def __init__(self, *args, **kwargs):
        self._title = "Create ByMuR database"
        self._style = kwargs.pop('style', 0)
        self._style |= wx.OK | wx.CANCEL
        self._localData = {'db_host': kwargs.pop('db_host', ''),
                           'db_port': kwargs.pop('db_port', ''),
                           'db_user': kwargs.pop('db_user', ''),
                           'db_password': kwargs.pop('db_password', ''),
                           'db_name': kwargs.pop('db_name', '')}
        self._localGeoDefaults = {'grid_path': kwargs.pop('grid_path', '')}
        self._localMapDefaults = {'lat_min': kwargs.pop('lat_min', 0),
                                  'lat_max': kwargs.pop('lat_max', 0),
                                  'lon_min': kwargs.pop('lon_min', 0),
                                  'lon_max': kwargs.pop('lon_max', 0),
                                  'map_path': kwargs.pop('map_path', '')}
        self._localHazDefaults = {'haz_path': kwargs.pop('haz_path', ''),
                                  'haz_perc': kwargs.pop('haz_perc', '')}

        super(BymurDBCreateDlg, self).__init__(style=self._style, *args,
                                               **kwargs)
        self.SetTitle(self._title)
        self._sizer = wx.BoxSizer(orient=wx.VERTICAL)
        self._gridSizer = wx.GridBagSizer(hgap=10, vgap=10)
        self._sizer.Add(self._gridSizer)

        self._geoBoxSizer = BymurGeoBoxSizer(parent=self,
                                             label="Geographical grid "
                                                   "data",
                                             **self._localGeoDefaults)
        self._gridSizer.Add(self._geoBoxSizer, flag=wx.EXPAND,
                            pos=(0, 0), span=(1, 1))

        self._mapBoxSizer = BymurMapBoxSizer(parent=self,
                                             label="Backgroud image map and "
                                                   "limits (UTM",
                                             **self._localMapDefaults)
        self._gridSizer.Add(self._mapBoxSizer, flag=wx.EXPAND,
                            pos=(1, 0), span=(1, 1))

        self._hazBoxSizer = BymurHazBoxSizer(parent=self,
                                             label="Hazard",
                                             **self._localHazDefaults)
        self._gridSizer.Add(self._hazBoxSizer, flag=wx.EXPAND,
                            pos=(0, 1), span=(1, 1))

        self._dbBoxSizer = BymurDBBoxSizer(parent=self,
                                           label="Database details",
                                           **self._localData)
        self._gridSizer.Add(self._dbBoxSizer, flag=wx.EXPAND,
                            pos=(1, 1), span=(1, 1))

        self._sizer.Add(self.CreateButtonSizer(flags=wx.OK | wx.CANCEL),
                        flag=wx.ALL | wx.ALIGN_CENTER, border=10)
        self.SetSizerAndFit(self._sizer)

    def ShowModal(self, *args, **kwargs):
        result = super(BymurDBCreateDlg, self).ShowModal(*args, **kwargs)
        if (result == wx.ID_OK):
            result = 1
            self._localData['db_host'] = self._dbBoxSizer.dbHost
            self._localData['db_port'] = self._dbBoxSizer.dbPort
            self._localData['db_user'] = self._dbBoxSizer.dbUser
            self._localData['db_password'] = self._dbBoxSizer.dbPassword
            self._localData['db_name'] = self._dbBoxSizer.dbName
            self._localData['grid_path'] = self._geoBoxSizer.gridPath
            self._localData['lat_min'] = self._mapBoxSizer.latMin
            self._localData['lat_max'] = self._mapBoxSizer.latMax
            self._localData['lon_min'] = self._mapBoxSizer.lonMin
            self._localData['lon_max'] = self._mapBoxSizer.lonMax
            self._localData['map_path'] = self._mapBoxSizer.mapPath
            self._localData['haz_path'] = self._hazBoxSizer.hazPath
            self._localData['haz_perc'] = self._hazBoxSizer.hazPerc
        elif (result == wx.ID_CANCEL):
            result = 0
        else:
            result = -1
        return (result, self._localData)


class BymurDBLoadDlg(wx.Dialog):
    _textSize = (300, -1)

    def __init__(self, *args, **kwargs):
        self._title = 'Load ByMuR database'
        self._style = kwargs.pop('style', 0)
        self._style |= wx.OK | wx.CANCEL
        self._dbDetails = {'db_host': kwargs.pop('db_host', ''),
                           'db_port': kwargs.pop('db_port', ''),
                           'db_user': kwargs.pop('db_user', ''),
                           'db_password': kwargs.pop('db_password', ''),
                           'db_name': kwargs.pop('db_name', '')
        }
        super(BymurDBLoadDlg, self).__init__(style=self._style, *args, **kwargs)
        self.SetTitle(self._title)
        self._sizer = wx.BoxSizer(orient=wx.VERTICAL)

        self._dbBoxSizer = BymurDBBoxSizer(parent=self,
                                           label="Connection details",
                                           orient=wx.VERTICAL,
                                           **self._dbDetails)

        self._dbBoxSizer.Add(self.CreateButtonSizer(flags=wx.OK | wx.CANCEL))

        self._sizer.Add(self._dbBoxSizer)
        self.SetSizerAndFit(self._sizer)

    def ShowModal(self, *args, **kwargs):
        result = super(BymurDBLoadDlg, self).ShowModal(*args, **kwargs)
        if (result == wx.ID_OK):
            result = 1
            self._dbDetails['db_host'] = self._dbBoxSizer.dbHost
            self._dbDetails['db_port'] = self._dbBoxSizer.dbPort
            self._dbDetails['db_user'] = self._dbBoxSizer.dbUser
            self._dbDetails['db_password'] = self._dbBoxSizer.dbPassword
            self._dbDetails['db_name'] = self._dbBoxSizer.dbName

        elif (result == wx.ID_CANCEL):
            result = 0
        else:
            result = -1
        return (result, self._dbDetails)


class BymurEnsembleDlg(wx.Dialog):
    _ensembleDetails = {}
    _ensBoxSizer = None

    def __init__(self, *args, **kwargs):
        self._title = kwargs.pop('title', '')
        self._style = kwargs.pop('style', 0)
        self._style |= wx.OK | wx.CANCEL
        self._localData = kwargs.pop('data', {})
        super(BymurEnsembleDlg, self).__init__(style=self._style, *args,
                                               **kwargs)

        self._sizer = wx.BoxSizer(orient=wx.VERTICAL)

        self._ensBoxSizer = BymurEnsBoxSizer(parent=self,
                                             label="Ensemble hazard definition",
                                             orient=wx.VERTICAL,
                                             data=self._localData)

        self._ensBoxSizer.Add(self.CreateButtonSizer(flags=wx.OK | wx.CANCEL),
                              flag=wx.ALL | wx.ALIGN_CENTER, border=10)

        self._sizer.Add(self._ensBoxSizer)
        self.SetSizerAndFit(self._sizer)

        self.SetTitle(self._title)

    def ShowModal(self, *args, **kwargs):
        result = super(BymurEnsembleDlg, self).ShowModal(*args, **kwargs)
        if (result == wx.ID_OK):
            result = 1
            ensLocalDetails = {
                'dtime': 0,
                'components': []
            }
            for i in range(len(self._ensBoxSizer.hazArray)):
                if self._ensBoxSizer.hazArray[i]['checkbox'].IsChecked():
                    ens_item = {
                        'index': i,
                        'name': self._ensBoxSizer.hazArray[i]['name'],
                        'weight': float(
                            self._ensBoxSizer.hazArray[i]['text'].GetValue())
                    }
                    ensLocalDetails['components'].append(ens_item)
            if len(ensLocalDetails['components']) < 2:
                gf.showMessage(parent=self, kind="BYMUR_ERROR",
                               caption="Error defining ensemble hazard",
                               message="Attention: at least 2 hazard should be "
                                       "selected!")
                result = -1
            else:
                try:
                    ensLocalDetails['dtime'] = self._ensBoxSizer.dtimeShared
                    self._ensembleDetails = ensLocalDetails
                except Exception as e:
                    gf.showMessage(parent=self, kind="BYMUR_ERROR",
                                   caption="Error defining ensemble hazard",
                                   message=str(e))
                    result = -1
        elif (result == wx.ID_CANCEL):
            result = 0
        else:
            result = -1
        return (result, self._ensembleDetails)


class BymurWxPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        self._bymur_label = kwargs.pop('label', "")
        self._controller = kwargs.pop('controller', None)
        super(BymurWxPanel, self).__init__(*args, **kwargs)
        self.Enable(False)

    def updateView(self, **kwargs):
        self.Enable(False)
        for panel in self.GetChildren():
            if isinstance(panel, BymurWxPanel):
                panel.updateView(**kwargs)
        self.Enable(True)


class BymurWxCurvesPanel(BymurWxPanel):
    def __init__(self, *args, **kwargs):
        super(BymurWxCurvesPanel, self).__init__(*args, **kwargs)

        self._sizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.SetSizer(self._sizer)
        self._nb = wx.Notebook(self)
        self._curvesNBHaz = BymurWxNBHazPage(parent=self._nb,
                                             controller=self._controller,
                                             label="NBHazPage")
        self._curvesNBVuln = BymurWxNBVulnPage(parent=self._nb,
                                               controller=self._controller,
                                               label="NBVulnPage")
        self._curvesNBRisk = BymurWxNBRiskPage(parent=self._nb,
                                               controller=self._controller,
                                               label="NBRiskPage")

        self._nb.AddPage(self._curvesNBHaz, self._curvesNBHaz.title)
        self._nb.AddPage(self._curvesNBVuln, self._curvesNBVuln.title)
        self._nb.AddPage(self._curvesNBRisk, self._curvesNBRisk.title)

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._controller.nbTabChanged)
        self._sizer.Add(self._nb, 1, wx.EXPAND | wx.ALL, 10)

        self.SetSize((-1, 100))

    def updateView(self, **kwargs):
        super(BymurWxCurvesPanel, self).updateView(**kwargs)
        self._nb.GetCurrentPage().updateView(**kwargs)


class BymurWxMapPanel(BymurWxPanel):
    def __init__(self, *args, **kwargs):
        self._title = kwargs.pop('title', "Map")
        super(BymurWxMapPanel, self).__init__(*args, **kwargs)
        self._sizer = wx.BoxSizer(orient=wx.VERTICAL)
        # self._map = plotLibs.MapFigure(self, self._controller)
        self._map = plotLibs.HazardGraph(parent=self,
                                   click_callback=self._controller.onMapClick)
        # TODO: fix these references
        self._sizer.Add(self._map._canvas, 1, wx.EXPAND | wx.ALL, 0)
        self._sizer.Add(self._map._toolbar, 0, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(self._sizer)

    def updateView(self, **kwargs):
        super(BymurWxMapPanel, self).updateView(**kwargs)
        self._map.plot(wx.GetTopLevelParent(self).hazard_description,
                       wx.GetTopLevelParent(self).hazard_values)
        self.Enable(True)

    @property
    def title(self):
        """Get the current page title."""
        return self._title

    @property
    def map(self):
        """Get the current page title."""
        return self._map


class BymurWxNBHazPage(BymurWxPanel):
    def __init__(self, *args, **kwargs):
        self._title = kwargs.pop('title', "Hazard")
        super(BymurWxNBHazPage, self).__init__(*args, **kwargs)
        self._sizer = wx.BoxSizer(orient=wx.VERTICAL)
        # self._map = plotLibs.HazFigure(self, self._controller)
        self._map = plotLibs.HazardCurve(parent=self)
        # TODO: fix these references
        self._sizer.Add(self._map._canvas, 1, wx.EXPAND | wx.ALL, 0)
        self._sizer.Add(self._map._toolbar, 0, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(self._sizer)

    def updateView(self, **kwargs):
        super(BymurWxNBHazPage, self).updateView(**kwargs)
        # TODO: fix these references
        self._map.plot(wx.GetTopLevelParent(self).hazard_options,
                       wx.GetTopLevelParent(self).hazard_description,
                       wx.GetTopLevelParent(self).selected_point,
                       wx.GetTopLevelParent(self).selected_point_curves)
        self.Enable(True)

    @property
    def title(self):
        """Get the current page title."""
        return self._title


class BymurWxNBVulnPage(BymurWxPanel):
    def __init__(self, *args, **kwargs):
        self._title = kwargs.pop('title', "Vulnerability")
        super(BymurWxNBVulnPage, self).__init__(*args, **kwargs)
        self._sizer = wx.BoxSizer(orient=wx.VERTICAL)
        self._map = plotLibs.VulnCurve(parent=self)
        self._sizer.Add(self._map._canvas, 1, wx.EXPAND | wx.ALL, 0)
        self._sizer.Add(self._map._toolbar, 0, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(self._sizer)

    @property
    def title(self):
        """Get the current page title."""
        return self._title


class BymurWxNBRiskPage(BymurWxPanel):
    def __init__(self, *args, **kwargs):
        self._title = kwargs.pop('title', "Risk")
        super(BymurWxNBRiskPage, self).__init__(*args, **kwargs)
        self._sizer = wx.BoxSizer(orient=wx.VERTICAL)
        self._map = plotLibs.RiskCurve(parent=self)
        self._sizer.Add(self._map._canvas, 1, wx.EXPAND | wx.ALL, 0)
        self._sizer.Add(self._map._toolbar, 0, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(self._sizer)

    @property
    def title(self):
        """Get the current page title."""
        return self._title


class BymurWxRightPanel(BymurWxPanel):
    def __init__(self, *args, **kwargs):
        super(BymurWxRightPanel, self).__init__(*args, **kwargs)
        self._sizer = wx.BoxSizer(orient=wx.VERTICAL)
        self._mapPanel = BymurWxMapPanel(parent=self,
                                         controller=self._controller,
                                         label="MapPanel")
        self._mapBox = wx.StaticBox(self, wx.ID_ANY, self._mapPanel.title)
        self._mapBoxSizer = wx.StaticBoxSizer(self._mapBox,
                                              orient=wx.HORIZONTAL)
        self._mapBoxSizer.Add(self._mapPanel, 1, wx.EXPAND | wx.ALL, 0)
        self._mapPanel.Enable(False)
        self._sizer.Add(self._mapBoxSizer, 1, wx.EXPAND | wx.ALL, 5)

        self._curvesPanel = BymurWxCurvesPanel(self, id=wx.ID_ANY,
                                               controller=self._controller,
                                               label="CurvesPanel")

        self._curvesPanel.Enable(False)
        self._sizer.Add(self._curvesPanel, 1, wx.EXPAND | wx.ALL, 0)

        self.Centre()
        self.SetSizer(self._sizer)

    def updateView(self, **kwargs):
        super(BymurWxRightPanel, self).updateView(**kwargs)
        # self.Layout()

    @property
    def curvesPanel(self):
        return self._curvesPanel

    @property
    def mapPanel(self):
        return self._mapPanel


class BymurWxLeftPanel(BymurWxPanel):
    def __init__(self, *args, **kwargs):
        self._ctrlsBoxTitle = kwargs.pop('title', "Controls")
        super(BymurWxLeftPanel, self).__init__(*args, **kwargs)
        self._sizer = wx.BoxSizer(orient=wx.VERTICAL)

        self._ctrlsBox = wx.StaticBox(
            self,
            wx.ID_ANY,
            self.ctrlsBoxTitle)
        self._ctrlsBoxSizer = wx.StaticBoxSizer(
            self._ctrlsBox,
            orient=wx.VERTICAL)

        self._ctrlsSizer = wx.GridBagSizer(hgap=5, vgap=5)
        self._ctrlsBoxSizer.Add(self._ctrlsSizer)

        self._hazModLabel = wx.StaticText(self, wx.ID_ANY,
                                          'Hazard Model')
        self._hazModCB = wx.ComboBox(self, wx.ID_ANY, choices=[],
                                     style=wx.CB_READONLY, size=(200, -1))

        self._hazModCB.Bind(wx.EVT_COMBOBOX, self.updateCtrls)

        self._ctrlsSizer.Add(self._hazModLabel, pos=(0, 0), span=(1, 2),
                             flag=wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT)
        self._ctrlsSizer.Add(self._hazModCB, pos=(0, 2), span=(1, 2))

        self._retPerLabel = wx.StaticText(self, wx.ID_ANY, 'Return Period')
        self._retPerText = wx.TextCtrl(self, wx.ID_ANY, size=(120, -1),
                                       style=wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_TEXT_ENTER, self._controller.updateParameters,
                  self._retPerText)
        self._retPerLabelBis = wx.StaticText(self, wx.ID_ANY, '[years]')
        self._ctrlsSizer.Add(self._retPerLabel, pos=(1, 0), span=(1, 2),
                             flag=wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT)
        self._ctrlsSizer.Add(self._retPerText, pos=(1, 2), span=(1, 1))
        self._ctrlsSizer.Add(self._retPerLabelBis, pos=(1, 3), span=(1, 2),
                             flag=wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM)

        self._intThresLabel = wx.StaticText(self, wx.ID_ANY, 'Intensity '
                                                             'Threshold')
        self._intThresText = wx.TextCtrl(self, wx.ID_ANY, size=(120, -1),
                                         style=wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_TEXT_ENTER, self._controller.updateParameters,
                  self._intThresText)
        self._intThresLabelBis = wx.StaticText(self, wx.ID_ANY, '[0-1]')
        self._ctrlsSizer.Add(self._intThresLabel, pos=(2, 0), span=(1, 2),
                             flag=wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT)
        self._ctrlsSizer.Add(self._intThresText, pos=(2, 2), span=(1, 1))
        self._ctrlsSizer.Add(self._intThresLabelBis, pos=(2, 3), span=(1, 1),
                             flag=wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM)

        # timeWindow
        self._timeWindowLabel = wx.StaticText(self, wx.ID_ANY, 'Exposure Time')
        self._timeWindowCB = wx.ComboBox(self, wx.ID_ANY, choices=[],
                                         style=wx.CB_READONLY, size=(120, -1))
        self._timeWindowLabelBis = wx.StaticText(self, wx.ID_ANY, '[years]')
        self._ctrlsSizer.Add(self._timeWindowLabel, pos=(3, 0), span=(1, 2),
                             flag=wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT)
        self._ctrlsSizer.Add(self._timeWindowCB, pos=(3, 2), span=(1, 1))
        self._ctrlsSizer.Add(self._timeWindowLabelBis, pos=(3, 3), span=(1, 1),
                             flag=wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM)

        self._updateButton = wx.Button(self, wx.ID_ANY | wx.EXPAND,
                                       'Update Map',
                                       size=(-1, -1))
        self.Bind(wx.EVT_BUTTON, self._controller.updateParameters,
                  self._updateButton)
        self._ctrlsSizer.Add(self._updateButton, flag=wx.EXPAND, pos=(4, 0),
                             span=(3, 4))

        self._sizer.Add(self._ctrlsBoxSizer)
        self.SetSizer(self._sizer)
        # self.Enable(False)

    def updateCtrls(self, ev ):
        if (ev.GetEventType() == wx.wxEVT_COMMAND_COMBOBOX_SELECTED) and\
                (ev.GetEventObject() == self._hazModCB):
            _haz_sel = self._hazModCB.GetValue()
            for haz in wx.GetTopLevelParent(self).ctrls_data['hazard_models']:
                if haz['hazard_name'] == _haz_sel:
                    _exp_times = [str(et['years']) for et in haz['exposure_times']]
                    self._timeWindowCB.Clear()
                    self._timeWindowCB.AppendItems(_exp_times)
                    self._timeWindowCB.SetSelection(0)
                    break

    def updateView(self, **kwargs):
        super(BymurWxLeftPanel, self).updateView(**kwargs)
        # [{'id_phenomenon', 'phenomenon_name', 'haz_id', 'haz_name'}]
        # print "kwargs %s"
        # print "kwargs %s" % kwargs
        ctrls_data = wx.GetTopLevelParent(self).ctrls_data

        _haz_sel = self._hazModCB.GetSelection()
        print "_haz_sel %s" % _haz_sel
        self._hazModCB.Clear()
        self._hazModCB.AppendItems([haz['hazard_name'] for haz in ctrls_data[
            'hazard_models']])
        try:
            self._hazModCB.SetSelection(_haz_sel)
        except:
            print "Exception _hazModCB.SetSelection"
            pass

        self._retPerText.SetValue(str(int(ctrls_data['ret_per'])))
        self._intThresText.SetValue(str(ctrls_data['int_thresh']))

        _exp_times = []
        for haz in ctrls_data['hazard_models']:
            if haz['hazard_name'] == _haz_sel:
                _exp_times = [str(et['years']) for et in haz['exposure_times']]

        _exp_sel = self._timeWindowCB.GetSelection()
        self._timeWindowCB.Clear()
        self._timeWindowCB.AppendItems(_exp_times)
        try:
            self._timeWindowCB.SetSelection(_exp_sel)
        except:
            print "Exception settin _exp_sel"
            pass
        # self.Enable(True)

    @property
    def ctrlsBoxTitle(self):
        """Get the current ctrlsBoxTitle."""
        return self._ctrlsBoxTitle

    @ctrlsBoxTitle.setter
    def ctrlsBoxTitle(self, value):
        self._ctrlsBoxTitle = value
        self._ctrlsBox.SetLabel(self._ctrlsBoxTitle)

    @property
    def hazard_options(self):
        """Get the current ctrlsBox parameters"""
        values = {}
        values['haz_mod'] = self._hazModCB.GetStringSelection()
        values['ret_per'] = self._retPerText.GetValue()
        values['int_thresh'] = self._intThresText.GetValue()
        print self._timeWindowCB.GetStringSelection()
        print self._timeWindowCB.GetCurrentSelection()
        print self._timeWindowCB.GetSelection()
        values['exp_time'] = self._timeWindowCB.GetStringSelection()
        return values


class BymurWxMenu(wx.MenuBar):
    """
    This class provides all program menus
    """
    _menu_actions = {}
    _db_actions = []
    _map_actions = []

    def __init__(self, *args, **kwargs):
        self._controller = kwargs.pop('controller', None)
        super(BymurWxMenu, self).__init__(*args, **kwargs)

        # File menu and items
        self.menuFile = wx.Menu()
        menuItemTmp = self.menuFile.Append(wx.ID_ANY, '&Load database')
        self._menu_actions[menuItemTmp.GetId()] = self._controller.loadDB
        menuItemTmp = self.menuFile.Append(wx.ID_ANY, '&Connect database')
        self._menu_actions[menuItemTmp.GetId()] = self._controller.connectDB
        menuItemTmp = self.menuFile.Append(wx.ID_ANY, '&EVENT')
        self._menu_actions[menuItemTmp.GetId()] = self.fireEvent
        self.menuFile.AppendSeparator()
        self.menuFile.Append(wx.ID_CLOSE, '&Quit')
        self._menu_actions[wx.ID_CLOSE] = self._controller.quit
        self.Append(self.menuFile, '&File')

        # Database menu and items
        self.menuDB = wx.Menu()
        menuItemTmp = self.menuDB.Append(wx.ID_ANY,
                                         '&Create DataBase (DB)')  # original method was openCreateDB
        self._menu_actions[menuItemTmp.GetId()] = self._controller.createDB
        menuItemTmp = self.menuDB.Append(wx.ID_ANY, '&Add Data to DB')
        self._db_actions.append(menuItemTmp)
        self._menu_actions[
            menuItemTmp.GetId()] = self._controller.addDBData  # original method was openAddDB
        menuItemTmp.Enable(False)
        self.menuDB.AppendSeparator()
        menuItemTmp = self.menuDB.Append(wx.ID_ANY, '&Drop All DB Tables')
        self._db_actions.append(menuItemTmp)
        menuItemTmp.Enable(False)
        self._menu_actions[
            menuItemTmp.GetId()] = self._controller.dropDBTables  # original method was dropAllTabs
        self.Append(self.menuDB, '&DataBase')

        # Plot menu and items
        self.menuPlot = wx.Menu()
        menuItemTmp = self.menuPlot.Append(wx.ID_ANY,
                                           '&Export Raster ASCII (GIS)')  # original method was exportAsciiGis
        self._menu_actions[menuItemTmp.GetId()] = self._controller.exportASCII
        self._map_actions.append(menuItemTmp)
        menuItemTmp.Enable(False)
        menuItemTmp = self.menuPlot.Append(wx.ID_ANY, '&Show Points',
                                           kind=wx.ITEM_CHECK)  # original method was showPoints
        self._menu_actions[menuItemTmp.GetId()] = self._controller.showPoints
        menuItemTmp.Enable(False)
        self.Append(self.menuPlot, '&Map')

        # Analysis menu and items
        self.menuAnalysis = wx.Menu()
        menuItemTmp = self.menuAnalysis.Append(wx.ID_ANY,
                                               'Create &Ensemble hazard')  # original method was openEnsembleFr
        self._menu_actions[
            menuItemTmp.GetId()] = self._controller.openEnsemble
        self._map_actions.append(menuItemTmp)
        menuItemTmp.Enable(False)
        self.Append(self.menuAnalysis, '&Analysis')


    def doMenuAction(self, event):
        evt_id = event.GetId()
        action = self._menu_actions.get(evt_id, None)
        if action:
            action()
        else:
            raise Exception, "Menu action not defined!"

    def fireEvent(self):
        print "Load..."
        event = gf.BymurUpdateEvent(gf.BYMUR_UPDATE_ALL,1)
        print "Aim"
        wx.PostEvent(self, event)
        print "Fire!"

    @property
    def dbControls(self):
        return self._db_actions

    @property
    def mapControls(self):
        return self._map_actions


class BymurWxView(wx.Frame):
    # TODO: lot of methods should be moved to wx.App, not frame
    status_txt_ready = "ByMuR ready"
    _isbusy = False
    _busymsg = "Wait please..."
    _disableAll = None

    # TODO: These should be in controller or core?
    _db_connected = False
    _db_loaded = False

    def __init__(self, *args, **kwargs):
        self._controller = kwargs.pop('controller', None)
        self._title = kwargs.pop('title', '')
        super(BymurWxView, self).__init__(*args, **kwargs)

        self._ctrls_data = {}
        self._hazard_options = {}
        self._hazard_description = None
        self._hazard_values = None
        self._selected_point = None
        self._selected_point_curves = None

        # TODO: make a list for events
        self.Bind(gf.BYMUR_UPDATE_ALL, self.OnBymurEvent)
        self.Bind(gf.BYMUR_UPDATE_CURVE, self.OnBymurEvent)
        self.Bind(gf.BYMUR_UPDATE_MAP, self.OnBymurEvent)
        self.Bind(gf.BYMUR_UPDATE_DIALOG, self.OnBymurEvent)
        self.Bind(gf.BYMUR_UPDATE_CTRLS, self.OnBymurEvent)
        self.Bind(gf.BYMUR_THREAD_CLOSED, self.OnBymurEvent)
        self.Bind(gf.BYMUR_DB_CONNECTED, self.OnBymurEvent)

        # Menu
        self.menuBar = BymurWxMenu(controller=self._controller)
        self.SetMenuBar(self.menuBar)
        self.Bind(wx.EVT_MENU, self.menuBar.doMenuAction)

        # StatusBar
        self.statusbar = self.CreateStatusBar()
        self.PushStatusText(self.status_txt_ready)

        # Main panel
        self.mainSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        self._leftPanel = BymurWxLeftPanel(parent=self,
                                           controller=self._controller,
                                           title="Hazard",
                                           label="LeftPanel")
        self._rightPanel = BymurWxRightPanel(parent=self,
                                             controller=self._controller,
                                             label="RightPanel")
        self.mainSizer.Add(self._leftPanel, 0, wx.EXPAND)
        self.mainSizer.Add(self._rightPanel, 1, wx.EXPAND)
        self.SetSizer(self.mainSizer)
        self.SetSize((950, 750))

    def refresh(self):
        wx.SafeYield()
        self.Refresh()
        self.Update()

    def updateView(self, **kwargs):
        print "Main WxFrame"
        # for panel in self.GetChildren():
        #     if isinstance(panel, BymurWxPanel):
        #         panel.updateView(**kwargs)

    def saveFile(self, dfl_dir, get_text):
        ext = '.txt'
        dlg = wx.FileDialog(self, message="Save File as...",
                            defaultDir=dfl_dir, defaultFile="*.txt",
                            wildcard="*.*",
                            style=wx.SAVE | wx.FD_OVERWRITE_PROMPT)
        dlg_result = dlg.ShowModal()
        dlg.Destroy()
        if dlg_result == wx.ID_OK:
            savepath = dlg.GetPath()
            if savepath[-4:] == ext:
                filename = savepath
            else:
                filename = savepath + ext

            try:
                fp = open(filename, "w")
                # TODO: i shloud refactor to avoid calculations in the view!
                fp.writelines(get_text(self.rightPanel.mapPanel.map.hazArray))
                fp.close()
            except Exception as e:
                gf.showMessage(parent=self,
                               message=str(e),
                               kind="BYMUR_ERROR",
                               caption="Error")

    def showDlg(self, dialog_type, **kwargs):
        """
        :param dialog_type: class name of the dialog to show
        :param **kwargs: argument to the specific dialog
        :return: dictionary containing dialog data on success, None on failure
        """
        result = -1
        data = {}
        dlg = eval(dialog_type)(parent=self, **kwargs)
        while result < 0:
            result, data = dlg.ShowModal()
        if result > 0:
            return data
        else:
            return None

    def GetBusy(self):
        """
        Is the application busy?
        :return: Boolean
        """
        return self._isbusy

    def SetBusy(self, state, **kwargs):
        """
        Setting the application busy
        :param state: Boolean
        """
        self._isbusy = state
        print "state %s" % state
        wait_msg = kwargs.pop('wait_msg', self._busymsg)
        if self._isbusy:
            # self._old_style = self.GetWindowStyle()
            # self.Hide()
            # self.SetWindowStyle(self._old_style | wx.STAY_ON_TOP)
            self.PushStatusText(wait_msg)
            self.Disable()
            self._busydlg = BymurBusyDlg(wait_msg, parent=self)


        else:
            self.PopStatusText()
            # self.Show()
            self._busydlg.Destroy()
            self.Enable()
            del self._busydlg
            # del self._disableAll
            # self.SetWindowStyle(self._old_style)


    def wait(self, **kwargs):
        self.SetBusy(True, **kwargs)


    def OnBymurEvent(self, event):
        print event.__class__.__name__
        print "Ricevuto!"
        if  event.GetEventType() == gf.wxBYMUR_DB_CONNECTED:
            print "gf.wxBYMUR_DB_CONNECTED"
        elif event.GetEventType() == gf.wxBYMUR_UPDATE_CTRLS:
            print "gf.wxBYMUR_UPDATE_CTRLS"
            self.leftPanel.updateView()
        elif event.GetEventType() == gf.wxBYMUR_UPDATE_ALL:
            print "gf.wxBYMUR_UPDATE_ALL"
            self.leftPanel.updateView()
            self.rightPanel.mapPanel.updateView()
            self.rightPanel.Enable(True)
        self.SetBusy(False)

# on connect
# gf.showMessage,
#                     {'parent' : self.wxframe,
#                      'message' : "Connection Succeded!",
#                      'kind': "BYMUR_INFO",
#                      'caption': "Info"},

    @property
    def rightPanel(self):
        return self._rightPanel

    @property
    def leftPanel(self):
        return self._leftPanel

    @property
    def hazard_options(self):
        return self._leftPanel.hazard_options


    @property
    def busymsg(self):
        """
        """
        return self._busymsg

    @busymsg.setter
    def busymsg(self, msg):
        self._busymsg = msg

    @property
    def dbConnected(self):
        return self._db_connected

    @dbConnected.setter
    def dbConnected(self, value):
        self._db_connected = value
        for item in self.menuBar.dbControls:
            self.menuBar.Enable(item.GetId(), value)

    @property
    def dbLoaded(self):
        return self._db_loaded

    @dbLoaded.setter
    def dbLoaded(self, value):
        self.dbConnected = value
        self._db_loaded = value
        for item in self.menuBar.mapControls:
            self.menuBar.Enable(item.GetId(), value)

    @property
    def ctrls_data(self):
        return self._ctrls_data

    @ctrls_data.setter
    def ctrls_data(self,data):
        self._ctrls_data = data
        
    @property
    def hazard_options(self):
        return self._hazard_options

    @hazard_options.setter
    def hazard_options(self, data):
        self._hazard_options = data
        
    @property
    def hazard_description(self):
        return self._hazard_description

    @hazard_description.setter
    def hazard_description(self, data):
        self._hazard_description = data

    @property
    def hazard_values(self):
        return self._hazard_values

    @hazard_values.setter
    def hazard_values(self, data):
        self._hazard_values = data
        
    @property
    def selected_point(self):
        return self._selected_point

    @selected_point.setter
    def selected_point(self, data):
        self._selected_point = data

    @property
    def selected_point_curves(self):
        return self._selected_point_curves

    @selected_point_curves.setter
    def selected_point_curves(self, data):
        self._selected_point_curves = data

class BymurWxApp(wx.App):
    def __init__(self, *args, **kwargs):
        self._controller = kwargs.pop('controller', None)
        super(BymurWxApp, self).__init__(*args, **kwargs)


    def OnInit(self):
        frame = BymurWxView(parent=None, controller=self._controller,
                            title="ByMuR - Refactoring")

        self._controller.SetWxFrame(frame)

        self._controller._wxframe = frame

        frame.Show(True)
        return True


if __name__ == "__main__":
    core = bymurcore.BymurCore()
    control = bymurcontroller.BymurController(core=core)
    app = BymurWxApp(redirect=False, controller=control)
    app.MainLoop()