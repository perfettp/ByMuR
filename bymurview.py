import wx
import plotLibs

class BymurDBDialog(wx.Dialog):
    def __init__(self, *args, **kwargs):
        self._title=kwargs.pop('title', '')
        # self._style=kwargs.pop('style', 0)
        # self._style |= wx.OK|wx.CANCEL
        super(BymurDBDialog, self).__init__(*args, **kwargs)

        self._sizer=wx.BoxSizer(orient=wx.VERTICAL)
        self._mainBox=wx.StaticBox(self, label="Connection details")
        self._mainBoxSizer=wx.StaticBoxSizer(self._mainBox,
                                      orient=wx.VERTICAL)

        self._dbSizer=wx.GridBagSizer(hgap=5, vgap=5)
        self._mainBoxSizer.Add(self._dbSizer)

        self._dbHost = wx.StaticText(self, wx.ID_ANY, 'Server hostname: ')
        self._dbSizer.Add(self._dbHost, pos=(0, 0))
        self._dbHostText = wx.TextCtrl(self, wx.ID_ANY)
        self._dbSizer.Add(self._dbHostText, pos=(0, 1))
        self._dbUser = wx.StaticText(self, wx.ID_ANY, 'User: ')
        self._dbSizer.Add(self._dbUser, pos=(1, 0))
        self._dbUserText = wx.TextCtrl(self, wx.ID_ANY)
        self._dbSizer.Add(self._dbUserText, pos=(1, 1))
        self._dbPassword = wx.StaticText(self, wx.ID_ANY, 'Password: ')
        self._dbSizer.Add(self._dbPassword, pos=(2, 0))
        self._dbPasswordText = wx.TextCtrl(self, wx.ID_ANY)
        self._dbSizer.Add(self._dbPasswordText, pos=(2, 1))
        self._dbName = wx.StaticText(self, wx.ID_ANY, 'Database name: ')
        self._dbSizer.Add(self._dbName, pos=(3, 0))
        self._dbNameText = wx.TextCtrl(self, wx.ID_ANY)
        self._dbSizer.Add(self._dbNameText, pos=(3, 1))

        self._okButton=wx.Button(self, label='Ok')
        self._dbSizer.Add(self._okButton, pos=(4, 0))
        self._closeButton = wx.Button(self, label='Close')
        self._dbSizer.Add(self._closeButton, pos=(4, 1))

        self._sizer.Add(self._mainBoxSizer)
        self.SetSizer(self._sizer)

        # # okButton.Bind(wx.EVT_BUTTON, self.OnClose)
        # # closeButton.Bind(wx.EVT_BUTTON, self.OnClose)

        # self.SetSize((350, 200))
        self.SetTitle(self._title)

class BymurWxMapPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        self._controller = kwargs.pop('controller', None)
        self._title = kwargs.pop('title', "Map")
        super(BymurWxMapPanel, self).__init__(*args, **kwargs)
        self._sizer = wx.BoxSizer(orient=wx.VERTICAL)
        self._map = plotLibs.MapFigure(self, self._controller)
        self._sizer.Add(self._map.canvas, 1, wx.EXPAND | wx.ALL, 0)
        self._sizer.Add(self._map.toolbar, 0, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(self._sizer)

    @property
    def title(self):
        """Get the current page title."""
        return self._title

class BymurWxNBHazPage(wx.Panel):
    def __init__(self, *args, **kwargs):
        self._controller = kwargs.pop('controller', None)
        self._title = kwargs.pop('title', "Hazard")
        super(BymurWxNBHazPage, self).__init__(*args, **kwargs)
        self._sizer = wx.BoxSizer(orient=wx.VERTICAL)
        self._map = plotLibs.HazFigure(self, self._controller)
        self._sizer.Add(self._map.canvas, 1, wx.EXPAND | wx.ALL, 0)
        self._sizer.Add(self._map.toolbar, 0, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(self._sizer)

    @property
    def title(self):
        """Get the current page title."""
        return self._title

class BymurWxNBVulnPage(wx.Panel):
    def __init__(self, *args, **kwargs):
        self._controller = kwargs.pop('controller', None)
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

class BymurWxNBRiskPage(wx.Panel):
    def __init__(self, *args, **kwargs):
        self._controller = kwargs.pop('controller', None)
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

class BymurWxRightPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        self._controller = kwargs.pop('controller', None)
        super(BymurWxRightPanel, self).__init__(*args, **kwargs)
        self._sizer = wx.BoxSizer(orient=wx.VERTICAL)
        self._mapPanel = BymurWxMapPanel(parent=self,
                                         controller=self._controller)
        self._mapBox = wx.StaticBox(self, wx.ID_ANY, self._mapPanel.title)
        self._mapBoxSizer = wx.StaticBoxSizer(self._mapBox,
                                              orient=wx.HORIZONTAL)
        self._mapBoxSizer.Add(self._mapPanel, 1, wx.EXPAND | wx.ALL, 0)
        self._mapPanel.Enable(False)
        self._sizer.Add(self._mapBoxSizer, 1, wx.EXPAND | wx.ALL, 5)

        self._curvesPanel = wx.Panel(self, wx.ID_ANY)
        self._curvesSizer = wx.BoxSizer(orient=wx.VERTICAL)
        self._curvesPanel.SetSizer(self._curvesSizer)
        self._curvesNB = wx.Notebook(self._curvesPanel)
        self._curvesNBHaz = BymurWxNBHazPage(parent=self._curvesNB,
                                             controller=self._controller)
        self._curvesNBVuln = BymurWxNBVulnPage(parent=self._curvesNB,
                                               controller=self._controller)
        self._curvesNBRisk = BymurWxNBRiskPage(parent=self._curvesNB,
                                               controller=self._controller)

        self._curvesNB.AddPage(self._curvesNBHaz, self._curvesNBHaz.title)
        self._curvesNB.AddPage(self._curvesNBVuln, self._curvesNBVuln.title)
        self._curvesNB.AddPage(self._curvesNBRisk, self._curvesNBRisk.title)

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._controller.nbTabChanged)
        self._curvesSizer.Add(self._curvesNB, 1, wx.EXPAND | wx.ALL, 10)

        self._curvesPanel.Enable(False)
        self._sizer.Add(self._curvesPanel, 1, wx.EXPAND | wx.ALL, 0)

        self._curvesPanel.SetSize((-1, 100))
        self.Centre()
        self.SetSizer(self._sizer)

class BymurWxLeftPanel(wx.Panel):

    def __init__(self, *args, **kwargs):
        self._controller = kwargs.pop('controller', None)
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
               
        # hazMod
        self._hazModLabel = wx.StaticText(self, wx.ID_ANY,
                                        'Select Hazard Model:')
        self._hazModCB = wx.ComboBox(self, wx.ID_ANY, choices=[],
                                    style=wx.CB_READONLY, size=(-1, -1))
        self.Bind(wx.EVT_COMBOBOX, self._controller.selHazard, self._hazModCB)
        self._ctrlsSizer.Add(self._hazModLabel, pos = (0 , 0), span = (1, 2))
        self._ctrlsSizer.Add(self._hazModCB, pos = (1, 0), span = (1, 2))

        # retPer
        self._retPerLabel = wx.StaticText(self, wx.ID_ANY,
                                         'Select Return Period (year):')
        self._retPerText = wx.TextCtrl(self, wx.ID_ANY, size=(80, -1))
        self._retPerButton = wx.Button(self, wx.ID_ANY, 'Update Map',
                                  size=(-1, 26))
        self.Bind(wx.EVT_BUTTON, self._controller.selReturnPeriod,
                    self._retPerButton)
        self._ctrlsSizer.Add(self._retPerLabel, pos = (2, 0), span = (1, 2))
        self._ctrlsSizer.Add(self._retPerText, pos = (3, 0), span = (1, 1))
        self._ctrlsSizer.Add(self._retPerButton, pos = (3, 1), span = (1, 1))

        # intThres
        self._intThresLabel = wx.StaticText(self, wx.ID_ANY,
                                        'Select Intensity Threshold (0-1):')
        self._intThresText = wx.TextCtrl(self, wx.ID_ANY, size=(80, -1))
        self._intThresButton = wx.Button(self, wx.ID_ANY, 'Update Map',
                                  size=(-1, -1))
        self.Bind(wx.EVT_BUTTON, self._controller.selIntensityTh,
                  self._intThresButton)
        self._ctrlsSizer.Add(self._intThresLabel, pos = (4, 0), span = (1, 2))
        self._ctrlsSizer.Add(self._intThresText, pos = (5, 0), span = (1, 1))
        self._ctrlsSizer.Add(self._intThresButton, pos = (5, 1), span = (1, 1))

        # expTime
        self._expTimeLabel = wx.StaticText(self, wx.ID_ANY,
                                        'Select Exposure Time (years)')
        self._expTimeCB = wx.ComboBox(self, wx.ID_ANY, choices=[],
                                     style=wx.CB_READONLY, size=(80, -1))
        self.Bind(wx.EVT_COMBOBOX, self._controller.selTimeWindow,
                  self._expTimeCB)
        self._ctrlsSizer.Add(self._expTimeLabel, pos = (6, 0), span = (1, 2))
        self._ctrlsSizer.Add(self._expTimeCB, pos = (7, 0), span = (1, 1))

        self._sizer.Add(self._ctrlsBoxSizer)
        self.SetSizer(self._sizer)

    @property
    def ctrlsBoxTitle(self):
        """Get the current ctrlsBoxTitle."""
        return self._ctrlsBoxTitle

    @ctrlsBoxTitle.setter
    def ctrlsBoxTitle(self, value):
        self._ctrlsBoxTitle = value
        self._ctrlsBox.SetLabel(self._ctrlsBoxTitle)

class BymurWxMenu(wx.MenuBar):
    _menu_actions = {}

    def __init__(self, *args, **kwargs):
        self._controller = kwargs.pop('controller', None)
        super(BymurWxMenu, self).__init__(*args, **kwargs)

        # TODO: devo trovare il modo di memorizzarmi l'identificativo, altrimenti non posso modificare i controlli
        # TODO: quando il modello mi notifica un cambiamento

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
                                           title="Hazard")
        self._rightPanel = BymurWxRightPanel(parent=self,
                                             controller=self._controller)
        self.mainSizer.Add(self._leftPanel, 0, wx.EXPAND)
        self.mainSizer.Add(self._rightPanel, 1, wx.EXPAND)
        self.SetSizer(self.mainSizer)
        self.SetSize((950, 750))

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