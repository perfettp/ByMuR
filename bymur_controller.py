import os
import time
import bymur_functions as bf


class BymurController(object):
    _exception_debug = False
    _basedir = os.getcwd()
    _dbDetails = {'db_host': '***REMOVED***',
                  'db_port': '3306',
                  'db_user': '***REMOVED***',
                  'db_password': '***REMOVED***',
                  'db_name': 'bymurDB-dev-utm'
    }

    _addDBDataDetails = {
        'haz_path': os.path.join(_basedir, "hazards"),
        'haz_perc': "10:90:10",
        'grid_path': os.path.join(_basedir, "data", "naples-grid.txt"),
    }

    _createDBDetails = {'db_host': '***REMOVED***',
                        'db_port': '3306',
                        'db_user': '***REMOVED***',
                        'db_password': '***REMOVED***',
                        # 'db_name': 'bymurDB',
                        'db_name': 'paoloDB',
                        'grid_path': os.path.join(_basedir, "data",
                                                  "naples-grid.txt"),
                        'northing_min': 4449200,
                        'northing_max': 4569800,
                        'easting_min': 375300,
                        'easting_max': 508500,
                        'map_path': os.path.join(_basedir, "data",
                                                 "naples_gmaps.png"),
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
        self._hazard_options = {}

    def loadDB(self):
        if (not self._core.db):
            dialogResult = self._wxframe.showDlg("BymurDBLoadDlg",
                                             **self._dbDetails)
            if dialogResult:
                self._dbDetails.update(dialogResult)
                try:
                    bf.SpawnThread(self.wxframe,
                        bf.wxBYMUR_DB_CONNECTED,
                        self._core.connectAndFetch,
                        self._dbDetails,
                        callback=self.set_ctrls_data,
                        wait_msg="Loading database...")
                except Exception as e:
                    bf.showMessage(parent=self.wxframe,
                                           debug=self._exception_debug,
                                           message=str(e),
                                           kind="BYMUR_ERROR",
                                           caption="Error")
        else:
            try:
                bf.SpawnThread(
                    self.wxframe,
                    bf.wxBYMUR_UPDATE_CTRLS,
                    self._core.connectAndFetch, {},
                    callback=self.set_ctrls_data,
                    wait_msg="Loading database...")
                self.wxframe.dbLoaded = True
            except Exception as e:
                bf.showMessage(parent=self.wxframe,
                                       debug=self._exception_debug,
                                       message=str(e),
                                       kind="BYMUR_ERROR",
                                       caption="Error")

    def createDB(self):
        if self._core.db:
            msg = "Close connected database?"
            confirmation = bf.showMessage(parent=self.wxframe,
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
                bf.SpawnThread(self.wxframe,
                               bf.wxBYMUR_UPDATE_DIALOG,
                                         self._core.createDB,
                                         self._createDBDetails,
                                         self.set_ctrls_data,
                                         wait_msg="Creating database...")
            except Exception as e:
                bf.showMessage(parent=self.wxframe,
                                       message=str(e),
                                       debug=self._exception_debug,
                                       kind="BYMUR_ERROR",
                                       caption="Error")

    def quit(self):
        print "Close"
        self._core.closeDB()
        self.wxframe.Close()


    def addDBData(self):
        print "addDBData"
        dialogResult = self._wxframe.showDlg("BymurAddDBDataDlg",
                                                       **self._addDBDataDetails)
        if dialogResult:
            self._addDBDataDetails.update(dialogResult)
            try:
                bf.SpawnThread(self.wxframe,
                               bf.wxBYMUR_UPDATE_DIALOG,
                               self._core.addDBData,
                               self._addDBDataDetails,
                               self.set_ctrls_data,
                               wait_msg="Adding data to database...")
            except Exception as e:
                bf.showMessage(parent=self.wxframe,
                               message=str(e),
                               debug=self._exception_debug,
                               kind="BYMUR_ERROR",
                               caption="Error")


    def dropDBTables(self):
        print "dropDBTables"
        msg = "Are you really sure you want to delete all tables in the " \
             "database?"
        confirmation = bf.showMessage(parent=self.wxframe,
                                             message=msg,
                                             kind="BYMUR_CONFIRM",
                                             caption="Please confirm this action")
        if confirmation:
            try:
                self.wxframe.busymsg = "Dropping tables..."
                self.wxframe.busy = True
                self._core.dropDBTables()
                txt = "Tables deleted"
                bf.showMessage(parent=self.wxframe,
                                       message=txt,
                                       kind="BYMUR_INFO",
                                       caption="Info")
            except Exception as e:
                bf.showMessage(parent=self.wxframe,
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
                bf.showMessage(parent=self.wxframe,
                                       message="This is function is not "
                                               "implemented yet",
                                       kind="BYMUR_INFO",
                                       caption="Ensemble hazard definition")
                self.wxframe.leftPanel.updateView(**self._core.data)
            except Exception as e:
                bf.showMessage(parent=self.wxframe,
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
        try:
            self.hazard_options = self.wxframe.leftPanel.hazard_options
            bf.SpawnThread(self.wxframe,
                       bf.wxBYMUR_UPDATE_ALL,
                       self._core.updateModel,
                       self.hazard_options,
                       callback=self.update_hazard_data,
                       wait_msg="Updating maps...")
        except Exception as e:
            bf.showMessage(parent=self.wxframe,
                           debug=self._exception_debug,
                           message="Error setting hazard_options!\n" + str(e),
                           kind="BYMUR_ERROR",
                           caption="Error")



    def nbTabChanged(self, event):
        self.wxframe.rightPanel.curvesPanel.updateView(**self._core.data)

    def pick_point(self, index):
        if self._core.set_point_by_index(index):
            self.set_selected_point()
            self.set_selected_point_curves()
            bf.fire_event(self.wxframe, bf.wxBYMUR_UPDATE_POINT)


    def onPointSelect(self, easting, northing):
        if self._core.setPoint(easting, northing):
            self.set_selected_point()
            self.set_selected_point_curves()
            bf.fire_event(self.wxframe, bf.wxBYMUR_UPDATE_POINT)

    def update_hazard_data(self):
        self.set_hazard_options()
        self.set_hazard_description()
        self.set_hazard_metadata()
        self.set_hazard_values()
        self.set_grid_points()

    def set_ctrls_data(self):
        self.wxframe.ctrls_data = self._core.ctrls_data

    def set_hazard_options(self):
        self.wxframe.hazard_options = self._core.hazard_options

    def set_hazard_description(self):
        self.wxframe.hazard_description = self._core.hazard_description

    def set_hazard_metadata(self):
        self.wxframe.hazard_metadata = self._core.hazard_metadata
        
    def set_hazard_values(self):
        self.wxframe.hazard_values = self._core.hazard_values

    def set_grid_points(self):
        self.wxframe.grid_points = self._core.grid_points
        
    def set_selected_point(self):
        self.wxframe.selected_point = self._core.selected_point

    def set_selected_point_curves(self):
        self.wxframe.selected_point_curves = self._core.selected_point_curves

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

    @property
    def basedir(self):
        return self._basedir

    def sleep_fun(self):
        print "in sleep"
        time.sleep(10)
        print "out sleep"

    @property
    def hazard_options(self):
        return self._hazard_options

    @hazard_options.setter
    def hazard_options(self, data):
        print "Setting hazard_options data: %s" % data
        tmp = {}
        if (data['ret_per'] is None) or (data['int_thresh'] is None) or  \
                (data['hazard_name'] is None) or (data['exp_time'] is None):
            raise StandardError("Hazard options are not complete")
        tmp['hazard_name'] = data['hazard_name']
        tmp['ret_per'] = float(data['ret_per'])
        tmp['int_thresh'] = float(data['int_thresh'])
        tmp['exp_time'] = int(data['exp_time'])
        self._hazard_options = tmp