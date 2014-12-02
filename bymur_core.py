import bymur_functions as bf
import bymur_db as db
import numpy as np  # ma lo uso solo per sqrt?
import math
import random as rnd
import os
import scipy.interpolate as interpolate


class HazardPoint(object):
    """Describe data of a point in a HazardModel."""

    def __init__(self, core):
        """
        :rtype : bymur_core.HazardPoint
        :type core: bymur_core.BymurCore
        """
        self._core = core
        self._hazard = None
        self._index = None
        self._curves = None
        self._easting = None
        self._northing = None
        self._haz_value = None
        self._prob_value = None

    def update(self, hazard, index, hazard_threshold, intensity_treshold):
        """
        Update object to keep track of current selected point.

        :type hazard: bymur_core.HazardModel
        :type hazard_threshold: float
        :type intensity_treshold: float

        """
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
        """
        Return point easting.

        :return: bigint
        """
        return self._easting

    @property
    def northing(self):
        """
        Return point northing.

        :return: bigint
        """
        return self._northing

    @property
    def index(self):
        """
        Return grid point index.

        :return: bigint
        """
        return self._index

    @property
    def curves(self):
        """
        Return all point data curves.

        :return: list of dict{'statistic':{}, 'curve':{}}
        """
        return self._curves

    @property
    def haz_value(self):
        """
        Return point hazard value.

        :return: float
        """
        return self._haz_value

    @property
    def prob_value(self):
        """
        Return point probability value.

        :return: float
        """
        return self._prob_value

class EnsembleModel(object):
    def __init__(self, hazard_name, exposure_time, phen_name, db):
        self._db = db
        self._hazard_name = hazard_name
        self._exposure_time = exposure_time
        self._phenomenon_name = phen_name
        self._statistics = None
        self._datagrid_id = None
        self._points_data = None
        self._iml = None
        self._imt = None

    def save(self):
        phenomenon_id = self._db.insert_id_phenomenon(self._phenomenon_name)
        print " new hazard phenomenon name: %s , id: %s" \
              % (self._phenomenon_name, phenomenon_id)
        hazard_model_id = self._db.insert_id_hazard_model(
                phenomenon_id,
                self.datagrid_id,
                self.hazard_name,
                self.exposure_time,
                " ".join([str(x) for x in self.iml]),
                self.imt)

        print "new hazard_model_id %s" % hazard_model_id

        for stat in self._statistics:
            if stat != 'mean':
                stat_id = self._db.insert_id_statistic('percentile', stat)
            else:
                stat_id = self._db.insert_id_statistic(stat,'0')

            self._db.insert_hazard_statistic_rel(hazard_model_id, stat_id)

            self._db.insert_hazard_data(self.phenomenon,hazard_model_id,
                                        stat_id,
                                        [ point['point_id']
                                          for point in self.points_data],
                                        [ point['point_data'][stat]
                                          for point in self.points_data])



    @property
    def hazard_name(self):
        return self._hazard_name

    @property
    def exposure_time(self):
        return self._exposure_time

    @property
    def datagrid_id(self):
        return self._datagrid_id

    @datagrid_id.setter
    def datagrid_id(self, grid_id):
        self._datagrid_id = grid_id

    @property
    def phenomenon(self):
        return self._phenomenon_name

    @property
    def iml(self):
        return self._iml

    @iml.setter
    def iml(self, iml_thresholds):
        self._iml = iml_thresholds

    @property
    def imt(self):
        return self._imt

    @imt.setter
    def imt(self, imt):
        self._imt = imt

    @property
    def statistics(self):
        return self._statistics

    @statistics.setter
    def statistics(self, stat_list):
        self._statistics = stat_list

    @property
    def points_data(self):
        return self._points_data

    @points_data.setter
    def points_data(self, data):
        self._points_data = data



class HazardModel(object):
    """
    Rapresentation of an Hazard model, read from data_provider and
    exposed as PythonObject.

    """

    def __init__(self, data_provider, id=None, hazard_name=None, exp_time=None):
        """
        :type data_provider: bymur_db.BymurDB
        :type id: int
        :type hazard_name: str
        :type exp_time: float
        """

        self._db = data_provider
        if id is not None:
            hm = self._db.get_hazard_model_by_id(id)
        elif hazard_name is not None and exp_time is not None:
            hm = self._db.get_hazard_model_by_name_exptime(hazard_name,
                                                           exp_time)
        else:
            raise Exception("Bad initialization of HazardModel")

        self._hazard_id = hm['hazard_id']
        self._hazard_name = hm['hazard_name']
        self._phenomenon_id = hm['phenomenon_id']
        self._phenomenon_name = self._db.get_phenomenon_by_id(
            hm['phenomenon_id'])['name']
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
        self._points_data = []

    def fetch_all_points_data(self):
        self._points_data = self._db.get_points_all_data(self.phenomenon_id,
                                                    self.hazard_id,
                                                    self.grid_points)
        # print self._points_data[1000]
        # print len(self._points_data)
        # print self._points_data[0]

    def curves_by_statistics(self, statistic_name='mean'):
        """
        Return all points and corrisponding data curve for specified statistic.

        :type statistic_name: str
        :return: list of dict {'point': {}, 'curve':[]}
        """

        try:
            return self._curves[statistic_name]
        except KeyError:
            # print "HazardModel fetching statistic %s curves " % statistic_name
            stat_id = self._db.get_statistic_by_value(statistic_name)
            self._curves[statistic_name] = self._db.get_curves(
                self.phenomenon_id,
                self.hazard_id,
                stat_id)
        return self._curves[statistic_name]

    def to_xml(self):
        hazard_xml = ''


        return

    @property
    def hazard_id(self):
        """Return harzard model id. """

        return self._hazard_id

    @property
    def hazard_name(self):
        """Return harzard model name. """

        return self._hazard_name

    @property
    def datagrid_id(self):
        """Return associated datagrid id."""

        return self._datagrid_id

    @property
    def phenomenon_id(self):
        """Return associated phenonmenon id."""

        return self._phenomenon_id

    @property
    def phenomenon_name(self):
        """Return associated phenonmenon name."""

        return self._phenomenon_name

    @property
    def exposure_time(self):
        """Return associated exposure time."""

        return self._exposure_time

    @property
    def iml(self):
        """Return associad intensity threshold list."""

        return self._iml

    @property
    def imt(self):
        """Return associated unit measure for hazard."""

        return self._imt

    @property
    def date(self):
        """Return date (not yer used)."""

        return self._date

    @property
    def grid_points(self):
        """Return the associated grid points list."""

        return self._grid_points

    @property
    def grid_limits(self):
        """Return associated grid easting and northing min/max."""

        return self._grid_limits

    @property
    def curves(self):
        """
        Return all data curves defined for all grid point in the
        hazard grid.
        """

        return self._curves

    @property
    def points_data(self):
        """ Return all points data as list of dict. """
        return self._points_data


class BymurCore(object):
    """
    BymurCore object contain the model of ByMuR. It is in charge of organize
    hazard internals rapresentation and operations. All the values are
    calculated by methods defined inside this class.
    """

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

    ens_sample_number = 1000
    ens_percentiles = np.arange(5,100,5)

    def __init__(self):
        self._db = None
        self._db_details = None
        self._ctrls_data = {}
        self._grid_points = []
        self._hazard_options = {}
        self._hazard = None
        self._hazard_data = None
        self._selected_point = None
        # self._selected_point = HazardPoint(self)
        # self._selected_area = dict(inventory=bf.InventorySection(),
        self._selected_area = dict(inventory=None,
                                   fragility=None)
        # self._inventory = bf.parse_xml_inventory("data/InventoryByMuR.xml")
        self._inventory = None
        self._fragility = None
        self._loss = None
        self._risk = None

    def clear(self):
        self.grid_points = []
        self.hazard_options = {}
        self.hazard = None
        self.hazard_data = None
        self.selected_point = None
        self.selected_area = dict(inventory=None,
                                   fragility=None,
                                   loss = None,
                                   risk = None)
        self._inventory = None
        self._fragility = None
        self._loss = None
        self._risk = None

    def load_db(self, **dbDetails):
        """ Connect database and load hazard models data."""

        if (not self._db) and dbDetails:
            self.connect_db(**dbDetails)
        self._ctrls_data = self.get_controls_data()

    def connect_db(self, **dbDetails):
        """
        Connect database.

        :param dbDetails: dict(db_host= str, db_port= str,
                      db_user= str, db_password= str, db_name= str)
        """
        self._db_details = dbDetails
        try:
            self._db = db.BymurDB(**self._db_details)
        except:
            raise

    # TODO: devo implementare un reset dei pannelli

    def close_db(self):
        """ Close database connection. """

        if self._db:
            try:
                self._db.close()
                self._db = None
            except:
                raise
                self._ctrls_data = {}
                self._grid_points = []
                self._hazard_options = {}
                self._hazard = None
                self._hazard_data = None

    def drop_tables(self, **kwargs):
        """ Drop all tables in currently open database."""
        try:
            self._db.drop_tables()
        except:
            raise


    def create_db(self, **createDBDetails):
        """ Create a new database.

        Create database if it doesn't exist yet. If a database with the given
        name is already present, populate it with tables.

        :param dbDetails: dict(db_host= str, db_port= str,
                      db_user= str, db_password= str, db_name= str)

        """
        print "core.createDB"
        if self._db:
            raise Exception("You need to close the open db first!")

        self._db = db.BymurDB(db_host=createDBDetails['db_host'],
                              db_port=createDBDetails['db_port'],
                              db_user=createDBDetails['db_user'],
                              db_password=createDBDetails['db_password'])
        self.db.create(createDBDetails['db_name'])
        self._ctrls_data = self.get_controls_data()
        # TODO: add a dialog for successfull creation

    def add_data(self, **addDBData):
        """
        Read data from XML files and add to database.

        :param addDBData: dict(haz_files = list(str), phenomenon = str,
        datagrid_name = str)

        """

        self.db.add_data(addDBData['datagrid_name'],
                         addDBData['haz_files'],
                         addDBData['phenomenon'])
        self._ctrls_data = self.get_controls_data()

    def load_grid(self, **gridData):
        """
        Read grid from file and add it to database.

        :param gridData: dict(basedir=str, filepath=str)
        """

        print "core loadGrid: %s" % gridData
        filepath = gridData.pop('filepath', None)
        return self.db.load_grid(filepath)

    def get_controls_data(self):
        """ Read hazard models data from database. """

        ret = {}
        hazard_models = self.db.get_hazard_models_list()
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
        # print "phenomena %s " % ret['phenomena']
        return ret

    def read_fragility_model(self, phenomenon_id):
        frag_dic = self.db.get_fragility_model_by_phenid(phenomenon_id)
        _fragility = bf.FragilityModel()
        _fragility.id = frag_dic['id']
        _fragility.model_name = frag_dic['model_name']
        _fragility.description = frag_dic['description']
        _fragility.imt = frag_dic['imt']
        _fragility.iml = [float(l) for l in frag_dic['iml'].split(" ")]
        _fragility.hazard_type = self.db.get_phenomenon_by_id(
            frag_dic['phenomenon_id'])['name']
        _fragility.limit_states = [ls['name'] for ls in
                            self.db.get_limitstates_by_frag_id(frag_dic['id'])]
        _fragility.statistics = [st['name'] for st in
                            self.db.get_statistics_by_frag_id(frag_dic['id'])]
        return _fragility
    
    def read_loss_model(self, phenomenon_id, frag_id):
        loss_dic = self.db.get_loss_model_by_phenid(phenomenon_id)
        _loss = bf.LossModel()
        _loss.id = loss_dic['id']
        _loss.loss_type = loss_dic['loss_type']
        _loss.model_name = loss_dic['model_name']
        _loss.description = loss_dic['description']
        _loss.unit = loss_dic['unit']
        _loss.hazard_type = self.db.get_phenomenon_by_id(
            loss_dic['phenomenon_id'])['name']
        _loss.limit_states = [ls['name'] for ls in
                            self.db.get_limitstates_by_frag_id(frag_id)]
        _loss.statistics = [st['name'] for st in
                            self.db.get_statistics_by_loss_id(loss_dic['id'])]
        return _loss
    
    def read_risk_model(self, haz_id):
        risk_dic = self.db.get_risk_model_by_hazid(haz_id)
        print "Risk dic: %s"  % risk_dic
        if risk_dic is None:
            return None
        _risk = bf.RiskModel()
        _risk.id = risk_dic['id']
        _risk.risk_type = risk_dic['risk_type']
        _risk.model_name = risk_dic['model_name']
        _risk.hazard_model_name = self.db.get_hazard_model_by_id(risk_dic[
            'hazard_id'])['hazard_name']
        _risk.fragility_model_name = self.db.get_fragility_model_by_id(risk_dic[
            'fragility_id'])['model_name']
        _risk.loss_model_name = self.db.get_loss_model_by_id(risk_dic[
            'loss_id'])['model_name']
        _risk.description = risk_dic['description']
        _risk.investigation_time = risk_dic['investigation_time']
        _risk.hazard_type = self.db.get_phenomenon_by_id(
            risk_dic['phenomenon_id'])['name']
        _risk.statistics = [st['name'] for st in
                            self.db.get_statistics_by_risk_id(risk_dic['id'])]
        return _risk


    def read_inventory_model(self, grid_id):
        inv_dic = self.db.get_inventory_by_datagrid_id(grid_id)
        _inventory = bf.InventoryModel(name=inv_dic['name'])
        _inventory.classes.update({'generalClasses':[],
                                        'ageClasses':[],
                                        'houseClasses':[]})
        for c in inv_dic['general_classes']:
            _inventory.classes['generalClasses'].append(
                bf.InventoryGeneralClass(name=c['name'],
                                         label=c['label']))
        for c in inv_dic['age_classes']:
            _inventory.classes['ageClasses'].append(
                bf.InventoryAgeClass(name=c['name'],
                                     label=c['label']))
        for c in inv_dic['house_classes']:
            _inventory.classes['houseClasses'].append(
                bf.InventoryHouseClass(name=c['name'],
                                       label=c['label']))

        _inventory.classes['costClasses'] = dict()
        for phen_class in inv_dic['cost_classes']:
            phen = phen_class['phenomenon_name']
            _inventory.classes['costClasses'][phen.lower()] = []
            for c_str in phen_class['classes'].split(":"):
                c_name, c_label = c_str.lstrip("(").rstrip(")").split(",")
                c_tmp = bf.InventoryCostClass(phenomenon=phen.lower(),
                                              name=c_name,
                                              label=c_label)
                _inventory.classes['costClasses']\
                        [phen.lower()].append(c_tmp)

        _inventory.classes['fragilityClasses'] = dict()
        for phen_class in inv_dic['fragility_classes']:
            phen = phen_class['phenomenon_name'].lower()
            _inventory.classes['fragilityClasses'][phen] = []
            for c_str in phen_class['classes'].split(":"):
                c_name, c_label = c_str.lstrip("(").rstrip(")").split(",")
                c_tmp = bf.InventoryFragilityClass(phenomenon=phen,
                                                   name=c_name,
                                                   label=c_label)
                _inventory.classes['fragilityClasses']\
                        [phen].append(c_tmp)

        _inventory_sections = self.db.get_sections_by_inventory_id(
            inv_dic['inventory_id'])

        for sec in _inventory_sections:
            sec_tmp = bf.InventorySection()
            sec_tmp.areaID = int(sec['areaID'])
            sec_tmp.sectionID = int(sec['sectionID'])
            sec_tmp.centroid =  (float(sec['centroidX']),
                                 float(sec['centroidY']))
            sec_tmp.geometry = [(float(p.strip().split(" ")[0]),
                                 float(p.strip().split(" ")[1]))
                                for p in sec['geometry'].split(",")]
            sec_tmp.asset = bf.InventoryAsset()
            sec_tmp.asset.total = int(sec['total_buildings'])
            if sec_tmp.asset.total > 0:
                sec_tmp.asset.counts['genClassCount'] = \
                    [int(i) for i in sec['general_classes_count'].split(" ")]
                sec_tmp.asset.counts['ageClassCount'] = \
                    [int(i) for i in sec['age_classes_count'].split(" ")]
                sec_tmp.asset.counts['houseClassCount'] = \
                    [int(i) for i in sec['house_classes_count'].split(" ")]

                cc_prob = self.db.get_costclass_prob_by_area_id(sec['id'])
                for phen_class in cc_prob:
                    phen = phen_class['phenomenon_name'].lower()
                    fnc_tmp = [float(f) for f in phen_class['fnc'].split(" ")]
                    sec_tmp.asset.cost_class_prob[phen] = dict(fnc=fnc_tmp)

                fc_prob = self.db.get_fragclass_prob_by_area_id(sec['id'])
                for phen_class in fc_prob:
                    phen = phen_class['phenomenon_name'].lower()
                    fnt_tmp = [float(f) for f in phen_class['fnt'].split(" ")]
                    fnt_given_tmp = [[float(x) for x in c_list.split(" ")]
                            for c_list in
                            phen_class['fnt_given_general_class'].split(",")]
                    sec_tmp.asset.frag_class_prob[phen] = \
                        dict(fnt=fnt_tmp,
                             fntGivenGeneralClass = fnt_given_tmp)
            _inventory.sections.append(sec_tmp)

        return _inventory

    def updateModel(self, **ctrls_options):

        """Update HazardModel reflecting selected options. """
        # print "ctrls_options %s" % ctrls_options
        self.clear()
        haz_tmp = ctrls_options
        haz_tmp['hazard_threshold'] = 1 - math.exp(- haz_tmp['exp_time'] /
                                                   haz_tmp['ret_per'])
        self.hazard_options = haz_tmp

        self._hazard = HazardModel(self._db,
                                   hazard_name=
                                   self.hazard_options['hazard_name'],
                                   exp_time=self.hazard_options['exp_time'])

        self.inventory = self.read_inventory_model(self._hazard.datagrid_id)

        if ctrls_options['risk_model_name'] is not None and ctrls_options[
                                     'risk_model_name'] != '':
            print "Reading fragility, loss and risk models"
            self.fragility = self.read_fragility_model(self._hazard.phenomenon_id)
            self.loss = self.read_loss_model(self._hazard.phenomenon_id,
                                             self.fragility.id)
            self.risk = self.read_risk_model(self._hazard.hazard_id)

        # TODO: grid_point should be eliminated from here
        # TODO: or from
        self.grid_points = self._hazard.grid_points

        self.hazard_data = self._compute_hazard_data(
            self._hazard,
            self.hazard_options['int_thresh'],
            self.hazard_options['hazard_threshold'])

    def set_area_by_ID(self, areaID):
        for sec in self.inventory.sections:
            if sec.areaID == areaID:
                self.selected_area['areaID'] = areaID
                self.selected_area['area_db_id'] = \
                    self.db.get_area_dbid_by_areaid(areaID)
                self.selected_area['inventory'] = sec
                # TODO: questi dovrebbero diventare oggetti
                if self.risk is not None:
                    self.selected_area['fragility'] = self.db.get_fragdata_by_areaid(
                                self.fragility.id, areaID)
                    self.selected_area['loss'] = self.db.get_lossdata_by_areaid(
                                self.loss.id, areaID)
                    self.selected_area['risk'] = self.db.get_riskdata_by_areaid(
                                self.risk.id, areaID)
                break

    def set_point_by_index(self, index):
        """
        Set selected point by index in model.

        :param index: bigint
        """
        try:
            tmp = HazardPoint(self)
            tmp.update(self.hazard, index,
                       self.hazard_options['hazard_threshold'],
                       self.hazard_options['int_thresh'])
            self.selected_point = tmp
            # self.selected_point.update(self.hazard, index,
            #                            self.hazard_options['hazard_threshold'],
            #                            self.hazard_options['int_thresh'])
            return True
        except Exception as e:
            print "Exception in select_point_by_index: %s" % str(e)
            return False


    def set_point_by_coordinates(self, xpoint, ypoint):
        """
        Set selected point by coordinates in model.

        :param xpoint: bigint
        :param ypoint: bigint
        """

        xsel = np.float64(xpoint)
        ysel = np.float64(ypoint)
        if (self.hazard.grid_limits['east_min'] <= xsel <=
                self.hazard.grid_limits['east_max']
            and self.hazard.grid_limits['north_min'] <= ysel <=
                self.hazard.grid_limits['north_max']):
            distances = np.hypot(xsel-[p['easting'] for p in self.grid_points],
                                 ysel-[p['northing'] for p in self.grid_points])
            tmp = HazardPoint(self)
            tmp.update(self.hazard, distances.argmin(),
                       self.hazard_options['hazard_threshold'],
                       self.hazard_options['int_thresh'])
            self.selected_point = tmp
            return True
        else:
            return False

    def get_haz_value(self, int_thresh_list, hazard_threshold, curve):
        """
        Calculate and return hazard value interpolation.

        :type int_thresh_list: list of float
        :type hazard_threshold: float
        :type curve: list of float
        :return: float
        """
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
        """
        Calculate and probability hazard value interpolation.

        :type int_thresh_list: list of float
        :type intensity_threshold: float
        :type curve: list of float
        :return: float
        """
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


    def _compute_hazard_data(self, hazard,
                              intensity_threshold, hazard_threshold,
                              statistic_name='mean'):

        """
        Calculate hazard statistics interpolations for every point.

        :type hazard: bymur_core.HazardModel
        :type intensity_threshold: float
        :type hazard_threshold: float
        :type statistic_name: str
        :return: list of dict(point: {}, haz_value: float, prob_value: float)
        """
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


    # def _get_grid_points(self, grid_id):
    #     return self.db.get_points_by_datagrid_id(grid_id)


    def exportRawPoints(self, haz_array):
        export_string = ''
        for i in range(self.data['npts']):
            export_string += "%f %f %f\n" % (self.data['lon'][i] *
                                             1000, self.data['lat'][i] * 1000,
                                             haz_array[i])
        return export_string

    def _comulative_prob(self, hazard, threshold_index):
        pass
        _comulative = list()
        # devo escludere la media
        # for key in hazard.curves.keys():
        #     for point in hazard.c
        #     _comulative.append(hazard.curves[key]['curve'][threshold_index])


    def exportHaz(self, **local_data):

        haz_model = HazardModel(self.db, hazard_name=local_data['expHazModel'],
                                   exp_time=local_data['expHazExpTime'])
        tmp_name = os.path.join(local_data['expHazDir'], haz_model.hazard_name)
        if not os.path.exists(tmp_name):
            os.makedirs(tmp_name)
        tmp_name = os.path.join(tmp_name, local_data['expHazExpTime'])
        if not os.path.exists(tmp_name):
            os.makedirs(tmp_name)

        for stat in haz_model.statistics:
            haz_model_xml = bf.HazardModelXML(local_data['expHazPhen'])

            if stat['name'] == 'mean':
                haz_model_xml.statistic = 'mean'
                haz_model_xml.percentile_value = '0'
                filename = os.path.join(tmp_name,
                                    "hazardcurve-mean.xml"
                                    )
            else:
                haz_model_xml.statistic = 'percentile'
                haz_model_xml.percentile_value = \
                    stat['name'][len("percentile"):]
                filename = os.path.join(tmp_name,
                                "hazardcurve-percentile-"+
                                str(haz_model_xml.percentile_value).zfill(2) +
                                ".xml" )

            # print haz_model.hazard_name
            haz_model_xml.hazard_model_name = haz_model.hazard_name
            try:
                haz_model_xml.model_name = haz_model.model_name
            except Exception as e:
                pass

            # print haz_model.iml
            haz_model_xml.iml_thresholds = haz_model.iml
            # print haz_model.imt
            haz_model_xml.iml_imt = haz_model.imt
            # print haz_model.exposure_time
            haz_model_xml.exp_time = haz_model.exposure_time

            haz_model_xml.points_coords = [dict(easting=p['easting'],
                                                northing=p['northing'])
                                           for p in haz_model.grid_points]
            haz_model_xml.points_values = [" ".join([str(v)
                                                for v in c['curve']])
                    for c in haz_model.curves_by_statistics(stat['name'])]

            print "Exporting to file %s" % filename
            file_desc = open(filename,"w")
            file_desc.writelines(haz_model_xml.tostring())
            file_desc.close()




    def defEnsembleHaz(self, **local_data):

        # Instantiate HazardModels and fetch all curves for all
        # defined statistics
        _haz_models = [{'model': HazardModel(self.db,
                                   hazard_name=haz['hazard_name'],
                                   exp_time=local_data['ensExpTime'])}
                       for haz in local_data['ensHaz']]

        for haz in _haz_models:
                haz['model'].fetch_all_points_data()
                haz['stats_labels'] = [stat['name'][len('percentile'):]
                        for stat in haz['model'].statistics
                        if stat['name'] != 'mean']
                haz['y_percentiles'] = np.sort(np.array(
                    [float(s)/100 for s in haz['stats_labels']]))

        # Parse and normalize hazards weight
        _haz_weights = np.array([np.float(haz['weight'])
                                 for haz in local_data['ensHaz']])
        _haz_weights /= _haz_weights.sum()
        for i_haz in range(len(_haz_models)):
            _haz_models[i_haz]['weight'] = _haz_weights[i_haz]
            _haz_models[i_haz]['samples_number'] = np.int(np.rint(
                _haz_weights[i_haz] * np.float(self.ens_sample_number)))


        # Extract some metadata on new ensemble hazard definition and
        # istantiate new object
        ensemble_data = dict()
        # ensemble_data['hazard_name'] = "_".join([haz['model'].hazard_name + \
        #                                  "-" + str(np.around(haz['weight'],
        #                                                decimals=2))
        #                                 for haz in _haz_models])
        ensemble_data['hazard_name'] = local_data['ensName']
        ensemble_data['exposure_time'] = local_data['ensExpTime']
        ensemble_data['iml_thresholds'] = local_data['ensIMLThresh']
        ensemble_data['grid_name'] = local_data['ensGrid']

        ensemble_data['imt'] = _haz_models[0]['model'].imt

        print "Ensemble data: %s" % ensemble_data
        new_ensemble = EnsembleModel(ensemble_data['hazard_name'],
                                     ensemble_data['exposure_time'],
                                     local_data['ensPhen'],
                                     self.db)
        new_ensemble.datagrid_id = _haz_models[0]['model'].datagrid_id
        new_ensemble.iml = ensemble_data['iml_thresholds']
        new_ensemble.imt = ensemble_data['imt']

        # Make sure samples_number sum is self.ens_sample_number adjusting
        # hazard samples number if needed
        _sum_diff = self.ens_sample_number - \
                np.int(np.sum([haz['samples_number'] for haz in _haz_models]))
        while _sum_diff != 0:
            haz_ind = np.random.random_integers(0, len(_haz_models)-1)
            if _sum_diff < 0:
                _haz_models[haz_ind]['samples_number'] -= 1
            else:
                _haz_models[haz_ind]['samples_number'] += 1
            _sum_diff = self.ens_sample_number - \
                np.int(np.sum([haz['samples_number'] for haz in _haz_models]))

        print "haz_models_id %s" % [h['model'].hazard_id for h in _haz_models]
        print "haz_weights %s" % [h['weight'] for h in _haz_models]
        print "samples_number %s , sum %s" % ([h['samples_number'] for h in
                                       _haz_models],
                    np.array([h['samples_number'] for h in _haz_models]).sum())
        print "haz_stats %s" % [h['stats_labels'] for h in _haz_models]
        print "haz_y_percentiles %s" % [h['y_percentiles'] for h in _haz_models]

        # point_curves structure
        # point_curves = [ {point_id,
        #                   point_data: {hazard_1: [ [soglia1percentile1,
        #                                             soglia1percentile2,
        #                                              ...               ],
        #                                            [soglia2percentile1,
        #                                             soglia2percentile2,
        #                                             ...               ]
        #                                           ],
        #                                hazard_2: [ [soglia1percentile1,
        #                                           .....]
        #                                },...},
        #                   {point_id,...

        # For every point 'p', every hazard component 'h', every threshold 't'
        # build an array point_curves[p_index]['point_data'][h_index][t_index]
        # containing values of all percentiles stored in database
        point_curves = []
        for i_point in range(len(_haz_models[0]['model'].grid_points)):
            p_tmp = dict()
            p_tmp['point_id'] = _haz_models[0]['model'].grid_points[i_point]['id']
            p_tmp['point_data'] = dict()
            for haz in _haz_models:
                _haz_point_data = []
                for i_thresh in range(len(local_data['ensIMLThresh'])):
                    _thresh_data = []
                    for stat in haz['stats_labels']:
                        _thresh_data.append(
                            haz['model'].points_data[i_point]['point_data']
                            [stat][i_thresh])
                    _haz_point_data.append(_thresh_data)
                p_tmp['point_data'][haz['model'].hazard_id] =\
                    np.sort(np.array(_haz_point_data))
            point_curves.append(p_tmp)
        # print "Esempio di dati per un punto %s" % point_curves[0]
        # print point_curves[1000]['point_data'][_haz_models[0]['model'].hazard_id][0]


        # Generate random sample points
        _samples = np.random.uniform(0, 1, self.ens_sample_number)

        # For every point, for every threshold, sample data, calculate
        # percentiles and mean, store values in point_curves array
        for i_point in range(len(_haz_models[0]['model'].grid_points)):
            point_data = point_curves[i_point]['point_data']
            point_ensemble_hazard = []
            for i_thresh in range(len(local_data['ensIMLThresh'])):
                haz_ind = 0
                sample_index = 0
                ens_thresh_haz = dict()
                ens_thresh_haz['samples'] = np.array([])
                while sample_index < self.ens_sample_number:
                    inv_cdf = interpolate.interp1d(
                        _haz_models[haz_ind]['y_percentiles'],
                        point_data[_haz_models[haz_ind]['model'].hazard_id][
                            i_thresh],
                        bounds_error=False)
                    point_ens_samples = \
                        inv_cdf(_samples[sample_index:sample_index+
                                    _haz_models[haz_ind]['samples_number']])
                    sample_index += _haz_models[haz_ind]['samples_number']
                    haz_ind += 1
                    ens_thresh_haz['samples'] = np.append(
                        ens_thresh_haz['samples'],
                        point_ens_samples)
                ens_thresh_haz['percentiles'] = \
                    np.nanpercentile(ens_thresh_haz['samples'],
                                  self.ens_percentiles)
                ens_thresh_haz['mean'] =  np.nanmean(ens_thresh_haz['samples'])
                point_ensemble_hazard.append(ens_thresh_haz)
            point_curves[i_point]['point_data']['ensemble'] = \
                point_ensemble_hazard

        # print point_curves[1000]['point_data']['ensemble'][7]

        # Transform point_curves array in a structure compatible with
        # points_data as returned(taken) from HazardModel(EsembleModel) class
        ensemble_points_data = list()
        for i_point in range(len(_haz_models[0]['model'].grid_points)):
            p_tmp = dict()
            p_tmp['point_id'] = point_curves[i_point]['point_id']
            p_tmp['point_data'] = dict()

            for i_perc in range(len(self.ens_percentiles)):
                p_tmp['point_data'][str(self.ens_percentiles[i_perc]).zfill(2)]\
                    = [_thresh_data['percentiles'][i_perc] for _thresh_data in
                       point_curves[i_point]['point_data']['ensemble']]

            p_tmp['point_data']['mean'] = [_thresh_data['mean']
                                               for _thresh_data in
                                point_curves[i_point]['point_data']['ensemble']]
            ensemble_points_data.append(p_tmp)

        new_ensemble.points_data = ensemble_points_data
        # print new_ensemble.points_data[1000]

        stat_tmp = [str(int(x)).zfill(2) for x in self.ens_percentiles]
        stat_tmp.append("mean")
        new_ensemble.statistics = stat_tmp


        new_ensemble.save()

        return
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
    @hazard.setter
    def hazard(self, data):
        self._hazard = data

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
        self._hazard_data = data

    @property
    def inventory(self):
        return self._inventory
    @inventory.setter
    def inventory(self, data):
        self._inventory = data
        
    @property
    def fragility(self):
        return self._fragility
    @fragility.setter
    def fragility(self, data):
        self._fragility = data

    @property
    def loss(self):
        return self._loss
    @loss.setter
    def loss(self, data):
        self._loss = data
        
    @property
    def risk(self):
        return self._risk
    @risk.setter
    def risk(self, data):
        self._risk = data

    @property
    def selected_area(self):
        return self._selected_area
    @selected_area.setter
    def selected_area(self, data):
        self._selected_area = data

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
