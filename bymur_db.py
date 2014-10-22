#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
  Bymur Software computes Risk and Multi-Risk associated to Natural Hazards.
  In particular this tool aims to provide a final working application for
  the city of Naples, considering three natural phenomena, i.e earthquakes,
  volcanic eruptions and tsunamis.
  The tool is the final product of BYMUR, an Italian project funded by the
  Italian Ministry of Education (MIUR) in the frame of 2008 FIRB, Futuro in
  Ricerca funding program.

  Copyright(C) 2012 Roberto Tonini and Jacopo Selva

  This file is part of BYMUR software.

  BYMUR is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  BYMUR is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with BYMUR. If not, see <http://www.gnu.org/licenses/>.

'''

import os
import re
import MySQLdb as mdb
import bymur_functions as bf


class BymurDB(object):
    _sql_schema = """

    """

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

    def get_datagrid_id_by_name(self, name):
        sqlquery = "SELECT id FROM datagrids WHERE name = '{0}'"
        self._cursor.execute(sqlquery.format(name.upper()))
        id = self._cursor.fetchone()
        if id:
            return id[0]
        else:
            return 0

    def get_datagrid_name_by_id(self, id):
        sqlquery = "SELECT name FROM datagrids WHERE id = {0}"
        self._cursor.execute(sqlquery.format(id))
        id = self._cursor.fetchone()
        if id:
            return id[0]
        else:
            return 0

    def get_datagrids_list(self):
        sqlquery = "SELECT id, name FROM datagrids"
        self._cursor.execute(sqlquery)
        return [dict(zip(('datagrid_id', 'datagrid_name'), phen))
                for phen in self._cursor.fetchall()]

    def insert_id_datagrid(self, name):

        sqlquery = "SELECT id FROM datagrids WHERE name = '{0}'"
        self._cursor.execute(sqlquery.format(name.upper()))
        id = self._cursor.fetchone()
        if id:
            return id[0]
        else:
            sqlquery = "INSERT INTO datagrids (name) VALUES('{0}')"
            self._cursor.execute(sqlquery.format(name.upper()))
            return self._cursor.lastrowid

    def insert_datagrid_points_rels(self, datagrid_id, points_id_list):
        """

        """
        sqlquery = """
                    INSERT IGNORE INTO grid_points (id_datagrid, id_point)
                        VALUES(""" + str(datagrid_id) + """, %s)"""
        return self._cursor.executemany(sqlquery, [(id,) for id
                                                   in points_id_list])

    def get_points_by_datagrid_id(self, datagrid_id):
        sqlquery = """ SELECT `p`.`id`, `p`.`easting`, `p`.`northing`,
            `p`.`zone_number`,  `p`.`zone_letter`
            FROM `points` p LEFT JOIN `grid_points` gp ON  p.`id`=gp.`id_point`
            WHERE gp.`id_datagrid`= %s
        """
        sqlquery %= str(datagrid_id)
        self._cursor.execute(sqlquery)
        return [dict(zip(['id', 'easting', 'northing',
                          'zone_number', 'zone_letter'], x))
                for x in self._cursor.fetchall()]

    def get_hazard_models_list(self):
        sqlquery = """
                    SELECT `haz`.`id` as `haz_id`,
                            `haz`.`name` as `haz_name`,
                            `haz`.`exposure_time` as `exp_time`,
                            `haz`.`iml` as `iml`,
                            `haz`.`imt` as `imt`,
                            `haz`.`date` as `date`,
                            `phen`.`id` as `id_phenomenon`,
                            `phen`.`name` as `phenomenon_name`,
                            `haz`.`id_datagrid` as `grid_id`,
                            `grid`.`name` as `grid_name`
                    FROM (`hazard_models` haz LEFT JOIN `phenomena` phen
                    ON `haz`.`id_phenomenon`=`phen`.`id`)
                        JOIN `datagrids` grid WHERE
                        `haz`.`id_datagrid`=`grid`.`id`
                """
        self._cursor.execute(sqlquery)
        return [dict(zip(['hazard_id', 'hazard_name', 'exposure_time', 'iml',
                          'imt', 'date', 'phenomenon_id',
                          'phenomenon_name', 'grid_id', 'grid_name'], x))
                for x in self._cursor.fetchall()]


    def insert_datagrid_points(self, datagrid_id, points):
        """
        """

        # # Insert grid if it doesn't exists
        # datagrid_id = self.datagrid_get_insert_id(datagrid_name)
        # Insert points
        # print "Point insert result: %s" % self.points_insert(points)
        # Get list of points id
        pointsid_list = self.get_pointsid_list_by_coords(points)
        # print "Points id list: %s " % pointsid_list
        # Associate grid with points
        return self.insert_datagrid_points_rels(datagrid_id, pointsid_list)


    def insert_utm_points(self, points):
        """
        Insert multiple point in table 'points' if they don't already exist
        :param points: list of point dictionaries
        :return: number of new points inserted
        """
        sqlquery = """
                    INSERT IGNORE INTO points (easting,
                                        northing, zone_number, zone_letter)
                        VALUES(%(easting)s, %(northing)s,
                        %(zone_number)s, %(zone_letter)s)
                    """
        return self._cursor.executemany(sqlquery, points)

    def get_pointsid_list_by_coords(self, points):
        """
        Get points id list from table 'point'
        :param points: list of point dictionaries
        :return:
        """

        # print points
        sqlquery = """
                    SELECT id FROM points WHERE (easting, northing,
                                zone_number, zone_letter)
                        IN (%s)
                    """
        if len(points) < 1:
            return -1
        points_list = ', '.join([str((x['easting'], x['northing'],
                                      x['zone_number'], x['zone_letter'])) for
                                 x in
                                 points])
        sqlquery %= points_list
        self._cursor.execute(sqlquery)
        return [item[0] for item in self._cursor.fetchall()]

    def insert_id_phenomenon(self, phenomenon_name):

        sqlquery = "SELECT id FROM phenomena WHERE name = '{0}'"
        self._cursor.execute(sqlquery.format(phenomenon_name.upper()))
        id = self._cursor.fetchone()
        if id:
            return id[0]
        else:
            sqlquery = "INSERT INTO phenomena (name) VALUES('{0}')"
            self._cursor.execute(sqlquery.format(phenomenon_name.upper()))
            return self._cursor.lastrowid

    def get_phenomena_list(self):
        sqlquery = "SELECT id, name FROM phenomena"
        self._cursor.execute(sqlquery)
        return [dict(zip(('phenomenon_id', 'phenomenon_name'), phen))
                for phen in self._cursor.fetchall()]

    def get_phenomenon_by_id(self, phenomeon_id):
        sqlquery = """ SELECT `ph`.`id`, `ph`.`name`
            FROM `phenomena` `ph`  WHERE `ph`.`id`= '{0}'
        """
        self._cursor.execute(sqlquery.format(phenomeon_id))
        return dict(zip(['id', 'name'], self._cursor.fetchone()))

    def insert_id_statistic(self, statistic,
                                percentile_value):
        sqlquery = "SELECT id FROM statistics WHERE name = '{0}'"
        if percentile_value != '0':
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

    def get_statistic_by_value(self, statistic_name):
        sqlquery = """ SELECT `st`.`id`
            FROM `statistics` `st`  WHERE `st`.`name`= '{0}'
        """
        # sqlquery %= str(statistic_name)
        self._cursor.execute(sqlquery.format(statistic_name))
        return self._cursor.fetchone()[0]

    def get_statistics_by_haz(self, haz_id):
        sqlquery = """ SELECT `st`.`id`, `st`.`name`
            FROM `hazmodel_statistics` `haz_stat` LEFT JOIN
            `statistics` `st` ON
            `haz_stat`.`id_statistic`=`st`.`id`
            WHERE `haz_stat`.`id_hazard_model`= %s
        """
        sqlquery %= str(haz_id)
        self._cursor.execute(sqlquery)
        return [dict(zip(['id', 'name'], (x[0], x[1])))
                for x in self._cursor.fetchall()]

    def insert_hazard_statistic_rel(self, hazard_id, statistic_id):
        """

        """
        sqlquery = """
                    INSERT IGNORE INTO hazmodel_statistics
                    (id_hazard_model, id_statistic)
                        VALUES ({0}, {1})"""
        return self._cursor.execute(sqlquery.format(hazard_id, statistic_id))

    def get_volcanos_list(self, haz_id):
        sqlquery = """ SELECT `vol`.`id`, `vol`.`name`
            FROM `hazmodel_volcanos` `haz_vol` LEFT JOIN
            `volcanos` `vol` ON
            `haz_vol`.`id_volcano`=`vol`.`id`
            WHERE `haz_vol`.`id_hazard_model`= %s
        """
        sqlquery %= str(haz_id)
        self._cursor.execute(sqlquery)
        return [dict(zip(['id', 'name'], x))
                for x in self._cursor.fetchall()]

    def insert_id_volcano(self, volcano):
        sqlquery = "SELECT id FROM volcanos WHERE name = '{0}'"
        self._cursor.execute(sqlquery.format(volcano.upper()))
        id = self._cursor.fetchone()
        if id:
            return id[0]
        else:
            sqlquery = "INSERT INTO volcanos (name) VALUES('{0}')"
            self._cursor.execute(sqlquery.format(volcano.upper()))
            return self._cursor.lastrowid

    def insert_hazard_volcano_rel(self, hazard_id, volcano_id):
        """

        """
        sqlquery = """
                    INSERT IGNORE INTO hazmodel_volcanos
                    (id_hazard_model, id_volcano)
                        VALUES({0}, {1})"""
        return self._cursor.execute(sqlquery.format(hazard_id, volcano_id))

    def insert_id_hazard_model(self, id_phen, id_datagrid, name,
                               exp_time, iml, imt, date='0'):
        sqlquery = """SELECT id FROM hazard_models
                   WHERE name = '{0}' AND exposure_time = '{1}'
                   """
        self._cursor.execute(sqlquery.format(name.upper(), exp_time))
        id = self._cursor.fetchone()
        if id:
            return id[0]
        else:
            sqlquery = """
                    INSERT INTO hazard_models (id_phenomenon, id_datagrid,
                                        name, exposure_time, iml, imt, date)
                                        VALUES({0}, {1}, '{2}', '{3}', '{4}',
                                        '{5}', {6})
                    """
            self._cursor.execute(sqlquery.format(id_phen, id_datagrid,
                                                 name.upper(), exp_time,
                                                 iml, imt, date))
            return self._cursor.lastrowid

    def get_hazard_model_by_id(self, haz_id):
        sqlquery = """ SELECT `haz_mod`.`id`,
                    `haz_mod`.`id_phenomenon`,
                    `haz_mod`.`id_datagrid`,
                    `haz_mod`.`name`,
                    `haz_mod`.`exposure_time`,
                    `haz_mod`.`iml`,
                    `haz_mod`.`imt`,
                    `haz_mod`.`date`
            FROM `hazard_models` `haz_mod`
            WHERE `haz_mod`.`id`= %s
        """
        sqlquery %= str(haz_id)
        self._cursor.execute(sqlquery)
        return dict(zip(['hazard_id', 'phenomenon_id', 'datagrid_id',
                         'hazard_name', 'exposure_time', 'iml', 'imt', 'date'],
                        self._cursor.fetchone()))

    # TODO: sistemare questa
    def get_hazard_model_by_name_exptime(self, haz_name, exp_time):
        sqlquery = """ SELECT `haz_mod`.`id`,
                    `haz_mod`.`id_phenomenon`,
                    `haz_mod`.`id_datagrid`,
                    `haz_mod`.`name`,
                    `haz_mod`.`exposure_time`,
                    `haz_mod`.`iml`,
                    `haz_mod`.`imt`,
                    `haz_mod`.`date`
            FROM `hazard_models` `haz_mod`
            WHERE `haz_mod`.`name`= '%s' AND  `haz_mod`.`exposure_time`= '%s'
        """
        sqlquery %= (str(haz_name.upper()), str(exp_time))
        self._cursor.execute(sqlquery)
        return dict(zip(['hazard_id', 'phenomenon_id', 'datagrid_id',
                         'hazard_name', 'exposure_time', 'iml', 'imt', 'date'],
                        self._cursor.fetchone()))

    def insert_hazard_data(self, phenomenon, hazard_model_id, stat_id,
                           points, curves):

        if phenomenon == 'VOLCANIC':
            table_name = "volcanic_data"
        elif phenomenon == 'SEISMIC':
            table_name = "seismic_data"
        elif phenomenon == 'TSUNAMIC':
            table_name = "tsunamic_data"

        points_idlist = self.get_pointsid_list_by_coords(points)
        point_curve_map = zip(points_idlist,
                              [", ".join(map(str, x)) for x in curves])
        sqlquery = """
                    INSERT IGNORE INTO `{0}` (id_hazard_model,
                        id_point, id_statistic, hazard_curve)
                        VALUES ( """ + str(hazard_model_id) + """
                        , %s, """ + str(stat_id) + """, %s )"""

        sqlquery = sqlquery.format(table_name)
        return self._cursor.executemany(sqlquery, point_curve_map)

    def insert_volcanic_data(self, hazard_model_id, stat_id, points, curves):
        return self.insert_hazard_data('VOLCANIC', hazard_model_id, stat_id,
                                       points, curves)

    def insert_seismic_data(self, hazard_model_id, stat_id, points, curves):
        return self.insert_hazard_data('SEISMIC', hazard_model_id, stat_id,
                                       points, curves)

    def get_point_all_curves(self, phenomenon_id, hazard_id, point_id):
        phenomenon = self.get_phenomenon_by_id(phenomenon_id)
        if phenomenon['name'] == 'VOLCANIC':
            table_name = "volcanic_data"
        elif phenomenon['name'] == 'SEISMIC':
            table_name = "seismic_data"
        elif phenomenon['name'] == 'TSUNAMIC':
            table_name = "tsunamic_data"
        else:
            return None
        sqlquery = """
                    SELECT `st`.`name`,
                       `dt`.`hazard_curve`
                    FROM `{0}` `dt` JOIN `statistics` `st` ON
                        `dt`.`id_statistic` = `st`.`id`
                    WHERE `dt`.`id_hazard_model`={1} AND
                     `dt`.`id_point`={2}
        """
        query = sqlquery.format(table_name, hazard_id, point_id)
        self._cursor.execute(query)
        res = self._cursor.fetchall()
        return dict(res)

    def get_curves(self, phenomenon_id, hazard_model_id, stat_id):
        phenomenon = self.get_phenomenon_by_id(phenomenon_id)
        if phenomenon['name'] == 'VOLCANIC':
            table_name = "volcanic_data"
        elif phenomenon['name'] == 'SEISMIC':
            table_name = "seismic_data"
        elif phenomenon['name'] == 'TSUNAMIC':
            table_name = "tsunamic_data"
        else:
            return None

        sqlquery = """ SELECT `p`.`id`, `p`.`easting`, `p`.`northing`,
                        `p`.`zone_number`, `p`.`zone_letter`,
                        `d`.`hazard_curve` FROM
            `{0}` `d` LEFT JOIN `points` `p`
             ON `d`.`id_point`=`p`.`id`
             WHERE `d`.`id_hazard_model`= {1}
             AND `d`.`id_statistic` = {2}
        """
        self._cursor.execute(sqlquery.format(table_name,
                                             hazard_model_id,
                                             stat_id))
        return [dict(zip(['point', 'curve'],
                         (dict(zip(['id', 'easting', 'northing',
                                    'zone_number', 'zone_letter'],
                                   (x[0], x[1], x[2], x[3], x[4]))),
                          ([float(a) for a in x[5].split(',')]))))
                for x in self._cursor.fetchall()]

    def create(self):
        # TODO: create DB for real!
        print "create"


    def load_grid(self, datagridfile_path):
        datagrid_name, datagrid_ext = os.path.splitext(os.path.basename(
            datagridfile_path))
        datagrid_points = bf.get_gridpoints_from_file(datagridfile_path)
        newpoints = self.insert_utm_points(datagrid_points)
        datagrid_id = self.insert_id_datagrid(datagrid_name)
        rel_tmp = self.insert_datagrid_points(datagrid_id, datagrid_points)

        print "Filename: %s , datagrid name: %s , id: %s" \
              % (os.path.basename(datagridfile_path),
                 datagrid_name,
                 datagrid_id)
        print "Read points: %s , new points inserted: %s, new rels: %s" \
              % (len(datagrid_points),
                 newpoints,
                 rel_tmp)
        return datagrid_name


    def add_data(self, datagrid_name, haz_files, phenomenon_name):
        """

        """
        datagrid_id = self.insert_id_datagrid(datagrid_name)
        print " datagrid name: %s , id: %s" \
              % (datagrid_name, datagrid_id)

        phenomenon_id = self.insert_id_phenomenon(phenomenon_name)
        print " phenomenon name: %s , id: %s" \
              % (phenomenon_name, phenomenon_id)

        for hazFile in haz_files:
            try:
                fileXmlModel = bf.HazardXMLModel(hazFile, phenomenon_name)
            except Exception as e:
                print "ERROR: %s is not a valid ByMuR file! %s" \
                      "Skipping to next one" % (hazFile, str(e))
                continue
            # Foreign keys are already defined
            # Now insert hazard, after this other
            # many-to-many relationship
            print "DB > Creating hazarm_models entry"
            hazard_model_id = self.insert_id_hazard_model(
                phenomenon_id,
                datagrid_id,
                fileXmlModel.model_name,
                fileXmlModel.exp_time,
                fileXmlModel.iml_thresholds,
                fileXmlModel.iml_imt)

            # Data in hazmodel_statistics
            print "DB > Inserting statistics"
            stat_id = self.insert_id_statistic(
                fileXmlModel.statistic,
                fileXmlModel.percentile_value)

            self.insert_hazard_statistic_rel(hazard_model_id,
                                      stat_id)

            print "DB > Inserting hazard data: " \
                  "phenomenon: %s \n" \
                  "hazard_model_id: %s \n" \
                  "datagrid_id: %s \n" \
                  "stat_id: %s \n" \
                  "exp_time : %s \n" \
                  "iml : %s \n" \
                  "imt : %s \n" \
                  "points_id_len: %s \n" \
                  "points_value_len: %s \n" \
                  % (
                fileXmlModel.phenomenon,
                hazard_model_id,
                datagrid_id,
                stat_id,
                fileXmlModel.exp_time,
                fileXmlModel.iml_thresholds,
                fileXmlModel.iml_imt,
                len(fileXmlModel.points_coords),
                len(fileXmlModel.points_values)
            )

            self.insert_hazard_data(fileXmlModel.phenomenon,
                                    hazard_model_id,
                                    stat_id,
                                    fileXmlModel.points_coords,
                                    fileXmlModel.points_values)
            del fileXmlModel
        return True

    def drop_tables(self):
        query = "SHOW TABLES"
        self._cursor.execute(query)
        tables = self._cursor.fetchall()
        query = "DROP TABLE %s"
        self._cursor.executemany(query, tables)

    def close(self):
        self._connection.close()


    # TODO: da eliminare modificando prima il codice

    # def intensity_measure_unit_get_insert_id(self, unit_name):
    #     sqlquery = """
    #                 SELECT id FROM intensity_measure_unit
    #                 WHERE measure_unit_text = '{0}'
    #                """
    #     # print sqlquery.format(unit_name)
    #     self._cursor.execute(sqlquery.format(unit_name))
    #     id = self._cursor.fetchone()
    #     if id:
    #         return id[0]
    #     else:
    #         sqlquery = """
    #                     INSERT INTO intensity_measure_unit (measure_unit_text)
    #                     VALUES('{0}')
    #                    """
    #         # print sqlquery.format(unit_name)
    #         self._cursor.execute(sqlquery.format(unit_name))
    #         return self._cursor.lastrowid

    # def get_intensity_measure_unit_by_haz(self, haz_id):
    #     sqlquery = """ SELECT `imu`.`measure_unit_text`
    #         FROM (`hazmodel_intensities` `haz_int` LEFT JOIN
    #         `intensity_thresholds` `it` ON
    #         `haz_int`.`id_intensity_threshold`=`it`.`id`)
    #             LEFT JOIN `intensity_measure_unit` `imu` ON
    #                 `it`.`id_unit` = `imu`.`id`
    #         WHERE `haz_int`.`id_hazard_model`= %s LIMIT 1
    #     """
    #     sqlquery %= str(haz_id)
    #     self._cursor.execute(sqlquery)
    #     return self._cursor.fetchone()[0]


    # def intensity_thresholds_insert(self, int_thres, imt_id):
    #     """
    #     """
    #     sqlquery = """
    #                 INSERT IGNORE INTO intensity_thresholds (value,
    #                     id_unit) VALUES( %s, """ + str(imt_id) + """)"""
    #
    #     # print sqlquery
    #     # print int_thres
    #
    #     return self._cursor.executemany(sqlquery, [(val,) for val
    #                                                in int_thres])

    # def intensity_thresholds_idlist(self, imt_id, iml_thresholds):
    #     """
    #     """
    #
    #     sqlquery = """
    #                 SELECT id FROM intensity_thresholds WHERE
    #                 (value) IN (%s) AND id_unit=""" + str(imt_id)
    #
    #     if len(iml_thresholds) < 1:
    #         return -1
    #         # print iml_thresholds
    #     iml_thresh_list = ', '.join([str(y) for y in [float(x)
    #                                                   for x in
    #                                                   iml_thresholds]])
    #     sqlquery %= iml_thresh_list
    #     self._cursor.execute(sqlquery)
    #     return [item[0] for item in self._cursor.fetchall()]

    # def hazard_thresholds_rel(self, hazard_id, thresholds_id_list):
    #     """
    #
    #     """
    #     sqlquery = """
    #                 INSERT IGNORE INTO hazmodel_intensities
    #                 (id_hazard_model, id_intensity_threshold)
    #                     VALUES(""" + str(hazard_id) + """, %s)"""
    #     return self._cursor.executemany(sqlquery, [(id,) for id
    #                                                in thresholds_id_list])

    # def get_intensity_threshods_by_haz(self, haz_id):
    #
    #     sqlquery = """ SELECT `it`.`value`
    #         FROM `hazmodel_intensities` `haz_int` LEFT JOIN
    #         `intensity_thresholds` `it` ON
    #         `haz_int`.`id_intensity_threshold`=`it`.`id`
    #         WHERE `haz_int`.`id_hazard_model`= %s ORDER BY `it`.`value`
    #     """
    #     sqlquery %= str(haz_id)
    #     self._cursor.execute(sqlquery)
    #     return [float(item[0]) for item in self._cursor.fetchall()]

    # def get_exposure_times_by_haz(self, haz_id):
    #     sqlquery = """ SELECT `et`.`id`, `et`.`years`
    #         FROM `hazmodel_exptimes` `haz_exp` LEFT JOIN
    #         `exposure_times` `et` ON
    #         `haz_exp`.`id_exposure_time`=`et`.`id`
    #         WHERE `haz_exp`.`id_hazard_model`= %s
    #     """
    #     sqlquery %= str(haz_id)
    #     self._cursor.execute(sqlquery)
    #     return [dict(zip(['id', 'years'], (x[0], int(x[1]))))
    #             for x in self._cursor.fetchall()]

    # def get_exposure_time_by_value(self, exp_time_value):
    #     sqlquery = """ SELECT `et`.`id`
    #         FROM `exposure_times` `et`
    #         WHERE `et`.`years`= %s
    #     """
    #     sqlquery %= str(exp_time_value)
    #     self._cursor.execute(sqlquery)
    #     return self._cursor.fetchone()[0]


    # def exposure_time_get_insert_id(self, exposure_time):
    #     sqlquery = "SELECT id FROM exposure_times WHERE years = '{0}'"
    #     self._cursor.execute(sqlquery.format(str(float(exposure_time))))
    #     id = self._cursor.fetchone()
    #     if id:
    #         return id[0]
    #     else:
    #         sqlquery = "INSERT INTO exposure_times (years) VALUES('{0}')"
    #         self._cursor.execute(sqlquery.format(str(float(exposure_time))))
    #         return self._cursor.lastrowid

    # def hazard_exposure_time_rel(self, hazard_id, exposure_time_id):
    #     """
    #
    #     """
    #     sqlquery = """
    #                 INSERT IGNORE INTO hazmodel_exptimes
    #                 (id_hazard_model, id_exposure_time)
    #                     VALUES({0}, {1})"""
    #     return self._cursor.execute(
    #         sqlquery.format(hazard_id, exposure_time_id))
