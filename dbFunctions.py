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
import sys
import warnings
import wx
import numpy as np
import xml.etree.ElementTree as xml
import MySQLdb as mdb
import globalFunctions as gf


# JACOPO 10/06/13
def dbReadHC(*kargs):
    haz_sel = kargs[0]        # selected hazard phenomenon
    tw = kargs[1]             # selected time window
    dtime = kargs[2]          # selected hazard phenomenon
    cur = kargs[3]            # cursor of database
    hc = kargs[4]             # hazard array
    hc_perc = kargs[5]        # percentiles given for this hazard

    print 'haz_sel-->', haz_sel
    print 'tw-->', tw
    # print hc.shape

    tbname = "hazard" + str(haz_sel + 1)
#    cmd = "SELECT stat FROM " + tbname + " WHERE STRCMP(dtime,'" \
#       + dtime[tw] + "')>0 AND stat != 'Average' AND id_points = 1"
    cmd = "SELECT stat FROM " + tbname + " WHERE dtime = '" + \
        dtime[haz_sel][tw].zfill(3) + "' AND stat != 'Average' AND id_points = 1"
    cur.execute(cmd)
    tmp1 = cur.fetchall()
    nperc_haz = len(tmp1)
    perc_haz = np.zeros(nperc_haz, dtype=np.int8)
    print cmd
    print 'cur.fetchall: ', tmp1
    for iperchaz in range(nperc_haz):
        line = tmp1[iperchaz]
        tmp2 = line[0].split('Perc')
        perc_haz[iperchaz] = tmp2[1]
#    hc_perc.insert(haz_sel,perc_haz)
    hc_perc[haz_sel] = perc_haz
#    print 'hc_perc',hc_perc
    percsel = range(1, 100)  # [10,50,90]
# hc[haz_sel][tw][perc][pt_sel][:]
    cmd = "SELECT id_points,curve FROM " + tbname + " WHERE dtime ='" \
        + dtime[haz_sel][tw].zfill(3) + "' AND stat = 'Average'"
    cur.execute(cmd)
    rows = cur.fetchall()
    for row in rows:
        ipoint = row[0]
        curvetmp = row[1]
#       print len(curvetmp)
#       print len(hc[haz_sel][tw][0][ipoint-1])
        hc[haz_sel][tw][0][ipoint - 1] = curvetmp

    for ipercsel in range(len(perc_haz)):
        perctmp = perc_haz[ipercsel]
        # print "Selected percentile:" + str(perctmp)
        cmd = "SELECT id_points,curve FROM " + tbname + " WHERE dtime = '" + \
            dtime[haz_sel][tw].zfill(3) + "' AND stat = 'Perc" + str(perctmp) + "'"
        cur.execute(cmd)
        rows = cur.fetchall()
        for row in rows:
            ipoint = row[0]
            curvetmp = row[1]
            hc[haz_sel][tw][perctmp][ipoint - 1] = curvetmp

    print 'DB table read!!'
    return hc

# JACOPO 10/06/13


# ROBERTO 28/06/2013
def dbSelectDtime(*kargs):
    """
    """

    con = kargs[0]
    cur = kargs[1]
    nhaz = kargs[2]

    with con:
        sql_query = """
                SELECT dtime from {0} WHERE id_points=1 AND stat='Average'
                """
        cur.execute(sql_query.format(nhaz))
        rows = cur.fetchall()
        return rows

# END ROBERTO 28/06/2013


# ROBERTO 23/09/2013
def dbAssignFlagPerc(*kargs):
    """
    """

    con = kargs[0]
    cur = kargs[1]
    nhaz = kargs[2]

    with con:
        #    sql_query = """
        #                SELECT id from {0} WHERE stat LIKE 'Perc%'
        #                """
        #    cur.execute(sql_query.format(nhaz))
        #    if cur.fetchone():
        #      return 1
        #    else:
        #      return 0

        sql_query = """
                SELECT curve from {0} WHERE stat LIKE 'Perc%' AND id_points=1
                """
        cur.execute(sql_query.format(nhaz))
        rows = cur.fetchall()
        sumval = 0
        for row in rows:
            tmp = [float(j) for j in str(row[0]).split()]
            sumval = sumval + tmp[0]

        if (sumval > 0):
            return 1
        else:
            return 0

# END ROBERTO 23/09/2013


def dbConnection(*kargs):
    """
    Connecting to database
    """

    server = kargs[0]
    user = kargs[1]
    pwd = kargs[2]
    dbname = kargs[3]

    try:
        connection = mdb.connect(server, user, pwd, dbname)
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        db_version = cursor.fetchone()
        txt = "\nConnection Succeded!\nMySQL version : {0} ".format(
            db_version[0])
        gf.show_message(None, txt, "Info")
        return connection, cursor

    except mdb.Error as e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)

def dbClose(*kargs):
    cursor = kargs[0]
    return cursor.close()


def dbXmlParsing(*kargs):
    """
    Reading of hazard curves.
    It opens and reads xml files formatted on the basis of the standard
    semantic proposed by the OpenQuake/GEM projects.

    """

    path = kargs[0]

    if os.path.isfile(path):

        tree = xml.parse(path)
        root = tree.getroot()

        pos = []
        poe = []

        # for node in tree.iter():          # python 2.7
        for node in tree.findall('.//*'):   # python 2.6
            if ("model" in node.tag):
                mod = node.attrib.get("Model")
            if ("timeterm" in node.tag):
                dtime = node.attrib.get("deltaT")
            if ("IML" in node.tag):
                iml = " ".join(x for x in node.text.split())
                imt = node.attrib.get("IMT")
            if ("gmlpos" in node.tag):
                pos.append([float(x) for x in node.text.split()])
            if ("poE" in node.tag):
                poe.append(" ".join(x for x in node.text.split()))

        npts = len(pos)
        lat = [pos[i][0] for i in range(npts)]
        lon = [pos[i][1] for i in range(npts)]

        return mod, dtime, imt, iml, lat, lon, poe, npts

    else:
        msg = ("ERROR:\nUploaded file path is wrong")
        gf.showErrorMessage(None, msg, "ERROR")
        return


def dbCreateTables(*kargs):
    """
    Creating DB Tables if they do not exist.
    """

    con = kargs[0]
    cur = kargs[1]
    perc = kargs[2]
    hazards = kargs[3]
    models = kargs[4]

    ntables_haz = sum([len(models[i][:]) for i in range(len(models))])

    with con:
        warnings.simplefilter('ignore', mdb.Warning)

        # Hazard phenomena table creation
        sql_query = """
                CREATE TABLE IF NOT EXISTS hazard_phenomena
                (id_haz INT UNSIGNED NOT NULL PRIMARY KEY,
                id_map_info INT, id_spatial_data INT,
                vd_ID INT,
                 name VARCHAR(32), model VARCHAR(32),
                 imt VARCHAR(32), iml TEXT);
                """
        cur.execute(sql_query)

        # Spatial Data table creation
        sql_query = """
                CREATE TABLE IF NOT EXISTS spatial_data1
                (id_points INT UNSIGNED NOT NULL PRIMARY KEY,
                id_area INT UNSIGNED, lon DOUBLE, lat DOUBLE);
                """
        cur.execute(sql_query)

        # Hazard tables creation
        for i in range(ntables_haz):
            tbname = "hazard" + str(i + 1)
            sql_query = """
                  CREATE TABLE IF NOT EXISTS {0}
                  (id INT UNSIGNED NOT NULL PRIMARY KEY, id_haz INT,
                  id_points INT, stat VARCHAR(20), dtime VARCHAR(20), curve MEDIUMTEXT);
                  """
            cur.execute(sql_query.format(tbname))

        # Map Info table creation
        sql_query = """
                CREATE TABLE IF NOT EXISTS map_info
                (id INT UNSIGNED NOT NULL PRIMARY KEY, imgpath TEXT,
                lon_min DOUBLE, lon_max DOUBLE, lat_min DOUBLE, lat_max DOUBLE);
                """
        cur.execute(sql_query)


def dbSpatDataPop(*kargs):
    """
    Populating Spatial Data table  or update it if it already exists.

    """

    con = kargs[0]
    cur = kargs[1]
    gridpath = kargs[2]

    A = np.loadtxt(gridpath)
    lon = A[:, 0]
    lat = A[:, 1]
    id_area = A[:, 2]
    npts = len(lon)

    with con:
        sql = "SELECT COUNT(1) FROM spatial_data1 WHERE id_points = '1'"
        cur.execute(sql)
        if cur.fetchone()[0]:
            for i in range(npts):
                sql = """
              UPDATE spatial_data1 SET id_area='{0}',
              lon='{1}', lat='{2}' WHERE id_points={3}
              """
                cur.execute(sql.format(id_area[i], lon[i], lat[i], i + 1))
        else:
            for i in range(npts):
                sql = """
              INSERT INTO spatial_data1 (id_points, id_area,
              lon, lat) VALUES ({0}, '{1}', '{2}', '{3}')
              """
                cur.execute(sql.format(i + 1, id_area[i], lon[i], lat[i]))

    return npts


def dbHazTabPop(*kargs):
    """
    Populating hazard tables of Bymur DB if they are empty or update them if
    they already exist.
    """
    con = kargs[0]
    cur = kargs[1]
    perc = kargs[2]
    hazards = kargs[3]
    models = kargs[4]
    dtime = kargs[5]
    hazpath = kargs[6]
    npts = kargs[7]

# JACOPO 18.06.2013
    dtimefold = kargs[8]
# JACOPO 18.06.2013

    mod = []
    imt = []
    iml = []
    mean = []
    hc = []
    nmods = 0

    for h in range(len(hazards)):
        for m in range(len(models[h])):
            nmods = nmods + 1
            hcTmp = []
            meanTmp = []

            for k in range(len(dtime[nmods - 1])):
                # JACOPO 18.06.2013
                #        curdir = os.path.join(hazpath, hazards[h], models[h][m], dtime[k])
                print h, m, k, nmods
                print hazpath, hazards[h], models[h][m], dtimefold[nmods - 1][k]
                curdir = os.path.join(
                    hazpath,
                    hazards[h],
                    models[h][m],
                    dtimefold[
                        nmods -
                        1][k])
                print "reading from ", curdir
# FINE JACOPO 18.06.2013
                if not os.listdir(curdir):
                    # break
                    modTmp = "Null"
                    imtTmp = "Null"
                    imlTmp = "0"
                    meanTmp = [["0"] * npts] * len(dtime[nmods - 1])
                    hcTmp = [
                        [["0"] * npts] * len(perc)] * len(dtime[nmods - 1])
                else:
                    print "found: dtime=", k, ' from: ', curdir
                    # reading average
#          filexml = os.path.join(curdir, "hazardcurve-average.xml")
                    filexml = os.path.join(curdir, "hazardcurve-mean.xml")
#          print 'file -->',filexml
                    tmp = dbXmlParsing(filexml)
                    modTmp = tmp[0]
                    imtTmp = tmp[2]
                    imlTmp = tmp[3]
                    meanTmp.append(tmp[6])
                    npts = len(tmp[6])
                    niml = len([float(j) for j in tmp[6][0].split()])

                    # reading percentiles
                    hcTmp2 = []
                    path = os.path.join(curdir, "hazardcurve-percentile-")
                    for p in perc:
                        filexml = path + str(p) + ".xml"
                        if os.path.isfile(filexml):
                            tmp = dbXmlParsing(filexml)
                            hcTmp2.append(tmp[6])
                        else:
                            tmplist = [
                                ' '.join(
                                    '0.0 ' for i in range(niml))] * npts
                            hcTmp2.append(tmplist)
#              msg = ("ERROR:\nUploaded file path is wrong: " + filexml)
#              gf.showErrorMessage(None, msg, "ERROR")
#              return

                    else:
                        hcTmp.append(hcTmp2)

            else:
                mod.append(modTmp)
                imt.append(imtTmp)
                iml.append(imlTmp)
                mean.append(meanTmp)
                hc.append(hcTmp)

    print mod, imt, iml
    print len(mod), len(imt), len(iml)
    print len(mean), len(mean[0][:]), len(mean[0][0][:])
    print len(hc), len(hc[0][:]), len(hc[0][0][:]), len(hc[0][0][0][:])

    with con:
        # Populating Hazard Phenomena table
        nmods = 0
        for h in range(len(hazards)):
            for m in range(len(models[h])):
                nmods = nmods + 1
                sql = "SELECT COUNT({0}) FROM hazard_phenomena WHERE id_haz = {1}"
                cur.execute(sql.format(nmods, nmods))
                if cur.fetchone()[0]:
                    sql = """
                UPDATE hazard_phenomena SET name='{0}',
                model='{1}', imt='{2}', iml='{3}'
                id_map_info = 1, id_spatial_data = 1,
                vd_ID = 0,
                WHERE id_haz={4}
                """
                    cur.execute(sql.format(hazards[h], models[h][m], imt[
                                nmods - 1].replace("_", " "), iml[nmods - 1], nmods))
                else:
                    sql = """
                INSERT INTO hazard_phenomena (id_haz, name, model,
                imt, iml, id_map_info, id_spatial_data, vd_ID) VALUES
                ({0}, '{1}', '{2}', '{3}', '{4}', 1, 1, 0)
                """
                    cur.execute(sql.format(nmods,
                                           hazards[h],
                                           models[h][m],
                                           imt[nmods - 1].replace("_",
                                                                  " "),
                                           iml[nmods - 1]))

        # Populating Hazard tables
        sql = "SELECT COUNT(1) FROM hazard1 WHERE id_points = '1'"
        cur.execute(sql)
        if cur.fetchone()[0]:
            for m in range(len(mod)):
                tbname = "hazard" + str(m + 1)
                idc = 0
                for k in range(len(dtime[m])):
                    for i in range(npts):
                        idc = idc + 1
                        sql = """
                  UPDATE {0} SET id_haz={1}, id_points={2}, stat='{3}',
                  dtime='{4}', curve='{5}' WHERE id={6}
                  """
                        cur.execute(
                            sql.format(
                                tbname,
                                m + 1,
                                i + 1,
                                "Average",
                                dtime[m][k],
                                mean[m][k][i],
                                idc))

                    for p in range(len(perc)):
                        pp = str(perc[p])
                        for i in range(npts):
                            idc = idc + 1
                            sql = """
                    UPDATE {0} SET id_haz={1}, id_points={2}, stat='{3}',
                    dtime='{4}', curve='{5}' WHERE id={6}
                    """
                            cur.execute(
                                sql.format(
                                    tbname,
                                    m + 1,
                                    i + 1,
                                    "Perc" + pp,
                                    dtime[m][k],
                                    hc[m][k][p][i],
                                    idc))

        else:
            for m in range(len(mod)):
                tbname = "hazard" + str(m + 1)
                idc = 0
                for k in range(len(dtime[m])):
                    for i in range(npts):
                        idc = idc + 1
                        sql = """
                  INSERT INTO {0} (id, id_haz, id_points, stat,
                  dtime, curve) VALUES ( {1}, {2}, {3}, '{4}', '{5}', '{6}' )
                  """
                        cur.execute(
                            sql.format(
                                tbname,
                                idc,
                                m + 1,
                                i + 1,
                                "Average",
                                dtime[m][k],
                                mean[m][k][i]))

                    for p in range(len(perc)):
                        pp = str(perc[p])
                        for i in range(npts):
                            idc = idc + 1
                            sql = """
                    INSERT INTO {0} (id, id_haz, id_points, stat,
                    dtime, curve) VALUES ( {1}, {2}, {3}, '{4}', '{5}', '{6}' )
                    """
                            cur.execute(
                                sql.format(
                                    tbname,
                                    idc,
                                    m + 1,
                                    i + 1,
                                    "Perc" + pp,
                                    dtime[m][k],
                                    hc[m][k][p][i]))


def dbReadTable(*kargs):
    """
    Reading all tables from Bymur DB and storing all data in python lists.
    """

    con = kargs[0]
    cur = kargs[1]
    nameTB = kargs[2]

    with con:

        query = "SELECT * FROM {0}"
        cur.execute(query.format(nameTB))
        rows = cur.fetchall()
        return rows


def dbGenInfoPop(*kargs):
    """
    """
    con = kargs[0]
    cur = kargs[1]
    imgpath = kargs[2]
    limits = kargs[3]

    with con:
        sql = "SELECT COUNT(1) FROM map_info WHERE id = '1'"
        cur.execute(sql)
        if cur.fetchone()[0]:
            sql = """
            UPDATE map_info SET imgpath='{0}', lon_min={1}, lon_max={2},
            lat_min={3}, lat_max={4} WHERE id=1
            """
            cur.execute(sql.format(imgpath, limits[0], limits[1],
                                   limits[2], limits[3]))
        else:
            sql = """
            INSERT INTO map_info (id, imgpath, lon_min, lon_max,
            lat_min, lat_max) VALUES (1, '{0}', {1}, {2}, {3}, {4})
            """
            cur.execute(sql.format(imgpath, limits[0], limits[1],
                                   limits[2], limits[3]))


def dbDropAllTabs(*kargs):
    """
    """
    con = kargs[0]
    cur = kargs[1]
    with con:
        query = "SHOW TABLES"
        cur.execute(query)
        tables = cur.fetchall()

        for tab in tables:
            # print tab[0]
            query = "DROP TABLE {0}"
            cur.execute(query.format(tab[0]))
