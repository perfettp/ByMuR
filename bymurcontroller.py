import os
import time
import globalFunctions as gf


class BymurController(object):
    _exception_debug = True
    _basedir = os.getcwd()
    _dbDetails = {'db_host': '***REMOVED***',
                  'db_port': '3306',
                  'db_user': '***REMOVED***',
                  'db_password': '***REMOVED***',
                  'db_name': 'bymurDB-dev'
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
        self._ctrls_data = {}
        self._wxframe = kwargs.pop('wxframe', None)
        self._wxapp = kwargs.pop('wxapp', None)
        try:
            self._core = kwargs.pop('core')
        except Exception as e:
            raise


    def connectDB(self):
        dialogResult = self._wxframe.showDlg("BymurDBLoadDlg",
                                             **self._dbDetails)

        if dialogResult:
            self._dbDetails.update(dialogResult)
            try:
                gf.SpawnThread(
                    self.wxframe,
                    gf.wxBYMUR_DB_CONNECTED,
                    self._core.connectDB,
                    self._dbDetails,
                    wait_msg="Connecting database...")

            except Exception as e:
                gf.showMessage(parent=self.wxframe,
                                       message=str(e),
                                       debug=self._exception_debug,
                                       kind="BYMUR_ERROR",
                                       caption="Error")

    def loadDB(self):
        if (not self._core.db):
            dialogResult = self._wxframe.showDlg("BymurDBLoadDlg",
                                             **self._dbDetails)
            if dialogResult:
                self._dbDetails.update(dialogResult)
                try:
                    gf.SpawnThread(self.wxframe,
                        gf.wxBYMUR_UPDATE_CTRLS,
                        self._core.connectAndFetch,
                        self._dbDetails,
                        callback=self.set_ctrls_data,
                        wait_msg="Loading database...")
                    self.wxframe.dbLoaded = True
                except Exception as e:
                    gf.showMessage(parent=self.wxframe,
                                           debug=self._exception_debug,
                                           message=str(e),
                                           kind="BYMUR_ERROR",
                                           caption="Error")
        else:
            try:
                gf.SpawnThread(
                    self.wxframe,
                    gf.wxBYMUR_UPDATE_CTRLS,
                    self._core.connectAndFetch, {},
                    callback=self.set_ctrls_data,
                    wait_msg="Loading database...")
                self.wxframe.dbLoaded = True
            except Exception as e:
                gf.showMessage(parent=self.wxframe,
                                       debug=self._exception_debug,
                                       message=str(e),
                                       kind="BYMUR_ERROR",
                                       caption="Error")

    def createDB(self):
        if self._core.db:
            msg = "Close connected database?"
            confirmation = gf.showMessage(parent=self.wxframe,
                                             message=msg,
                                             kind="BYMUR_CONFIRM",
                                             caption="Please confirm this action")
            if confirmation:
                self._core.closeDB()
            else:
                return
        dialogResult = self._wxframe.showDlg("BymurDBCreateDlg",
                                             **self._createDBDetails)
        if dialogResult:
            self._createDBDetails.update(dialogResult)
            self.wxframe.busymsg = "Creating DB..."
            self.wxframe.busy = True
            try:
                gf.SpawnThread(self.wxframe,
                               gf.wxBYMUR_UPDATE_DIALOG,
                                         self._core.createDB,
                                         self._createDBDetails,
                                         self.set_ctrls_data,
                                         wait_msg="Creating database...")
            except Exception as e:
                gf.showMessage(parent=self.wxframe,
                                       message=str(e),
                                       debug=self._exception_debug,
                                       kind="BYMUR_ERROR",
                                       caption="Error")




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
        confirmation = gf.showMessage(parent=self.wxframe,
                                             message=msg,
                                             kind="BYMUR_CONFIRM",
                                             caption="Please confirm this action")
        if confirmation:
            try:
                self.wxframe.busymsg = "Dropping tables..."
                self.wxframe.busy = True
                self._core.dropDBTables()
                txt = "Tables deleted"
                gf.showMessage(parent=self.wxframe,
                                       message=txt,
                                       kind="BYMUR_INFO",
                                       caption="Info")
            except Exception as e:
                gf.showMessage(parent=self.wxframe,
                                       message=str(e),
                                       debug=self._exception_debug,
                                       kind="BYMUR_ERROR",
                                       caption="Error")
            finally:
                self.wxframe.busy = False

    def exportASCII(self):
        self.wxframe.saveFile(self._basedir, self._core.exportRawPoints)

    def showPoints(self):
        print "showPoints"

    def openEnsemble(self):
        print "openEnsemble"
        dialogResult = self._wxframe.showDlg("BymurEnsembleDlg",
                                             **self._core.data)
        if dialogResult:
            self.wxframe.busymsg = "Creating ensemble hazard..."
            self.wxframe.busy = True
            try:
                #self._core.defEnsembleHaz(**dialogResult)
                gf.showMessage(parent=self.wxframe,
                                       message="This is function is not "
                                               "implemented yet",
                                       kind="BYMUR_INFO",
                                       caption="Ensemble hazard definition")
                self.wxframe.leftPanel.updateView(**self._core.data)
            except Exception as e:
                gf.showMessage(parent=self.wxframe,
                                       message=str(e),
                                       debug=self._exception_debug,
                                       kind="BYMUR_ERROR",
                                       caption="Ensemble hazard definition")

            finally:
                self.wxframe.busy = False


    def selHazard(self, event):
        self._core.changeHazardModel(event.GetSelection())
        self.wxframe.updateView(**self._core.data)

    def updateParameters(self, event):
        hazard_options = self.wxframe.hazard_options
        gf.SpawnThread(self.wxframe,
                       gf.wxBYMUR_UPDATE_ALL,
                       self._core.updateModel,
                       hazard_options,
                       callback=self.set_hazard_values,
                       wait_msg="Updating maps...")


    def nbTabChanged(self, event):
        self.wxframe.rightPanel.curvesPanel.updateView(**self._core.data)

    def onMapClick(self, event):
        if (event.inaxes != self.wxframe.rightPanel.mapPanel.map.ax1):
            print "Sono fuori asse? "
        else:
            if self._core.setPoint(event.xdata, event.ydata):
                self.updateCurves()
            else:
                print "Problem setting point"


    def set_ctrls_data(self):
        self.wxframe.ctrls_data = self._core.ctrls_data

    def set_hazard_values(self):
        self.wxframe.hazard_values = self._core.hazard_values

    def refresh(self):
        self._wxframe.refresh()

    # @property will not work properly beacause of the old-style class
    def SetWxFrame(self, frame):
        print "Setting frame"
        self._wxframe = frame

    def GetWxFrame(self):
        return self._wxframe

    @property
    def wxframe(self):
        return self._wxframe


    def sleep_fun(self):
        print "in sleep"
        time.sleep(10)
        print "out sleep"

    def get_ctrls_data(self):
        return self._core.ctrls_data