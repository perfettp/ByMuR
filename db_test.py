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
import os
import re
import time
import dbFunctions as db
import bymurcore

dbDetails = {'db_host': '***REMOVED***',
                  'db_port': '3306',
                  'db_user': '***REMOVED***',
                  'db_password': '***REMOVED***',
                  'db_name': 'bymurDB-dev-utm'
    }



# database=db.BymurDB(**dbDetails)
core = bymurcore.BymurCore()
core.connectDB(**dbDetails)
core._db.populate('/hades/dev/bymur-data/test_git', '10:100:10',
                   '/hades/dev/bymur-data/V1_bymurgrid.txt')
# '/hades/dev/bymur-data/naples_100m_UTM.txt')

# curves =  core._db.get_curves(2,3,1,4,1)
#core.compute_hazard_map(1, 50, 4975)

# a = database.get_intensity_threshods_by_haz(1)
#
# print a


# database.commit()
#database.close()

# x = HazardModel("/hades/dev/bymur-data/test/seismic/Historical_i4/dt50"
#                 "/hazardcurve-mean.xml",
#                 "volcanic")
#
# try:
#     x = HazardModel("/hades/dev/bymur-data/test/seismic/Historical_i4/dt50"
#                 "/test.xml",
#                 # "/hazardcurve-mean.xml",
#                 "volcanic")
# except Exception as e:
#     print "Errore di conformita'"

#  HazardModel("/hades/dev/bymur/schema/input1.xml", "volcanic")

#
# print points_to_latlon(x.points_coords)

print "Terminato, ho!"