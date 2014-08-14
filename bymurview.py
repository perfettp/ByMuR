import wx
import plotLibs


def bymurMessage(**kwargs):
    style=kwargs.pop('style',0)
    style |= wx.OK
    if (kwargs.get('kind','') == 'BYMUR_ERROR'):
        style |= wx.ICON_ERROR
    else:
        style |= wx.ICON_INFORMATION
    wx.MessageBox(message=kwargs.pop('message',''),
                  caption=kwargs.pop('caption',''),
                  style=style
    )

class BymurDBDialog(wx.Dialog):

    _textSize=(300, -1)

    def __init__(self, *args, **kwargs):
        self._title=kwargs.pop('title', '')
        self._style=kwargs.pop('style', 0)
        self._style |= wx.OK|wx.CANCEL
        self._dbDetails={'dbHost': kwargs.pop('dbHost',''),
                         'dbPort': kwargs.pop('dbPort',''),
                         'dbUser': kwargs.pop('dbUser',''),
                         'dbPassword': kwargs.pop('dbPassword',''),
                         'dbName':  kwargs.pop('dbName','')
        }
        super(BymurDBDialog, self).__init__(style=self._style,*args, **kwargs)

        self._sizer=wx.BoxSizer(orient=wx.VERTICAL)
        self._mainBox=wx.StaticBox(self, label="Connection details")
        self._mainBoxSizer=wx.StaticBoxSizer(self._mainBox,
                                      orient=wx.VERTICAL)

        self._dbSizer=wx.GridBagSizer(hgap=5, vgap=5)
        self._mainBoxSizer.Add(self._dbSizer)

        row = 0
        self._dbHost = wx.StaticText(self, wx.ID_ANY, 'Server hostname: ')
        self._dbSizer.Add(self._dbHost, pos=(row, 0))
        self._dbHostText = wx.TextCtrl(self, wx.ID_ANY, size=self._textSize)
        self._dbHostText.SetValue(self._dbDetails['dbHost'])
        self._dbSizer.Add(self._dbHostText, pos=(row, 1))
        row += 1
        self._dbPort = wx.StaticText(self, wx.ID_ANY, 'Server Port: ')
        self._dbSizer.Add(self._dbPort, pos=(row, 0))
        self._dbPortText = wx.TextCtrl(self, wx.ID_ANY, size=self._textSize)
        self._dbPortText.SetValue(self._dbDetails['dbPort'])
        self._dbSizer.Add(self._dbPortText, pos=(row, 1))
        row += 1
        self._dbUser = wx.StaticText(self, wx.ID_ANY, 'User: ')
        self._dbSizer.Add(self._dbUser, pos=(row, 0))
        self._dbUserText = wx.TextCtrl(self, wx.ID_ANY, size=self._textSize)
        self._dbUserText.SetValue(self._dbDetails['dbUser'])
        self._dbSizer.Add(self._dbUserText, pos=(row, 1))
        row += 1
        self._dbPassword = wx.StaticText(self, wx.ID_ANY, 'Password: ')
        self._dbSizer.Add(self._dbPassword, pos=(row, 0))
        self._dbPasswordText = wx.TextCtrl(self, wx.ID_ANY, size=self._textSize)
        self._dbPasswordText.SetValue(self._dbDetails['dbPassword'])
        self._dbSizer.Add(self._dbPasswordText, pos=(row, 1))
        row += 1
        self._dbName = wx.StaticText(self, wx.ID_ANY, 'Database name: ')
        self._dbSizer.Add(self._dbName, pos=(row, 0))
        self._dbNameText = wx.TextCtrl(self, wx.ID_ANY, size=self._textSize)
        self._dbNameText.SetValue(self._dbDetails['dbName'])
        self._dbSizer.Add(self._dbNameText, pos=(row, 1))

        self._mainBoxSizer.Add(self.CreateButtonSizer(flags=wx.OK|wx.CANCEL))

        self._sizer.Add(self._mainBoxSizer)
        self.SetSizerAndFit(self._sizer)

        self.SetTitle(self._title)

    def ShowModal(self, *args, **kwargs):
        result = super(BymurDBDialog, self).ShowModal(*args, **kwargs)
        if (result==wx.ID_OK):
            result=1
            self._dbDetails['dbHost']=self._dbHostText.GetValue()
            self._dbDetails['dbPort']=self._dbPortText.GetValue()
            self._dbDetails['dbUser']=self._dbUserText.GetValue()
            self._dbDetails['dbPassword']=self._dbPasswordText.GetValue()
            self._dbDetails['dbName']=self._dbNameText.GetValue()
        elif (result==wx.ID_CANCEL):
            result=0
        else:
            result=-1
        return (result, self._dbDetails)

class BymurWxPanel(wx.Panel):

    def __init__(self, *args, **kwargs):
        self._bymur_label = kwargs.pop('label', "")
        self._controller = kwargs.pop('controller', None)
        super(BymurWxPanel, self).__init__(*args, **kwargs)
        self.Enable(False)

    def updateView(self, **kwargs):
        #TODO: is it correct to enable/disable here?
        self.Enable(False)
        print self._bymur_label
        for panel in  self.GetChildren():
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
        self._map = plotLibs.MapFigure(self, self._controller)
        self._sizer.Add(self._map.canvas, 1, wx.EXPAND | wx.ALL, 0)
        self._sizer.Add(self._map.toolbar, 0, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(self._sizer)

    def updateView(self, **kwargs):
        super(BymurWxMapPanel, self).updateView(**kwargs)
        self._map.hazardMap(**kwargs)

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
        self._map = plotLibs.HazFigure(self, self._controller)
        self._sizer.Add(self._map.canvas, 1, wx.EXPAND | wx.ALL, 0)
        self._sizer.Add(self._map.toolbar, 0, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(self._sizer)

    def updateView(self, **kwargs):
        super(BymurWxNBHazPage, self).updateView(**kwargs)
        self._map.hazardCurve(**kwargs)

    @property
    def title(self):
        """Get the current page title."""
        return self._title

class BymurWxNBVulnPage(BymurWxPanel):
    def __init__(self, *args, **kwargs):
        self._title = kwargs.pop('title', "Vulnerability")
        super(BymurWxNBVulnPage, self).__init__(*args, **kwargs)
        self._sizer = wx.BoxSizer(orient=wx.VERTICAL)
        self._map = plotLibs.VulnFigure(self, self._controller)
        self._sizer.Add(self._map.canvas, 1, wx.EXPAND | wx.ALL, 0)
        self._sizer.Add(self._map.toolbar, 0, wx.EXPAND | wx.ALL, 0)
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
        self._map = plotLibs.RiskFigure(self, self._controller)
        self._sizer.Add(self._map.canvas, 1, wx.EXPAND | wx.ALL, 0)
        self._sizer.Add(self._map.toolbar, 0, wx.EXPAND | wx.ALL, 0)
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
        self._ctrlsSizer.Add(self._hazModLabel, pos = (0 , 0), span = (1, 2),
                              flag = wx.ALIGN_BOTTOM|wx.ALIGN_RIGHT)
        self._ctrlsSizer.Add(self._hazModCB, pos = (0, 2), span = (1, 2))

        self._retPerLabel = wx.StaticText(self, wx.ID_ANY, 'Return Period')
        self._retPerText = wx.TextCtrl(self, wx.ID_ANY, size=(120, -1),
                                       style=wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_TEXT_ENTER , self._controller.updateParameters,
                  self._retPerText)
        self._retPerLabelBis = wx.StaticText(self, wx.ID_ANY, '[years]')
        self._ctrlsSizer.Add(self._retPerLabel, pos = (1, 0), span = (1, 2),
                             flag = wx.ALIGN_BOTTOM|wx.ALIGN_RIGHT)
        self._ctrlsSizer.Add(self._retPerText, pos = (1, 2), span = (1, 1))
        self._ctrlsSizer.Add(self._retPerLabelBis, pos = (1, 3), span = (1,2),
                              flag = wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM )

        self._intThresLabel = wx.StaticText(self, wx.ID_ANY, 'Intensity '
                                                             'Threshold')
        self._intThresText = wx.TextCtrl(self, wx.ID_ANY, size=(120, -1),
                                              style=wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_TEXT_ENTER , self._controller.updateParameters,
                  self._intThresText)
        self._intThresLabelBis = wx.StaticText(self, wx.ID_ANY, '[0-1]')
        self._ctrlsSizer.Add(self._intThresLabel, pos = (2, 0), span = (1, 2),
                              flag = wx.ALIGN_BOTTOM|wx.ALIGN_RIGHT)
        self._ctrlsSizer.Add(self._intThresText, pos = (2, 2), span = (1, 1))
        self._ctrlsSizer.Add(self._intThresLabelBis, pos = (2, 3), span = (1,1),
                             flag = wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM)

        # expTime
        self._expTimeLabel = wx.StaticText(self, wx.ID_ANY, 'Exposure Time')
        self._expTimeCB = wx.ComboBox(self, wx.ID_ANY, choices=[],
                                     style=wx.CB_READONLY, size=(120, -1))
        self._expTimeLabelBis = wx.StaticText(self, wx.ID_ANY, '[years]')
        self._ctrlsSizer.Add(self._expTimeLabel, pos = (3, 0), span = (1, 2),
                             flag = wx.ALIGN_BOTTOM|wx.ALIGN_RIGHT)
        self._ctrlsSizer.Add(self._expTimeCB, pos = (3, 2), span = (1, 1))
        self._ctrlsSizer.Add(self._expTimeLabelBis, pos = (3, 3), span = (1, 1),
                             flag = wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM)


        self._updateButton = wx.Button(self, wx.ID_ANY|wx.EXPAND, 'Update Map',
                                  size=(-1, -1))
        self.Bind(wx.EVT_BUTTON, self._controller.updateParameters,
                  self._updateButton)
        self._ctrlsSizer.Add(self._updateButton, flag=wx.EXPAND, pos = (4, 0),
                             span = (3, 4))

        self._sizer.Add(self._ctrlsBoxSizer)
        self.SetSizer(self._sizer)


    def updateView(self, **kwargs):
        super(BymurWxLeftPanel, self).updateView(**kwargs)
        self._hazModCB.Clear()
        self._hazModCB.AppendItems(kwargs['model'])
        self._hazModCB.SetSelection(kwargs['haz_mod'])
        self._retPerText.SetValue(str(int(kwargs['ret_per'])))
        self._intThresText.SetValue(str(kwargs['int_thres']))
        self._expTimeCB.Clear()
        self._expTimeCB.AppendItems(kwargs['dtime'][
            self._hazModCB.GetSelection()])
        self._expTimeCB.SetSelection(kwargs['exp_time'])
        self.Enable(True)

    @property
    def ctrlsBoxTitle(self):
        """Get the current ctrlsBoxTitle."""
        return self._ctrlsBoxTitle

    @ctrlsBoxTitle.setter
    def ctrlsBoxTitle(self, value):
        self._ctrlsBoxTitle = value
        self._ctrlsBox.SetLabel(self._ctrlsBoxTitle)

    @property
    def ctrlsValues(self):
        """Get the current ctrlsBox parameters"""
        values={}
        values['haz_mod']=self._hazModCB.GetSelection()
        values['ret_per']=self._retPerText.GetValue()
        values['int_thres']=self._intThresText.GetValue()
        values['exp_time']=self._expTimeCB.GetSelection()
        return values

class BymurWxMenu(wx.MenuBar):
    """
    This class provides all program menus
    """
    _menu_actions = {}

    def __init__(self, *args, **kwargs):
        self._controller = kwargs.pop('controller', None)
        super(BymurWxMenu, self).__init__(*args, **kwargs)

        # File menu and items
        self.menuFile = wx.Menu()
        menuItemTmp = self.menuFile.Append(wx.ID_ANY, '&Load database')
        self._menu_actions[menuItemTmp.GetId()] = self._controller.loadDB
        menuItemTmp = self.menuFile.Append(wx.ID_ANY, '&Load remote ByMuR DB')
        self._menu_actions[menuItemTmp.GetId()] = self._controller.remoteDB
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
        self._menu_actions[
            menuItemTmp.GetId()] = self._controller.addDBData  # original method was openAddDB
        menuItemTmp.Enable(False)
        self.menuDB.AppendSeparator()
        menuItemTmp = self.menuDB.Append(wx.ID_ANY, '&Drop All DB Tables')
        self._menu_actions[
            menuItemTmp.GetId()] = self._controller.dropDBTables  # original method was dropAllTabs
        self.Append(self.menuDB, '&DataBase')

        # Plot menu and items
        self.menuPlot = wx.Menu()
        menuItemTmp = self.menuPlot.Append(wx.ID_ANY,
                                           '&Export Raster ASCII (GIS)')  # original method was exportAsciiGis
        self._menu_actions[menuItemTmp.GetId()] = self._controller.exportASCII
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
        self._menu_actions[menuItemTmp.GetId()] = self._controller.openEnsembleFr
        menuItemTmp.Enable(False)
        self.Append(self.menuAnalysis, '&Analysis')


    def doMenuAction(self, event):
        evt_id = event.GetId()
        action = self._menu_actions.get(evt_id, None)
        if action:
            action()
        else:
            raise Exception, "Menu action not defined!"

class BymurWxView(wx.Frame):
    textWelcome = "Welcome in ByMuR"

    def __init__(self, *args, **kwargs):
        self._controller = kwargs.pop('controller', None)
        self._title = kwargs.pop('title', '')
        super(BymurWxView, self).__init__( *args, **kwargs)

        # Menu
        self.menuBar = BymurWxMenu(controller=self._controller)
        self.SetMenuBar(self.menuBar)
        self.Bind(wx.EVT_MENU, self.menuBar.doMenuAction)

        # StatusBar
        self.statusbar = self.CreateStatusBar()
        self.PushStatusText(self.textWelcome)

        #Main panel
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

    def updateView(self, **kwargs):
        print "Main WxFrame"
        for panel in  self.GetChildren():
            if isinstance(panel, BymurWxPanel):
                panel.updateView(**kwargs)

    @property
    def rightPanel(self):
        return self._rightPanel

    @property
    def leftPanel(self):
        return self._leftPanel

    @property
    def ctrlsValues(self):
        print "Dentro BymurWxView"
        return self._leftPanel.ctrlsValues

class BymurWxApp(wx.App):
    def __init__(self, *args, **kwargs):
        self._controller = kwargs.pop('controller', None)
        super(BymurWxApp, self).__init__( *args, **kwargs)


    def OnInit(self):
        frame = BymurWxView(parent=None, controller=self._controller,
                            title="ByMuR - Refactoring")
        self._controller.wxframe = frame
        frame.Show(True)
        return True