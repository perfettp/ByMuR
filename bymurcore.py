import os
import dbFunctions as db
import globalFunctions as gf
import getGMapsImg as gmaps
import numpy as np # ma lo uso solo per sqrt?
import math
import random as rnd
import time


class BymurCore():
    _conf = { 'haz_mod':0,                  # selected hazard phenomenon
              'ret_per':4975,               # selected Return Period
              'int_thres': 3.0,             # selected intensity threshold
              'tw': 0,                # selected time window
              # Qui sotto non so perche' siano definite queste costanti
              'limits':[375.300, 508.500, 4449.200, 4569.800],
              'perc': range(1, 100),
              'pt_sel': 0
    }

    _data = {}
    _db = None

    def __init__(self):
        self._db_details=None
        pass

    def connectAndFetch(self, **dbDetails):
        self.connectDB(**dbDetails)
        data = self.getHazMapData()
        self._data.update(data)

    def fetchDataFromDB(self):
        data = self.getHazMapData()
        self._data.update(data)


    def connectDB(self, **dbDetails):
        self._db_details=dbDetails
        try:
            self._db = db.BymurDB(**self._db_details)
        except:
            raise

    # TODO: devo implementare un reset dei pannelli

    def closeDB(self):
        print "close"
        if self._db:
            try:
                self._db.close()
                self._db = None
            except:
                raise

    def dropDBTables(self):
        try:
            self._db.dropAllTables()
        except:
            raise


    def createDB(self, **createDBDetails):
        """
        Using data provided by the input form (see openCreateDB function)
        to create Tables in Bymur DB and populate them.

        NOTA: STO SUPPONENDO CHE L'UTENTE PREPARI UNA STRUTTURA AD ALBERO
        GERARCHICA DEI DATI :

        cartella_hazard/
            |--hazard1/
               |--model1/
                  |--time1/
                  |--time2/
                  |--time3/
               |--model2/
                  |--time1/
                  |--time2/
                  |--time3/
            |--hazard2/
            |--hazard3/

        NB: ogni hazard puo' avere una quantita' diversa di modelli (minimo uno),
            e invece suppongo che i tempi di ricorrenza (time1,time2...) siano
            gli stessi per ogni modello
        """


        # TODO: mancano MOLTI controlli sulla struttura delle directory
        # TODO: prima di creare un nuovo database devo chiudere quello
        # eventualmente aperto. Dopo averlo creato devo chiedere se voglio
        # caricarne i dati

        print "createDB"
        if self._db:
            raise Exception("You need to close the open db first!")
        createDBdata = {}
        createDBdata['limits'] = [createDBDetails['lon_min']/1000,
                                  createDBDetails['lon_max']/1000,
                                  createDBDetails['lat_min']/1000,
                                  createDBDetails['lat_max']/1000]
        createDBdata['hazards'] = os.listdir(createDBDetails['haz_path'])
        createDBdata['models'] = []
        createDBdata['dtime'] = []
        createDBdata['dtimefold'] = []

        for ind, haz in enumerate(createDBdata['hazards']):
            print 'hpath-->', createDBDetails['haz_path']
            print 'haz-->', haz
            createDBdata['models'].append(os.listdir(
                os.path.join(createDBDetails['haz_path'], haz)))
            for mod in createDBdata['models'][ind]:
                if (os.path.isdir(os.path.join(createDBDetails['haz_path'],
                                               haz, mod))
                    and (os.listdir(os.path.join(createDBDetails['haz_path'],
                                                 haz, mod)))):
                    tmp = os.listdir(os.path.join(createDBDetails['haz_path'],
                                                  haz, mod))
                    createDBdata['dtimefold'].append(tmp)

                    dtime_tmp = [str(tmp[i].replace("dt", "")).zfill(3)
                                 for i in range(len(tmp))]
                    createDBdata['dtime'].append(dtime_tmp)

        createDBdata['nt'] = max([len(createDBdata['dtime'][i])
                       for i in range(len(createDBdata['dtime']))])

        print createDBdata['hazards']
        print createDBdata['models']
        print createDBdata['dtime']

        percpattern = str(createDBDetails['haz_perc'])  # selected percentiles

        if (percpattern.find(":") != -1):
            ii, ff, dd = percpattern.split(":")
            createDBdata['perc'] = range(int(ii), int(ff) + int(dd), int(dd))
        elif (percpattern.find(",") != -1):
            val = percpattern.split(",")
            createDBdata['perc'] = [int(val[i]) for i in range(len(val))]
        else:
            raise Exception("Input in percentiles field is not correct")

        self._db = db.BymurDB(db_host=createDBDetails['db_host'],
                                 db_port=createDBDetails['db_port'],
                                 db_user=createDBDetails['db_user'],
                                 db_password=createDBDetails['db_password'],
                                 db_name=createDBDetails['db_name'])


        # comment the following two lines if DB tables exist and are populated
        self._db.createTables(createDBdata['models'])

        self._db.genInfoPop( createDBDetails['map_path'],
                                createDBdata['limits'])

        createDBdata['npts'] = self._db.spatDataPop(createDBDetails['grid_path'])

        self._db.hazTabPop(
            createDBdata['perc'],
            createDBdata['hazards'],
            createDBdata['models'],
            createDBdata['dtime'],
            createDBDetails['haz_path'],
            createDBdata['npts'],
            createDBdata['dtimefold'])
        # TODO: add a dialog for successfull creation

    def getHazMapData(self):
        data_tmp ={}
        table_rows=self._db.readTable("spatial_data1")
        data_tmp['npts'] = len(table_rows)
        data_tmp['id_area'] = [int(table_rows[i][1])
                           for i in range(data_tmp['npts'])]
        data_tmp['lon'] = [float(table_rows[i][2]) / 1000
                       for i in range(data_tmp['npts'])]
        data_tmp['lat'] = [float(table_rows[i][3]) / 1000
                       for i in range(data_tmp['npts'])]
        data_tmp['nareas'] = len(data_tmp['id_area'])

        table_rows=self._db.readTable("hazard_phenomena")
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
            tmp = self._db.selecDtime(hazmodtb)
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
            data_tmp['perc_flag'].append(self._db.assignFlagPerc(haznametb))

        print("FLAGS PERCENTILES = {0}".format(data_tmp['perc_flag']))

        if (gf.verifyInternetConn()):
            srcdir = os.path.dirname(os.path.realpath(__file__))
            savepath = os.path.join(srcdir, "data", "naples_gmaps.png")
            utm_zone = "33N"
            data_tmp['imgpath'] = gmaps.getUrlGMaps(375300, 4449200,
                                             508500, 4569800,
                                             utm_zone, savepath)

        print data_tmp['dtime']
        data_tmp['th'] = prob_thr(self._conf['ret_per'],
                            data_tmp['dtime'][self._conf['haz_mod']]
                            [self._conf['tw']])
        data_tmp['hc'] = self._db.readHC(self._conf['haz_mod'],
                                 self._conf['tw'],
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

    def updateModel(self, **kwargs):
        self.data['haz_mod'] = kwargs.pop('haz_mod','')
        self.data['dtime'] = []
        for k in range(self.data['nhaz']):
            hazmodtb = "hazard" + str(k + 1)
            tmp = self._db.selecDtime(hazmodtb)
            dtlist = [str(tmp[i][0]) for i in range(len(tmp))]
            self.data['dtime'].append(dtlist)
        self.data['tw'] = 0

        ntry = int(math.floor(self.data['npts'] * 0.5))
        tmp2 = self.data['hc'][self.data['haz_mod']][
            self.data['tw']][0][ntry]
        # print tmp2, type(tmp2)
        tmp = sum([float(j) for j in tmp2.split()])
        if (tmp == 0):
            # busydlg = wx.BusyInfo("...Reading hazard from DB")
            # wx.Yield()
            #self._lasta_data['hc']self._db.dbReadHC(self.data['haz_mod'],
            self._db.readHC(self.data['haz_mod'],
                              self.data['tw'],
                              self.data['dtime'],
                              self.data['hc'],
                              self.data['hc_perc'])
            # COSA VUOL DIRE CHE NON FACCIO NULLA?
            # Dovrei almeno assegnare dbReadHC a last_data['hc']??
            # busydlg = None

        self.data['int_thres']=float(kwargs.pop('int_thres',0))
        self.data['ret_per'] = float(kwargs.pop('ret_per',0))

        self.data['th'] = prob_thr(self.data['ret_per'],
                            self.data['dtime'][self.data['haz_mod']]
                            [self.data['tw']])

    def exportRawPoints(self, haz_array):
        export_string = ''
        for i in range(self.data['npts']):
            export_string += "%f %f %f\n" %  (self.data['lon'][i] *
                                              1000, self.data['lat'][i]*1000,
                                              haz_array[i])
        return export_string


    def defEnsembleHaz(self, **_localEnsembleDetails):
        # TODO: this function is not correct at all!!
        haz_len = len(_localEnsembleDetails['components'])
        for i in range(haz_len):
            ntry = int(math.floor(self.data['npts'] * 0.5))
            tmp2 = self.data['hc'][_localEnsembleDetails['components'][i][
                'index']] [self.data['dtime'].index(_localEnsembleDetails[
                'dtime'])][0][
                ntry]
            tmp = sum([float(j) for j in tmp2.split()])
            if (tmp == 0):
                # busydlg = wx.BusyInfo("...Reading hazard from DB")
                # TODO: Perche' dovrei invocare questa funzione
                # Non salvo il risultato e non sembra avere side-effect?!?!
                self._db.readHC(_localEnsembleDetails['components'][i][
                                     'index'],
                            _localEnsembleDetails['dtime'],
                            self.data['dtime'],
                            self.data['hc'],
                            self.data['hc_perc'])

        # self.sb.SetStatusText("... generating ensemble model")
        percsel = range(10,100,10)
        tmp = ensemble(self.data['hc'],
                                  self.data['hc_perc'],
                                  self.data['tw'],
                                  self.data['hazards'],
                                  self.data['dtime'],
                                  self.data['selected'],
                                  self.data['weights'],
                                  self.data['twsel'],
                                  percsel,
                                  self.data['perc_flag'])

        nt = max([len(self.data['dtime'][i])
                  for i in range(len(self.data['dtime']))])
        hccomb = [[['0' for i in range(self.data['npts'])] for j in range(100)]
                  for k in range(nt)]
        for i in range(self.data['npts']):
            for j in range(100):
                hccomb[0][j][i] = ' '.join(map(str, tmp[0, j, i][:]))

        # self.sb.SetStatusText("... updating DB")
        ntw = 1
        self.data['nhaz'] += 1
        tmpid = self.data['nhaz']
        tmpname = _localEnsembleDetails['components'][0]['name']
        tmpmodel = "EN:"
        for i in range(haz_len):
            tmpmodel += _localEnsembleDetails['components'][i]['name'] + "("
            tmpmodel += str(_localEnsembleDetails['components'][i]['weight'])
            tmpmodel += ");" # ID in DB

        tmpmodel += "_T:"
        tmpmodel += str(_localEnsembleDetails['dtime']) + ";"
        tmpimt = self.data['imt'][_localEnsembleDetails['components'][i][
            'index']]
        tmp = self.data['iml'][_localEnsembleDetails['components'][i][
            'index']]
        tmpiml = ' '.join(map(str, tmp[:]))


        self._db.insertHazard(tmpid, tmpname, tmpmodel, tmpimt, tmpiml)

        # update variables
        tmp = self._db.readTable("hazard_phenomena")
        self.data['nhaz'] = len(tmp)
        self.data['hz_name'] = [tmp[i][4] for i in range(self.data['nhaz'])]
        self.data['model'] = [tmp[i][5] for i in range(self.data['nhaz'])]
        self.data['imt'] = [tmp[i][6] for i in range(self.data['nhaz'])]
        self.data['iml'] = [[float(j) for j in tmp[i][7].split()]
                    for i in range(self.data['nhaz'])]

        hctmp = self.data['hc']
        niml = len(self.data['iml'][_localEnsembleDetails['components'][i]['index']])
        # self.hc = np.zeros((self.nhaz, self.nt, self.nperc+1, self.npts, niml))
        self.data['hc'] = [[[['0' for i in range(self.data['npts'])]
                             for j in range(100)]
                    for k in range(self.nt)] for h in range(self.data['nhaz'])]
        for ihz in range(self.data['nhaz'] - 1):
            self.data['hc'][ihz] = hctmp[ihz]
        self.data['hc'][-1][0] = hccomb[0]
        # print self.hc.shape

        # print 'prima-->',self.hc_perc
        # self.hc_perc.insert(self.nhaz,np.asarray(self.percsel))
        self.data['hc_perc'].append(np.asarray(self.data['percsel']))
        # print 'dopo-->',self.hc_perc

        tbname = "hazard" + str(self.data['nhaz'])
        self._db.createHazardTable(tbname)

        idc = 0
        dtimetmp = self.data['dtime']
        nperc = len(self.data['hc'][0][0]) - 1
        npts = len(self.data['hc'][0][0][0])

        for iii in range(ntw):

            # dt = self.data['dtime'][self.selected[0]][self.twsel[0]]
            dt = _localEnsembleDetails['dtime']
            print 'dT= ', dt, ' yr'
            for i in range(npts):
                idc = idc + 1
                # TODO: make a uniq query!
                self._db.insertHazPoint(tbname, idc, tmpid, i + 1,
                                        "Average", dt, hccomb[0][0][i])
            for p in range(len(self.data['percsel'])):
                pp = str(self.data['percsel'][p])
                print('percsel[p]', self.data['percsel'][p])
                for i in range(npts):
                    idc = idc + 1
                    self._db.insertHazPoint(tbname, idc, tmpid, i + 1,
                                        "Perc"+pp, dt,
                                        hccomb[0][self.data['percsel'][p]][i])

        print 'DB populated!!'
        self.data['perc_flag'].append(self._db.assignFlagPerc(tbname))
        print("UPDATE FLAGS PERCENTILES = {0}".format(self.self.data[
            'perc_flag']))

        #self.sb.SetStatusText("... ensemble model evaluated")
        print 'Task completed!!'
        print '------------------------------'


        # update DB, table hazard#

    def GetData(self):
        return self.data

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    @property
    def db(self):
        return self._db


def ensemble(*kargs):
    """
    It opens a pop-up dialog showing a text message.
    """
    hc = kargs[0]             # hazard curves
    hc_perc = kargs[1]        # percentiles for hazard curves
    tw = kargs[2]             # selected time window
    hazard = kargs[3]         # hazard phenomena
    dtime = kargs[4]          # time windows
    haz_selected = kargs[5]   # selected hazards to be combined
    haz_weights = kargs[6]    # selected weights for the hazards to be combined
    twsel = kargs[7]          # time windows selected
    percsel = kargs[8]        # percentiles to be computed
    # for each hazard, it is =1 if it has percentiles, =0 otherwise
    perc_flag = kargs[9]



    print "----ensemble()--------------"
# hc[hsel][tw][perc][pt_sel][:]
    sel_first = haz_selected[0]
#  ntw = len(hc[sel_first])
    ntw = 1

    npts = len(hc[sel_first][0][0])
    tmp = hc[sel_first][0][0][0]
    curve = [float(j) for j in tmp.split()]
    nimls = len(curve)
    print "Number of time windows: " + str(ntw)
    print "Number of pts: " + str(npts)

    nhaz = len(haz_selected)
    weights = np.array(haz_weights)
    weights = weights / sum(haz_weights)
    print "Num. of models: " + str(nhaz)
    print "Weights: " + str(weights[:])

    check_uncert = 1
    for jhaz in range(nhaz):
        ihc = haz_selected[jhaz]
        check_uncert = check_uncert * perc_flag[ihc]
    print "Check epistemic uncertainties: " + str(check_uncert)

    if check_uncert == 1:
        nrun = 100
        run_fl = weights * nrun

        nrun_haz = 0
        for jhaz in range(nhaz):
            nrun_haz = nrun_haz + int(run_fl[jhaz])
        nrun_eff = nrun_haz

        print 'Dim of hccomb_sample:', ntw, npts, nrun_eff, nimls
        hccomb_sample = np.zeros((ntw, npts, nrun_eff, nimls))
        isample = -1
        for jhaz in range(nhaz):
            ihc = haz_selected[jhaz]
            print "Hazard " + str(jhaz + 1) + "(ind:" + str(ihc) + ")"
            itw = twsel[jhaz]

            nrun_haz = int(run_fl[jhaz])
            print "--> n run: " + str(nrun_haz)
            hazperc = hc_perc[ihc]
#     print "--> hazperc: " + str(hazperc)
            nperc = len(hazperc)
            print "--> n perc: " + str(nperc) + "(val:" + str(hazperc) + ")"
            for irun in range(nrun_haz):
                xrnd = rnd.uniform(0., 100.)
#        print xrnd
                ipercsel = nperc - 1
                for j in range(nperc):
                    if (xrnd < float(hazperc[j])):
                        ipercsel = j
                        break
#        print "Perc. sel: " + str(ipercsel)
                isample = isample + 1
#        print hazperc[ipercsel]
                for ipt in range(npts):
                    tmp = hc[ihc][itw][hazperc[ipercsel]][ipt]
                    curve = [float(j) for j in tmp.split()]
                    hccomb_sample[0][ipt][isample] = curve
        if (isample + 1 != nrun_eff):
            print "!!!!!!!Errore nel calcolo run totali" + str(isample + 1) + "<->" + str(nrun_eff)
        print "N run totali: " + str(nrun_eff)

        npercsel = len(percsel)
        # hccomb = np.zeros((ntw, nperc+1, npts, nimls))
        hccomb = np.zeros((ntw, 100, npts, nimls))
        ntot = ntw * npts
        for iii in range(ntw):
            # itw = twsel[iii]
            itw = 1
            for ipt in range(npts):
                msg = str(ipt + 1 + iii * ntw) + "/" + str(ntot)
#      print msg
                for iptensity in range(nimls):
                    values = hccomb_sample[0][ipt][0:nrun_eff + 1, iptensity]
                    value = np.mean(values)
                    hccomb[0][0][ipt][iptensity] = value
                    for iperc in range(npercsel):
                        values.sort()
                        pval = percsel[iperc] / 100.
                        value = percentile(values, pval)
                        hccomb[0][percsel[iperc]][ipt][iptensity] = value
        print "Sample created!!"

    else:
        print "For at least one model, ep. uncertainty is NOT estimated"
#    @@@ DA VERIFICARE!!! @@@
        hccomb = np.zeros((ntw, 100, npts, nimls))
        for jhaz in range(nhaz):
            ihc = haz_selected[jhaz]
            print "Hazard " + str(jhaz + 1) + "(ind:" + str(ihc) + ")"
            itw = twsel[jhaz]
            for ipt in range(npts):
                tmp = hc[ihc][itw][0][ipt]
                curve = [float(j) for j in tmp.split()]
                hccomb[0][0][ipt] = hccomb[0][0][ipt] + weights[jhaz] * curve
    return hccomb


def percentile(N, percent, key=lambda x: x):
    """
    Find the percentile of a list of values.

    @parameter N - is a list of values. Note N MUST BE already sorted.
    @parameter percent - a float value from 0.0 to 1.0.
    @parameter key - optional key function to compute value from each element of N.

    @return - the percentile of the values
    """
    k = (len(N) - 1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return key(N[int(k)])
    d0 = key(N[int(f)]) * (c - k)
    d1 = key(N[int(c)]) * (k - f)
    return d0 + d1

def prob_thr(RP, dt):
    dtmp = float(dt)
    dRP = float(RP)
    th = 1 - math.exp(-dtmp / dRP)
    print 'Prob. threshold= ', th
    return th
