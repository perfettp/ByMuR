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
SET FOREIGN_KEY_CHECKS=0;
SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

DROP TABLE IF EXISTS `datagrids`;
CREATE TABLE IF NOT EXISTS `datagrids` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=7 ;

DROP TABLE IF EXISTS `grid_points`;
CREATE TABLE IF NOT EXISTS `grid_points` (
  `id_datagrid` int(11) NOT NULL,
  `id_point` bigint(20) NOT NULL,
  PRIMARY KEY (`id_datagrid`,`id_point`),
  KEY `fk_grid_points_1` (`id_datagrid`),
  KEY `fk_grid_points_2` (`id_point`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

DROP TABLE IF EXISTS `hazard_models`;
CREATE TABLE IF NOT EXISTS `hazard_models` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_phenomenon` int(11) NOT NULL,
  `id_datagrid` int(11) NOT NULL,
  `name` varchar(45) COLLATE utf8_bin NOT NULL,
  `exposure_time` varchar(10) COLLATE utf8_bin DEFAULT NULL,
  `iml` mediumtext COLLATE utf8_bin,
  `imt` varchar(45) COLLATE utf8_bin DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_hazard_models_1_idx` (`id_datagrid`),
  KEY `fk_hazard_models_2_idx` (`id_phenomenon`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=44 ;

DROP TABLE IF EXISTS `hazmodel_statistics`;
CREATE TABLE IF NOT EXISTS `hazmodel_statistics` (
  `id_hazard_model` int(11) NOT NULL,
  `id_statistic` int(11) NOT NULL,
  PRIMARY KEY (`id_hazard_model`,`id_statistic`),
  KEY `fk_hazmodels_statistics_1` (`id_hazard_model`),
  KEY `fk_hazmodels_statistics_2` (`id_statistic`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

DROP TABLE IF EXISTS `hazmodel_volcanos`;
CREATE TABLE IF NOT EXISTS `hazmodel_volcanos` (
  `id_hazard_model` int(11) NOT NULL,
  `id_volcano` int(11) NOT NULL,
  PRIMARY KEY (`id_hazard_model`,`id_volcano`),
  KEY `fk_hazmodel_volcano_1` (`id_hazard_model`),
  KEY `fk_hazmodel_volcano_2` (`id_volcano`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

DROP TABLE IF EXISTS `phenomena`;
CREATE TABLE IF NOT EXISTS `phenomena` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=10 ;

DROP TABLE IF EXISTS `points`;
CREATE TABLE IF NOT EXISTS `points` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `easting` bigint(20) NOT NULL,
  `northing` bigint(20) NOT NULL,
  `zone_number` tinyint(4) DEFAULT NULL,
  `zone_letter` char(1) COLLATE utf8_bin DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `coords` (`easting`,`northing`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=206903 ;

DROP TABLE IF EXISTS `seismic_data`;
CREATE TABLE IF NOT EXISTS `seismic_data` (
  `id_hazard_model` int(11) NOT NULL,
  `id_point` bigint(20) NOT NULL,
  `id_statistic` int(11) NOT NULL,
  `hazard_curve` mediumtext COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`id_hazard_model`,`id_point`,`id_statistic`),
  KEY `index_haz_grid_stat` (`id_hazard_model`,`id_statistic`),
  KEY `fk_seismic_data_1` (`id_hazard_model`),
  KEY `fk_seismic_data_2` (`id_point`),
  KEY `fk_seismic_data_4` (`id_statistic`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

DROP TABLE IF EXISTS `statistics`;
CREATE TABLE IF NOT EXISTS `statistics` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=152 ;

DROP TABLE IF EXISTS `tsunamic_data`;
CREATE TABLE IF NOT EXISTS `tsunamic_data` (
  `id_hazard_model` int(11) NOT NULL,
  `id_point` bigint(20) NOT NULL,
  `id_statistic` int(11) NOT NULL,
  `hazard_curve` mediumtext COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`id_hazard_model`,`id_point`,`id_statistic`),
  KEY `index_haz_grid_stat` (`id_hazard_model`,`id_statistic`),
  KEY `fk_tsunamic_data_1` (`id_hazard_model`),
  KEY `fk_tsunamic_data_2_idx` (`id_point`),
  KEY `fk_tsunamic_data_3_idx` (`id_statistic`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

DROP TABLE IF EXISTS `volcanic_data`;
CREATE TABLE IF NOT EXISTS `volcanic_data` (
  `id_hazard_model` int(11) NOT NULL,
  `id_point` bigint(20) NOT NULL,
  `id_statistic` int(11) NOT NULL,
  `hazard_curve` mediumtext COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`id_hazard_model`,`id_point`,`id_statistic`),
  KEY `index_haz_grid_stat` (`id_hazard_model`,`id_statistic`),
  KEY `fk_volcanic_data_3_idx` (`id_statistic`),
  KEY `fk_volcanic_data_2` (`id_point`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

DROP TABLE IF EXISTS `volcanos`;
CREATE TABLE IF NOT EXISTS `volcanos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=1 ;

ALTER TABLE `grid_points`
  ADD CONSTRAINT `fk_grid_points_1` FOREIGN KEY (`id_datagrid`) REFERENCES `datagrids` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  ADD CONSTRAINT `fk_grid_points_2` FOREIGN KEY (`id_point`) REFERENCES `points` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `hazard_models`
  ADD CONSTRAINT `fk_hazard_models_1` FOREIGN KEY (`id_datagrid`) REFERENCES `datagrids` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  ADD CONSTRAINT `fk_hazard_models_2` FOREIGN KEY (`id_phenomenon`) REFERENCES `phenomena` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `hazmodel_statistics`
  ADD CONSTRAINT `fk_hazmodels_statistics_1` FOREIGN KEY (`id_hazard_model`) REFERENCES `hazard_models` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  ADD CONSTRAINT `fk_hazmodels_statistics_2` FOREIGN KEY (`id_statistic`) REFERENCES `statistics` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `hazmodel_volcanos`
  ADD CONSTRAINT `fk_hazmodel_volcano_1` FOREIGN KEY (`id_hazard_model`) REFERENCES `hazard_models` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  ADD CONSTRAINT `fk_hazmodel_volcano_2` FOREIGN KEY (`id_volcano`) REFERENCES `volcanos` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `seismic_data`
  ADD CONSTRAINT `fk_seismic_data_1` FOREIGN KEY (`id_hazard_model`) REFERENCES `hazard_models` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  ADD CONSTRAINT `fk_seismic_data_2` FOREIGN KEY (`id_point`) REFERENCES `points` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  ADD CONSTRAINT `fk_seismic_data_3` FOREIGN KEY (`id_statistic`) REFERENCES `statistics` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `tsunamic_data`
  ADD CONSTRAINT `fk_tsunamic_data_1` FOREIGN KEY (`id_hazard_model`) REFERENCES `hazard_models` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  ADD CONSTRAINT `fk_tsunamic_data_2` FOREIGN KEY (`id_point`) REFERENCES `points` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  ADD CONSTRAINT `fk_tsunamic_data_3` FOREIGN KEY (`id_statistic`) REFERENCES `statistics` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE `volcanic_data`
  ADD CONSTRAINT `fk_volcanic_data_1` FOREIGN KEY (`id_hazard_model`) REFERENCES `hazard_models` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  ADD CONSTRAINT `fk_volcanic_data_2` FOREIGN KEY (`id_point`) REFERENCES `points` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  ADD CONSTRAINT `fk_volcanic_data_3` FOREIGN KEY (`id_statistic`) REFERENCES `statistics` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION;
SET FOREIGN_KEY_CHECKS=1;

INSERT INTO `phenomena` (`name`) VALUES('SEISMIC');
INSERT INTO `phenomena` (`name`) VALUES('TSUNAMIC');
INSERT INTO `phenomena` (`name`) VALUES('VOLCANIC')
    """

    def __init__(self, **kwargs):
        """
        Connecting to database
        """
        try:
            if kwargs.get('db_name') is None:
                print "Creating db!"
                self._connection = mdb.connect(host=kwargs.pop('db_host',
                                                       '***REMOVED***'),
                                       port=int(kwargs.pop('db_port',
                                                           3306)),
                                       user=kwargs.pop('db_user',
                                                       '***REMOVED***'),
                                       passwd=kwargs.pop('db_password',
                                                         '***REMOVED***'))
            else:
                print "Connecting db!"
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

    def create(self, dbname):
        # print "db.create"
        # print "dbname %s" % dbname
        # using manual escape to avoid unsupported quoting
        sqlquery = "CREATE DATABASE IF NOT EXISTS %s"
        sqlquery %= mdb.escape_string(dbname)
        self._cursor.execute(sqlquery)
        # print "use"
        sqlquery = "USE %s"
        sqlquery %= mdb.escape_string(dbname)
        self._cursor.execute(sqlquery)
        # print "import"
        for sql in self._sql_schema.split(";"):
            self._cursor.execute(sql)
            self.commit()

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
            WHERE gp.`id_datagrid`= %s ORDER BY `p`.`id`
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

    def get_general_classes_list(self):
        sqlquery = "SELECT id, name, label FROM general_classes"
        self._cursor.execute(sqlquery)
        return [dict(zip(('id', 'name', 'label'), c))
                for c in self._cursor.fetchall()]

    def get_age_classes_list(self):
        sqlquery = "SELECT id, name, label FROM age_classes"
        self._cursor.execute(sqlquery)
        return [dict(zip(('id', 'name', 'label'), c))
                for c in self._cursor.fetchall()]

    def get_house_classes_list(self):
        sqlquery = "SELECT id, name, label FROM house_classes"
        self._cursor.execute(sqlquery)
        return [dict(zip(('id', 'name', 'label'), c))
                for c in self._cursor.fetchall()]

    def get_phenomenon_by_id(self, phenomeon_id):
        sqlquery = """ SELECT `ph`.`id`, `ph`.`name`
            FROM `phenomena` `ph`  WHERE `ph`.`id`= '{0}'
        """
        self._cursor.execute(sqlquery.format(phenomeon_id))
        return dict(zip(['id', 'name'], self._cursor.fetchone()))

    def insert_id_statistic(self, statistic,
                                percentile_value):
        sqlquery = "SELECT id FROM statistics WHERE name = '{0}'"
        if (percentile_value) == '0' or (percentile_value is None) or (
                percentile_value == 0):
            statistic_name = statistic
        else:
            statistic_name = statistic + str(percentile_value).zfill(2)

        self._cursor.execute(sqlquery.format(statistic_name))
        id = self._cursor.fetchone()
        if id:
            return id[0]
        else:
            sqlquery = "INSERT INTO statistics (name) VALUES('{0}')"
            self._cursor.execute(sqlquery.format(statistic_name))
            return self._cursor.lastrowid

    def insert_id_statistic_new(self, statistic):
        sqlquery = "SELECT id FROM statistics WHERE name = '{0}'"

        self._cursor.execute(sqlquery.format(statistic))
        id = self._cursor.fetchone()
        if id:
            return id[0]
        else:
            sqlquery = "INSERT INTO statistics (name) VALUES('{0}')"
            self._cursor.execute(sqlquery.format(statistic))
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
        # print sqlquery
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


        point_curve_map = zip(points,
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
        """

        :rtype : object
        """
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


    def get_points_all_data(self, phenomenon_id, hazard_model_id, points):
        _res = list()
        for p in points:
            data = self.get_point_all_curves(phenomenon_id,
                                             hazard_model_id,
                                             p['id'])
            _point_data = dict(zip([stat[len("percentile"):]
                                    for stat in data.keys() if stat != "mean"],
                                    [[float(x) for x in val.split(',')]
                                        for val in data.values()]))
            _res.append(dict(zip(['point_id', 'point_data'],
                                 [p['id'], _point_data])))
        return _res


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
                fileXmlModel = bf.parse_xml_hazard(hazFile,
                                                   phenomenon_name)
            except Exception as e:
                print "ERROR: %s is not a valid ByMuR file! %s" \
                      "Skipping to next one" % (hazFile, str(e))
                continue
            # Foreign keys are already defined
            # Now insert hazard, after this other
            # many-to-many relationship
            print "DB > Creating hazarm_models entry"
            if fileXmlModel.hazard_model_name != '':
                _name = fileXmlModel.hazard_model_name
            else:
                _name = fileXmlModel.model_name

            print "_name = %s" % _name
            hazard_model_id = self.insert_id_hazard_model(
                phenomenon_id,
                datagrid_id,
                _name,
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

            points_idlist = self.get_pointsid_list_by_coords(
                fileXmlModel.points_coords)
            self.insert_hazard_data(fileXmlModel.phenomenon,
                                    hazard_model_id,
                                    stat_id,
                                    points_idlist,
                                    fileXmlModel.points_values)
            del fileXmlModel
        return True

    def drop_tables(self):
        query = "SHOW TABLES"
        self._cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        self._cursor.execute(query)
        tables = self._cursor.fetchall()
        print tables
        for tab in tables:
            query = "DROP TABLE %s"
            query %= tab[0]
            print query
            self._cursor.execute(query)
        self._cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

    def close(self):
        self._connection.close()

    def insert_id_age_class(self, name, label):
        sqlquery = "SELECT id FROM age_classes WHERE name LIKE '{0}'"
        self._cursor.execute(sqlquery.format(name))
        id = self._cursor.fetchone()
        if id:
            return id[0]
        else:
            sqlquery = "INSERT INTO age_classes (name, label)" \
                       "VALUES('{0}', '{1}')"
            self._cursor.execute(sqlquery.format(name, label))
            return self._cursor.lastrowid
        
    def insert_id_general_class(self, name, label):
        sqlquery = "SELECT id FROM general_classes WHERE name LIKE '{0}'"
        self._cursor.execute(sqlquery.format(name))
        id = self._cursor.fetchone()
        if id:
            return id[0]
        else:
            sqlquery = "INSERT INTO general_classes (name, label)" \
                       "VALUES('{0}', '{1}')"
            self._cursor.execute(sqlquery.format(name, label))
            return self._cursor.lastrowid
        
    def insert_id_house_class(self, name, label):
        sqlquery = "SELECT id FROM house_classes WHERE name LIKE '{0}'"
        self._cursor.execute(sqlquery.format(name))
        id = self._cursor.fetchone()
        if id:
            return id[0]
        else:
            sqlquery = "INSERT INTO house_classes (name, label)" \
                       "VALUES('{0}', '{1}')"
            self._cursor.execute(sqlquery.format(name, label))
            return self._cursor.lastrowid


    def insert_id_cost_classes(self, cost_classes_str, phen_id):
        sqlquery = "SELECT id FROM cost_classes WHERE classes LIKE '{0}' AND " \
                   "id_phenomenon = '{1}'"
        self._cursor.execute(sqlquery.format(cost_classes_str, phen_id))
        id = self._cursor.fetchone()
        if id:
            return id[0]
        else:
            sqlquery = "INSERT INTO cost_classes (id_phenomenon, classes)" \
                       "VALUES('{0}', '{1}')"
            self._cursor.execute(sqlquery.format(phen_id, cost_classes_str))
            return self._cursor.lastrowid
        
    def insert_id_frag_classes(self, frag_classes_str, phen_id):
        sqlquery = "SELECT id FROM fragility_classes WHERE classes LIKE '{" \
                   "0}' AND id_phenomenon = '{1}'"
        self._cursor.execute(sqlquery.format(frag_classes_str, phen_id))
        id = self._cursor.fetchone()
        if id:
            return id[0]
        else:
            sqlquery = "INSERT INTO fragility_classes (id_phenomenon, " \
                       "classes) VALUES('{0}', '{1}')"
            self._cursor.execute(sqlquery.format(phen_id, frag_classes_str))
            return self._cursor.lastrowid

    def get_fragility_classes_by_inv_id(self, inv_id):
        sqlquery = """ SELECT `phen`.`name`, `fc`.`classes`
            FROM (`inventory_frag_classes` `inv_fc` LEFT JOIN
            `fragility_classes` `fc` ON
            `inv_fc`.`id_frag_class`=`fc`.`id`)
                LEFT JOIN `phenomena` `phen`
                ON `fc`.`id_phenomenon` = `phen`.`id`
            WHERE `inv_fc`.`id_inventory`= %s
        """
        sqlquery %= str(inv_id)
        self._cursor.execute(sqlquery)
        return [dict(zip(['phenomenon_name', 'classes'], (x[0], x[1])))
                for x in self._cursor.fetchall()]

    def get_cost_classes_by_inv_id(self, inv_id):
        sqlquery = """ SELECT `phen`.`name`, `cc`.`classes`
            FROM (`inventory_cost_classes` `inv_cc` LEFT JOIN
            `cost_classes` `cc` ON
            `inv_cc`.`id_cost_class`=`cc`.`id`)
                LEFT JOIN `phenomena` `phen`
                ON `cc`.`id_phenomenon` = `phen`.`id`
            WHERE `inv_cc`.`id_inventory`= %s
        """
        sqlquery %= str(inv_id)
        self._cursor.execute(sqlquery)
        return [dict(zip(['phenomenon_name', 'classes'], (x[0], x[1])))
                for x in self._cursor.fetchall()]

    def get_costclass_prob_by_area_id(self, area_id):
        sqlquery = """ SELECT `phen`.`name`, `cc_prob`.`fnc`
            FROM `area_costclass_prob` `cc_prob` LEFT JOIN
            `phenomena` `phen` ON
            `cc_prob`.`id_phenomenon`=`phen`.`id`
            WHERE `cc_prob`.`id_area`= %s
        """
        sqlquery %= str(area_id)
        self._cursor.execute(sqlquery)
        return [dict(zip(['phenomenon_name', 'fnc'], (x[0], x[1])))
                for x in self._cursor.fetchall()]
    
    def get_fragclass_prob_by_area_id(self, area_id):
        sqlquery = """ SELECT `phen`.`name`, `fc_prob`.`fnt`,
            `fc_prob`.`fnt_given_general_class`
            FROM `area_fragclass_prob` `fc_prob` LEFT JOIN
            `phenomena` `phen` ON
            `fc_prob`.`id_phenomenon`=`phen`.`id`
            WHERE `fc_prob`.`id_area`= %s
        """

        sqlquery %= str(area_id)
        self._cursor.execute(sqlquery)
        return [dict(zip(['phenomenon_name', 'fnt', 'fnt_given_general_class'],
                         (x[0], x[1], x[2])))  for x in self._cursor.fetchall()]


    def insert_id_inventory(self, id_grid, name,
                               gen_classes, age_classes, house_classes):
        sqlquery = """SELECT id FROM inventory
                   WHERE name = '{0}'
                   """
        self._cursor.execute(sqlquery.format(name.upper()))
        id = self._cursor.fetchone()
        if id:
            return id[0]
        else:
            sqlquery = """
                    INSERT INTO inventory (grid_id, name, general_classes,
                                        age_classes, house_classes)
                                        VALUES({0}, '{1}', '{2}', '{3}', '{4}')
                    """
            self._cursor.execute(sqlquery.format(id_grid, name.upper(),
                                                 gen_classes, age_classes,
                                                 house_classes))
            return self._cursor.lastrowid

    def insert_inventory_cost_class_rel(self, inventory_id, class_id):
        """

        """
        sqlquery = """
                    INSERT IGNORE INTO inventory_cost_classes
                    (id_inventory, id_cost_class)
                        VALUES ({0}, {1})"""
        return self._cursor.execute(sqlquery.format(inventory_id, class_id))
    
    def insert_inventory_frag_class_rel(self, inventory_id, class_id):
        """

        """
        sqlquery = """
                    INSERT IGNORE INTO inventory_frag_classes
                    (id_inventory, id_frag_class)
                        VALUES ({0}, {1})"""
        return self._cursor.execute(sqlquery.format(inventory_id, class_id))

    def insert_areas(self, areas):
        sqlquery = """
                    INSERT IGNORE INTO areas (areaID, sectionID, centroidX,
                                        centroidY, total_buildings,
                                        general_classes_count,
                                        age_classes_count,
                                        house_classes_count,
                                        geometry)
                        VALUES(%(areaID)s, %(sectionID)s, %(centroidX)s,
                        %(centroidY)s, %(total_buildings)s,
                        %(general_classes_count)s, %(age_classes_count)s,
                        %(house_classes_count)s, %(geometry)s)
                    """
        return self._cursor.executemany(sqlquery, areas)

    def get_areas_list_by_id(self, areas):


        sqlquery = " SELECT id FROM areas WHERE (areaID)  IN (%s)"
        if len(areas) < 1:
            return -1
        areas_list = ', '.join([str((int(x['areaID']) )) for x in areas])
        sqlquery %= areas_list
        self._cursor.execute(sqlquery)
        return [item[0] for item in self._cursor.fetchall()]

    def insert_inventory_areas_rels(self, inv_id, areas_id_list):
        """

        """
        sqlquery = """
                    INSERT IGNORE INTO inventory_areas (id_inventory, id_area)
                        VALUES(""" + str(inv_id) + """, %s)"""
        return self._cursor.executemany(sqlquery, [(id,) for id
                                                   in areas_id_list])

    def insert_cost_prob_class(self, phen_id, fun_list):

        sqlquery = """
                    INSERT IGNORE INTO area_costclass_prob (id_phenomenon,
                    id_area, fnc) VALUES(""" + str(phen_id) + """, %s, %s)"""
        return self._cursor.executemany(sqlquery, fun_list)


    def insert_frag_prob_class(self, phen_id, fun_list):

        sqlquery = """
                    INSERT IGNORE INTO area_fragclass_prob (id_phenomenon,
                    id_area, fnt, fnt_given_general_class) VALUES(""" + \
                   str(phen_id) + """, %s, %s, %s)"""
        return self._cursor.executemany(sqlquery, fun_list)

    def get_sections_by_inventory_id(self, inv_id):
        sqlquery = """ SELECT `a`.`id`, `a`.`areaID`, `a`.`sectionID`,
            `a`.`centroidX`,  `a`.`centroidY`, `a`.`total_buildings`,
            `a`.`general_classes_count`, `a`.`age_classes_count`,
            `a`.`house_classes_count`, `a`.`geometry`
            FROM `areas` a LEFT JOIN `inventory_areas` ia ON
            a.`id`=ia.`id_area`
            WHERE ia.`id_inventory`= %s ORDER BY `a`.`id`
        """
        sqlquery %= str(inv_id)
        self._cursor.execute(sqlquery)
        return [dict(zip(['id', 'areaID', 'sectionID', 'centroidX', 'centroidY',
                          'total_buildings', 'general_classes_count',
                          'age_classes_count', 'house_classes_count',
                          'geometry'], x))
                for x in self._cursor.fetchall()]

    def get_inventory_by_datagrid_id(self, grid_id):
        sqlquery = """ SELECT `inv`.`id`,
                    `inv`.`grid_id`,
                    `inv`.`name`,
                    `inv`.`general_classes`,
                    `inv`.`age_classes`,
                    `inv`.`house_classes`
            FROM `inventory` `inv` WHERE `inv`.`grid_id`= %s
        """
        sqlquery %= str(grid_id)
        self._cursor.execute(sqlquery)
        _inv_dic = dict(zip(['inventory_id', 'grid_id', 'name',
                         'general_classes_ids', 'age_classes_ids',
                         'house_classes_ids'],
                        self._cursor.fetchone()))

        _inv_dic['general_classes'] = []
        _general_classes = self.get_general_classes_list()
        self.get_general_classes_list()
        for id_c in [int(id) for id in _inv_dic['general_classes_ids'].split()]:
            for j_c in _general_classes:
                if j_c['id'] == id_c:
                    _inv_dic['general_classes'].append(j_c)

        _inv_dic['age_classes'] = []
        _age_classes = self.get_age_classes_list()
        self.get_age_classes_list()
        for id_c in [int(id) for id in _inv_dic['age_classes_ids'].split()]:
            for j_c in _age_classes:
                if j_c['id'] == id_c:
                    _inv_dic['age_classes'].append(j_c)
        
        _inv_dic['house_classes'] = []
        _house_classes = self.get_house_classes_list()
        self.get_house_classes_list()
        for id_c in [int(id) for id in _inv_dic['house_classes_ids'].split()]:
            for j_c in _house_classes:
                if j_c['id'] == id_c:
                    _inv_dic['house_classes'].append(j_c)

        _inv_dic['cost_classes'] = self.get_cost_classes_by_inv_id(
            _inv_dic['inventory_id'])
        _inv_dic['fragility_classes'] =  self.get_fragility_classes_by_inv_id(
            _inv_dic['inventory_id'])


        return _inv_dic

    def add_inventory(self, inventory_xml, grid_id):

        age_classes_list = []
        general_classes_list = []
        house_classes_list = []
        if type(inventory_xml.classes) is dict:
            if ('ageClasses' in inventory_xml.classes.keys()) and \
                (len(inventory_xml.classes['ageClasses']) > 0):
                for c in inventory_xml.classes['ageClasses']:
                    c_id = self.insert_id_age_class(c.name, c.label)
                    age_classes_list.append(str(c_id))

            if ('generalClasses' in inventory_xml.classes.keys()) and \
                (len(inventory_xml.classes['generalClasses']) > 0):
                for c in inventory_xml.classes['generalClasses']:
                    c_id = self.insert_id_general_class(c.name, c.label)
                    general_classes_list.append(str(c_id))

            if ('houseClasses' in inventory_xml.classes.keys()) and \
                (len(inventory_xml.classes['houseClasses']) > 0):
                for c in inventory_xml.classes['houseClasses']:
                    c_id = self.insert_id_house_class(c.name, c.label)
                    house_classes_list.append(str(c_id))

        inventory_id = self.insert_id_inventory(grid_id, inventory_xml.name,
                            " ".join(general_classes_list),
                            " ".join(age_classes_list),
                            " ".join(house_classes_list))

        # Add classes
        if type(inventory_xml.classes) is dict:
            if 'costClasses' in inventory_xml.classes.keys():
                for p_class in inventory_xml.classes['costClasses'].keys():
                    cost_class_id = -1
                    phen_id = self.insert_id_phenomenon(p_class)
                    class_list = []
                    for i_class in range(len(inventory_xml.classes
                    ['costClasses'][p_class])):
                        c_tmp = (inventory_xml.classes['costClasses']
                                 [p_class][i_class].name,
                                 inventory_xml.classes['costClasses']
                                 [p_class][i_class].label)
                        class_list.append(c_tmp)
                    cost_classes_str = "("+str(class_list[0][0]) + "," \
                                + str(class_list[0][1])+")"
                    for c in class_list[1:]:
                        cost_classes_str += ":("+str(c[0]) + "," \
                                + str(c[1])+")"
                    cost_class_id = self.insert_id_cost_classes(
                        cost_classes_str, phen_id)
                    if cost_class_id >=0:
                        self.insert_inventory_cost_class_rel(inventory_id,
                                                             cost_class_id)

            if 'fragilityClasses' in inventory_xml.classes.keys():
                for p_class in inventory_xml.classes['fragilityClasses'].keys():
                    frag_class_id = -1
                    phen_id = self.insert_id_phenomenon(p_class)
                    class_list = []
                    for i_class in range(len(inventory_xml.classes
                    ['fragilityClasses'][p_class])):
                        c_tmp = (inventory_xml.classes['fragilityClasses']
                                 [p_class][i_class].name,
                                 inventory_xml.classes['fragilityClasses']
                                 [p_class][i_class].label)
                        class_list.append(c_tmp)
                    frag_classes_str = "("+str(class_list[0][0]) + "," \
                                + str(class_list[0][1])+")"
                    for c in class_list[1:]:
                        frag_classes_str += ":("+str(c[0]) + "," \
                                + str(c[1])+")"
                    frag_class_id =  self.insert_id_frag_classes(
                        frag_classes_str, phen_id)
                    if frag_class_id >=0:
                        self.insert_inventory_frag_class_rel(inventory_id,
                                                             frag_class_id)


        # Add areas
        a_list = []
        for a in inventory_xml.sections:
            a_dic = dict(areaID = a.areaID,
                         sectionID = a.sectionID,
                         centroidX = a.centroid[0],
                         centroidY = a.centroid[1],
                         total_buildings = a.asset.total,
                         geometry = ",".join(a.geometry),
                         frag_class_prob = a.asset.frag_class_prob,
                         cost_class_prob = a.asset.cost_class_prob)
            gen_class_count = age_class_count = house_class_count = ''
            if int(a.asset.total) > 0:
                gen_class_count = " ".join(a.asset.counts['genClassCount'])
                age_class_count = " ".join(a.asset.counts['ageClassCount'])
                house_class_count = " ".join(a.asset.counts['houseClassCount'])
            a_dic.update(dict(general_classes_count = gen_class_count,
                              age_classes_count = age_class_count,
                              house_classes_count = house_class_count))
            a_list.append(a_dic)
            # self.insert_areas([a_dic])
            # areas_id_list = self.get_areas_list_by_id([a_dic])
            # self.insert_inventory_areas_rels(inventory_id, areas_id_list)

        # Add inventory_areas relationship
        self.insert_areas(a_list)
        areas_id_list = self.get_areas_list_by_id(a_list)
        # print "Areas id list: %s " % areas_id_list
        for i_a in range(len(a_list)):
            a_list[i_a].update(dict(id_db=areas_id_list[i_a]))

        self.insert_inventory_areas_rels(inventory_id, areas_id_list)

        phen_id_dic = dict()
        for p in self.get_phenomena_list():
            phen_id_dic.update({p['phenomenon_name'].lower():p['phenomenon_id']})

        # Add areas cost and fragility class probability
        for phen_k in phen_id_dic.keys():
            cost_prob_class = []
            for a in a_list:
                if phen_k in a['cost_class_prob'].keys():
                    cost_prob_class.append((a['id_db'],
                            " ".join(a['cost_class_prob'][phen_k]['fnc'])))
                    # print "cost class prob, phen: %s, areaID: %s" %(phen_k,
                    #                                                 a['areaID'])
            # print cost_prob_class
            self.insert_cost_prob_class(phen_id_dic[phen_k], cost_prob_class)

        for phen_k in phen_id_dic.keys():
            frag_prob_class = []
            for a in a_list:
                if phen_k in a['frag_class_prob'].keys():
                    frag_prob_class.append((a['id_db'],
                                " ".join(a['frag_class_prob'][phen_k]['fnt']),
                                ",".join([" ".join(f) for f in
                                          a['frag_class_prob'][phen_k]
                                          ['fntGivenGeneralClass']])))
                    # print "frag class prob, phen: %s, areaID: %s" %(phen_k,
                    #                                                 a['areaID'])
            # print frag_prob_class
            self.insert_frag_prob_class(phen_id_dic[phen_k], frag_prob_class)

    def insert_id_fragility_model(self, id_phen, name, description,
                               iml, imt):
        sqlquery = """SELECT id FROM fragility_models
                   WHERE model_name = '{0}'
                   """
        self._cursor.execute(sqlquery.format(name.upper()))
        id = self._cursor.fetchone()
        if id:
            return id[0]
        else:
            sqlquery = """
                    INSERT INTO fragility_models (id_phenomenon,
                                                model_name, description,
                                                iml, imt)
                                        VALUES({0}, '{1}', '{2}', '{3}', '{4}')
                    """
            self._cursor.execute(sqlquery.format(id_phen, name.upper(),
                                                 description, iml, imt))
            return self._cursor.lastrowid

    def insert_fragility_statistic_rel(self, frag_id, statistic_id):
        """

        """
        sqlquery = """
                    INSERT IGNORE INTO fragmodel_statistics
                    (id_fragility_model, id_statistic)
                        VALUES ({0}, {1})"""
        return self._cursor.execute(sqlquery.format(frag_id, statistic_id))

    def get_statistics_by_frag_id(self, frag_id):
        sqlquery = """ SELECT `st`.`id`, `st`.`name`
            FROM `fragmodel_statistics` `frag_stat` LEFT JOIN
            `statistics` `st` ON
            `frag_stat`.`id_statistic`=`st`.`id`
            WHERE `frag_stat`.`id_fragility_model`= %s
        """
        sqlquery %= str(frag_id)
        self._cursor.execute(sqlquery)
        return [dict(zip(['id', 'name'], (x[0], x[1])))
                for x in self._cursor.fetchall()]

    def get_fragdata_by_areaid(self, frag_id, area_id):

        area_db_id = self.get_area_dbid_by_areaid(area_id)
        sqlquery = """
                    SELECT `st`.`name`, `ls`.`name`, `gc`.`name`,
                       `fd`.`fragility_curve`
                    FROM ((`fragility_data` `fd` JOIN `statistics` `st` ON
                      `fd`.`id_statistic` = `st`.`id`) LEFT JOIN
                      `general_classes` `gc` ON
                        `fd`.`id_general_class` = `gc`.`id`) LEFT JOIN
                        `limit_states` `ls` ON
                        `fd`.`id_limit_state` = `ls`.`id`
                    WHERE `fd`.`id_fragility_model`={0} AND
                     `fd`.`id_area`={1}
        """
        query = sqlquery.format(frag_id, area_db_id)
        self._cursor.execute(query)
        res = self._cursor.fetchall()
        return [dict(zip(['statistic', 'limit_state', 'general_class',
                          'fragility_curve'], x))
                for x in res]

    def get_lossdata_by_areaid(self, loss_id, area_id):

        area_db_id = self.get_area_dbid_by_areaid(area_id)
        sqlquery = """
                    SELECT `st`.`name`, `ls`.`name`, `ld`.`loss_function`
                    FROM (`loss_data` `ld` JOIN `statistics` `st` ON
                      `ld`.`id_statistic` = `st`.`id`) LEFT JOIN
                        `limit_states` `ls` ON
                        `ld`.`id_limit_state` = `ls`.`id`
                    WHERE `ld`.`id_loss_model`={0} AND
                     `ld`.`id_area`={1}
        """
        query = sqlquery.format(loss_id, area_db_id)
        self._cursor.execute(query)
        res = self._cursor.fetchall()
        return [dict(zip(['statistic', 'limit_state', 'loss_function'], x))
                for x in res]
    
    def get_riskdata_by_areaid(self, risk_id, area_id):

        area_db_id = self.get_area_dbid_by_areaid(area_id)
        print "area_db_id %s " % area_db_id
        sqlquery = """
                    SELECT `st`.`name`, `rd`.`risk_function`,
                    `rd`.`average_risk`
                    FROM `risk_data` `rd` LEFT JOIN `statistics` `st` ON
                      `rd`.`id_statistic` = `st`.`id`
                    WHERE `rd`.`id_risk_model`={0} AND
                     `rd`.`id_area`={1}
        """
        query = sqlquery.format(risk_id, area_db_id)
        self._cursor.execute(query)
        res = self._cursor.fetchall()
        return [dict(zip(['statistic', 'risk_function', 'average_risk'], x))
                for x in res]



    def insert_id_limitstate(self, limit_state):
        sqlquery = "SELECT id FROM limit_states WHERE name = '{0}'"

        self._cursor.execute(sqlquery.format(limit_state))
        id = self._cursor.fetchone()
        if id:
            return id[0]
        else:
            sqlquery = "INSERT INTO limit_states (name) VALUES('{0}')"
            self._cursor.execute(sqlquery.format(limit_state))
            return self._cursor.lastrowid

    def insert_fragmodel_limitstate_rel(self, frag_id, ls_id):
        """
        """
        sqlquery = """
                    INSERT IGNORE INTO fragmodel_limitstates
                    (id_fragility_model, id_limitstate)
                        VALUES ({0}, {1})"""
        return self._cursor.execute(sqlquery.format(frag_id, ls_id))
    
    def get_limitstates_by_frag_id(self, frag_id):
        sqlquery = """ SELECT `ls`.`id`, `ls`.`name`
            FROM `fragmodel_limitstates` `frag_ls` LEFT JOIN
            `limit_states` `ls` ON
            `frag_ls`.`id_limitstate`=`ls`.`id`
            WHERE `frag_ls`.`id_fragility_model`= %s
            ORDER BY `frag_ls`.`position`
        """
        sqlquery %= str(frag_id)
        self._cursor.execute(sqlquery)
        return [dict(zip(['id', 'name'], (x[0], x[1])))
                for x in self._cursor.fetchall()]

    def get_area_dbid_by_areaid(self, areaid):
        sqlquery = "SELECT id FROM areas WHERE areaID = {0}"
        self._cursor.execute(sqlquery.format(areaid))
        id = self._cursor.fetchone()
        if id:
            return id[0]
        else:
            return 0

    def insert_fragility_data(self, frag_id, stat_id, frag_entries):
        sqlquery = """
                    INSERT IGNORE INTO fragility_data (id_fragility_model,
                        id_area, id_statistic, id_limit_state,
                        id_general_class, fragility_curve)
                        VALUES ( """ + str(frag_id) + """
                        , %s, """ + str(stat_id) + """, %s , %s, %s)"""

        return self._cursor.executemany(sqlquery, frag_entries)

    def add_fragility(self, fragility_xml):
        phen_id_dic = dict()
        for p in self.get_phenomena_list():
            phen_id_dic.update({p['phenomenon_name']:p['phenomenon_id']})
        phen_id = phen_id_dic[fragility_xml.hazard_type.upper()]

        frag_id = self.insert_id_fragility_model(phen_id,
                            fragility_xml.model_name,
                            fragility_xml.description,
                            " ".join([str(f) for f in fragility_xml.iml]),
                            fragility_xml.imt)
        
        fragility_model = self.get_fragility_model_by_name(
            fragility_xml.model_name)
        # print "Inserted fragility model %s" % fragility_model

        stat_id = self.insert_id_statistic(
                fragility_xml.statistic,
                fragility_xml.quantile_value)


        # TODO: to add position!
        self.insert_fragility_statistic_rel(frag_id, stat_id)

        ls_id_dic = dict()

        for ls in fragility_xml.limit_states:
            ls_id = self.insert_id_limitstate(ls)
            ls_id_dic.update({ls.lower():ls_id})
            self.insert_fragmodel_limitstate_rel(frag_id, ls_id)

        general_class_id_dic = dict()
        for c in self.get_general_classes_list():
            general_class_id_dic.update({c['name'].lower():c['id']})

        frag_entries = []
        for a in fragility_xml.areas:
            for cat_key in a.functions.keys():
                for ls_key in a.functions[cat_key].keys():
                    f_tmp = ( self.get_area_dbid_by_areaid(a.areaID),
                              ls_id_dic[ls_key.lower()],
                              general_class_id_dic[cat_key.lower()],
                              " ".join([str(x) for x in
                                        a.functions[cat_key][ls_key]]))
                    frag_entries.append(f_tmp)
        self.insert_fragility_data(frag_id, stat_id, frag_entries)
        
    

    def insert_id_loss_model(self, id_phen, loss_type, model_name, unit):
        sqlquery = """SELECT id FROM loss_models
                   WHERE model_name = '{0}'
                   """
        self._cursor.execute(sqlquery.format(model_name.upper()))
        id = self._cursor.fetchone()
        if id:
            return id[0]
        else:
            sqlquery = """
                    INSERT INTO loss_models (loss_type, id_phenomenon,
                                                model_name, unit)
                                        VALUES('{0}', {1}, '{2}', '{3}')
                    """
            self._cursor.execute(sqlquery.format(loss_type,
                                                 id_phen,
                                                 model_name.upper(),
                                                 unit))
            return self._cursor.lastrowid

    def insert_loss_statistic_rel(self, loss_id, statistic_id):
        """

        """
        sqlquery = """
                    INSERT IGNORE INTO lossmodel_statistics
                    (id_loss_model, id_statistic)
                        VALUES ({0}, {1})"""
        return self._cursor.execute(sqlquery.format(loss_id, statistic_id))
    
    def get_statistics_by_loss_id(self, loss_id):
        sqlquery = """ SELECT `st`.`id`, `st`.`name`
            FROM `lossmodel_statistics` `loss_stat` LEFT JOIN
            `statistics` `st` ON
            `loss_stat`.`id_statistic`=`st`.`id`
            WHERE `loss_stat`.`id_loss_model`= %s
        """
        sqlquery %= str(loss_id)
        self._cursor.execute(sqlquery)
        return [dict(zip(['id', 'name'], (x[0], x[1])))
                for x in self._cursor.fetchall()]

    def insert_loss_data(self, loss_id, stat_id, loss_entries):
        sqlquery = """
                    INSERT IGNORE INTO loss_data (id_loss_model,
                        id_area, id_statistic, id_limit_state,
                        loss_function)
                        VALUES ( """ + str(loss_id) + """
                        , %s, """ + str(stat_id) + """, %s , %s)"""

        return self._cursor.executemany(sqlquery, loss_entries)

    def add_loss(self, loss_xml):
        phen_id_dic = dict()
        for p in self.get_phenomena_list():
            phen_id_dic.update({p['phenomenon_name']:p['phenomenon_id']})
        phen_id = phen_id_dic[loss_xml.hazard_type.upper()]

        loss_id = self.insert_id_loss_model(phen_id,
                                            loss_xml.loss_type,
                                            loss_xml.model_name,
                                            loss_xml.unit)

        loss_model = self.get_loss_model_by_name(loss_xml.model_name)
        print "Inserted loss model %s" % loss_model
        
        stat_id = self.insert_id_statistic(
                loss_xml.statistic,
                loss_xml.quantile_value)

        self.insert_loss_statistic_rel(loss_id, stat_id)

        ls_id_dic = dict()

        loss_entries = []
        for a in loss_xml.areas:
            for ls_key in a.functions.keys():
                if ls_key not in ls_id_dic.keys():
                    ls_id = self.insert_id_limitstate(ls_key)
                    ls_id_dic.update({ls_key.lower():ls_id})
                else:
                    ls_id = ls_id_dic[ls_key.lower()]
                function_point_list = []
                if len(a.functions[ls_key]['losses']) != len(a.functions[ls_key]['poEs']):
                    raise Exception("different lengths")
                for i_x in range(len(a.functions[ls_key]['losses'])):
                    function_point = str(a.functions[ls_key]['losses'][i_x]) + \
                                  " " + str(a.functions[ls_key]['poEs'][i_x])
                    function_point_list.append(function_point)

                f_tmp = ( self.get_area_dbid_by_areaid(a.areaID),
                          ls_id,
                          ",".join(function_point_list))
                loss_entries.append(f_tmp)
        self.insert_loss_data(loss_id, stat_id, loss_entries)

    def get_fragility_model_by_name(self, frag_name):
        sqlquery = """ SELECT `frag_mod`.`id`,
                    `frag_mod`.`id_phenomenon`,
                    `frag_mod`.`model_name`,
                    `frag_mod`.`description`,
                    `frag_mod`.`iml`,
                    `frag_mod`.`imt`
            FROM `fragility_models` `frag_mod`
            WHERE `frag_mod`.`model_name`= '%s'
        """
        sqlquery %= (str(frag_name.upper()))
        self._cursor.execute(sqlquery)
        return dict(zip(['id', 'phenomenon_id',
                         'model_name', 'description',
                         'iml', 'imt'],
                        self._cursor.fetchone()))

    def get_fragility_model_by_phenid(self, phen_id):
        sqlquery = """ SELECT `frag_mod`.`id`,
                    `frag_mod`.`id_phenomenon`,
                    `frag_mod`.`model_name`,
                    `frag_mod`.`description`,
                    `frag_mod`.`iml`,
                    `frag_mod`.`imt`
            FROM `fragility_models` `frag_mod`
            WHERE `frag_mod`.`id_phenomenon`= %s
        """
        sqlquery %= (str(phen_id))
        self._cursor.execute(sqlquery)
        return dict(zip(['id', 'phenomenon_id',
                         'model_name', 'description',
                         'iml', 'imt'],
                        self._cursor.fetchone()))

    def get_fragility_model_by_id(self, frag_id):
        sqlquery = """ SELECT `frag_mod`.`id`,
                    `frag_mod`.`id_phenomenon`,
                    `frag_mod`.`model_name`,
                    `frag_mod`.`description`,
                    `frag_mod`.`iml`,
                    `frag_mod`.`imt`
            FROM `fragility_models` `frag_mod`
            WHERE `frag_mod`.`id`= %s
        """
        sqlquery %= (str(frag_id))
        self._cursor.execute(sqlquery)
        return dict(zip(['id', 'phenomenon_id',
                         'model_name', 'description',
                         'iml', 'imt'],
                        self._cursor.fetchone()))


    def get_loss_model_by_name(self, loss_name):
        sqlquery = """ SELECT `loss_mod`.`id`,
                    `loss_mod`.`loss_type`,
                    `loss_mod`.`id_phenomenon`,
                    `loss_mod`.`model_name`,
                    `loss_mod`.`description`,
                    `loss_mod`.`unit`
            FROM `loss_models` `loss_mod`
            WHERE `loss_mod`.`model_name`= '%s'
        """
        sqlquery %= (str(loss_name.upper()))
        self._cursor.execute(sqlquery)
        return dict(zip(['id', 'loss_type', 'phenomenon_id',
                         'model_name', 'description',
                         'unit'],
                        self._cursor.fetchone()))

    def get_loss_model_by_id(self, loss_id):
        sqlquery = """ SELECT `loss_mod`.`id`,
                    `loss_mod`.`loss_type`,
                    `loss_mod`.`id_phenomenon`,
                    `loss_mod`.`model_name`,
                    `loss_mod`.`description`,
                    `loss_mod`.`unit`
            FROM `loss_models` `loss_mod`
            WHERE `loss_mod`.`id`= %s
        """
        sqlquery %= (str(loss_id))
        self._cursor.execute(sqlquery)
        return dict(zip(['id', 'loss_type', 'phenomenon_id',
                         'model_name', 'description',
                         'unit'],
                        self._cursor.fetchone()))
    
    def get_loss_model_by_phenid(self, phen_id):
        sqlquery = """ SELECT `loss_mod`.`id`,
                    `loss_mod`.`loss_type`,
                    `loss_mod`.`id_phenomenon`,
                    `loss_mod`.`model_name`,
                    `loss_mod`.`description`,
                    `loss_mod`.`unit`
            FROM `loss_models` `loss_mod`
            WHERE `loss_mod`.`id_phenomenon`= %s
        """
        sqlquery %= (str(phen_id))
        self._cursor.execute(sqlquery)
        return dict(zip(['id', 'loss_type', 'phenomenon_id',
                         'model_name', 'description',
                         'unit'],
                        self._cursor.fetchone()))
    
    def get_risk_model_by_hazid(self, haz_id):
        sqlquery = """ SELECT `risk_mod`.`id`,
                    `risk_mod`.`risk_type`,
                    `risk_mod`.`id_phenomenon`,
                    `risk_mod`.`id_hazard_model`,
                    `risk_mod`.`id_fragility_model`,
                    `risk_mod`.`id_loss_model`,
                    `risk_mod`.`model_name`,
                    `risk_mod`.`investigation_time`,
                    `risk_mod`.`description`
            FROM `risk_models` `risk_mod`
            WHERE `risk_mod`.`id_hazard_model`= %s
        """
        sqlquery %= (str(haz_id))
        self._cursor.execute(sqlquery)
        res = self._cursor.fetchone()
        if res is None:
            return None
        else:
            return dict(zip(['id', 'risk_type', 'phenomenon_id',
                         'hazard_id', 'fragility_id', 'loss_id',
                         'model_name', 'investigation_time', 'description'],
                        res))
    
    
    def insert_id_risk_model(self, id_phen, risk_type, model_name,
                             fragility_model_name, hazard_model_name,
                             loss_model_name, investigation_time):
        sqlquery = """SELECT id FROM risk_models
                   WHERE model_name = '{0}' AND investigation_time = {1}
                   """
        self._cursor.execute(sqlquery.format(model_name.upper(),
                                             investigation_time))
        id = self._cursor.fetchone()
        if id:
            return id[0]
        else:
            haz_model = self.get_hazard_model_by_name_exptime(
                hazard_model_name,
                                                           investigation_time)
            frag_model = self.get_fragility_model_by_name(fragility_model_name)
            loss_model = self.get_loss_model_by_name(loss_model_name)

            sqlquery = """
                    INSERT INTO risk_models (id_phenomenon,
                                            id_hazard_model, id_fragility_model,
                                            id_loss_model, risk_type,
                                            model_name, investigation_time)
                                VALUES({0}, {1}, {2}, {3}, '{4}', '{5}', {6})
                    """
            self._cursor.execute(sqlquery.format(id_phen,
                                                 haz_model['hazard_id'],
                                                 frag_model['id'],
                                                 loss_model['id'],
                                                 risk_type,
                                                 model_name.upper(),
                                                 investigation_time))
            return self._cursor.lastrowid

    def get_statistics_by_risk_id(self, risk_id):
        sqlquery = """ SELECT `st`.`id`, `st`.`name`
            FROM `riskmodel_statistics` `risk_stat` LEFT JOIN
            `statistics` `st` ON
            `risk_stat`.`id_statistic`=`st`.`id`
            WHERE `risk_stat`.`id_risk_model`= %s
        """
        sqlquery %= str(risk_id)
        self._cursor.execute(sqlquery)
        return [dict(zip(['id', 'name'], (x[0], x[1])))
                for x in self._cursor.fetchall()]

    def insert_risk_statistic_rel(self, risk_id, statistic_id):
        """

        """
        sqlquery = """
                    INSERT IGNORE INTO riskmodel_statistics
                    (id_risk_model, id_statistic)
                        VALUES ({0}, {1})"""
        return self._cursor.execute(sqlquery.format(risk_id, statistic_id))

    def insert_risk_data(self, risk_id, stat_id, risk_entries):
        sqlquery = """
                    INSERT IGNORE INTO risk_data (id_risk_model,
                        id_area, id_statistic, risk_function, average_risk)
                        VALUES ( """ + str(risk_id) + """
                        , %s, """ + str(stat_id) + """, %s , %s)"""

        return self._cursor.executemany(sqlquery, risk_entries)

    def get_risk_model_by_name_invtime(self, risk_name, investigation_time):
        sqlquery = """ SELECT `risk_mod`.`id`,
                    `risk_mod`.`id_phenomenon`,
                    `risk_mod`.`id_hazard_model`,
                    `risk_mod`.`id_fragility_model`,
                    `risk_mod`.`id_loss_model`,
                    `risk_mod`.`risk_type`,
                    `risk_mod`.`model_name`,
                    `risk_mod`.`investigation_time`,
                    `risk_mod`.`description`
            FROM `risk_models` `risk_mod`
            WHERE `risk_mod`.`model_name`= '%s' AND
            `risk_mod`.`investigation_time`= '%s'
        """
        sqlquery %= (str(risk_name.upper()), str(investigation_time))
        print sqlquery
        self._cursor.execute(sqlquery)
        return dict(zip(['id', 'phenomenon_id', 'hazard_id', 'fragility_id',
                         'loss_id', 'risk_type', 'model_name',
                         'investigation_time', 'description'],
                        self._cursor.fetchone()))


    def add_risk(self, risk_xml):
        phen_id_dic = dict()
        for p in self.get_phenomena_list():
            phen_id_dic.update({p['phenomenon_name']:p['phenomenon_id']})
        phen_id = phen_id_dic[risk_xml.hazard_type.upper()]


        risk_id = self.insert_id_risk_model(phen_id,
                                            risk_xml.risk_type,
                                            risk_xml.model_name,
                                            risk_xml.fragility_model_name,
                                            risk_xml.hazard_model_name,
                                            risk_xml.loss_model_name,
                                            risk_xml.investigation_time)

        risk_model = self.get_risk_model_by_name_invtime(risk_xml.model_name,
                                                risk_xml.investigation_time)
        print "Inserted risk model %s" % risk_model
        area_dic = dict()
        for stat in list(set([a.statistic for a in risk_xml.areas])):
            print "Insert id stat: %s" % stat
            area_dic[stat] = dict(stat_id=self.insert_id_statistic_new(stat),
                                  risk_entries=[])
            print "Insert risk stat rel, stat_id: %s" % area_dic[stat]['stat_id']
            self.insert_risk_statistic_rel(risk_id, area_dic[stat]['stat_id'])

        for a in risk_xml.areas:
                function_point_list = []
                if len(a.functions['losses']) != len(a.functions['poEs']):
                    raise Exception("different lengths")
                for i_x in range(len(a.functions['losses'])):
                    function_point = str(a.functions['losses'][i_x]) + \
                                  " " + str(a.functions['poEs'][i_x])
                    function_point_list.append(function_point)

                f_tmp = (self.get_area_dbid_by_areaid(a.areaID),
                          ",".join(function_point_list),
                          a.average_risk
                )
                area_dic[a.statistic]['risk_entries'].append(f_tmp)

        for stat in area_dic.keys():
            print "Insert risk data, risk_id %s" % risk_id
            print "Insert risk data, stat_id %s" % area_dic[stat]['stat_id'],
            print "Insert risk data, risk entries %s" % area_dic[stat][
                'risk_entries']
            self.insert_risk_data(risk_id, area_dic[stat]['stat_id'],
                                  area_dic[stat]['risk_entries'])
