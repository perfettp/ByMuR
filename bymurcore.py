import os
import dbFunctions as db
import globalFunctions as gf
import getGMapsImg as gmaps
import scientLibs
import numpy as np # ma lo uso solo per sqrt?
import math


class BymurCore():
    _conf = { 'haz_mod':0,                  # selected hazard phenomenon
              'ret_per':4975,               # selected Return Period
              'int_thres': 3.0,             # selected intensity threshold
              'exp_time': 0,                # selected time window
              # Qui sotto non so perche' siano definite queste costanti
              'limits':[375.300, 508.500, 4449.200, 4569.800],
              'perc': range(1, 100),
              'pt_sel': 0
    }

    _data = {}

    def __init__(self):
        self._db_details=None
        pass

    def connectDB(self, **dbDetails):
        self._db_details=dbDetails
        try:
            self._db = db.BymurDB(**self._db_details)
        except:
            raise

    def closeDB(self):
        try:
            self._db.closeDB()
        except:
            pass

    def getHazMapData(self):
        data_tmp ={}
        table_rows=self._db.dbReadTable("spatial_data1")
        data_tmp['npts'] = len(table_rows)
        data_tmp['id_area'] = [int(table_rows[i][1])
                           for i in range(data_tmp['npts'])]
        data_tmp['lon'] = [float(table_rows[i][2]) / 1000
                       for i in range(data_tmp['npts'])]
        data_tmp['lat'] = [float(table_rows[i][3]) / 1000
                       for i in range(data_tmp['npts'])]
        data_tmp['nareas'] = len(data_tmp['id_area'])

        table_rows=self._db.dbReadTable("hazard_phenomena")
        data_tmp['nhaz'] = len(table_rows)
        data_tmp['hz_name']= [table_rows[i][4] for i in range(data_tmp['nhaz'])]
        data_tmp['model'] = [table_rows[i][5] for i in range(data_tmp['nhaz'])]
        data_tmp['imt'] = [table_rows[i][6] for i in range(data_tmp['nhaz'])]
        data_tmp['iml'] = [[float(j) for j in table_rows[i][7].split()]
                       for i in range(data_tmp['nhaz'])]

        niml = max([len(data_tmp['iml'][i]) for i in range(data_tmp['nhaz'])])

        data_tmp['dtime'] = []
        for k in range(data_tmp['nhaz']):
            hazmodtb = "hazard" + str(k + 1)
            tmp = self._db.dbSelectDtime(hazmodtb)
            dtlist = [str(tmp[i][0]) for i in range(len(tmp))]
            data_tmp['dtime'].append(dtlist)
        print "dtime = ", data_tmp['dtime']
        self._nt = max([len(data_tmp['dtime'][i])
                        for i in range(len(data_tmp['dtime']))])

        for k in range(data_tmp['nhaz']):
            if (len(data_tmp['iml'][k]) < niml):
                for i in range(niml - len(data_tmp['iml'][k])):
                    data_tmp['iml'][k].append(0)

        # self.hc = np.zeros((self.nhaz, self.nt, self.nperc+1, self.npts, niml))
        data_tmp['hc'] = [[[['0' for i in range(data_tmp['npts'])] for j in range(100)]
                    for k in range(self._nt)] for h in range(data_tmp['nhaz'])]

        print 'niml=', niml
        data_tmp['hc_perc'] = list()
        for k in range(data_tmp['nhaz']):
            data_tmp['hc_perc'].append(0)

        data_tmp['perc_flag'] = []
        for i in range(data_tmp['nhaz']):
            haznametb = "hazard" + str(i + 1)
            data_tmp['perc_flag'].append(self._db.dbAssignFlagPerc(haznametb))

        print("FLAGS PERCENTILES = {0}".format(data_tmp['perc_flag']))

        if (gf.verifyInternetConn()):
            srcdir = os.path.dirname(os.path.realpath(__file__))
            savepath = os.path.join(srcdir, "data", "naples_gmaps.png")
            utm_zone = "33N"
            data_tmp['imgpath'] = gmaps.getUrlGMaps(375300, 4449200,
                                             508500, 4569800,
                                             utm_zone, savepath)

        print data_tmp['dtime']
        data_tmp['th'] = scientLibs.prob_thr(self._conf['ret_per'],
                            data_tmp['dtime'][self._conf['haz_mod']]
                            [self._conf['exp_time']])
        data_tmp['hc'] = self._db.dbReadHC(self._conf['haz_mod'],
                                 self._conf['exp_time'],
                                 data_tmp['dtime'],
                                 data_tmp['hc'],
                                 data_tmp['hc_perc'])

        ret_value = {}
        ret_value.update(self._conf)
        ret_value.update(data_tmp)
        self.data = ret_value
        return ret_value

    def setPoint(self, xsel, ysel):
        lon1 = min(self.data['lon'])
        lon2 = max(self.data['lon'])
        lat1 = min(self.data['lat'])
        lat2 = max(self.data['lat'])
        if (xsel >= lon1 and xsel <= lon2 and ysel >= lat1 and ysel <= lat2):
            dist = np.sqrt((self.data['lon'] - xsel) ** 2 +
                           (self.data['lat'] - ysel) ** 2)
            self.data['pt_sel'] = np.argmin(dist)
            return True
        else:
            return False

    # def changeHazardModel(self, haz_mod):
    #     print "changeHazardModel"
    # 
    #     self._last_data['haz_mod'] = haz_mod
    #     self._last_data['dtime'] = []
    #     for k in range(self._last_data['nhaz']):
    #         hazmodtb = "hazard" + str(k + 1)
    #         tmp = self._db.dbSelectDtime(hazmodtb)
    #         dtlist = [str(tmp[i][0]) for i in range(len(tmp))]
    #         self._last_data['dtime'].append(dtlist)
    #     self._last_data['exp_time'] = 0
    # 
    #     ntry = int(math.floor(self._last_data['npts'] * 0.5))
    #     tmp2 = self._last_data['hc'][self._last_data['haz_mod']][
    #         self._last_data['exp_time']][0][ntry]
    #     # print tmp2, type(tmp2)
    #     tmp = sum([float(j) for j in tmp2.split()])
    #     if (tmp == 0):
    #         # busydlg = wx.BusyInfo("...Reading hazard from DB")
    #         # wx.Yield()
    #         #self._lasta_data['hc']self._db.dbReadHC(self._last_data['haz_mod'],
    #         self._db.dbReadHC(self._last_data['haz_mod'],
    #                           self._last_data['exp_time'],
    #                           self._last_data['dtime'],
    #                           self._last_data['hc'],
    #                           self._last_data['hc_perc'])
    #         # COSA VUOL DIRE CHE NON FACCIO NULLA?
    #         # Dovrei almeno assegnare dbReadHC a last_data['hc']??
    #         # busydlg = None
    # 
    # def changeReturnPeriod(self, returnPeriod):
    #     print returnPeriod
    #     self._last_data['ret_per'] = float(returnPeriod)
    #     self._last_data['th'] = scientLibs.prob_thr(self._last_data['ret_per'],
    #                         self._last_data['dtime'][self._last_data['haz_mod']]
    #                         [self._last_data['exp_time']])
    # 
    #     print "changeReturnPeriod"
    #    
    # def changeIntensityTh(self, intensityTh):
    #     self._last_data['int_thres']=float(intensityTh)
    #     print "changeIntensityTh"


    def updateModel(self, values):
        self.data['haz_mod'] = values['haz_mod']
        self.data['dtime'] = []
        for k in range(self.data['nhaz']):
            hazmodtb = "hazard" + str(k + 1)
            tmp = self._db.dbSelectDtime(hazmodtb)
            dtlist = [str(tmp[i][0]) for i in range(len(tmp))]
            self.data['dtime'].append(dtlist)
        self.data['exp_time'] = 0

        ntry = int(math.floor(self.data['npts'] * 0.5))
        tmp2 = self.data['hc'][self.data['haz_mod']][
            self.data['exp_time']][0][ntry]
        # print tmp2, type(tmp2)
        tmp = sum([float(j) for j in tmp2.split()])
        if (tmp == 0):
            # busydlg = wx.BusyInfo("...Reading hazard from DB")
            # wx.Yield()
            #self._lasta_data['hc']self._db.dbReadHC(self.data['haz_mod'],
            self._db.dbReadHC(self.data['haz_mod'],
                              self.data['exp_time'],
                              self.data['dtime'],
                              self.data['hc'],
                              self.data['hc_perc'])
            # COSA VUOL DIRE CHE NON FACCIO NULLA?
            # Dovrei almeno assegnare dbReadHC a last_data['hc']??
            # busydlg = None

        self.data['int_thres']=float(values['int_thres'])
        self.data['ret_per'] = float(values['ret_per'])

        self.data['th'] = scientLibs.prob_thr(self.data['ret_per'],
                            self.data['dtime'][self.data['haz_mod']]
                            [self.data['exp_time']])


    @property
    def data(self):
        return self._data