import wx

#TODO: move BymurController declaration to a different file
class BymurController():

    def loadDB(self):
        print "Local"

    def remoteDB(self):
        print "Remote"

    def quit(self):
        print "Close"

    def createDB(self):
        print "createDB"

    def addDBData(self):
        print "addDBData"

    def dropDBTables(self):
        print "dropDBTables"

    def exportASCII(self):
        print "exportASCII"

    def showPoints(self):
        print "showPoints"

    def openEnsembleFr(self):
        print "openEnsembleFr"

class BymurWxMenu(wx.MenuBar):

    _menu_actions = {}

    def __init__(self, controller):
        super(BymurWxMenu,self).__init__()
        self.controller = controller


        # TODO: devo trovare il modo di memorizzarmi l'identificativo, altrimenti non posso modificare i controlli
        # TODO: quando il modello mi notifica un cambiamento

        # File menu and items
        self.menuFile = wx.Menu()
        menuItemTmp = self.menuFile.Append(wx.ID_ANY, '&Load database')
        self._menu_actions[menuItemTmp.GetId()] = self.controller.loadDB
        menuItemTmp = self.menuFile.Append(wx.ID_ANY, '&Load remote ByMuR DB')
        self._menu_actions[menuItemTmp.GetId()] = self.controller.remoteDB
        self.menuFile.AppendSeparator()
        self.menuFile.Append(wx.ID_CLOSE, '&Quit')
        self._menu_actions[wx.ID_CLOSE] = self.controller.quit
        self.Append(self.menuFile, '&File')

        # Database menu and items
        self.menuDB = wx.Menu()
        menuItemTmp = self.menuDB.Append(wx.ID_ANY, '&Create DataBase (DB)')  # original method was openCreateDB
        self._menu_actions[menuItemTmp.GetId()] = self.controller.createDB
        menuItemTmp = self.menuDB.Append(wx.ID_ANY, '&Add Data to DB')
        self._menu_actions[menuItemTmp.GetId()] = self.controller.addDBData  # original method was openAddDB
        menuItemTmp.Enable(False)
        self.menuDB.AppendSeparator()
        menuItemTmp = self.menuDB.Append(wx.ID_ANY, '&Drop All DB Tables')
        self._menu_actions[menuItemTmp.GetId()] = self.controller.dropDBTables  # original method was dropAllTabs
        self.Append(self.menuDB, '&DataBase')

        # Plot menu and items
        self.menuPlot = wx.Menu()
        menuItemTmp = self.menuPlot.Append(wx.ID_ANY, '&Export Raster ASCII (GIS)')  # original method was exportAsciiGis
        self._menu_actions[menuItemTmp.GetId()] = self.controller.exportASCII
        menuItemTmp.Enable(False)
        menuItemTmp = self.menuPlot.Append(wx.ID_ANY, '&Show Points', kind = wx.ITEM_CHECK)  # original method was showPoints
        self._menu_actions[menuItemTmp.GetId()] = self.controller.showPoints
        menuItemTmp.Enable(False)
        self.Append(self.menuPlot, '&Map')

        # Analysis menu and items
        self.menuAnalysis = wx.Menu()
        menuItemTmp = self.menuAnalysis.Append(wx.ID_ANY, 'Create &Ensemble hazard')  # original method was openEnsembleFr
        self._menu_actions[menuItemTmp.GetId()] = self.controller.openEnsembleFr
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

    def __init__(self, parent, controller, model, title):

        super(BymurWxView, self).__init__(parent, title=title)

        fileMenuItemList = ()
        self.controller = controller
        self.menuBar = BymurWxMenu(self.controller)
        self.SetMenuBar(self.menuBar)
        self.Bind(wx.EVT_MENU, self.menuBar.doMenuAction)

class BymurWxApp(wx.App):

    def OnInit(self):
        frame = BymurWxView(None, BymurController(), None, "ByMuR - Refactoring")
        frame.Show(True)
        return True