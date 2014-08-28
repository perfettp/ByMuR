import bymurview
import bymurcore
import os


class BymurController():
    _exception_debug = True
    _basedir = os.getcwd()
    _dbDetails = {'db_host': '***REMOVED***',
                  'db_port': '3306',
                  'db_user': '***REMOVED***',
                  'db_password': '***REMOVED***',
                  'db_name': 'paoloDB'
    }

    _createDBDetails = {'db_host': '***REMOVED***',
                        'db_port': '3306',
                        'db_user': '***REMOVED***',
                        'db_password': '***REMOVED***',
                        # 'db_name': 'bymurDB',
                        'db_name': 'paoloDB',
                        'grid_path': os.path.join(_basedir, "data",
                                                  "naples-grid.txt"),
                        'lat_min': 4449200,
                        'lat_max': 4569800,
                        'lon_min': 375300,
                        'lon_max': 508500,
                        'map_path': os.path.join(_basedir, "data",
                                                 "naples.png"),
                        'haz_path': os.path.join(_basedir, "hazards"),
                        'haz_perc': "10:90:10"
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

    def connectDB(self):
        openDialog = bymurview.BymurDBLoadDlg(parent=None,
                                              title='Load ByMuR database',
                                              **self._dbDetails)

        dialogResult, _localdbDetails = openDialog.ShowModal()
        openDialog.Destroy()
        if dialogResult:
            self._dbDetails.update(_localdbDetails)
            self.wxframe.busymsg = "Connecting DB..."
            self.wxframe.busy = True
            try:
                self._core.connectDB(**self._dbDetails)
                self.wxframe.dbConnected = True
                txt = "\nConnection Succeded!\n"
                bymurview.bymurMessage(parent=self.wxframe,
                                       message=txt,
                                       kind="BYMUR_INFO",
                                       caption="Info")
            except Exception as e:
                bymurview.bymurMessage(parent=self.wxframe,
                                       message=str(e),
                                       debug=self._exception_debug,
                                       kind="BYMUR_ERROR",
                                       caption="Error")
            finally:
                self.wxframe.busy = False

    def loadDB(self):
        if (not self._core.db):
            openDialog = bymurview.BymurDBLoadDlg(parent=self.wxframe,
                                                  title='Load ByMuR database',
                                                  **self._dbDetails)

            dialogResult, _localdbDetails = openDialog.ShowModal()
            openDialog.Destroy()
            if dialogResult:
                self._dbDetails.update(_localdbDetails)
                try:
                    self.wxframe.busymsg = "Loading DB..."
                    self.wxframe.busy = True
                    self._core.connectDB(**self._dbDetails)
                    self.initAll()
                    self.wxframe.dbLoaded = True
                except Exception as e:
                    bymurview.bymurMessage(parent=self.wxframe,
                                           debug=self._exception_debug,
                                           message=str(e),
                                           kind="BYMUR_ERROR",
                                           caption="Error")
                finally:
                    self.wxframe.busy = False
        else:
            try:
                self.wxframe.busymsg = "Loading DB..."
                self.wxframe.busy = True
                self.initAll()
                self.wxframe.dbLoaded = True
            except Exception as e:
                bymurview.bymurMessage(parent=self.wxframe,
                                       debug=self._exception_debug,
                                       message=str(e),
                                       kind="BYMUR_ERROR",
                                       caption="Error")
            finally:
                self.wxframe.busy = False


    def createDB(self):
        if self._core.db:
            msg = "Close connected database?"
            confirmation = bymurview.bymurMessage(parent=self.wxframe,
                                             message=msg,
                                             kind="BYMUR_CONFIRM",
                                             caption="Please confirm this action")
            if confirmation:
                self._core.closeDB()
            else:
                return
        openDialog = bymurview.BymurDBCreateDlg(parent=None,
                                                title='Create ByMuR database',
                                                **self._createDBDetails)

        dialogResult, _localCreateDBDetails = openDialog.ShowModal()
        openDialog.Destroy()
        if dialogResult:
            self._createDBDetails.update(_localCreateDBDetails)
            self.wxframe.busymsg = "Creating DB..."
            self.wxframe.busy = True
            try:
                self._core.createDB(**self._createDBDetails)
            except Exception as e:
                bymurview.bymurMessage(parent=self.wxframe,
                                       message=str(e),
                                       debug=self._exception_debug,
                                       kind="BYMUR_ERROR",
                                       caption="Error")

            finally:
                self.wxframe.busy = False

                # self.sb.SetStatusText("DPC-V1-DB Database successfully created")

    def initAll(self):
        """
        :rtype : None
        """
        self.wxframe.refresh()
        data = self._core.getHazMapData()
        # self.wxframe.leftPanel.updateView(**data)
        self.wxframe.updateView(**data)

    def updateCurves(self, **kwargs):
        print "update curves"
        self.wxframe.rightPanel.curvesPanel.updateView(**self._core.data)

    def quit(self):
        print "Close"
        self._core.closeDB()
        self.wxframe.Close()


    def addDBData(self):
        print "addDBData"

    def dropDBTables(self):
        print "dropDBTables"
        msg = "Are you really sure you want to delete all tables in the " \
             "database?"
        confirmation = bymurview.bymurMessage(parent=self.wxframe,
                                             message=msg,
                                             kind="BYMUR_CONFIRM",
                                             caption="Please confirm this action")
        if confirmation:
            try:
                self.wxframe.busymsg = "Dropping tables..."
                self.wxframe.busy = True
                self._core.dropDBTables()
                txt = "Tables deleted"
                bymurview.bymurMessage(parent=self.wxframe,
                                       message=txt,
                                       kind="BYMUR_INFO",
                                       caption="Info")
            except Exception as e:
                bymurview.bymurMessage(parent=self.wxframe,
                                       message=str(e),
                                       debug=self._exception_debug,
                                       kind="BYMUR_ERROR",
                                       caption="Error")
            finally:
                self.wxframe.busy = False

    def exportASCII(self):
        print "exportASCII"
        self.wxframe.saveFile(self._basedir, self._core.exportRawPoints)

    def showPoints(self):
        print "showPoints"

    def openEnsemble(self):
        print "openEnsemble"
        ensembleDialog = bymurview.BymurEnsembleDlg(parent=self.wxframe,
                                                title='Define ensemble hazard',
                                                data=self._core.data)
        dialogResult = -1
        while dialogResult < 0:
            dialogResult, _localEnsembleDetails = ensembleDialog.ShowModal()
        ensembleDialog.Destroy()
        if dialogResult:
            self.wxframe.busymsg = "Creating ensemble hazard..."
            self.wxframe.busy = True
            try:
                #self._core.defEnsembleHaz(**_localEnsembleDetails)
                bymurview.bymurMessage(parent=self.wxframe,
                                       message="This is function is not "
                                               "implemented yet",
                                       kind="BYMUR_INFO",
                                       caption="Ensemble hazard definition")
                self.wxframe.leftPanel.updateView(**self._core.data)
            except Exception as e:
                bymurview.bymurMessage(parent=self.wxframe,
                                       message=str(e),
                                       debug=self._exception_debug,
                                       kind="BYMUR_ERROR",
                                       caption="Ensemble hazard definition")

            finally:
                self.wxframe.busy = False


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