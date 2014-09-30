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
import globalFunctions as gf
import time

class BymurDB():
    _sql_schema = """
        SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";

        -- Table structure for table `datagrids`
        CREATE TABLE IF NOT EXISTS `datagrids` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `name` varchar(45) COLLATE utf8_bin NOT NULL,
          PRIMARY KEY (`id`),
          UNIQUE KEY `name_UNIQUE` (`name`)
        ) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

        -- Table structure for table `exposure_times`
        CREATE TABLE IF NOT EXISTS `exposure_times` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `years` float NOT NULL,
          PRIMARY KEY (`id`),
          UNIQUE KEY `years_UNIQUE` (`years`)
        ) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

        -- Table structure for table `grid_points`
        CREATE TABLE IF NOT EXISTS `grid_points` (
          `id_datagrid` int(11) NOT NULL,
          `id_point` bigint(20) NOT NULL,
          PRIMARY KEY (`id_datagrid`,`id_point`),
          KEY `fk_grid_points_1` (`id_datagrid`),
          KEY `fk_grid_points_2` (`id_point`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

        -- Table structure for table `hazard_models`
        CREATE TABLE IF NOT EXISTS `hazard_models` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `id_phenomenon` int(11) NOT NULL,
          `id_datagrid` int(11) NOT NULL,
          `name` varchar(45) COLLATE utf8_bin NOT NULL,
          `date` date DEFAULT NULL,
          PRIMARY KEY (`id`),
          KEY `fk_hazard_models_1` (`id_phenomenon`),
          KEY `fk_hazard_models_2` (`id_datagrid`)
        ) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

        -- Table structure for table `hazmodel_exptimes`
        CREATE TABLE IF NOT EXISTS `hazmodel_exptimes` (
          `id_hazard_model` int(11) NOT NULL,
          `id_exposure_time` int(11) NOT NULL,
          PRIMARY KEY (`id_hazard_model`,`id_exposure_time`),
          KEY `fk_hazmodels_exptimes_1` (`id_hazard_model`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

        -- Table structure for table `hazmodel_intensities`
        CREATE TABLE IF NOT EXISTS `hazmodel_intensities` (
          `id_hazard_model` int(11) NOT NULL,
          `id_intensity_threshold` int(11) NOT NULL,
          PRIMARY KEY (`id_hazard_model`,`id_intensity_threshold`),
          KEY `fk_hazmodel_intensities_1` (`id_hazard_model`),
          KEY `fk_hazmodel_intensities_2` (`id_intensity_threshold`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

        -- Table structure for table `hazmodel_statistics`
        CREATE TABLE IF NOT EXISTS `hazmodel_statistics` (
          `id_hazard_model` int(11) NOT NULL,
          `id_statistic` int(11) NOT NULL,
          PRIMARY KEY (`id_hazard_model`,`id_statistic`),
          KEY `fk_hazmodels_statistics_1` (`id_hazard_model`),
          KEY `fk_hazmodels_statistics_2` (`id_statistic`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

        -- Table structure for table `hazmodel_volcanos`
        CREATE TABLE IF NOT EXISTS `hazmodel_volcanos` (
          `id_hazard_model` int(11) NOT NULL,
          `id_volcano` int(11) NOT NULL,
          PRIMARY KEY (`id_hazard_model`,`id_volcano`),
          KEY `fk_hazmodel_volcanos_1` (`id_hazard_model`),
          KEY `fk_hazmodel_volcanos_2` (`id_volcano`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

        -- Table structure for table `intensity_measure_unit`
        CREATE TABLE IF NOT EXISTS `intensity_measure_unit` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `measure_unit_text` varchar(45) COLLATE utf8_bin NOT NULL,
          PRIMARY KEY (`id`),
          UNIQUE KEY `measure_unit_text_UNIQUE` (`measure_unit_text`)
        ) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

        -- Table structure for table `intensity_thresholds`
        CREATE TABLE IF NOT EXISTS `intensity_thresholds` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `value` float NOT NULL,
          `id_unit` int(11) NOT NULL,
          PRIMARY KEY (`id`),
          UNIQUE KEY `value` (`value`,`id_unit`),
          KEY `fk_intensity_thresholds_1` (`id_unit`)
        ) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

        -- Table structure for table `phenomena`
        CREATE TABLE IF NOT EXISTS `phenomena` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `name` varchar(45) COLLATE utf8_bin NOT NULL,
          PRIMARY KEY (`id`),
          UNIQUE KEY `name_UNIQUE` (`name`)
        ) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

        -- Table structure for table `points`
        CREATE TABLE IF NOT EXISTS `points` (
          `id` bigint(20) NOT NULL AUTO_INCREMENT,
          `latitude` double NOT NULL,
          `longitude` double NOT NULL,
          PRIMARY KEY (`id`),
          UNIQUE KEY `coords` (`latitude`,`longitude`)
        ) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

        -- Table structure for table `seismic_data`
        CREATE TABLE IF NOT EXISTS `seismic_data` (
          `id_hazard_model` int(11) NOT NULL,
          `id_point` bigint(20) NOT NULL,
          `id_grid` int(11) NOT NULL,
          `id_statistic` int(11) NOT NULL,
          `id_exposure_time` int(11) NOT NULL,
          `hazard_curve` mediumblob NOT NULL,
          PRIMARY KEY (`id_hazard_model`,`id_point`,`id_statistic`,`id_exposure_time`,`id_grid`),
          KEY `index_haz_grid_stat` (`id_hazard_model`,`id_statistic`,`id_grid`),
          KEY `fk_seismic_data_1` (`id_hazard_model`),
          KEY `fk_seismic_data_2` (`id_point`),
          KEY `fk_seismic_data_3` (`id_grid`),
          KEY `fk_seismic_data_4` (`id_statistic`),
          KEY `fk_seismic_data_5` (`id_exposure_time`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

        -- Table structure for table `statistics`
        CREATE TABLE IF NOT EXISTS `statistics` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `name` varchar(45) COLLATE utf8_bin NOT NULL,
          PRIMARY KEY (`id`),
          UNIQUE KEY `name_UNIQUE` (`name`)
        ) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

        -- Table structure for table `volcanic_data`
        CREATE TABLE IF NOT EXISTS `volcanic_data` (
          `id_hazard_model` int(11) NOT NULL,
          `id_point` bigint(20) NOT NULL,
          `id_grid` int(11) NOT NULL,
          `id_statistic` int(11) NOT NULL,
          `id_exposure_time` int(11) NOT NULL,
          `hazard_curve` mediumblob NOT NULL,
          PRIMARY KEY (`id_hazard_model`,`id_point`,`id_statistic`,`id_exposure_time`,`id_grid`),
          KEY `index_haz_grid_stat` (`id_hazard_model`,`id_statistic`,`id_grid`),
          KEY `fk_volcanic_data_1` (`id_hazard_model`),
          KEY `fk_volcanic_data_2` (`id_point`),
          KEY `fk_volcanic_data_3` (`id_grid`),
          KEY `fk_volcanic_data_4` (`id_statistic`),
          KEY `fk_volcanic_data_5` (`id_exposure_time`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

        -- Table structure for table `volcanos`
        CREATE TABLE IF NOT EXISTS `volcanos` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `name` varchar(45) COLLATE utf8_bin NOT NULL,
          PRIMARY KEY (`id`),
          UNIQUE KEY `name_UNIQUE` (`name`)
        ) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

        -- Constraints for table `grid_points`
        ALTER TABLE `grid_points`
          ADD CONSTRAINT `fk_grid_points_1` FOREIGN KEY (`id_datagrid`) REFERENCES `datagrids` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
          ADD CONSTRAINT `fk_grid_points_2` FOREIGN KEY (`id_point`) REFERENCES `points` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

        -- Constraints for table `hazard_models`
        ALTER TABLE `hazard_models`
          ADD CONSTRAINT `fk_hazard_models_1` FOREIGN KEY (`id_phenomenon`) REFERENCES `phenomena` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
          ADD CONSTRAINT `fk_hazard_models_2` FOREIGN KEY (`id_datagrid`) REFERENCES `datagrids` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

        -- Constraints for table `hazmodel_exptimes`
        ALTER TABLE `hazmodel_exptimes`
          ADD CONSTRAINT `fk_hazmodels_exptimes_1` FOREIGN KEY (`id_hazard_model`) REFERENCES `hazard_models` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

        -- Constraints for table `hazmodel_intensities`
        ALTER TABLE `hazmodel_intensities`
          ADD CONSTRAINT `fk_hazmodel_intensities_1` FOREIGN KEY (`id_hazard_model`) REFERENCES `hazard_models` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
          ADD CONSTRAINT `fk_hazmodel_intensities_2` FOREIGN KEY (`id_intensity_threshold`) REFERENCES `intensity_thresholds` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

        -- Constraints for table `hazmodel_statistics`
        ALTER TABLE `hazmodel_statistics`
          ADD CONSTRAINT `fk_hazmodels_statistics_1` FOREIGN KEY (`id_hazard_model`) REFERENCES `hazard_models` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
          ADD CONSTRAINT `fk_hazmodels_statistics_2` FOREIGN KEY (`id_statistic`) REFERENCES `statistics` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

        -- Constraints for table `hazmodel_volcanos`
        ALTER TABLE `hazmodel_volcanos`
          ADD CONSTRAINT `fk_hazmodel_volcanos_1` FOREIGN KEY (`id_hazard_model`) REFERENCES `hazard_models` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
          ADD CONSTRAINT `fk_hazmodel_volcanos_2` FOREIGN KEY (`id_volcano`) REFERENCES `volcanos` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

        -- Constraints for table `intensity_thresholds`
        ALTER TABLE `intensity_thresholds`
          ADD CONSTRAINT `fk_intensity_thresholds_1` FOREIGN KEY (`id_unit`) REFERENCES `intensity_measure_unit` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

        -- Constraints for table `seismic_data`
        ALTER TABLE `seismic_data`
          ADD CONSTRAINT `fk_seismic_data_1` FOREIGN KEY (`id_hazard_model`) REFERENCES `hazard_models` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
          ADD CONSTRAINT `fk_seismic_data_2` FOREIGN KEY (`id_point`) REFERENCES `points` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
          ADD CONSTRAINT `fk_seismic_data_3` FOREIGN KEY (`id_grid`) REFERENCES `datagrids` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
          ADD CONSTRAINT `fk_seismic_data_4` FOREIGN KEY (`id_statistic`) REFERENCES `statistics` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
          ADD CONSTRAINT `fk_seismic_data_5` FOREIGN KEY (`id_exposure_time`) REFERENCES `exposure_times` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

        -- Constraints for table `volcanic_data`
        ALTER TABLE `volcanic_data`
          ADD CONSTRAINT `fk_volcanic_data_1` FOREIGN KEY (`id_hazard_model`) REFERENCES `hazard_models` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
          ADD CONSTRAINT `fk_volcanic_data_2` FOREIGN KEY (`id_point`) REFERENCES `points` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
          ADD CONSTRAINT `fk_volcanic_data_3` FOREIGN KEY (`id_grid`) REFERENCES `datagrids` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
          ADD CONSTRAINT `fk_volcanic_data_4` FOREIGN KEY (`id_statistic`) REFERENCES `statistics` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
          ADD CONSTRAINT `fk_volcanic_data_5` FOREIGN KEY (`id_exposure_time`) REFERENCES `exposure_times` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;
    """

    def __init__(self, **kwargs):
        """
        Connecting to database
        """
        try:
            print "init"
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


    def datagrid_points_get(self, datagrid_id):
        sqlquery = """ SELECT `p`.`id`, `p`.`latitude`, `p`.`longitude`
            FROM `points` p LEFT JOIN `grid_points` gp ON  p.`id`=gp.`id_point`
            WHERE gp.`id_datagrid`= %s
        """
        sqlquery %= str(datagrid_id)
        self._cursor.execute(sqlquery)
        return [dict(zip(['id','latitude','longitude'], x))
                for x in self._cursor.fetchall()]


    def hazard_models_get(self):
        sqlquery = """
                    SELECT `haz`.`id` as `haz_id`,
                            `haz`.`name` as `haz_name`,
                            `phen`.`id` as `id_phenomenon`,
                            `phen`.`name` as `phenomenon_name`
                    FROM `hazard_models` haz LEFT JOIN `phenomena` phen
                    ON `haz`.`id_phenomenon`=`phen`.`id`
                """
        self._cursor.execute(sqlquery)
        return [dict(zip(['hazard_id','hazard_name','phenomenon_id',
                          'phenomenon_name'], x))
                for x in self._cursor.fetchall()]


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

    def get_phenomenon_by_id(self, phenomeon_id):
        sqlquery = """ SELECT `ph`.`id`, `ph`.`name`
            FROM `phenomena` `ph`  WHERE `ph`.`id`= '{0}'
        """
        self._cursor.execute(sqlquery.format(phenomeon_id))
        return dict(zip(['id','name'], self._cursor.fetchone()))

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

    def get_intensity_measure_unit_by_haz(self, haz_id):
        sqlquery = """ SELECT `imu`.`measure_unit_text`
            FROM (`hazmodel_intensities` `haz_int` LEFT JOIN
            `intensity_thresholds` `it` ON
            `haz_int`.`id_intensity_threshold`=`it`.`id`)
                LEFT JOIN `intensity_measure_unit` `imu` ON
                    `it`.`id_unit` = `imu`.`id`
            WHERE `haz_int`.`id_hazard_model`= %s LIMIT 1
        """
        sqlquery %= str(haz_id)
        self._cursor.execute(sqlquery)
        return self._cursor.fetchone()[0]


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
        """

        sqlquery = """
                    SELECT id FROM intensity_thresholds WHERE
                    (value) IN (%s) AND id_unit=""" + str(imt_id)

        if len(iml_thresholds) < 1:
            return -1
       #  print iml_thresholds
        iml_thresh_list = ', '.join([str(y) for y in [float(x)
                                                      for x in
                                                      iml_thresholds]])
        sqlquery %= iml_thresh_list
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

    def get_intensity_threshods_by_haz(self, haz_id):
        # sqlquery = """ SELECT `it`.`value`, `imu`.`measure_unit_text`
        #     FROM (`hazmodel_intensities` `haz_int` LEFT JOIN
        #     `intensity_thresholds` `it` ON
        #     `haz_int`.`id_intensity_threshold`=`it`.`id`)
        #         LEFT JOIN `intensity_measure_unit` `imu` ON
        #             `it`.`id_unit` = `imu`.`id`
        #     WHERE `haz_int`.`id_hazard_model`= %s
        # """
        sqlquery = """ SELECT `it`.`value`
            FROM `hazmodel_intensities` `haz_int` LEFT JOIN
            `intensity_thresholds` `it` ON
            `haz_int`.`id_intensity_threshold`=`it`.`id`
            WHERE `haz_int`.`id_hazard_model`= %s ORDER BY `it`.`value`
        """
        sqlquery %= str(haz_id)
        self._cursor.execute(sqlquery)
        return [float(item[0]) for item in self._cursor.fetchall()]
        # return [dict(zip(['id','value','imt'], x))
        #         for x in self._cursor.fetchall()]


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
        return [dict(zip(['id','name'], (x[0], x[1])))
                for x in self._cursor.fetchall()]


    def hazard_statistic_rel(self, hazard_id, statistic_id):
        """

        """
        sqlquery = """
                    INSERT IGNORE INTO hazmodel_statistics
                    (id_hazard_model, id_statistic)
                        VALUES ({0}, {1})"""
        return self._cursor.execute(sqlquery.format(hazard_id, statistic_id))

    def get_exposure_times_by_haz(self, haz_id):
        sqlquery = """ SELECT `et`.`id`, `et`.`years`
            FROM `hazmodel_exptimes` `haz_exp` LEFT JOIN
            `exposure_times` `et` ON
            `haz_exp`.`id_exposure_time`=`et`.`id`
            WHERE `haz_exp`.`id_hazard_model`= %s
        """
        sqlquery %= str(haz_id)
        self._cursor.execute(sqlquery)
        return [dict(zip(['id','years'], (x[0], int(x[1]))))
                for x in self._cursor.fetchall()]

    def get_exposure_time_by_value(self, exp_time_value):
        sqlquery = """ SELECT `et`.`id`
            FROM `exposure_times` `et`
            WHERE `et`.`years`= %s
        """
        sqlquery %= str(exp_time_value)
        self._cursor.execute(sqlquery)
        return self._cursor.fetchone()[0]


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

    def volcanos_list(self, haz_id):
        sqlquery = """ SELECT `vol`.`id`, `vol`.`name`
            FROM `hazmodel_volcanos` `haz_vol` LEFT JOIN
            `volcanos` `vol` ON
            `haz_vol`.`id_volcano`=`vol`.`id`
            WHERE `haz_vol`.`id_hazard_model`= %s
        """
        sqlquery %= str(haz_id)
        self._cursor.execute(sqlquery)
        return [dict(zip(['id','name'], x))
                for x in self._cursor.fetchall()]

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
                    INSERT IGNORE INTO hazmodel_volcanos
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

    def get_hazard_model_by_id(self, haz_id):
        sqlquery = """ SELECT `haz_mod`.`id`,
                    `haz_mod`.`id_phenomenon`,
                    `haz_mod`.`id_datagrid`,
                    `haz_mod`.`name`,
                    `haz_mod`.`date`
            FROM `hazard_models` `haz_mod`
            WHERE `haz_mod`.`id`= %s
        """
        sqlquery %= str(haz_id)
        self._cursor.execute(sqlquery)
        return dict(zip(['hazard_id', 'phenomenon_id', 'datagrid_id',
                         'hazard_name', 'date'], self._cursor.fetchone()))

    def get_hazard_model_by_name(self, haz_name):
        sqlquery = """ SELECT `haz_mod`.`id`,
                    `haz_mod`.`id_phenomenon`,
                    `haz_mod`.`id_datagrid`,
                    `haz_mod`.`name`,
                    `haz_mod`.`date`
            FROM `hazard_models` `haz_mod`
            WHERE `haz_mod`.`name`= '%s'
        """
        sqlquery %= str(haz_name.upper())
        self._cursor.execute(sqlquery)
        return dict(zip(['hazard_id', 'phenomenon_id', 'datagrid_id',
                         'hazard_name', 'date'], self._cursor.fetchone()))


    def hazard_data_insert(self, phenomenon, hazard_model_id, datagrid_id,
                             stat_id, exptime_id, points, curves):

        if phenomenon == 'VOLCANIC':
            table_name = "volcanic_data"
        elif phenomenon == 'SEISMIC':
            table_name = "seismic_data"
        elif phenomenon == 'TSUNAMIC':
            table_name = "tsunamic_data"

        points_idlist = self.pointsid_list(points)
        point_curve_map = zip(points_idlist,
                              [", ".join(map(str,x)) for x in curves])

        sqlquery = """
                    INSERT IGNORE INTO `{0}` (id_hazard_model,
                        id_point, id_grid, id_statistic, id_exposure_time,
                        hazard_curve) VALUES ( """ + str(hazard_model_id) + """
                        , %s, """ + str(datagrid_id) + ", " + str(
            stat_id) + ","  + str(exptime_id) + """, %s )"""

        sqlquery = sqlquery.format(table_name)
        print "point_curve_map %s " % point_curve_map
        return self._cursor.executemany(sqlquery, point_curve_map)

    def volcanic_data_insert(self, hazard_model_id, datagrid_id,
                             stat_id, exptime_id, points, curves):

        return self.hazard_data_insert('VOLCANIC', hazard_model_id,
                                       datagrid_id, stat_id, exptime_id,
                                       points, curves)
        # points_idlist = self.pointsid_list(points)
        # print "points_idlist %s " % points_idlist
        # time.sleep(5)
        # print "curves %s " % curves
        # time.sleep(5)
        # point_curve_map = zip(points_idlist,
        #                       [", ".join(map(str,x)) for x in curves])
        #
        # sqlquery = """
        #             INSERT IGNORE INTO volcanic_data (id_hazard_model,
        #                 id_point, id_grid, id_statistic, id_exposure_time,
        #                 hazard_curve) VALUES ( """ + str(hazard_model_id) + """
        #                 , %s, """ + str(datagrid_id) + ", " + str(
        #     stat_id) + ","  + str(exptime_id) + """, %s )"""
        # print "point_curve_map %s " % point_curve_map
        # return self._cursor.executemany(sqlquery, point_curve_map)

    def seismic_data_insert(self, hazard_model_id, datagrid_id,
                            stat_id, exptime_id, points, curves):
        return self.hazard_data_insert('SEISMIC', hazard_model_id,
                                       datagrid_id, stat_id, exptime_id,
                                       points, curves)
        # points_idlist = self.pointsid_list(points)
        #
        # point_curve_map = zip(points_idlist,
        #                       [", ".join(map(str,x)) for x in curves])
        #
        # sqlquery = """
        #             INSERT IGNORE INTO seismic_data (id_hazard_model,
        #                 id_point, id_grid, id_statistic, id_exposure_time,
        #                 hazard_curve) VALUES ( """ + str(hazard_model_id) + \
        #            """, %s, """ + str(datagrid_id) + ", " + str(stat_id) + \
        #                 ", " + str(exptime_id) + """, %s )
        #            """
        # return self._cursor.executemany(sqlquery, point_curve_map)

    def get_point_all_curves(self, phenomenon_id,
            hazard_id, point_id, exp_time_id):
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
                     `dt`.`id_point`={2} AND
                     `dt`.`id_exposure_time`={3}
        """
        query = sqlquery.format(table_name, hazard_id, point_id, exp_time_id)
        self._cursor.execute(query)
        res = self._cursor.fetchall()
        return dict(res)



    def get_curves(self, phenomenon_id, hazard_model_id,
                   datagrid_id, stat_id, exptime_id):


        phenomenon = self.get_phenomenon_by_id(phenomenon_id)
        if phenomenon['name'] == 'VOLCANIC':
            table_name = "volcanic_data"
        elif phenomenon['name'] == 'SEISMIC':
            table_name = "seismic_data"
        elif phenomenon['name'] == 'TSUNAMIC':
            table_name = "tsunamic_data"
        else:
            return None

        sqlquery = """ SELECT `p`.`id`, `p`.`latitude`, `p`.`longitude`,
                        `d`.`hazard_curve` FROM
            `{0}` `d` LEFT JOIN `points` `p`
             ON `d`.`id_point`=`p`.`id`
             WHERE `d`.`id_hazard_model`= {1} AND `d`.`id_grid` = {2}
             AND `d`.`id_statistic` = {3} and `d`.`id_exposure_time` = {4}
        """
        query = sqlquery.format(table_name,
                                             hazard_model_id,
                                             datagrid_id,
                                             stat_id, exptime_id)
        print "sqlquery %s" % query
        self._cursor.execute(sqlquery.format(table_name,
                                             hazard_model_id,
                                             datagrid_id,
                                             stat_id, exptime_id))
        return [dict(zip(['point', 'curve'],
                         (dict(zip(['id', 'latitude', 'longitude'],
                                   (x[0],x[1], x[2]))),
                          ([float(a) for a in x[3].split(',')]))))
                for x in self._cursor.fetchall()]

    def create(self):
        # TODO: create DB for real!
        print "create"

    def populate(self, datadir, percpattern, datagridfile_path):
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
        datagrid_points = gf.get_gridpoints_from_file(datagridfile_path)
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
                            try:
                                fileXmlModel =  gf.HazardXMLModel(
                                    os.path.join(dir_tmp, filename),
                                    phen['phenomenon_name'])
                            except Exception as e:
                                print "ERROR: %s is not a valid ByMuR file! " \
                                      "Skipping to next one" % filename
                                continue
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
                            imt_id = self.intensity_measure_unit_get_insert_id(
                                fileXmlModel.iml_imt)
                            self.intensity_thresholds_insert(
                                fileXmlModel.iml_thresholds, imt_id)
                            iml_thres = self.intensity_thresholds_idlist(imt_id,
                                fileXmlModel.iml_thresholds)
                            self.hazard_thresholds_rel(hazard_model_id,
                                                   iml_thres)

                            # Data in hazmodel_statistics
                            print "DB > Inserting statistics"
                            stat_id = self.statistic_get_insert_id(
                                fileXmlModel.statistic,
                                fileXmlModel.percentile_value)

                            self.hazard_statistic_rel(hazard_model_id,
                                                   stat_id)

                            # Data in hazmodel_exptimes
                            # TODO: dtime potrebbe essere chiamato exp_time?
                            print "DB > Inserting exposure times"
                            exptime_id = self.exposure_time_get_insert_id(
                                fileXmlModel.dtime)
                            self.hazard_exposure_time_rel(hazard_model_id,
                                                        exptime_id)


                            print "DB > Inserting hazard data: " \
                                  "phenomenon: %s \n" \
                                  "hazard_model id: %s \n" \
                                  "datagrid_id %s \n" \
                                  "stat_id %s \n" \
                                  "exptime id: %s \n" \
                                  "points_id_len: %s \n" \
                                  "points_value_len: %s \n" \
                                      % (
                                fileXmlModel.phenomenon,
                                hazard_model_id,
                                datagrid_id,
                                stat_id,
                                exptime_id,
                                len(gf.points_to_latlon(
                                    fileXmlModel.points_coords)),
                                len(fileXmlModel.points_values)
                            )

                            self.hazard_data_insert(
                                fileXmlModel.phenomenon,
                                hazard_model_id,
                                datagrid_id,
                                stat_id,
                                exptime_id,
                                gf.points_to_latlon(
                                    fileXmlModel.points_coords),
                                fileXmlModel.points_values
                            )
                            # # Data in hazmodel_volcanos
                            # if fileXmlModel.phenomenon == "VOLCANIC":
                            #     volcano_id = self.volcano_get_insert_id(
                            #     fileXmlModel.volcano)
                            #     self.hazard_volcano_rel(hazard_model_id,
                            #                             volcano_id)
                            #     print "DB > Inserting volcanic hazard data: " \
                            #           "hazard_model id: %s \n" \
                            #           "datagrid_id %s \n" \
                            #           "stat_id %s \n" \
                            #           "exptime id: %s \n" \
                            #           "points_id_len: %s \n" \
                            #           "points_value_len: %s \n" \
                            #           % (
                            #         hazard_model_id,
                            #         datagrid_id,
                            #         stat_id,
                            #         exptime_id,
                            #         len(gf.points_to_latlon(
                            #             fileXmlModel.points_coords)),
                            #         len(fileXmlModel.points_values)
                            #     )
                            #
                            #     self.volcanic_data_insert(
                            #         hazard_model_id,
                            #         datagrid_id,
                            #         stat_id,
                            #         exptime_id,
                            #         gf.points_to_latlon(
                            #             fileXmlModel.points_coords),
                            #         fileXmlModel.points_values
                            #     )
                            # elif fileXmlModel.phenomenon == "SEISMIC":
                            #     print "DB > Inserting seismic hazard data: " \
                            #           "hazard_model id: %s \n" \
                            #           "datagrid_id %s \n" \
                            #           "stat_id %s \n" \
                            #           "exptime id: %s \n" \
                            #           "points_id_len: %s \n" \
                            #           "points_value_len: %s \n" \
                            #           % (
                            #         hazard_model_id,
                            #         datagrid_id,
                            #         stat_id,
                            #         exptime_id,
                            #         len(gf.points_to_latlon(
                            #             fileXmlModel.points_coords)),
                            #         len(fileXmlModel.points_values)
                            #     )
                            #
                            #     self.seismic_data_insert(
                            #         hazard_model_id,
                            #         datagrid_id,
                            #         stat_id,
                            #         exptime_id,
                            #         gf.points_to_latlon(
                            #             fileXmlModel.points_coords),
                            #         fileXmlModel.points_values
                            #     )
                            # elif fileXmlModel.phenomenon == "TSUNAMIC":
                            #     print "DB > Inserting tsunamic hazard data: " \
                            #           "hazard_model id: %s \n" \
                            #           "datagrid_id %s \n" \
                            #           "stat_id %s \n" \
                            #           "exptime id: %s \n" \
                            #           "points_id_len: %s \n" \
                            #           "points_value_len: %s \n" \
                            #           % (
                            #         hazard_model_id,
                            #         datagrid_id,
                            #         stat_id,
                            #         exptime_id,
                            #         len(gf.points_to_latlon(
                            #             fileXmlModel.points_coords)),
                            #         len(fileXmlModel.points_values)
                            #     )
                            #
                            #     self.tsunamic_data_insert(
                            #         hazard_model_id,
                            #         datagrid_id,
                            #         stat_id,
                            #         exptime_id,
                            #         gf.points_to_latlon(
                            #             fileXmlModel.points_coords),
                            #         fileXmlModel.points_values
                            #     )
                            # else:
                            #     print "Phenomena not (yet?) implemented"
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



# class BymurDB():
#
#     def __init__(self, **kwargs):
#         """
#         Connecting to database
#         """
#         try:
#             self._connection = mdb.connect(host=kwargs.pop('db_host',''),
#                                            port=int(kwargs.pop('db_port',0)),
#                                            user=kwargs.pop('db_user',''),
#                                            passwd=kwargs.pop('db_password',''),
#                                            db=kwargs.pop('db_name',''))
#             self._cursor = self._connection.cursor()
#         except:
#             raise
#
#     def getVersion(self):
#         try:
#             self._cursor.execute("SELECT VERSION()")
#             db_version = self._cursor.fetchone()
#         except:
#             raise
#         return db_version[0]
#
#     def close(self):
#         self._connection.close()
#
#
#     def readTable(self, table_name):
#         """
#         Reading all tables from Bymur DB and storing all data in python lists.
#         """
#         query = "SELECT * FROM {0}"
#         self._cursor.execute(query.format(table_name))
#         return self._cursor.fetchall()
#
#     def selecDtime(self, nhaz):
#         """
#         """
#         sql_query = """
#             SELECT dtime from {0} WHERE id_points=1 AND stat='Average'
#             """
#         self._cursor.execute(sql_query.format(nhaz))
#         return self._cursor.fetchall()
#
#     def assignFlagPerc(self, table_name):
#         """
#         """
#
#         sql_query = """
#                 SELECT curve from {0} WHERE stat LIKE 'Perc%' AND id_points=1
#                 """
#         self._cursor.execute(sql_query.format(table_name))
#         rows = self._cursor.fetchall()
#         sumval = 0
#         for row in rows:
#             tmp = [float(j) for j in str(row[0]).split()]
#             sumval = sumval + tmp[0]
#
#         if (sumval > 0):
#             return 1
#         else:
#             return 0
#
#     def readHC(self, haz_sel, tw, dtime, hc, hc_perc):
#         """
#             haz_sel:  selected hazard phenomenon
#             tw:       selected time window
#             dtime:    selected hazard phenomenon
#             hc:       hazard array
#             hc_perc:  percentiles given for this hazard
#         """
#         print 'haz_sel-->', haz_sel
#         print 'tw-->', tw
#
#         tbname = "hazard" + str(haz_sel + 1)
#
#         cmd = "SELECT stat FROM " + tbname + " WHERE dtime = '" + \
#             dtime[haz_sel][tw].zfill(3) + "' AND stat != 'Average' AND id_points = 1"
#         self._cursor.execute(cmd)
#         tmp1 = self._cursor.fetchall()
#         nperc_haz = len(tmp1)
#         perc_haz = np.zeros(nperc_haz, dtype=np.int8)
#         print cmd
#         print 'cur.fetchall: ', tmp1
#         for iperchaz in range(nperc_haz):
#             line = tmp1[iperchaz]
#             tmp2 = line[0].split('Perc')
#             perc_haz[iperchaz] = tmp2[1]
#         hc_perc[haz_sel] = perc_haz
#         percsel = range(1, 100)  # [10,50,90]
#         cmd = "SELECT id_points,curve FROM " + tbname + " WHERE dtime ='" \
#             + dtime[haz_sel][tw].zfill(3) + "' AND stat = 'Average'"
#         self._cursor.execute(cmd)
#         rows = self._cursor.fetchall()
#         for row in rows:
#             ipoint = row[0]
#             curvetmp = row[1]
#             hc[haz_sel][tw][0][ipoint - 1] = curvetmp
#
#         for ipercsel in range(len(perc_haz)):
#             perctmp = perc_haz[ipercsel]
#             cmd = "SELECT id_points,curve FROM " + tbname + " WHERE dtime = '" + \
#                 dtime[haz_sel][tw].zfill(3) + "' AND stat = 'Perc" + str(perctmp) + "'"
#             self._cursor.execute(cmd)
#             rows = self._cursor.fetchall()
#             for row in rows:
#                 ipoint = row[0]
#                 curvetmp = row[1]
#                 hc[haz_sel][tw][perctmp][ipoint - 1] = curvetmp
#         return hc
#
#     def createTables(self,  models):
#         """
#         Creating DB Tables if they do not exist.
#         """
#
#         print "createTables"
#
#         ntables_haz = sum([len(models[i][:]) for i in range(len(models))])
#
#         # Hazard phenomena table creation
#         sql_query = """
#                     CREATE TABLE IF NOT EXISTS hazard_phenomena
#                     (id_haz INT UNSIGNED NOT NULL PRIMARY KEY,
#                     id_map_info INT, id_spatial_data INT,
#                     vd_ID INT,
#                      name VARCHAR(32), model VARCHAR(32),
#                      imt VARCHAR(32), iml TEXT);
#                     """
#         self._cursor.execute(sql_query)
#
#         # Spatial Data table creation
#         sql_query = """
#                     CREATE TABLE IF NOT EXISTS spatial_data1
#                     (id_points INT UNSIGNED NOT NULL PRIMARY KEY,
#                     id_area INT UNSIGNED, lon DOUBLE, lat DOUBLE);
#                     """
#         self._cursor.execute(sql_query)
#
#         # Hazard tables creation
#         for i in range(ntables_haz):
#             tbname = "hazard" + str(i + 1)
#             sql_query = """
#                       CREATE TABLE IF NOT EXISTS {0}
#                       (id INT UNSIGNED NOT NULL PRIMARY KEY, id_haz INT,
#                       id_points INT, stat VARCHAR(20), dtime VARCHAR(20), curve MEDIUMTEXT);
#                       """
#             self._cursor.execute(sql_query.format(tbname))
#
#         # Map Info table creation
#         sql_query = """
#                     CREATE TABLE IF NOT EXISTS map_info
#                     (id INT UNSIGNED NOT NULL PRIMARY KEY, imgpath TEXT,
#                     lon_min DOUBLE, lon_max DOUBLE, lat_min DOUBLE, lat_max DOUBLE);
#                     """
#         self._cursor.execute(sql_query)
#
#     def genInfoPop(self, map_path, limits):
#         """
#         """
#         print "genInfoPop"
#
#         sql = "SELECT COUNT(1) FROM map_info WHERE id = '1'"
#         self._cursor.execute(sql)
#         if self._cursor.fetchone()[0]:
#             sql = """
#                 UPDATE map_info SET imgpath='{0}', lon_min={1}, lon_max={2},
#                 lat_min={3}, lat_max={4} WHERE id=1
#                 """
#             self._cursor.execute(sql.format(map_path, limits[0], limits[1],
#                                             limits[2], limits[3]))
#         else:
#             sql = """
#                 INSERT INTO map_info (id, imgpath, lon_min, lon_max,
#                 lat_min, lat_max) VALUES (1, '{0}', {1}, {2}, {3}, {4})
#                 """
#             self._cursor.execute(sql.format(map_path, limits[0], limits[1],
#                                             limits[2], limits[3]))
#
#     def spatDataPop(self, grid_path):
#         """
#         Populating Spatial Data table  or update it if it already exists.
#
#         """
#         print "spatDataPop"
#
#         A = np.loadtxt(grid_path)
#         lon = A[:, 0]
#         lat = A[:, 1]
#         id_area = A[:, 2]
#         npts = len(lon)
#
#         sql = "SELECT COUNT(1) FROM spatial_data1 WHERE id_points = '1'"
#         self._cursor.execute(sql)
#         if self._cursor.fetchone()[0]:
#             for i in range(npts):
#                 sql = """
#                   UPDATE spatial_data1 SET id_area='{0}',
#                   lon='{1}', lat='{2}' WHERE id_points={3}
#                   """
#                 self._cursor.execute(sql.format(id_area[i], lon[i], lat[i], i + 1))
#         else:
#             for i in range(npts):
#                 sql = """
#                   INSERT INTO spatial_data1 (id_points, id_area,
#                   lon, lat) VALUES ({0}, '{1}', '{2}', '{3}')
#                   """
#                 self._cursor.execute(sql.format(i + 1, id_area[i], lon[i], lat[i]))
#         return npts
#
#     def hazTabPop(self, perc, hazards, models, dtime, haz_path, npts,
#                   dtimefold):
#         """
#         Populating hazard tables of Bymur DB if they are empty or update them if
#         they already exist.
#         """
#         print "hazTabPop"
#
#         mod = []
#         imt = []
#         iml = []
#         mean = []
#         hc = []
#         nmods = 0
#
#         for h in range(len(hazards)):
#             for m in range(len(models[h])):
#                 nmods = nmods + 1
#                 hcTmp = []
#                 meanTmp = []
#
#                 for k in range(len(dtime[nmods - 1])):
#                     print h, m, k, nmods
#                     print haz_path, hazards[h], models[h][m], dtimefold[nmods - 1][k]
#                     curdir = os.path.join(
#                         haz_path,
#                         hazards[h],
#                         models[h][m],
#                         dtimefold[
#                             nmods -
#                             1][k])
#                     print "reading from ", curdir
#
#                     if not os.listdir(curdir):
#                         # break
#                         modTmp = "Null"
#                         imtTmp = "Null"
#                         imlTmp = "0"
#                         meanTmp = [["0"] * npts] * len(dtime[nmods - 1])
#                         hcTmp = [
#                             [["0"] * npts] * len(perc)] * len(dtime[nmods - 1])
#                     else:
#                         print "found: dtime=", k, ' from: ', curdir
#                         filexml = os.path.join(curdir, "hazardcurve-mean.xml")
#                         tmp = dbXmlParsing(filexml)
#                         modTmp = tmp[0]
#                         imtTmp = tmp[2]
#                         imlTmp = tmp[3]
#                         meanTmp.append(tmp[6])
#                         npts = len(tmp[6])
#                         niml = len([float(j) for j in tmp[6][0].split()])
#
#                         # reading percentiles
#                         hcTmp2 = []
#                         path = os.path.join(curdir, "hazardcurve-percentile-")
#                         for p in perc:
#                             filexml = path + str(p) + ".xml"
#                             if os.path.isfile(filexml):
#                                 tmp = dbXmlParsing(filexml)
#                                 hcTmp2.append(tmp[6])
#                             else:
#                                 tmplist = [
#                                     ' '.join(
#                                         '0.0 ' for i in range(niml))] * npts
#                                 hcTmp2.append(tmplist)
#                         else:
#                             hcTmp.append(hcTmp2)
#
#                 else:
#                     mod.append(modTmp)
#                     imt.append(imtTmp)
#                     iml.append(imlTmp)
#                     mean.append(meanTmp)
#                     hc.append(hcTmp)
#
#         print mod, imt, iml
#         print len(mod), len(imt), len(iml)
#         print len(mean), len(mean[0][:]), len(mean[0][0][:])
#         print len(hc), len(hc[0][:]), len(hc[0][0][:]), len(hc[0][0][0][:])
#
#
#         # Populating Hazard Phenomena table
#         nmods = 0
#         for h in range(len(hazards)):
#             for m in range(len(models[h])):
#                 nmods = nmods + 1
#                 sql = "SELECT COUNT({0}) FROM hazard_phenomena WHERE id_haz = {1}"
#                 self._cursor.execute(sql.format(nmods, nmods))
#                 if self._cursor.fetchone()[0]:
#                     sql = """
#                 UPDATE hazard_phenomena SET name='{0}',
#                 model='{1}', imt='{2}', iml='{3}'
#                 id_map_info = 1, id_spatial_data = 1,
#                 vd_ID = 0,
#                 WHERE id_haz={4}
#                 """
#                     self._cursor.execute(sql.format(hazards[h], models[h][m], imt[
#                                 nmods - 1].replace("_", " "), iml[nmods - 1], nmods))
#                 else:
#                     sql = """
#                 INSERT INTO hazard_phenomena (id_haz, name, model,
#                 imt, iml, id_map_info, id_spatial_data, vd_ID) VALUES
#                 ({0}, '{1}', '{2}', '{3}', '{4}', 1, 1, 0)
#                 """
#                     self._cursor.execute(sql.format(nmods,
#                                            hazards[h],
#                                            models[h][m],
#                                            imt[nmods - 1].replace("_",
#                                                                   " "),
#                                            iml[nmods - 1]))
#
#         # Populating Hazard tables
#         sql = "SELECT COUNT(1) FROM hazard1 WHERE id_points = '1'"
#         self._cursor.execute(sql)
#         if self._cursor.fetchone()[0]:
#             for m in range(len(mod)):
#                 tbname = "hazard" + str(m + 1)
#                 idc = 0
#                 for k in range(len(dtime[m])):
#                     for i in range(npts):
#                         idc = idc + 1
#                         sql = """
#                   UPDATE {0} SET id_haz={1}, id_points={2}, stat='{3}',
#                   dtime='{4}', curve='{5}' WHERE id={6}
#                   """
#                         self._cursor.execute(
#                             sql.format(
#                                 tbname,
#                                 m + 1,
#                                 i + 1,
#                                 "Average",
#                                 dtime[m][k],
#                                 mean[m][k][i],
#                                 idc))
#
#                     for p in range(len(perc)):
#                         pp = str(perc[p])
#                         for i in range(npts):
#                             idc = idc + 1
#                             sql = """
#                     UPDATE {0} SET id_haz={1}, id_points={2}, stat='{3}',
#                     dtime='{4}', curve='{5}' WHERE id={6}
#                     """
#                             self._cursor.execute(
#                                 sql.format(
#                                     tbname,
#                                     m + 1,
#                                     i + 1,
#                                     "Perc" + pp,
#                                     dtime[m][k],
#                                     hc[m][k][p][i],
#                                     idc))
#
#         else:
#             for m in range(len(mod)):
#                 tbname = "hazard" + str(m + 1)
#                 idc = 0
#                 for k in range(len(dtime[m])):
#                     for i in range(npts):
#                         idc = idc + 1
#                         sql = """
#                   INSERT INTO {0} (id, id_haz, id_points, stat,
#                   dtime, curve) VALUES ( {1}, {2}, {3}, '{4}', '{5}', '{6}' )
#                   """
#                         self._cursor.execute(
#                             sql.format(
#                                 tbname,
#                                 idc,
#                                 m + 1,
#                                 i + 1,
#                                 "Average",
#                                 dtime[m][k],
#                                 mean[m][k][i]))
#
#                     for p in range(len(perc)):
#                         pp = str(perc[p])
#                         for i in range(npts):
#                             idc = idc + 1
#                             sql = """
#                     INSERT INTO {0} (id, id_haz, id_points, stat,
#                     dtime, curve) VALUES ( {1}, {2}, {3}, '{4}', '{5}', '{6}' )
#                     """
#                             self._cursor.execute(
#                                 sql.format(
#                                     tbname,
#                                     idc,
#                                     m + 1,
#                                     i + 1,
#                                     "Perc" + pp,
#                                     dtime[m][k],
#                                     hc[m][k][p][i]))
#
#     def dropAllTables(self):
#         """
#         """
#         query = "SHOW TABLES"
#         self._cursor.execute(query)
#         tables = self._cursor.fetchall()
#
#         for tab in tables:
#             print tab[0]
#             query = "DROP TABLE {0}"
#             self._cursor.execute(query.format(tab[0]))
#
#     def insertHazardDetails(self, id, name, model, imt, iml):
#          sql_query = """
#                 INSERT INTO hazard_phenomena (id_haz,name,model,imt,iml,
#                 id_map_info, id_spatial_data, vd_ID)
#                 VALUES('{0}','{1}','{2}','{3}','{4}',1, 1, 0);
#               """
#          self._cursor.execute(sql_query.format(id, name, model, imt, iml))
#
#     def createHazardTable(self,table_name):
#         sql_query = """
#                     CREATE TABLE IF NOT EXISTS {0}
#                     (id INT UNSIGNED NOT NULL PRIMARY KEY, id_haz INT,
#                     id_points INT, stat VARCHAR(20), dtime VARCHAR(20),
#                     curve MEDIUMTEXT);
#                     """
#         self._cursor.execute(sql_query.format(table_name))
#
#     def insertHazPoint(self,table_name, id, id_haz, id_point,
#                       stat, dtime, curve):
#         sql_query = """
#                   INSERT INTO {0} (id, id_haz, id_points, stat,
#                   dtime, curve) VALUES ( {1}, {2}, {3}, '{4}', '{5}', '{6}' )
#                   """
#         self._cursor.execute(sql_query.format(table_name, id, id_haz, id_point,
#                                             stat, dtime, curve))
