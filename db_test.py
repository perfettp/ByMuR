# from sqlalchemy.ext.automap import automap_base
# from sqlalchemy.orm import Session
# from sqlalchemy import create_engine
#
# Base = automap_base()
#
# engine = create_engine("mysql+mysqldb://***REMOVED***:***REMOVED***@***REMOVED***/bymurDB-dev?charset"
# "=utf8&use_unicode=0")
#
# Base.prepare(engine, reflect=True)
#
# Volcano = Base.classes.volcanos
# HazardModel = Base.classes.hazard_models
# Phenomena = Base.classes.phenomena
#
# session = Session(engine)
#
# volcanic = Phenomena(name='VOLCANIC')
# session.add(volcanic)
# our_volcano = session.query(Phenomena).first()
# print our_volcano
# for table in reversed(Base.metadata.sorted_tables):
#     print "%s - %s" % (table,table.foreign_keys)
#     print "%s - %s" % (table,table.primary_key)

import MySQLdb as mdb
import utm
import os
import xml.etree.ElementTree
import re
import time



class HazardModel(object):
    _hazard_schema = ''

    def __init__(self, filename, phenomenon):
        if not self._validate(self._hazard_schema):
            raise Exception("XML file not valid")
        else:
            self._filename = filename
            self._volcano = ''
            self._model_name = ''
            self._iml_thresholds = []
            self._iml_imt = ''
            self._dtime = ''
            self._statistic = ''
            self._percentile_value = 0
            self._points_values= []
            self._points_coords = []
            self._phenomenon = phenomenon.upper()

            print "Parsing %s" % self._filename
            try:
                self.parse()
            except Exception as e:
                print self.__class__.__name__ + ", error parsing file " + \
                      self._filename +  " : " + str(e)
                raise Exception(str(e))
    def parse(self):
        context = xml.etree.ElementTree.iterparse(self._filename,
                                               events=("start","end"))
        # context = iter(context)
        for event, element in context:
            if event == "start":
                if element.tag == 'hazardCurveField':
                    self._statistic = element.get('statistics')
                    if self.statistic == 'percentile':
                        self._percentile_value = float(element.get(
                            'percentileValue', '0'))
                    else:
                        self._percentile_value = 0
                    # print "statistic: %s" % self._statistic
                    # print "percentile: %s" % self._percentile_value

            else:
                if element.tag == 'volcano':
                    self._volcano = element.get('volcanoName')
                    element.clear()
                    # print "volcano: %s" % self._volcano
                elif element.tag == 'model':
                    self._model_name = element.get('Model')
                    # print "model: %s" % self._model_name
                    element.clear()
                elif element.tag == 'timeterm':
                    self._dtime = float(element.get('deltaT').strip('yr'))
                    # print "dtime: %s" % self._dtime
                    element.clear()
                elif element.tag == 'IML':
                    self._iml_imt = element.get('IMT')
                    # print "imt: %s" % self._iml_imt
                    self._iml_thresholds = list(element.text.strip().split())
                    # print "iml_thresholds: %s" % self._iml_thresholds
                    element.clear()
                elif element.tag == 'HCNode':
                    point_pos = {}
                    gml_pos = element.find('.//gmlpos').text.split()
                    point_pos['northing'] = float(gml_pos[0])
                    point_pos['easting']  = float(gml_pos[1])
                    point_val = [float(x) for x in
                                 element.find( './/poE').text.split()]
                    # print "point: %s" % point
                    self._points_coords.append(point_pos)
                    self._points_values.append(point_val)
                    element.clear()
                elif element.tag == 'hazardCurveField':
                    element.clear()
        return True

    def _validate(self, hazard_schema):
        return True

    @property
    def hazard_schema(self):
        return self.hazard_schema

    @property
    def filename(self):
        return self._filename

    @property
    def volcano(self):
        return self._volcano

    @property
    def model_name(self):
        return self._model_name

    @property
    def iml_thresholds(self):
        return self._iml_thresholds

    @property
    def iml_imt(self):
        return self._iml_imt

    @property
    def dtime(self):
        return self._dtime

    @property
    def statistic(self):
        return self._statistic

    @property
    def percentile_value(self):
        return self._percentile_value

    @property
    def points_values(self):
        return self._points_values

    @property
    def points_coords(self):
        return self._points_coords

    @property
    def phenomenon(self):
        return self._phenomenon


def points_to_latlon(points, utm_zone_number=33,
                     utm_zone_letter='T', decimals = 5):
    res = []
    for p in points:
        lat,lon = utm.to_latlon(float(p['easting']),
                                float(p['northing']),
                                utm_zone_number,
                                utm_zone_letter)
        res.append({'latitude': round(lat, decimals),
                    'longitude':round(lon, decimals)})
    return res


def get_gridpoints_from_file(filepath, utm_coords = True, utm_zone_number=33,
                             utm_zone_letter='T', decimals = 5 ):
        gridfile = open(filepath, 'r')
        points = []
        if utm_coords:
            for line in gridfile:
                line_arr = line.strip().split()
                lat, lon = utm.to_latlon(float(line_arr[0]),
                                         float(line_arr[1]),
                                         utm_zone_number,
                                         utm_zone_letter)
                points.append({'latitude': round(lat, decimals) ,
                               'longitude':round(lon, decimals)
                })
            return points
        else:
            return False


class BymurDB():
    _db = None

    def __init__(self, **kwargs):
        """
        Connecting to database
        """
        try:
            self._connection = mdb.connect(host=kwargs.pop('db_host',
                                                           '***REMOVED***'),
                                           port=int(kwargs.pop('db_port',
                                                               3306)),
                                           user=kwargs.pop('db_user',
                                                           '***REMOVED***'),
                                           passwd=kwargs.pop('db_password',
                                                             '***REMOVED***'),
                                           db=kwargs.pop('db_name',
                                                         'bymurDB-dev'))
            self._connection.autocommit(True)
            self._cursor = self._connection.cursor()
        except:
            raise

    def commit(self):
        self._connection.commit()

    def phenomena_list(self):
        sql_query = "SELECT * from phenomena"
        self._cursor.execute(sql_query.format())
        return self._cursor.fetchall()

    def datagrid_id(self, name):
        sqlquery = "SELECT id FROM datagrids WHERE name = '{0}'"
        self._cursor.execute(sqlquery.format(name.upper()))
        id = self._cursor.fetchone()
        if id:
            return id[0]
        else:
            return 0

    def datagrid_get_insert_id(self, name):

        sqlquery = "SELECT id FROM datagrids WHERE name = '{0}'"
        self._cursor.execute(sqlquery.format(name.upper()))
        id = self._cursor.fetchone()
        if id:
            return id[0]
        else:
            sqlquery = "INSERT INTO datagrids (name) VALUES('{0}')"
            self._cursor.execute(sqlquery.format(name.upper()))
            return self._cursor.lastrowid

    def datagrid_points_rel(self, datagrid_id, points_id_list):
        """
        Add a relationship in table 'grid_points' between datagrid_id and
        each point in points_id_list
        :param datagrid_id: id of datagrid entry
        :param points_id_list: list of points id to associate with datagrid_id
        :return: number of new relationship added
        """
        sqlquery = """
                    INSERT IGNORE INTO grid_points (id_datagrid, id_point)
                        VALUES(""" + str(datagrid_id) + """, %s)"""
        return self._cursor.executemany(sqlquery, [(id,) for id
                                                   in points_id_list])


    def datagrid_points_insert(self, datagrid_id, points):
        """
        """

        # # Insert grid if it doesn't exists
        # datagrid_id = self.datagrid_get_insert_id(datagrid_name)
        # Insert points
        # print "Point insert result: %s" % self.points_insert(points)
        # Get list of points id
        pointsid_list = self.pointsid_list(points)
        # print "Points id list: %s " % pointsid_list
        # Associate grid with points
        return self.datagrid_points_rel(datagrid_id, pointsid_list)


    def points_insert(self, points):
        """
        Insert multiple point in table 'points' if they don't already exist
        :param points: list of point dictionaries
        :return: number of new points inserted
        """
        sqlquery = """
                    INSERT IGNORE INTO points (latitude,
                                        longitude)
                        VALUES(%(latitude)s, %(longitude)s)
                    """
        return self._cursor.executemany(sqlquery, points)

    def pointsid_list(self, points):
        """
        Get points id list from table 'point'
        :param points: list of point dictionaries
        :return:
        """

        # print points
        sqlquery = """
                    SELECT id FROM points WHERE (latitude, longitude)
                        IN (%s)
                    """
        if len(points) < 1:
            return -1
        points_list = ', '.join([str((x['latitude'], x['longitude'])) for
                                x in
                                points])
        sqlquery %= points_list
        self._cursor.execute(sqlquery)
        return [item[0] for item in self._cursor.fetchall()]

    def phenomenon_get_insert_id(self, phenomenon_name):

        sqlquery = "SELECT id FROM phenomena WHERE name = '{0}'"
        self._cursor.execute(sqlquery.format(phenomenon_name.upper()))
        id = self._cursor.fetchone()
        if id:
            return id[0]
        else:
            sqlquery = "INSERT INTO phenomena (name) VALUES('{0}')"
            self._cursor.execute(sqlquery.format(phenomenon_name.upper()))
            return self._cursor.lastrowid

    def intensity_measure_unit_get_insert_id(self, unit_name):

        sqlquery = """
                    SELECT id FROM intensity_measure_unit
                    WHERE measure_unit_text = '{0}'
                   """
        # print sqlquery.format(unit_name)
        self._cursor.execute(sqlquery.format(unit_name))
        id = self._cursor.fetchone()
        if id:
            return id[0]
        else:
            sqlquery = """
                        INSERT INTO intensity_measure_unit (measure_unit_text)
                        VALUES('{0}')
                       """
            # print sqlquery.format(unit_name)
            self._cursor.execute(sqlquery.format(unit_name))
            return self._cursor.lastrowid

    def intensity_thresholds_insert(self, int_thres, imt_id):
        """
        """
        sqlquery = """
                    INSERT IGNORE INTO intensity_thresholds (value,
                        id_unit) VALUES( %s, """ + str(imt_id) + """)"""

        # print sqlquery
        # print int_thres

        return self._cursor.executemany(sqlquery, [(val,) for val
                                                   in int_thres])

    def intensity_thresholds_idlist(self, imt_id, iml_thresholds):
        """

        :param imt_id:
        :param iml_thresholds:
        :return:
        """

        sqlquery = """
                    SELECT id FROM intensity_thresholds WHERE
                    (value) IN (%s) AND id_unit=""" + str(imt_id)

        if len(iml_thresholds) < 1:
            return -1
       #  print iml_thresholds
        iml_thresh_list = ', '.join([str(y) for y in [float(x)
                                                      for x in iml_thresholds]])
        sqlquery %= iml_thresh_list
        # print "intensity_thresholds_idlist %s" % sqlquery
        self._cursor.execute(sqlquery)
        return [item[0] for item in self._cursor.fetchall()]

    def hazard_thresholds_rel(self, hazard_id, thresholds_id_list):
        """

        """
        sqlquery = """
                    INSERT IGNORE INTO hazmodel_intensities
                    (id_hazard_model, id_intensity_threshold)
                        VALUES(""" + str(hazard_id) + """, %s)"""
        return self._cursor.executemany(sqlquery, [(id,) for id
                                                   in thresholds_id_list])

    def statistic_get_insert_id(self, statistic,
                                percentile_value):
        sqlquery = "SELECT id FROM statistics WHERE name = '{0}'"
        if percentile_value:
            statistic_name = statistic + str(percentile_value)
        else:
            statistic_name = statistic

        self._cursor.execute(sqlquery.format(statistic_name))
        id = self._cursor.fetchone()
        if id:
            return id[0]
        else:
            sqlquery = "INSERT INTO statistics (name) VALUES('{0}')"
            self._cursor.execute(sqlquery.format(statistic_name))
            return self._cursor.lastrowid

    def hazard_statistic_rel(self, hazard_id, statistic_id):
        """

        """
        sqlquery = """
                    INSERT IGNORE INTO hazmodel_statistics
                    (id_hazard_model, id_statistic)
                        VALUES ({0}, {1})"""
        return self._cursor.execute(sqlquery.format(hazard_id, statistic_id))

    def exposure_time_get_insert_id(self, exposure_time):
        sqlquery = "SELECT id FROM exposure_times WHERE years = '{0}'"
        self._cursor.execute(sqlquery.format(str(float(exposure_time))))
        id = self._cursor.fetchone()
        if id:
            return id[0]
        else:
            sqlquery = "INSERT INTO exposure_times (years) VALUES('{0}')"
            self._cursor.execute(sqlquery.format(str(float(exposure_time))))
            return self._cursor.lastrowid

    def hazard_exposure_time_rel(self, hazard_id, exposure_time_id):
        """

        """
        sqlquery = """
                    INSERT IGNORE INTO hazmodel_exptimes
                    (id_hazard_model, id_exposure_time)
                        VALUES({0}, {1})"""
        return self._cursor.execute(sqlquery.format(hazard_id, exposure_time_id))


    def volcano_get_insert_id(self, volcano):
        sqlquery = "SELECT id FROM volcanos WHERE name = '{0}'"
        self._cursor.execute(sqlquery.format(volcano.upper()))
        id = self._cursor.fetchone()
        if id:
            return id[0]
        else:
            sqlquery = "INSERT INTO volcanos (name) VALUES('{0}')"
            self._cursor.execute(sqlquery.format(volcano.upper()))
            return self._cursor.lastrowid

    def hazard_volcano_rel(self, hazard_id, volcano_id):
        """

        """
        sqlquery = """
                    INSERT IGNORE INTO hazmodel_volcano
                    (id_hazard_model, id_volcano)
                        VALUES({0}, {1})"""
        return self._cursor.execute(sqlquery.format(hazard_id, volcano_id))

    def hazardmodel_get_insert_id(self, id_phen,
                                  id_datagrid, name, date='0'):
        sqlquery = "SELECT id FROM hazard_models WHERE name = '{0}'"
        self._cursor.execute(sqlquery.format(name.upper()))
        id = self._cursor.fetchone()
        if id:
            return id[0]
        else:
            sqlquery = """
                    INSERT INTO hazard_models (id_phenomenon, id_datagrid,
                                        name, date) VALUES({0}, {1}, '{2}', {3})
                    """
            self._cursor.execute(sqlquery.format(id_phen, id_datagrid,
                                                 name.upper(), date))
            return self._cursor.lastrowid

    def volcanic_data_insert(self, hazard_model_id, datagrid_id,
                             stat_id, exptime_id, points, curves):
        points_idlist = self.pointsid_list(points)
        point_curve_map = zip(points_idlist, [", ".join(str(x))
                                                for x in curves])
        sqlquery = """
                    INSERT IGNORE INTO volcanic_data (id_hazard_model,
                        id_point, id_grid, id_statistic, id_exposure_time,
                        hazard_curve) VALUES ( """ + str(hazard_model_id) + """
                        , %s, """ + str(datagrid_id) + ", " + str(
            stat_id) + ","  + str(exptime_id) + """, %s )"""
        return self._cursor.executemany(sqlquery, point_curve_map)


    def seismic_data_insert(self, hazard_model_id, datagrid_id,
                            stat_id, exptime_id, points, curves):
        points_idlist = self.pointsid_list(points)
        point_curve_map = zip(points_idlist, [", ".join(str(x))
                                                for x in curves])
        sqlquery = """
                    INSERT IGNORE INTO seismic_data (id_hazard_model,
                        id_point, id_grid, id_statistic, id_exposure_time,
                        hazard_curve) VALUES ( """ + str(hazard_model_id) + \
                   """, %s, """ + str(datagrid_id) + ", " + str(stat_id) + \
                        ", " + str(exptime_id) + """, %s )
                   """
        return self._cursor.executemany(sqlquery, point_curve_map)

    def db_create(self, datadir, percpattern, datagridfile_path,
                  **createDBDetails):
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

        createDBdata = {}

        # Read, build and insert datagrid in  the db
        datagrid_name, datagrid_ext = os.path.splitext(os.path.basename(
            datagridfile_path))
        datagrid_points = get_gridpoints_from_file(datagridfile_path)
        newpoints = self.points_insert(datagrid_points)
        pointsid_list = self.pointsid_list(datagrid_points)
        datagrid_id = self.datagrid_get_insert_id(datagrid_name)
        rel_tmp = self.datagrid_points_insert(datagrid_id, datagrid_points)

        print "Filename: %s , datagrid name: %s , id: %s" \
              % (os.path.basename(datagridfile_path),
                 datagrid_name,
                 datagrid_id)
        print "Read points: %s , new points inserted: %s, new rels: %s" \
              % (len(datagrid_points),
                 newpoints,
                 rel_tmp)


        # Read and parse percentiles field
        if percpattern.find(":") != -1:
            perc_start, perc_end, perc_step = percpattern.split(":")
            createDBdata['perc_list'] = range(int(perc_start), int(perc_end)
                                              + 1,
                                              int(perc_step))
        elif percpattern.find(",") != -1:
            createDBdata['perc_list'] = [int(i) for i in
                                         percpattern.split(",")]
        else:
            raise Exception("Input in percentiles field is not correct")

        # print "perc_list: %s " % (createDBdata['perc_list'])

        # Extract infos from directory tree
        createDBdata['phenomena'] = os.listdir(datadir)
        # print "phenomena: %s " % (createDBdata['phenomena'])

        createDBdata['hazard_models'] = []
        for phen in createDBdata['phenomena']:
            item_tmp = {'phenomenon_name': phen,
                        'phenomenon_id': self.phenomenon_get_insert_id(phen)}
            item_tmp['models'] = []
            for model in os.listdir(os.path.join(datadir, phen)):
                model_tmp = {'name': model}
                model_tmp['dtimes'] = []
                model_tmp['dtime_dirs'] = []
                for dtime in os.listdir(os.path.join(datadir, phen, model)):
                    model_tmp['dtimes'].append(dtime.replace("dt", "").zfill(3))
                    model_tmp['dtime_dirs'].append(dtime)
                item_tmp['models'].append(model_tmp)
            createDBdata['hazard_models'].append(item_tmp)

        print "Hazard models to populate\n%s " % createDBdata['hazard_models']

        # Build regular expression for percentiles
        # createDBdata['perc_list'] = [10, 20 ]
        perc_re = "|".join(["percentile-"+str(p) for p in
                                        createDBdata['perc_list']])
        perc_re = '(mean|' + perc_re + ')' if perc_re else  '(mean)'
        perc_re = 'hazardcurve-'+perc_re+'.xml'

        # Walk in data tree and Parse files matching my reg_exps
        for phen in createDBdata['hazard_models']:
            # print "phen['phenomenon_name'] %s" % phen['phenomenon_name']
            for mod in phen['models']:
                # print "mod['name'] %s" % mod['name']
                for dtime_dir_i in range(len(mod['dtime_dirs'])):
                    dtime_dir = mod['dtime_dirs'][dtime_dir_i]
                    dtime = mod['dtimes'][dtime_dir_i]
                    # print "timedir %s" % dtime_dir
                    # print "dtime %s" % dtime
                    dir_tmp = os.path.join(datadir, phen['phenomenon_name'],
                                           mod['name'], dtime_dir)
                    for filename in os.listdir(dir_tmp):
                        if re.match(perc_re, filename):
                            fileXmlModel =  HazardModel(os.path.join(dir_tmp,
                                                                     filename),
                                                        phen['phenomenon_name'])
                            # Foreign keys are already defined
                            # Now insert hazard, after this other
                            # many-to-many relationship
                            print "DB > Creating hazarm_models entry"
                            hazard_model_id = self.hazardmodel_get_insert_id(
                                phen['phenomenon_id'],
                                datagrid_id,
                                mod['name'])


                            # Data in hazmodel_intensities
                            # print "fileXmlModel.iml_imt: %s" % \
                            #       fileXmlModel.iml_imt
                            print "DB > Inserting intensities"
                            imt_id = db.intensity_measure_unit_get_insert_id(
                                fileXmlModel.iml_imt)
                            db.intensity_thresholds_insert(
                                fileXmlModel.iml_thresholds, imt_id)
                            iml_thres = db.intensity_thresholds_idlist(imt_id,
                                fileXmlModel.iml_thresholds)
                            db.hazard_thresholds_rel(hazard_model_id,
                                                   iml_thres)

                            # Data in hazmodel_statistics
                            print "DB > Inserting statistics"
                            stat_id = db.statistic_get_insert_id(
                                fileXmlModel.statistic,
                                fileXmlModel.percentile_value)

                            db.hazard_statistic_rel(hazard_model_id,
                                                   stat_id)

                            # Data in hazmodel_exptimes
                            # TODO: dtime potrebbe essere chiamato exp_time?
                            print "DB > Inserting exposure times"
                            exptime_id = db.exposure_time_get_insert_id(
                                fileXmlModel.dtime)
                            db.hazard_exposure_time_rel(hazard_model_id,
                                                        exptime_id)

                            # Data in hazmodel_volcano
                            if fileXmlModel.phenomenon == "VOLCANIC":
                                volcano_id = db.volcano_get_insert_id(
                                fileXmlModel.volcano)
                                db.hazard_volcano_rel(hazard_model_id,
                                                        volcano_id)
                                print "DB > Inserting volcanic hazard data: " \
                                      "hazard_model id: %s \n" \
                                      "datagrid_id %s \n" \
                                      "stat_id %s \n" \
                                      "exptime id: %s \n" \
                                      "points_id_len: %s \n" \
                                      "points_value_len: %s \n" \
                                      % (
                                    hazard_model_id,
                                    datagrid_id,
                                    stat_id,
                                    exptime_id,
                                    len(points_to_latlon(
                                        fileXmlModel.points_coords)),
                                    len(fileXmlModel.points_values)
                                )

                                db.volcanic_data_insert(
                                    hazard_model_id,
                                    datagrid_id,
                                    stat_id,
                                    exptime_id,
                                    points_to_latlon(
                                        fileXmlModel.points_coords),
                                    fileXmlModel.points_values
                                )
                            elif fileXmlModel.phenomenon == "SEISMIC":
                                print "DB > Inserting seismic hazard data: " \
                                      "hazard_model id: %s \n" \
                                      "datagrid_id %s \n" \
                                      "stat_id %s \n" \
                                      "exptime id: %s \n" \
                                      "points_id_len: %s \n" \
                                      "points_value_len: %s \n" \
                                      % (
                                    hazard_model_id,
                                    datagrid_id,
                                    stat_id,
                                    exptime_id,
                                    len(points_to_latlon(
                                        fileXmlModel.points_coords)),
                                    len(fileXmlModel.points_values)
                                )

                                db.seismic_data_insert(
                                    hazard_model_id,
                                    datagrid_id,
                                    stat_id,
                                    exptime_id,
                                    points_to_latlon(
                                        fileXmlModel.points_coords),
                                    fileXmlModel.points_values
                                )
                            else:
                                print "Phenomena not (yet?) implemented"
                            del fileXmlModel




        return

        for phen in createDBdata['phenomena']:
            print self.phenomenon_get_insert_id(phen)
            # TODO: DA QUI IN POI
            self.hazardmodel_get_insert_id(self.phenomenon_get_insert_id(phen),
            )

            # createDBdata['dtime'] = []
            # createDBdata['dtimefold'] = []
            #
            # for ind, haz in enumerate(createDBdata['hazards']):
            #     print 'hpath-->', createDBDetails['haz_path']
            #     print 'haz-->', haz
            #     createDBdata['models'].append(os.listdir(
            #         os.path.join(createDBDetails['haz_path'], haz)))
            #     for mod in createDBdata['models'][ind]:
            #         if (os.path.isdir(os.path.join(createDBDetails['haz_path'],
            #                                        haz, mod))
            #             and (os.listdir(os.path.join(createDBDetails['haz_path'],
            #                                          haz, mod)))):
            #             tmp = os.listdir(os.path.join(createDBDetails['haz_path'],
            #                                           haz, mod))
            #             createDBdata['dtimefold'].append(tmp)
            #
            #             dtime_tmp = [str(tmp[i].replace("dt", "")).zfill(3)
            #                          for i in range(len(tmp))]
            #             createDBdata['dtime'].append(dtime_tmp)
            #
            # createDBdata['nt'] = max([len(createDBdata['dtime'][i])
            #                for i in range(len(createDBdata['dtime']))])
            #
            # print createDBdata['hazards']
            # print createDBdata['models']
            # print createDBdata['dtime']
            #
            # percpattern = str(createDBDetails['haz_perc'])  # selected percentiles
            #
            # if (percpattern.find(":") != -1):
            #     ii, ff, dd = percpattern.split(":")
            #     createDBdata['perc'] = range(int(ii), int(ff) + int(dd), int(dd))
            # elif (percpattern.find(",") != -1):
            #     val = percpattern.split(",")
            #     createDBdata['perc'] = [int(val[i]) for i in range(len(val))]
            # else:
            #     raise Exception("Input in percentiles field is not correct")
            #
            # self._db = db.BymurDB(db_host=createDBDetails['db_host'],
            #                          db_port=createDBDetails['db_port'],
            #                          db_user=createDBDetails['db_user'],
            #                          db_password=createDBDetails['db_password'],
            #                          db_name=createDBDetails['db_name'])
            #
            #
            # # comment the following two lines if DB tables exist and are populated
            # self._db.createTables(createDBdata['models'])
            #
            # self._db.genInfoPop( createDBDetails['map_path'],
            #                         createDBdata['limits'])
            #
            # createDBdata['npts'] = self._db.spatDataPop(createDBDetails['grid_path'])
            #
            # self._db.hazTabPop(
            #     createDBdata['perc'],
            #     createDBdata['hazards'],
            #     createDBdata['models'],
            #     createDBdata['dtime'],
            #     createDBDetails['haz_path'],
            #     createDBdata['npts'],
            #     createDBdata['dtimefold'])

    def close(self):
        self._connection.close()


db = BymurDB()
db.db_create('/hades/dev/bymur-data/test', '10:100:10',
             '/hades/dev/bymur/data/naples-grid.txt')
# db.commit()
# db.close()

# x = HazardModel('/hades/dev/bymur-data/hazard-xml/volcanic/BET1_ES11/dt50'
#                 '/hazardcurve-percentile-10.xml')
#
# print points_to_latlon(x.points_coords)

print "Terminato, ho!"