import bymurview
import bymurcore


class BymurController():
    _dbDetails = {'dbHost': '***REMOVED***',
                  'dbPort': '3306',
                  'dbUser': 'bymurUser',
                  'dbPassword': 'bymurPwd',
                  'dbName': 'bymurDB'
    }

    def __init__(self, *args, **kwargs):
        self._wxframe = kwargs.pop('wxframe', None)
        try:
            self._core = kwargs.pop('core')
        except Exception as e:
            raise

    @property
    def wxframe(self):
        return self._wxframe

    @wxframe.setter
    def wxframe(self, value):
        self._wxframe = value

    def loadDB(self):
        openDialog = bymurview.BymurDBDialog(parent=None,
                                             title='Load ByMuR database',
                                             **self._dbDetails)

        dialogResult, self._dbDetails = openDialog.ShowModal()
        openDialog.Destroy()
        if dialogResult:
            try:
                self._core.connectDB(**self._dbDetails)
                # txt = "\nConnection Succeded!\n"
                # bymurview.bymurMessage(parent=None,
                # message=txt,
                # kind="BYMUR_INFO",
                # caption="Info")
            except Exception as e:
                bymurview.bymurMessage(parent=None,
                                       message=str(e),
                                       kind="BYMUR_ERROR",
                                       caption="Error")

        self.initAll()

    def initAll(self):
        """
        :rtype : None
        """
        data = self._core.getHazMapData()
        # self.wxframe.leftPanel.updateView(**data)
        self.wxframe.updateView(**data)

    def updateCurves(self, **kwargs):
        print "update curves"
        self.wxframe.rightPanel.curvesPanel.updateView(**self._core.data)

    def remoteDB(self):
        print "Remote"

    def quit(self):
        print "Close"
        self._core.closeDB()
        self.wxframe.Close()

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

    def selHazard(self, event):
        print "selHazard"
        self._core.changeHazardModel(event.GetSelection())
        self.wxframe.updateView(**self._core.data)

    def updateParameters(self, event):
        print "updateModel"
        print "wxframe"
        print self.wxframe
        self._core.updateModel(self.wxframe.ctrlsValues)
        self.wxframe.updateView(**self._core.data)

    # def selReturnPeriod(self, event):
    #     print "selReturnPeriod"
    #     print event.GetString()
    #     print event.GetClientData()
    #     print event
    #     self._core.changeReturnPeriod(event.GetString())
    #     self.wxframe.updateView(**self._core.data)
    #
    # def selIntensityTh(self, event):
    #     print "selIntensityTh"
    #     print event
    #     self._core.changeIntensityTh(event.GetString())
    #     self.wxframe.updateView(**self._core.data)
    #
    # def selTimeWindow(self, event):
    #     print "selTimeWindow"

    def nbTabChanged(self, event):
        print "nbTabChanged"
        self.wxframe.rightPanel.curvesPanel.updateView(**self._core.data)

    def onMapClick(self, event):
        if (event.inaxes != self.wxframe.rightPanel.mapPanel.map.ax1):
            print "Sono fuori dagli assi? "
        else:
            if self._core.setPoint(event.xdata, event.ydata):
                self.updateCurves()
            else:
                print "Problem setting point"



if __name__ == "__main__":
    core = bymurcore.BymurCore()
    control = BymurController(core=core)
    app = bymurview.BymurWxApp(redirect=False,
                               controller=control)
    app.MainLoop()