import bymurview
# import bymurcontroller


class BymurController():

    def __init__(self, *args, **kwargs):
        self._wxframe = kwargs.pop('wxframe', None)

    @property
    def wxframe(self):
        return self._wxframe

    @wxframe.setter
    def wxframe(self, value):
        self._wxframe = value

    def loadDB(self):
        openDialog=bymurview.BymurDBDialog(parent=None,
                                           title='Load ByMuR database')
        openDialog.ShowModal()
        print "Local"

    def remoteDB(self):
        print "Remote"

    def quit(self):
        print "Close"
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

    def selHazard(self, controlElement):
        print "selHazard"

    def selReturnPeriod(self,  controlElement):
        print "selReturnPeriod"

    def selIntensityTh(self, controlElement):
        print "selIntensityTh"

    def selTimeWindow(self,  controlElement):
        print "selTimeWindow"

    def nbTabChanged(self):
        print "bTabChanged"

    def onMapClick(self):
        print "onMapClick"



if __name__ == "__main__":
    control=BymurController()
    app = bymurview.BymurWxApp(redirect=False,
                               controller=control)
    app.MainLoop()