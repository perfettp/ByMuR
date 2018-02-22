#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
  Bymur Software computes Risk and Multi-Risk associated to Natural Hazards.
  In particular this tool aims to provide a final working application for
  the city of Naples, considering three natural phenomena, i.e earthquakes,
  volcanic eruptions and tsunamis.
  The tool is the final product of BYMUR, an Italian project funded by the
  Italian Ministry of Education (MIUR) in the frame of 2008 FIRB, Futuro in
  Ricerca funding program.

  Copyright(C) 2012-2015 Paolo Perfetti, Roberto Tonini and Jacopo Selva

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

"""

import bymur_db
import os
import bymur_functions as bf
import sys


def main(*args):
    if (len(args)<2):
        print "Root dir is needed"
        exit(-1)

    dbDetails = {'db_host': 'localhost',
                 'db_port': '3306',
                 'db_user': 'bymurTEST',
                 'db_password': 'bymurTEST',
                 'db_name': 'bymurTEST'
    }
    db=bymur_db.BymurDB(**dbDetails)

    rootdir = args[1]
    print "Scanning directory %s for files" % rootdir

    for root, dirs, files in os.walk(rootdir):
        for file in files:
            if file.startswith("arealRiskModel"):
                r_xml = bf.parse_xml_risk(
                    os.path.relpath(os.path.join(root,file), os.getcwd()))
                db.add_risk(r_xml)
            elif file.startswith("arealLossModel"):
                l_xml = bf.parse_xml_loss(
                    os.path.relpath(os.path.join(root, file), os.getcwd()))
                db.add_loss(l_xml)

            elif file.startswith("arealFragilityModel"):
                f_xml = bf.parse_xml_fragility(
                    os.path.relpath(os.path.join(root, file), os.getcwd()))
                db.add_fragility(f_xml)


if __name__ == "__main__":
    main(*sys.argv)
