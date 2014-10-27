import bymur_functions as bf
import bymur_db as db
import numpy as np  # ma lo uso solo per sqrt?
import math
import random as rnd
import os

class HazardPoint(object):

    def __init__(self, core):
        self._core = core
        self._hazard = None
        self._index = None
        self._curves = None
        self._easting = None
        self._northing = None
        self._haz_value = None
        self._prob_value = None

    def update(self, hazard, index, hazard_threshold, intensity_treshold):
        self._hazard = hazard
        self._index = index
        self._easting = self._hazard.grid_points[self._index]['easting']
        self._northing = self._hazard.grid_points[self._index]['northing']
        self._curves = self._core.db.get_point_all_curves(
            self._hazard.phenomenon_id,
            self._hazard.hazard_id,
            self._hazard.grid_points[self._index]['id'])
        self._haz_value = self._core.get_haz_value(self._hazard.iml,
                                                   hazard_threshold,
                                                   [float(x) for x
                                                    in self._curves['mean'].split(',')])
        self._prob_value = self._core.get_prob_value(self._hazard.iml,
                                                     intensity_treshold,
                                                     [float(x) for x
                                                     in self._curves[
                                                         'mean'].split(',')])

    @property
    def easting(self):
        return self._easting

    @property
    def northing(self):
        return self._northing

    @property
    def index(self):
        return self._index

    @property
    def curves(self):
        return self._curves

    @property
    def haz_value(self):
        return self._haz_value

    @property
    def prob_value(self):
        return self._prob_value


class HazardModel(object):
    def __init__(self, data_provider, id=None, hazard_name=None, exp_time=None):
        self._db = data_provider
        if id is not None:
            hm = self._db.get_hazard_model_by_id(self._hazard_id)
        elif hazard_name is not None and exp_time is not None:
            hm = self._db.get_hazard_model_by_name_exptime(hazard_name,
                                                           exp_time)
        else:
            raise Exception("Bad initialization of HazardModel")

        self._hazard_id = hm['hazard_id']
        self._hazard_name = hm['hazard_name']
        self._phenomenon_id = hm['phenomenon_id']
        self._datagrid_id = hm['datagrid_id']
        self._exposure_time = float(hm['exposure_time'])
        self._iml = [float(l) for l in hm['iml'].split()]
        self._imt = hm['imt']
        self._date = hm['date']
        self.statistics = self._db.get_statistics_by_haz(self._hazard_id)
        self._grid_points = self._db.get_points_by_datagrid_id(self.datagrid_id)
        self._grid_limits = {'east_min': min([p['easting']
                                              for p in self._grid_points]),
                             'east_max': max([p['easting']
                                              for p in self._grid_points]),
                             'north_min': min([p['northing']
                                               for p in self._grid_points]),
                             'north_max': max([p['northing']
                                               for p in self._grid_points])}
        self._curves = {}
        # self._selected_point = None
        # self._selected_point_curves = None

    def curves_by_statistics(self, statistic_name='mean'):
        try:
            return self._curves[statistic_name]
        except KeyError:
            stat_id = self._db.get_statistic_by_value(statistic_name)
            self._curves[statistic_name] = self._db.get_curves(
                self.phenomenon_id,
                self.hazard_id,
                stat_id)
        return self._curves[statistic_name]

    # def select_point(self, xpoint, ypoint):
    #     xsel = np.float64(xpoint)
    #     ysel = np.float64(ypoint)
    #     if (self.grid_limits['east_min'] <= xsel <= self.grid_limits['east_max']
    #         and self.grid_limits['north_min'] <= ysel <=
    #             self.grid_limits['north_max']):
    #         distances = np.hypot(xsel-[p['easting'] for p in self.grid_points],
    #                              ysel-[p['northing'] for p in self.grid_points])
    #         self._selected_point = self.grid_points[distances.argmin()]
    #         self._selected_point_curves = self._db.get_point_all_curves(
    #             self.phenomenon_id,
    #             self.hazard_id,
    #             self._selected_point['id'])
    #         return True
    #     else:
    #         return False

    # def select_point_by_index(self, p_index):
    #     try:
    #         self._selected_point = self.grid_points[p_index]
    #         self._selected_point_curves = self._db.get_point_all_curves(
    #             self.phenomenon_id,
    #             self.hazard_id,
    #             self._selected_point['id'])
    #         return True
    #     except:
    #         print "Exception in select_point_by_index"
    #         return False

    @property
    def hazard_id(self):
        return self._hazard_id

    @property
    def hazard_name(self):
        return self._hazard_name

    @property
    def datagrid_id(self):
        return self._datagrid_id

    @property
    def phenomenon_id(self):
        return self._phenomenon_id

    @property
    def exposure_time(self):
        return self._exposure_time

    @property
    def iml(self):
        return self._iml

    @property
    def imt(self):
        return self._imt

    @property
    def date(self):
        return self._date

    @property
    def grid_points(self):
        return self._grid_points

    @property
    def grid_limits(self):
        return self._grid_limits

    @property
    def curves(self):
        return self._curves

    # @property
    # def selected_point(self):
    #     return self._selected_point
    #
    # @property
    # def selected_point_curves(self):
    #     return self._selected_point_curves


class BymurCore(object):
    # Default values regardless of hazard model
    _ctrls_defaut = {
        'SEISMIC': {
            'ret_per': 475,
            'int_thresh': 0.1
        },
        'TSUNAMIC': {
            'ret_per': 475,
            'int_thresh': 0.1
        },
        'VOLCANIC': {
            'ret_per': 475,
            'int_thresh': 0.1
        },
        'basedir': os.getcwd(),
        # TODO: da eliminare quando scarichero' le mappe
    }

    def __init__(self):
        self._db = None
        self._db_details = None
        self._ctrls_data = {}
        self._grid_points = []
        self._hazard_options = {}
        self._hazard = None
        self._hazard_data = None

        self._hazard_curves = None

        self._selected_point = HazardPoint(self)
        # self._selected_point_curves = None

    def connectAndFetch(self, **dbDetails):
        if (not self._db) and dbDetails:
            self.connectDB(**dbDetails)
        self._ctrls_data = self.get_controls_data()

    def connectDB(self, **dbDetails):
        self._db_details = dbDetails
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
            self._db.drop_tables()
        except:
            raise


    def createDB(self, **createDBDetails):
        """

        """

        # TODO: prima di creare un nuovo database devo chiudere quello
        # eventualmente aperto. Dopo averlo creato devo chiedere se voglio
        # caricarne i dati

        print "createDB"
        if self._db:
            raise Exception("You need to close the open db first!")

        self._db = db.BymurDB(db_host=createDBDetails['db_host'],
                              db_port=createDBDetails['db_port'],
                              db_user=createDBDetails['db_user'],
                              db_password=createDBDetails['db_password'],
                              db_name=createDBDetails['db_name'])

        self.db.create()

        self.db.add_data(createDBDetails['haz_path'],
                         createDBDetails['haz_perc'],
                         createDBDetails['grid_path'])

        # TODO: add a dialog for successfull creation

    def addDBData(self, **addDBData):
        self.db.add_data(addDBData['datagrid_name'],
                         addDBData['haz_files'],
                         addDBData['phenomenon'])
        self._ctrls_data = self.get_controls_data()

    def loadGrid(self, **gridData):
        print "core loadGrid: %s" % gridData
        filepath = gridData.pop('filepath', None)
        return self.db.load_grid(filepath)

    def get_controls_data(self):
        ret = {}
        hazard_models = self.db.get_hazard_models_list()
        # [{'id_phenomenon', 'phenomenon_name', 'haz_id', 'haz_name'}]
        for ind, hazard in enumerate(hazard_models):
            haz_tmp = hazard
            if haz_tmp['phenomenon_name'] == 'VOLCANIC':
                haz_tmp['volcano'] = self.db.get_volcanos_list(
                    haz_tmp['hazard_id'])
            else:
                haz_tmp['volcano'] = None
            hazard_models[ind] = haz_tmp

        ret['hazard_models'] = hazard_models
        ret['phenomena'] = self.db.get_phenomena_list()
        print "hazard_models %s:" % ret['hazard_models']
        print "phenomena %s " % ret['phenomena']
        return ret


    def set_point_by_index(self, index):
        try:
            self.selected_point.update(self.hazard, index,
                                       self.hazard_options['hazard_threshold'],
                                       self.hazard_options['int_thresh'])
            # self._selected_point = self.grid_points[index]
            # self._selected_point_curves = self._db.get_point_all_curves(
            #     self.hazard.phenomenon_id,
            #     self.hazard.hazard_id,
            #     self._selected_point['id'])
            return True
        except Exception as e:
            print "Exception in select_point_by_index: %s" % str(e)
            return False
        # return self._hazard.select_point_by_index(index)

    def setPoint(self, xpoint, ypoint):
        # return self._hazard.select_point(xpar, ypar)
        xsel = np.float64(xpoint)
        ysel = np.float64(ypoint)
        if (self.hazard.grid_limits['east_min'] <= xsel <=
                self.hazard.grid_limits['east_max']
            and self.hazard.grid_limits['north_min'] <= ysel <=
                self.hazard.grid_limits['north_max']):
            distances = np.hypot(xsel-[p['easting'] for p in self.grid_points],
                                 ysel-[p['northing'] for p in self.grid_points])
            self.selected_point.update(self.hazard,
                                       distances.argmin(),
                                       self.hazard_options['hazard_threshold'],
                                       self.hazard_options['int_thresh'])

            # self._selected_point = self.grid_points[distances.argmin()]
            # self._selected_point_curves = self._db.get_point_all_curves(
            #     self.hazard.phenomenon_id,
            #     self.hazard.hazard_id,
            #     self._selected_point['id'])
            return True
        else:
            return False

    def get_haz_value(self, int_thresh_list, hazard_threshold, curve):
        y_th = hazard_threshold
        y = curve
        x = int_thresh_list
        x_1 = x_2 = float('NaN')
        for i in range(len(curve)):
            if y[i] < y_th:
                if i > 0:
                    y_1 = y[i - 1]
                    x_1 = x[i - 1]
                else:
                    y_1 = 1
                    x_1 = 0
                y_2 = y[i]
                x_2 = x[i]
                try:
                    x_th = x_1 + (x_2 - x_1) * (y_th - y_1) / (y_2 - y_1)
                except:
                    x_th = float('NaN')
                finally:
                    return x_th
        return x[len(x) - 1]

    def get_prob_value(self, int_thresh_list, intensity_threshold, curve):
        x_th = intensity_threshold
        y = curve
        x = int_thresh_list
        y_1 = y_2 = float('NaN')
        for i in range(len(x)):
            if x[i] > x_th:
                if i > 0:
                    y_1 = y[i - 1]
                    x_1 = x[i - 1]
                else:
                    y_1 = 1
                    x_1 = 0
                y_2 = y[i]
                x_2 = x[i]
                try:
                    y_th = y_1 + (y_2 - y_1) * (x_th - x_1) / (x_2 - x_1)
                except:
                    y_th = float('NaN')
                finally:
                    return y_th
        return y[len(x) - 1]


    def compute_hazard_data(self, hazard,
                              intensity_threshold, hazard_threshold,
                              statistic_name='mean'):

        self.hazard_data = hazard.curves_by_statistics(statistic_name)

        return map((lambda p: dict(zip(['point', 'haz_value',
                                        'prob_value'],
                                       (p['point'],
                                        self.get_haz_value(
                                            hazard.iml,
                                            hazard_threshold,
                                            p['curve']),
                                        self.get_prob_value(
                                            hazard.iml,
                                            intensity_threshold,
                                            p['curve'])
                                       )))),
                   self.hazard_data)


    def get_grid_points(self, grid_id):
        return self.db.get_points_by_datagrid_id(grid_id)


    def updateModel(self, **ctrls_options):

        print "ctrls_options %s" % ctrls_options
        haz_tmp = ctrls_options
        haz_tmp['hazard_threshold'] = 1 - math.exp(- haz_tmp['exp_time'] /
                                                   haz_tmp['ret_per'])
        self.hazard_options = haz_tmp

        print "core hazard_options %s " % self.hazard_options

        self._hazard = HazardModel(self._db,
                                   hazard_name=
                                   self.hazard_options['hazard_name'],
                                   exp_time=self.hazard_options['exp_time'])

        # TODO: grid_point should be eliminated from here
        # TODO: or from
        self.grid_points = self._hazard.grid_points

        self.hazard_data = self.compute_hazard_data(
            self._hazard,
            self.hazard_options['int_thresh'],
            self.hazard_options['hazard_threshold'])



    def exportRawPoints(self, haz_array):
        export_string = ''
        for i in range(self.data['npts']):
            export_string += "%f %f %f\n" % (self.data['lon'][i] *
                                             1000, self.data['lat'][i] * 1000,
                                             haz_array[i])
        return export_string


    def defEnsembleHaz(self, **_localEnsembleDetails):
        # TODO: this function is not correct at all!!
        haz_len = len(_localEnsembleDetails['components'])
        for i in range(haz_len):
            ntry = int(math.floor(self.data['npts'] * 0.5))
            tmp2 = self.data['hc'][_localEnsembleDetails['components'][i][
                'index']][self.data['dtime'].index(_localEnsembleDetails[
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
        percsel = range(10, 100, 10)
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
            tmpmodel += ");"  # ID in DB

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
        niml = len(
            self.data['iml'][_localEnsembleDetails['components'][i]['index']])
        # self.hc = np.zeros((self.nhaz, self.nt, self.nperc+1, self.npts, niml))
        self.data['hc'] = [[[['0' for i in range(self.data['npts'])]
                             for j in range(100)]
                            for k in range(self.nt)] for h in
                           range(self.data['nhaz'])]
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
                                            "Perc" + pp, dt,
                                            hccomb[0][self.data['percsel'][p]][
                                                i])

        print 'DB populated!!'
        self.data['perc_flag'].append(self._db.assignFlagPerc(tbname))
        print("UPDATE FLAGS PERCENTILES = {0}".format(self.self.data[
            'perc_flag']))

        # self.sb.SetStatusText("... ensemble model evaluated")
        print 'Task completed!!'
        print '------------------------------'


        # update DB, table hazard#

    @property
    def ctrls_data(self):
        return dict(self._ctrls_defaut.items() + self._ctrls_data.items())

    @property
    def hazard(self):
        return self._hazard

    @property
    def hazard_options(self):
        return self._hazard_options

    @hazard_options.setter
    def hazard_options(self, data):
        self._hazard_options = data

    @property
    def hazard_data(self):
        return self._hazard_data

    @hazard_data.setter
    def hazard_data(self, data):
        print "hazard_data setter"
        self._hazard_data = data

    @property
    def selected_point(self):
        return self._selected_point

    @selected_point.setter
    def selected_point(self, data):
        self._selected_point = data

    @property
    def selected_point_curves(self):
        return self._selected_point_curves

    @selected_point_curves.setter
    def selected_point_curves(self, data):
        self._selected_point_curves = data

    @property
    def grid_points(self):
        return self._grid_points

    @grid_points.setter
    def grid_points(self, points_list):
        self._grid_points = points_list

    @property
    def db(self):
        return self._db


def ensemble(*kargs):
    """
    It opens a pop-up dialog showing a text message.
    """
    hc = kargs[0]  # hazard curves
    hc_perc = kargs[1]  # percentiles for hazard curves
    tw = kargs[2]  # selected time window
    hazard = kargs[3]  # hazard phenomena
    dtime = kargs[4]  # time windows
    haz_selected = kargs[5]  # selected hazards to be combined
    haz_weights = kargs[6]  # selected weights for the hazards to be combined
    twsel = kargs[7]  # time windows selected
    percsel = kargs[8]  # percentiles to be computed
    # for each hazard, it is =1 if it has percentiles, =0 otherwise
    perc_flag = kargs[9]

    print "----ensemble()--------------"
    # hc[hsel][tw][perc][pt_sel][:]
    sel_first = haz_selected[0]
    # ntw = len(hc[sel_first])
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
            print "!!!!!!!Errore nel calcolo run totali" + str(
                isample + 1) + "<->" + str(nrun_eff)
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
